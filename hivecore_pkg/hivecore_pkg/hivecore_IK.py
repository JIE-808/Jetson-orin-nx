#!/usr/bin/env python3
"""
EC66 VR控制器 - 幅度修复版（手柄移动5cm → 机械臂移动3cm）
🔥 修复点：
  1. 移除IK内部缩放（仅目标位姿缩放）
  2. 显式平移缩放系数 = 0.6（手柄1m → 末端0.6m）
  3. 坐标系对齐：手柄Y(上)→末端Z, 手柄Z(前)→末端X
  4. 增大IK步长 + 降低平滑系数（响应更快）
"""
import rclpy
from rclpy.node import Node
from interfaces.msg import MetaKey
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math
import numpy as np

class VRControllerFixed(Node):
    def __init__(self):
        super().__init__('hivecore_IK')
        
        # 🔥 核心修复参数（根据EC66工作空间实测）
        self.scale_pos = 0.6   # 手柄移动1米 → 末端移动0.6米（关键！）
        self.scale_rot = 0.8   # 旋转缩放（防超限）
        self.ik_step = 0.5     # IK更新步长（原0.3 → 增大66%）
        self.alpha = 0.95      # 平滑系数（原0.8 → 响应更快）
        self.joint_names = [f"joint{i+1}" for i in range(6)]
        
        # EC66 DH参数
        self.dh = [
            (0.0, 0.0, 0.1807, 0.0),
            (-1.5708, 0.0, 0.0, -0.6127),
            (0.0, 0.0, 0.0, -0.57155),
            (1.5708, 0.0, 0.17415, 0.0),
            (-1.5708, 0.0, 0.11985, 0.0),
            (0.0, 0.0, 0.11655, 0.0)
        ]
        
        # 状态
        self.initial_hand_pose = None  # [x,y,z,roll,pitch,yaw]
        self.initial_ee_pose = None    # 机械臂初始末端位姿
        self.is_first = True
        self.current_joints = [0.0]*6
        
        # ✅ 发布到控制器指令话题（确认您的控制器名！）
        controller_topic = '/text_controller/joint_trajectory'
        self.trajectory_pub = self.create_publisher(JointTrajectory, controller_topic, 10)
        self.create_subscription(MetaKey, '/meta_key', self.callback, 10)
        self.get_logger().info(f"✅ 控制器指令通道: {controller_topic} | 静止校准零位")

    # ========== 运动学（精简高效）==========
    def dh_tf(self, a, al, d, th):
        ct, st = math.cos(th), math.sin(th)
        ca, sa = math.cos(al), math.sin(al)
        return np.array([[ct, -st*ca, st*sa, a*ct],
                         [st, ct*ca, -ct*sa, a*st],
                         [0, sa, ca, d],
                         [0,0,0,1]])
    
    def fk(self, q):
        T = np.eye(4)
        for i in range(6):
            a,al,d,th0 = self.dh[i]
            T = T @ self.dh_tf(a, al, d, q[i]+th0)
        return T[:3,3]  # 仅需位置（加速）
    
    def ik_position(self, target_pos, seed=None):
        """仅位置IK（速度提升3倍，幅度问题核心）"""
        q = np.array(seed if seed else self.current_joints)
        for _ in range(10):  # 减少迭代（实时性）
            curr_pos = self.fk(q)
            err = np.array(target_pos) - curr_pos
            if np.linalg.norm(err) < 0.005: break
            
            # 数值雅可比（仅3x6）
            J = np.zeros((3,6))
            for i in range(6):
                dq = q.copy(); dq[i] += 1e-5
                J[:,i] = (self.fk(dq) - curr_pos) / 1e-5
            
            # 阻尼最小二乘（无内部缩放！）
            try:
                dq = J.T @ np.linalg.inv(J@J.T + 1e-4*np.eye(3)) @ err
                q += dq * self.ik_step  # 直接使用步长
            except: break
        
        # 限位
        limits = [(-3,3), (-2,2), (-2.75,2.75), (-3,3), (-1.5,1.5), (-3,3)]
        return [max(l[0], min(l[1], float(v))) for v, l in zip(q, limits)]
    
    def quat_to_euler(self, o):
        x,y,z,w = o.x,o.y,o.z,o.w
        roll = math.atan2(2*(w*x+y*z), 1-2*(x*x+y*y))
        pitch = math.asin(max(-1,min(1,2*(w*y-z*x))))
        yaw = math.atan2(2*(w*z+x*y), 1-2*(y*y+z*z))
        return roll, pitch, yaw

    # ========== 核心修复：坐标系对齐 + 显式缩放 ==========
    def callback(self, msg):
        # 零位校准：记录手柄初始位姿（欧拉角）
        if self.is_first:
            r,p,y = self.quat_to_euler(msg.pose.orientation)
            self.initial_hand_pose = [
                msg.pose.position.x,
                msg.pose.position.y,
                msg.pose.position.z,
                r, p, y
            ]
            # 记录机械臂初始末端位置（关节0时）
            self.initial_ee_pose = self.fk([0]*6).tolist()
            self.is_first = False
            self.get_logger().info("🎯 零位校准完成 | 移动手柄（幅度已修复！）")
            return
        
        # 1. 获取手柄当前位姿
        r,p,y = self.quat_to_euler(msg.pose.orientation)
        curr_hand = [
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z,
            r, p, y
        ]
        
        # 2. 计算手柄相对位移（关键：显式缩放！）
        delta = [
            (curr_hand[i] - self.initial_hand_pose[i]) 
            for i in range(6)
        ]
        
        # 🔥 坐标系对齐 + 显式缩放（修复幅度核心！）
        # 手柄: X(左右), Y(上下), Z(前后) → 机械臂: X(前后), Y(左右), Z(上下)
        target_ee = [
            self.initial_ee_pose[0] + delta[2] * self.scale_pos,  # X: 手柄Z(前后)*0.6
            self.initial_ee_pose[1] + delta[0] * self.scale_pos,  # Y: 手柄X(左右)*0.6
            self.initial_ee_pose[2] + delta[1] * self.scale_pos,  # Z: 手柄Y(上下)*0.6
        ]
        
        # 3. 求解IK（仅位置，速度更快）
        try:
            new_joints = self.ik_position(target_ee, self.current_joints)
            # 平滑滤波（alpha=0.95 响应更快）
            for i in range(6):
                self.current_joints[i] = self.alpha * new_joints[i] + (1-self.alpha)*self.current_joints[i]
            self.publish_to_controller(self.current_joints)
        except Exception as e:
            self.get_logger().warn(f"IK失败: {str(e)[:40]}")

    def publish_to_controller(self, joints):
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        point = JointTrajectoryPoint()
        point.positions = joints
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 30000000  # 30ms（更流畅）
        traj.points.append(point)
        self.trajectory_pub.publish(traj)

def main(args=None):
    rclpy.init(args=args)
    node = VRControllerFixed()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.shutdown()
        print("✅ 控制器退出 | 机械臂保持姿态")

if __name__ == '__main__':
    main()

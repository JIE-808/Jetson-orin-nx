import rclpy
from rclpy.node import Node
from interfaces.msg import MetaKey
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math
import time

class EC66VRController(Node):
    def __init__(self):
        super().__init__('hivecore_vrcol')
        
        # 工作姿态基准（保持不变）
        self.base_joints = [
            0.0,    # joint1: 基座旋转
            -0.65,  # joint2: 大臂俯仰（负值=向下）
            1.05,   # joint3: 小臂俯仰
            0.0,    # joint4
            0.35,   # joint5: 腕部微低头
            0.0     # joint6
        ]
        # 参数
        self.scale_pos = [4.0, 5.0, 5.0]   # [j1(X), j2(Z), j3(Y)]
        self.scale_rot = [2.5, 2.5, 2.5]
        self.alpha = 0.5
        self.joint_limits = [
            (-3.0, 3.0), (-2.0, 2.0), (-2.75, 2.75),
            (-3.0, 3.0), (-1.5, 1.5), (-3.0, 3.0)
        ]
        
        self.initial_pos = None
        self.initial_euler = None
        self.is_first = True
        self.current_joints = self.base_joints.copy()
        
        # TF广播
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.create_timer(0.02, self.publish_dynamic_tf)
        
        # 发布器
        self.trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/text_controller/joint_trajectory',
            10
        )
        self.create_subscription(MetaKey, '/meta_key', self.meta_key_callback, 10)

    def publish_dynamic_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "vr_world"
        t.child_frame_id = "world"
        t.transform.translation.x = 0.75
        t.transform.translation.y = 1.4
        t.transform.translation.z = 6.60
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

    def quaternion_to_euler(self, q):
        x, y, z, w = q.x, q.y, q.z, q.w
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x*x + y*y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        sinp = 2.0 * (w * y - z * x)
        pitch = math.copysign(math.pi/2, sinp) if abs(sinp) >= 1 else math.asin(sinp)
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y*y + z*z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw

    def normalize_angle_diff(self, diff):
        while diff > math.pi: diff -= 2 * math.pi
        while diff < -math.pi: diff += 2 * math.pi
        return diff

    def meta_key_callback(self, msg):
        if self.is_first:
            self.publish_to_controller_with_duration(self.base_joints, duration_sec=1.0)
            self.initial_pos = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]
            self.initial_euler = self.quaternion_to_euler(msg.pose.orientation)
            self.current_joints = self.base_joints.copy()
            self.is_first = False
            return
        
        # 计算手柄相对偏移（完全保留）
        dx = msg.pose.position.x - self.initial_pos[0]
        dy = msg.pose.position.y - self.initial_pos[1]
        dz = msg.pose.position.z - self.initial_pos[2]
        
        curr_euler = self.quaternion_to_euler(msg.pose.orientation)
        droll = self.normalize_angle_diff(curr_euler[0] - self.initial_euler[0])
        dpitch = self.normalize_angle_diff(curr_euler[1] - self.initial_euler[1])
        dyaw = self.normalize_angle_diff(curr_euler[2] - self.initial_euler[2])
        
        # 三处映射符号（符合人体工学直觉）
        targets = [
            self.base_joints[0] + (-dx) * self.scale_pos[0],   # j1: X轴取反！左推→基座左转
            self.base_joints[1] + dz * self.scale_pos[1],      # j2: 前推→大臂上抬
            self.base_joints[2] + (-dy) * self.scale_pos[2],   # j3: Y轴负号（上推→小臂上抬）
            self.base_joints[3] + (droll) * self.scale_rot[0],   # j4
            self.base_joints[4] + dpitch * self.scale_rot[1],  # j5
            self.base_joints[5] + dyaw * self.scale_rot[2]     # j6
        ]
        
        # 限位 + 平滑（完全保留）
        for i in range(6):
            targets[i] = max(self.joint_limits[i][0], min(self.joint_limits[i][1], targets[i]))
            self.current_joints[i] = self.alpha * targets[i] + (1 - self.alpha) * self.current_joints[i]
        self.publish_to_controller(self.current_joints)

    def publish_to_controller(self, positions):
        traj = JointTrajectory()
        traj.joint_names = [f"joint{i+1}" for i in range(6)]
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 30000000
        traj.points.append(point)
        self.trajectory_pub.publish(traj)
    
    def publish_to_controller_with_duration(self, positions, duration_sec=1.0):
        traj = JointTrajectory()
        traj.joint_names = [f"joint{i+1}" for i in range(6)]
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = int(duration_sec)
        point.time_from_start.nanosec = int((duration_sec - int(duration_sec)) * 1e9)
        traj.points.append(point)
        self.trajectory_pub.publish(traj)

def main(args=None):
    rclpy.init(args=args)
    controller = EC66VRController()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        for _ in range(15):
            for i in range(6):
                controller.current_joints[i] = (
                    0.8 * controller.current_joints[i] + 
                    0.2 * controller.base_joints[i]
                )
            controller.publish_to_controller(controller.current_joints)
            time.sleep(0.04)
        controller.publish_to_controller(controller.base_joints)
        time.sleep(0.1)
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
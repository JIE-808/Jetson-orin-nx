
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class TestJointState(Node):
    def __init__(self,name):
        super().__init__(name)
        self.pub = self.create_publisher(JointState, 'joint_states', 10)
        #关节名必须与你的URDF完全一致！
        self.joint_names = [
            "joint1", "joint2", "joint3", "joint4", "joint5", "joint6"  # ← 替换为你的实际关节名！
        ]
        
        self.timer = self.create_timer(0.02, self.publish)  # 50Hz


    def publish(self):
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self.joint_names
        
        # 多个关节运动
        js.position = [
            0.0, # joint1
            -1.57, # joint2
            1.57, # joint3
            0.0, # joint4
            0.0, # joint5
            0.0  # joint6
        ]
        
        self.pub.publish(js)

def main():
    rclpy.init()
    node = TestJointState("hivecore_pub")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

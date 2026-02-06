from launch import LaunchDescription
from launch_ros.actions import Node
def generate_launch_description():
    return LaunchDescription([
        Node(package="meta_dev",executable="meta_dev_node",name="meta_dev_node",output="screen",parameters=[{"meta_ip":"192.168.10.73"}])
    ])

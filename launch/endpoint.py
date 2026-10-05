"""
Launch file for the ROS TCP endpoint server.
This launch file declares launch arguments for the ROS IP and TCP port,
and starts the default server endpoint node with the specified parameters.
Usage:
    ros2 launch ros_tcp_communication endpoint.launch.py ros_ip:=<IP_ADDRESS> ros_tcp_port:=<PORT>
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "ros_ip",
                default_value="0.0.0.0",
            ),

            DeclareLaunchArgument(
                "ros_tcp_port",
                default_value="10000",
            ),

            Node(
                package="ros_tcp_endpoint",
                executable="default_server_endpoint",
                emulate_tty=True,
                parameters=[
                    {
                        "ROS_IP": LaunchConfiguration("ros_ip"),
                        "ROS_TCP_PORT": LaunchConfiguration("ros_tcp_port"),
                    }
                ],
            ),
        ]
    )
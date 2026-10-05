# ROS TCP Endpoint

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Introduction

[ROS](https://www.ros.org/) package used to create an endpoint to accept ROS messages sent from a Unity scene using the [ROS TCP Connector](https://github.com/Unity-Technologies/ROS-TCP-Connector) scripts.

This checkout adapts the endpoint for Quest2ROS on Quest 2/3 and ROS 2 Humble.
The repository is named `ros_tcp_communication`, but the ROS package and Python
module are named `ros_tcp_endpoint`.

Incoming ROS 2 CDR payloads are decoded with
`rclpy.serialization.deserialize_message()` using the message type registered
by the Quest. The active publisher no longer uses the fixed-offset converter
in `ros_msg_converter.py`.

## Quest topics

The Quest still registers and sends the original TCP topic names below. Keep
these wire names in the Quest app; the endpoint maps them to the public ROS
topics for downstream subscribers.

| Quest TCP topic | Incoming message type | Public ROS topic | Published message type |
| --- | --- | --- | --- |
| `q2r_right_hand_pose` | `geometry_msgs/msg/PoseStamped` | `/q2_right/pose` | `geometry_msgs/msg/PoseStamped` |
| `q2r_left_hand_pose` | `geometry_msgs/msg/PoseStamped` | `/q2_left/pose` | `geometry_msgs/msg/PoseStamped` |
| `q2r_right_hand_twist` | `geometry_msgs/msg/Twist` | `/q2_right/velocity` | `geometry_msgs/msg/TwistStamped` |
| `q2r_left_hand_twist` | `geometry_msgs/msg/Twist` | `/q2_left/velocity` | `geometry_msgs/msg/TwistStamped` |
| `q2r_right_hand_inputs` | `quest2ros/msg/OVR2ROSInputs` | `/q2_right/button_{upper,lower,index,middle}` | `std_msgs/msg/Bool` on each topic |
| `q2r_left_hand_inputs` | `quest2ros/msg/OVR2ROSInputs` | `/q2_left/button_{upper,lower,index,middle}` | `std_msgs/msg/Bool` on each topic |

The button notation represents four separate topics per controller:
`button_upper`, `button_lower`, `button_index`, and `button_middle`.

- Pose and velocity headers use the ROS receipt time and `frame_id: base_link`.
  Setting the frame ID does not transform the coordinates; align the Quest
  controller frame with the intended robot base frame in the Quest app.
- Incoming `Twist` values are copied into `TwistStamped.twist` without scaling.
- Upper and lower buttons use `button_upper` and `button_lower` from the input
  message. Index and middle buttons are true only when `press_index` or
  `press_middle` is greater than `0.5`; a value of exactly `0.5` is false.
- Input messages are split into the four Boolean topics. Thumbstick values
  and analog trigger values are not published on these topics.

Publishers are created when the Quest registers its topics, so these topics
may not appear until the app connects. Other registered topic names retain
their original names and message types.

## Build and launch

This package depends on [`quest2ros`](https://github.com/Quest2ROS/quest2ros)
for the `OVR2ROSInputs` message type. Clone its ROS 2 branch into the same
workspace as this repository before building:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone --branch ros2 https://github.com/Quest2ROS/quest2ros.git
```

Place this repository at `~/ros2_ws/src/ros_tcp_communication`. With ROS 2
Humble installed, build both packages and source the workspace:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select quest2ros ros_tcp_endpoint
source install/setup.bash
```

For subsequent endpoint-only rebuilds, use
`colcon build --symlink-install --packages-select ros_tcp_endpoint`.

Start the endpoint:

```bash
ros2 launch ros_tcp_endpoint endpoint.py ros_ip:=0.0.0.0 ros_tcp_port:=10000
```

Both arguments are optional: `ros_ip` defaults to `0.0.0.0` (listen on all
interfaces), and `ros_tcp_port` defaults to `10000`. To bind only to a specific
interface, replace `0.0.0.0` with the host's current IP address on that interface.

## License
[Apache License 2.0](LICENSE)

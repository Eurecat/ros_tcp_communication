# Repository Instructions

## Scope

These instructions apply only to the `ros_tcp_communication` repository and
its descendants.

This is the active ROS TCP endpoint mounted by
`teleop_data_recording/docker/compose.yaml`. Do not edit the separate
`docker/deps/ROS-TCP-Endpoint` checkout when working on this package.

## Change Workflow

- Before editing, describe the files, functions, behavior, and reason for the
  proposed change.
- Do not modify files until the user explicitly approves the proposal.
- Implement only the approved scope. Stop and request approval if another
  change becomes necessary.
- Preserve user changes and avoid unrelated refactors, renames, formatting, or
  dependency changes.
- After editing, report the files and functions changed, behavior changed,
  risks, and validation performed.

## Documentation

Keep `README.md` independent of Docker and the teleop stack. Use generic ROS 2
workspace clone, `colcon build`, and launch instructions, and document the
`quest2ros` dependency with its repository link.

## Package Role

The package receives Unity/Quest messages over TCP and publishes ROS 2
messages. Keep the Quest wire topic names separate from the public ROS topic
names: the TCP registration keys must continue matching the names sent by the
Quest even when `RosPublisher` remaps the resulting ROS topics.

Use `rclpy.serialization.deserialize_message()` for incoming ROS 2 CDR
payloads. Do not manually unpack ROS messages with fixed byte offsets unless a
captured payload and ROS 2 serialization test prove that conversion is
required.

The current public Quest interface is:

- `/q2_right/pose` and `/q2_left/pose`:
  `geometry_msgs/msg/PoseStamped`
- `/q2_right/velocity` and `/q2_left/velocity`:
  `geometry_msgs/msg/TwistStamped`
- `/q2_{right,left}/button_{upper,lower,index,middle}`:
  `std_msgs/msg/Bool`

Pose and velocity messages use the ROS receipt time and `base_link` frame.
Index and middle analog triggers become true only when their value is greater
than `0.5`. Do not scale decoded velocities unless the user explicitly requests
it.

## Safety

- Do not power, move, or command robot hardware during tests without explicit
  user authorization.
- Prefer deterministic serialization tests and passive ROS topic inspection.
- Reject or surface malformed and non-finite motion data rather than silently
  forwarding unsafe values.
- Do not expose `.env` values, credentials, calibration data, packet captures,
  or other secrets in logs or responses.

## Build and Validation

The development service mounts this repository at
`/workspace/ros2_ws/src/ros_tcp_communication` in the ROS Humble container.

Run a syntax check for modified Python files:

```bash
python3 -m py_compile ros_tcp_endpoint/<modified_file>.py
```

Build the package in the existing development container:

```bash
docker exec docker-dev-soarm-publisher-1 bash -lc \
  'source /opt/ros/humble/setup.bash && cd /workspace/ros2_ws && \
   colcon build --symlink-install --packages-select ros_tcp_endpoint'
```

For message-path changes, validate with known serialized messages before using
live Quest data. Check topic names and types with `ros2 topic list -t`, then use
`ros2 topic echo --once` for passive live verification.

The endpoint uses CycloneDDS domain 88 and host networking. A bind error for a
configured address usually means the Wi-Fi/hotspot interface is down or its IP
changed; do not work around that by changing unrelated serialization code.

Treat Setuptools dash-key and `tests_require` output as existing warnings, not
build failures. Do not edit generated `build/`, `install/`, `log/`, or
`__pycache__/` content.

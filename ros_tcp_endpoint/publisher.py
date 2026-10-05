#  Copyright 2020 Unity Technologies
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import rclpy
import re

from geometry_msgs.msg import TwistStamped
from rclpy.serialization import deserialize_message
from std_msgs.msg import Bool

from .communication import RosSender


VELOCITY_TOPICS = {
    "q2r_right_hand_twist": "/q2_right/velocity",
    "q2r_left_hand_twist": "/q2_left/velocity",
}

POSE_TOPICS = {
    "q2r_right_hand_pose": "/q2_right/pose",
    "q2r_left_hand_pose": "/q2_left/pose",
}

BUTTON_NAMESPACES = {
    "q2r_right_hand_inputs": "/q2_right",
    "q2r_left_hand_inputs": "/q2_left",
}


class RosPublisher(RosSender):
    """
    Class to publish messages to a ROS topic
    """

    # TODO: surface latch functionality
    def __init__(self, topic, message_class, queue_size=10, latch=False):
        """

        Args:
            topic:         Topic name to publish messages to
            message_class: The message class in catkin workspace
            queue_size:    Max number of entries to maintain in an outgoing queue
        """
        strippedTopic = re.sub("[^A-Za-z0-9_]+", "", topic)
        node_name = f"{strippedTopic}_RosPublisher"
        RosSender.__init__(self, node_name)
        self.topic = topic  
        self.msg = message_class()
        self.button_pubs = {}

        button_namespace = BUTTON_NAMESPACES.get(topic)
        if button_namespace is None:
            output_topic = VELOCITY_TOPICS.get(topic, POSE_TOPICS.get(topic, topic))
            output_type = TwistStamped if topic in VELOCITY_TOPICS else message_class
            self.pub = self.create_publisher(output_type, output_topic, queue_size)
        else:
            self.pub = None
            for name in ("upper", "lower", "index", "middle"):
                self.button_pubs[name] = self.create_publisher(
                    Bool, f"{button_namespace}/button_{name}", queue_size
                )

    def send(self, data):
        """
        Takes in serialized message data from source outside of the ROS network,
        deserializes it into it's message class, and publishes the message to ROS topic.

        Args:
            data: The already serialized message_class data coming from outside of ROS

        Returns:
            None: Explicitly return None so behaviour can be
        """
        message_type = type(self.msg)
        message = deserialize_message(data, message_type)

        if self.button_pubs:
            button_values = {
                "upper": message.button_upper,
                "lower": message.button_lower,
                "index": message.press_index > 0.5,
                "middle": message.press_middle > 0.5,
            }
            for name, value in button_values.items():
                self.button_pubs[name].publish(Bool(data=bool(value)))
            return None

        if self.topic in VELOCITY_TOPICS:
            stamped_message = TwistStamped()
            stamped_message.header.stamp = self.get_clock().now().to_msg()
            stamped_message.header.frame_id = "base_link"
            stamped_message.twist = message
            self.pub.publish(stamped_message)
            return None

        if self.topic in POSE_TOPICS:
            message.header.stamp = self.get_clock().now().to_msg()
            message.header.frame_id = "base_link"

        self.pub.publish(message)

        return None

    def unregister(self):
        """

        Returns:

        """
        if self.pub is not None:
            self.destroy_publisher(self.pub)
        for publisher in self.button_pubs.values():
            self.destroy_publisher(publisher)
        self.destroy_node()

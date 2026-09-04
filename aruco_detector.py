import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from px4_msgs.msg import VehicleCommand

import cv2
import cv2.aruco as aruco


class ArucoDetector(Node):

    def __init__(self):
        super().__init__('aruco_detector')

        self.bridge = CvBridge()

        # ============================================================
        # ARUCO
        # ============================================================

        self.dictionary = aruco.getPredefinedDictionary(
            aruco.DICT_4X4_50
        )

        # Only land when ID 0 is detected
        self.target_id = 0

        # Prevent sending LAND command repeatedly
        self.land_command_sent = False

        # ============================================================
        # CAMERA
        # ============================================================

        self.camera_topic = (
            '/world/aruco/model/'
            'x500_mono_cam_down_0/link/camera_link/'
            'sensor/camera/image'
        )

        self.subscription = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            10
        )

        # ============================================================
        # PX4 VEHICLE COMMAND PUBLISHER
        # ============================================================

        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand,
            '/fmu/in/vehicle_command',
            10
        )

        self.get_logger().info(
            'ArUco detector started'
        )

        self.get_logger().info(
            'Waiting for ArUco ID 0...'
        )

    # ================================================================
    # CAMERA CALLBACK
    # ================================================================

    def image_callback(self, msg):

        try:

            # ROS Image → OpenCV image
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

        except Exception as e:

            self.get_logger().error(
                f'Could not convert image: {e}'
            )

            return

        # ============================================================
        # GRAYSCALE
        # ============================================================

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # ============================================================
        # ARUCO DETECTION
        # ============================================================

        corners, ids, rejected = aruco.detectMarkers(
            gray,
            self.dictionary
        )

        # ============================================================
        # MARKER DETECTED
        # ============================================================

        if ids is not None:

            aruco.drawDetectedMarkers(
                frame,
                corners,
                ids
            )

            for marker_id in ids.flatten():

                print(
                    f'MARKER DETECTED | ID={marker_id}'
                )

                # ----------------------------------------------------
                # CHECK FOR TARGET ID
                # ----------------------------------------------------

                if marker_id == self.target_id:

                    cv2.putText(
                        frame,
                        'TARGET DETECTED - LANDING',
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                    # ------------------------------------------------
                    # SEND LAND COMMAND ONLY ONCE
                    # ------------------------------------------------

                    if not self.land_command_sent:

                        self.get_logger().info(
                            'ARUCO ID 0 DETECTED!'
                        )

                        self.get_logger().info(
                            'SENDING PX4 LAND COMMAND'
                        )

                        self.send_land_command()

                        self.land_command_sent = True

                    break

        else:

            cv2.putText(
                frame,
                'SEARCHING FOR ARUCO ID 0',
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # ============================================================
        # DISPLAY
        # ============================================================

        cv2.imshow(
            'Precision Landing - GAZEBO CAMERA',
            frame
        )

        cv2.waitKey(1)

    # ================================================================
    # PX4 LAND COMMAND
    # ================================================================

    def send_land_command(self):

        msg = VehicleCommand()

        msg.timestamp = (
            self.get_clock()
            .now()
            .nanoseconds // 1000
        )

        # PX4 LAND command
        msg.command = (
            VehicleCommand.VEHICLE_CMD_NAV_LAND
        )

        # Default parameters
        msg.param1 = 0.0
        msg.param2 = 0.0

        # PX4 system/component
        msg.target_system = 1
        msg.target_component = 1

        msg.source_system = 1
        msg.source_component = 1

        # Command comes from external application
        msg.from_external = True

        self.vehicle_command_pub.publish(msg)

        self.get_logger().info(
            'PX4 LAND COMMAND SENT'
        )


# ====================================================================
# MAIN
# ====================================================================

def main(args=None):

    rclpy.init(args=args)

    node = ArucoDetector()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()

        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

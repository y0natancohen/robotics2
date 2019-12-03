#!/usr/bin/env python
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist


cmd_vel_pub = None
bridge = None
speed = 0.2
rotation_speed = 0.4
distance_upper_bound = 0.55
distance_lower_bound = 0.45

stop_vec = Twist()
stop_vec.angular.x = 0
stop_vec.angular.y = 0
stop_vec.angular.z = 0
stop_vec.linear.x = 0
stop_vec.linear.y = 0
stop_vec.linear.z = 0

forward_vec = Twist()
forward_vec.angular.x = 0
forward_vec.angular.y = 0
forward_vec.angular.z = 0
forward_vec.linear.x = speed
forward_vec.linear.y = 0
forward_vec.linear.z = 0

right_vec = Twist()
right_vec.angular.x = 0
right_vec.angular.y = 0
right_vec.angular.z = -rotation_speed
right_vec.linear.x = speed / 2
right_vec.linear.y = 0
right_vec.linear.z = 0


left_vec = Twist()
left_vec.angular.x = 0
left_vec.angular.y = 0
left_vec.angular.z = rotation_speed
left_vec.linear.x = speed / 2
left_vec.linear.y = 0
left_vec.linear.z = 0

goal_achieved = False


def is_yellow(b, g, r):
    return b < 10 and g > 240 and r > 240


def is_white(b, g, r):
    return b > 210 and g > 240 and r > 240


def decide_direction(cv_image):
    lowest_row = cv_image[-1:, :, :][0]
    for bgr in lowest_row:
        b, g, r = bgr
        if is_yellow(b, g, r):
            return left_vec
        if is_white(b, g, r):
            return right_vec
    return forward_vec


def drive_loop_callback(image_data):
    if not goal_achieved:
        cv_image = bridge.imgmsg_to_cv2(image_data, "bgr8")
        vector = decide_direction(cv_image)
        cmd_vel_pub.publish(vector)


def scanner_callback(scanner_data):
    print "hi"
    global goal_achieved

    if isinstance(scanner_data, LaserScan):
        to_the_right_distances = scanner_data.ranges[265: 275]
        for distance in to_the_right_distances:
            if distance_lower_bound < distance < distance_upper_bound:
                cmd_vel_pub.publish(stop_vec)
                goal_achieved = True


def driver():
    global cmd_vel_pub, bridge
    bridge = CvBridge()
    rospy.init_node('driver', anonymous=True)
    cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber("/camera/rgb/image_raw", Image, drive_loop_callback)
    rospy.Subscriber("/scan", LaserScan, scanner_callback)
    print("starting to listen on topic '/camera/rgb/image_raw'")
    print "starting to drive"

    rospy.spin()


if __name__ == '__main__':
    try:
        driver()
    except rospy.ROSInterruptException:
        pass

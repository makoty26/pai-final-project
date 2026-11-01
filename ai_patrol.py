import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import torch
import numpy as np

class AIPatrolNode(Node):
    def __init__(self):
        super().__init__('ai_patrol_node')
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/model/my_robot/cmd_vel', 10)
        self.bridge = CvBridge()
        
        self.state = 'PATROL'
        self.action_timer = 0
        
        self.get_logger().info("Edge Patrol Node Started...")

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        tensor_image = torch.from_numpy(cv_image)
        
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        
        defect_score = torch.tensor(mask).sum().item()
        twist = Twist()

        # 【修正】しきい値を4500万へ大幅引き上げ。壁が目前に迫るまで反応しない。
        PROXIMITY_THRESHOLD = 45000000 

        if self.state == 'STOP':
            self.get_logger().warn(f"STOPPING... ({self.action_timer})")
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.state = 'TURN'
                self.action_timer = 15  
                
        elif self.state == 'TURN':
            self.get_logger().warn(f"TURNING LEFT... ({self.action_timer})")
            twist.linear.x = 0.0        
            twist.angular.z = 1.0
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.state = 'ESCAPE'   
                self.action_timer = 30  
                
        elif self.state == 'ESCAPE':
            self.get_logger().info(f"ESCAPING FROM WALL... ({self.action_timer})")
            twist.linear.x = 0.5        
            twist.angular.z = 0.0
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.state = 'PATROL'   
                
        elif self.state == 'PATROL':
            if defect_score > PROXIMITY_THRESHOLD:
                self.get_logger().warn(f"WALL CLOSE! Stopping first. (Score: {defect_score})")
                self.state = 'STOP'
                self.action_timer = 10
                twist.linear.x = 0.0
                twist.angular.z = 0.0
            else:
                self.get_logger().info(f"Patrolling safely... (Score: {defect_score})")
                twist.linear.x = 0.5
                twist.angular.z = 0.0

        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = AIPatrolNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
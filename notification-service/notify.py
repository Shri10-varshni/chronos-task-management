import pika
import json
import time

class NotificationSender:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='task_notifications', durable=True)

    def send_notification(self, task_id: int, message: str):
        notification_data = {
            "task_id": task_id,
            "message": message
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='task_notifications',
            body=json.dumps(notification_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(f"Notification sent for Task {task_id}: {message}")

    def close(self):
        self.connection.close()

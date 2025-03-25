from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from . import notify

app = FastAPI()
notification_sender = notify.NotificationSender()

class NotificationRequest(BaseModel):
    task_id: int
    due_date: str

@app.post("/send-notification/")
def send_notification(notification: NotificationRequest, background_tasks: BackgroundTasks):
    due_date = datetime.strptime(notification.due_date, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()

    time_diff = (due_date - current_time).total_seconds()

    if time_diff > 0:
        # Simulate sending a notification in the future (e.g., reminder 1 hour before due date)
        background_tasks.add_task(notification_sender.send_notification, notification.task_id, f"Reminder: Task {notification.task_id} is due in {time_diff / 3600:.1f} hours.")
        return {"message": "Notification scheduled successfully."}
    else:
        return {"message": "Task is overdue, no notification sent."}

@app.on_event("shutdown")
def shutdown_event():
    notification_sender.close()

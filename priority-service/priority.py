from datetime import datetime

def calculate_priority(due_date: str, description: str) -> str:
    # Simple priority calculation based on due date and description
    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()

    time_diff = (due_date_obj - current_time).total_seconds()

    if time_diff < 0:
        return "High"  # Past due tasks are high priority
    elif time_diff < 86400:  # Less than a day
        return "Medium"
    else:
        return "Low"

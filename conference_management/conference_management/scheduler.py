from conference_management.conference_management.api.apis import send_daily_session_recommendations

def daily_task_scheduler():
    """
    Function to handle daily tasks, such as sending session recommendations.
    """
    send_daily_session_recommendations()

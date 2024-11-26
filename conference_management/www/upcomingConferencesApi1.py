import frappe

def get_context(context):
    """
    Load upcoming and ongoing conferences and their sessions for the web page.
    """
    # Fetch all conferences with status Upcoming or Ongoing
    conferences = frappe.get_all(
        "Conference",
        fields=["conference_name", "start_date", "end_date", "status"],
        filters={"status": ["in", ["Upcoming", "Ongoing"]]},
        order_by="start_date ASC"
    )

    for conference in conferences:
        # Fetch related sessions
        sessions = frappe.get_all(
            "Session",
            fields=["session_name", "speaker", "start_time", "end_time"],
            filters={"conference": conference.conference_name},
            order_by="start_time ASC"
        )
        conference["sessions"] = sessions

    # Pass the data to the template
    context.conferences = conferences
    return context

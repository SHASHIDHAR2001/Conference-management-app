import frappe
from frappe.utils import get_datetime, now
def get_context(context):
    """
    Load upcoming and ongoing conferences and their sessions for the web page.
    """
    current_time = get_datetime(now())  # Current date and time

    # Fetch all conferences with status Upcoming or Ongoing
    conferences = frappe.get_all(
        "Conference",
        fields=["conference_name", "start_date", "end_date", "status"],
        filters={"status": ["in", ["Upcoming", "Ongoing"]]},
        order_by="start_date ASC"
    )

    valid_conferences = []

    for conference in conferences:
        # Convert start and end dates of the conference to datetime objects
        conference_start = get_datetime(conference["start_date"])
        conference_end = get_datetime(conference["end_date"])

        if conference_end < current_time:
            # Skip expired conferences
            continue

        if conference_start > current_time:
            status = "Upcoming"
        else:
            status = "Ongoing"

        # Fetch related sessions only if the conference is valid (Upcoming or Ongoing)
        sessions = frappe.get_all(
            "Session",
            fields=["session_name", "speaker", "start_time", "end_time"],
            filters={"conference": conference["conference_name"]},
            order_by="start_time ASC"
        )

        # Only add conferences with sessions
        if sessions:
            conference["sessions"] = sessions
            conference["status"] = status
            valid_conferences.append(conference)

    # Pass the data to the template
    context.conferences = valid_conferences
    return context

# import frappe
# from frappe.utils import get_datetime, now

# def get_context(context):
#     """
#     Load upcoming and ongoing conferences and their sessions for the web page.
#     """
#     current_time = get_datetime(now()) 
#     # Fetch all conferences with status Upcoming or Ongoing
#     conferences = frappe.get_all(
#         "Conference",
#         fields=["conference_name", "start_date", "end_date", "status"],
#         filters={"status": ["in", ["Upcoming", "Ongoing"]]},
#         order_by="start_date ASC"
#     )

#     for conference in conferences:

#         # Convert start and end dates of the conference to datetime objects
#         conference_start = get_datetime(conference["start_date"])
#         conference_end = get_datetime(conference["end_date"])

#         if conference_start > current_time:
#             # Upcoming conference
#             status = "Upcoming"
#         elif conference_end < current_time:
#             # Completed conference, skip it
#             continue
#         else:
#             status = "Ongoing"
#         # Fetch related sessions
#         sessions = frappe.get_all(
#             "Session",
#             fields=["session_name", "speaker", "start_time", "end_time"],
#             filters={"conference": conference.conference_name},
#             order_by="start_time ASC"
#         )
#         conference["sessions"] = sessions

#     # Pass the data to the template
#     context.conferences = conferences
#     return context
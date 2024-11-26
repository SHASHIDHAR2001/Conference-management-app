import frappe
from frappe.utils import formatdate

@frappe.whitelist(allow_guest=True)
def getupcomingConference():
    """
    Load upcoming and ongoing conferences and their sessions as JSON.
    """
    try:
        # Fetch all conferences with status Upcoming or Ongoing
        conferences = frappe.get_all(
            "Conference",
            fields=["conference_name", "start_date", "end_date", "status"],
            filters={"status": ["in", ["Upcoming", "Ongoing"]]},
            order_by="start_date ASC"
        )

        # Process dates and fetch related sessions for each conference
        for conference in conferences:
            # Convert date fields to string
            conference["start_date"] = str(conference["start_date"]) if conference["start_date"] else None
            conference["end_date"] = str(conference["end_date"]) if conference["end_date"] else None

            # Fetch related sessions
            sessions = frappe.get_all(
                "Session",
                fields=["session_name", "speaker", "start_time", "end_time"],
                filters={"conference": conference["conference_name"]},
                order_by="start_time ASC"
            )

            # Convert session date fields to string
            for session in sessions:
                session["start_time"] = str(session["start_time"]) if session["start_time"] else None
                session["end_time"] = str(session["end_time"]) if session["end_time"] else None

            # Add sessions to each conference entry
            conference["sessions"] = sessions

        # Return conferences as a dictionary
        return {"conferences": conferences}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching upcoming conferences")
        return {"error": str(e)}

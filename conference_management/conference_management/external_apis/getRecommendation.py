import frappe,json
from frappe.utils import now
from datetime import date


@frappe.whitelist(allow_guest=True)
def get_recommendations(attendee_email):
    """
    Fetch recommended conferences, sessions, and speakers for an attendee based on their preferences 
    and the sessions they've registered for.
    Args:
        attendee_email (str): The email address of the attendee.
    Returns:
        dict: Recommendations grouped by conferences, their sessions, and speakers.
    """
    try:
        # Step 1: Validate attendee email
        if not attendee_email:
            frappe.throw("Attendee email is required.")

        attendee = frappe.db.get_value("Attendee", {"email": attendee_email}, ["name", "attendee_name"], as_dict=True)
        if not attendee:
            frappe.throw("Attendee not found.")

        attendee_name = attendee["attendee_name"]

        # Step 2: Fetch preferences from Preferences child table in Attendee doctype
        preferences = frappe.get_all(
            "Preference",
            filters={"parent": attendee["name"]},
            fields=["session"]
        )
        preferred_sessions = [pref["session"] for pref in preferences]

        # Step 3: Fetch registered sessions from Registration doctype
        registrations = frappe.get_all(
            "Registration",
            filters={"attendee": attendee["name"]},
            fields=["session"]
        )
        registered_sessions = [reg["session"] for reg in registrations]

        # Combine all sessions of interest
        all_sessions = list(set(preferred_sessions + registered_sessions))

        # Step 4: Fetch all matching sessions
        sessions = frappe.get_all(
            "Session",
            filters={"name": ["in", all_sessions]},
            fields=["name", "session_name", "speaker", "start_time", "end_time", "conference", "session_fee"]
        )

        # Extract all speakers associated with these sessions
        speakers = set(session["speaker"] for session in sessions if session["speaker"])

        # Step 5: Fetch additional sessions based on matched speakers
        speaker_sessions = frappe.get_all(
            "Session",
            filters={"speaker": ["in", list(speakers)]},
            fields=["name", "session_name", "speaker", "start_time", "end_time", "conference", "session_fee"]
        )

        # Merge sessions and deduplicate
        all_sessions_details = {session["name"]: session for session in sessions + speaker_sessions}.values()

        # Step 6: Organize sessions by conference
        recommendations = {}
        for session in all_sessions_details:
            conference_name = frappe.db.get_value("Conference", session["conference"], "conference_name")
            if session["conference"] not in recommendations:
                recommendations[session["conference"]] = {
                    "conference_name": conference_name,
                    "start_date": frappe.db.get_value("Conference", session["conference"], "start_date"),
                    "end_date": frappe.db.get_value("Conference", session["conference"], "end_date"),
                    "status": frappe.db.get_value("Conference", session["conference"], "status"),
                    "sessions": [],
                    "speakers": set()
                }

            # Add session details
            recommendations[session["conference"]]["sessions"].append({
                "session_name": session["session_name"],
                "speaker": session["speaker"],
                "start_time": session["start_time"],
                "end_time": session["end_time"],
                "session_fee": session["session_fee"]
            })

            # Add speakers
            if session["speaker"]:
                recommendations[session["conference"]]["speakers"].add(session["speaker"])

        # Convert speakers set to list for JSON serialization
        for conf in recommendations.values():
            conf["speakers"] = list(conf["speakers"])

        # Optional: Log API call
        log_api_request(attendee_email, recommendations)

        # Return structured data
        return {"message": {
            "attendee": attendee_name,
            "conferences": list(recommendations.values())
        }}

    except frappe.ValidationError as e:
        frappe.log_error(str(e), "Get Recommendations API Validation Error")
        return {"error": str(e)}

    except Exception as e:
        frappe.log_error(str(e), "Get Recommendations API Error")
        return {"error": f"An unexpected error occurred: {str(e)}"}


def serialize_data(obj):
    """
    Serialize unsupported objects like date to a JSON-serializable format.
    """
    if isinstance(obj, date):
        return obj.isoformat()  
    raise TypeError(f"Type {type(obj)} not serializable")

## Logging logs for both exception and results
def log_api_request(attendee_email, recommendations=None, error_message=None):
    """
    Log API request and response to the APILog doctype.

    Args:
        attendee_email (str): The attendee's email.
        recommendations (dict): The recommendations returned by the API.
    """
    try:
        # Serialize recommendations with custom serialization
        response_body = (
            json.dumps(recommendations, default=serialize_data)
            if recommendations is not None
            else error_message
        )
        api_endpoint = "/api/method/conference_management.external_apis.get_recommendations"
        
        frappe.get_doc({
            "doctype": "APILog",
            "api_endpoint": api_endpoint,
            "method": "GET",
            "request_body": json.dumps({"attendee_email": attendee_email}),  # Serialize request
            "response_body": response_body,  # Serialized response
            "timestamp": now(),
            "status_code": 500 if error_message else 200,
        }).insert(ignore_permissions=True)
        
        # Commit the transaction
        frappe.db.commit()
    except Exception as e:
        # Log the exception in case of failure
        frappe.log_error(f"Failed to log API request: {str(e)}", "API Log Failure")
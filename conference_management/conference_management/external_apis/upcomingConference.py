import frappe,json
from frappe.utils import get_datetime, now
from datetime import date

@frappe.whitelist(allow_guest=True)
def getupcomingConference():
    """
    Load upcoming and ongoing conferences and their sessions.
    """
    try:
        # current time to filter expired conferences and sessions
        current_time = get_datetime(now())

        query = """
            SELECT 
                c.name AS conference_id, 
                c.conference_name, 
                c.start_date, 
                c.end_date, 
                c.status, 
                c.description,
                s.session_name,
                s.name, 
                s.speaker, 
                s.start_time, 
                s.end_time, 
                s.session_fee
            FROM 
                `tabConference` c
            LEFT JOIN 
                `tabSession` s
            ON 
                c.name = s.conference
            WHERE 
                c.status IN ('Upcoming', 'Ongoing')
                AND c.end_date >= %(current_time)s
                # AND (s.end_time >= %(current_time)s)
            ORDER BY 
                c.start_date ASC, s.start_time ASC;
        """

        data = frappe.db.sql(query, {"current_time": current_time}, as_dict=True)

        # Group data into conferences with their sessions
        conferences = {}
        for row in data:
            conference_id = row["conference_id"]
            if conference_id not in conferences:
                conferences[conference_id] = {
                    "conference_name": row["conference_name"],
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "status": row["status"],
                    "description": row["description"],
                    "sessions": []
                }
            if row["session_name"]:  # Add session details if available
                conferences[conference_id]["sessions"].append({
                    "session_name": row["session_name"],
                    "speaker": row["speaker"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "session_fee": row["session_fee"],
                    "name": row['name']
                })

        # Convert grouped conferences to a list for context
        context = {"conferences": list(conferences.values())}

        # If no conferences are found
        if not context["conferences"]:
            context["error_message"] = "No matching conferences or sessions found."
        log_api_request(conferences)

        return context

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching upcoming conferences")
        return {"error": str(e)}

def log_api_request(conferences):
    """
    Log the API request and response to the APILog doctype.

        conferences (list): The matching records returned in the response.
    """
    request_body = {"getallupcomingconferences": True}
    
    try:
        time_stamp = now()
        print(f"Timestamp: {time_stamp}")
        
        # Convert conferences list to JSON string
        conferences_json = json.dumps(conferences, default=serialize_date)

        print(f"Conferences JSON: {conferences_json}")
        
        method = "GET"
        status_code = 200
        api_endpoint = "/getupcomingConference"
        
        # Create the API log entry
        api_log = frappe.get_doc({
            "doctype": "APILog",
            "api_endpoint": api_endpoint,
            "request_body": json.dumps(request_body),  # Serialize request body
            "response_body": conferences_json,  # Serialized response body
            "method": method,
            "status_code": status_code,
            "timestamp": time_stamp
        })
        
        print("Inserting log...")
        api_log.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Log inserted successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")

def serialize_date(obj):
    """
    Serialize unsupported objects like date to a JSON-serializable format.
    """
    if isinstance(obj, date):
        return obj.isoformat()  # Convert date to ISO 8601 string format
    raise TypeError("Type not serializable")



# import frappe
# from frappe.utils import formatdate

# @frappe.whitelist(allow_guest=True)
# def getupcomingConference():
#     """
#     Load upcoming and ongoing conferences and their sessions as JSON.
#     """
#     try:
#         # Fetch all conferences with status Upcoming or Ongoing
#         conferences = frappe.get_all(
#             "Conference",
#             fields=["conference_name", "start_date", "end_date", "status"],
#             filters={"status": ["in", ["Upcoming", "Ongoing"]]},
#             order_by="start_date ASC"
#         )

#         # Process dates and fetch related sessions for each conference
#         for conference in conferences:
#             # Convert date fields to string
#             conference["start_date"] = str(conference["start_date"]) if conference["start_date"] else None
#             conference["end_date"] = str(conference["end_date"]) if conference["end_date"] else None

#             # Fetch related sessions
#             sessions = frappe.get_all(
#                 "Session",
#                 fields=["session_name", "speaker", "start_time", "end_time"],
#                 filters={"conference": conference["conference_name"]},
#                 order_by="start_time ASC"
#             )

#             # Convert session date fields to string
#             for session in sessions:
#                 session["start_time"] = str(session["start_time"]) if session["start_time"] else None
#                 session["end_time"] = str(session["end_time"]) if session["end_time"] else None

#             # Add sessions to each conference entry
#             conference["sessions"] = sessions

#         # Return conferences as a dictionary
#         return {"conferences": conferences}

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Error fetching upcoming conferences")
#         return {"error": str(e)}

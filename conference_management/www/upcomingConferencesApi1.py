import frappe,json
from frappe.utils import now
from frappe import _
from datetime import date
def get_context(context):

    current_time = now()  # Get current date and time
    
    # SQL query to fetch conferences and sessions
    query = """
    SELECT 
        c.conference_name AS conference_name,
        c.start_date AS start_date,
        c.end_date AS end_date,
        CASE
            WHEN c.start_date > %(current_time)s THEN 'Upcoming'
            WHEN c.end_date >= %(current_time)s THEN 'Ongoing'
        END AS status,
        s.session_name AS session_name,
        s.speaker AS speaker,
        s.start_time AS start_time,
        s.end_time AS end_time
    FROM 
        `tabConference` c
    LEFT JOIN 
        `tabSession` s
    ON 
        c.conference_name = s.conference
    WHERE 
        c.end_date >= %(current_time)s
    ORDER BY 
        c.start_date ASC,
        s.start_time ASC;
    """
    
    # Execute the SQL query
    data = frappe.db.sql(query, {"current_time": current_time}, as_dict=True)
    
    # Group sessions under conferences
    conferences = {}
    for row in data:
        conference_name = row.get("conference_name") 
        if conference_name not in conferences:
            # Initialize a conference entry if it doesn't exist
            conferences[conference_name] = {
                "conference_name": conference_name,
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "status": row["status"],
                "sessions": []
            }
        # Add session details if available
        if row["session_name"]:  # Only add sessions if they exist
            conferences[conference_name]["sessions"].append({
                "session_name": row["session_name"],
                "speaker": row["speaker"],
                "start_time": row["start_time"],
                "end_time": row["end_time"]
            })
    
    # Convert grouped conferences to a list for template context
    context.conferences = list(conferences.values())
    log_api_request(conferences)
    return context

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
        api_endpoint = "/upcomingConferencesApi1"
        
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
        # Print the exception error message for debugging
        print(f"Error: {str(e)}")

def serialize_date(obj):
    """
    Serialize unsupported objects like date to a JSON-serializable format.
    """
    if isinstance(obj, date):
        return obj.isoformat()  # Convert date to ISO 8601 string format
    raise TypeError("Type not serializable")













# import frappe
# from frappe.utils import get_datetime, now
# def get_context(context):
#     """
#     Load upcoming and ongoing conferences and their sessions for the web page.
#     """
#     current_time = get_datetime(now())  # Current date and time

#     # Fetch all conferences with status Upcoming or Ongoing
#     conferences = frappe.get_all(
#         "Conference",
#         fields=["conference_name", "start_date", "end_date", "status"],
#         filters={"status": ["in", ["Upcoming", "Ongoing"]]},
#         order_by="start_date ASC"
#     )

#     valid_conferences = []

#     for conference in conferences:
#         # Convert start and end dates of the conference to datetime objects
#         conference_start = get_datetime(conference["start_date"])
#         conference_end = get_datetime(conference["end_date"])

#         if conference_end < current_time:
#             # Skip expired conferences
#             continue

#         if conference_start > current_time:
#             status = "Upcoming"
#         else:
#             status = "Ongoing"

#         # Fetch related sessions only if the conference is valid (Upcoming or Ongoing)
#         sessions = frappe.get_all(
#             "Session",
#             fields=["session_name", "speaker", "start_time", "end_time"],
#             filters={"conference": conference["conference_name"]},
#             order_by="start_time ASC"
#         )

#         # Only add conferences with sessions
#         if sessions:
#             conference["sessions"] = sessions
#             conference["status"] = status
#             valid_conferences.append(conference)

#     # Pass the data to the template
#     context.conferences = valid_conferences
#     return context
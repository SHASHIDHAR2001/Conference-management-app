import frappe,json
from frappe.utils import now
from frappe import _
from datetime import date
from frappe.utils import now, get_datetime

def get_context(context):
    """
    Fetch upcoming and ongoing conferences along with their sessions.
    """
    try:
        keyword = frappe.form_dict.get('keyword')  # Get search keyword from the URL query string
        keyword_filter = f"%{keyword.lower()}%" if keyword else None
        current_time = get_datetime(now())

        # Constructing the dynamic WHERE clause for keyword filtering
        keyword_clause = ""
        if keyword_filter:
            keyword_clause = """
            AND (LOWER(c.conference_name) LIKE %(keyword)s OR 
                 LOWER(s.session_name) LIKE %(keyword)s OR 
                 LOWER(s.speaker) LIKE %(keyword)s)
            """

        # SQL query to fetch conferences and their sessions
        query = f"""
        SELECT 
            c.name AS conference_id,
            c.conference_name,
            c.start_date,
            c.end_date,
            c.status,
            c.description,
            s.session_name,
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
            {keyword_clause}
            # AND (
            #     s.end_time >= %(current_time)s 
            # )
        ORDER BY 
            c.name ASC, s.start_time ASC;
        """

        # Execute the query
        data = frappe.db.sql(
            query,
            {"keyword": keyword_filter,"current_time": current_time},
            as_dict=True
        )

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
                    "session_fee": row["session_fee"]
                })

        # Convert grouped conferences to a list for context
        context.conferences = list(conferences.values())

        # If no conferences are found
        if not context.conferences:
            context.error_message = "No matching conferences or sessions found."

        log_api_request(keyword, conferences)
        return context

    except Exception as e:
        frappe.log_error(f"Error in get_context: {str(e)}", "Conference Context Error")
        context.error_message = f"An error occurred: {str(e)}"
        return context

def serialize_date(obj):
    """
    Serialize unsupported objects like date to a JSON-serializable format.
    """
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def log_api_request(keyword, conferences):
    """
    Log the API request and response to the APILog doctype.

    Args:
        keyword (str): The search keyword used in the request.
        conferences (list): The matching records returned in the response.
    """
    request_body = {"keyword": keyword}
    
    try:
        time_stamp = now()
        print(f"Timestamp: {time_stamp}")
        
        # Convert conferences list to JSON string
        conferences_json = json.dumps(conferences, default=serialize_date)

        print(f"Conferences JSON: {conferences_json}")
        
        method = "GET"
        status_code = 200
        api_endpoint = "/SearchconferenceSessionApi1"
        
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














# def get_context(context):
#     """
#     Load upcoming and ongoing conferences and their sessions for the web page.
#     Search sessions across all conferences for a keyword and include all conferences.
#     If no sessions match, search conferences directly by keyword.
#     """
#     try:
#         keyword = frappe.form_dict.get('keyword')  # Get search keyword from the URL query string
#         keyword_filter = f"%{keyword.lower()}%" if keyword else None

#         # SQL query to fetch all conferences (Upcoming and Ongoing)
#         conference_query = """
#             SELECT 
#                 name, conference_name, start_date, end_date, status, description
#             FROM 
#                 `tabConference`
#             WHERE 
#                 status IN ('Upcoming', 'Ongoing')
#             ORDER BY 
#                 start_date ASC
#         """
#         conferences = frappe.db.sql(conference_query, as_dict=True)

#         if not conferences:
#             context.conferences = []
#             return context

#         conference_ids = [conf['name'] for conf in conferences]

#         # SQL query to fetch sessions across all conferences
#         session_query = """
#             SELECT 
#                 conference, session_name, speaker, start_time, end_time, session_fee
#             FROM 
#                 `tabSession`
#             WHERE 
#                 {keyword_clause}
#                 conference IN %(conference_ids)s
#             ORDER BY 
#                 start_time ASC
#         """.format(
#             keyword_clause="(LOWER(session_name) LIKE %(keyword)s OR LOWER(speaker) LIKE %(keyword)s) AND" if keyword_filter else ""
#         )

#         sessions = frappe.db.sql(
#             session_query,
#             {"conference_ids": tuple(conference_ids), "keyword": keyword_filter},
#             as_dict=True
#         )

#         # Group sessions by conference
#         session_map = {}
#         for session in sessions:
#             session_map.setdefault(session['conference'], []).append(session)

#         # Attach sessions to their respective conferences
#         for conference in conferences:
#             conference["sessions"] = session_map.get(conference['name'], [])

#         # If searching and no sessions match, perform a secondary search for conferences by keyword
#         if keyword:
#             conferences_with_sessions = [conf for conf in conferences if conf["sessions"]]
#             if not conferences_with_sessions:
#                 # Secondary search for conferences by keyword
#                 conference_keyword_query = """
#                     SELECT 
#                         name, conference_name, start_date, end_date, status, description
#                     FROM 
#                         `tabConference`
#                     WHERE 
#                         status IN ('Upcoming', 'Ongoing') AND
#                         LOWER(conference_name) LIKE %(keyword)s
#                     ORDER BY 
#                         start_date ASC
#                 """
#                 conferences = frappe.db.sql(
#                     conference_keyword_query, {"keyword": keyword_filter}, as_dict=True
#                 )
#             else:
#                 conferences = conferences_with_sessions

#         # If no conferences are found after both searches
#         if not conferences:
#             context.conferences = []
#             context.error_message = "No matching conferences or sessions found."
#         else:
#             context.conferences = conferences

#         log_api_request(keyword, conferences)

#         return context

#     except frappe.exceptions.DoesNotExistError as e:
#         frappe.log_error(f"Error while fetching conferences or sessions: {str(e)}", "Get Context")
#         context.error_message = f"An error occurred while fetching the data. Please try again later. Details: {str(e)}"
#         return context

#     except Exception as e:
#         frappe.log_error(f"Unexpected error: {str(e)}", "Get Context")
#         context.error_message = f"An unexpected error occurred. Please try again later: {str(e)}"
#         return context
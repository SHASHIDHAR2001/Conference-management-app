import frappe,json
from frappe.utils import now
from frappe import _
from datetime import date

def get_context(context):
    """
    Load upcoming and ongoing conferences and their sessions for the web page.
    Search sessions across all conferences for a keyword and include all conferences.
    If no sessions match, search conferences directly by keyword.
    """
    try:
        keyword = frappe.form_dict.get('keyword')  # Get search keyword from the URL query string
        keyword_filter = f"%{keyword.lower()}%" if keyword else None

        # SQL query to fetch all conferences (Upcoming and Ongoing)
        conference_query = """
            SELECT 
                name, conference_name, start_date, end_date, status, description
            FROM 
                `tabConference`
            WHERE 
                status IN ('Upcoming', 'Ongoing')
            ORDER BY 
                start_date ASC
        """
        conferences = frappe.db.sql(conference_query, as_dict=True)

        if not conferences:
            context.conferences = []
            return context

        conference_ids = [conf['name'] for conf in conferences]

        # SQL query to fetch sessions across all conferences
        session_query = """
            SELECT 
                conference, session_name, speaker, start_time, end_time, session_fee
            FROM 
                `tabSession`
            WHERE 
                {keyword_clause}
                conference IN %(conference_ids)s
            ORDER BY 
                start_time ASC
        """.format(
            keyword_clause="(LOWER(session_name) LIKE %(keyword)s OR LOWER(speaker) LIKE %(keyword)s) AND" if keyword_filter else ""
        )

        sessions = frappe.db.sql(
            session_query,
            {"conference_ids": tuple(conference_ids), "keyword": keyword_filter},
            as_dict=True
        )

        # Group sessions by conference
        session_map = {}
        for session in sessions:
            session_map.setdefault(session['conference'], []).append(session)

        # Attach sessions to their respective conferences
        for conference in conferences:
            conference["sessions"] = session_map.get(conference['name'], [])

        # If searching and no sessions match, perform a secondary search for conferences by keyword
        if keyword:
            conferences_with_sessions = [conf for conf in conferences if conf["sessions"]]
            if not conferences_with_sessions:
                # Secondary search for conferences by keyword
                conference_keyword_query = """
                    SELECT 
                        name, conference_name, start_date, end_date, status, description
                    FROM 
                        `tabConference`
                    WHERE 
                        status IN ('Upcoming', 'Ongoing') AND
                        LOWER(conference_name) LIKE %(keyword)s
                    ORDER BY 
                        start_date ASC
                """
                conferences = frappe.db.sql(
                    conference_keyword_query, {"keyword": keyword_filter}, as_dict=True
                )
            else:
                conferences = conferences_with_sessions

        # If no conferences are found after both searches
        if not conferences:
            context.conferences = []
            context.error_message = "No matching conferences or sessions found."
        else:
            context.conferences = conferences

        log_api_request(keyword, conferences)

        return context

    except frappe.exceptions.DoesNotExistError as e:
        frappe.log_error(f"Error while fetching conferences or sessions: {str(e)}", "Get Context")
        context.error_message = f"An error occurred while fetching the data. Please try again later. Details: {str(e)}"
        return context

    except Exception as e:
        frappe.log_error(f"Unexpected error: {str(e)}", "Get Context")
        context.error_message = f"An unexpected error occurred. Please try again later: {str(e)}"
        return context

def serialize_date(obj):
    """
    Serialize unsupported objects like date to a JSON-serializable format.
    """
    if isinstance(obj, date):
        return obj.isoformat()  # Convert date to ISO 8601 string format
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
        api_endpoint = "/SerchconferenceSessionApi1"
        
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
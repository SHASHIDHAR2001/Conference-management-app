import frappe
from frappe.utils import now

@frappe.whitelist(allow_guest=True)
def get_registered_sessions():
    email = frappe.form_dict.get('attendee_email')
    print(email)
    """
    Fetch registered sessions for a specific attendee.
    """
    try:
        query = """
            SELECT 
                r.session AS session_id,
                s.session_name, 
                s.start_time, 
                s.end_time,
                c.conference_name,  
                s.speaker
            FROM 
                tabRegistration r
            LEFT JOIN 
                tabSession s ON r.session = s.name
            LEFT JOIN 
                tabConference c ON r.conference = c.name
            WHERE 
                r.attendee = %(email)s
            ORDER BY 
                s.start_time ASC;
        """
        data = frappe.db.sql(query, {"email": email}, as_dict=True)

        return {"registered_sessions": data or []}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching registered sessions")
        return {"error": str(e)}

import frappe
from frappe.utils import nowdate,now
from frappe import _

@frappe.whitelist()
def get_sessions_with_details():
    print("Fetching sessions for ongoing and upcoming conferences.")
    
    # Step 1: Get the relevant conferences based on status and start date
    conferences = frappe.get_all(
        'Conference',
        fields=['name'],
        filters={
            'status': ['in', ['Ongoing', 'Upcoming']],
            'start_date': ['>=', nowdate()]  # Filter conferences starting from today
        }
    )

    # Extract the conference names from the result
    conference_names = [conference['name'] for conference in conferences]
    
    # Step 2: Use the list of conference names to fetch related sessions
    sessions = frappe.get_all(
        'Session',
        fields=['session_name', 'start_time'],
        filters={
            'conference': ['in', conference_names]  # Filter sessions by conference
        }
    )
    
    return sessions


##  fetching Conferences on registration page using custom Script
@frappe.whitelist(allow_guest=True)
def get_recommended_sessions(attendee_email):
    print("shashi what do u do")
    # Get the attendee document by email
    attendee_doc = frappe.get_doc('Attendee', {'email': attendee_email})
    preferences = attendee_doc.preferences

    if preferences:
        # Query sessions based on the sessions listed in the preferences
        recommended_sessions = get_sessions_based_on_preference_ui(preferences)
        return recommended_sessions
    else:
        return []

def get_sessions_based_on_preference_ui(preferences):
    """Fetch sessions based on the session preferences."""
    recommended_sessions = []
    for preference in preferences:
        # Get the session linked to the preference
        session = frappe.get_doc('Session', preference.session)
        recommended_sessions.append({
            'session_name': session.session_name,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'speaker': session.speaker
        })
    return recommended_sessions


## recommendations via scheduler
@frappe.whitelist()
def send_daily_session_recommendations():
    """Send daily session recommendations to attendees based on their preferences."""
    
    # Get all attendees (fetching basic fields like attendee_name and email)
    attendees = frappe.get_all('Attendee', fields=['attendee_name', 'email'])

    for attendee in attendees:
        # Fetch the preferences for the current attendee using the email
        preferences = frappe.get_all('Preference', filters={'parent': attendee['email']}, fields=['session'])
        preferred_sessions = [pref["session"] for pref in preferences]

        registrations = frappe.get_all('Registration', filters={'attendee': attendee['email']}, fields=['session'])
        registered_sessions = [reg["session"] for reg in registrations]

        # Combine all sessions of interest
        preferences = list(set(preferred_sessions + registered_sessions))


        if preferences:
            # Fetch recommended sessions based on the session preferences
            recommended_sessions = get_sessions_based_on_preferences(preferences)

            if recommended_sessions:  # Proceed only if there are recommendations
                # Format the email content with recommended sessions
                email_content = format_email_content(recommended_sessions)

                # Send email with session recommendations
                send_email_to_attendee(attendee['email'], email_content)

def get_sessions_based_on_preferences(preferences):
    """Fetch sessions based on attendee preferences."""
    recommended_sessions = []
    
    for preference in preferences:
        # Get the session linked to the preference using the session ID (which is a Link field in the Preference table)
        session = frappe.get_doc('Session', preference['session'])
        recommended_sessions.append({
            'session_name': session.session_name,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'speaker': session.speaker
        })
    
    return recommended_sessions

def format_email_content(sessions):
    """Format the session list into an HTML email body."""
    content = "<h3>Recommended Sessions for You:</h3><ul>"
    
    for session in sessions:
        content += f"<li><strong>{session['session_name']}</strong><br>" \
                   f"Time: {session['start_time']} - {session['end_time']}<br>" \
                   f"Speaker: {session['speaker']}</li><br>"
    
    content += "</ul>"
    return content

def send_email_to_attendee(email, content):
    """Send the email to the attendee."""
    frappe.sendmail(
        recipients=[email],
        subject="Your Daily Session Recommendations",
        message=content
    )


## updating the mock payment status for apilog and registration page FROM UI
@frappe.whitelist(allow_guest=True)
def update_api_log(conference, session, attendee, registration_date, payment_status):
    request_body = {
        "conference": conference,
        "session": session,
        "attendee": attendee,
        "registration_date": registration_date,
        "payment_status": payment_status
    }
    
    # Define success or failure response based on payment status
    if payment_status.lower() == "paid":
        response_body = {"success": True}
        status_code = 200  # Successful payment
    elif payment_status.lower() == "failed":
        response_body = {"success": False}
        status_code = 500  # Payment failed
    else:  # Pending case
        response_body = {"success": False}
        status_code = 202  # Payment pending

    try:
        api_endpoint = "conference_management.conference_management.api.apis.update_api_log"

        # Create a new API Log document using 'frappe.new_doc'
        api_log = frappe.new_doc("APILog")  
        api_log.api_endpoint = api_endpoint  # Set the api_endpoint field
        api_log.request_body = frappe.as_json(request_body) # Convert request_body to JSON string
        api_log.response_body = frappe.as_json(response_body)  # Convert response_body to JSON string
        api_log.status_code = status_code  # Set the status_code
        api_log.method = "POST"  # Set the HTTP method
        api_log.timestamp = now()
        # Save log
        api_log.insert()
        frappe.db.commit()

        # Update Registration document with payment status
        registration_doc = frappe.get_doc("Registration", {"attendee": attendee, "conference": conference, "session": session})

        if registration_doc:
            registration_doc.payment_status = payment_status
            registration_doc.save()
            frappe.db.commit()

        if response_body["success"]:
            return {"status": "success", "message": "API Log Updated", "data": response_body}
        else:
            return {"status": "failure", "message": "Payment failed. API Log Updated", "data": response_body}

    except Exception as e:
        print(e)
        frappe.log_error(title="API Log Error", message=str(e))  # Log the error
        return {"status": "error", "message": str(e)}

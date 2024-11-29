import json
import frappe
from frappe.utils import nowdate, now
import random
from frappe import _

def mock_payment():
    """
    Simulates a payment process with random outcomes.
    """
    return random.choice(["Paid", "Failed", "Pending"])

@frappe.whitelist(allow_guest=True)
def add_attendee_and_register():
    try:
        # Decode and parse the incoming JSON data
        data = frappe.request.data.decode('utf-8')  # Decode the bytes to string
        data = json.loads(data)  # Parse the JSON string into a dictionary

        # Prepare data for logging
        api_endpoint = "api/method/conference_management/external_apis/addAttendeeAndRegisterApi/add_attendee_and_register"
        method = frappe.local.request.method
        request_body = json.dumps(data)  # Log the incoming request body
        time_stamp = now()  # Current timestamp for the log
        print(time_stamp)

        # Initialize response variables
        response_body = ""
        status_code = 200

        # Now you can work with the data directly
        attendee_data = data.get('attendee', {})
        registration_data = data.get('registration', {})

        # Check if registration data for the conference is provided
        conference_name = registration_data.get('conference')
        session_id = registration_data.get('session')

        if conference_name:
            # Check if the conference exists
            conference = frappe.get_doc('Conference', conference_name)
            if conference:
                try:
                    # checking if the session is already registered in that conference
                    existing_registration = frappe.get_all('Registration', filters={
                        'conference': conference,
                        'session': session_id
                    })

                    if existing_registration:
                        return {
                            "status": "Failure",
                            "message": "Attendee is already registered for this session."
                        }
                    else:
                        # Check if the session belongs to the given conference
                        session_belongs_to_conference = frappe.get_all('Session', filters={
                            'conference': conference_name,
                            'session_name': session_id
                        })

                        if not session_belongs_to_conference:
                            # Session does not belong to this conference
                            return {
                                "status": "Failure",
                                "message": "Session does not belong to this conference. Please use the correct session name."
                            }
                except Exception as e:
                    # Check if the session belongs to the given conference
                    session_belongs_to_conference = frappe.get_all('Session', filters={
                        'conference': conference_name,
                        'session_name': session_id
                    })

                    if not session_belongs_to_conference:
                        # Session does not belong to this conference
                        return {
                            "status": "Failure",
                            "message": "Session does not belong to this conference. Please use the correct session name."
                        }
            
        preferences_data = data.get("preferences", [])

        if not attendee_data or not registration_data:
            frappe.throw("Attendee and Registration details are required.")

        # Check if the attendee exists based on their email
        if frappe.db.exists("Attendee", attendee_data["email"]):
            # If attendee exists, get the document
            attendee_doc = frappe.get_doc("Attendee", attendee_data["email"])
            attendee_doc.update(attendee_data)  # Update with new details
            method = "PUT"  # If updating, change method to PUT
        else:
            # If attendee does not exist, create a new attendee
            attendee_doc = frappe.new_doc("Attendee")
            attendee_doc.email = attendee_data.get("email")
            attendee_doc.attendee_name = attendee_data.get("attendee_name")
            attendee_doc.phone_number = attendee_data.get("phone_number")
            attendee_doc.organization = attendee_data.get("organization")
            attendee_doc.insert(ignore_permissions=True)
            frappe.db.commit()  # Commit changes to ensure they are saved
            method = "POST"  # If creating a new attendee, it's a POST

        # Add preferences if any
        for pref in preferences_data:
            session_name = pref.get("session")  # Get session name from preferences
            if frappe.db.exists("Session", {"session_name": session_name}):
                session_doc_name = frappe.db.get_value("Session", {"session_name": session_name}, "name")
                # Check if this preference already exists for the attendee
                existing_preference = next(
                    (p for p in attendee_doc.preferences if p.session == session_doc_name), None
                )
                if existing_preference:
                    existing_preference.session = session_doc_name
                else:
                    # If preference does not exist, append it
                    attendee_doc.append("preferences", {"session": session_doc_name})
            else:
                frappe.throw(f"Session '{session_name}' does not exist.")

        attendee_doc.save()  # Save preferences to the attendee doc
        frappe.db.commit()  # Commit changes to ensure they are saved

        # Simulate payment
        payment_status = mock_payment()

        # Check if the attendee is already registered for this session
        existing_registration = frappe.db.exists(
            "Registration", {
                "conference": registration_data["conference"],
                "session": registration_data["session"],
                "attendee": attendee_doc.email
            }
        )

        if existing_registration:
            # If already registered, return success message
            response_body = json.dumps({
                "status": "success",
                "message": "Attendee is already registered for this session.",
                "payment_status": payment_status
            })

            try:
                frappe.get_doc({
                    "doctype": "APILog",
                    "api_endpoint": api_endpoint,
                    "method": method,
                    "request_body": request_body,
                    "response_body": response_body,
                    "status_code": status_code,
                    "timestamp": time_stamp,
                }).insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as log_exception:
                frappe.log_error(frappe.get_traceback(), "API Log Error")

            return {
                "status": "success",
                "message": "Attendee is already registered for this session.",
                "payment_status": payment_status
            }
        else:
            method = "GET"
            registration_doc = frappe.get_doc({
                "doctype": "Registration",
                "conference": registration_data["conference"],
                "session": registration_data["session"],
                "attendee": attendee_doc.email,
                "registration_date": nowdate(),
                "payment_status": payment_status
            })
            registration_doc.insert(ignore_permissions=True)
            frappe.db.commit()  # Commit changes to ensure they are saved
            response_body = json.dumps({
                "status": "success",
                "message": "Registration completed successfully.",
                "payment_status": payment_status
            })

            # Log the successful API interaction (POST/PUT)
            try:
                frappe.get_doc({
                    "doctype": "APILog",
                    "api_endpoint": api_endpoint,
                    "method": method,
                    "request_body": request_body,
                    "response_body": response_body,
                    "status_code": status_code,
                    "timestamp": time_stamp,
                }).insert(ignore_permissions=True)
                frappe.db.commit()

            except Exception as log_exception:
                # If logging fails, still continue with the core functionality
                frappe.log_error(frappe.get_traceback(), "API Log Error")

        # Return success response
        return {
            "status": "success",
            "message": "Attendee added and registration completed successfully.",
            "payment_status": payment_status
        }

    except Exception as e:
        # If an error occurs, log the exception and return error response
        status_code = 500
        response_body = json.dumps({
            "status": "error",
            "message": str(e)
        })

        # Log the failed API interaction (error scenario)
        try:
            frappe.get_doc({
                "doctype": "APILog",
                "api_endpoint": api_endpoint,
                "method": method,
                "request_body": request_body,
                "response_body": response_body,
                "status_code": status_code,
                "timestamp": time_stamp,
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as log_exception:
            # If logging fails, still continue with the core functionality
            frappe.log_error(frappe.get_traceback(), "API Log Error")

        return {
            "status": "error",
            "message": str(e)
        }

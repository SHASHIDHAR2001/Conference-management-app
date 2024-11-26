import frappe,json
from frappe.utils import nowdate,now
import random

def mock_payment():
    """ Simulates a payment process with a 70% chance for 'Paid' and 30% for 'Pending' or 'Failed' """
    payment_outcome = random.choices(
        ["Paid", "Pending", "Failed"], 
        weights=[0.7, 0.15, 0.15], 
        k=1
    )[0]
    return payment_outcome

@frappe.whitelist(allow_guest=True)
def process_mock_payment():
    try:
        # Get attendee email and session name from the request body
        attendee_email = frappe.local.form_dict.get('attendee_email')
        session_name = frappe.local.form_dict.get('session_name')
        payment_status_request = frappe.local.form_dict.get('payment_status',None)
        api_endpoint = "/api/method/conference_management.external_apis.paymentSimulationApi.process_mock_payment"

        # Request body to log
        request_body = {
            "attendee_email": attendee_email,
            "session_name": session_name,
            "payment_status": payment_status_request
        }

        # Check if both parameters are provided
        if not attendee_email or not session_name:
            response = {
                "status": "error",
                "message": "Both attendee_email and session_name are required."
            }
            log_api_request(api_endpoint, request_body, response)

            return {
                "status": "error",
                "message": "Both attendee_email and session_name are required."
            }
        
        # Validate the payment_status_request
        valid_statuses = ["Paid", "Pending", "Failed"]
        if payment_status_request and payment_status_request not in valid_statuses:
            response = {
                "status": "error",
                "message": f"Invalid payment_status value. Accepted values are: {', '.join(valid_statuses)}."
            }
            log_api_request(api_endpoint, request_body, response)
            return response

        # Fetch the Registration record based on attendee email and session name
        registration = frappe.db.get_value(
            "Registration", 
            {
                "attendee": attendee_email,
                "session": session_name
            },
            "name"  # This will return the 'name' field (which is the registration ID)
        )

        if not registration:
            response = {
                "status": "error",
                "message": "Registration not found for the given attendee and session."
            }
            log_api_request(api_endpoint, request_body, response)
            return response

       # Use the provided payment_status if available; otherwise, simulate payment
        if payment_status_request:
            payment_status = payment_status_request
        else:
            payment_status = mock_payment()

        # Update the Registration record with the new payment status
        registration_doc = frappe.get_doc("Registration", registration)
        registration_doc.payment_status = payment_status
        registration_doc.payment_date = nowdate()  # Add payment date
        registration_doc.save(ignore_permissions=True)
        frappe.db.commit()  # Ensure changes are committed to the database

        # Return the result with a customized message
        if payment_status == "Paid":
            response = {
                "status": "success",
                "message": f"Payment successfully processed for Session: {session_name} (Registration ID: {registration})",
                "payment_status": "Paid"
            }
        elif payment_status == "Pending":
            response = {
                "status": "success",
                "message": f"Payment is pending. If amount is deducted, we will update the status. Otherwise, you will receive a refund.",
                "payment_status": "Pending"
            }
        else:  # Failed
            response = {
                "status": "success",
                "message": f"Payment failed for Session: {session_name} (Registration ID: {registration}). Please try again.",
                "payment_status": "Failed"
            }
        log_api_request(api_endpoint, request_body, response)
        return response

    except Exception as e:
        response = {
            "status": "error",
            "message": str(e)
            }
        log_api_request(api_endpoint,
            {"attendee_email": frappe.local.form_dict.get('attendee_email'),
             "session_name": frappe.local.form_dict.get('session_name')},
            response
        )
        frappe.log_error(frappe.get_traceback(), "Payment Simulation API Error")
        return response


def log_api_request(api_endpoint, request_body, response_body):
    """
    Log API request and response to the APILog doctype.

    Args:
        api_endpoint (str): The API endpoint being accessed.
        request_body (dict): The request payload.
        response_body (dict): The response returned by the API.
    """
    try:
        frappe.get_doc({
            "doctype": "APILog",
            "api_endpoint": api_endpoint,
            "method": "POST",  # Method is POST for this API
            "request_body": json.dumps(request_body),  # Serialize request body
            "response_body": json.dumps(response_body),  # Serialize response body
            "timestamp": now(),
            "status_code": 500 if response_body.get("status") == "error" else 200, 
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        # Log the exception in case logging itself fails
        frappe.log_error(f"Failed to log API request: {str(e)}", "API Log Failure")

import frappe
def get_context(context):
    # Pass CSRF token explicitly to the template
    context.csrf_token = frappe.sessions.get_csrf_token()

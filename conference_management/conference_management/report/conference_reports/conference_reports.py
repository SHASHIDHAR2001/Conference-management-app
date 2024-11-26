# # Copyright (c) 2024, shashi and contributors
# # For license information, please see license.txt
from frappe import _
import frappe

def execute(filters=None):
    """Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
    columns = get_columns()
    data = get_data()
    chart = get_chart_data(data)

    return columns, data, None, chart


def get_chart_data(data):
    """Prepare chart data."""
    labels = [row["conference_name"] for row in data]
    registered_attendees = [row["registered_attendees"] for row in data]
    sessions = [row["num_sessions"] for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Registered Attendees", "values": registered_attendees},
                {"name": "Number of Sessions", "values": sessions}
            ]
        },
        "type": "bar",
        "height": 300
    }

def get_columns():
    """Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
    return [
        {"label": "Conference Name", "fieldname": "conference_name", "fieldtype": "Data", "width": 200},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 120},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 120},
        {"label": "Total Attendees in System", "fieldname": "total_attendees", "fieldtype": "Int", "width": 150},
        {"label": "Registered Attendees", "fieldname": "registered_attendees", "fieldtype": "Int", "width": 150},
        {"label": "Number of Sessions", "fieldname": "num_sessions", "fieldtype": "Int", "width": 150},
    ]


def get_data():
    """Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
    # Fetch all conferences with start_date and end_date
    conferences = frappe.get_all(
        "Conference",
        fields=["name", "start_date", "end_date"]
    )

    data = []
    for conference in conferences:
        conference_name = conference.name
        conference_start_date = conference.start_date
        conference_end_date = conference.end_date

        # Total attendees in the system
        total_attendees = frappe.db.count("Attendee")

        # Registered attendees for this conference
        registered_attendees = frappe.db.count("Registration", filters={"conference": conference_name})

        # Number of sessions in this conference
        num_sessions = frappe.db.count("Session", filters={"conference": conference_name})

        data.append({
            "conference_name": conference_name,
            "total_attendees": total_attendees,
            "registered_attendees": registered_attendees,
            "num_sessions": num_sessions,
            "start_date": conference_start_date,
            "end_date": conference_end_date
        })

    return data

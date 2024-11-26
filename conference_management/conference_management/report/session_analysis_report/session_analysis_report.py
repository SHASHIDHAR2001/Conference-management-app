# Copyright (c) 2024, shashi and contributors
# For license information, please see license.txt

# import frappe
from frappe import _
import frappe

def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()
	chart_data = get_chart_data(data)

	return columns, data, None, chart_data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{"label": "Session Name", "fieldname": "session_name", "fieldtype": "Data", "width": 200},
		{"label": "Conference Name", "fieldname": "conference_name", "fieldtype": "Data", "width": 200},
		{"label": "Total Registrations", "fieldname": "total_registrations", "fieldtype": "Int", "width": 150},
		{"label": "Remaining Capacity", "fieldname": "remaining_capacity", "fieldtype": "Int", "width": 150},
		{"label": "Revenue Generated", "fieldname": "revenue_generated", "fieldtype": "Currency", "width": 150},
	]


def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
  	# Fetch all sessions
	sessions = frappe.get_all(
		"Session",
		fields=["name", "conference", "max_attendees", "session_fee"]
	)

	data = []
	for session in sessions:
		session_name = session["name"]
		conference_name = frappe.db.get_value("Conference", session["conference"], "conference_name")
		max_attendees = session["max_attendees"]
		session_fee = session["session_fee"]

		# Total registrations for the session
		total_registrations = frappe.db.count("Registration", filters={"session": session_name})

		# Remaining capacity
		remaining_capacity = max(0, max_attendees - total_registrations)

		# Revenue generated from paid registrations
		paid_registrations = frappe.get_all(
			"Registration",
			filters={"session": session_name, "payment_status": "Paid"},
			fields=["name"]
		)
		revenue_generated = len(paid_registrations) * session_fee

		data.append({
			"session_name": session_name,
			"conference_name": conference_name,
			"total_registrations": total_registrations,
			"remaining_capacity": remaining_capacity,
			"revenue_generated": revenue_generated,
		})

	return data

def get_chart_data(data):
    """Prepare data for the chart."""
    labels = [d["session_name"] for d in data]
    total_registrations = [d["total_registrations"] for d in data]
    remaining_capacity = [d["remaining_capacity"] for d in data]
    revenue_generated = [d["revenue_generated"] for d in data]

    # Adjust space between bars for better clarity
    space_between_bars = 0.2

    return {
        "data": {
            "labels": labels,  # Session Names as X-axis labels
            "datasets": [
                {
                    "name": "Total Registrations", 
                    "values": total_registrations, 
                    "chartType": "bar",  # Bar chart for this dataset
                    "barOptions": {
                        "spaceRatio": space_between_bars 
                    }
                },
                {
                    "name": "Remaining Capacity", 
                    "values": remaining_capacity,  # Data for Remaining Capacity
                    "chartType": "bar",  
                    "barOptions": {
                        "spaceRatio": space_between_bars
                    }
                },
                {
                    "name": "Revenue Generated", 
                    "values": revenue_generated,  # Data for Revenue Generated
                    "chartType": "bar",  
                    "barOptions": {
                        "spaceRatio": space_between_bars 
                    }
                }
            ],
        },
        "type": "bar",  
        "barOptions": {
            "stacked": False,  
            "spaceRatio": 0.3,  
        },
    }



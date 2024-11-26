# Copyright (c) 2024, shashi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

class Session(Document):
    def before_insert(self):
        # Ensure session time falls within the conference's start and end time
        self.validate_session_time()

    def validate_session_time(self):
        # Get the conference details to validate against
        conference = frappe.get_doc("Conference", self.conference)

        # Convert the session's start and end time to datetime objects
        session_start = get_datetime(self.start_time)
        session_end = get_datetime(self.end_time)

        # Check if session time falls within the conference time
        if session_start < get_datetime(conference.start_date) or session_end > get_datetime(conference.end_date):
            frappe.throw("Session time must be within the conference start and end time.")

        # Check if any other session overlaps with the current session time in the same conference
        overlapping_sessions = frappe.db.sql("""
            SELECT name, start_time, end_time
            FROM `tabSession`
            WHERE conference = %s AND name != %s
            AND ((%s BETWEEN start_time AND end_time) OR (%s BETWEEN start_time AND end_time) OR 
                 (start_time BETWEEN %s AND %s) OR (end_time BETWEEN %s AND %s))
        """, (self.conference, self.name, session_start, session_end, session_start, session_end, session_start, session_end), as_dict=True)
        # If there are overlapping sessions, throw an error
        print(overlapping_sessions)

        if overlapping_sessions:
            overlap_details = "\n".join([f"Session {s['name']} from {s['start_time']} to {s['end_time']}" for s in overlapping_sessions])
            frappe.throw(f"Session time overlaps with the following existing sessions in the same conference:\n{overlap_details}")

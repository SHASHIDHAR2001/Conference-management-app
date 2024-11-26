# Copyright (c) 2024, shashi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

class Conference(Document):
    def before_insert(self):
        # Automatically set the status of the conference based on current date
        if not self.status:
            if get_datetime(self.start_date) > get_datetime():
                self.status = "Upcoming"
            elif get_datetime(self.end_date) < get_datetime():
                self.status = "Completed"
            else:
                self.status = "Ongoing"
        
    def validate(self):
        # Ensure that the end date is after the start date
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                frappe.throw("End date cannot be before the start date of the conference.")
        
        is_existing_conference = frappe.db.exists("Conference", self.name)

        if is_existing_conference:
            # Validate sessions within the conference only if the conference is already saved
            for session in self.sessions:
                self.validate_session_time(session)

    def validate_session_time(self, session):
        # Get the conference details to validate against
        conference_start = get_datetime(self.start_date)
        conference_end = get_datetime(self.end_date)

        # Convert the session's start and end time to datetime objects
        session_start = get_datetime(session.start_time)
        session_end = get_datetime(session.end_time)

        # Check if session time falls within the conference time
        if session_start < conference_start or session_end > conference_end:
            frappe.throw(f"Session '{session.session_name}' time must be within the conference start and end time.")

        # Check if any other session overlaps with the current session time in the same conference
        overlapping_sessions = frappe.db.sql("""
            SELECT name, start_time, end_time
            FROM `tabSession`
            WHERE conference = %s AND name != %s
            AND ((%s BETWEEN start_time AND end_time) OR (%s BETWEEN start_time AND end_time) OR 
                 (start_time BETWEEN %s AND %s) OR (end_time BETWEEN %s AND %s))
        """, (self.name, session.name, session_start, session_end, session_start, session_end, session_start, session_end), as_dict=True)

        if overlapping_sessions:
            overlap_details = "\n".join([f"Session {s['name']} from {s['start_time']} to {s['end_time']}" for s in overlapping_sessions])
            frappe.throw(f"Session time overlaps with the following existing sessions in the same conference:\n{overlap_details}")

                
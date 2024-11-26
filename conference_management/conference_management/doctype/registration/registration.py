# Copyright (c) 2024, shashi and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from datetime import date

# class Registration(Document):
# 	def before_insert(self):
# 		# Combine conference, session, and attendee to create a unique name
# 		self.name = f"{self.conference}-{self.session}-{self.attendee}"

# 		if not self.registration_date:
# 			self.registration_date = date.today()

##NEW NEW
import frappe
from frappe.model.document import Document
from datetime import date
from frappe.utils import get_datetime

class Registration(Document):
    def before_insert(self):
        # Combine conference, session, and attendee to create a unique name
        self.name = f"{self.conference}-{self.session}-{self.attendee}"

        # Set registration date to today's date if not provided
        if not self.registration_date:
            self.registration_date = date.today()

        # Validate capacity
        self.validate_capacity()

        # Prevent overlap registration
        self.prevent_overlap_registration()

    def validate_capacity(self):
        # Check if session capacity has been reached
        session = frappe.get_doc("Session", self.session)
        current_registrations = frappe.db.count("Registration", {"session": self.session})

        if current_registrations >= session.max_attendees:
            frappe.throw(f"Cannot register. Maximum capacity of {session.max_attendees} attendees reached for this session.")

        
    def prevent_overlap_registration(self):
        # Ensure the attendee is not registered for overlapping sessions
        current_session = frappe.get_doc("Session", self.session)
        new_start = get_datetime(current_session.start_time)
        new_end = get_datetime(current_session.end_time)

        # Get all other registrations for the same attendee
        overlapping_sessions = frappe.db.sql("""
            SELECT s.name, s.start_time, s.end_time
            FROM `tabRegistration` r
            JOIN `tabSession` s ON r.session = s.name
            WHERE r.attendee = %s AND r.session != %s
        """, (self.attendee, self.session), as_dict=True)

        for session in overlapping_sessions:
            existing_start = get_datetime(session['start_time'])
            existing_end = get_datetime(session['end_time'])

            # Check for time overlap: If the new session overlaps with an existing one
            if (new_start < existing_end and new_end > existing_start):
                frappe.throw(f"Attendee is already registered for a session that overlaps with session {current_session.name} (from {current_session.start_time} to {current_session.end_time}).")


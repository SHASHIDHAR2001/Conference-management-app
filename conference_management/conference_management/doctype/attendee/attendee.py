# # Copyright (c) 2024, shashi and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe.utils import get_url, nowdate, getdate

# class Attendee(Document):
    
# 	def before_insert(self):
# 		# Ensure attendee email is unique
# 		self.validate_unique_email()

# 	def validate_unique_email(self):
# 		# Check if attendee email already exists
# 		if frappe.db.exists("Attendee", {"email": self.email}):
# 			frappe.throw(f"Attendee with email {self.email} already exists.")
            
# 	def after_insert(self):
# 		self.send_dynamic_recommendations()

# 	def send_dynamic_recommendations(self):
# 		preferences = frappe.get_all(
# 			"Preference",
# 			filters={"parent": self.name},
# 			fields=["session"]
# 		)

# 		if not preferences:
# 			return  # No preferences selected, skip recommendations

# 		preference_sessions = [pref["session"] for pref in preferences]
# 		similar_sessions = self.get_similar_sessions(preference_sessions)

# 		if not similar_sessions:
# 			return  # No similar sessions found, no email to send

# 		session_links = []
# 		for session in similar_sessions:
# 			speaker = session.get("speaker", "No speaker assigned")
# 			link = get_url(f"/app/registration/new-registration?session={session['session_name']}&attendee={self.name}")
# 			session_links.append(f"""
# 				<p>
# 					<b>Session:</b> {session['session_name']}<br>
# 					<b>Speaker:</b> {speaker}<br>
# 					<b>Time:</b> {session['start_time']} to {session['end_time']}<br>
# 					<a href="{link}">Register for this session</a>
# 				</p>
# 			""")

# 		email_content = f"""
# 			<p>Dear {self.attendee_name},</p>
# 			<p>Based on your preferences, we recommend the following active sessions for you:</p>
# 			{''.join(session_links)}
# 			<p>We hope you find these sessions valuable!</p>
# 		"""

# 		try:
# 			frappe.sendmail(
# 				recipients=[self.email],
# 				subject="Recommended Sessions for Registration",
# 				message=email_content
# 			)
# 		except Exception as e:
# 			print(f"Error sending email: {str(e)}", "Attendee Email Notification")


# 	def get_similar_sessions(self, preference_sessions):
# 		try:
# 			# Get the current date
# 			current_date = getdate(nowdate())
# 			print(preference_sessions)

# 			# Fetch conferences and speakers for the preference sessions
# 			preference_conferences = frappe.get_all(
# 				"Session",
# 				filters={"session_name": ["in", preference_sessions]},  # Updated filter field
# 				fields=["conference", "speaker"]
# 			)
# 			print(preference_conferences)

# 			if not preference_conferences:
# 				return []  # No matching conferences found

# 			# Extract unique conference and speaker data
# 			conferences = list({item["conference"] for item in preference_conferences if item.get("conference")})
# 			speakers = list({item["speaker"] for item in preference_conferences if item.get("speaker")})
# 			print(conferences)
# 			print(speakers)

# 			# Fetch similar sessions
# 			similar_sessions = frappe.get_all(
# 				"Session",
# 				filters={
# 					"conference": ["in", conferences],
# 					"speaker": ["in", speakers]
# 				},
# 				fields=["session_name", "speaker", "start_time", "end_time"]  # Updated field list
# 			)
# 			print(similar_sessions, "yep got it")

# 			return similar_sessions
# 		except Exception as e:
# 			print(f"Error fetching similar sessions: {str(e)}", "Attendee Registration")
# 			return []


import frappe
from frappe.model.document import Document
from frappe.utils import get_url, nowdate, getdate

class Attendee(Document):

    def before_insert(self):
        # Ensure attendee email is unique
        self.validate_unique_email()

    def validate_unique_email(self):
        # Check if attendee email already exists
        if frappe.db.exists("Attendee", {"email": self.email}):
            frappe.throw(f"Attendee with email {self.email} already exists.")

    def after_insert(self):
        # Send dynamic recommendations asynchronously
        frappe.enqueue(self.send_dynamic_recommendations)

    def send_dynamic_recommendations(self):
        preferences = frappe.get_all(
            "Preference",
            filters={"parent": self.name},
            fields=["session"]
        )

        if not preferences:
            return  # No preferences selected, skip recommendations

        preference_sessions = [pref["session"] for pref in preferences]
        similar_sessions = self.get_similar_sessions(preference_sessions)

        if not similar_sessions:
            return  # No similar sessions found, no email to send

        session_links = []
        for session in similar_sessions:
            speaker = session.get("speaker", "No speaker assigned")
            link = get_url(f"/app/registration/new-registration?session={session['session_name']}&attendee={self.name}")
            session_links.append(f"""
                <p>
                    <b>Session:</b> {session['session_name']}<br>
                    <b>Speaker:</b> {speaker}<br>
                    <b>Time:</b> {session['start_time']} to {session['end_time']}<br>
                    <a href="{link}">Register for this session</a>
                </p>
            """)

        email_content = f"""
            <p>Dear {self.attendee_name},</p>
            <p>Based on your preferences, we recommend the following active sessions for you:</p>
            {''.join(session_links)}
            <p>We hope you find these sessions valuable!</p>
        """

        try:
            frappe.sendmail(
                recipients=[self.email],
                subject="Recommended Sessions for Registration",
                message=email_content
            )
        except Exception as e:
            frappe.log_error(f"Error sending email: {str(e)}", "Attendee Email Notification")

    def get_similar_sessions(self, preference_sessions):
        try:
            # Get the current date
            current_date = getdate(nowdate())
            print(preference_sessions)

            # Fetch conferences and speakers for the preference sessions
            preference_conferences = frappe.get_all(
                "Session",
                filters={"session_name": ["in", preference_sessions]},  # Updated filter field
                fields=["conference", "speaker"]
            )
            print(preference_conferences)

            if not preference_conferences:
                return []  # No matching conferences found

            # Extract unique conference and speaker data
            conferences = list({item["conference"] for item in preference_conferences if item.get("conference")})
            speakers = list({item["speaker"] for item in preference_conferences if item.get("speaker")})
            print(conferences)
            print(speakers)

            # Fetch similar sessions
            similar_sessions = frappe.get_all(
                "Session",
                filters={
                    "conference": ["in", conferences],
                    "speaker": ["in", speakers]
                },
                fields=["session_name", "speaker", "start_time", "end_time"]  # Updated field list
            )
            print(similar_sessions, "yep got it")

            return similar_sessions
        except Exception as e:
            frappe.log_error(f"Error fetching similar sessions: {str(e)}", "Attendee Registration")
            return []

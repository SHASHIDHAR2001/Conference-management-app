# Copyright (c) 2024, shashi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class APILog(Document):
	def before_insert(self):
		# Combine api_endpoint, method to create a unique name
		self.name = f"{self.api_endpoint}-{self.method}"
		
	def validate(self):
		# Ensure method is valid (GET, POST, PUT, DELETE)
		if self.method not in ["GET", "POST", "PUT", "DELETE"]:
			frappe.throw(f"Invalid method: {self.method}. Allowed methods are GET, POST, PUT, DELETE.")

		# Ensure status code is valid (in the range of 100 to 599)
		if not (100 <= self.status_code <= 599):
			frappe.throw(f"Invalid status code: {self.status_code}. Status code should be between 100 and 599.")
# Copyright (c) 2022, korecent solutions pvt. ltd and contributors
# For license information, please see license.txt

from trello.api import trello_settings
from frappe.model.document import Document
import requests
import frappe
import json 

board_base_url = "https://api.trello.com/1/members/"
class TrelloMembers(Document):
	def after_insert(self):
		update_email(doc=self)

@frappe.whitelist()
def update_email(doc):
    url = "https://api.trello.com/1/members/"+doc.member_id

    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': trello_settings().get('key'),
		'token': trello_settings().get('token'),
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )
    response = json.loads(response.text)
    email = response.get('email')
    frappe.db.set_value(doc.doctype, doc.name, 'user', email)
    frappe.db.commit()
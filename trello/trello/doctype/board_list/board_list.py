# Copyright (c) 2022, korecent solutions pvt. ltd and contributors
# For license information, please see license.txt

from trello.api import trello_settings
from frappe.model.document import Document
import requests
import frappe
import json 


url = "https://api.trello.com/1/lists"
class BoardList(Document):
	def after_insert(self):
		create_board_list(doc=self)

	def after_delete(self):
		archive_list(doc=self)


@frappe.whitelist()
def create_board_list(doc):
    query = {
		'name': doc.name,
		'idBoard': doc.board_id,
		'key': trello_settings().get('key'),
		'token': trello_settings().get('token'),
    }

    response = requests.request(
        "POST",
        url,
        params=query
    )
    response = json.loads(response.text)
    frappe.db.set_value(doc.doctype, doc.name, 'id', response.get('id'))
    frappe.db.commit()

@frappe.whitelist()
def archive_list(doc):
	path = url+"/"+doc.id+"/closed"
	frappe.log_error(path, "url")
	query = {
		'key': trello_settings().get('key'),
		'token': trello_settings().get('token'),
	}

	requests.request(
		"PUT",
		url=path,
		params=query
	)
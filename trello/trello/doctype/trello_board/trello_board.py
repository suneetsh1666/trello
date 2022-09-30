# Copyright (c) 2022, korecent solutions pvt. ltd and contributors
# For license information, please see license.txt

from trello.api import trello_settings
from frappe.model.document import Document
import requests
import frappe
import json 


board_base_url = "https://api.trello.com/1/boards/"
class TrelloBoard(Document):
	def after_insert(self):
		create_board(board_name=self.name)

	def on_update(self):
		assign_members(board_name=self.name)
		frappe.db.commit()
		self.reload()
		trello_members = frappe.db.sql(""" select name, board_id, member_id from `tabTrello Members` where board_id = "{}" """.format(self.board_id), as_dict=1)
		board_id=self.board_id
		members = [i.member_id for i in self.trello_board_members]
		for val in trello_members:
			if board_id == val.board_id and val.member_id not in members:
				remove_members(board_id=self.board_id, member_id=val.member_id)
				frappe.delete_doc('Trello Members', val.name)
				frappe.db.commit()

	def after_delete(self):
		delete_board(board_id=self.board_id)

@frappe.whitelist()
def create_board(board_name=None):
	try:
		url = board_base_url
		query = {
			'name': board_name,
			'key': trello_settings().get('key'),
			'token': trello_settings().get('token'),
		}
		response = requests.request(
			"POST",
			url,
			params=query
		)
		response = json.loads(response.text)
		frappe.db.set_value('Trello Board', board_name, 'b_name', response.get('name'))
		frappe.db.set_value('Trello Board', board_name, 'board_id', response.get('id'))
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(e, "after_insert")
		frappe.throw(
			title='Error',
			msg=e,
			exc=IOError
		)


@frappe.whitelist()
def update_board(board_name=None):
	pass

@frappe.whitelist()
def delete_board(board_id):
	url = board_base_url+board_id
	query = {
		'key': trello_settings().get('key'),
		'token': trello_settings().get('token'),
	}
	requests.request(
		"DELETE",
		url,
		params=query
	)
	frappe.db.sql("""delete FROM `tabTrello Members` WHERE board_id="{}" """.format(board_id))

@frappe.whitelist()
def assign_members(board_name=None):
	doc = frappe.get_doc("Trello Board", board_name)
	url = board_base_url+doc.board_id+"/members"
	headers = {
		"Content-Type": "application/json"
	}
	payload = json.dumps( {
		"fullName": "<string>"
	} )

	# board_id = None
	response = {}
	if doc.trello_board_members:
		username_list = []
		board_list = []
		for bm in doc.trello_board_members:
			if not bm.is_member:
				username_list.append(bm.username)
				board_list.append(doc.board_id)
				query = {
					'email': bm.member,
					'key': trello_settings().get('key'),
					'token': trello_settings().get('token'),
					'type': bm.type
				}
				response = requests.request(
					"PUT",
					url,
					data=payload,
					headers=headers,
					params=query
				)
				response = json.loads(response.text)
				board_id = response.get('id')
				if board_id:
					frappe.db.set_value(bm.doctype, bm.name, 'is_member', 1)
					for resp in response.get('members'):
						if resp.get('username') == bm.username:
							frappe.db.set_value(bm.doctype, bm.name, 'member_id', resp.get('id'))
						for mb_resp in response.get('memberships'):
							tm_id = resp.get('username')+"-"+response.get('id')
							if mb_resp.get('memberType') != "admin" and resp.get('id') == mb_resp.get('idMember'):
								if not frappe.db.exists("Trello Members", tm_id):
									tm_doc = frappe.get_doc({
										'doctype': 'Trello Members',
										'member_id': resp.get('id'),
										'full_name':resp.get('fullName'),
										'abr':resp.get('initials'),
										'user_name':resp.get('username'),
										'member__type':resp.get('memberType'),
										'board_id': board_id
									})
									tm_doc.insert()
			
@frappe.whitelist()
def remove_members(board_id, member_id):
	url = board_base_url+board_id+"/members/"+member_id
	query = {
		'key': trello_settings().get('key'),
		'token': trello_settings().get('token'),
	}

	requests.request(
		"DELETE",
		url,
		params=query
	)

@frappe.whitelist()
def get_board_members(board_id):
	url = board_base_url+board_id+"/members"
	query = {
		'key': trello_settings().get('key'),
		'token': trello_settings().get('token'),
	}
	response = requests.request(
		"GET",
		url,
		params=query
	)
	response = json.loads(response.text)
	return response
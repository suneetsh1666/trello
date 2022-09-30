import frappe
import requests
import json
import re


def update_user(doc, method):
    frappe.db.set_value(doc.doctype, doc.name, 'username', None)
    frappe.db.commit()

@frappe.whitelist()
def get_board_list(board_id):
    url = "https://api.trello.com/1/boards/"+board_id+"/lists"
    query = {
        'key': trello_settings().get('key'),
        'token': trello_settings().get('token')
    }
    response = requests.request(
        "GET",
		url,
		params=query
	)
    response = json.loads(response.text)
    return response

@frappe.whitelist()
def create_card(doc, method):
    url = "https://api.trello.com/1/cards"

    headers = {
        "Accept": "application/json"
    }

    members_id = []
    for members in doc.trello_id_members:
        members_id.append(members.member_id)
    members_id = ",".join(members_id)
    
    query = {
        'idList': doc.list_id,
        'key': trello_settings().get('key'),
        'token': trello_settings().get('token'),
        'name': doc.subject,
        'start': doc.start_date,
        'due': doc.end_date,
        'desc': re.sub('<[^<]+?>', '', doc.description),
        'idMembers': members_id
    }
    response = requests.request(
        "POST",
        url,
        headers=headers,
        params=query
    )
    response = json.loads(response.text)
    frappe.db.set_value(doc.doctype, doc.name, 'card_id', response.get('id'))
    frappe.db.commit()
    if response.get('id') and doc.card_label:
        update_label(card_id=response.get('id'), card_label=doc.card_label)
        update_card(doc, method)


@frappe.whitelist()
def update_label(card_id=None, card_label=None):
    url = "https://api.trello.com/1/cards/"+card_id+"/labels"

    query = {
        'color': card_label,
        'key': trello_settings().get('key'),
        'token': trello_settings().get('token')
    }

    requests.request(
        "POST",
        url,
        params=query
    )


@frappe.whitelist()
def update_card(doc, method):
    if doc.card_id:
        url = "https://api.trello.com/1/cards/"+doc.card_id

        headers = {
            "Accept": "application/json"
        }

        members_id = []
        for members in doc.trello_id_members:
            members_id.append(members.member_id)
        members_id = ",".join(members_id)

        query = {
            'key': trello_settings().get('key'),
            'token': trello_settings().get('token'),
            'name': doc.subject,
            'start': doc.start_date,
            'due': doc.end_date,
            'desc': re.sub('<[^<]+?>', '', doc.description),
            'idMembers': members_id
        }
        requests.request(
            "PUT",
            url,
            headers=headers,
            params=query
        )

        if doc.card_label:
            update_label(card_id=doc.card_id, card_label=doc.card_label)


def remove_card(doc, method):
    if doc.card_id:
        url = "https://api.trello.com/1/cards/"+doc.card_id

        query = {
            'key': trello_settings().get('key'),
            'token': trello_settings().get('token')
        }

        requests.request(
            "DELETE",
            url,
            params=query
        )
# @frappe.whitelist()
# def assign_card(doc, method):
#     if doc.reference_type == "Issue":
#         issue_doc = frappe.get_doc(doc.reference_type, doc.reference_name)
#         update_card(doc=issue_doc, method=None, members=[issue_doc.owner])


def update_image(doc, method):
    if doc.attached_to_doctype == "Issue":
        card_id = frappe.db.get_value('Issue', doc.attached_to_name, 'card_id')
        url = "https://api.trello.com/1/cards/"+card_id+"/attachments"
        path = frappe.utils.get_url() + doc.file_url
        headers = {
            "Accept": "application/json"
        }

        query = {
            'key': trello_settings().get('key'),
            'token': trello_settings().get('token'),
            'url': path
        }

        requests.request(
            "POST",
            url,
            headers=headers,
            params=query
        )

def trello_settings():
    try:
        trello_doc = frappe.get_doc('Trello Settings')
        return {
            'key': trello_doc.key,
            'token': trello_doc.get_password(fieldname="token", raise_exception=False)
        }
    except Exception as e:
        return {
            'key': "",
            'token': ""
        }

def update_comment(doc, method):
    if doc.reference_doctype == "Issue":
        card_id = frappe.db.get_value('Issue', doc.reference_name, 'card_id')
        url = "https://api.trello.com/1/cards/"+card_id+"/actions/comments"
        headers = {
            "Accept": "application/json"
        }

        query = {
            'text': re.sub('<[^<]+?>', '', doc.content),
            'key': trello_settings().get('key'),
            'token': trello_settings().get('token')
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            params=query
        )
        response = json.loads(response.text)
        frappe.db.set_value(doc.doctype, doc.name, 'trello_comment_id', response.get('id'))
        frappe.db.commit()

def delete_comment(doc, method):
    if doc.reference_doctype == "Issue":
        card_id = frappe.db.get_value('Issue', doc.reference_name, 'card_id')
        if doc.trello_comment_id:
            url = "https://api.trello.com/1/cards/"+card_id+"/actions/"+doc.trello_comment_id+"/comments"
            query = {
                'key': trello_settings().get('key'),
                'token': trello_settings().get('token')
            }
            requests.request(
                "DELETE",
                url,
                params=query
            )
        
@frappe.whitelist()
def test_webhooks(response=None):
    frappe.log_error(response, "response")
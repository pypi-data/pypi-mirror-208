# An Exchange convenience wrapper around python-o365 library - https://github.com/O365/python-o365
# Source reference
# - https://github.com/O365/python-o365/blob/master/O365/mailbox.py
# - https://github.com/O365/python-o365/blob/master/O365/message.py
# Message properties
# - https://learn.microsoft.com/en-us/graph/api/resources/message?view=graph-rest-1.0
# - https://learn.microsoft.com/en-us/graph/filter-query-parameter?tabs=http
# Common Message Properties
# - Message body -> body/content
# - From address -> from/emailAddress/address
# - Message subject -> subject
# - Message received Datetime -> receivedDatetime
# - Message send Datetime -> sendDatetime
# - Is read flag -> isRead
# See examples/exchange folder for usage scenarios

import re
import time

from O365 import Account
from O365.mailbox import MailBox, Folder, Message


def delete_message(message: Message):
    message.delete()


def get_mailbox(client_id: str, client_secret: str, tenant_id: str, mailbox_address: str) -> MailBox:
    credentials = (client_id, client_secret)

    account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
    account.authenticate()

    return account.mailbox(mailbox_address)


def get_inbox(mailbox: MailBox) -> Folder:
    return mailbox.inbox_folder()


def get_folder(mailbox: MailBox, folder_name: str) -> Folder:
    return mailbox.get_folder(folder_name=folder_name)


def get_message_in_folder(folder: Folder, query_filter: str, order_by: str = None, timeout: int = 30) -> Message:
    end_time = time.time() + float(timeout)
    interval = 1

    # Given the wait interval specified, get a single message meeting the query/order_by criteria
    while time.time() < end_time:
        try:
            messages = get_messages_in_folder(folder, query_filter, order_by, 1)
            message = next(messages)
            return message
        except StopIteration:
            # No messages meet the filter at this time
            time.sleep(interval)


def get_messages_in_folder(folder: Folder, query_filter: str, order_by: str = None, limit: int = 30) -> list:
    # See the following for guidance construction of order-by clauses
    # https://learn.microsoft.com/en-us/graph/api/user-list-messages?view=graph-rest-1.0&tabs=http#using-filter-and-orderby-in-the-same-query
    # Example
    # - query_filter = 'from/emailaddress/address eq test@company.com'
    # - order_by = 'from/emailAddress/address,sentDateTime desc'

    return folder.get_messages(query=query_filter, order_by=order_by, limit=limit)


def get_value_from_subject(message: Message, extract_regex) -> str:
    subject = message.subject()
    matches = re.findall(extract_regex, subject)

    return matches[0] if matches else None


def get_value_from_body(message: Message, extract_regex: str) -> str:
    body = message.get_body_text()
    matches = re.findall(extract_regex, body)

    return matches[0] if matches else None


def send_message(mailbox: MailBox, subject: str, body: str, to: list, sender: str) -> Message:
    drafts_folder = mailbox.drafts_folder()

    message = drafts_folder.new_message()
    message.subject = subject
    message.body = body
    message.sender = sender

    for recipient in to:
        message.to.add(recipient)

    message.send()
    return message

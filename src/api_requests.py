from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import base64
import contextlib
import json
import requests

from datetime import date
from dateutil.relativedelta import relativedelta

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def authenticate_gmail_api():
    """Authenticate email API from credentials stored in a local JSON file.

    Returns:
        API service object.
    """

    SCOPE = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPE)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPE)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    return service

def get_email_content(service, query):
    """Use the GMail API to query email bodies and decode into string format.

    Args:
        service: GMail API service object.
        query: A string containing GMail search syntax.
    
    Returns:
        decoded_list: A list of email bodies.
    """

    # Call the Gmail API
    emails = service.users().messages().list(userId='me',q=query, maxResults=101,includeSpamTrash=False).execute()
    emails = emails.get('messages')

    id_list = [id['id'] for id in emails]
    del emails

    body_list = []

    # Check for container MIME message parts.

    body = service.users().messages().get(userId='me',id=id_list[0]).execute().get('payload').get('body').get('data')

    if body == None:
        for email in id_list:
            body = service.users().messages().get(userId='me',id=email).execute().get('payload').get('parts')
            text = body[0].get('body').get('data')
            html = body[1].get('body').get('data')
            body = tuple((text,html))
            #del text
            #del html
            body_list.append(html)
        
    else:
        for email in id_list:
            body = service.users().messages().get(userId='me',id=email).execute().get('payload').get('body').get('data')
            body_list.append(body)

    del id_list
    del body

    bytes_list = [bytes(str(x),encoding='utf-8') for x in body_list]
    del body_list
    decoded_list = [base64.urlsafe_b64decode(x) for x in bytes_list]
    del bytes_list
    str_list = [str(x) for x in decoded_list]
    del decoded_list
        
    return str_list


def get_rescuetime_daily(KEY):
    """Use the RescueTime API to get daily totals for the past two weeks of time spent on personal digital devices.
    
    Args:
        KEY: RescueTime API Key.

    Returns:
        rescuetime_tuple: List of tuples containing daily total, productive, distracting, and neutral hours.
    """

    url = f'https://www.rescuetime.com/anapi/daily_summary_feed?key={KEY}'

    with requests.Session() as s:
        r = s.get(url)
        iter_result = r.json()

        days = [day.get('date') for day in iter_result]
        prod_hours = [day.get('all_productive_hours') for day in iter_result]
        dist_hours = [day.get('all_distracting_hours') for day in iter_result]
        neut_hours = [day.get('neutral_hours') for day in iter_result]

        rescuetime_tuple = [(day,p,d,n) for (day,p,d,n) in zip(days,prod_hours,dist_hours,neut_hours)]

        s.close()

    return rescuetime_tuple


    
    
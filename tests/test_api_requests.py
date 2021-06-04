from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from contextlib import closing

import pytest

from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

from codex_vitae.api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily


def test_authenticate_gmail_api():
    """
    GIVEN credentials to authenticate a GMail API session,
    WHEN the session is authenticated,
    THEN the API token should be valid.
    """

    os.chdir(os.getenv('CONFIG'))

    service = authenticate_gmail_api(os.getenv('CREDENTIALS'))

    with pytest.raises(google.auth.exceptions.RefreshError):
        pytest.exit('GMail token has expired.')

    service.close()

def test_get_email_content():
    """
    GIVEN credentials to authenticate a GMail API session,
    WHEN the session is authenticated,
    THEN the API token should be valid.
    """

    # Perform API calls for production data.
    os.chdir(os.getenv('CONFIG'))

    date_ = str(date.today()-relativedelta(days=7))

    with closing(authenticate_gmail_api(os.getenv('CREDENTIALS'))) as service:
        remarkable = get_email_content(service,query=f"from:my@remarkable.com,after:{date_}")
        mynetdiary = get_email_content(service,query="from:no-reply@mynetdiary.net")

    assert type(remarkable) == list
    assert type(mynetdiary) == list


def test_get_rescuetime_daily():

    rescuetime = closing(get_rescuetime_daily(os.getenv('API_KEY')))
    
    assert type(rescuetime) == list

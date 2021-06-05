from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from contextlib import closing

from datetime import date
from dateutil.relativedelta import relativedelta

from codex_vitae.api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily


def test_get_email_content():
    """
    GIVEN credentials to authenticate a GMail API session,
    WHEN the session is authenticated and an API call is made,
    THEN the returned objects should be of type list or None.
    """

    os.chdir(os.getenv('CONFIG'))
    date_ = str(date.today()-relativedelta(days=7))
    
    with closing(authenticate_gmail_api(os.getenv('CREDENTIALS'))) as service:
        remarkable = get_email_content(service,query=f"from:my@remarkable.com,after:{date_}")
        mynetdiary = get_email_content(service,query=f"from:no-reply@mynetdiary.net,after:{date_}")

    assert type(remarkable) == list
    assert mynetdiary is None


def test_get_rescuetime_daily():
    """
    GIVEN credentials to authenticate a RescueTime API session,
    WHEN the session is authenticated and an API call is made,
    THEN the returned object should be a list containing 15 elements.
    """

    rescuetime = get_rescuetime_daily(os.getenv('API_KEY'))
    
    assert type(rescuetime) == list
    assert len(rescuetime) == 15

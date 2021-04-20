from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib

from unittest import TestCase
from unittest import mock

class ETLMethodTestCase(TestCase):
    def setUp(self):
        pass

    @mock.patch
    def test_(self):
        """
        GIVEN
        WHEN
        THEN
        """

        pass


    
    def doCleanups(self):
        self.widget.dispose()
        #subTest(
    
# Search the last two weeks of emails for MyNetDiary nutrition reports.
    date_ = str(date.today()-relativedelta(days=14))
    service = authenticate_gmail_api()
    mynetdiary = get_email_content(service,query=f"from:no-reply@mynetdiary.net,after:{date_}")

    #Confirm two weekly reports were returned.
    assert(len(mynetdiary) == 3)



# python -m -c -b --locals unittest test_etl.TestETLMethods
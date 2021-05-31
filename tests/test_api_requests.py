from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from contextlib import closing

from unittest import TestCase
from unittest import mock

from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

from db_module import db_prod, db_backup
from api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily
from text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing


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

        db_ver = db_create(os.getenv('DB_PATH'))   

        rt = get_rescuetime_daily(os.getenv('API_KEY'))
        rt_ins = rescuetime_insert(os.getenv('DB_PATH'), rt)
        
        con = sqlite3.connect(os.getenv('DB_PATH')) 
        #con.row_factory = sqlite3.Row

        sql = """
        select * from rescuetime
        """
        cur = con.cursor()
        cur.execute(sql)
        print(cur.fetchall())
        
        con.close()


    
    def doCleanups(self):
        self.widget.dispose()
        #subTest(
    
# Search the last two weeks of emails for MyNetDiary nutrition reports.
    date_ = str(date.today()-relativedelta(days=14))
    service = authenticate_gmail_api()
    mynetdiary = get_email_content(service,query=f"from:no-reply@mynetdiary.net,after:{date_}")
    
    #Confirm at least one weekly report was returned.
    assert(len(mynetdiary) >= 1)


# python -m -c -b --locals unittest test_etl.TestETLMethods
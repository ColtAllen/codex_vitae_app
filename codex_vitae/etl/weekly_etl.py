from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from contextlib import closing
import json

from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

from sqlite_module import db_prod, db_backup
from api_requests import authenticate_gmail_api, get_email_content, get_rescuetime_daily
from text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing


os.chdir(os.getenv('CONFIG'))

date_ = str(date.today()-relativedelta(days=14))

# Return last two weeks of emails for MyNetDiary nutrition reports.
with authenticate_gmail_api(os.getenv('CREDENTIALS')) as service:
    _remarkable = get_email_content(service,query=f"from:my@remarkable.com,after:{date_}")
    _mynetdiary = get_email_content(service,query=f"from:no-reply@mynetdiary.net,after:{date_}")

_rescuetime = get_rescuetime_daily(os.getenv('API_KEY'))

# Convert reMarkable and MyNetDiary data into tuple generators.
_remarkable = reMarkableParsing().run(_remarkable)

if _mynetdiary is not None:
    _fitness = fitness_parsing(_mynetdiary)
    _nutrition = nutrition_parsing(_mynetdiary)

    _prod_list = [_rescuetime,
                  _remarkable,
                  _fitness,
                  _nutrition,
                  ]

else:
    _prod_list = [_rescuetime,
                  _remarkable,
                  ]

# Insert into DB and create backup files.
db_prod(os.getenv('DB_PATH'), _prod_list)
db_backup(os.getenv('DB_PATH'))

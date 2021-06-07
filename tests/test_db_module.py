from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from contextlib import closing

import pytest

from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

from codex_vitae.etl.sqlite3_module import db_prod, db_backup
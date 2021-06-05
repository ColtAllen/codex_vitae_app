from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json

from codex_vitae.data_viz import journal_calendar

def test_journal_calendar(mocker):
    """
    GIVEN
    WHEN
    THEN
    """

    journal_tuples = [
                      ('2021-01-04',3.0,'This is a sample journal entry for unit testing.'),
                      ('2021-02-04',5.0,'This is also a sample journal entry for unit testing.'),
                      ('2021-03-04',4.0,'This is another sample journal entry for unit testing.'),
                      ('2021-04-04',2.0,'This is yet another sample journal entry for unit testing.'),
                      ('2021-05-04',1.0,'This is one more sample journal entry for unit testing.'),
                      ]
    
    journal_json = journal_calendar(journal_tuples)
    journal_dict = json.loads(journal_json)

    assert type(journal_json) == str
    assert len(journal_dict.get('data')[0].keys()) == 14

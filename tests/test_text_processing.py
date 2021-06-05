from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import pytest
import datetime

from codex_vitae.text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing


with open('test_remarkable.txt', 'r') as f:
        _remarkable = f.read()

with open('test_mynetdiary.txt', 'r') as f:
        _mynetdiary = f.read()

def test_remarkable(remarkable=_remarkable):
    """
    GIVEN An example of a raw reMarkable email body retrieved via the GMail API and variations of cleaned email text,
    WHEN each method in the reMarkableParsing class is called,
    THEN the returned value of each method should match the required format.
    """

    clean1 = 'Sat, Jan 1,2022Mood: 5 This is a sample journal entry for unit testing. '
    clean2 = 'Sat, Jan 1,2022Mood:5 This is a sample journal entry for unit testing. '
    clean3 = 'Sat, Jan 1,2022Mood: 5This is a sample journal entry for unit testing. '
    clean4 = 'Sat, Jan 1,2022Mood:5This is a sample journal entry for unit testing. '

    clean_variants = [clean1, clean2, clean3, clean4]

    # Required formats. 
    date_ = datetime.date(2022, 1, 1)
    rating = 5.0
    entry = 'This is a sample journal entry for unit testing.'
    tuple_ = [(datetime.date(2022, 1, 1),5.0,'This is a sample journal entry for unit testing.')]
    
    cleaned = reMarkableParsing().clean_emails(remarkable)
    dated = reMarkableParsing().journal_date(cleaned)
    rated = reMarkableParsing().mood_rating(cleaned)
    
    # The 'run' method requires a list as an input
    processed = reMarkableParsing().run([remarkable])

    assert clean1 == cleaned
    assert date_ == dated
    assert rating == rated

    for variant in clean_variants:
        parsed = reMarkableParsing().journal_entry(variant)
        assert entry == parsed
    
    assert tuple_ == processed

def test_fitness(mynetdiary=_mynetdiary):
    """
    GIVEN an example of a raw MyNetDiary email body retrieved via the GMail API,
    WHEN the fitness_parsing method is called,
    THEN the returned list of tuples should have a length of 7.
    """

    _fitness = fitness_parsing([mynetdiary])

    assert len(_fitness) == 7
    

def test_nutrition(mynetdiary=_mynetdiary):
    """
    GIVEN An example of a raw MyNetDiary email body retrieved via the GMail API and variations of cleaned email text,
    WHEN the nutrition_parsing method is called,
    THEN the returned list of tuples should have a length of 5.
    """

    _nutrition = nutrition_parsing([mynetdiary])

    assert len(_nutrition) == 5
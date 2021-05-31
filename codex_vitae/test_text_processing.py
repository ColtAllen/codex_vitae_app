import pytest

import datetime

from text_processing import reMarkableParsing, fitness_parsing, nutrition_parsing


def test_remarkable():
    """
    GIVEN An example of a raw email body retrieved via the GMail API,
    WHEN each method in the reMarkableParsing class is called,
    THEN the returned value of each method should match the specified format.
    """

    raw = '<!DOCTYPE HTML PUBLIC>\\r\\n<html><head></head><body>Sat, Jan 1,2022\\r\\n<p>Mood: 5 </p>This is a sample journal entry for unit testing. </p></body>--<br>Sent from my reMarkable paper tablet<br>Get yours at www.remarkable.com<br><br>PS: You cannot reply to this email<br>\\r\\n\''
    
    clean = 'Sat, Jan 1,2022Mood: 5 This is a sample journal entry for unit testing. '
    date_ = datetime.date(2022, 1, 1)
    rating = 5.0
    entry = 'This is a sample journal entry for unit testing.'
    tuple_ = [(datetime.date(2022, 1, 1),5.0,'This is a sample journal entry for unit testing.')]
    
    cleaned = reMarkableParsing().clean_emails(raw)
    dated = reMarkableParsing().journal_date(cleaned)
    rated = reMarkableParsing().mood_rating(cleaned)
    parsed = reMarkableParsing().journal_entry(cleaned)
    processed = reMarkableParsing().run([raw])

    assert clean == cleaned
    assert date_ == dated
    assert rating == rated
    assert entry == parsed
    assert tuple_ == processed

def test_fitness():
    """
    GIVEN
    WHEN
    THEN
    """

    pass

def test_nutrition():
    """
    GIVEN
    WHEN
    THEN
    """

    pass
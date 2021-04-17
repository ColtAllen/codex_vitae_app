import datetime
import re
from dateutil.parser import parse

class reMarkableParsing:
    """Extract date, mood rating, and journal entry from raw email bodies."""

    def __init__(self, text_list: list):
        """Inits reMarkableParsing class with text_list.

        Args:
            text_list: List of strings containing raw emails to be processed.
        """
        self.text_list = text_list

    @staticmethod
    def clean_emails(text: str) -> str:
        """Removes HTML and CSS syntax, line breaks, and footer from journal entries.

        Args:
            text: A string of raw email text.

        Returns:
            clean_text: A string of clean text data.
        """

        # Remove HTML tags
        tag_re = re.compile(r'<[^>]+>')
        text = tag_re.sub('', text)
        # Remove line breaks
        text = text.replace("\\r\\n","")
        # Remove apostrophe breaks
        text = text.replace("\\'","")
        # Remove CSS syntx
        text = text.replace("b'p, li { white-space: pre-wrap; }","")
        # Remove Remarkable Footer
        clean_text = text.replace(" --Sent from my reMarkable paper tabletGet yours at www.remarkable.comPS: You cannot reply to this email'","")

        return clean_text

    @staticmethod
    def mood_rating(text: str) -> float:
        """Extracts mood rating from journal entry, accounting for spacing inconsistencies.

        Args:
            text: A string of cleaned text containing mood rating.

        Returns:
            rating: Mood rating as a float.
        """

        try:
            p = re.compile(r'Mood: \d')
            rating =  float(p.search(text).group().split(":")[1])
        except AttributeError:
            p = re.compile(r'Mood:\d')
            rating =  float(p.search(text).group().split(":")[1])

        return rating

    @staticmethod
    def journal_date(text: str):
        """Extracts date of journal entry and converts to datetime format.

        Args:
            text: A string of cleaned text containing date.
        Returns:
            date: Date as datetime type.
        """

        date_ = parse(text.split("Mood")[0]).date()

        return date_

    @staticmethod
    def journal_entry(text: str) -> str:
        """Extracts journal entry from cleaned text.

        Arguments:
            text: A string of cleaned text.
        Returns:
            entry: A string of journal entry.
        """

        entry = str(text.split(":")[1])[2:]

        return entry
    
    def run(self) -> list:
        """Arranges all journal data in format required for database insertion.

        Returns: 
            journal_tuples: List of tuples sorted by date containing parsed journal data.
        """

        # Emails containing PDF attachments instead of text must be removed.
        for entry in self.text_list:
            if entry == "b'6\\x89\\xde'":
                self.text_list.remove(entry)

        clean_text = [self.clean_emails(entry) for entry in self.text_list]
        mood = [self.mood_rating(entry) for entry in clean_text]
        date_ = [self.journal_date(entry) for entry in clean_text]
        journal = [self.journal_entry(entry) for entry in clean_text]

        journal_tuples = [(day,m,j) for (day,m,j) in zip(date_, mood,journal)]
        journal_tuples = sorted(journal_tuples,key=lambda x: x[0])

        return journal_tuples






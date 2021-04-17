import re

class reMarkableParsing:
    """Extract date, mood rating, and journal entry from raw email bodies.
    
    Attributes:
        text: A string of journal entry text to process.
    
    """

    def __init__(self, text=None):
        """Inits reMarkableParsing class with journal entry."""
        self.text = text

    def clean_journal_entry(self):
        """Removes HTML and CSS syntax, line breaks, and footer from journal entries.
        Arguments:
            text: str of raw journal entry text.
        Returns:
            clean_text: str of clean text data.
        """

        # Remove HTML tags
        tag_re = re.compile(r'<[^>]+>')
        text = tag_re.sub('', self.text)
        # Remove line breaks
        text = text.replace("\\r\\n","")
        # Remove apostrophe breaks
        text = text.replace("\\'","")
        # Remove CSS syntx
        text = text.replace("b'p, li { white-space: pre-wrap; }","")
        # Remove Remarkable Footer
        clean_text = text.replace(" --Sent from my reMarkable paper tabletGet yours at www.remarkable.comPS: You cannot reply to this email'","")

        return clean_text

    def mood_rating(self):
        """Extracts mood rating from journal entry, accounting for spacing inconsistencies.
        Arguments:
            text: str containing mood rating.
        Returns:
            rating: Mood rating as a float.
        """

        clean_text = clean_journal_entry(self.text)

        try:
            p = re.compile(r'Mood: \d')
            rating =  float(p.search(clean_text).group().split(":")[1])
        except AttributeError:
            p = re.compile(r'Mood:\d')
            rating =  float(p.search(clean_text).group().split(":")[1])

        return rating
        
    def journal_date(self):
        """Extracts date of journal entry and converts to datetime format.
        Arguments:
            text: str containing date.
        Returns:
            date: Date as datetime type.
        """
        clean_text = clean_journal_entry(self.text)

        date_ = parse(clean_text.split("Mood")[0]).date()

        return date_

    def journal_entry(self):
        """Extracts journal entry from cleaned text.
        Arguments:
            text: str of clean text.
        Returns:
            entry: str of journal entry.
        """
        clean_text = clean_journal_entry(self.text)

        entry = str(clean_text.split(":")[1])[2:]

        return entry



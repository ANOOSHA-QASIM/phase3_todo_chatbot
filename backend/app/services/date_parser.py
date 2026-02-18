"""
DateParser Service for Phase III AI Chatbot
Handles natural language date parsing with Roman Urdu support
"""

from datetime import date, datetime, timedelta
from typing import Optional
import dateparser
import pytz

class DateParser:
    """
    Parse natural language dates with support for English, Urdu, and Roman Urdu
    """

    # Roman Urdu date mapping dictionary
    ROMAN_URDU_MAPPING = {
        # Days
        "aaj": "today",
        "kal": "tomorrow",
        "parso": "day after tomorrow",
        "parson": "day after tomorrow",
        "kal raat": "tomorrow night",

        # Relative time
        "agle hafte": "next week",
        "agle mahine": "next month",
        "is hafte": "this week",
        "is mahine": "this month",

        # Days of week
        "peer": "monday",
        "mangal": "tuesday",
        "budh": "wednesday",
        "jumerat": "thursday",
        "juma": "friday",
        "hafta": "saturday",
        "itwaar": "sunday",

        # Months
        "january": "january",
        "february": "february",
        "march": "march",
        "april": "april",
        "may": "may",
        "june": "june",
        "july": "july",
        "august": "august",
        "september": "september",
        "october": "october",
        "november": "november",
        "december": "december",
    }

    def __init__(self, timezone: str = "UTC"):
        """
        Initialize DateParser with timezone

        Args:
            timezone: Timezone string (default: UTC)
        """
        self.timezone = pytz.timezone(timezone)

    def _preprocess_roman_urdu(self, text: str) -> str:
        """
        Convert Roman Urdu date expressions to English equivalents

        Args:
            text: Input text potentially containing Roman Urdu dates

        Returns:
            Text with Roman Urdu dates converted to English
        """
        text_lower = text.lower()

        # Replace Roman Urdu terms with English equivalents
        for urdu_term, english_term in self.ROMAN_URDU_MAPPING.items():
            if urdu_term in text_lower:
                text_lower = text_lower.replace(urdu_term, english_term)

        return text_lower

    def parse(self, date_string: str) -> Optional[date]:
        """
        Parse natural language date string to date object

        Supports:
        - English: "tomorrow", "next Friday", "15 Feb"
        - Roman Urdu: "kal", "agle peer", "15 february"
        - ISO dates: "2026-02-15"

        Args:
            date_string: Natural language date string

        Returns:
            date object if parsing successful, None otherwise
        """
        if not date_string or not isinstance(date_string, str):
            return None

        # Preprocess Roman Urdu terms
        processed_text = self._preprocess_roman_urdu(date_string.strip())

        # Parse using dateparser library
        parsed_datetime = dateparser.parse(
            processed_text,
            settings={
                'TIMEZONE': str(self.timezone),
                'RETURN_AS_TIMEZONE_AWARE': True,
                'PREFER_DATES_FROM': 'future',  # Prefer future dates for ambiguous cases
            }
        )

        if parsed_datetime:
            # Convert to date only (no time component)
            return parsed_datetime.date()

        return None

    def parse_with_fallback(self, date_string: str, fallback: Optional[date] = None) -> Optional[date]:
        """
        Parse date with fallback value if parsing fails

        Args:
            date_string: Natural language date string
            fallback: Fallback date if parsing fails (default: None)

        Returns:
            Parsed date or fallback value
        """
        parsed = self.parse(date_string)
        return parsed if parsed is not None else fallback

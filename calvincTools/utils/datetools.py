from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil.rrule import (
    rrule, rruleset, 
    DAILY, WEEKLY, MONTHLY, YEARLY, 
    MO, TU, WE, TH, FR, SA, SU, 
    )

import re

def coerce_date(date_to_coerce: object, raise_on_fail: bool = False) -> date:
    """
    Parse dates in multiple common formats.
    
    Tries various formats and returns the first match.
    """
    if isinstance(date_to_coerce, datetime):
        return date_to_coerce.date()
    if isinstance(date_to_coerce, date):
        return date_to_coerce
    if isinstance(date_to_coerce, str):
        cleaned = date_to_coerce.strip()
        if cleaned:
            # List of common date formats
            commonformats = [
                '%Y-%m-%d',           
                '%Y/%m/%d',           
                '%d-%m-%Y',           
                '%d/%m/%Y',         
                "%m-%d-%Y",
                '%m/%d/%Y',           
                '%d.%m.%Y',          
                '%Y%m%d',            
                '%B %d, %Y',      
                '%b %d, %Y',         
                '%d %B %Y',          
                '%d %b %Y',           
            ]
            for fmt in commonformats:
                try:
                    return datetime.strptime(cleaned, fmt).date()
                except ValueError:
                    continue
    
    if raise_on_fail:
        raise ValueError(f"Unable to coerce date from {date_to_coerce!r}")
    return datetime.today().date()

def IsDateString(datestr):
    try:
        D = parse(datestr)
        return True
    except:
        return False
# IsDateString
    
def parse_relative_time(time_string, reference_time=None):
    """
    Convert relative time strings to datetime objects.
    
    Examples: "2 hours ago", "3 days ago", "1 week ago"
    """
    if reference_time is None:
        reference_time = datetime.now()
    
    # Normalize the string
    time_string = time_string.lower().strip()
    
    # Pattern: number + time unit + "ago"
    pattern = r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s*ago'
    match = re.match(pattern, time_string)
    
    if not match:
        raise ValueError(f"Cannot parse: {time_string}")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    # Map units to timedelta kwargs
    unit_mapping = {
        'second': 'seconds',
        'minute': 'minutes',
        'hour': 'hours',
        'day': 'days',
        'week': 'weeks',
    }
    
    if unit in unit_mapping:
        delta_kwargs = {unit_mapping[unit]: amount}
        return reference_time - timedelta(**delta_kwargs)
    elif unit == 'month':
        # Approximate: 30 days per month
        return reference_time - timedelta(days=amount * 30)
    elif unit == 'year':
        # Approximate: 365 days per year
        return reference_time - timedelta(days=amount * 365)
# parse_relative_time

def extract_date_from_text(text, current_year=None):
    """
    Extract dates from natural language text.
    
    Handles formats like:
    - "January 15th, 2024"
    - "March 3rd"
    - "Dec 25th, 2023"
    """
    if current_year is None:
        current_year = datetime.now().year
    
    # Month names (full and abbreviated)
    months = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    # Pattern: Month Day(st/nd/rd/th), Year (year optional)
    pattern = r'(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?'
    
    matches = re.findall(pattern, text.lower())
    
    if not matches:
        return None
    
    # Take the first match
    month_str, day_str, year_str = matches[0]
    
    month = months[month_str]
    day = int(day_str)
    year = int(year_str) if year_str else current_year
    
    return datetime(year, month, day)
# extract_date_from_text


from datetime import datetime, timedelta
from django import template

register = template.Library()

@register.filter
def add_years(value, years):
    """Add a given number of years to a date string"""
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        new_date = date_obj.replace(year=date_obj.year + int(years))
        return new_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return value

@register.filter
def add_days(value, days):
    """Add a given number of days to a date string"""
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        new_date = date_obj + timedelta(days=int(days))
        return new_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return value

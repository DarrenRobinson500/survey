from datetime import date
import calendar

def create_choices(choices):
    result = []
    for choice in choices:
        result.append((choice, choice))
    return result

def get_month_dates(input_date):
    # Get first and last day of the month
    start_date = date(input_date.year, input_date.month, 1)
    end_date = date(input_date.year, input_date.month, calendar.monthrange(input_date.year, input_date.month)[1])

    # Format month name
    month_label = f"{input_date.strftime('%B %Y')}"

    return month_label, start_date, end_date

def get_quarter_dates(input_date):
    # Define quarter boundaries
    quarters = [
        (date(input_date.year, 1, 1), date(input_date.year, 3, 31)),
        (date(input_date.year, 4, 1), date(input_date.year, 6, 30)),
        (date(input_date.year, 7, 1), date(input_date.year, 9, 30)),
        (date(input_date.year, 10, 1), date(input_date.year, 12, 31)),
    ]

    # Determine which quarter the input date belongs to
    for start_date, end_date in quarters:
        if start_date <= input_date <= end_date:
            label = f"{end_date.strftime('%B %Y')} Quarter"
            return label, start_date, end_date



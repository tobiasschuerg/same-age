def get_number_of_weeks(start_date, end_date):
    delta = end_date - start_date
    num_weeks = delta.days // 7
    return num_weeks + 1


def get_number_of_months(start_date, end_date):
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def get_group_key(start_date, end_date):
    """Return a sortable group key: by week for < 2 years, by month for >= 2 years."""
    delta = end_date - start_date
    if delta.days >= 730:
        return (1, get_number_of_months(start_date, end_date))
    return (0, get_number_of_weeks(start_date, end_date))


def diff_str(start_date, end_date):
    delta = end_date - start_date

    if delta.days >= 730:
        months = get_number_of_months(start_date, end_date)
        y = months // 12
        m = months % 12
        y_label = "year" if y == 1 else "years"
        m_label = "month" if m == 1 else "months"
        if m:
            return f"{y} {y_label} and {m} {m_label}"
        return f"{y} {y_label}"

    years = delta.days // 365
    remaining_days = delta.days - (years * 365)
    weeks = remaining_days // 7 + 1

    y_label = "year" if years == 1 else "years"
    w_label = "week" if weeks == 1 else "weeks"

    if years:
        if weeks:
            return f"{years} {y_label} and {weeks} {w_label}"
        return f"{years} {y_label}"
    return f"{weeks} {w_label}"

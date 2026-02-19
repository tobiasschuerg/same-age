def get_number_of_weeks(start_date, end_date):
    delta = end_date - start_date
    num_weeks = delta.days // 7
    return num_weeks + 1


def diff_str(start_date, end_date):
    delta = end_date - start_date

    years = delta.days // 365
    remaining_days = delta.days - (years * 365)
    weeks = remaining_days // 7

    weeks += 1

    y_label = "year" if years == 1 else "years"
    w_label = "week" if weeks == 1 else "weeks"

    if years:
        if weeks:
            return f"{years} {y_label} and {weeks} {w_label}"
        else:
            return f"{years} {y_label}"
    else:
        return f"{weeks} {w_label}"

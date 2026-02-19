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

    if years:
        if weeks:
            return f'{years} years and {weeks} weeks'
        else:
            return f'{years} years'
    else:
        return f'{weeks} weeks'

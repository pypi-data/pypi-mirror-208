import pytz
from datetime import datetime


def get_dayparting(dayparting_schedule):
    """ Transform a dayparting schedule. """
    ret = []
    for key in sorted(dayparting_schedule):
        base = int(key) * 24
        if dayparting_schedule[key] == [0]:
            continue
        for item in dayparting_schedule[key]:
            ret.append(base + item)

    return ret


def build_filters(filters, **kwargs):
    """ Provide any of `affiliate_id`, `offer_id`, `product_id`, `advertiser_id` to add to list of filters. """
    if 'affiliate_id' in kwargs.keys():
        filters.append({'column': 'affiliateId', 'type': 'includes', 'value': [kwargs['affiliate_id']]})
    if 'offer_id' in kwargs.keys():
        filters.append({'column': 'offerId', 'type': 'includes', 'value': [kwargs['offer_id']]})
    if 'product_id' in kwargs.keys():
        filters.append({'column': 'productId', 'type': 'includes', 'value': [kwargs['product_id']]})
    if 'advertiser_id' in kwargs.keys():
        filters.append({'column': 'advertiserId', 'type': 'includes', 'value': [kwargs['advertiser_id']]})

    return filters


def build_daterange(start_date, end_date):
    _daterange = []
    if isinstance(start_date, datetime):
        _daterange.append(start_date.strftime('%Y-%m-%d'))
    elif isinstance(start_date, str):
        _daterange.append(start_date)
    else:
        raise ValueError('`start_date` must be a date/datetime object or a YYYY-MM-DD string.')

    if isinstance(end_date, datetime):
        _daterange.append(end_date.strftime('%Y-%m-%d'))
    elif isinstance(end_date, str):
        _daterange.append(end_date)
    else:
        raise ValueError('`end_date` must be a date/datetime object or a YYYY-MM-DD string.')

    return _daterange


def format_adjustment_date(date_str):
    """ Prepare a YYYY-MM-DD date string to a valid Edge timestamp.

    For clarity, we like to submit Edge adjustments at noon ET on the given date so that adjustments are clearly
    visible in all timezones when using default date filtering in reporting.

    :param date_str: a YYYY-MM-DD date string
    :return: a localized datetime string, converted to valid Edge input datetime
    """
    try:
        day = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Date must be provided as YYYY-MM-DD.')
    tz = pytz.timezone('America/New_York')
    local_time = tz.localize(day).replace(hour=12)
    return local_time.astimezone(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:00:00.000Z')

from datetime import datetime, timedelta


def get_utc_now(offset_minutes: int) -> str:
    # If using this function to filter emails with timestamp properties (e.g. sentDatetime), offset a few minute back
    # from the time the email was sent if the filter is being called soon after the email send
    current_utc_time = datetime.utcnow()

    adjusted_utc_time = current_utc_time + timedelta(minutes=offset_minutes)
    return adjusted_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

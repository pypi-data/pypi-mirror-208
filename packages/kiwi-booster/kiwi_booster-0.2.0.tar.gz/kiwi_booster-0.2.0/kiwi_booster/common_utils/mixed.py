def get_current_timezone() -> str:
    """
    Get the current timezone of the machine. If will try to get the timezone from the ip address,
    if it fails, it will use the local timezone of the machine.

    Returns:
        str: Timezone string
    """
    local_timezone = str(get_localzone())
    client = IpregistryClient("tryout")
    timezone = client.lookup()._json.get("time_zone", local_timezone)
    if isinstance(timezone, dict):  # if the timezone is a dict, get the value
        timezone = timezone.get("id", local_timezone)

    return timezone


def parse_date_str(date: str) -> datetime:
    """
    Parse a date string in the format YYYY-MM-DD or YYYY-MM-DD HH:MM to a datetime object

    Args:
        date_str (str): Date string in the format YYYY-MM-DD. If None, the current date is used + 1 minute

    Returns:
        datetime.datetime: Datetime object
    """
    if date is None:
        # cron str 1 minute after now
        date = datetime.now() + timedelta(minutes=1)
    else:
        # Parse the date to a datetime object even if hour is not provide
        has_hour = len(date.split(" ")) == 2
        if has_hour:
            date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        else:
            date = datetime.strptime(date, "%Y-%m-%d")
            print("Hour not provided, setting it to 5 am")
            # add 5 hours to the date to make it 5 am
            date = date + timedelta(hours=5)

    return date

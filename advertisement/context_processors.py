from datetime import date, timedelta


def get_today_and_yesterday_date(request):
    """Вычисляет вчерашнюю и сегодняшнюю дату
        и добавляет их в context"""
    date_today = date.today()
    date_yesterday = date_today - timedelta(1)

    context = {
        "date_today": date_today,
        "date_yesterday": date_yesterday,

    }
    return context

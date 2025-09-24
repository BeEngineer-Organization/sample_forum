from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()

from django.utils.translation import gettext, ngettext

@register.filter
@register.simple_tag
def elapsed_time(dt):
    if not dt:
        return None

    delta = timezone.now() - dt

    zero = timedelta()
    one_hour = timedelta(hours=1)
    one_day = timedelta(days=1)
    one_week = timedelta(days=7)

    # 未来の時刻はエラーにする
    if delta < zero:
        raise ValueError("未来の時刻です。")

    if delta < one_hour:  # 経過時間が 1 時間以内のとき
        minutes = delta.seconds // 60
        return ngettext("%d minute ago", "%d minutes ago", minutes) % minutes
    elif delta < one_day:  # 経過時間が 1 日以内のとき
        hours = delta.seconds // 3600
        return ngettext("%d hour ago", "%d hours ago", hours) % hours
    elif delta < one_week:  # 経過時間が 1 週間以内のとき
        return ngettext("%d day ago", "%d days ago", delta.days) % delta.days
    else:
        return gettext("more than 1 week")
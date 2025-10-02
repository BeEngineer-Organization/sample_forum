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
            return f"{delta.seconds // 60} 分前"
        elif delta < one_day:  # 経過時間が 1 日以内のとき
            return f"{delta.seconds // 3600} 時間前"
        elif delta < one_week:  # 経過時間が 1 週間以内のとき
            return f"{delta.days} 日前"
        else:
            return "1 週間以上前"
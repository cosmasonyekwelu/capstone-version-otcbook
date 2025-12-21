from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import OPHistory, Badge, UserBadge, Notification
from trades.models import Trade


TRADE_POINTS = 10
FAST_TRADE_BONUS_PERCENT = 18


def award_trade_points(trade: Trade):
    user = trade.trader

    OPHistory.objects.create(
        user=user,
        action="trade_logged",
        points=TRADE_POINTS,
        meta={"trade_id": trade.id}
    )

    if timezone.now() - trade.trade_date <= timedelta(minutes=2):
        bonus = int(TRADE_POINTS * FAST_TRADE_BONUS_PERCENT / 100)
        OPHistory.objects.create(
            user=user,
            action="trade_bonus",
            points=bonus,
            meta={"trade_id": trade.id}
        )

    check_badges(user)


def check_badges(user):
    trade_count = Trade.objects.filter(trader=user).count()

    if trade_count >= 100:
        badge = Badge.objects.get(code="pro_trader")
        unlocked, created = UserBadge.objects.get_or_create(
            user=user,
            badge=badge
        )

        if created:
            OPHistory.objects.create(
                user=user,
                action="badge_unlocked",
                points=0,
                meta={"badge": badge.code}
            )

            Notification.objects.create(
                user=user,
                type="badge",
                title="Badge Unlocked",
                message=f"You unlocked the {badge.name} badge!"
            )


def get_total_op(user):
    return (
        OPHistory.objects
        .filter(user=user)
        .aggregate(total=Sum("points"))["total"]
        or 0
    )

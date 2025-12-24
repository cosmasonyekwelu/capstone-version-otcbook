from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from trades.models import Trade
from .models import OPHistory, Badge, UserBadge, Notification


class GamificationService:
    BASE_TRADE_POINTS = 10
    FAST_TRADE_BONUS_PERCENT = 18
    INVITE_POINTS = 30

    @staticmethod
    def award_trade_points(trade: Trade):
        user = trade.trader
        points = GamificationService.BASE_TRADE_POINTS
        is_fast = False

        if trade.trade_date:
            delta = abs((trade.created_at - trade.trade_date).total_seconds())
            if delta <= 120:
                bonus = int(points * GamificationService.FAST_TRADE_BONUS_PERCENT / 100)
                points += bonus
                is_fast = True

                OPHistory.objects.create(
                    user=user,
                    action="trade_bonus",
                    points=bonus,
                    meta={"trade_id": trade.id},
                )

        OPHistory.objects.create(
            user=user,
            action="trade_logged",
            points=points,
            meta={
                "trade_id": trade.id,
                "asset": trade.asset.symbol,
                "amount": float(trade.amount_ngn),
                "fast": is_fast,
            },
        )

        Notification.objects.create(
            user=user,
            type="points",
            title="Trade Logged",
            message=f"+{points} OP earned for logging a trade",
        )

        GamificationService.check_badges(user)

    @staticmethod
    def award_invite_points(user):
        OPHistory.objects.create(
            user=user,
            action="invite",
            points=GamificationService.INVITE_POINTS,
        )

        Notification.objects.create(
            user=user,
            type="points",
            title="Invite Bonus",
            message=f"+{GamificationService.INVITE_POINTS} OP for inviting a teammate",
        )

        GamificationService.check_badges(user)

    @staticmethod
    def check_badges(user):
        total_points = (
            OPHistory.objects.filter(user=user)
            .aggregate(total=Sum("points"))["total"]
            or 0
        )

        total_trades = Trade.objects.filter(trader=user).count()

        badges = Badge.objects.filter(is_active=True)

        for badge in badges:
            if total_trades >= badge.min_trades and total_points >= badge.min_points:
                obj, created = UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge,
                )

                if created:
                    OPHistory.objects.create(
                        user=user,
                        action="badge_unlocked",
                        points=0,
                        meta={"badge": badge.code},
                    )

                    Notification.objects.create(
                        user=user,
                        type="badge",
                        title="Badge Unlocked",
                        message=f"You unlocked the {badge.name} badge",
                    )

from django.db.models.signals import post_save
from django.dispatch import receiver
from trades.models import Trade
from .services import GamificationService


@receiver(post_save, sender=Trade)
def trade_created(sender, instance, created, **kwargs):
    if created:
        GamificationService.award_trade_points(instance)

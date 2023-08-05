from django.dispatch import receiver

from pretix.base.signals import register_payment_providers
from pretix.presale.signals import order_meta_from_request

@receiver(register_payment_providers, dispatch_uid="payment_mpesa.provider")
def register_payment_provider(sender, **kwargs):
    from .payment import MpesaPayment
    return MpesaPayment
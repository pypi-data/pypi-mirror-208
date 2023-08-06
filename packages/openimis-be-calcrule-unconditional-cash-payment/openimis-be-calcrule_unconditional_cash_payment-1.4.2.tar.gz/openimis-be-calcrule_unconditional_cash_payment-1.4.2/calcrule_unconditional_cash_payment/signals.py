from core.forms import User
from core.signals import bind_service_signal
from core.service_signals import ServiceSignalBindType
from policy.models import Policy
from calcrule_unconditional_cash_payment.calculation_rule import UnconditionalCashPaymentCalculationRule


def bind_service_signals():
    bind_service_signal(
        'policy_service.create',
        on_policy_create,
        bind_type=ServiceSignalBindType.AFTER
    )


def on_policy_create(**kwargs):
    policy = kwargs.get('result', None)
    if policy:
        if policy.status in [Policy.STATUS_IDLE, Policy.STATUS_ACTIVE]:
            user = User.objects.filter(i_user__id=policy.audit_user_id).first()
            # run calcrule for Bill if there is valid rule
            return UnconditionalCashPaymentCalculationRule.signal_calculate_event.send(
                sender=policy.__class__.__name__, instance=policy, user=user, context="PolicyCreated"
            )

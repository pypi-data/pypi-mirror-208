from django.contrib.contenttypes.models import ContentType

from calcrule_unconditional_cash_payment.apps import AbsCalculationRule
from calcrule_unconditional_cash_payment.config import CLASS_RULE_PARAM_VALIDATION, DESCRIPTION_CONTRIBUTION_VALUATION, FROM_TO
from calcrule_unconditional_cash_payment.converters import PolicyToBillConverter, PolicyToBillItemConverter

from contribution_plan.models import PaymentPlan
from invoice.services import BillService
from core.models import User
from core.signals import *
from core import datetime


class UnconditionalCashPaymentCalculationRule(AbsCalculationRule):
    version = 1
    uuid = "16bca786-1c12-4e8e-9cbf-e33c2a6d9f4f"
    calculation_rule_name = "payment: unconditional cash payment"
    description = DESCRIPTION_CONTRIBUTION_VALUATION
    impacted_class_parameter = CLASS_RULE_PARAM_VALIDATION
    date_valid_from = datetime.datetime(2000, 1, 1)
    date_valid_to = None
    status = "active"
    from_to = FROM_TO
    type = "account_payable"
    sub_type = "cash_payment"

    signal_get_rule_name = Signal(providing_args=[])
    signal_get_rule_details = Signal(providing_args=[])
    signal_get_param = Signal(providing_args=[])
    signal_get_linked_class = Signal(providing_args=[])
    signal_calculate_event = Signal(providing_args=[])
    signal_convert_from_to = Signal(providing_args=[])

    @classmethod
    def ready(cls):
        now = datetime.datetime.now()
        condition_is_valid = (now >= cls.date_valid_from and now <= cls.date_valid_to) \
            if cls.date_valid_to else (now >= cls.date_valid_from and cls.date_valid_to is None)
        if condition_is_valid:
            if cls.status == "active":
                # register signals getParameter to getParameter signal and getLinkedClass ot getLinkedClass signal
                cls.signal_get_rule_name.connect(cls.get_rule_name, dispatch_uid="on_get_rule_name_signal")
                cls.signal_get_rule_details.connect(cls.get_rule_details, dispatch_uid="on_get_rule_details_signal")
                cls.signal_get_param.connect(cls.get_parameters, dispatch_uid="on_get_param_signal")
                cls.signal_get_linked_class.connect(cls.get_linked_class, dispatch_uid="on_get_linked_class_signal")
                cls.signal_calculate_event.connect(cls.run_calculation_rules, dispatch_uid="on_calculate_event_signal")
                cls.signal_convert_from_to.connect(cls.run_convert, dispatch_uid="on_convert_from_to")

    @classmethod
    def active_for_object(cls, instance, context, type="account_payable", sub_type="cash_payment"):
        return instance.__class__.__name__ == "Policy" \
               and context in ["PolicyCreated"] \
               and cls.check_calculation(instance)

    @classmethod
    def check_calculation(cls, instance):
        class_name = instance.__class__.__name__
        match = False
        if class_name == "ABCMeta":
            match = str(cls.uuid) == str(instance.uuid)
        elif class_name == "PaymentPlan":
            match = str(cls.uuid) == str(instance.calculation)
        elif class_name == "Policy":
            match = cls.check_calculation(instance.product)
        elif class_name == "Product":
            # if product → paymentPlans
            payment_plans = PaymentPlan.objects.filter(benefit_plan=instance, is_deleted=False)
            for pp in payment_plans:
                if cls.check_calculation(pp):
                    match = True
                    break
        return match

    @classmethod
    def calculate(cls, instance, **kwargs):
        context = kwargs.get('context', None)
        user = kwargs.get('user', None)
        if user is None:
            user = User.objects.filter(i_user__id=instance.audit_user_id).first()
        class_name = instance.__class__.__name__
        if class_name == "Policy":
            product = instance.product
            payment_plan = PaymentPlan.objects.filter(benefit_plan=product, calculation=cls.uuid, is_deleted=False)
            if payment_plan:
                payment_plan = payment_plan.first()
                cls.run_convert(instance=instance,
                                context=context,
                                convert_to='Bill',
                                payment_plan=payment_plan,
                                user=user)
            return f"conversion finished {cls.calculation_rule_name}"

    @classmethod
    def get_linked_class(cls, sender, class_name, **kwargs):
        list_class = []
        if class_name is not None:
            model_class = ContentType.objects.filter(model=class_name).first()
            if model_class:
                model_class = model_class.model_class()
                list_class = list_class + [f.remote_field.model.__name__ for f in model_class._meta.fields
                                           if f.get_internal_type() == 'ForeignKey'
                                           and f.remote_field.model.__name__ != "User"]
        else:
            list_class.append("Calculation")
        # because we have calculation in PaymentPlan
        #  as uuid - we have to consider this case
        if class_name == "PaymentPlan":
            list_class.append("Calculation")
        return list_class

    @classmethod
    def convert(cls, instance, convert_to, **kwargs):
        context = kwargs.get('context', None)
        payment_plan = kwargs.get('payment_plan')
        convert_results = {}
        if context == "PolicyCreated":
            json_data = cls._get_data_from_json_ext(payment_plan)
            convert_results = cls._convert_policies(convert_to, payment_plan, instance, json_data)
            convert_results['user'] = kwargs.get('user', None)
            convert_results['type_conversion'] = 'batch run policy - bill'
            BillService.bill_create(convert_results=convert_results)
        return convert_results

    @classmethod
    def _get_data_from_json_ext(cls, payment_plan):
        json_data = {}
        if 'calculation_rule' in payment_plan.json_ext:
            calculation_rule_json_ext_dict = payment_plan.json_ext['calculation_rule']
            if 'lumpsum_to_be_paid' in calculation_rule_json_ext_dict:
                json_data['lumpsum_to_be_paid'] = calculation_rule_json_ext_dict['lumpsum_to_be_paid']
            if 'invoice_label' in calculation_rule_json_ext_dict:
                json_data['invoice_label'] = calculation_rule_json_ext_dict['invoice_label']
        return json_data

    @classmethod
    def _convert_policies(cls, convert_to, payment_plan, instance, json_data):
        convert_results = {}
        if convert_to == 'Bill':
            convert_results['bill_data'] = \
                PolicyToBillConverter.to_bill_obj(payment_plan=payment_plan,
                                                  policy=instance,
                                                  lumpsum_to_be_paid=json_data['lumpsum_to_be_paid'],
                                                  invoice_label=json_data['invoice_label'])
            convert_results['bill_data_line'] = \
                [PolicyToBillItemConverter.to_bill_item_obj(policy=instance,
                                                            lumpsum_to_be_paid=json_data['lumpsum_to_be_paid'])]
        return convert_results


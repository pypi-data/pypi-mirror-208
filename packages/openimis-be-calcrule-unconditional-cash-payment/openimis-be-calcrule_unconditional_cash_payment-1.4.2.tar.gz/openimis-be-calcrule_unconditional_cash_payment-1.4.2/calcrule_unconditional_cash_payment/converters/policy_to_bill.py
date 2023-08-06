from django.contrib.contenttypes.models import ContentType
from invoice.apps import InvoiceConfig
from invoice.models import Bill


class PolicyToBillConverter:

    @classmethod
    def to_bill_obj(cls, payment_plan, policy, lumpsum_to_be_paid, invoice_label):
        bill = {}
        cls.build_subject(bill, policy)
        cls.build_thirdparty(bill, policy)
        cls.build_code(bill, policy)
        cls.build_price(bill, lumpsum_to_be_paid)
        cls.build_terms(bill, payment_plan, invoice_label)
        cls.build_date_dates(bill, policy)
        cls.build_currency(bill)
        cls.build_status(bill)
        return bill

    @classmethod
    def build_subject(cls, bill, policy):
        bill["subject_id"] = policy.id
        bill['subject_type'] = ContentType.objects.get_for_model(policy)

    @classmethod
    def build_thirdparty(cls, bill, policy):
        bill["thirdparty_id"] = policy.family.head_insuree.id
        bill['thirdparty_type'] = ContentType.objects.get_for_model(policy.family.head_insuree)

    @classmethod
    def build_code(cls, bill, policy):
        bill["code"] = f"IV-UC-{policy.family.head_insuree.chf_id}-{policy.id}"

    @classmethod
    def build_price(cls, bill, lumpsum_to_be_paid):
        bill["amount_net"] = lumpsum_to_be_paid

    @classmethod
    def build_date_dates(cls, bill, policy):
        from core import datetime, datetimedelta
        bill["date_due"] = datetime.date.today() + datetimedelta(days=30)
        bill["date_bill"] = datetime.date.today()
        bill["date_valid_from"] = policy.validity_from
        bill["date_valid_to"] = policy.validity_to

    @classmethod
    def build_currency(cls, bill):
        bill["currency_tp_code"] = InvoiceConfig.default_currency_code
        bill["currency_code"] = InvoiceConfig.default_currency_code

    @classmethod
    def build_status(cls, bill):
        bill["status"] = Bill.Status.VALIDATED.value

    @classmethod
    def build_terms(cls, bill, payment_plan, invoice_label):
        bill["terms"] = f'{payment_plan.benefit_plan.name}, {invoice_label}'

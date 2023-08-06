from django.contrib.contenttypes.models import ContentType


class PolicyToBillItemConverter:

    @classmethod
    def to_bill_item_obj(cls, policy, lumpsum_to_be_paid):
        bill_line_item = {}
        cls.build_line_fk(bill_line_item, policy)
        cls.build_code(bill_line_item, policy)
        cls.build_date_dates(bill_line_item, policy)
        cls.build_price(bill_line_item, lumpsum_to_be_paid)
        cls.build_quantity(bill_line_item)
        return bill_line_item
    
    @classmethod
    def build_line_fk(cls, bill_line_item, policy):
        bill_line_item["line_id"] = policy.id
        bill_line_item['line_type'] = ContentType.objects.get_for_model(policy)

    @classmethod
    def build_quantity(cls, bill_line_item):
        bill_line_item["quantity"] = 1

    @classmethod
    def build_price(cls, bill_line_item, lumpsum_to_be_paid):
        bill_line_item["amount_total"] = lumpsum_to_be_paid
        bill_line_item["unit_price"] = int(lumpsum_to_be_paid)

    @classmethod
    def build_code(cls, bill_line_item, policy):
        bill_line_item["code"] = f"IV-UC-{policy.family.head_insuree.chf_id}-{policy.id}"

    @classmethod
    def build_date_dates(cls, bill, policy):
        bill["date_valid_from"] = policy.validity_from
        bill["date_valid_to"] = policy.validity_to

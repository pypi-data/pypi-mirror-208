import json

from django.contrib.contenttypes.models import ContentType


class PremiumToBillItemConverter(object):

    @classmethod
    def to_bill_line_item_obj(cls, batch_run, premium, payment_plan, commission_value):
        bill_line_item = {}
        cls.build_line_fk(bill_line_item, premium)
        cls.build_dates(bill_line_item, batch_run)
        cls.build_code(bill_line_item, payment_plan, premium)
        cls.build_description(bill_line_item)
        cls.build_details(bill_line_item, premium)
        cls.build_quantity(bill_line_item)
        cls.build_unit_price(bill_line_item, commission_value)
        cls.build_discount(bill_line_item, payment_plan)
        #cls.build_tax(bill_line_item)
        cls.build_amounts(bill_line_item)
        return bill_line_item

    @classmethod
    def build_line_fk(cls, bill_line_item, premium):
        bill_line_item["line_id"] = premium.id
        bill_line_item['line_type'] = ContentType.objects.get_for_model(premium)

    @classmethod
    def build_dates(cls, bill_line_item, batch_run):
        from core import datetime, datetimedelta
        bill_line_item["date_valid_from"] = batch_run.run_date
        bill_line_item["date_valid_to"] = batch_run.run_date + datetimedelta(days=30)

    @classmethod
    def build_code(cls, bill_line_item, payment_plan, premium):
        bill_line_item["code"] = f"{payment_plan.code}-{premium.id}"

    @classmethod
    def build_description(cls, bill_line_item):
        bill_line_item["description"] = "Commission"

    @classmethod
    def build_details(cls, bill_line_item, premium):
        details = {
            "head_of_family_chfid": f'{premium.policy.family.head_insuree.chf_id}',
        }
        bill_line_item["details"] = details

    @classmethod
    def build_quantity(cls, bill_line_item):
        bill_line_item["quantity"] = 1

    @classmethod
    def build_unit_price(cls, bill_line_item, commission_value):
        bill_line_item["unit_price"] = commission_value

    @classmethod
    def build_discount(cls, bill_line_item, payment_plan):
        pp_params = payment_plan.json_ext
        if isinstance(pp_params, str):
            pp_params = json.loads(pp_params)
        if pp_params:
            pp_params = pp_params["calculation_rule"] if "calculation_rule" in pp_params else None
        commision_rate = 0
        if "commision_rate" in pp_params:
            commision_rate = float(pp_params["commision_rate"])
        bill_line_item["discount"] = 1-(commision_rate/100) if commision_rate != 0 else 0

    @classmethod
    def build_tax(cls, bill_line_item):
        bill_line_item["tax_rate"] = None
        bill_line_item["tax_analysis"] = None

    @classmethod
    def build_amounts(cls, bill_line_item):
        bill_line_item["amount_net"] = bill_line_item["quantity"] * bill_line_item["unit_price"]
        bill_line_item["amount_total"] = bill_line_item["amount_net"]

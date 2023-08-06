CLASS_RULE_PARAM_VALIDATION = [
    {
        "class": "PaymentPlan",
        "parameters": [
            {
                "type": "number",
                "name": "lumpsum_to_be_paid",
                "label": {
                    "en": "Lumpsum to be paid",
                    "fr": "Lumpsum to be paid"
                },
                "rights": {
                    'read': "157101",
                    "write": "157102",
                    "update": "157103",
                    "replace": "157206"
                },
                "relevance": "True",
                "condition": "INPUT>=0",
                "default": "0"
            },
            {
                "type": "string",
                "name": "invoice_label",
                "label": {
                    "en": "Invoice label",
                    "fr": "Invoice label"
                },
                "rights": {
                    "read": "157101",
                    "write": "157102",
                    "update": "157103",
                    "replace": "157206"
                },
                "relevance": "True",
                "default": "value"
            },
        ]
    },
    {
        "class": "Product",
        "parameters": [
            ]
    },
    {
        "class": "Family",
        "parameters": [
            ]
    }
]

FROM_TO = [
        {'from':  'Policy', 'to':  'Bill'},
        {'from':  'Policy', 'to':  'BillItem'}
]


DESCRIPTION_CONTRIBUTION_VALUATION = F"" \
    F"This calculation will, for the selected product" \
    F" create bill with 1 item, if the policy is about a product with a payment plan linked to this calculation"

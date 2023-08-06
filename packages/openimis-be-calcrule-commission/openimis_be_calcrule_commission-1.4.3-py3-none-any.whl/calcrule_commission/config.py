CLASS_RULE_PARAM_VALIDATION = [
    {
        "class": "PaymentPlan",
        "parameters": [
            {
                "type": "number",
                "name": "commission_rate",
                "label": {
                    "en": "Commission rate(%)",
                    "fr": "Taux de commission(%)"
                },
                "rights": {
                    'read': "157101",
                    "write": "157102",
                    "update": "157103",
                    "replace": "157206"
                },
                "relevance": "True",
                "condition": "INPUT<100",
                "default": "10"
            }
        ]
    },
    {
        "class": "Product",
        "parameters": [
            ]
    }
]

FROM_TO = [
        {"from": "BatchRun", "to": "Bill"},
        {"from": "Premium", "to": "BillItem"}
]

DESCRIPTION_CONTRIBUTION_VALUATION = F"" \
    F"This calculation will, for the selected level and product," \
    F" calculate how much the insurance need to" \
    F" pay the commission to EO"

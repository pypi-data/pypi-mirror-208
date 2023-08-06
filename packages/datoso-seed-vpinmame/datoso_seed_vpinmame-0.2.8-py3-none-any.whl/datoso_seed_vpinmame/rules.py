from datoso_seed_vpinmame.dats import VPinMameDat

rules = [
    {
        'name': 'VPinMame Dat',
        '_class': VPinMameDat,
        "seed": "vpinmame",
        "priority": 50,
        "rules": [
            {
                "key": "name",
                "operator": "contains",
                "value": "VPinMAME"
            }
        ]
    }
]


def get_rules():
    return rules
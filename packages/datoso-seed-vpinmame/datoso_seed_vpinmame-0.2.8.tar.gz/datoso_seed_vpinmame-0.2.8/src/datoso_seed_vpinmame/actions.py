from datoso_seed_vpinmame.dats import VPinMameDat

actions = {
    '{dat_origin}': [
        {
            'action': 'LoadDatFile',
            '_class': VPinMameDat
        },
        {
            'action': 'DeleteOld'
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}'
        },
        {
            'action': 'SaveToDatabase'
        }
    ]
}

def get_actions():
    return actions
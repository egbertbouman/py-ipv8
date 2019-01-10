from __future__ import absolute_import

import copy

default = {
    'address': '0.0.0.0',
    'port': 8090,
    'keys': [
        {
            'alias': "my peer",
            'generation': u"medium",
            'file': u"ec.pem"
        },
        {
            'alias': "anonymous id",
            'generation': u"curve25519",
            'file': u"ec_multichain.pem"
        }
    ],
    'logger': {
        'level': "INFO"
    },
    'walker_interval': 0.5,
    'overlays': [
        {
            'class': 'DiscoveryCommunity',
            'key': "my peer",
            'walkers': [
                {
                    'strategy': "RandomWalk",
                    'peers': 20,
                    'init': {
                        'timeout': 3.0
                    }
                },
                {
                    'strategy': "RandomChurn",
                    'peers': -1,
                    'init': {
                        'sample_size': 8,
                        'ping_interval': 10.0,
                        'inactive_time': 27.5,
                        'drop_time': 57.5
                    }
                }
            ],
            'initialize': {},
            'on_start': [
                ('resolve_dns_bootstrap_addresses', )
            ]
        },
        {
            'class': 'AttestationCommunity',
            'key': "anonymous id",
            'walkers': [{
                'strategy': "RandomWalk",
                'peers': 4,
                'init': {
                    'timeout': 60.0
                }
            }],
            'initialize': {},
            'on_start': []
        },
        {
            'class': 'IdentityCommunity',
            'key': "anonymous id",
            'walkers': [{
                'strategy': "RandomWalk",
                'peers': 4,
                'init': {
                    'timeout': 60.0
                }
            }],
            'initialize': {},
            'on_start': []
        },
    ]
}

def get_default_configuration():
    return copy.deepcopy(default)

__all__ = ['get_default_configuration']

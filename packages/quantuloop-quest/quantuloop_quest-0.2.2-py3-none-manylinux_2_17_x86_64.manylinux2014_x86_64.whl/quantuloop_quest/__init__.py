"""This module provides a package that includes an interface to the GPU accelerated quantum simulator
QuEST. This simulator can be used as a quantum execution target for the quantum
programming language Ket. For more information on the Ket language, visit <https://quantumket.org>.

Quantuloop QuEST is a powerful simulator build with the open-source quantum simulator QuEST.

To use Quantuloop QuEST, you must obtain a Quantuloop Access Token. This token is required to
authenticate your access to the simulator. To get an access token, visit the Quantuloop website
at https://quantuloop.com."""

from __future__ import annotations
# Copyright (C) 2023 Quantuloop - All rights reserved

__version__ = "0.2.2"

from ctypes import *
from os import environ, PathLike
from os.path import dirname
from random import Random
from typing import Literal
import warnings
from ket.base import set_quantum_execution_target, set_process_features
from ket.clib.wrapper import load_lib
import jwt

__all__ = ["set_simulator"]

QULOOP_PUBKEY = """\
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAqMVLlLgPaisE4Se3oqqF
1zgxFsQuBpv46d25X60FnGe2TVbqxz6lCVT33oowk22b9sMVjTkMoFCL4ocTCQxP
PLUqNgJnWAGr1GpdUvTzWgB5An2V9rKvknfLuSfoCeVIV5qxonz45Yh/F83cDjU3
T4+oXDjvadc9rGQmKhZ46yPeeODj/EGwcGUbgOcg3g3SckfO035NXrWfz8ndUWre
zrbHHAJdpCfEh9yBct9qMcVeQ3nlRwHG8z7d9/d8XKCujvEOWs3WV/kHt5B+M4Xc
29BtyaRFJ/kpluz+glA6eYtwPx3VRc/4QXjEVz6jOjEUe/rdATJUmL3LA/P5iawI
zGPe8qUAbLrY9fRIoAyA9NELtt61Vqrez3/i89MqX8wEc7CDzKmzafFwGJrdEhCp
WkN9eR6dJ7jtJsqXdm+CKJ+Le/4u/rqM+hWjIKjERPHTMGHwzHhWAQgAopasu/SJ
OtSm7/au1KBYG8efS0Q1KXl7xO3B8CxS5iKGtOgqW1mwZ/0V9Cx22NHdHteWEJtj
plVVSEgb5yZLX9hnTBbQaVmo3Up6QzCbIR8r/p9HKzJ/gWarvpy26T+rO5Rh+JdY
YKrqZc6vpo3uYm+7jLWGFsTH0JesgwYXkK59nuOPIoGEBLtPIl5CuZS7awMH5mSM
QWbrTs7JkgcoZ9HgU17m+y8CAwEAAQ==
-----END PUBLIC KEY-----
"""

API = load_lib(
    'Quantuloop QuEST',
    dirname(__file__)+"/libquloop_quest.so",
    {
        'quloop_quest_run_and_set_result': ([c_void_p], []),
        'quloop_quest_run_serialized': ([POINTER(c_uint8), c_size_t, POINTER(c_uint8), c_size_t, c_int32], [c_void_p]),
        'kbw_result_get': ([c_void_p], [POINTER(c_uint8), c_size_t]),
        'kbw_result_delete': ([c_void_p], []),
    },
    'kbw_error_message'
)

RNG = Random()


def _quantum_execution_target(process):
    environ['QULOOP_SEED'] = str(RNG.getrandbits(64))
    API['quloop_quest_run_and_set_result'](process)


def set_simulator(*,
                  token: str | None = None,
                  token_file: PathLike | None = None,
                  seed: any | None = None,
                  dump_type: Literal["vector",
                                     "probability", "shots"] | None = None,
                  shots: int | None = None):
    """Set Quantuloop QuEST as the quantum execution target.

    Args:
        token: A Quantuloop Access Token. This token is used to authenticate access to the
            simulator. If you do not provide a token, the simulator will not work.
        token_file: A file containing the Quantuloop Access Token. The file must contain a
            single line with the access token. If you specify both a token and a token file,
            the function will raise a ValueError.
        seed: A value used to initialize the simulator's random number generator.
            If you do not provide a seed, the simulator will generate a random seed.
        dump_type: A string that specifies the dump type.
        shots: An integer select the number of shots for dump type "shots".
    """

    if token is not None and token_file is not None:
        raise ValueError(
            'parameter "token" must not be used when the parameter "token_file" is set')

    if token_file is not None:
        with open(token_file, 'r') as file:
            token = file.read()
    if token is not None:
        environ['QULOOP_TOKEN'] = str(token)

    if seed is not None:
        global RNG
        RNG = Random(seed)

    if dump_type:
        if dump_type not in ["vector", "probability", "shots"]:
            raise ValueError(
                'parameter "dump_type" must be "vector", "probability", or "shots"')
        environ['QULOOP_DUMP_TYPE'] = dump_type

    if shots:
        if shots < 1:
            raise ValueError('parameter "shots" must be greater than one')
        environ['QULOOP_SHOTS'] = str(shots)

    if 'QULOOP_TOKEN' not in environ:
        warnings.warn('Quantuloop Access Token undefined')
    else:
        try:
            jwt.decode(environ['QULOOP_TOKEN'], QULOOP_PUBKEY,
                       algorithms=['RS256'], audience="sim")
        except Exception as exception:
            warnings.warn(f'Quantuloop Access Token: {exception}')

    set_quantum_execution_target(_quantum_execution_target)
    set_process_features(plugins=['pown'])

"""The Quantuloop Quantum Simulator Suite for HPC is a collection of
high-performance quantum computer simulators for the Ket programming language.

As quantum algorithms explore distinct aspects of quantum computation
to extract advantages, there is no silver bullet for the simulation
of a quantum computer.

To use this simulator, you will need a Quantuloop Access Token. For more information,
visiting https://simulator.quantuloop.com."""

from __future__ import annotations
# Copyright (C) 2023 Quantuloop - All rights reserved

from os import environ, PathLike
from typing import Literal
import quantuloop_dense
import quantuloop_sparse
import quantuloop_quest


def set_simulator(simulator: Literal['Dense', 'Sparse', 'QuEST'] | None = None, *,
                  token: str | None = None,
                  token_file: PathLike | None = None,
                  seed: any | None = None,
                  dump_type: Literal['vector',
                                     'probability', 'shots'] | None = None,
                  shots: int | None = None,
                  gpu_count: int | None = None,
                  precision: Literal[1, 2] | None = None):
    """Set a Quantuloop simulator as the quantum execution target

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
        gpu_count: An integer that determine the maximum number of GPUs used in the execution.
            If set to 0, the simulator will use all available GPUs.
        precision: A integer the specifies the floating point precision used in the simulation.
            Positive values are 1 for single precision (float) and 2 for double precision.
    """

    if token is not None and token_file is not None:
        raise ValueError(
            'parameter "token" must not be used when the parameter "token_file" is set')

    if token_file is not None:
        with open(token_file, 'r') as file:
            token = file.read()
    if token is not None:
        environ['QULOOP_TOKEN'] = str(token)

    if dump_type:
        if dump_type not in ["vector", "probability", "shots"]:
            raise ValueError(
                'parameter "dump_type" must be "vector", "probability", or "shots"')
        environ['QULOOP_DUMP_TYPE'] = dump_type

    if shots:
        if shots < 1:
            raise ValueError('parameter "shots" must be greater than one')
        environ['QULOOP_SHOTS'] = str(shots)

    if gpu_count is not None:
        environ['QULOOP_GPU'] = str(int(gpu_count))

    if precision is not None:
        if precision not in [1, 2]:
            raise ValueError('parameter "dump_type" must be int(1) or int(2)')
        environ['QULOOP_FP'] = str(int(precision))

    if simulator is not None:
        simulator = str(simulator).lower()
        if simulator not in ["dense", "sparse", "quest"]:
            raise ValueError(
                'parameter "simulator" must be "dense", "sparse", "quest"')

        if simulator == "dense":
            quantuloop_dense.set_simulator(seed=seed)
        elif simulator == "sparse":
            quantuloop_sparse.set_simulator(seed=seed)
        elif simulator == "quest":
            quantuloop_quest.set_simulator(seed=seed)

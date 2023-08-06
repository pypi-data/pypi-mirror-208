from __future__ import annotations

import os
from typing import List

import netsquid as ns

from qoala.lang.ehi import UnitModule
from qoala.lang.parse import QoalaParser
from qoala.lang.program import QoalaProgram
from qoala.runtime.config import (
    LatenciesConfig,
    ProcNodeConfig,
    ProcNodeNetworkConfig,
    TopologyConfig,
)
from qoala.runtime.environment import NetworkInfo
from qoala.runtime.program import BatchInfo, ProgramInput
from qoala.runtime.schedule import TaskSchedule
from qoala.sim.build import build_network
from qoala.sim.network import ProcNodeNetwork


def create_network_info() -> NetworkInfo:
    env = NetworkInfo.with_nodes({0: "alice"})

    env.set_global_schedule([0])
    env.set_timeslot_len(1e6)

    return env


def get_config() -> ProcNodeConfig:
    topology = TopologyConfig.perfect_config_uniform_default_params(1)
    return ProcNodeConfig(
        node_name="alice",
        node_id=0,
        topology=topology,
        latencies=LatenciesConfig(qnos_instr_time=1000),
    )


def create_network(
    node_cfg: ProcNodeConfig,
) -> ProcNodeNetwork:
    network_info = create_network_info()

    network_cfg = ProcNodeNetworkConfig(nodes=[node_cfg], links=[])
    return build_network(network_cfg, network_info)


def load_program() -> QoalaProgram:
    path = os.path.join(os.path.dirname(__file__), "simple_program.iqoala")
    with open(path) as file:
        text = file.read()
    program = QoalaParser(text).parse()

    return program


def create_batch(
    inputs: List[ProgramInput],
    unit_module: UnitModule,
    num_iterations: int,
    deadline: int,
) -> BatchInfo:
    program = load_program()

    return BatchInfo(
        program=program,
        inputs=inputs,
        unit_module=unit_module,
        num_iterations=num_iterations,
        deadline=deadline,
    )


def run_program():
    ns.sim_reset()

    node_config = get_config()
    network = create_network(node_config)
    procnode = network.nodes["alice"]

    num_iterations = 100
    inputs = [ProgramInput({}) for i in range(num_iterations)]

    unit_module = UnitModule.from_full_ehi(procnode.memmgr.get_ehi())

    batch_info = create_batch(
        inputs=inputs,
        unit_module=unit_module,
        num_iterations=num_iterations,
        deadline=0,
    )

    procnode.submit_batch(batch_info)
    procnode.initialize_processes()
    tasks = procnode.scheduler.get_tasks_to_schedule()
    schedule = TaskSchedule.consecutive(tasks)
    procnode.scheduler.upload_schedule(schedule)

    network.start_all_nodes()
    ns.sim_run()

    all_results = procnode.scheduler.get_batch_results()
    batch0_result = all_results[0]
    results = [result.values["m"] for result in batch0_result.results]
    print(results)


def test_simple_program():
    # LogManager.set_log_level("DEBUG")
    # LogManager.log_to_file("logs/simple_program.log")

    run_program()


if __name__ == "__main__":
    test_simple_program()

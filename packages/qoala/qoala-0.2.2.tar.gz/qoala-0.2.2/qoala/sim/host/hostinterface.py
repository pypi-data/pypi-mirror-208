from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from pydynaa import EventExpression
from qoala.runtime.environment import LocalEnvironment
from qoala.runtime.message import Message
from qoala.sim.componentprot import ComponentProtocol, PortListener
from qoala.sim.events import (
    EVENT_WAIT,
    SIGNAL_HOST_HOST_MSG,
    SIGNAL_NSTK_HOST_MSG,
    SIGNAL_QNOS_HOST_MSG,
)
from qoala.sim.host.hostcomp import HostComponent


@dataclass
class HostLatencies:
    host_instr_time: float = 0  # duration of classical Host instr execution
    host_peer_latency: float = 0  # processing time for messages from remote node

    @classmethod
    def all_zero(cls) -> HostLatencies:
        # NOTE: can also just use HostLatencies() which will default all values to 0
        # However, using this classmethod makes this behavior more explicit and clear.
        return HostLatencies(0, 0)


class HostInterface(ComponentProtocol):
    """NetSquid protocol representing a Host."""

    def __init__(
        self,
        comp: HostComponent,
        local_env: LocalEnvironment,
    ) -> None:
        """Host protocol constructor.

        :param comp: NetSquid component representing the Host
        """
        name = f"{comp.name}_protocol"
        super().__init__(name=name, comp=comp)
        self._comp = comp

        self._local_env = local_env

        self.add_listener(
            "qnos",
            PortListener(self._comp.qnos_in_port, SIGNAL_QNOS_HOST_MSG),
        )
        self.add_listener(
            "netstack",
            PortListener(self._comp.netstack_in_port, SIGNAL_NSTK_HOST_MSG),
        )
        for peer in self._local_env.get_all_other_node_names():
            self.add_listener(
                f"peer_{peer}",
                PortListener(
                    self._comp.peer_in_port(peer), f"{SIGNAL_HOST_HOST_MSG}_{peer}"
                ),
            )

    def send_qnos_msg(self, msg: Message) -> None:
        self._comp.qnos_out_port.tx_output(msg)

    def receive_qnos_msg(self) -> Generator[EventExpression, None, Message]:
        return (yield from self._receive_msg("qnos", SIGNAL_QNOS_HOST_MSG))

    def send_netstack_msg(self, msg: Message) -> None:
        self._comp.netstack_out_port.tx_output(msg)

    def receive_netstack_msg(self) -> Generator[EventExpression, None, Message]:
        return (yield from self._receive_msg("netstack", SIGNAL_NSTK_HOST_MSG))

    def send_peer_msg(self, peer: str, msg: Message) -> None:
        self._comp.peer_out_port(peer).tx_output(msg)

    def receive_peer_msg(self, peer: str) -> Generator[EventExpression, None, Message]:
        return (
            yield from self._receive_msg(
                f"peer_{peer}", f"{SIGNAL_HOST_HOST_MSG}_{peer}"
            )
        )

    def wait(self, delta_time: float) -> Generator[EventExpression, None, None]:
        self._schedule_after(delta_time, EVENT_WAIT)
        event_expr = EventExpression(source=self, event_type=EVENT_WAIT)
        yield event_expr

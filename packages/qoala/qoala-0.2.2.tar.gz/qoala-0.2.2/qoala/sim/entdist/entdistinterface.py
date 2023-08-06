from __future__ import annotations

from typing import Generator, List

from pydynaa import EventExpression
from qoala.runtime.environment import NetworkInfo
from qoala.runtime.message import Message
from qoala.sim.componentprot import ComponentProtocol, PortListener
from qoala.sim.entdist.entdistcomp import EntDistComponent
from qoala.sim.events import SIGNAL_NSTK_ENTD_MSG


class EntDistInterface(ComponentProtocol):
    def __init__(
        self,
        comp: EntDistComponent,
        network_info: NetworkInfo,
    ) -> None:
        super().__init__(name=f"{comp.name}_protocol", comp=comp)
        self._comp = comp
        self._network_info = network_info

        self._all_node_names: List[str] = self._network_info.get_all_node_names()

        for node in self._all_node_names:
            self.add_listener(
                f"node_{node}",
                PortListener(
                    self._comp.node_in_port(node), f"{SIGNAL_NSTK_ENTD_MSG}_{node}"
                ),
            )

    def remote_id_to_peer_name(self, remote_id: int) -> str:
        return self._network_info.get_nodes()[remote_id]

    def send_node_msg(self, node: str, msg: Message) -> None:
        self._comp.node_out_port(node).tx_output(msg)

    def receive_node_msg(self, node: str) -> Generator[EventExpression, None, Message]:
        return (
            yield from self._receive_msg(
                f"node_{node}", f"{SIGNAL_NSTK_ENTD_MSG}_{node}"
            )
        )

    def receive_msg(self) -> Generator[EventExpression, None, Message]:
        return (
            yield from self._receive_msg_any_source(
                [f"node_{node}" for node in self._all_node_names],
                [f"{SIGNAL_NSTK_ENTD_MSG}_{node}" for node in self._all_node_names],
            )
        )

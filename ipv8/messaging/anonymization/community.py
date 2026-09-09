"""
The tunnel community.

Author(s): Egbert Bouman
"""
from __future__ import annotations

from binascii import unhexlify
from typing import TYPE_CHECKING, cast

from ipv8_rust_tunnels import (
    TunnelEngine,
    TunnelSettings as EngineSettings,
    PEER_FLAG_EXIT_BT,
    PEER_FLAG_EXIT_IPV8,
    PEER_FLAG_RELAY,
    PEER_FLAG_SPEED_TEST,
)

from ...community import Community, CommunitySettings
from ...peer import Peer
from ..interfaces.dispatcher.endpoint import DispatcherEndpoint
from .payload import (
    ExtraIntroductionPayload,
    Flags,
)

if TYPE_CHECKING:
    from ...messaging.payload_headers import GlobalTimeDistributionPayload
    from ..interfaces.udp.endpoint import Address
    from ..payload import (
        IntroductionRequestPayload,
        IntroductionResponsePayload,
        NewIntroductionRequestPayload,
        NewIntroductionResponsePayload,
    )
    from ..serialization import Serializer


class TunnelSettings(CommunitySettings):
    """
    Settings to forward to the TunnelCommunity.
    """

    peer_flags: set[int] = {PEER_FLAG_RELAY, PEER_FLAG_SPEED_TEST}


class TunnelCommunity(Community):
    """
    Community to create circuits of intermediate peers (hops) that send data into (exit) and receive from the Internet.
    """

    version = b"\x02"
    community_id = unhexlify("81ded07332bdc775aa5a46f96de9f8f390bbc9f3")
    settings_class = TunnelSettings

    def __init__(self, settings: TunnelSettings) -> None:
        """
        Create a new TunnelCommunity.
        """
        super().__init__(settings)
        # Keeps track of the candidates that want to be a relay/exit node
        self.candidates: dict[Peer, list[int]] = {}
        self.settings = settings

        if isinstance(self.endpoint, DispatcherEndpoint):
            endpoint = cast("Endpoint", self.endpoint.interfaces["UDPIPv4"])
        else:
            endpoint = self.endpoint

        self.engine = TunnelEngine()
        tunnel_settings = EngineSettings()
        tunnel_settings.prefix = self.get_prefix()
        tunnel_settings.peer_flags = settings.peer_flags
        self.engine.start(endpoint, self.my_peer.key.ec, tunnel_settings)
        self.register_task("set_tunnel_peers", self.set_tunnel_peers, delay=1, interval=5.0)

    async def set_tunnel_peers(self) -> None:
        if self.engine:
            self.engine.set_peers(self.candidates)

    def get_serializer(self) -> Serializer:
        """
        Extend our serializer with the ability to (un)pack exit node flags.
        """
        serializer = super().get_serializer()
        serializer.add_packer("flags", Flags())
        return serializer

    def get_candidates(self, *requested_flags: int) -> list[Peer]:
        """
        Get all the peers that we can create circuits with.
        """
        return [peer for peer, flags in self.candidates.items() if set(requested_flags) <= set(flags)]

    def extract_peer_flags(self, extra_bytes: bytes) -> list[int]:
        """
        Convert piggybacked introduction bytes to a list of peer flags.
        """
        if not extra_bytes:
            return []

        payload, _ = self.serializer.unpack_serializable(ExtraIntroductionPayload, extra_bytes)
        return payload.flags

    def introduction_request_callback(self, peer: Peer, dist: GlobalTimeDistributionPayload,
                                      payload: IntroductionRequestPayload | NewIntroductionRequestPayload) -> None:
        """
        Try to extract piggybacked data from the introduction request.
        """
        self.candidates[peer] = self.extract_peer_flags(payload.extra_bytes)

    def introduction_response_callback(self, peer: Peer, dist: GlobalTimeDistributionPayload,
                                       payload: IntroductionResponsePayload | NewIntroductionResponsePayload) -> None:
        """
        Try to extract piggybacked data from the introduction response.
        """
        self.candidates[peer] = self.extract_peer_flags(payload.extra_bytes)
        if self.engine and self.my_estimated_wan not in [("::1", 0), ("0.0.0.0", 0)]:
            self.engine.set_my_estimated_wan(self.my_estimated_wan)

    def create_introduction_request(self, socket_address: Address, extra_bytes: bytes = b"",
                                    new_style: bool = False, prefix: bytes | None = None) -> bytes:
        """
        Add peer flags to our introduction requests.
        """
        extra_payload = ExtraIntroductionPayload(self.settings.peer_flags)
        extra_bytes = self.serializer.pack_serializable(extra_payload)
        return super().create_introduction_request(socket_address, extra_bytes, new_style)

    def create_introduction_response(self, lan_socket_address: Address, socket_address: Address,  # noqa: PLR0913
                                     identifier: int, introduction: Peer | None = None, extra_bytes: bytes = b"",
                                     prefix: bytes | None = None,
                                     new_style: bool = False) -> bytes:
        """
        Add peer flags to our introduction responses.
        """
        extra_payload = ExtraIntroductionPayload(self.settings.peer_flags)
        extra_bytes = self.serializer.pack_serializable(extra_payload)
        return super().create_introduction_response(lan_socket_address, socket_address,
                                                    identifier, introduction, extra_bytes,
                                                    prefix, new_style)

    def send_ping(self, peer: Peer) -> None:
        """
        Send a ping message to a peer.
        """
        self.send_introduction_request(peer)

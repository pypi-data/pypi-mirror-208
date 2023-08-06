"""
This module contains Vertex subclasses for this behavioral package.
"""

from collections import defaultdict
from typing import Optional

from Viper.meta.decorators import staticproperty

from ....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import UniqueVertex, Vertex

__all__ = ["Connection", "Socket", "Host"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class Connection(UniqueVertex):

    """
    A connection vertex. This is a link vertex between two socket. It might only exist for a part of the lifetime of both its connected sockets.
    """

    __slots__ = {
        "duration" : "The duration that the connection was maintained for",
        "volume" : "The amount of data transfered through the connection",
        "src" : "The source address",
        "dest" : "The destination address"
    }

    __pickle_slots__ = {
        "duration",
        "volume",
        "src",
        "dest"
    }

    default_color = ColorSetting(Color(100, 50, 255))
    default_size = SizeSetting(1.5)

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        from typing import Any
        super().__init__(parent=parent)
        self.duration : float = 0.
        self.volume : int = 0
        self.src : Any = None
        self.dest : Any = None

    @property
    def socket(self) -> "Socket":
        """
        The local Socket that this connection was made through.
        """
        from .relations import HasConnection
        for e in self.edges:
            if isinstance(e, HasConnection):
                return e.source
        raise RuntimeError("Got a Connection bound to no Socket.")





class Socket(UniqueVertex):

    """
    A socket vertex. Represents a handle given by the system to allow some kind of communication.
    """

    __slots__ = {
        "family" : "The socket address family. For example, 'InterNetwork' is for IP V4 addresses. Refer to Socket.families for documentation",
        "protocol" : "The transport protocol used by the socket. For example, Tcp. Refer to Socket.protocols for documentation",
        "type" : "The type of socket. For exemple, Dgram is a socket that supports datagrams. Refer to Socket.types for documentation"
    }

    __pickle_slots__ = {
        "family",
        "protocol",
        "type"
    }

    default_color = ColorSetting(Color(178, 153, 153))
    default_size = SizeSetting(2.5)

    families = defaultdict(lambda : ("Uncharted", "The value does not correspond to any known address family"), {
        16 : ('AppleTalk', 'AppleTalk address.'),
        22 : ('Atm', 'Native ATM services address.'),
        21 : ('Banyan', 'Banyan address.'),
        10 : ('Ccitt', 'Addresses for CCITT protocols, such as X.25.'),
        5 : ('Chaos', 'Address for MIT CHAOS protocols.'),
        24 : ('Cluster', 'Address for Microsoft cluster products.'),
        65537 : ('ControllerAreaNetwork', 'Controller Area Network address.'),
        9 : ('DataKit', 'Address for Datakit protocols.'),
        13 : ('DataLink', 'Direct data-link interface address.'),
        12 : ('DecNet', 'DECnet address.'),
        8 : ('Ecma', 'European Computer Manufacturers Association (ECMA) address.'),
        19 : ('FireFox', 'FireFox address.'),
        15 : ('HyperChannel', 'NSC Hyperchannel address.'),
        1284425 : ('Ieee', 'IEEE 1284.4 workgroup address.'),
        3 : ('ImpLink', 'ARPANET IMP address.'),
        2 : ('InterNetwork', 'Address for IP version 4.'),
        623 : ('InterNetworkV', 'Address for IP version 6.'),
        6 : ('Ipx', 'IPX or SPX address.'),
        26 : ('Irda', 'IrDA address.'),
        7 : ('Iso', 'Address for ISO protocols.'),
        14 : ('Lat', 'LAT address.'),
        29 : ('Max', 'MAX address.'),
        17 : ('NetBios', 'NetBios address.'),
        28 : ('NetworkDesigners', 'Address for Network Designers OSI gateway-enabled protocols.'),
        6 : ('NS', 'Address for Xerox NS protocols.'),
        7 : ('Osi', 'Address for OSI protocols.'),
        65536 : ('Packet', 'Low-level Packet address.'),
        4 : ('Pup', 'Address for PUP protocols.'),
        11 : ('Sna', 'IBM SNA address.'),
        1 : ('Unix', 'Unix local to host address.'),
        -1 : ('Unknown', 'Unknown address family.'),
        0 : ('Unspecified', 'Unspecified address family.'),
        18 : ('VoiceView', 'VoiceView address.'),
    })

    protocols = defaultdict(lambda : ("Uncharted", "The value does not correspond to any known protocol"), {
        3 : ('Ggp', 'Gateway To Gateway Protocol.'),
        1 : ('Icmp', 'Internet Control Message Protocol.'),
        58 : ('IcmpV6', 'Internet Control Message Protocol for IPv6.'),
        22 : ('Idp', 'Internet Datagram Protocol.'),
        2 : ('Igmp', 'Internet Group Management Protocol.'),
        0 : ('IP', 'Internet Protocol.'),
        51 : ('IPSecAuthenticationHeader', 'IPv6 Authentication header. For details'),
        50 : ('IPSecEncapsulatingSecurityPayload', 'IPv6 Encapsulating Security Payload header.'),
        4 : ('IPv4', 'Internet Protocol version 4.'),
        41 : ('IPv6', 'Internet Protocol version 6 (IPv6).'),
        60 : ('IPv6DestinationOptions', 'IPv6 Destination Options header.'),
        44 : ('IPv6FragmentHeader', 'IPv6 Fragment header.'),
        0 : ('IPv6HopByHopOptions', 'IPv6 Hop by Hop Options header.'),
        59 : ('IPv6NoNextHeader', 'IPv6 No next header.'),
        43 : ('IPv6RoutingHeader', 'IPv6 Routing header.'),
        1000 : ('Ipx', 'Internet Packet Exchange Protocol.'),
        77 : ('ND', 'Net Disk Protocol (unofficial).'),
        12 : ('Pup', 'PARC Universal Packet Protocol.'),
        255 : ('Raw', 'Raw IP packet protocol.'),
        1256 : ('Spx', 'Sequenced Packet Exchange protocol.'),
        1257 : ('SpxII', 'Sequenced Packet Exchange version 2 protocol.'),
        6 : ('Tcp', 'Transmission Control Protocol.'),
        17 : ('Udp', 'User Datagram Protocol.'),
        -1 : ('Unknown', 'Unknown protocol.'),
        0 : ('Unspecified', 'Unspecified protocol.'),
    })

    types = defaultdict(lambda : ("Uncharted", "The value does not correspond to any known socket type"), {
        2 : ('Dgram', 'Supports datagrams, which are connectionless, unreliable messages of a fixed (typically small) maximum length. Messages might be lost or duplicated and might arrive out of order. A Socket of type Dgram requires no connection prior to sending and receiving data, and can communicate with multiple peers. Dgram uses the Datagram Protocol (ProtocolType.Udp) and the AddressFamily. InterNetwork address family.'),
        3 : ('Raw', 'Supports access to the underlying transport protocol. Using Raw, you can communicate using protocols like Internet Control Message Protocol (ProtocolType.Icmp) and Internet Group Management Protocol (ProtocolType.Igmp). Your application must provide a complete IP header when sending. Received datagrams return with the IP header and options intact.'),
        4 : ('Rdm', 'Supports connectionless, message-oriented, reliably delivered messages, and preserves message boundaries in data. Rdm (Reliably Delivered Messages) messages arrive unduplicated and in order. Furthermore, the sender is notified if messages are lost. If you initialize a Socket using Rdm, you do not require a remote host connection before sending and receiving data. With Rdm, you can communicate with multiple peers.'),
        5 : ('Seqpacket', 'Provides connection-oriented and reliable two-way transfer of ordered byte streams across a network. Seqpacket does not duplicate data, and it preserves boundaries within the data stream. A Socket of type Seqpacket communicates with a single peer and requires a remote host connection before communication can begin.'),
        1 : ('Stream', 'Supports reliable, two-way, connection-based byte streams without the duplication of data and without preservation of boundaries. A Socket of this type communicates with a single peer and requires a remote host connection before communication can begin. Stream uses the Transmission Control Protocol (ProtocolType.Tcp) and the AddressFamily.InterNetwork address family.'),
        -1 : ('Unknown', 'Specifies an unknown Socket type.'),
    })

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        super().__init__(parent=parent)
        self.family : str = ""
        self.protocol : str = ""
        self.type : str = ""





class Host(UniqueVertex):

    """
    A machine vertex. It represents a physical machine.
    """

    __current : Optional["Host"] = None

    @staticproperty
    def current() -> "Host":
        """
        The currently active Host node. This is used to indicate which Host node is the machine running the sample.
        """
        if Host.__current is None:
            raise AttributeError("Host class has no attribute 'current'.")
        return Host.__current

    @current.setter
    def current(value : "Host"):
        if not isinstance(value, Host):
            raise TypeError("Cannot set attribute 'current' of class 'Host' to object of type '{}'".format(type(value).__name__))
        Host.__current = value

    __slots__ = {
        "address" : "The IP address of the machine",
        "domain" : "The URL the machine is known as if any",
        "name" : "The machine's name",
        "platform" : "The operating system the host is running on"
    }

    __pickle_slots__ = {
        "address",
        "domain",
        "name",
        "platform"
    }

    default_color = ColorSetting(Color.white)
    default_size = SizeSetting(10.0)

    def __init__(self, *, parent: Vertex | None = None) -> None:
        super().__init__(parent=parent)
        self.address : str = ""
        self.domain : str = ""
        self.name : str = ""
        self.platform : str = "Unknown"
    
    @property
    def label(self) -> str:
        """
        Returns a label for this Host node.
        """
        if self.name:
            return "Host " + repr(self.name)
        return "Host at " + self.address





del Color, ColorSetting, SizeSetting, Optional, UniqueVertex, Vertex, defaultdict, logger, staticproperty
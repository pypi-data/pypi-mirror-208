from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Address(_message.Message):
    __slots__ = ["other_address", "tcpip_address", "uds_address"]
    class OtherAddress(_message.Message):
        __slots__ = ["name", "value"]
        NAME_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        value: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class TcpIpAddress(_message.Message):
        __slots__ = ["ip_address", "port"]
        IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        PORT_FIELD_NUMBER: _ClassVar[int]
        ip_address: bytes
        port: int
        def __init__(self, ip_address: _Optional[bytes] = ..., port: _Optional[int] = ...) -> None: ...
    class UdsAddress(_message.Message):
        __slots__ = ["filename"]
        FILENAME_FIELD_NUMBER: _ClassVar[int]
        filename: str
        def __init__(self, filename: _Optional[str] = ...) -> None: ...
    OTHER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TCPIP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UDS_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    other_address: Address.OtherAddress
    tcpip_address: Address.TcpIpAddress
    uds_address: Address.UdsAddress
    def __init__(self, tcpip_address: _Optional[_Union[Address.TcpIpAddress, _Mapping]] = ..., uds_address: _Optional[_Union[Address.UdsAddress, _Mapping]] = ..., other_address: _Optional[_Union[Address.OtherAddress, _Mapping]] = ...) -> None: ...

class Channel(_message.Message):
    __slots__ = ["channel_ref", "data", "ref", "socket_ref", "subchannel_ref"]
    CHANNEL_REF_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    SOCKET_REF_FIELD_NUMBER: _ClassVar[int]
    SUBCHANNEL_REF_FIELD_NUMBER: _ClassVar[int]
    channel_ref: _containers.RepeatedCompositeFieldContainer[ChannelRef]
    data: ChannelData
    ref: ChannelRef
    socket_ref: _containers.RepeatedCompositeFieldContainer[SocketRef]
    subchannel_ref: _containers.RepeatedCompositeFieldContainer[SubchannelRef]
    def __init__(self, ref: _Optional[_Union[ChannelRef, _Mapping]] = ..., data: _Optional[_Union[ChannelData, _Mapping]] = ..., channel_ref: _Optional[_Iterable[_Union[ChannelRef, _Mapping]]] = ..., subchannel_ref: _Optional[_Iterable[_Union[SubchannelRef, _Mapping]]] = ..., socket_ref: _Optional[_Iterable[_Union[SocketRef, _Mapping]]] = ...) -> None: ...

class ChannelConnectivityState(_message.Message):
    __slots__ = ["state"]
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CONNECTING: ChannelConnectivityState.State
    IDLE: ChannelConnectivityState.State
    READY: ChannelConnectivityState.State
    SHUTDOWN: ChannelConnectivityState.State
    STATE_FIELD_NUMBER: _ClassVar[int]
    TRANSIENT_FAILURE: ChannelConnectivityState.State
    UNKNOWN: ChannelConnectivityState.State
    state: ChannelConnectivityState.State
    def __init__(self, state: _Optional[_Union[ChannelConnectivityState.State, str]] = ...) -> None: ...

class ChannelData(_message.Message):
    __slots__ = ["calls_failed", "calls_started", "calls_succeeded", "last_call_started_timestamp", "state", "target", "trace"]
    CALLS_FAILED_FIELD_NUMBER: _ClassVar[int]
    CALLS_STARTED_FIELD_NUMBER: _ClassVar[int]
    CALLS_SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    LAST_CALL_STARTED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    calls_failed: int
    calls_started: int
    calls_succeeded: int
    last_call_started_timestamp: _timestamp_pb2.Timestamp
    state: ChannelConnectivityState
    target: str
    trace: ChannelTrace
    def __init__(self, state: _Optional[_Union[ChannelConnectivityState, _Mapping]] = ..., target: _Optional[str] = ..., trace: _Optional[_Union[ChannelTrace, _Mapping]] = ..., calls_started: _Optional[int] = ..., calls_succeeded: _Optional[int] = ..., calls_failed: _Optional[int] = ..., last_call_started_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChannelRef(_message.Message):
    __slots__ = ["channel_id", "name"]
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    name: str
    def __init__(self, channel_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class ChannelTrace(_message.Message):
    __slots__ = ["creation_timestamp", "events", "num_events_logged"]
    CREATION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    NUM_EVENTS_LOGGED_FIELD_NUMBER: _ClassVar[int]
    creation_timestamp: _timestamp_pb2.Timestamp
    events: _containers.RepeatedCompositeFieldContainer[ChannelTraceEvent]
    num_events_logged: int
    def __init__(self, num_events_logged: _Optional[int] = ..., creation_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., events: _Optional[_Iterable[_Union[ChannelTraceEvent, _Mapping]]] = ...) -> None: ...

class ChannelTraceEvent(_message.Message):
    __slots__ = ["channel_ref", "description", "severity", "subchannel_ref", "timestamp"]
    class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CHANNEL_REF_FIELD_NUMBER: _ClassVar[int]
    CT_ERROR: ChannelTraceEvent.Severity
    CT_INFO: ChannelTraceEvent.Severity
    CT_UNKNOWN: ChannelTraceEvent.Severity
    CT_WARNING: ChannelTraceEvent.Severity
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    SUBCHANNEL_REF_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    channel_ref: ChannelRef
    description: str
    severity: ChannelTraceEvent.Severity
    subchannel_ref: SubchannelRef
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, description: _Optional[str] = ..., severity: _Optional[_Union[ChannelTraceEvent.Severity, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., channel_ref: _Optional[_Union[ChannelRef, _Mapping]] = ..., subchannel_ref: _Optional[_Union[SubchannelRef, _Mapping]] = ...) -> None: ...

class GetChannelRequest(_message.Message):
    __slots__ = ["channel_id"]
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    def __init__(self, channel_id: _Optional[int] = ...) -> None: ...

class GetChannelResponse(_message.Message):
    __slots__ = ["channel"]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    channel: Channel
    def __init__(self, channel: _Optional[_Union[Channel, _Mapping]] = ...) -> None: ...

class GetServerRequest(_message.Message):
    __slots__ = ["server_id"]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class GetServerResponse(_message.Message):
    __slots__ = ["server"]
    SERVER_FIELD_NUMBER: _ClassVar[int]
    server: Server
    def __init__(self, server: _Optional[_Union[Server, _Mapping]] = ...) -> None: ...

class GetServerSocketsRequest(_message.Message):
    __slots__ = ["max_results", "server_id", "start_socket_id"]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    START_SOCKET_ID_FIELD_NUMBER: _ClassVar[int]
    max_results: int
    server_id: int
    start_socket_id: int
    def __init__(self, server_id: _Optional[int] = ..., start_socket_id: _Optional[int] = ..., max_results: _Optional[int] = ...) -> None: ...

class GetServerSocketsResponse(_message.Message):
    __slots__ = ["end", "socket_ref"]
    END_FIELD_NUMBER: _ClassVar[int]
    SOCKET_REF_FIELD_NUMBER: _ClassVar[int]
    end: bool
    socket_ref: _containers.RepeatedCompositeFieldContainer[SocketRef]
    def __init__(self, socket_ref: _Optional[_Iterable[_Union[SocketRef, _Mapping]]] = ..., end: bool = ...) -> None: ...

class GetServersRequest(_message.Message):
    __slots__ = ["max_results", "start_server_id"]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    START_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    max_results: int
    start_server_id: int
    def __init__(self, start_server_id: _Optional[int] = ..., max_results: _Optional[int] = ...) -> None: ...

class GetServersResponse(_message.Message):
    __slots__ = ["end", "server"]
    END_FIELD_NUMBER: _ClassVar[int]
    SERVER_FIELD_NUMBER: _ClassVar[int]
    end: bool
    server: _containers.RepeatedCompositeFieldContainer[Server]
    def __init__(self, server: _Optional[_Iterable[_Union[Server, _Mapping]]] = ..., end: bool = ...) -> None: ...

class GetSocketRequest(_message.Message):
    __slots__ = ["socket_id", "summary"]
    SOCKET_ID_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    socket_id: int
    summary: bool
    def __init__(self, socket_id: _Optional[int] = ..., summary: bool = ...) -> None: ...

class GetSocketResponse(_message.Message):
    __slots__ = ["socket"]
    SOCKET_FIELD_NUMBER: _ClassVar[int]
    socket: Socket
    def __init__(self, socket: _Optional[_Union[Socket, _Mapping]] = ...) -> None: ...

class GetSubchannelRequest(_message.Message):
    __slots__ = ["subchannel_id"]
    SUBCHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    subchannel_id: int
    def __init__(self, subchannel_id: _Optional[int] = ...) -> None: ...

class GetSubchannelResponse(_message.Message):
    __slots__ = ["subchannel"]
    SUBCHANNEL_FIELD_NUMBER: _ClassVar[int]
    subchannel: Subchannel
    def __init__(self, subchannel: _Optional[_Union[Subchannel, _Mapping]] = ...) -> None: ...

class GetTopChannelsRequest(_message.Message):
    __slots__ = ["max_results", "start_channel_id"]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    START_CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    max_results: int
    start_channel_id: int
    def __init__(self, start_channel_id: _Optional[int] = ..., max_results: _Optional[int] = ...) -> None: ...

class GetTopChannelsResponse(_message.Message):
    __slots__ = ["channel", "end"]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    channel: _containers.RepeatedCompositeFieldContainer[Channel]
    end: bool
    def __init__(self, channel: _Optional[_Iterable[_Union[Channel, _Mapping]]] = ..., end: bool = ...) -> None: ...

class Security(_message.Message):
    __slots__ = ["other", "tls"]
    class OtherSecurity(_message.Message):
        __slots__ = ["name", "value"]
        NAME_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        value: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class Tls(_message.Message):
        __slots__ = ["local_certificate", "other_name", "remote_certificate", "standard_name"]
        LOCAL_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
        OTHER_NAME_FIELD_NUMBER: _ClassVar[int]
        REMOTE_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
        STANDARD_NAME_FIELD_NUMBER: _ClassVar[int]
        local_certificate: bytes
        other_name: str
        remote_certificate: bytes
        standard_name: str
        def __init__(self, standard_name: _Optional[str] = ..., other_name: _Optional[str] = ..., local_certificate: _Optional[bytes] = ..., remote_certificate: _Optional[bytes] = ...) -> None: ...
    OTHER_FIELD_NUMBER: _ClassVar[int]
    TLS_FIELD_NUMBER: _ClassVar[int]
    other: Security.OtherSecurity
    tls: Security.Tls
    def __init__(self, tls: _Optional[_Union[Security.Tls, _Mapping]] = ..., other: _Optional[_Union[Security.OtherSecurity, _Mapping]] = ...) -> None: ...

class Server(_message.Message):
    __slots__ = ["data", "listen_socket", "ref"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LISTEN_SOCKET_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    data: ServerData
    listen_socket: _containers.RepeatedCompositeFieldContainer[SocketRef]
    ref: ServerRef
    def __init__(self, ref: _Optional[_Union[ServerRef, _Mapping]] = ..., data: _Optional[_Union[ServerData, _Mapping]] = ..., listen_socket: _Optional[_Iterable[_Union[SocketRef, _Mapping]]] = ...) -> None: ...

class ServerData(_message.Message):
    __slots__ = ["calls_failed", "calls_started", "calls_succeeded", "last_call_started_timestamp", "trace"]
    CALLS_FAILED_FIELD_NUMBER: _ClassVar[int]
    CALLS_STARTED_FIELD_NUMBER: _ClassVar[int]
    CALLS_SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    LAST_CALL_STARTED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    calls_failed: int
    calls_started: int
    calls_succeeded: int
    last_call_started_timestamp: _timestamp_pb2.Timestamp
    trace: ChannelTrace
    def __init__(self, trace: _Optional[_Union[ChannelTrace, _Mapping]] = ..., calls_started: _Optional[int] = ..., calls_succeeded: _Optional[int] = ..., calls_failed: _Optional[int] = ..., last_call_started_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ServerRef(_message.Message):
    __slots__ = ["name", "server_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    server_id: int
    def __init__(self, server_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class Socket(_message.Message):
    __slots__ = ["data", "local", "ref", "remote", "remote_name", "security"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    REMOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    SECURITY_FIELD_NUMBER: _ClassVar[int]
    data: SocketData
    local: Address
    ref: SocketRef
    remote: Address
    remote_name: str
    security: Security
    def __init__(self, ref: _Optional[_Union[SocketRef, _Mapping]] = ..., data: _Optional[_Union[SocketData, _Mapping]] = ..., local: _Optional[_Union[Address, _Mapping]] = ..., remote: _Optional[_Union[Address, _Mapping]] = ..., security: _Optional[_Union[Security, _Mapping]] = ..., remote_name: _Optional[str] = ...) -> None: ...

class SocketData(_message.Message):
    __slots__ = ["keep_alives_sent", "last_local_stream_created_timestamp", "last_message_received_timestamp", "last_message_sent_timestamp", "last_remote_stream_created_timestamp", "local_flow_control_window", "messages_received", "messages_sent", "option", "remote_flow_control_window", "streams_failed", "streams_started", "streams_succeeded"]
    KEEP_ALIVES_SENT_FIELD_NUMBER: _ClassVar[int]
    LAST_LOCAL_STREAM_CREATED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_RECEIVED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_SENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LAST_REMOTE_STREAM_CREATED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FLOW_CONTROL_WINDOW_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_SENT_FIELD_NUMBER: _ClassVar[int]
    OPTION_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FLOW_CONTROL_WINDOW_FIELD_NUMBER: _ClassVar[int]
    STREAMS_FAILED_FIELD_NUMBER: _ClassVar[int]
    STREAMS_STARTED_FIELD_NUMBER: _ClassVar[int]
    STREAMS_SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    keep_alives_sent: int
    last_local_stream_created_timestamp: _timestamp_pb2.Timestamp
    last_message_received_timestamp: _timestamp_pb2.Timestamp
    last_message_sent_timestamp: _timestamp_pb2.Timestamp
    last_remote_stream_created_timestamp: _timestamp_pb2.Timestamp
    local_flow_control_window: _wrappers_pb2.Int64Value
    messages_received: int
    messages_sent: int
    option: _containers.RepeatedCompositeFieldContainer[SocketOption]
    remote_flow_control_window: _wrappers_pb2.Int64Value
    streams_failed: int
    streams_started: int
    streams_succeeded: int
    def __init__(self, streams_started: _Optional[int] = ..., streams_succeeded: _Optional[int] = ..., streams_failed: _Optional[int] = ..., messages_sent: _Optional[int] = ..., messages_received: _Optional[int] = ..., keep_alives_sent: _Optional[int] = ..., last_local_stream_created_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_remote_stream_created_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_message_sent_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_message_received_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., local_flow_control_window: _Optional[_Union[_wrappers_pb2.Int64Value, _Mapping]] = ..., remote_flow_control_window: _Optional[_Union[_wrappers_pb2.Int64Value, _Mapping]] = ..., option: _Optional[_Iterable[_Union[SocketOption, _Mapping]]] = ...) -> None: ...

class SocketOption(_message.Message):
    __slots__ = ["additional", "name", "value"]
    ADDITIONAL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    additional: _any_pb2.Any
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., additional: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class SocketOptionLinger(_message.Message):
    __slots__ = ["active", "duration"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    active: bool
    duration: _duration_pb2.Duration
    def __init__(self, active: bool = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SocketOptionTcpInfo(_message.Message):
    __slots__ = ["tcpi_advmss", "tcpi_ato", "tcpi_backoff", "tcpi_ca_state", "tcpi_fackets", "tcpi_last_ack_recv", "tcpi_last_ack_sent", "tcpi_last_data_recv", "tcpi_last_data_sent", "tcpi_lost", "tcpi_options", "tcpi_pmtu", "tcpi_probes", "tcpi_rcv_mss", "tcpi_rcv_ssthresh", "tcpi_rcv_wscale", "tcpi_reordering", "tcpi_retrans", "tcpi_retransmits", "tcpi_rto", "tcpi_rtt", "tcpi_rttvar", "tcpi_sacked", "tcpi_snd_cwnd", "tcpi_snd_mss", "tcpi_snd_ssthresh", "tcpi_snd_wscale", "tcpi_state", "tcpi_unacked"]
    TCPI_ADVMSS_FIELD_NUMBER: _ClassVar[int]
    TCPI_ATO_FIELD_NUMBER: _ClassVar[int]
    TCPI_BACKOFF_FIELD_NUMBER: _ClassVar[int]
    TCPI_CA_STATE_FIELD_NUMBER: _ClassVar[int]
    TCPI_FACKETS_FIELD_NUMBER: _ClassVar[int]
    TCPI_LAST_ACK_RECV_FIELD_NUMBER: _ClassVar[int]
    TCPI_LAST_ACK_SENT_FIELD_NUMBER: _ClassVar[int]
    TCPI_LAST_DATA_RECV_FIELD_NUMBER: _ClassVar[int]
    TCPI_LAST_DATA_SENT_FIELD_NUMBER: _ClassVar[int]
    TCPI_LOST_FIELD_NUMBER: _ClassVar[int]
    TCPI_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TCPI_PMTU_FIELD_NUMBER: _ClassVar[int]
    TCPI_PROBES_FIELD_NUMBER: _ClassVar[int]
    TCPI_RCV_MSS_FIELD_NUMBER: _ClassVar[int]
    TCPI_RCV_SSTHRESH_FIELD_NUMBER: _ClassVar[int]
    TCPI_RCV_WSCALE_FIELD_NUMBER: _ClassVar[int]
    TCPI_REORDERING_FIELD_NUMBER: _ClassVar[int]
    TCPI_RETRANSMITS_FIELD_NUMBER: _ClassVar[int]
    TCPI_RETRANS_FIELD_NUMBER: _ClassVar[int]
    TCPI_RTO_FIELD_NUMBER: _ClassVar[int]
    TCPI_RTTVAR_FIELD_NUMBER: _ClassVar[int]
    TCPI_RTT_FIELD_NUMBER: _ClassVar[int]
    TCPI_SACKED_FIELD_NUMBER: _ClassVar[int]
    TCPI_SND_CWND_FIELD_NUMBER: _ClassVar[int]
    TCPI_SND_MSS_FIELD_NUMBER: _ClassVar[int]
    TCPI_SND_SSTHRESH_FIELD_NUMBER: _ClassVar[int]
    TCPI_SND_WSCALE_FIELD_NUMBER: _ClassVar[int]
    TCPI_STATE_FIELD_NUMBER: _ClassVar[int]
    TCPI_UNACKED_FIELD_NUMBER: _ClassVar[int]
    tcpi_advmss: int
    tcpi_ato: int
    tcpi_backoff: int
    tcpi_ca_state: int
    tcpi_fackets: int
    tcpi_last_ack_recv: int
    tcpi_last_ack_sent: int
    tcpi_last_data_recv: int
    tcpi_last_data_sent: int
    tcpi_lost: int
    tcpi_options: int
    tcpi_pmtu: int
    tcpi_probes: int
    tcpi_rcv_mss: int
    tcpi_rcv_ssthresh: int
    tcpi_rcv_wscale: int
    tcpi_reordering: int
    tcpi_retrans: int
    tcpi_retransmits: int
    tcpi_rto: int
    tcpi_rtt: int
    tcpi_rttvar: int
    tcpi_sacked: int
    tcpi_snd_cwnd: int
    tcpi_snd_mss: int
    tcpi_snd_ssthresh: int
    tcpi_snd_wscale: int
    tcpi_state: int
    tcpi_unacked: int
    def __init__(self, tcpi_state: _Optional[int] = ..., tcpi_ca_state: _Optional[int] = ..., tcpi_retransmits: _Optional[int] = ..., tcpi_probes: _Optional[int] = ..., tcpi_backoff: _Optional[int] = ..., tcpi_options: _Optional[int] = ..., tcpi_snd_wscale: _Optional[int] = ..., tcpi_rcv_wscale: _Optional[int] = ..., tcpi_rto: _Optional[int] = ..., tcpi_ato: _Optional[int] = ..., tcpi_snd_mss: _Optional[int] = ..., tcpi_rcv_mss: _Optional[int] = ..., tcpi_unacked: _Optional[int] = ..., tcpi_sacked: _Optional[int] = ..., tcpi_lost: _Optional[int] = ..., tcpi_retrans: _Optional[int] = ..., tcpi_fackets: _Optional[int] = ..., tcpi_last_data_sent: _Optional[int] = ..., tcpi_last_ack_sent: _Optional[int] = ..., tcpi_last_data_recv: _Optional[int] = ..., tcpi_last_ack_recv: _Optional[int] = ..., tcpi_pmtu: _Optional[int] = ..., tcpi_rcv_ssthresh: _Optional[int] = ..., tcpi_rtt: _Optional[int] = ..., tcpi_rttvar: _Optional[int] = ..., tcpi_snd_ssthresh: _Optional[int] = ..., tcpi_snd_cwnd: _Optional[int] = ..., tcpi_advmss: _Optional[int] = ..., tcpi_reordering: _Optional[int] = ...) -> None: ...

class SocketOptionTimeout(_message.Message):
    __slots__ = ["duration"]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    duration: _duration_pb2.Duration
    def __init__(self, duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SocketRef(_message.Message):
    __slots__ = ["name", "socket_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SOCKET_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    socket_id: int
    def __init__(self, socket_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class Subchannel(_message.Message):
    __slots__ = ["channel_ref", "data", "ref", "socket_ref", "subchannel_ref"]
    CHANNEL_REF_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    SOCKET_REF_FIELD_NUMBER: _ClassVar[int]
    SUBCHANNEL_REF_FIELD_NUMBER: _ClassVar[int]
    channel_ref: _containers.RepeatedCompositeFieldContainer[ChannelRef]
    data: ChannelData
    ref: SubchannelRef
    socket_ref: _containers.RepeatedCompositeFieldContainer[SocketRef]
    subchannel_ref: _containers.RepeatedCompositeFieldContainer[SubchannelRef]
    def __init__(self, ref: _Optional[_Union[SubchannelRef, _Mapping]] = ..., data: _Optional[_Union[ChannelData, _Mapping]] = ..., channel_ref: _Optional[_Iterable[_Union[ChannelRef, _Mapping]]] = ..., subchannel_ref: _Optional[_Iterable[_Union[SubchannelRef, _Mapping]]] = ..., socket_ref: _Optional[_Iterable[_Union[SocketRef, _Mapping]]] = ...) -> None: ...

class SubchannelRef(_message.Message):
    __slots__ = ["name", "subchannel_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SUBCHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    subchannel_id: int
    def __init__(self, subchannel_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

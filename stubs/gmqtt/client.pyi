"""Stubs for gmqtt.client."""
from typing import Any, List, Tuple, Dict, Union, Optional, Sequence

class Message:
    def __init__(
        self,
        topic: Union[str, bytes],
        payload: Optional[Union[List[Any], Tuple[Any, ...], Dict[Any, Any], int, float, str, bytes]],
        qos: int = 0,
        retain: bool = False,
        **kwargs: Any,
    ): ...

class Subscription:
    def __init__(
        self,
        topic: Union[str, bytes],
        qos: int = 0,
        no_local: bool = False,
        retain_as_published: bool = False,
        retain_handling_options: int = 0,
        subscription_identifier: Optional[str] = None,
    ): ...

class Client:
    def __init__(
        self,
        client_id: str,
        clean_session: bool = True,
        optimistic_acknowledgement: bool = True,
        will_message: Optional[Message] = None, 
        **kwargs: Any,
    ): ...

    @property
    def is_connected(self) -> bool: ...

    def set_auth_credentials(self, username: str, password: Optional[str] = None) -> None: ...

    async def connect(
        self,
        host: str,
        port: int = 1883,
        ssl: bool = False,
        keepalive: int = 60,
        version: int = 5,
        raise_exc: bool = True,
    ) -> None: ...

    async def disconnect(self, reason_code: int = 0) -> None: ...

    def subscribe(
        self,
        subscription_or_topic: Union[str, Subscription, Sequence[Subscription]],
        qosint: int = 0,
        no_local: bool = False,
        retain_as_published: bool = False,
        retain_handling_optionsint: int = 0,
    )-> int: ...

    def publish(
        self,
        message_or_topic: Union[Message, str, bytes],
        payloadOptional: Optional[Union[List[Any], Tuple[Any, ...], Dict[Any, Any], int, float, str, bytes]] = None,
        qos: int = 0,
        retain: bool = False,
    ) -> None: ...

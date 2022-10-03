"""
Astoria HTTP Bridge.

Enables external access to the Astoria state and event bus.
"""
import asyncio
import json
import logging
from typing import Any, Dict, Match, Optional
from uuid import uuid4

import click
import uvicorn  # type: ignore
from pydantic import parse_obj_as
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from astoria.common.config.system import AstoriaConfig
from astoria.common.ipc import REQUEST_TYPE_MAP, RequestResponse
from astoria.common.mqtt.wrapper import MQTTWrapper

LOGGER = logging.getLogger(__name__)


MANAGER_STATE_NAME_MAP = {
    "astdiskd": "disks",
    "astmetad": "metadata",
    "astprocd": "process",
    "astwifid": "wifi",
}

STATE_NAME_MANAGER_MAP = {
    v: k for k, v in MANAGER_STATE_NAME_MAP.items()
}


class MQTTBus:
    """MQTT Bus Integration for use with Starlette."""

    def __init__(self) -> None:
        self.config = AstoriaConfig.load()
        self._mqtt = MQTTWrapper(
            "asthttpd",
            self.config.mqtt,
        )
        self._lock = asyncio.Lock()
        self._state: Dict[str, Dict[str, Any]] = {}  # TODO: Rename this

        self._mqtt.subscribe("+", self._handle_state_event)

    async def _handle_state_event(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle an event from a state manager."""
        manager_name = match.group(1)
        state_name = MANAGER_STATE_NAME_MAP.get(manager_name, manager_name)
        try:
            data = json.loads(payload)
            async with self._lock:
                if data.get("status", "STOPPED") == "RUNNING":
                    self._state[state_name] = {
                        k: v
                        for k, v in data.items()
                        if k not in {"status", "astoria_version"}
                    }
                elif state_name in self._state:
                    del self._state[state_name]
        except json.JSONDecodeError as e:
            LOGGER.warning(f"Bad JSON from State Manager: {e}")

    async def get_state(self) -> Dict[str, Dict[str, str]]:
        """Get the state."""
        async with self._lock:
            return self._state

    async def connect(self) -> None:
        """Connect to the MQTT broker."""
        await self._mqtt.connect()

    async def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        await self._mqtt.disconnect()

    @classmethod
    async def on_startup(cls) -> None:
        """Startup hook for Starlette."""
        app.state.bus = cls()
        await app.state.bus.connect()

    @classmethod
    async def on_shutdown(cls) -> None:
        """Shutdown hook for Starlette."""
        await app.state.bus.disconnect()

    async def manager_request(
        self,
        manager_name: str,
        request_name: str,
        data: Any,
    ) -> RequestResponse:
        """Make a request to a state manager."""
        model = REQUEST_TYPE_MAP[manager_name][request_name]  # TODO: Handle this

        self._mqtt.subscribe(
            f"{manager_name}/request/+/+",  # TODO: Why does it only work with this?
            self._mqtt._request_response_message_handler,
        )
        return await self._mqtt.manager_request(  # TODO: Handle exceptions from here
            manager_name,
            request_name,
            parse_obj_as(model, data),
        )


async def list_states(request: Request) -> JSONResponse:
    """List all state groups."""
    all_states = await request.app.state.bus.get_state()
    return JSONResponse(all_states)


async def get_state(request: Request) -> JSONResponse:
    """Get a state group."""
    all_states = await request.app.state.bus.get_state()
    state_name = request.path_params.get("state_name")
    state = all_states.get(state_name)
    if state:
        return JSONResponse(state)
    else:
        return JSONResponse(
            {"status": f"Unable to find state name: {state_name}"},
            status_code=400,
        )


async def make_request(request: Request) -> JSONResponse:
    """Proxy a state manager request."""
    state_name = str(request.path_params.get("state_name"))

    all_states = await request.app.state.bus.get_state()
    if state_name not in all_states:
        return JSONResponse(
            {"status": f"Unknown state name {state_name}. Is the component running?"},
        )

    manager_name = STATE_NAME_MANAGER_MAP.get(state_name, state_name)
    request_name = request.path_params.get("request_name")
    try:
        data = await request.json()
    except json.JSONDecodeError:
        body = await request.body()
        if not body:
            data = {}
        else:
            return JSONResponse({"status": "Invalid JSON"})
    data["uuid"] = uuid4()
    data["sender_name"] = "asthttpd"
    print(data)
    try:
        response = await request.app.state.bus.manager_request(
            manager_name,
            request_name,
            data,
        )
        return JSONResponse({"message": response.reason})
    except RuntimeError:
        return JSONResponse({"status": "No response to request"}, status_code=400)


app = Starlette(
    debug=False,
    routes=[
        Route('/', list_states),
        Route('/{state_name:str}', get_state),
        Route('/{state_name:str}/{request_name:str}', make_request, methods=["POST"]),
    ],
    on_startup=[MQTTBus.on_startup],
    on_shutdown=[MQTTBus.on_shutdown],
)


@click.command("asthttpd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:  # TODO: Use arguments
    """Astoria HTTP Bridge."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s asthttpd %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    uvicorn.run("astoria.asthttpd:app", port=5467, log_level="info")


if __name__ == "__main__":
    main()

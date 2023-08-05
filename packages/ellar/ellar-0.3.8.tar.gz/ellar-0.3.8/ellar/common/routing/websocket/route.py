import typing as t

from starlette.routing import WebSocketRoute as StarletteWebSocketRoute, compile_path
from starlette.status import WS_1008_POLICY_VIOLATION
from starlette.websockets import WebSocketState

from ellar.common.constants import (
    CONTROLLER_OPERATION_HANDLER_KEY,
    EXTRA_ROUTE_ARGS_KEY,
    NOT_SET,
)
from ellar.common.exceptions import (
    ImproperConfiguration,
    WebSocketRequestValidationError,
)
from ellar.common.helper import get_name
from ellar.common.interfaces import IExecutionContext
from ellar.common.params import ExtraEndpointArg, WebsocketEndpointArgsModel
from ellar.reflect import reflect

from ..base import WebsocketRouteOperationBase
from .handler import WebSocketExtraHandler


class WebsocketRouteOperation(WebsocketRouteOperationBase, StarletteWebSocketRoute):
    websocket_endpoint_args_model: t.Type[
        WebsocketEndpointArgsModel
    ] = WebsocketEndpointArgsModel

    __slots__ = (
        "endpoint",
        "_handlers_kwargs",
        "endpoint_parameter_model",
        "_extra_handler_type",
    )

    def __init__(
        self,
        *,
        path: str,
        name: t.Optional[str] = None,
        endpoint: t.Callable,
        encoding: str = "json",
        use_extra_handler: bool = False,
        extra_handler_type: t.Optional[t.Type[WebSocketExtraHandler]] = None,
        **handlers_kwargs: t.Any,
    ) -> None:
        assert path.startswith("/"), "Routed paths must start with '/'"
        self._handlers_kwargs: t.Dict[str, t.Any] = dict(
            encoding=encoding,
            on_receive=None,
            on_connect=None,
            on_disconnect=None,
        )
        self._handlers_kwargs.update(handlers_kwargs)
        self._use_extra_handler = use_extra_handler
        self._extra_handler_type: t.Optional[
            t.Type[WebSocketExtraHandler]
        ] = extra_handler_type

        self.path = path
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            self.path
        )
        self.endpoint = endpoint  # type: ignore
        self.name = get_name(endpoint) if name is None else name

        self.endpoint_parameter_model: WebsocketEndpointArgsModel = NOT_SET

        reflect.define_metadata(CONTROLLER_OPERATION_HANDLER_KEY, self, self.endpoint)

        if self._use_extra_handler:
            self._handlers_kwargs.update(on_receive=self.endpoint)
        self._load_model()

    @classmethod
    def get_websocket_handler(cls) -> t.Type[WebSocketExtraHandler]:
        return WebSocketExtraHandler

    def add_websocket_handler(self, handler_name: str, handler: t.Callable) -> None:
        if handler_name not in self._handlers_kwargs:
            raise Exception(
                f"Invalid Handler Name. Handler Name must be in {list(self._handlers_kwargs.keys())}"
            )
        self._handlers_kwargs.update({handler_name: handler})

    async def _handle_request(self, context: IExecutionContext) -> None:
        func_kwargs, errors = await self.endpoint_parameter_model.resolve_dependencies(
            ctx=context
        )
        if errors:
            websocket = context.switch_to_websocket().get_client()
            exc = WebSocketRequestValidationError(errors)
            if websocket.client_state == WebSocketState.CONNECTING:
                await websocket.accept()
            await websocket.send_json(
                dict(code=WS_1008_POLICY_VIOLATION, errors=exc.errors())
            )
            await websocket.close(code=WS_1008_POLICY_VIOLATION)
            raise exc

        if self._use_extra_handler:
            ws_extra_handler_type = (
                self._extra_handler_type or self.get_websocket_handler()
            )
            ws_extra_handler = ws_extra_handler_type(
                route_parameter_model=self.endpoint_parameter_model,
                **self._handlers_kwargs,
            )
            await ws_extra_handler.dispatch(context=context, **func_kwargs)
        else:
            await self.endpoint(**func_kwargs)

    def _load_model(self) -> None:
        extra_route_args: t.List["ExtraEndpointArg"] = (
            reflect.get_metadata(EXTRA_ROUTE_ARGS_KEY, self.endpoint) or []
        )

        if self.endpoint_parameter_model is NOT_SET:
            self.endpoint_parameter_model = self.websocket_endpoint_args_model(
                path=self.path_format,
                endpoint=self.endpoint,
                param_converters=self.param_convertors,
                extra_endpoint_args=extra_route_args,
            )
            self.endpoint_parameter_model.build_model()
        if not self._use_extra_handler and self.endpoint_parameter_model.body_resolver:
            raise ImproperConfiguration(
                "`WsBody` should only be used when "
                "`use_extra_handler` flag is set to True in WsRoute"
            )

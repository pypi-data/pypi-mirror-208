import inspect
import re
import typing as t
from collections import defaultdict

from pydantic import BaseModel
from pydantic.error_wrappers import ErrorWrapper
from pydantic.fields import FieldInfo, ModelField
from pydantic.typing import ForwardRef, evaluate_forwardref  # type:ignore
from pydantic.utils import Representation, lenient_issubclass
from starlette.convertors import Convertor
from starlette.requests import (
    HTTPConnection as StarletteHTTPConnection,
    Request as StarletteRequest,
)
from starlette.responses import Response
from starlette.websockets import WebSocket as StarletteWebSocket

from ellar.common.constants import (
    ROUTE_OPENAPI_PARAMETERS,
    primitive_types,
    sequence_types,
)
from ellar.common.exceptions import ImproperConfiguration
from ellar.common.interfaces import IExecutionContext

from .. import params
from ..helpers import is_scalar_field, is_scalar_sequence_field
from ..resolvers import (
    BaseRouteParameterResolver,
    IRouteParameterResolver,
    NonParameterResolver,
)
from ..resolvers.non_parameter import (
    ConnectionParam,
    ExecutionContextParameter,
    RequestParameter,
    ResponseRequestParam,
    WebSocketParameter,
)
from .extra_args import ExtraEndpointArg
from .factory import get_parameter_field
from .resolver_generators import (
    BulkArgsResolverGenerator,
    FormArgsResolverGenerator,
    PathArgsResolverGenerator,
    QueryHeaderResolverGenerator,
)

DEFAULT_RESOLVERS: t.Dict[t.Type, t.Type[NonParameterResolver]] = {
    StarletteRequest: RequestParameter,
    StarletteWebSocket: WebSocketParameter,
    Response: ResponseRequestParam,
    StarletteHTTPConnection: ConnectionParam,
    IExecutionContext: ExecutionContextParameter,
}


def add_default_resolver(
    type_identifier: t.Type, resolver_type: t.Type[NonParameterResolver]
) -> None:  # pragma: no cover
    DEFAULT_RESOLVERS.update({type_identifier: resolver_type})


class EndpointArgsModel:
    _bulk_resolvers_generators = {
        str(params.FormFieldInfo): FormArgsResolverGenerator,
        str(params.PathFieldInfo): PathArgsResolverGenerator,
        str(params.QueryFieldInfo): QueryHeaderResolverGenerator,
        str(params.HeaderFieldInfo): QueryHeaderResolverGenerator,
    }

    _provider_skip = primitive_types + sequence_types + (Representation,)

    __slots__ = (
        "path",
        "_computation_models",
        "path_param_names",
        "body_resolver",
        "endpoint_signature",
        "_route_models",
        "param_converters",
        "_extra_endpoint_args",
    )

    def __init__(
        self,
        *,
        path: str,
        endpoint: t.Callable,
        param_converters: t.Dict[str, Convertor],
        extra_endpoint_args: t.Sequence[ExtraEndpointArg] = None,
    ) -> None:
        self.path = path
        self.param_converters = param_converters
        self._computation_models: t.DefaultDict[
            str, t.List[IRouteParameterResolver]
        ] = defaultdict(list)
        self.path_param_names = self.get_path_param_names(path)
        self.endpoint_signature = self.get_typed_signature(endpoint)
        self.body_resolver: t.Optional[
            t.Union[t.Any, BaseRouteParameterResolver]
        ] = None
        self._route_models: t.List[IRouteParameterResolver] = []
        self._extra_endpoint_args: t.List[ExtraEndpointArg] = (
            list(extra_endpoint_args) if extra_endpoint_args else []
        )

    def get_resolver_generator(
        self, param: params.ParamFieldInfo
    ) -> t.Type[BulkArgsResolverGenerator]:
        return self._bulk_resolvers_generators.get(
            str(type(param)), BulkArgsResolverGenerator
        )

    def get_route_models(self) -> t.List[IRouteParameterResolver]:
        """
        Returns all computed endpoint resolvers required for function execution
        :return: List[BaseRouteParameterResolver]
        """
        return self._route_models

    def get_all_models(self) -> t.List[IRouteParameterResolver]:
        """
        Returns all computed endpoint resolvers + omitted resolvers
        :return: List[BaseRouteParameterResolver]
        """
        return (
            self.get_route_models() + self._computation_models[ROUTE_OPENAPI_PARAMETERS]
        )

    @classmethod
    def get_convertor_model_field(
        cls, param_name: str, convertor: Convertor
    ) -> ModelField:
        _converter_signature = inspect.signature(convertor.convert)
        assert (
            _converter_signature.return_annotation is not inspect.Parameter.empty
        ), f"{convertor.__class__.__name__} Convertor must have return type"
        _type = _converter_signature.return_annotation
        return get_parameter_field(
            param_default=params.PathFieldInfo(),
            param_annotation=_type,
            default_field_info=params.PathFieldInfo,
            param_name=param_name,
        )

    def get_omitted_prefix(self) -> t.List[ModelField]:
        """
        Tracks for omitted path parameters for OPENAPI purpose
        :return: None
        """
        _omitted: t.List[ModelField] = []

        signature_dict = dict(self.endpoint_signature.parameters)
        for name, _converter in self.param_converters.items():
            if name in signature_dict:
                continue

            _omitted.append(self.get_convertor_model_field(name, _converter))
        return _omitted

    def build_model(self) -> None:
        """
        Run all endpoint model resolver computation
        :return:
        """
        self._computation_models = defaultdict(list)
        self.compute_route_parameter_list()
        self.compute_extra_route_args()
        self.build_body_field()
        self._route_models = (
            self._computation_models[params.HeaderFieldInfo.in_.value]
            + self._computation_models[params.PathFieldInfo.in_.value]
            + self._computation_models[params.QueryFieldInfo.in_.value]
            + self._computation_models[params.CookieFieldInfo.in_.value]
            + self._computation_models[NonParameterResolver.in_]
        )

    def compute_route_parameter_list(
        self, body_field_class: t.Type[FieldInfo] = params.BodyFieldInfo
    ) -> None:
        for param_name, param in self.endpoint_signature.parameters.items():
            if (
                param.kind == param.VAR_KEYWORD
                or param.kind == param.VAR_POSITIONAL
                or (
                    param.name == "self" and param.annotation == inspect.Parameter.empty
                )
            ):
                # Skipping **kwargs, *args, self
                continue

            if self._add_non_pydantic_field_to_dependency(
                param_name=param.name,
                param_default=param.default,
                param_annotation=param.annotation,
            ):
                continue

            if self._add_non_field_param_to_dependency(
                param_name=param.name,
                param_default=param.default,
                param_annotation=param.annotation,
            ):
                continue

            if param_name in self.path_param_names:
                if isinstance(param.default, params.PathFieldInfo):
                    ignore_default = False
                else:
                    ignore_default = True
                param_field = get_parameter_field(
                    param_default=param.default,
                    param_annotation=param.annotation,
                    param_name=param_name,
                    default_field_info=params.PathFieldInfo,
                    ignore_default=ignore_default,
                )
                assert is_scalar_field(
                    field=param_field
                ), "Path params must be of one of the supported types"
                self._add_to_model(field=param_field)
            else:
                default_field_info = t.cast(
                    t.Type[params.ParamFieldInfo],
                    param.default
                    if isinstance(param.default, FieldInfo)
                    else params.QueryFieldInfo,
                )
                param_field = get_parameter_field(
                    param_default=param.default,
                    param_annotation=param.annotation,
                    default_field_info=default_field_info,
                    param_name=param_name,
                    body_field_class=body_field_class,
                )
                if not isinstance(
                    param_field.field_info, (params.BodyFieldInfo, params.FileFieldInfo)
                ) and not is_scalar_field(field=param_field):
                    if not is_scalar_sequence_field(param_field):
                        if not lenient_issubclass(param_field.outer_type_, BaseModel):
                            raise ImproperConfiguration(
                                f"{param_field.outer_type_} type can't be processed as a field"
                            )

                        bulk_resolver_generator_class = self.get_resolver_generator(
                            param.default
                        )
                        bulk_resolver_generator_class(param_field).generate_resolvers(
                            body_field_class=body_field_class
                        )
                self._add_to_model(field=param_field)

    def _add_non_field_param_to_dependency(
        self,
        *,
        param_default: t.Any,
        param_name: str,
        param_annotation: t.Optional[t.Type],
        key: str = None,
    ) -> t.Optional[bool]:
        if isinstance(param_default, NonParameterResolver):
            model = param_default(param_name, param_annotation)  # type:ignore
            self._computation_models[key or model.in_].append(model)
            return True
        return None

    @classmethod
    def get_path_param_names(cls, path: str) -> t.Set[str]:
        return set(re.findall("{(.*?)}", path))

    @classmethod
    def get_typed_signature(cls, call: t.Callable[..., t.Any]) -> inspect.Signature:
        signature = inspect.signature(call)
        global_ns = getattr(call, "__globals__", {})
        typed_params = [
            inspect.Parameter(
                name=param.name,
                kind=param.kind,
                default=param.default,
                annotation=cls.get_typed_annotation(param, global_ns),
            )
            for param in signature.parameters.values()
        ]
        typed_signature = inspect.Signature(typed_params)
        return typed_signature

    @classmethod
    def get_typed_annotation(
        cls, param: inspect.Parameter, globalns: t.Dict[str, t.Any]
    ) -> t.Any:
        annotation = param.annotation
        if isinstance(annotation, str):
            annotation = ForwardRef(annotation)
            annotation = evaluate_forwardref(annotation, globalns, globalns)
        return annotation

    def _add_to_model(self, *, field: ModelField, key: str = None) -> None:
        field_info = t.cast(params.ParamFieldInfo, field.field_info)
        self._computation_models[str(key or field_info.in_.value)].append(
            field_info.create_resolver(model_field=field)
        )

    async def resolve_dependencies(
        self, *, ctx: IExecutionContext
    ) -> t.Tuple[t.Dict[str, t.Any], t.List[ErrorWrapper]]:
        values: t.Dict[str, t.Any] = {}
        errors: t.List[ErrorWrapper] = []

        if self.body_resolver:
            await self.resolve_body(ctx, values, errors)

        if not errors:
            for parameter_resolver in self._route_models:
                value_, value_errors = await parameter_resolver.resolve(ctx=ctx)
                if value_:
                    values.update(value_)
                if value_errors:
                    _errors = (
                        value_errors
                        if isinstance(value_errors, list)
                        else [value_errors]
                    )
                    errors += _errors
        return values, errors

    def compute_extra_route_args(self) -> None:
        self._add_extra_route_args(*self._extra_endpoint_args)

    def _add_extra_route_args(
        self, *extra_operation_args: ExtraEndpointArg, key: str = None
    ) -> None:
        for param in extra_operation_args:
            if self._add_non_field_param_to_dependency(
                param_name=param.name,
                param_default=param.default,
                param_annotation=param.annotation,
                key=key,
            ):
                continue

            default_field_info = t.cast(
                t.Type[params.ParamFieldInfo],
                param.default
                if isinstance(param.default, FieldInfo)
                else params.QueryFieldInfo,
            )
            param_field = get_parameter_field(
                param_default=param.default,
                param_annotation=param.annotation,
                default_field_info=default_field_info,
                param_name=param.name,
            )
            self._add_to_model(field=param_field, key=key)

    async def resolve_body(
        self, ctx: IExecutionContext, values: t.Dict, errors: t.List
    ) -> None:
        """Body Resolver Implementation"""

    def __deepcopy__(
        self, memodict: t.Dict = {}
    ) -> "EndpointArgsModel":  # pragma: no cover
        return self.__copy__(memodict)

    def __copy__(
        self, memodict: t.Dict = {}
    ) -> "EndpointArgsModel":  # pragma: no cover
        return self

    def build_body_field(self) -> None:
        raise NotImplementedError

    def _add_non_pydantic_field_to_dependency(
        self, param_name: str, param_default: t.Any, param_annotation: t.Any
    ) -> bool:
        resolver_class = DEFAULT_RESOLVERS.get(param_annotation)
        if resolver_class and param_default == inspect.Parameter.empty:
            _inject = resolver_class()(param_name, param_annotation)
            self._computation_models[_inject.in_].append(_inject)
            return True
        return False

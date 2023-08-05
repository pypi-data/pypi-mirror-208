import typing as t

from ellar.common.constants import GUARDS_KEY

from .base import set_metadata as set_meta

if t.TYPE_CHECKING:  # pragma: no cover
    from ellar.common.models import GuardCanActivate


def Guards(
    *_guards: t.Union[t.Type["GuardCanActivate"], "GuardCanActivate"]
) -> t.Callable:
    """
    =========CONTROLLER AND ROUTE FUNCTION DECORATOR ==============

    Defines list of guards for a route function
    :param _guards: Guard Type or Instance
    :return:
    """
    return set_meta(GUARDS_KEY, list(_guards))

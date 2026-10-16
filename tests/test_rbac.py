import pytest

from mss.core.rbac import (
    Permission,
    PermissionError_,
    Principal,
    Role,
)


def test_admin_can_factory_reset() -> None:
    p = Principal(user_id="a", roles=frozenset({Role.ADMIN}))
    p.require(Permission.FACTORY_RESET)


def test_viewer_cannot_backup() -> None:
    p = Principal(user_id="v", roles=frozenset({Role.VIEWER}))
    with pytest.raises(PermissionError_):
        p.require(Permission.BACKUP_DEVICE)
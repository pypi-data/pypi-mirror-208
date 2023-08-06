import uuid
from typing import NamedTuple, Protocol


class BaseUser(Protocol):
    id: uuid.UUID
    name: str
    email: str | None
    permissions: set[str]

    @staticmethod
    def is_authenticated() -> bool:
        ...

    def has_permission(self, permission: str) -> bool:
        ...

    def has_permissions(self, permissions: set[str]) -> bool:
        ...


class AnonymousUser:
    id: uuid.UUID
    name: str
    email: str | None
    permissions: set[str]

    @staticmethod
    def is_authenticated() -> bool:
        return False

    def has_permission(self, permission: str) -> bool:
        return False

    def has_permissions(self, permissions: set[str]) -> bool:
        return False


class User(NamedTuple):
    id: uuid.UUID = None
    name: str = None
    email: str | None = None
    permissions: set[str] = set()

    @staticmethod
    def is_authenticated() -> bool:
        return True

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_permissions(self, permissions: set[str]) -> bool:
        return permissions.issubset(self.permissions)

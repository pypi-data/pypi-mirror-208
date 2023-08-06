import uuid
from typing import Protocol


class BaseUser(Protocol):
    id: uuid.UUID
    username: str
    email: str | None
    permissions: set[str]
    data: dict = {}

    @staticmethod
    def is_authenticated() -> bool:
        ...

    def has_permission(self, permission: str) -> bool:
        ...

    def has_permissions(self, permissions: set[str]) -> bool:
        ...


class AnonymousUser:
    id: uuid.UUID
    username: str
    email: str | None
    permissions: set[str]
    data: dict = {}

    @staticmethod
    def is_authenticated() -> bool:
        return False

    def has_permission(self, permission: str) -> bool:
        return False

    def has_permissions(self, permissions: set[str]) -> bool:
        return False


class User:

    def __init__(
        self,
        id: uuid.UUID,
        phone_number: str | None = None,
        username: str | None = None,
        email: str | None = None,
        permissions: set[str] = None,
        **kwargs,
    ):
        self.id = id
        self.phone_number = phone_number
        self.username = username
        self.email = email
        self.permissions = permissions or set()
        self.data = kwargs

    @staticmethod
    def is_authenticated() -> bool:
        return True

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_permissions(self, permissions: set[str]) -> bool:
        return permissions.issubset(self.permissions)

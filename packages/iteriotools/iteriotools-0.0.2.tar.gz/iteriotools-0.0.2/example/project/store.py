from collections.abc import Iterable

from .models import User


class Store:
    def __init__(self, *args, users: Iterable[User], **kwargs):
        super().__init__(*args, **kwargs)
        self.users = users

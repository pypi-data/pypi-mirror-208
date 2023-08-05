from typing import Dict


class User:
    id: int
    username: str
    name: str

    def __init__(self, id_: int, username: str, name: str) -> None:
        self.id = id_
        self.username = username
        self.name = name

    @classmethod
    def from_json(self, data: 'Dict[str, str | int]') -> 'User':
        return User(
            int(data["id"]),
            str(data["username"]),
            str(data["name"])
        )

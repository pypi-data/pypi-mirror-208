from typing import List, Union

from perun.connector.models.HasIdAbstract import HasIdAbstract


class Facility(HasIdAbstract):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        rp_id: str,
        attributes: dict[str, Union[str, int, bool, List[str], dict[str, str]]],
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.rp_id = rp_id
        self.attributes = attributes

    def __str__(self):
        return (
            f"id: {self.id} name: {self.name} description: "
            f"{self.description} rp_id: {self.rp_id} attributes: {self.attributes}"
        )

    def __eq__(self, other):
        if isinstance(other, Facility):
            return (
                self.id == other.id
                and self.name == other.name
                and self.description == other.description
                and self.rp_id == other.rp_id
            )
        return False

    def __hash__(self):
        return hash((self.id, self.name, self.description, self.rp_id))

from uuid import uuid4

from ..Units.Unit import Unit


class Kingdom:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.available = {}
        self.armies = {}
        self.diplomacy = 0
        self.espionage = 0
        self.lore = 0
        self.operations = 0
        self.communications = 10
        self.resolve = 10
        self.resources = 10
        self.ledger = []

    def add_transaction(self, transaction: "LedgerEntry"):
        self.ledger.append(transaction)

    def get_treasury(self) -> int:
        total = 0
        for transaction in self.ledger:
            total = total + transaction.change
        return total

    def research_unit(self, new_unit_type: Unit):
        new_unit_id = uuid4()
        self.available[new_unit_id] = new_unit_type

    def muster_unit(self, unit_type_id: str):
        if unit_type_id not in self.available.keys():
            raise UnitNotFoundError(f"Could not find unit with ID: {unit_type_id}")
        new_unit_type = self.available[unit_type_id]
        new_unit = new_unit_type.clone()
        new_unit_id = uuid4()
        self.armies[new_unit_id] = new_unit

    class LedgerEntry:
        def __init__(self, description: str, change: int) -> None:
            self.description = description
            self.change = change

    class UnitNotFoundError(Exception):
        pass

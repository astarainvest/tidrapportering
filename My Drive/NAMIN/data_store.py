import json
from pathlib import Path


class DataStore:
    """Sparar och laddar all programdata som JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).resolve().parent / "data" / "app_data.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict = {}

    def load(self) -> dict:
        if self.path.exists():
            with self.path.open(encoding="utf-8") as file:
                self._data = json.load(file)
        else:
            self._data = {}
        return self._data

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self._data, file, ensure_ascii=False, indent=2)

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, value: dict) -> None:
        self._data = value
        self.save()

    def update(self, **changes) -> None:
        self._data.update(changes)
        self.save()

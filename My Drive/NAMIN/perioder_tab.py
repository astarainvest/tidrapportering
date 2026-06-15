from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data_store import DataStore


def perioder(data_store: DataStore) -> list[dict]:
    items = data_store.data.get("perioder")
    if not isinstance(items, list):
        items = []
        data_store.update(perioder=items)
    return items


def delete_perioder_for_units(data_store: DataStore, enhet_beteckningar: set[str]) -> None:
    if not enhet_beteckningar:
        return
    items = [
        period
        for period in perioder(data_store)
        if period.get("enhet_beteckning") not in enhet_beteckningar
    ]
    data_store.update(perioder=items)


def create_period_for_unit(data_store: DataStore, enhet_beteckning: str) -> dict:
    items = perioder(data_store)
    unit_count = sum(
        1 for period in items if period.get("enhet_beteckning") == enhet_beteckning
    )
    new_period = {
        "enhet_beteckning": enhet_beteckning,
        "beteckning": enhet_beteckning,
        "index": unit_count + 1,
    }
    items.append(new_period)
    data_store.update(perioder=items)
    return new_period


def enhet_namn(data_store: DataStore, enhet_beteckning: str) -> str:
    for unit in data_store.data.get("organisation", []):
        if unit.get("beteckning") == enhet_beteckning:
            return unit.get("namn", "")
    return ""


class PerioderTab(QWidget):
    COLUMNS = ("Beteckning", "Index", "Enhet")

    def __init__(self, data_store: DataStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.data_store = data_store

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

        self.reload()

    def reload(self) -> None:
        items = sorted(
            perioder(self.data_store),
            key=lambda period: (period.get("enhet_beteckning", ""), period.get("index", 0)),
        )
        self.table.setRowCount(len(items))
        for row, period in enumerate(items):
            beteckning = period.get("beteckning", "")
            index = period.get("index", "")
            enhet = enhet_namn(self.data_store, period.get("enhet_beteckning", ""))

            beteckning_item = QTableWidgetItem(beteckning)
            beteckning_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            )
            index_item = QTableWidgetItem(str(index))
            index_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            )

            self.table.setItem(row, 0, beteckning_item)
            self.table.setItem(row, 1, index_item)
            self.table.setItem(row, 2, QTableWidgetItem(enhet))

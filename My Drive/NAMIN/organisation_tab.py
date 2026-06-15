from PySide6.QtCore import QRegularExpression, QTimer, Qt
from PySide6.QtGui import QAction, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data_store import DataStore
from perioder_tab import (
    PerioderTab,
    create_period_for_unit,
    delete_perioder_for_units,
    perioder,
)

LETTER_PATTERN = QRegularExpression(r"^[A-ZÅÄÖ]$")


class HuvudenhetDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Huvudenhet")
        self.setModal(True)

        self.beteckning_input = QLineEdit()
        self.beteckning_input.setMaxLength(1)
        self.beteckning_input.setPlaceholderText("A")
        self.beteckning_input.setValidator(
            QRegularExpressionValidator(LETTER_PATTERN)
        )
        self.beteckning_input.textChanged.connect(self._on_beteckning_changed)

        self.namn_input = QLineEdit()
        self.namn_input.setPlaceholderText("Namn på huvudenheten")

        form = QFormLayout()
        form.addRow("Beteckning:", self.beteckning_input)
        form.addRow("Namn:", self.namn_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        self._ok_button = buttons.button(QDialogButtonBox.Ok)
        self._ok_button.setEnabled(False)
        self.namn_input.textChanged.connect(self._update_ok_button)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Organisationen är tom. Ange en huvudenhet."))
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_beteckning_changed(self, text: str) -> None:
        upper = text.upper()
        if text != upper:
            self.beteckning_input.blockSignals(True)
            self.beteckning_input.setText(upper)
            self.beteckning_input.blockSignals(False)
        self._update_ok_button()

    def _update_ok_button(self) -> None:
        beteckning_ok = bool(self.beteckning_input.text().strip())
        namn_ok = bool(self.namn_input.text().strip())
        self._ok_button.setEnabled(beteckning_ok and namn_ok)

    def values(self) -> tuple[str, str]:
        return (
            self.beteckning_input.text().strip(),
            self.namn_input.text().strip(),
        )


class SubenhetDialog(QDialog):
    def __init__(
        self,
        parent_beteckning: str,
        existing_beteckningar: set[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.parent_beteckning = parent_beteckning
        self.existing_beteckningar = existing_beteckningar
        self.setWindowTitle("Subenhet")
        self.setModal(True)

        self.bokstav_input = QLineEdit()
        self.bokstav_input.setMaxLength(1)
        self.bokstav_input.setPlaceholderText("A")
        self.bokstav_input.setValidator(
            QRegularExpressionValidator(LETTER_PATTERN)
        )
        self.bokstav_input.textChanged.connect(self._on_bokstav_changed)

        self.beteckning_label = QLabel()
        self.namn_input = QLineEdit()
        self.namn_input.setPlaceholderText("Namn på subenheten")

        form = QFormLayout()
        form.addRow("Överordnad:", QLabel(parent_beteckning))
        form.addRow("Extra bokstav:", self.bokstav_input)
        form.addRow("Beteckning:", self.beteckning_label)
        form.addRow("Namn:", self.namn_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)
        self._ok_button = buttons.button(QDialogButtonBox.Ok)
        self._ok_button.setEnabled(False)
        self.namn_input.textChanged.connect(self._update_ok_button)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Skapa subenhet under {parent_beteckning}."))
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._update_beteckning_label()

    def _full_beteckning(self) -> str:
        return self.parent_beteckning + self.bokstav_input.text().strip()

    def _on_bokstav_changed(self, text: str) -> None:
        upper = text.upper()
        if text != upper:
            self.bokstav_input.blockSignals(True)
            self.bokstav_input.setText(upper)
            self.bokstav_input.blockSignals(False)
        self._update_beteckning_label()
        self._update_ok_button()

    def _update_beteckning_label(self) -> None:
        letter = self.bokstav_input.text().strip()
        if letter:
            self.beteckning_label.setText(self._full_beteckning())
        else:
            self.beteckning_label.setText("—")

    def _update_ok_button(self) -> None:
        letter_ok = bool(self.bokstav_input.text().strip())
        namn_ok = bool(self.namn_input.text().strip())
        unique_ok = self._full_beteckning() not in self.existing_beteckningar
        self._ok_button.setEnabled(letter_ok and namn_ok and unique_ok)

    def _try_accept(self) -> None:
        beteckning = self._full_beteckning()
        if beteckning in self.existing_beteckningar:
            QMessageBox.warning(
                self,
                "Beteckning finns redan",
                f"Beteckningen \"{beteckning}\" används redan. Välj en annan bokstav.",
            )
            return
        self.accept()

    def values(self) -> tuple[str, str]:
        return self._full_beteckning(), self.namn_input.text().strip()


class OrganisationTab(QWidget):
    COLUMNS = ("Beteckning", "Namn")

    def __init__(
        self,
        data_store: DataStore,
        perioder_tab: PerioderTab | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.data_store = data_store
        self.perioder_tab = perioder_tab

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

        self._load_table()
        QTimer.singleShot(0, self._ensure_huvudenhet)

    def _units(self) -> list[dict]:
        units = self.data_store.data.get("organisation")
        if not isinstance(units, list):
            units = []
            self.data_store.update(organisation=units)
        return units

    def _beteckningar(self) -> set[str]:
        return {unit.get("beteckning", "") for unit in self._units()}

    def _load_table(self) -> None:
        units = self._units()
        self.table.setRowCount(len(units))
        for row, unit in enumerate(units):
            self._set_row(row, unit.get("beteckning", ""), unit.get("namn", ""))

    def _set_row(self, row: int, beteckning: str, namn: str) -> None:
        beteckning_item = QTableWidgetItem(beteckning)
        beteckning_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.table.setItem(row, 0, beteckning_item)
        self.table.setItem(row, 1, QTableWidgetItem(namn))

    def _show_context_menu(self, position) -> None:
        row = self.table.rowAt(position.y())
        if row < 0:
            return

        beteckning_item = self.table.item(row, 0)
        if beteckning_item is None:
            return

        menu = QMenu(self)
        parent_beteckning = beteckning_item.text()

        create_period_action = QAction("Skapa period", self)
        create_period_action.triggered.connect(
            lambda: self._create_period(parent_beteckning)
        )
        menu.addAction(create_period_action)

        create_action = QAction("Skapa subenhet…", self)
        create_action.triggered.connect(
            lambda: self._create_subenhet(row, parent_beteckning)
        )
        menu.addAction(create_action)

        menu.addSeparator()

        delete_action = QAction("Radera enhet…", self)
        namn_item = self.table.item(row, 1)
        enhet_namn = namn_item.text() if namn_item is not None else ""
        delete_action.triggered.connect(
            lambda: self._delete_enhet(parent_beteckning, enhet_namn)
        )
        menu.addAction(delete_action)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _create_period(self, enhet_beteckning: str) -> None:
        create_period_for_unit(self.data_store, enhet_beteckning)
        if self.perioder_tab is not None:
            self.perioder_tab.reload()

    def _create_subenhet(self, row: int, parent_beteckning: str) -> None:
        dialog = SubenhetDialog(
            parent_beteckning,
            self._beteckningar(),
            self.window(),
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        beteckning, namn = dialog.values()
        if beteckning in self._beteckningar():
            QMessageBox.warning(
                self,
                "Beteckning finns redan",
                f"Beteckningen \"{beteckning}\" används redan.",
            )
            return

        units = self._units()
        units.insert(row + 1, {"beteckning": beteckning, "namn": namn})
        self.data_store.update(organisation=units)
        self._load_table()

    def _beteckningar_to_delete(self, beteckning: str) -> set[str]:
        return {
            unit.get("beteckning", "")
            for unit in self._units()
            if unit.get("beteckning") == beteckning
            or (
                unit.get("beteckning", "").startswith(beteckning)
                and len(unit.get("beteckning", "")) > len(beteckning)
            )
        }

    def _delete_enhet(self, beteckning: str, namn: str) -> None:
        to_delete = self._beteckningar_to_delete(beteckning)
        sub_count = len(to_delete) - 1

        period_count = sum(
            1
            for period in perioder(self.data_store)
            if period.get("enhet_beteckning") in to_delete
        )

        message = f"Vill du radera enheten {beteckning}"
        if namn:
            message += f" ({namn})"
        message += "?"
        if sub_count:
            message += f"\n\n{sub_count} subenhet(er) raderas också."
        if period_count:
            message += f"\n\n{period_count} period(er) raderas också."

        answer = QMessageBox.question(
            self,
            "Radera enhet",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        units = [
            unit
            for unit in self._units()
            if unit.get("beteckning") not in to_delete
        ]
        delete_perioder_for_units(self.data_store, to_delete)
        self.data_store.update(organisation=units)
        self._load_table()
        if self.perioder_tab is not None:
            self.perioder_tab.reload()
        if not self._units():
            QTimer.singleShot(0, self._ensure_huvudenhet)

    def _ensure_huvudenhet(self) -> None:
        if self._units():
            return

        while not self._units():
            dialog = HuvudenhetDialog(self.window())
            if dialog.exec() != QDialog.DialogCode.Accepted:
                continue

            beteckning, namn = dialog.values()
            if beteckning in self._beteckningar():
                QMessageBox.warning(
                    self,
                    "Beteckning finns redan",
                    f"Beteckningen \"{beteckning}\" används redan.",
                )
                continue

            self.data_store.update(
                organisation=[{"beteckning": beteckning, "namn": namn}]
            )
            self._load_table()

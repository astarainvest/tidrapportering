import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from data_store import DataStore
from organisation_tab import OrganisationTab
from perioder_tab import PerioderTab


class MainWindow(QMainWindow):
    def __init__(self, data_store: DataStore) -> None:
        super().__init__()
        self.data_store = data_store

        self.setWindowTitle("Namin")
        self.setMinimumSize(800, 600)

        tabs = QTabWidget()
        perioder_tab = PerioderTab(data_store)
        tabs.addTab(OrganisationTab(data_store, perioder_tab), "Organisation")
        tabs.addTab(perioder_tab, "Perioder")
        self.setCentralWidget(tabs)

    def closeEvent(self, event) -> None:
        self.data_store.save()
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)

    data_store = DataStore()
    data_store.load()

    window = MainWindow(data_store)
    window.showMaximized()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

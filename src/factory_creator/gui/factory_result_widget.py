from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .quiet_web_engine_page import QuietWebEnginePage


class FactoryResultWidget(QWidget):
    """
    Displays generated factory results either in embedded tabs or external browser buttons.
    """

    def __init__(self, use_embedded_browser: bool = True) -> None:
        """
        Create the result display for the selected browser mode.

        :param use_embedded_browser: Whether to show results in embedded web views.
        """
        super().__init__()

        self.use_embedded_browser = use_embedded_browser
        self.factory_link = None
        self.evolved_factory_link = None

        if self.use_embedded_browser:
            layout = QVBoxLayout(self)

            self.factory_browser_tabs = QTabWidget()

            self.factory_browser = QWebEngineView()
            self.evolved_factory_browser = QWebEngineView()
            self.factory_browser.setPage(QuietWebEnginePage(self.factory_browser))
            self.evolved_factory_browser.setPage(QuietWebEnginePage(self.evolved_factory_browser))

            self.factory_browser_tabs.addTab(self.factory_browser, "Factory")
            self.factory_browser_tabs.addTab(self.evolved_factory_browser, "Evolved factory")
            self.factory_browser_tabs.setMinimumHeight(600)

            layout.addWidget(self.factory_browser_tabs)
        else:
            layout = QHBoxLayout(self)

            self.factory_link_button = QPushButton("Show factory")
            layout.addWidget(self.factory_link_button)

            self.evolved_factory_link_button = QPushButton("Show evolved factory")
            layout.addWidget(self.evolved_factory_link_button)

            self.factory_link_button.clicked.connect(self._open_factory_link)
            self.evolved_factory_link_button.clicked.connect(self._open_evolved_factory_link)

        self.hide()

    def show_results(self, factory_link: str, evolved_factory_link: str) -> None:
        """
        Store and display links for the initial and evolved factory blueprints.

        :param factory_link: URL for the factory before evolution.
        :param evolved_factory_link: URL for the factory after evolution.
        """
        self.factory_link = factory_link
        self.evolved_factory_link = evolved_factory_link

        if self.use_embedded_browser:
            self.factory_browser.load(QUrl(self.factory_link))
            self.evolved_factory_browser.load(QUrl(self.evolved_factory_link))

        self.show()

    def clear(self) -> None:
        self.factory_link = None
        self.evolved_factory_link = None
        self.hide()

    def set_controls_enabled(self, enabled: bool) -> None:
        """
        Enable or disable external browser buttons when they exist.

        :param enabled: Whether result controls should accept user input.
        """
        if not self.use_embedded_browser:
            self.factory_link_button.setEnabled(enabled)
            self.evolved_factory_link_button.setEnabled(enabled)

    def _open_factory_link(self) -> None:
        self._open_link(self.factory_link, "Factory link is empty")

    def _open_evolved_factory_link(self) -> None:
        self._open_link(self.evolved_factory_link, "Evolved factory link is empty")

    def _open_link(self, link: str | None, error_message: str) -> None:
        if link is None:
            QMessageBox.critical(self, "Error", error_message)
            return

        QDesktopServices.openUrl(QUrl(link))

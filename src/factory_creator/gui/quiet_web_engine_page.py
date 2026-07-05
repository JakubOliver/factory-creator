from PySide6.QtWebEngineCore import QWebEnginePage


class QuietWebEnginePage(QWebEnginePage):
    """
    Web engine page that suppresses selected harmless JavaScript console warnings.
    """

    IGNORED_CONSOLE_MESSAGES = (
        "Failed to create WebGPU Context Provider",
    )

    def javaScriptConsoleMessage(self, level, message, line_number, source_id) -> None:
        """
        Forward JavaScript console messages except known ignored warnings.

        :param level: Severity level reported by Qt WebEngine.
        :param message: JavaScript console message text.
        :param line_number: Source line number for the message.
        :param source_id: Source identifier reported by Qt WebEngine.
        """
        if any(ignored_message in message for ignored_message in self.IGNORED_CONSOLE_MESSAGES):
            return

        super().javaScriptConsoleMessage(level, message, line_number, source_id)

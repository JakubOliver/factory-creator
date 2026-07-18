from collections.abc import Callable
from enum import IntEnum


class OutputLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class OutputReporter:
    def __init__(
        self,
        report_method: Callable = print,
        level: OutputLevel = OutputLevel.MEDIUM,
    ) -> None:
        self.report_method = report_method
        self.level = level

    def low(self, message: str) -> None:
        self._report(message, OutputLevel.LOW)

    def medium(self, message: str) -> None:
        self._report(message, OutputLevel.MEDIUM)

    def high(self, message: str) -> None:
        self._report(message, OutputLevel.HIGH)

    def _report(self, message: str, minimum_level: OutputLevel) -> None:
        if self.level >= minimum_level:
            self.report_method(message)

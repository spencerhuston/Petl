import logging
from enum import Enum
from typing import List


class Log:
    __debug_enabled: bool = False

    __title_separator: str = "=" * 20

    class LogLevel(Enum):
        DEBUG = 0,
        INFO = 1,
        WARN = 2,
        ERROR = 3

    __reset: str = "\033[0;0m"
    __warn_color: str = "\033[33m"
    __error_color: str = "\033[1;31m"

    __warnings: List[str] = []
    __errors: List[str] = []

    def __init__(self, debug=False):
        self.__debug_enabled = debug
        self.__warnings = []
        self.__errors = []

    def color_text(self, text: str, color: str) -> str:
        return f"{color}{text}{self.__reset}"

    def __print(self, text: str, level: LogLevel):
        if level == self.LogLevel.DEBUG and self.__debug_enabled:
            print(text)
        elif level == self.LogLevel.INFO:
            print(text)
        elif level == self.LogLevel.WARN:
            print(self.color_text(text, self.__warn_color))
        elif level == self.LogLevel.ERROR:
            print(self.color_text(text, self.__error_color))

    def info(self, text: str):
        self.__print(text, self.LogLevel.INFO)
        logging.info(text)

    def get_debug_enabled(self) -> bool:
        return self.__debug_enabled

    def debug(self, text: str):
        self.__print(text, self.LogLevel.DEBUG)

    def debug_block(self, title: str, block: str):
        self.debug(f"{self.__make_title(title)}\n{block}\n{self.__title_separator}\n")

    def warn(self, text: str):
        self.__warnings.append(text)
        self.__print(text, self.LogLevel.WARN)

    def error(self, text: str):
        self.__errors.append(text)
        self.__print(text, self.LogLevel.ERROR)

    def warnings_occurred(self) -> bool:
        return len(self.__warnings) > 0

    def get_warnings(self) -> List[str]:
        return self.__warnings

    def errors_occurred(self) -> bool:
        return len(self.__errors) > 0

    def get_errors(self) -> List[str]:
        return self.__errors

    def __make_title(self, title: str) -> str:
        return f"{self.__title_separator}\n{title}\n{self.__title_separator}"

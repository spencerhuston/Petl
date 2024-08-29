from dataclasses import dataclass


@dataclass
class FilePosition:
    line: int = 0
    column: int = 0
    line_text: str = ""

    def to_string(self):
        character_location_str: str = ('-' * self.column) + "^"
        return f"Line: {self.line + 1}, column: {self.column + 1}\n{self.line_text}\n{character_location_str}"

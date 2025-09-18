from dataclasses import dataclass, field


@dataclass
class FilePosition:
    line: int = field(default_factory=int)
    column: int = field(default_factory=int)
    line_text: str = field(default_factory=str)

    def to_string(self):
        character_location_str: str = ('-' * self.column) + "^"
        return f"Line: {self.line + 1}, column: {self.column + 1}\n{self.line_text}\n{character_location_str}"

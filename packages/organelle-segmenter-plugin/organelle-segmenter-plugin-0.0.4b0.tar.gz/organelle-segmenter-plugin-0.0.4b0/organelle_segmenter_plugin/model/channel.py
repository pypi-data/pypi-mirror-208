from dataclasses import dataclass


@dataclass
class Channel:  # These are really z-slices
    index: int
    name: str = None

    @property
    def display_name(self):
        if self.name is None or self.name.strip().isspace():
            return f"Channel {self.index}"

        return f"Ch{self.index}.  {self.name}"

    def __repr__(self):
        return self.display_name

from dataclasses import dataclass

@dataclass
class Club:

    name: str
    id: int|None=None

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict[str,str]:
        return {
            'name': self.name
        }
    

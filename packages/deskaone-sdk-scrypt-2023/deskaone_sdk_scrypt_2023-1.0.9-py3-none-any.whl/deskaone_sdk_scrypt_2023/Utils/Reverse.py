
class Reverse:
    
    @staticmethod
    def Dict(data: dict) -> dict:
        return dict(sorted(reversed(list(data.items()))))
    
    @staticmethod
    def List(data: dict) -> list:
        return list(sorted(reversed(list(data.items()))))
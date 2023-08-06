import os, platform

class __Reset__:
    
    def __init__(self) -> None:        
        if platform.system().lower() == "windows":
            os.system('color')
            os.system('cls')
        else:os.system('clear')
class Reset(__Reset__): ...
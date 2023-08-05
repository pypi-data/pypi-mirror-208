from typing import Optional
import os, sys, datetime, time
from .Color import Color
from deskaone_sdk_scrypt_2023.Exceptions import Error, Stoper

class Typer:
    
    @staticmethod
    def Parse_Text(message: str):
        Size = os.get_terminal_size()
        Length = Size.columns
        if len(message) > Length:message = message[:Length]
        elif len(message) < Length:message  = message + ' ' * (Length - len(message))
        return message
    
    @staticmethod
    def Parse_Text_Line(message: str, Normal: Optional[bool] = None, Bold: Optional[bool] = None):
        Size = os.get_terminal_size()
        Length = int((Size.columns - 22) / 2)
        if len(message) > Length:message = message[:Length]
        elif len(message) < Length:
            if Normal is True:message  = message + '-' * (Length - len(message))
            elif Bold is True:message  = message + '=' * (Length - len(message))
        return message
    
    @staticmethod
    def Print(message: any, Refresh: Optional[bool] = None, Enter: Optional[bool] = None, isTimer: Optional[bool] = None): # type: ignore
        if Refresh is None and Enter is None:raise Error('Refresh True or False / Enter True or False')
        if Enter is True:
            sys.stdout.write(f'{Typer.Parse_Text(" ")}\r')
            sys.stdout.write(f'{Typer.Parse_Text(message)}{Color.WHITE}\n')
            sys.stdout.write(f'{Typer.Parse_Text(" ")}\r')
            sys.stdout.flush()
        if Refresh is True:
            sys.stdout.write(f'{Typer.Parse_Text(message)}{Color.WHITE}\r')
            if isTimer is False:sys.stdout.write(f'{Typer.Parse_Text(" ")}\r')

    @staticmethod
    def Line(Normal: Optional[bool] = None, Bold: Optional[bool] = None):
        if Normal is None and Bold is None:raise Error('Normal True or False / Bold True or False')
        if Normal is True:sys.stdout.write(
            f'{Typer.Parse_Text_Line("-", Normal=True)}{Color.BLUE}[{Color.YELLOW}{datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}{Color.BLUE}]{Color.WHITE}{Typer.Parse_Text_Line("-", Normal=True)}{Color.WHITE}\n')
        if Bold is True:sys.stdout.write(f'{Typer.Parse_Text_Line("=", Bold=True)}{Color.BLUE}[{Color.YELLOW}{datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}{Color.BLUE}]{Color.WHITE}{Typer.Parse_Text_Line("=", Bold=True)}{Color.WHITE}\n')

    @staticmethod
    def Run(message: any, Refresh: Optional[bool] = None, Enter: Optional[bool] = None): # type: ignore
        if Refresh is None and Enter is None:raise Error('Refresh True or False / Enter True or False')
        if Refresh is True:
            for c in str(message) + "\r":
                sys.stdout.write(c)
                sys.stdout.flush()
                time.sleep(2 * 0.001)
        if Enter is True:
            for c in str(message) + "\n":
                sys.stdout.write(c)
                sys.stdout.flush()
                time.sleep(2 * 0.001)

    @staticmethod
    def Input(message: any, Integer: Optional[bool] = None, String: Optional[bool] = None): # type: ignore
        if Integer is None and String is None:raise Error('Integer True or False / String True or False')
        if Integer is True:
            while True:
                try:return int(input(f'{Color.WHITE}{message}{Color.WHITE}'))
                except KeyboardInterrupt:raise Stoper('Exit')
        if String is True:
            while True:
                try:return str(input(f'{Color.WHITE}{message}{Color.WHITE}'))
                except KeyboardInterrupt:raise Stoper('Exit')
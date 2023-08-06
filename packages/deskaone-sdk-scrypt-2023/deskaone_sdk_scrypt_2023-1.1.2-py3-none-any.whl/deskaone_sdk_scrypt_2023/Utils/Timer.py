import time, sys, datetime
from datetime import datetime as DTime
from .Color import Color
from .Typer import Typer
from deskaone_sdk_scrypt_2023.Exceptions import Error, Stoper

class Timer:
    
    @staticmethod
    def sleep(seconds: int):
        while True:            
            try:
                seconds    -= 1
                DAYS = int(seconds / 60 / 60 / 24)
                HOURS = int(seconds / 60 / 60) % 24
                MINUTES = int(seconds / 60) % 60
                SECONDS = int(seconds) % 60
                if seconds < 0:
                    sys.stdout.write("                                                                      \r")
                    break
                time.sleep(1)
                SPACE_1 = f'{Color.YELLOW}['
                SPACE_2 = f'{Color.YELLOW}]'
                WHITE   = Color.WHITE
                GREEN   = Color.GREEN
                RED     = Color.RED
                RESET   = Color.RESET
                if len(str(DAYS)) == 1:DAYS_V = f'0{DAYS}'
                else:DAYS_V = f'{DAYS}'
                if len(str(HOURS)) == 1:HOURS_V = f'0{HOURS}'
                else:HOURS_V = f'{HOURS}'
                if len(str(MINUTES)) == 1:MINUTES_V = f'0{MINUTES}'
                else:MINUTES_V = f'{MINUTES}'
                if len(str(SECONDS)) == 1:SECONDS_V = f'0{SECONDS}'
                else:SECONDS_V = f'{SECONDS}'
                
                if DAYS > 0 and HOURS >= 0 and MINUTES >= 0 and SECONDS >= 0:Typer.Print(f'{RED}=> {WHITE}Please Wait {SPACE_1}{GREEN}{DAYS_V}{SPACE_2} {WHITE}Days {SPACE_1}{GREEN}{HOURS_V}{SPACE_2} {WHITE}Hours {SPACE_1}{GREEN}{MINUTES_V}{SPACE_2} {WHITE}Minute {SPACE_1}{GREEN}{SECONDS_V}{SPACE_2} {WHITE}Seconds  ', Refresh=True, isTimer=True)
                elif HOURS > 0 and MINUTES >= 0 and SECONDS >= 0:Typer.Print(f'{RED}=> {WHITE}Please Wait {SPACE_1}{GREEN}{HOURS_V}{SPACE_2} {WHITE}Hours {SPACE_1}{GREEN}{MINUTES_V}{SPACE_2} {WHITE}Minute {SPACE_1}{GREEN}{SECONDS_V}{SPACE_2} {WHITE}Seconds           ', Refresh=True, isTimer=True)
                elif MINUTES > 0 and SECONDS >= 0:Typer.Print(f'{RED}=> {WHITE}Please Wait {SPACE_1}{GREEN}{MINUTES_V}{SPACE_2} {WHITE}Minute {SPACE_1}{GREEN}{SECONDS_V}{SPACE_2} {WHITE}Seconds                        ', Refresh=True, isTimer=True)
                elif SECONDS >= 0:Typer.Print(f'{RED}=> {WHITE}Please Wait {SPACE_1}{GREEN}{SECONDS_V}{SPACE_2} {WHITE}Seconds{RESET}                                        ', Refresh=True, isTimer=True)
            except KeyboardInterrupt:raise Stoper('Exit')
            except Error as e:raise Error(str(e))
    
    @staticmethod
    def for24hours(now: DTime):
        NEXT    = float(int(time.mktime(datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=0, hours=24)).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S").timetuple())))
        return NEXT - float(int(now.timestamp()))
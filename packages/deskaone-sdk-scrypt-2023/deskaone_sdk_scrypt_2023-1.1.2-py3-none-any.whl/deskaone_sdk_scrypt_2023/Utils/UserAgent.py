import random
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem, HardwareType, SoftwareEngine, SoftwareType

class UserAgent:
    
    while True:
        try:
            # you can also import SoftwareEngine, HardwareType, SoftwareType, Popularity from random_user_agent.params
            # you can also set number of user agents required by providing `limit` as parameter
            __softwareName        = [SoftwareName.ANDROID.value]
            __hardwareType        = [HardwareType.MOBILE__PHONE.value]
            __softwareType        = [SoftwareType.APPLICATION.value]
            __operating_systems   = [OperatingSystem.ANDROID.value, OperatingSystem.LINUX.value]   

            #user_agent_rotator = UserAgent(software_types=softwareType, software_names=softwareName, hardware_types=hardwareType, operating_systems=operating_systems, limit=100)

            __user_agent_rotator = UserAgent(software_names=__softwareName, limit=100)
            #, software_names=softwareName, hardware_types=hardwareType, operating_systems=operating_systems

            # Get list of user agents.
            __user_agents = __user_agent_rotator.get_user_agents()

            # Get Random User Agent String.
            __user_agent = __user_agent_rotator.get_random_user_agent()
            __UU = "Dalvik/2.1.0 (" + str(__user_agent).split("(")[1].split(")")[0] + ")"
            __UA = str(__UU).split(";")
            try:
                __USER_AGENT = __UA[0] + ";" + __UA[1] + ";" + __UA[2] + ";" + __UA[4] + ";" + __UA[5]
                __SPLIT_1     = __USER_AGENT.split('Android ')[0]
                __SPLIT_2     = __USER_AGENT.split('Android ')[1]
                __SPLIT_3     = __USER_AGENT.split('Android ')[1].split(';')[1]
                __RANDOM_VERSION  = f'{random.randint(5, 12)}.0.0;'
                USER_AGENT = f'{__SPLIT_1}Android {__RANDOM_VERSION} {__SPLIT_3}'
                break
            except:
                try:
                    __USER_AGENT = __UA[0] + ";" + __UA[1] + ";" + __UA[2] + ";" + __UA[4]
                    __SPLIT_1     = __USER_AGENT.split('Android ')[0]
                    __SPLIT_2     = __USER_AGENT.split('Android ')[1]
                    __SPLIT_3     = __USER_AGENT.split('Android ')[1].split(';')[1]
                    __RANDOM_VERSION  = f'{random.randint(5, 12)}.0.0;'
                    USER_AGENT = f'{__SPLIT_1}Android {__RANDOM_VERSION}{__SPLIT_3}'
                    break
                except:
                    continue
        except:
            continue


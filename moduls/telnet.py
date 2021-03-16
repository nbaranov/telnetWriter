#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from os import name
import socket
import time
from telnetlib import Telnet


class TelnetError(BaseException):
    pass

def readBytes(line):
    '''Format normal string to bytes type'''
    return f"{line}".encode("utf-8")

def writeBytes(line):
    '''Format normal string to bytes type'''
    return f"{line}\n".encode("utf-8")


def listToStr(list):
    result = ''
    for line in list:
        result += str(line).strip() + '\n'
    return result

def printAndLogDebug(msg):
    global logger
    print(msg)
    logging.debug(msg)
    
def printAndLogInfo(msg):
    global logger
    print(msg)
    logging.info(msg)

def printAndLogError(msg):
    global logger
    print(msg)
    logging.error(msg)


def authAndRunCommands(ip, login, password, commands, window):
    '''Function for run list commands on network element
    ip = str
    login = str
    password = str
    commandsList = list of str
    '''
    try:
        with Telnet(ip, timeout=5) as ne:
            try:
                index, match, output = ne.expect(
                    [b"[Pp]assword", b"[Uu]sername", b"[Ll]ogin", b"[Uu]ser", b"[Nn]ame"], timeout=2
                )
                if index != 0:
                    ne.write(writeBytes(login))

                index, match, output = ne.expect([b"[Pp]assword"], timeout=2)
                ne.write(writeBytes(password))
                output = ne.expect([b"[>#]"], timeout=5)[2]
                neName = (
                    output.decode("utf-8").replace("\r\n", "\n").split("\n")[-1].strip("<>[]()#")
                )
                if len(neName) < 5:
                    raise EOFError
                printAndLogDebug(f"Выполнен вход на {neName} {ip}")
                window.refresh()
            except EOFError:
                raise TelnetError(f"Не удалось авторизоваться на элементе {ip}")

            try:
                printAndLogDebug("Начато выполнение команд")
                window.refresh()
                for command in commands:
                    fullOutput = ""
                    ne.write(writeBytes(command))
# Не работает нормально. работает с хуавеем и не работает с ериксоном и наоборот. Видимо надо их как-то разделить. И алкатель не работает по telnet
                    while True:
                        time.sleep(0.3)
                        try:
                            index, match, partOfOutput = ne.expect([readBytes(neName), readBytes("---- More ----"), readBytes("key to continue")], timeout=2)
                            # index1, match1, partOfOutput1 = ne.expect([readBytes(neName), readBytes("---- More ----"), readBytes("key to continue")], timeout=0.1)
                            # if index1 != -1:
                            #     index, match, partOfOutput = index1, match1, partOfOutput1
                            partOfOutput = partOfOutput.decode("utf-8").replace("\r\n", "\n").split("\n")
                            partOfOutput[0] = partOfOutput[0].replace('\x1b[42D', '').strip()
                            if index != 0:
                                withOutLastLine = partOfOutput[:-1]
                                fullOutput += listToStr(withOutLastLine)
                                ne.write(writeBytes(" "))

                            else:
                                fullOutput += listToStr(partOfOutput)
                                output =  ne.expect([readBytes("[>#]")], timeout=5)
                                break
                        except BaseException as error:
                            printAndLogError(error)
                            break
                    fullOutput = fullOutput.split('\n')
                    fullOutput[0] = str(neName).strip() + ': ' + str(command).strip()
                    fullOutput = listToStr(fullOutput)
                    printAndLogInfo(f'Рузультат выполнения команды {command} \n{fullOutput}')
                    window.refresh()
                printAndLogDebug(f'Выполнение команд для {neName} {ip} завершено \n\
======================================================================================\n')
                window.refresh()
            except EOFError:
                raise TelnetError(f"Не удалаось ввести команды или считать вывод на элементе {ip}")
    except socket.timeout:
        raise TelnetError(f"Не удалось подключиться к елементу {ip}")


def runTMS(login, password, ipList, commandList, window):
    '''Function for run list commands on list of IP
    login = str
    password = str
    ipList = list of str
    commandsList = list of str
    window = object of interface
    '''    
    for i in range(len(ipList)):
        print(f'{i+1} from {len(ipList)}:')
        try:
            authAndRunCommands(ipList[i], login, password, commandList, window)
        except TelnetError as error:
            printAndLogError(f"Произлшла ошибка: {error}")
            window.refresh()
    window.find_element("Stop").update(disabled=True)
    window.find_element("Run").update(disabled=False)



logger = logging
logger.Logger('telnet')
logger.basicConfig(
    level=logging.DEBUG,
    filename='log.log',
    format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# ipList = ['10.174.132.194', '10.174.132.195', '10.174.132.196'] 
# commands = [
#     'show backplane 1',
#     'show subrack 1',
#     'show board 1/0',
#     'show board 1/1',
#     'show board 1/2',
#     "show board 1/3",
#     "show board 1/4",
#     "show board 1/5",
#     "show board 1/6",
#     "show board 1/7",
#     "show board 1/8",
#     "show board 1/9",
#     "show board 1/11",
#     "show board 1/12",
#     "show board 1/13",
#     "show board 1/14",
#     "show board 1/15",
#     "show board 1/16",
#     "show board 1/17",
#     "show board 1/18",
#     "show board 1/19",
#     "show board 1/20",
#     "show board 1/21",
# ]


# ipList = ['10.174.0.1', '10.174.0.2'] 
# commands = ['dis ip int loop 0', 'dis int gi 1/1/1']

# ipList = ['10.174.136.61', ''] 
# commands = ['dis ip int loop 0', 'dis int gi 1/1/1']

# runTMS(user, password, ipList, commands)
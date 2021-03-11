from telnetlib import Telnet
import re
import time

IPSTR = '''10.174.169.173,
10.174.136.187
                ;;;
10.172.71.74

'''

COMMANDSTR = '''
show version
show ip interface brief 
show version

'''


def readIP(string):
    ipList = []
    templst = re.split(';|,|\n|\t', string)
    for ip in templst:
        if ip.strip(" , . ; \n \t "):
            ipList.append(ip.strip(" , . ; \n \t "))
    return ipList


def readCommands(string):
    commandList = []
    templst = string.split('\n')
    for line in templst:
        if line.strip(" , . ; \n \t "):
            commandList.append(line.strip(" , . ; \n \t "))
    return commandList


def to_bytes(line):
    return f"{line}\n".encode("utf-8")


def auth(ip, login, password):
    try:
        ne = Telnet(ip, timeout=5) 
        index, match, string = ne.expect([b'[Pp]assword', b'[Uu]sername', b'[Ll]ogin', b'[Uu]ser'], timeout=2)
        print(match)
        if index != 0:
            print('есть логин')
            ne.write(to_bytes(login))
            print('Логин введен')

        index, match, string = ne.expect([b'[Pp]assword]'], timeout=2)
        print('запрос пароля')
        ne.write(to_bytes(password))
        print('пароль введён \n\n')
        string = ne.expect([b'[>#]'], timeout=2)[2]
        neName = string.decode("utf-8").replace("\r\n", "\n").split('\n')[-1].strip('<>[]#')
        print(f'Выполнено вход на  {neName}')
        return ne, neName
    except EOFError:
        print(f'Не удалось подключиться к {ip}')


def runCommandList(ne, name, commands):
    print('run commands\n\n')
    result = []
    for command in commands:
        output = b''
        ne.write(to_bytes(command))
        while True:
            try:
                string = ne.expect([b'---- More ----', b'key to continue', to_bytes(name)], timeout=2)[2]
                lastLine = string.decode("utf-8").replace("\r\n", "\n").split('\n')[-1].strip('<>[]#')
                print(lastLine)
                if name != lastLine:
                    ne.write(to_bytes(' '))
                    output += string
                    time.sleep(0.2)
                else:
                    output += string
                    break
            except:
                break
        output = output.decode("utf-8")
        result.append(output.replace("\r\n", "\n"))

    for command in result:
        print(command+ '\n\n') #create log

    ne.close()



ipList = readIP(IPSTR)
commandList = readCommands(COMMANDSTR)
login = ''
password = 'ericsson'

ne, neName = auth("10.174.169.173", login, password)
runCommandList(ne, neName, readCommands(COMMANDSTR))

import PySimpleGUI as sg
import pickle
import re


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


def saveSett(login, password, iplist, commands):
    obj = {'login' : login,
           'password': password,
           'iplist' : iplist,
           'commands' : commands
          }
    with open('settings', 'wb') as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)


def loadSett():
    with open('settings', 'rb') as file:
        try:
            obj = pickle.load(file)
            login = obj['login']
            password = obj['password']
            iplist = obj['iplist']
            commands = obj['commands']
        except:
            login, password, iplist, commands = 'Login', 'Password', '', ''
        finally:
            print(login, password, iplist, commands)
            return login, password, iplist, commands


sg.theme('Dark')   # Add a touch of color)
# All the stuff inside your window.
login, password, iplist, commands = loadSett()


layout = [  [sg.Text('Login:', size=(15, None)), sg.Input(default_text=login, size=(85, 10), justification='center', key='login')],
            [sg.Text('Password:', size=(15, None)),sg.Input(default_text=password, size=(85, 10), justification='center', key='password', password_char="#")],
            
            [sg.Text('IP list (delimiters , ; tab enter):', size = (100, None), justification='center')],
            [sg.Multiline(iplist, key="IP_list", size=(100, 10), justification='left')],
            
            [sg.Text('Commands list (delimiter enter):', size = (100, None), justification='center')],
            [sg.Multiline(commands, key="commands_list", size=(100, 10), justification='left')],
            #buttons run & stop
            [sg.Button('Run', disabled=False, size=(47, None)), sg.Button('Stop', disabled=True, size=(47, None))],
            #output form
            [sg.Text('Logs:', size = (100, None), justification='center')],
            [sg.Output(size=(100, 20))],
            #buttons save & exit
            [sg.Button('Save parameters', visible=True, size=(47, None), ), sg.Button('Exit', visible=True, size=(47, None))]
        ]

# Create the Window
window = sg.Window('Telnet Mass Writer by nikita.baranov@nokia.com', icon='./moduls/img/icon.png').Layout(layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=100)
    if  event == 'Save parameters':	# Click Save button
        login =  values['login']
        password = values['password']
        iplist = values['IP_list']
        commands = values['commands_list']
        saveSett(login, password, iplist, commands)
#        break
    elif event == "Run": # Clik Run button
        window.find_element('Stop').update(disabled=False)
        window.find_element('Run').update(disabled=True)
        #thread = threading.Thread(target=checkLicense, args=(values["path"], window), daemon=True)
        #thread.start()
    elif event == "Stop":
        window.find_element('Stop').update(disabled=True)
        window.find_element('Run').update(disabled=False)
        print('process in stoped')
    elif event == sg.WIN_CLOSED or event == 'Exit' or None: # if user closes window or clicks Exit
        break


window.close()
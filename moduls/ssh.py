import paramiko
import time

def writeBytes(line):
    '''Format normal string to bytes type'''
    return f"{line}\n".encode("utf-8")

ipList = ['10.174.136.61'] 
user = 'NiVBaranov'
password = '8OSmerka'
commands = ['show alias', 'show time', 'show port 1/1/1 detail']

for ip in ipList:
    client = paramiko.SSHClient()
    # client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=password)
    
    for command in commands:
        chan = client.invoke_shell()
        chan.send(writeBytes(command))
        time.sleep(1)
        output = chan.recv(64)
        for line in output:
            print(line)
import socket
import ast
import sys

class bcolors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'


s = socket.socket()
s.connect(('127.0.0.1', 1234))

print(s.recv(1024).decode(encoding='utf8'))
data = input("-->")
while True:
    s.send(data.encode())
    tmp = s.recv(1024).decode()
    res = ast.literal_eval(tmp)
    for k, v in res.items():
        if type(k) == int or k == "Help" or k == "Error" or k == "Log" or k == "Location Error":
            if type(k) == int:
                print(bcolors.OK + "\nResult " + str(k +1))
                print("----------------------------\n")
                for i in v:
                    print(i + " : " + v[i])
                print("============================\n" + bcolors.RESET)
            elif k == "Log":
                print(bcolors.WARNING + "\nLog ")
                print("----------------------------\n")
                for i in v:
                    print(str(i) + " : " + v[i])
                print("============================\n" + bcolors.RESET)
            else:
                print(bcolors.FAIL + k)
                print("----------------------------\n")
                if len(v) == 1:
                    for i in v:
                        print(i + " : " + v[i])
                else:
                    print(v)
                print("============================\n" + bcolors.RESET)

    if k != "User Disconnected":
        data = input("-->")
    else:
        sys.exit()

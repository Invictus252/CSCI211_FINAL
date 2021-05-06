from pyowm.owm import OWM
import socket
import threading
import re
import sys


class TextColors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'


class WeatherArt:
    rain = "\n      __   _\n    _(  )_( )_\n   (_   _    _)\n  / /(_) (__)\n / / / / / /\n/ / / / / /"
    clouds = "\n      __   _\n    _(  )_( )_\n   (_   _    _)\n     (_) (__)\n"
    clear = "\n      ;   :   ;\n   .   \_,!,_/   ,\n    `.,'     `.,'\n     /         \\ \n~ -- :         : -- ~\n     \         /\n    ,'`._   _.'`.\n   '   / `!` \   `\n      ;   :   ;"


apiKey = 'INSERT KEY HERE'
owm = OWM(apiKey)
mgr = owm.weather_manager()
COUNTRY = 'US'

host = '127.0.0.1'
port = 1234
address = (host, port)
buffersize = 1024

socket_server = None
conn_pool = []

regex = re.compile(r"(\d{5})")
regex2 = re.compile(r"(\[.*?\])")

tmp = {}
tmp2 = {}
call_count = 0
call_log = {}

client = None
banner = TextColors.FAIL + "╦ ╦┌─┐┌─┐┌┬┐┬ ┬┌─┐┬─┐\n║║║├┤ ├─┤ │ ├─┤├┤ ├┬┘\n╚╩╝└─┘┴ ┴ ┴ ┴ ┴└─┘┴└─\n╔╗ ┬  ┬ ┬┌┐┌┌┬┐┌─┐┬─┐┌─┐┬─┐┌─┐┬ ┬┌┐┌┌┬┐\n╠╩╗│  │ ││││ ││├┤ ├┬┘│ ┬├┬┘│ ││ ││││ ││\n╚═╝┴─┘└─┘┘└┘─┴┘└─┘┴└─└─┘┴└─└─┘└─┘┘└┘─┴┘" + TextColors.RESET
options = "Enter Search Parameters.\nType help for instructions || bye to quit || {LOG} for search history"
weather_help = {"By ZipCode": "XXXXX", "By City" : "[CITY-NAME]", "Multiple" : "Enter as a spaced sequence\nXXXXX [CITY-NAME] xxxxx [ANOTHER-CITY]"}

def init():
    global socket_server
    socket_server = socket.socket()
    # reuse port or allow reconnect
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind(address)
    socket_server.listen(5)
    print(banner)
    print("Weather Blunderground is listening...")


def accept_client():
    global client, conn_pool
    while True:
        client, addr = socket_server.accept()
        # Add a connection to pool
        conn_pool.append(client)
        print("+ Client : Current Count is {}".format(len(conn_pool)))
        mythread = threading.Thread(target=message_handle, args=(client, addr))
        mythread.start()


def message_handle(client, addr):
    welcome = banner + TextColors.OK + "\nWelcome " + str(addr) + ". You have connected to the Blunderground.\n" + TextColors.RESET + TextColors.WARNING + options + "\n" + TextColors.RESET
    client.send(welcome.encode())
    while True:
        try:
            getWeather(client,addr)
        except:
            loc_error = {'Location Error': 'Invalid location data sent'}
            client.send("{}".format(loc_error).encode())
            continue


def getWeather(client,addr):
    global tmp, tmp2, call_count, call_log
    data = client.recv(buffersize).decode()  # byte
    if data:
        matches = re.findall(regex, data)
        city_matches = re.findall(regex2, data)
        if matches:
            for i in range(0, len(matches)):
                weather = mgr.weather_at_zip_code(matches[i], COUNTRY).weather
                temp_dict_fahrenheit = weather.temperature('fahrenheit')
                if weather.status == "Rain":
                    tmp['Currently'] = WeatherArt.rain
                if weather.status == "Clouds":
                    tmp['Currently'] = WeatherArt.clouds
                if weather.status == "Clear":
                    tmp['Currently'] = WeatherArt.clear
                buildOutput(i, matches[i], weather.status, weather.detailed_status, str(temp_dict_fahrenheit['temp']),
                            str(weather.humidity))
                call_count += 1
                call_log[call_count] = matches[i]
        if city_matches:
            for i in range(0, len(city_matches)):
                city = city_matches[i]
                weather = mgr.weather_at_place(city[1:-1] + "," + COUNTRY).weather
                temp_dict_fahrenheit = weather.temperature('fahrenheit')
                if weather.status == "Rain":
                    tmp['Currently'] = WeatherArt.rain
                if weather.status == "Clouds":
                    tmp['Currently'] = WeatherArt.clouds
                if weather.status == "Clear":
                    tmp['Currently'] = WeatherArt.clear
                buildOutput(i + len(matches), city[1:-1], weather.status, weather.detailed_status,
                            str(temp_dict_fahrenheit['temp']), str(weather.humidity))
                call_count += 1
                call_log[call_count] = city[1:-1]
        if "bye" in data:
            tmp2["User Disconnected"] = "Goodbye"
            client.send("{}".format(tmp2).encode())
            conn_pool.remove(client)
            print("- Client: Current Count is {}".format(len(conn_pool)))
            sys.exit()
        if "help" in data:
            tmp2["Help"] = weather_help
        if "{LOG}" in data:
            tmp2["Log"] = call_log
        if not matches and not city_matches and not "bye" in data and not "help" in data and not "{LOG}" in data:
            tmp2["Error"] = {'Input': data}
        client.send("{}".format(tmp2).encode())
        print("Scans Ran: {}".format(call_count))
        tmp2 = {}


def buildOutput(ctr, loc, stat, dstat, temp, hum):
    global tmp, tmp2
    tmp['Location'] = loc
    tmp['Status'] = stat
    tmp['Detailed Status'] = dstat
    tmp['Temp'] = str(temp) + " \u00B0"
    tmp['Humidity'] = str(hum) + "%"
    tmp2[ctr] = tmp
    tmp = {}


if __name__ == "__main__":
    init()
    this_thread = threading.Thread(target=accept_client())
    this_thread.start()






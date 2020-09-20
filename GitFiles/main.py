#Created by Dom Devereux
#Version 0.1
#Python 3.8
#UTF-8

import http.server
import socketserver
import re
import requests
import subprocess
import time

PORT = 6969
IP = "127.0.0.1"

versionList = []

#Web page dic structure 'Label name' : [<webpage>, <key phrase to search for>, <version number range>]

webPageList = {
    'Grand Ma 2' : ["https://www.malighting.com/downloads/products/grandma2/", "Version ....... ", [7, -1]],
    'Avolites' : ["https://www.avolites.com/software/downloads/titan-pc-suite", "Titan PC Suite v....", [16, 20]],
    'Grand Ma 3' : ["https://www.malighting.com/downloads/products/grandma3/", "Version ....... ", [7, -1]],
    'ETC' : ["https://www.etcconnect.com/Products/Consoles/Eos-Family/?LangType=1033", "Eos Family ..... for PC", [11, -6]],
}

def internetTest():
    try:
        subprocess.check_output("ping -n 2 8.8.8.8", shell=True) #Pings google dns server to check internet
        return 0
    except subprocess.CalledProcessError:
        return 1

def genrateVersionList(dic):
    for i in webPageList:
        page = requests.get(webPageList.get(i)[0]) #pulls html page from web address
        page = page.content.decode()
        check = re.search(webPageList.get(i)[1], page) #searchs for key phrase in html page
        try:
            check = list(check.span())
        except AttributeError:
            return "Error"
        check = page[check[0]:check[1]]
        versionList.append(check[webPageList.get(i)[2][0]:webPageList.get(i)[2][1]]) #adds the version to the version list

def generateHtml():
    f = open("index.html", "r")
    htmlText = f.read()
    f.close()
    cnt = 0
    for i in range(len(versionList)):
        search = re.search("{ver" + str(i) + "}", htmlText) #Find var to be replaced
        location = list(search.span())
        startStr = htmlText[:location[0]]
        endStr = htmlText[location[1]:]
        htmlText = startStr + versionList[i] + endStr
    for i in webPageList:
        search = re.search("{var" + str(cnt) + "}", htmlText) #Find var to be replaced
        location = list(search.span())
        startStr = htmlText[:location[0]]
        endStr = htmlText[location[1]:]
        htmlText = startStr + i + endStr
        cnt = cnt + 1
    return htmlText #return updated html page

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self): #defines what happens when a get request is made
        if self.path == "/":
            text = generateHtml()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(str.encode(text))
    
    def log_message(self, format, *args): #Nulls the output
        return

print("Checking files and settings")
try:
    f = open("index.html", "r") #checks that the index page is present
    f.close()
except FileNotFoundError:
    print("index file can't be found")
    input("Press Enter to exit")
    exit()

print("Checking Internet connection")
if internetTest() == 1:
    print("Internet error, please check your connection/firewall and try again")
    input("Press Enter to exit")
    exit()
print("Scraping web for versions")
genrateVersionList(webPageList)

with socketserver.TCPServer((IP, PORT), Handler) as httpd:
    print("Server started")
    print("Connect at ", "http://" + IP + ":" +str(PORT))
    try:
        httpd.serve_forever() #Starts server
    except KeyboardInterrupt:
        print("Server Stopped Keyboard Interrupt")
    else:
        print("Fatal error please try again")

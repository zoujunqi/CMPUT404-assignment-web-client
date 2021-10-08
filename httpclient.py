#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def get_url_info(self, url):
        # get the information from the input url
        parse_result = urlparse(url)
        port = parse_result.port
        path = parse_result.path
        if not port:
            port = 80
        if path == '':
            path = '/'
        return port, parse_result.hostname, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        splited_data = data.split('\r\n\r\n')
        if len(splited_data) > 1:
            return splited_data[1]
        else:
            return ''
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # get the info from input url
        port, host, path = self.get_url_info(url)

        # Send request to server
        self.connect(host, port)
        request = "GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n".format(path=path, host=host)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        # Get info needed to generate response and display
        header = self.get_headers(response)
        code = self.get_code(response)
        body = self.get_body(response)
        print(header, code, body, sep='\n')

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Check if args is given
        if args:
            args_body = urlencode(args)
        else:
            args_body = ''

        # Get info from url
        port, host, path = self.get_url_info(url)

        # Send request
        self.connect(host, port)
        request = "POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {length}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{body}".format(path=path, host=host, length=len(args_body), body=args_body)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        # Get info needed to generate response and display
        header = self.get_headers(response)
        code = self.get_code(response)
        body = self.get_body(response)
        print(header, code, body, sep='\n')

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

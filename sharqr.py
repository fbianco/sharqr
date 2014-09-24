#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2014 François Bianco <francois.bianco@skadi.ch>


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

See COPYING file for the full license.
"""

import os
import argparse
import qrcode
import mimetypes
import netifaces
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer, socket

PROTOCOL = 2 # From socket.h in Linux, IPv4 = 2, IPv6 = 10
FILENAME = None # Hack to secure that request is bound to only the selected file

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):

    def send_head(self):
        """Reimplement GET & HEAD to serve the requested file."""

        global FILENAME # Hack to secure that only the requested file is served

        path = self.translate_path(self.path)
        if os.path.basename(self.path) != FILENAME or os.path.isdir(path):
            self.send_error(403, "Forbidden")
            return None

        f = None
        ctype = self.guess_type(path)
        if ctype.startswith('text/'):
            mode = 'r'
        else:
            mode = 'rb'
        try:
            f = open(path, mode)
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-Disposition", "attachment; filename=\"{}\"".format(FILENAME))
        self.send_header("Content-Description", "File Transfer")
        self.send_header("Content-type", ctype)
        self.end_headers()
        return f

class CustomHTTPServer(HTTPServer):

    def verify_request(self, request, client_address):
        # TODO We could add a filter on client_address to enhance the security
        #   If not client_address in addresses_list:
        #       self.send_error(403, "Forbidden")
        #   # Method might not be available in server
        #       return False # Will block the request
        return True

def main():
    global FILENAME

    interfaces = netifaces.interfaces()
    try:
        interfaces.remove('lo')
    except ValueError:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="File to share")
    parser.add_argument("-p", "--port", help="Server port", type=int, default=9999)
    parser.add_argument("-n", "--num", help="Number of requests, default infinite (negative will be infinite)", type=int, default=-1)
    parser.add_argument("--interface", help="Define on which interface to serve the file", choices=interfaces)
    parser.add_argument("-c", "--console", help="Print QR code in terminal instead of using GUI", action='store_true')
    args = parser.parse_args()

    if not args.interface:
        args.interface = interfaces[0] # first non loopback

    address = netifaces.ifaddresses(args.interface)[PROTOCOL][0]['addr']

    FILENAME = os.path.basename(args.filename)
    os.chdir(os.path.dirname(os.path.abspath(args.filename)))
    try:
        s = CustomHTTPServer((address,args.port), CustomHTTPRequestHandler)
    except socket.error, e:
        print "Error starting the server, try changing port."
        print e
        return

    qr = qrcode.QRCode()
    qr.add_data('http://{0}:{1}/{2}'.format(address, args.port, os.path.basename(args.filename)))
    if args.console:
        qr.make()
        qr.print_tty()
    else:
        qr.make_image().show()

    try:
        while args.num!=0:
            s.handle_request()
            args.num-=1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

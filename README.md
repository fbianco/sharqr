sharqr
======

Shark'r (or SharQR): serve a local file via http over network and show its
adress in a QrCode.

Its usefull for sharing quickly a file to a smartphone running a barcode reader,
but might also be used to share a file to an other computer within the same
network.

Usage
-----
```
sharqr.py [-h] [-p PORT] [-n NUM] [--interface {eth0,wlan0}] [-c] filename

positional arguments:
filename              File to share

optional arguments:
-h, --help            show this help message and exit
-p PORT, --port PORT  Server port
-n NUM, --num NUM     Number of requests, default infinite (negative will be
                        infinite)
--interface {eth0,wlan0}
                        Define on which interface to serve the file
-c, --console         Print QR code in terminal instead of using GUI
```

**Note**: interface will be defined from your local available interfaces.

Example
-------

`python sharqr.py --interface eth0 -p 8008 -n 1 -c ~/hello.world`

Will show a Qr Code directly in current tty and share the file *hello.world*
through interface eth0 on port 8008 for only one request.

Requires
--------
qrcode and netifaces

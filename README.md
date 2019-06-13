# serv.py

The `python -m http.server` is handy but lack of function to asign specific directory.

So, I've built this small toy called `serv.py` for self-use.

## Usage

```
 ➜  python serv.py -h
usage: serv.py [-h] [-d DIR] [-p PORT] [-b ADDRESS]

A Simple Web Server.

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Specify alternate dir [default: web]
  -p PORT, --port PORT  Specify alternate port [default: 8000]
  -b ADDRESS, --bind ADDRESS
                        Specify alternate bind address [default: all
                        interfaces]
```

## Details

- Modify method `translate_path()` in class `SimpleHTTPRequestHandler` to support arbitrary directories. 

- Modify initial function of class `HTTPServer` to pass parameters of root directory.


## Todo

- A human version of listing dirs.
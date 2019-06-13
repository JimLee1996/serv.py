# serv.py

The `python -m http.server` is handy but lack of function to asign specific directory.

So, I've built this small toy called `serv.py` for self-use


## Details

- Modify method `translate_path()` in class `SimpleHTTPRequestHandler` to support arbitrary dir. 

- Modify initial function of class `HTTPServer` to pass parameters of directory.


## Todo

- A human version of listing dirs.
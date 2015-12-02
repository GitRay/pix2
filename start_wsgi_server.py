import sys
from wsgiref.simple_server import make_server
sys.path.append('cgi-bin')
from Application import Application

app = Application()

httpd = make_server('', 8000, app)
print("Serving on port 8000...")
httpd.serve_forever()
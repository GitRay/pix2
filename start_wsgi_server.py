import sys
from wsgiref.simple_server import make_server
sys.path.append('bin')
import wsgi

httpd = make_server('', 8000, wsgi.application)
print("Serving on port 8000...")
httpd.serve_forever()
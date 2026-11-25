"""
Servidor local para ver la web explicativa.

Uso (desde la carpeta del proyecto):
    python servidor.py            # puerto 8000
    python servidor.py 8080       # otro puerto

Solo usa la librería estándar de Python 3. Ctrl+C para detenerlo.
"""

import functools
import http.server
import os
import socketserver
import sys
import webbrowser

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web-explicativa")
PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Servidor(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    manejador = functools.partial(http.server.SimpleHTTPRequestHandler, directory=CARPETA)
    with Servidor(("127.0.0.1", PUERTO), manejador) as servidor:
        url = f"http://localhost:{PUERTO}/"
        print(f"Web explicativa en {url}  (Ctrl+C para detener)")
        webbrowser.open(url)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    main()

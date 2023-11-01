from werkzeug.serving import make_server

class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        log.info('starting server')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def start_server():
    global server
    app = flask.Flask('myapp')
    # App routes defined here
    server = ServerThread(app)
    server.start()
    log.info('server started')

def stop_server():
    global server
    server.shutdown()
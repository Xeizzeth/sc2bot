import os.path
import string
import random
import uuid
import webbrowser

from logging import getLogger

import tornado.escape
import tornado.web
import tornado.websocket

logger = getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler), (r"/logsocket", LogSocketHandler)]
        settings = dict(
            cookie_secret=''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10, 100))),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class LogSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    messages = []

    def get_compression_options(self):
        return {}

    def open(self):
        LogSocketHandler.clients.add(self)
        if len(LogSocketHandler.clients) == 1:
            for message in LogSocketHandler.messages:
                LogSocketHandler.send_updates(message)

    def on_close(self):
        LogSocketHandler.clients.remove(self)

    async def on_message(self, message):
        logger.info(f"got message {message}")
        parsed = tornado.escape.json_decode(message)
        await self.post_message(parsed["body"])

    @classmethod
    def send_updates(cls, message):
        logger.info(f"sending message to {len(cls.clients)} clients")
        for client in cls.clients:
            try:
                message_dict = {"id": str(uuid.uuid4()), "body": message}
                message_dict["html"] = tornado.escape.to_basestring(
                    client.render_string("message.html", message=message_dict)
                )
                client.write_message(message_dict)
            except:
                logger.error("Error sending message", exc_info=True)

    @classmethod
    async def post_message(cls, message):
        cls.messages.append(message)
        cls.send_updates(message)


def start_server():
    if not LogSocketHandler.clients:
        app = Application()
        app.listen(8888)
        webbrowser.open("http://localhost:8888")

from typing import ClassVar, List, Optional
import asyncio
import threading

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, SecretStr
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging

class EmailServiceAlreadyInitialized(Exception):
    pass

class EmailServiceMissingArguments(Exception):
    pass

class EmailServiceNotInitialized(Exception):
    pass

class DummyEmailService:
    _smtp_controller: ClassVar[Optional[Controller]] = None
    _event_loop: ClassVar[Optional[asyncio.AbstractEventLoop]] = None
    _loop_thread: ClassVar[Optional[threading.Thread]] = None
    _fm: ClassVar[Optional[FastMail]] = None

    @classmethod
    def initialize(cls):
        if cls._fm is not None:
            raise EmailServiceAlreadyInitialized()

        cls._smtp_controller = cls._start_local_smtp_server()
        print("DummyEmailService: smtp server initialized")

        cls._start_event_loop()
        print("DummyEmailService: event loop started")

        conf = ConnectionConfig(
            MAIL_USERNAME = "dummy_username",
            MAIL_PASSWORD = SecretStr("dummy_password"),
            MAIL_FROM = "test@dummymailservice.com",
            MAIL_PORT = 1025,
            MAIL_SERVER = "localhost",
            MAIL_FROM_NAME= "Patient Registration App",
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS = False,
            USE_CREDENTIALS = True,
            VALIDATE_CERTS = False
        )

        cls._fm = FastMail(conf)
        print("DummyEmailService: FastMail instance initialized")

    @classmethod
    def shutdown(cls):
        if cls._fm is not None:
            cls._fm = None
            print("DummyEmailService: FastMail instance closed")

        if cls._event_loop is not None and cls._loop_thread is not None:
            cls._event_loop.call_soon_threadsafe(cls._event_loop.stop)
            cls._loop_thread.join()
            cls._event_loop = None
            print("DummyEmailService: event loop stopped")

        if cls._smtp_controller is not None:
            cls._smtp_controller.stop()
            cls._smtp_controller = None
            print("DummyEmailService: smtp server shut down")

    @classmethod
    def send_in_background(cls, subject: str, recipients: List[EmailStr], body: str):
        """Send email as a background task."""
        if cls._fm is None or cls._event_loop is None:
            raise EmailServiceNotInitialized()

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=MessageType.plain
        )

        asyncio.run_coroutine_threadsafe(cls._fm.send_message(message), cls._event_loop)
        print(f"DummyEmailService: created task for sending {subject} to {recipients}")

    @classmethod
    def _start_event_loop(cls):
        def run_event_loop():
            cls._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._event_loop)
            cls._event_loop.run_forever()

        cls._loop_thread = threading.Thread(target=run_event_loop, daemon=True)
        cls._loop_thread.start()

    @classmethod
    def _start_local_smtp_server(cls) -> Controller:
        """Starts a local aiosmtpd server on a separate thread."""
        handler = Debugging()
        controller = Controller(handler, hostname='localhost', port=1025)
        
        thread = threading.Thread(target=controller.start, daemon=True)
        thread.start()

        return controller

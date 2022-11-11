import json
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List


@dataclass
class Sender:
    email: str
    smtp_host: str
    smtp_port: int
    password: str


class Stan:
    def __init__(self):
        pass

    def render_jinja_template(self, template_path: str, **kwargs) -> str:
        templateLoader = FileSystemLoader(searchpath="./templates")
        jinja_env = Environment(
            loader=templateLoader, autoescape=select_autoescape(["html"])
        )
        template = jinja_env.get_template(template_path)
        html = template.render(**kwargs)
        return html

    def load_sender_settings(self, sender_data: dict) -> Sender:
        """
        Loads required data to send an email.
        email, smtp host, smtp port and password
        """

        sender = Sender(**sender_data)
        return sender

    def load_senders_from_json(self, file_path: str) -> List[Sender]:
        """
        Loads sender data from json file and converts it to list of `Sender`s.
        Each record in json file should contain email, smtp_host, smtp_port and password.
        """
        file = open(file_path)
        data = json.load(file)
        return [self.load_sender_settings(sender) for sender in data]

    def prepare_message_content(self, template_path: str, sender_email: str, recipient_email: str) -> EmailMessage:
        """Prepare message based on template file."""

        html = self.render_jinja_template(template_path, gender="male")

        msg = EmailMessage()
        msg["Subject"] = "Test email"
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.set_content(html, subtype="html")
        return msg

    def send_message(
        self, sender: Sender, recipients: List[str]
    ) -> None:
        """Use sender smtp to send a message to list of recipients."""
                
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            sender.smtp_host, sender.smtp_port, context=context
        ) as server:
            server.login(sender.email, sender.password)
        
            for recipient in recipients:
                msg = self.prepare_message_content("test_msg.html", sender.email, recipient)
            server.send_message(msg, sender.email, recipients)


if __name__ == "__main__":
    stan = Stan()
    senders = stan.load_senders_from_json("senders.json")
    recipients = ["jakubmatyszewski1@gmail.com"]
    for sender in senders:
        stan.send_message(sender, recipients)

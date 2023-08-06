import smtplib
from email.mime.text import MIMEText


class Email(object):
    def __init__(
        self,
        host,
        port,
        sender,
        password,
        receiver,
    ):
        self.host = host
        self.port = port
        self.sender = sender
        self.password = password
        self.receiver = receiver

    def send_email(self, message):

        message["From"] = self.sender
        message["To"] = self.receiver

        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        server.login(self.sender, self.password)
        server.sendmail(message["From"], message["To"], message.as_string())
        server.quit()

    def send_release_email(self, project, tag):
        assert project.has_file("NEWS.rst")

        # The contents of NEWS.rst will be the email body
        with open(project.file_path("NEWS.rst"), "r") as input:
            # Create an html message that contains preformatted text (which is
            # displayed in a fixed-width font for better readability)
            message = MIMEText("<pre>" + input.read() + "</pre>", "html")
        message["Subject"] = "{}: Version {} released!".format(project.name, tag)
        self.send(message)

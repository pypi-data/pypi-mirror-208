import json
import slack
import yagmail
from twilio.rest import Client as twilio_client

class Messenger:
    def __init__(self, message):
        self.message = message

    def send_to_slack(
            self,
            token: str,
            channel: str,
            image: str = None,
            image_title: str = None,
    ) -> None:
        """
        Send message to slack channel
        """
        client = slack.WebClient(token=token)
        if image and 'http' not in image:
            client.files_upload(channels=channel, file=image,
                                initial_comment=self.message, title=image_title)
            return
        elif image and 'http' in image:
            title = image_title if image_title else ''
            attachments = [{"title": title, "image_url": image}]
        elif not image:
            attachments = None

        client.chat_postMessage(
            channel=channel,
            text=self.message,
            attachments=attachments
        )

    def send_email(
            self,
            title: str,
            receiver_email: str,
            sender_email: str,
            sender_pwd: str,
            sender_host: str,
            sender_port=465,
    ) -> None:
        """
        send message to an email address
        """
        yag = yagmail.SMTP(
            user=sender_email,
            password=sender_pwd,
            host=sender_host,
            port=sender_port)
        yag.send(receiver_email, title, self.message)

    def send_sms(
            self,
            twilio_sid: str,
            twilio_token: str,
            from_: int,
            to: int,
    ) -> None:
        """
        send SMS using twilio api
        """
        print("Sending sms:", self.message)
        client = twilio_client(twilio_sid, twilio_token)
        client.api.account.messages.create(
            to=to,
            from_=from_,
            body=self.message
        )


if __name__ == '__main__':
    with open('secret.json') as f:
        secrets = json.load(f)
    Messenger('test').send_to_slack(
        token=secrets['slack_oath'],
        channel=secrets['slack_channel'])

import requests
import src.flaskapp.config as config


def send_email(to, subject, body):
    """Api to send emails from the app to app users via the Mailgun Platform

    Args:
        to : (list of str) list of emails to send to
        subject: (str) text for the subject of the email
        body: (str) text for the body of the email

    Return:
        response object from mailgun
    """
    return requests.post(
        f"https://api.mailgun.net/v3/{config.DOMAIN_NAME}/messages",
        auth=("api", config.MAILGUN_API_KEY),
        data={
            "from": f"TeamRU <mailgun@{config.DOMAIN_NAME}>",
            "to": to,
            "subject": subject,
            "text": body,
        },
    )

import os
from typing import Union, Any
import boto3
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError
from xm_ai.time_utils import today


def send_email_w_attachment(sender: str, recipients: list[str], subject: str, filepath: str, filename: str) -> Union[
    tuple[str, Any], Any]:
    BODY_TEXT = f"See attached Excel file for the Trial Report."  # email body for recipients with non-HTML email clients
    BODY_HTML = f"""
        <html>
            <head></head>
            <body>
                <h1>
                    {today} Trial Report
                </h1>
                <p>
                    {BODY_TEXT}
                </p>
            </body>
        </html>
    """  # HTML body of the email

    client = boto3.client('ses', region_name='us-east-2')

    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sender
    msg_body = MIMEMultipart('alternative')
    # noinspection PyTypeChecker
    textpart = MIMEText(BODY_TEXT.encode("utf-8"), 'plain', "utf-8")
    # noinspection PyTypeChecker
    htmlpart = MIMEText(BODY_HTML.encode("utf-8"), 'html', "utf-8")
    #  Add the text and HTML parts to the child container
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    att = MIMEApplication(
        open(filepath, 'rb').read())  # define the attachment part and encode it using MIMEApplication.
    att.add_header('Content-Disposition', 'attachment', filename=filename)

    if os.path.exists(filepath) is False:
        raise FileNotFoundError("File does not exist")

    msg.attach(msg_body)  # attach the multipart/alternative child container to the multipart/mixed parent container
    msg.attach(att)  # attach the attachment to the parent container

    try:
        response = client.send_raw_email(
            Source=msg['From'],
            Destinations=recipients,
            RawMessage={
                'Data': msg.as_string(),
            }
        )
    except ClientError as err:
        return err.response['Error']['Message']
    else:
        return "Email sent! Message ID:", response['MessageId']

#!/usr/bin/env python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ySQL
import zQueries


def compile_email(from_address, to_address, files, businessdate):

    # todo pull in 'NA' cntpryids
    results = ySQL.get_sql_fetchall(zQueries.sql_get_missing_cntrprty(businessdate), 'OPDS')

    # If files or cntrprtys are missing then send email
    if files or results:
        html = """\
                    <html>
                      <head></head>
                      <body>
                        <p> """
        # Missing Files
        if files:
            html = html + """<br><br>The following file(s) were not processed<br><br> """ + '<br><br>'.join(filter(None, files))
        # Missing Cntprty
        if results:
            html = html + """<br><br>The cntrprty(s) could not locate FSA information<br><br> """ + str([" ".join(x) for x in results])

        html = html + """   </p>
                         </body>
                       </html> """
        # Send
        send_email([from_address], [to_address], html)


def send_email(from_address, to_address, body):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "TEST"
    msg['From'] = ", ".join(from_address)
    msg['To'] = ", ".join(to_address)

    # Create the body of the message (a plain-text and an HTML version).
    # text = body
    html = body

    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('cnjimc01')
    # sendmail function takes 3 arguments: sender's address, recipient's address and message to send
    s.sendmail(from_address, to_address, msg.as_string())
    s.quit()
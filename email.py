import click

import smtplib
from email.mime.multipart import MIMEMultipart

@click.command()
@click.option('--sender',help="from who",default='test@gmail.com')
@click.option('--receive',help="to who")
@click.option('--content',help="what")
@click.option('--annex')


def main():
    msg=MIMEMultipart()
    msg['From']=
    msg['To']=
    msg['Subject']
    
    msg.attach(MIMEText(u'Hi all,\n\n    This is a test email for you.\n\nBest','plain','utf-8'))

if __name__ == "main()":
    main()
    
#MIMEText, MIMEImage, MIMEMultipart


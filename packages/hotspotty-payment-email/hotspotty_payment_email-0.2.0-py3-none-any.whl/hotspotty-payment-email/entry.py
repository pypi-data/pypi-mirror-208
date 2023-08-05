import argparse
from datetime import date
from email.message import EmailMessage

import pandas as pd
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from jinja2 import Template
from requests import HTTPError
import logging
logger = logging.getLogger(__name__)

def send_email(*, service: Resource, subject: str, template_path: str, recipient_email: str, start_date: str, end_date: str, name: str, wallet: str, amount_iot: float, amount_hnt: float, draft: bool = True):

    with open(template_path, 'r') as f:
        template = Template(f.read())

    context = {
        'name': name,
        'start_date': start_date,
        'end_date': end_date,
        'wallet_address': wallet,
        'amount_hnt': amount_hnt,
        'amount_iot': amount_iot
    }
    body = template.render(context)

    message = EmailMessage()
    message.set_content(body, 'html')
    message['to'] = recipient_email
    message['subject'] = subject
    create_message = {
        'message': {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
        }
    }

    try:
        if draft:
            service.users().drafts().create(userId="me", body=create_message).execute()
        else:
            message = service.users().messages().send(userId="me", body=create_message).execute()
    except HTTPError as error:
        logger.error(F'The following error occurred whe trying to send email to {recipient_email}: {error}')
        message = None
    return message

def process_reports(reports: list[str], delimiter: str) -> pd.DataFrame:
    data = pd.DataFrame()
    for report in reports:
        data = pd.concat([data, pd.read_csv(report, delimiter=delimiter)])

    result = pd.DataFrame(columns=['email', 'name', 'wallet', 'amount_hnt', 'amount_iot'])

    emails = set(data['email'].tolist())
    for email in emails:
        data_by_email = data[data['email'] == email]
        if (data_by_email['walletAddress_blockchain'] != 'solana').any():
            raise ValueError('There are some rows with walletAddress_blockchain != solana')
        new_row = {
            'email': email,
            'name': data_by_email['name'].iloc[0],
            'wallet': data_by_email['walletAddress_walletAddress'].iloc[0],
            'amount_iot': data_by_email[data_by_email['currency'] == 'iot']['amount'].sum(),
            'amount_hnt': data_by_email[data_by_email['currency'] == 'hnt']['amount'].sum()
        }
        result.loc[len(result)] = new_row

    return result

def main():
    parser = argparse.ArgumentParser(
        description='Send payment notification emails to users inside some contact commissions reports files exported from Hotspotty.')
    parser.add_argument('--credentials', type=str, required=True,
                        help='Path to the secret file exported from google cloud platform to authorize the tool to send emails. See README.md for more details.')
    parser.add_argument('--template', type=str, required=True,
                        help='Path to a html file representing email template to use to build emails. It can use the following variables: name, start_date, end_date, wallet_address, amount_hnt, amount_iot.')
    parser.add_argument('--reports', type=str, nargs='+', required=True,
                        help='Path to one ore more commissions reports. In order to be processable they must have these columns: email, name, walletAddress_blockchain, walletAddress_walletAddress, currency, amount.')
    parser.add_argument('--subject', type=str, help='Subject of the emails to send.')
    parser.add_argument('--start', type=date.fromisoformat, help='Specify a start date for the report in ISO format (YYYY-MM-DD)')
    parser.add_argument('--end', type=date.fromisoformat, help='Specify a end date for the report in ISO format (YYYY-MM-DD)')
    parser.add_argument('--delimiter', type=str, default=',', help='Delimiter used in the reports files.')
    parser.add_argument('--draft', type=bool, default=True, help='If true, the email will be created as a draft.')
    args = parser.parse_args()
    credentials: str = args.credentials
    reports: list[str] = args.reports
    subject: str = args.subject
    template: str = args.template
    start: date = args.start
    end: date = args.end
    delimiter: str = args.delimiter
    draft: bool = args.draft

    result = process_reports(reports, delimiter)

    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
    flow = InstalledAppFlow.from_client_secrets_file(credentials, SCOPES)
    creds = flow.run_local_server(port=0)
    service: Resource = build('gmail', 'v1', credentials=creds)
    for index, row in result.iterrows():
        send_email(
            service=service,
            template_path=template,
            subject=subject,
            recipient_email=row['email'],
            draft=draft,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            name=row['name'],
            wallet=row['wallet'],
            amount_iot=row['amount_iot'],
            amount_hnt=row['amount_hnt'],
        )


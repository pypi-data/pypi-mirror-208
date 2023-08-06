from datetime import date
from email.message import EmailMessage
from typing import List

import click
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from jinja2 import Template
from pandas import DataFrame, read_csv, concat
from requests import HTTPError
import logging

logger = logging.getLogger(__name__)


def send_email(*, service: Resource, subject: str, template_path: str, recipient_email: str, start_date: str,
               end_date: str, name: str, wallet: str, amount_iot: float, amount_hnt: float, draft: bool = True):
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
            click.echo(f"Preparing draft e-mail for: {recipient_email} - {name}")
            service.users().drafts().create(userId="me", body=create_message).execute()
        else:
            click.echo(f"Sending e-mail to: {recipient_email} - {name}")
            message = service.users().messages().send(userId="me", body=create_message).execute()
    except HTTPError as error:
        logger.error(F'The following error occurred whe trying to send email to {recipient_email}: {error}')
        message = None
    return message


def process_reports(reports: List[str], delimiter: str) -> DataFrame:
    data = DataFrame()
    for report in reports:
        data = concat([data, read_csv(report, delimiter=delimiter)])

    result = DataFrame(columns=['email', 'name', 'wallet', 'amount_hnt', 'amount_iot'])

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


@click.command(
    help='Send payment notification emails to users inside some contact commissions reports files exported from Hotspotty.')
@click.option('--credentials', type=str, required=True,
              help='Path to the secret file exported from google cloud platform to authorize the tool to send emails. See README.md for more details.')
@click.option('--template', type=str, required=True,
              help='Path to a html file representing email template to use to build emails. It can use the following variables: name, start_date, end_date, wallet_address, amount_hnt, amount_iot.')
@click.option('-r', '--report', type=str, multiple=True, required=True,
              help='Path to one ore more commissions reports. In order to be processable they must have these columns: email, name, walletAddress_blockchain, walletAddress_walletAddress, currency, amount.')
@click.option('--subject', type=str, help='Subject of the emails to send.')
@click.option('--start', type=date.fromisoformat,
              help='Specify a start date for the report in ISO format (YYYY-MM-DD)')
@click.option('--end', type=date.fromisoformat,
              help='Specify a end date for the report in ISO format (YYYY-MM-DD)')
@click.option('--delimiter', type=str, default=',', help='Delimiter used in the reports files.')
@click.option('--draft', type=bool, default=True, help='If true, the email will be created as a draft.')
def cli(credentials: str, report: List[str], subject: str, template: str, start: date, end: date, delimiter: str,
        draft: bool):

    result = process_reports(report, delimiter)

    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
    flow = InstalledAppFlow.from_client_secrets_file(credentials, SCOPES)
    creds = flow.run_local_server(port=0)
    service: Resource = build('gmail', 'v1', credentials=creds)

    if draft:
        click.echo(f"Preparing {len(result)} drafts...")
    else:
        click.echo(f"Sending {len(result)} e-mail...")

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

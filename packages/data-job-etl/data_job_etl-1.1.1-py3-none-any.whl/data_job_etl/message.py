from __future__ import print_function

import pandas as pd
from pathlib import Path
from datetime import datetime

from data_job_etl.config.etl_logger import logger

import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from data_job_etl.extract.extract import Extractor

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class Messenger:

    def __init__(self):
        self.logger = logger
        self.extractor = Extractor()
        self.credentials_file = Path(__file__). parent / 'credentials.json'
        self.last_scraped_date = None

    def message(self):
        jobs = self.extract_recent_ranked_jobs()
        print(jobs.info())
        text, html = self.format_simple_message(jobs)
        self.send_message(text, html)

    def extract_recent_ranked_jobs(self):
        last_scraped_date_query = """
            SELECT created_at
            FROM raw_jobs
            ORDER BY created_at DESC limit 1;
        """
        last_scraped_date = self.extractor.extract_query(last_scraped_date_query)
        self.last_scraped_date = last_scraped_date.loc[0, 'created_at']
        query = f"""
            SELECT * FROM relevant
            WHERE created_at = '2023-05-03'
            ORDER BY rank DESC;
        """
        recent_ranked_jobs = self.extractor.extract_query(query)
        return recent_ranked_jobs

    def format_simple_message(self, jobs):
        text = "Hi, here are new jobs for you."

        table = """<tr>
                <td>Rank</td>
                <td>Id</td>
                <td>Created at</td>
                <td>Remote</td>
                <td>Experience</td>
                <td>Title</td>
                <td>Company</td>
                <td>Stack</td>
                <td>Location</td>
            </tr>
            """
        for i in range(len(jobs)):
            row = f"""<tr>
                <td>{round(jobs.loc[i, 'rank']*100, 2)}</td>
                <td>{jobs.loc[i, 'id']}</td>
                <td>{jobs.loc[i, 'created_at']}</td>
                <td>{jobs.loc[i, 'remote']}</td>
                <td>{jobs.loc[i, 'experience']}</td>
                <td>{jobs.loc[i, 'title']}</td>
                <td>{jobs.loc[i, 'company']}</td>
                <td>{jobs.loc[i, 'stack']}</td>
                <td>{jobs.loc[i, 'location']}</td>
                <td><a href="{jobs.loc[i, 'url']}">link</a></td>
            </tr>
            """
            table += row

        html = f"""\
            <!DOCTYPE html>
            <html lang="en-us">
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <title>Simple table</title>
                <link href="minimal-table.css" rel="stylesheet" type="text/css">
              </head>
              <body>
                <h1>Simple table</h1>
                <p>
                Les derniers jobs scrapés datent du {self.last_scraped_date}. Il y a {len(jobs)} annonces à consulter.
                </p>
                <table>
                {table}
                </table>
              </body>
            </html>
            """
        return text, html

    def send_message(self, text, html):
        """Send a message from authentified Gmail user.
        Contains last scraped jobs.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            message = MIMEMultipart('alternative')
            message['to'] = 'donorfelita@msn.com'
            message['subject'] = 'New hot jobs'

            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            message.attach(part1)
            message.attach(part2)

            created_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

            try:
                message = (service.users().messages().send(userId="me", body=created_message).execute())
                print(F'sent message to {message} Message Id: {message["id"]}')
            except HttpError as error:
                print(F'An error occurred: {error}')
                message = None

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')


if __name__ == '__main__':
    Messenger().message()


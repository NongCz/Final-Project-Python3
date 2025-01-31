# File: expense_tracker/sheets_integration.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
from typing import List, Dict, Any
from datetime import datetime
from models import Transaction

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsSync:
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """Handle Google Sheets authentication"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'service-account.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('sheets', 'v4', credentials=self.creds)

    def setup_spreadsheet(self):
        """Initialize the spreadsheet with headers"""
        headers = [
            ['ID', 'Date', 'Type', 'Category', 'Amount', 'Description', 'Balance']
        ]
        
        body = {
            'values': headers
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range='A1:G1',
            valueInputOption='RAW',
            body=body
        ).execute()

    def sync_transaction(self, transaction: Transaction, running_balance: float):
        """Sync a single transaction to Google Sheets"""
        row = [
            [
                str(transaction.id),
                transaction.date.strftime('%Y-%m-%d %H:%M'),
                transaction.transaction_type.value,
                transaction.category.value,
                str(transaction.amount),
                transaction.description,
                str(running_balance)
            ]
        ]
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='A:G',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': row}
        ).execute()
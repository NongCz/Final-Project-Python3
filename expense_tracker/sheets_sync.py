# File: sheets_sync.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from models import Transaction

class GoogleSheetsSync:
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.creds = service_account.Credentials.from_service_account_file(
            'service-account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.creds)

    def setup_spreadsheet(self):
        """Initialize the spreadsheet with headers"""
        headers = [
            ['Date', 'Type', 'Category', 'Amount', 'Description', 'Balance']
        ]
        
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range='A1:F1',
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()

    def sync_transaction(self, transaction: Transaction, running_balance: float):
        """Sync a single transaction to Google Sheets"""
        row = [[
            transaction.date.strftime('%Y-%m-%d %H:%M'),
            transaction.transaction_type.value,
            transaction.category.value,
            str(transaction.amount),
            transaction.description,
            str(running_balance)
        ]]
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='A:F',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': row}
        ).execute()
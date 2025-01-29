# File: expense_tracker/database.py

import sqlite3
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from models import Transaction, TransactionType, Category
from sheets_integration import GoogleSheetsSync

class ExpenseTracker:
    def __init__(self, db_path: str = "expense_tracker.db", spreadsheet_id: Optional[str] = None):
        self.db_path = db_path
        self.init_database()
        self.sheets_sync = None
        if spreadsheet_id:
            self.sheets_sync = GoogleSheetsSync(spreadsheet_id)
            self.sheets_sync.authenticate()
            self.sheets_sync.setup_spreadsheet()

    def init_database(self):
       """Initialize SQLite database and create necessary tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount DECIMAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    date TIMESTAMP NOT NULL
                )
            ''')
            conn.commit()

    def add_transaction(self, transaction: Transaction) -> int:
        """Add a new transaction to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (amount, transaction_type, category, description, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(transaction.amount),
                transaction.transaction_type.value,
                transaction.category.value,
                transaction.description,
                transaction.date.isoformat()
            ))
            conn.commit()
            transaction_id = cursor.lastrowid

            # Sync to Google Sheets if enabled
            if self.sheets_sync:
                transaction.id = transaction_id
                balance = self.get_balance()
                self.sheets_sync.sync_transaction(transaction, balance)

            return transaction_id

    def get_transactions(self, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None,
                        transaction_type: Optional[TransactionType] = None,
                        category: Optional[Category] = None) -> List[Transaction]:
        """Retrieve transactions with optional filters."""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type.value)
        if category:
            query += " AND category = ?"
            params.append(category.value)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            return [
                Transaction(
                    id=row['id'],
                    amount=Decimal(row['amount']),
                    transaction_type=TransactionType(row['transaction_type']),
                    category=Category(row['category']),
                    description=row['description'],
                    date=datetime.fromisoformat(row['date'])
                )
                for row in cursor.fetchall()
            ]

    def get_balance(self) -> Decimal:
        """Calculate current balance based on all transactions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE -amount END), 0)
                FROM transactions
            ''')
            return Decimal(cursor.fetchone()[0])
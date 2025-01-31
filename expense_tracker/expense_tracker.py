import sqlite3
from decimal import Decimal
from datetime import datetime
from typing import List, Optional  
from models import Transaction, TransactionType, Category
from sheets_sync import GoogleSheetsSync

class ExpenseTracker:
    def __init__(self, db_path: str = "expense_tracker.db", spreadsheet_id: Optional[str] = None):
        self.db_path = db_path
        self.init_database()
        self.sheets_sync = None
        if spreadsheet_id:
            self.sheets_sync = GoogleSheetsSync(spreadsheet_id)
            self.sheets_sync.setup_spreadsheet()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount DECIMAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    date TIMESTAMP NOT NULL
                )
            ''')

    def add_transaction(self, transaction: Transaction) -> int:
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
            
            if self.sheets_sync:
                balance = self.get_balance()
                self.sheets_sync.sync_transaction(transaction, balance)
            
            return transaction_id

    def get_balance(self) -> Decimal:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(SUM(
                    CASE WHEN transaction_type = 'income' 
                    THEN amount ELSE -amount END
                ), 0) FROM transactions
            ''')
            return Decimal(cursor.fetchone()[0])

    def get_transactions(self) -> List[Transaction]:
        """Retrieve all transactions from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT amount, transaction_type, category, description, date FROM transactions')
            
            transactions = []
            for row in cursor.fetchall():
                amount, transaction_type, category, description, date = row
                transaction = Transaction(
                    amount=Decimal(amount),
                    transaction_type=TransactionType(transaction_type),
                    category=Category(category),
                    description=description,
                    date=datetime.fromisoformat(date)
                )
                transactions.append(transaction)
        
        return transactions
    
    def get_transactions_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
    """Retrieve transactions within a specific date range."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT amount, transaction_type, category, description, date 
            FROM transactions 
            WHERE date BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))

        transactions = []
        for row in cursor.fetchall():
            amount, transaction_type, category, description, date = row
            transaction = Transaction(
                amount=Decimal(amount),
                transaction_type=TransactionType(transaction_type),
                category=Category(category),
                description=description,
                date=datetime.fromisoformat(date)
            )
            transactions.append(transaction)

    return transactions

# File: main.py
from decimal import Decimal
from datetime import datetime
from models import Transaction, TransactionType, Category
from expense_tracker import ExpenseTracker

def main():
    SPREADSHEET_ID = "1hTxKJXnNuhTwOFWnjhjSnnADfaoBNO-i9wQO-nXxEYs"
    
    tracker = ExpenseTracker(spreadsheet_id=SPREADSHEET_ID)
    
    transactions = [
        Transaction(
            amount=Decimal("1000.00"),
            transaction_type=TransactionType.INCOME,
            category=Category.SALARY,
            description="Monthly salary",
            date=datetime.now()
        ),
        Transaction(
            amount=Decimal("25.50"),
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            description="Lunch at cafe",
            date=datetime.now()
        )
    ]
    
    for transaction in transactions:
        transaction_id = tracker.add_transaction(transaction)
        print(f"Added transaction {transaction_id}")
    
    balance = tracker.get_balance()
    print(f"Current balance: ${balance:.2f}")

if __name__ == "__main__":
    main()
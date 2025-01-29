# File: expense_tracker/cli.py

import cmd
from decimal import Decimal
from datetime import datetime
from models import Transaction, TransactionType, Category
from database import ExpenseTracker

class ExpenseTrackerCLI(cmd.Cmd):
    intro = 'Welcome to the Expense Tracker. Type help or ? to list commands.\n'
    prompt = '(expense-tracker) '

    def __init__(self):
        super().__init__()
        self.tracker = ExpenseTracker(spreadsheet_id="1hTxKJXnNuhTwOFWnjhjSnnADfaoBNO-i9wQO-nXxEYs/edit?gid=0#gid=0")  

    def do_add(self, arg):
        """Add a new transaction: add <amount> <type> <category> <description>
        Example: add 50.00 expense food "Lunch at cafe" """
        try:
            args = arg.split(maxsplit=3)
            if len(args) != 4:
                print("Invalid number of arguments")
                return

            amount, trans_type, category, description = args
            transaction = Transaction(
                amount=Decimal(amount),
                transaction_type=TransactionType(trans_type.lower()),
                category=Category(category.lower()),
                description=description.strip('"'),
                date=datetime.now()
            )
            
            transaction_id = self.tracker.add_transaction(transaction)
            print(f"Transaction added successfully with ID: {transaction_id}")
        
        except (ValueError, KeyError) as e:
            print(f"Error: {str(e)}")

    def do_balance(self, arg):
        """Show current balance"""
        balance = self.tracker.get_balance()
        print(f"Current balance: ${balance:.2f}")

    def do_list(self, arg):
        """List all transactions"""
        transactions = self.tracker.get_transactions()
        if not transactions:
            print("No transactions found")
            return

        print("\nTransaction History:")
        print("-" * 80)
        for t in transactions:
            print(f"ID: {t.id}")
            print(f"Date: {t.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"Type: {t.transaction_type.value}")
            print(f"Category: {t.category.value}")
            print(f"Amount: ${t.amount:.2f}")
            print(f"Description: {t.description}")
            print("-" * 80)

    def do_quit(self, arg):
        """Exit the program"""
        print("Thank you for using Expense Tracker!")
        return True

if __name__ == '__main__':
    ExpenseTrackerCLI().cmdloop()
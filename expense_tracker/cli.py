# File: cli.py

import cmd
import dotenv
import os
from decimal import Decimal
from datetime import datetime, timedelta
from models import Transaction, TransactionType, Category
from expense_tracker import ExpenseTracker
from llm_processor import LLMProcessor

dotenv.load_dotenv()
api_key = os.environ["KEY"]

class ExpenseTrackerCLI(cmd.Cmd):
    intro = '''
        Welcome to the Smart Expense Tracker!
        Available commands:
            add      - Add transaction manually
            quick    - Add transaction using natural language
            balance  - Show current balance
            list     - List all transactions
            analyze  - Get spending insights
            ask      - Ask questions about your finances
            budget   - Get budget recommendations
            help     - Show this help message
            quit     - Exit the program
        '''
    prompt = '(expense-tracker) '

    def __init__(self, api_key: str, spreadsheet_id: str = None):
        super().__init__()
        self.tracker = ExpenseTracker(spreadsheet_id=spreadsheet_id)
        self.llm = LLMProcessor(api_key=api_key)

    def do_add(self, arg):
        """Add a new transaction: add <amount> <type> <category> <description>
        Example: add 50.00 expense food "Lunch at cafe" """
        try:
            args = arg.split(maxsplit=3)
            if len(args) != 4:
                print("Usage: add <amount> <type> <category> <description>")
                print("Example: add 50.00 expense food \"Lunch at cafe\"")
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
            print("\nAvailable categories:", [c.value for c in Category])
            print("Transaction types:", [t.value for t in TransactionType])

    def do_quick(self, arg):
        """Add transaction using natural language
        Example: quick Spent $25 on lunch today
        Example: quick Received $1000 salary"""
        if not arg:
            print("Please provide a description of your transaction.")
            return
            
        transaction = self.llm.process_transaction_input(arg)
        if transaction:
            print("\nInterpreted as:")
            print(f"Type: {transaction.transaction_type.value}")
            print(f"Amount: ${transaction.amount}")
            print(f"Category: {transaction.category.value}")
            print(f"Description: {transaction.description}")
            
            confirm = input("\nIs this correct? (y/n): ")
            if confirm.lower() == 'y':
                transaction_id = self.tracker.add_transaction(transaction)
                print(f"Transaction added successfully with ID: {transaction_id}")
            else:
                print("Transaction cancelled")
        else:
            print("Could not process the input. Please try again or use the 'add' command.")

    def do_analyze(self, arg):
        """Get insights about your spending patterns"""
        transactions = self.tracker.get_transactions()
        if not transactions:
            print("No transactions found to analyze.")
            return
            
        insights = self.llm.get_insights(transactions)
        print("\nFinancial Insights:")
        print("-" * 80)
        print(insights)
        print("-" * 80)

    def do_ask(self, arg):
        """Ask questions about your finances
        Example: ask How much did I spend on food last month?
        Example: ask What's my biggest expense category?"""
        if not arg:
            print("Please ask a question about your finances.")
            return
            
        transactions = self.tracker.get_transactions()
        if not transactions:
            print("No transaction data available.")
            return
            
        answer = self.llm.answer_question(arg, transactions)
        print("\nAnswer:")
        print("-" * 80)
        print(answer)
        print("-" * 80)

    def do_budget(self, arg):
        """Get personalized budget recommendations"""
        transactions = self.tracker.get_transactions()
        if not transactions:
            print("No transaction history available for budget recommendations.")
            return
            
        recommendations = self.llm.get_budget_recommendation(transactions)
        print("\nBudget Recommendations:")
        print("-" * 80)
        print(recommendations)
        print("-" * 80)
    
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

    def default(self, line):
        print(f"Unknown command: {line}")
        print("Type 'help' for available commands.")
    
    def do_plot(self, arg):
        """Plot daily expenses between two dates: plot <date_from> <date_to>
        Example: plot 2025-01-01 2025-01-14"""
        try:
            date_from_str, date_to_str = arg.split()
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d')

            # Fetch transactions in the specified date range
            transactions = self.tracker.get_transactions_in_date_range(date_from, date_to)
            if not transactions:
                print("No transactions found in this date range.")
                return

            # Process data for plotting
            daily_expenses = self.process_daily_expenses(transactions)

            # Plotting the data
            self.plot_expenses(daily_expenses)

        except ValueError:
            print("Invalid input format. Please use 'plot <date_from> <date_to>' with format YYYY-MM-DD.")
        except Exception as e:
            print(f"Error: {e}")

    def process_daily_expenses(self, transactions):
        """Process transactions to group by day and sum expenses."""
        daily_expenses = {}
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.EXPENSE:
                day = transaction.date.date()  # Get just the date part
                if day not in daily_expenses:
                    daily_expenses[day] = Decimal('0.00')
                daily_expenses[day] += transaction.amount
        return daily_expenses

    def plot_expenses(self, daily_expenses):
        """Plot expenses using matplotlib."""
        import matplotlib.pyplot as plt

        days = list(daily_expenses.keys())
        amounts = [float(daily_expenses[day]) for day in days]

        plt.figure(figsize=(10, 5))
        plt.bar(days, amounts, color='blue')
        plt.xlabel('Date')
        plt.ylabel('Total Expenses ($)')
        plt.title('Daily Expenses')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
if __name__ == '__main__':
    API_KEY = api_key
    SPREADSHEET_ID = "1hTxKJXnNuhTwOFWnjhjSnnADfaoBNO-i9wQO-nXxEYs" 
    ExpenseTrackerCLI(api_key=API_KEY, spreadsheet_id=SPREADSHEET_ID).cmdloop()
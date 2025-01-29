# File: expense_tracker/models.py

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Optional

class TransactionType(Enum):
    EXPENSE = "expense"
    INCOME = "income"

class Category(Enum):
    FOOD = "food"
    TRANSPORTATION = "transportation"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    SALARY = "salary"
    INVESTMENT = "investment"
    OTHER = "other"

@dataclass
class Transaction:
    amount: Decimal
    transaction_type: TransactionType
    category: Category
    description: str
    date: datetime
    id: Optional[int] = None
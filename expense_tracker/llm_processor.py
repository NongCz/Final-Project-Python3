from typing import Optional, List
from decimal import Decimal
from datetime import datetime
import json
from mistralai.client import MistralClient
from models import Transaction, TransactionType, Category

class LLMProcessor:
    def __init__(self, api_key: str):
        self.client = MistralClient(api_key=api_key)

    def process_transaction_input(self, text: str) -> Optional[Transaction]:
        """Process natural language input to extract transaction details."""
        prompt = f"""
        Extract transaction details from: "{text}"
        
        Return a JSON object with:
        - type: either "expense" or "income"
        - amount: a number
        - category: one of {[c.value for c in Category]}
        - description: short summary
        """

        try:    
            response = self.client.chat(
                model="mistral-medium",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Print the raw response for debugging
            print("Raw LLM response:", response)

            try:
                parsed = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                print("❌ Failed to parse LLM response as JSON.")
                return None

            return Transaction(
                amount=Decimal(str(parsed['amount'])),
                transaction_type=TransactionType(parsed['type']),
                category=Category(parsed['category']),
                description=parsed['description'],
                date=datetime.now(),
            )
        except Exception as e:
            print(f"❌ Error processing transaction: {e}")
            return None



    def get_insights(self, transactions: List[Transaction]) -> str:
        """Generate financial insights based on spending patterns."""
        trans_summary = "\n".join([
            f"- {t.date.strftime('%Y-%m-%d')}: {t.transaction_type.value} ${t.amount} on {t.category.value}"
            for t in transactions[-10:]  
        ])
        
        prompt = f"""
        Analyze these recent transactions and provide financial insights:
        {trans_summary}

        Provide:
        1. Spending trends
        2. High expenditure areas
        3. Savings opportunities
        4. Budget recommendations

        Keep it clear and actionable.
        """

        try:
            response = self.client.chat(
                model="mistral-medium",
                messages=[{"role": "user", "content": prompt}]
            )

            return response.choices[0].message["content"]
        except Exception as e:
            return f"❌ Error generating insights: {e}"

    def answer_question(self, question: str, transactions: List[Transaction]) -> str:
        """Answer financial questions using transaction data."""
        trans_summary = {}
        for t in transactions:
            month_key = t.date.strftime('%Y-%m')
            if month_key not in trans_summary:
                trans_summary[month_key] = {'total': 0, 'categories': {}}
            
            if t.transaction_type == TransactionType.EXPENSE:
                trans_summary[month_key]['total'] += float(t.amount)
                if t.category.value not in trans_summary[month_key]['categories']:
                    trans_summary[month_key]['categories'][t.category.value] = 0
                trans_summary[month_key]['categories'][t.category.value] += float(t.amount)

        context = json.dumps(trans_summary)
        
        prompt = f"""
        Answer this finance question: "{question}"
        
        Transaction data:
        {context}
        
        Provide a clear answer based on data.
        """

        try:
            response = self.client.chat(
                model="mistral-medium",
                messages=[{"role": "user", "content": prompt}]
            )

            return response.choices[0].message["content"]
        except Exception as e:
            return f"❌ Error answering question: {e}"
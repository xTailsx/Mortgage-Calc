import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
import io
import base64

app = Flask(__name__)

# Mortgage calculation function
def calculate_mortgage(loan_amount, interest_rate, loan_term_years, offset_balance, extra_repayment):
    monthly_rate = interest_rate / 100 / 12
    total_months = loan_term_years * 12
    adjusted_loan_amount = loan_amount - offset_balance

    if monthly_rate > 0:
        monthly_repayment = adjusted_loan_amount * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)
    else:
        monthly_repayment = adjusted_loan_amount / total_months

    total_cost = monthly_repayment * total_months
    adjusted_total_cost = total_cost - (extra_repayment * total_months)
    interest_saved = total_cost - adjusted_total_cost
    years_saved = (adjusted_total_cost / monthly_repayment) / 12  # Calculate years saved
    revised_term_months = adjusted_total_cost / monthly_repayment
    revised_term_years = revised_term_months / 12  # Convert months to years

    return {
        "monthly_repayment": round(monthly_repayment, 2),
        "total_cost": round(total_cost, 2),
        "interest_saved": round(interest_saved, 2),
        "years_saved": round(years_saved, 2),
        "adjusted_total_cost": round(adjusted_total_cost, 2),
        "revised_term_years": round(revised_term_years, 2)  # Use years here
    }

# Function to create repayment schedule graph
def generate_graph(loan_amount, interest_rate, loan_term_years, offset_balance, extra_repayment):
    monthly_rate = interest_rate / 100 / 12
    total_months = loan_term_years * 12
    adjusted_loan_amount = loan_amount - offset_balance

    if monthly_rate > 0:
        monthly_repayment = adjusted_loan_amount * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)
    else:
        monthly_repayment = adjusted_loan_amount / total_months

    balance = adjusted_loan_amount
    monthly_balances = [balance]
    for month in range(1, total_months + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_repayment - interest_payment
        balance -= principal_payment
        balance = max(balance, 0)
        monthly_balances.append(balance)

    plt.figure(figsize=(10, 6))
    plt.plot(monthly_balances, label='Loan Balance Over Time', color='b')
    plt.title('Mortgage Repayment Schedule')
    plt.xlabel('Months')
    plt.ylabel('Loan Balance')
    plt.grid(True)
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')
    return graph_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get form data
        loan_amount = float(request.form['loan_amount'])
        interest_rate = float(request.form['interest_rate'])
        loan_term_years = int(request.form['loan_term_years'])
        offset_balance = float(request.form['offset_balance'])
        extra_repayment = float(request.form['extra_repayment'])

        # Perform mortgage calculations
        result = calculate_mortgage(loan_amount, interest_rate, loan_term_years, offset_balance, extra_repayment)

        # Generate the graph
        graph_url = generate_graph(loan_amount, interest_rate, loan_term_years, offset_balance, extra_repayment)

        # Return results and graph to the template
        return render_template('index.html', result=result, graph_url=graph_url)

    except Exception as e:
        print(f"Error: {e}")
        return "There was an error with your calculation.", 500

if __name__ == '__main__':
    app.run(debug=True)

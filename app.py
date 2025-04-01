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

    # Regular monthly repayment without the extra repayment
    if monthly_rate > 0:
        monthly_repayment = adjusted_loan_amount * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)
    else:
        monthly_repayment = adjusted_loan_amount / total_months

    # Add the extra repayment to the regular repayment
    total_monthly_repayment = monthly_repayment + extra_repayment

    total_cost = monthly_repayment * total_months
    adjusted_total_cost = total_cost - (extra_repayment * total_months)
    interest_saved = total_cost - adjusted_total_cost

    # Calculate the number of months saved by extra repayments
    balance = adjusted_loan_amount
    months_paid_off_early = 0

    while balance > 0:
        interest_payment = balance * monthly_rate
        principal_payment = total_monthly_repayment - interest_payment
        balance -= principal_payment
        months_paid_off_early += 1
        if balance < 0:
            balance = 0

    # Calculate years saved
    months_saved = total_months - months_paid_off_early
    years_saved = months_saved / 12
    revised_term_months = months_paid_off_early

    return {
        "monthly_repayment": round(monthly_repayment, 2),
        "total_cost": round(total_cost, 2),
        "interest_saved": round(interest_saved, 2),
        "years_saved": round(years_saved, 2),
        "adjusted_total_cost": round(adjusted_total_cost, 2),
        "revised_term_months": revised_term_months,
        "revised_term_years": round(revised_term_months / 12, 2)  # Revised term in years
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

    total_monthly_repayment = monthly_repayment + extra_repayment

    balance = adjusted_loan_amount
    monthly_balances = [balance]
    for month in range(1, total_months + 1):
        interest_payment = balance * monthly_rate
        principal_payment = total_monthly_repayment - interest_payment
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
    loan_amount = float(request.form['loan_amount'])
    interest_rate = float(request.form['interest_rate'])
    loan_term_years = int(request.form['loan_term_years'])
    offset_balance = float(request.form['offset_balance'])
    extra_repayment = float(request.form['extra_repayment'])  # Ensure extra_repayment is a float

    result = calculate_mortgage(loan_amount, interest_rate, loan_term_years, offset_balance, extra_repayment)
    graph_url = generate_graph(loan_amount, interest_rate, loan_term_years, offset_balance, extra_repayment)

    # Pass extra_repayment to the template
    return render_template('index.html', result=result, graph_url=graph_url, extra_repayment=extra_repayment)


if __name__ == '__main__':
    app.run(debug=True)

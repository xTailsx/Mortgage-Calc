function calculateMortgage() {
    // Get input values
    const loanAmount = parseFloat(document.getElementById('loan-amount').value);
    const interestRate = parseFloat(document.getElementById('interest-rate').value) / 100;
    const loanTerm = parseFloat(document.getElementById('loan-term').value);
    const offsetBalance = parseFloat(document.getElementById('offset-balance').value);
    const extraRepayment = parseFloat(document.getElementById('extra-repayment').value);

    // Validate inputs
    if (isNaN(loanAmount) || isNaN(interestRate) || isNaN(loanTerm) || isNaN(offsetBalance) || isNaN(extraRepayment)) {
        alert('Please fill in all fields with valid values.');
        return;
    }

    // Adjusted loan amount after considering the offset
    const adjustedLoanAmount = loanAmount - offsetBalance;

    // Monthly interest rate
    const monthlyRate = interestRate / 12;

    // Number of payments (months)
    const numberOfPayments = loanTerm * 12;

    // Monthly repayment without extra payments (standard mortgage calculation)
    const monthlyRepayment = (adjustedLoanAmount * monthlyRate) / (1 - Math.pow(1 + monthlyRate, -numberOfPayments));

    // Calculate new monthly repayment with extra repayment
    const newMonthlyRepayment = monthlyRepayment + extraRepayment;

    // Total cost of the loan with extra repayments
    let remainingLoanAmount = adjustedLoanAmount;
    let months = 0;
    let totalRepayment = 0;
    let totalInterestPaid = 0;

    while (remainingLoanAmount > 0) {
        let interestPayment = remainingLoanAmount * monthlyRate;
        let principalPayment = newMonthlyRepayment - interestPayment;
        remainingLoanAmount -= principalPayment;
        totalRepayment += newMonthlyRepayment;
        totalInterestPaid += interestPayment;
        months++;

        if (remainingLoanAmount <= 0) break;
    }

    // Calculate years saved
    const revisedTerm = months / 12;
    const yearsSaved = loanTerm - revisedTerm;

    // Calculate interest saved
    const totalInterestWithoutExtra = (monthlyRepayment * numberOfPayments) - adjustedLoanAmount;
    const interestSaved = totalInterestWithoutExtra - totalInterestPaid;

    // Display results
    document.getElementById('monthly-repayment').textContent = `Monthly Repayment: $${monthlyRepayment.toFixed(2)}`;
    document.getElementById('new-repayment').textContent = `New Repayment (with extra): $${newMonthlyRepayment.toFixed(2)}`;
    document.getElementById('total-cost').textContent = `Total Cost: $${totalRepayment.toFixed(2)}`;
    document.getElementById('total-interest-saved').textContent = `Interest Saved: $${interestSaved.toFixed(2)}`;
    document.getElementById('years-saved').textContent = `Years Saved: ${yearsSaved.toFixed(2)} years`;
    document.getElementById('revised-term').textContent = `Revised Loan Term: ${revisedTerm.toFixed(2)} years`;

    // Graph: Display repayment breakdown
    displayGraph(months, newMonthlyRepayment, adjustedLoanAmount, monthlyRate);
}

function displayGraph(months, newMonthlyRepayment, loanAmount, monthlyRate) {
    const dataPoints = [];
    let remainingLoanAmount = loanAmount;
    
    for (let i = 0; i < months; i++) {
        let interestPayment = remainingLoanAmount * monthlyRate;
        let principalPayment = newMonthlyRepayment - interestPayment;
        remainingLoanAmount -= principalPayment;
        dataPoints.push(remainingLoanAmount);
        
        if (remainingLoanAmount <= 0) break;
    }

    const ctx = document.getElementById('repayment-graph').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: months }, (_, i) => i + 1),
            datasets: [{
                label: 'Remaining Loan Balance',
                data: dataPoints,
                borderColor: 'rgb(75, 192, 192)',
                fill: false,
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Months'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Remaining Balance ($)'
                    },
                    beginAtZero: true,
                }
            }
        }
    });
}

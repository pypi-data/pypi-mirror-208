# EMI Calculator

The EMI Calculator is a Python library that provides a convenient way to calculate the Equated Monthly Installment (EMI) for a loan. It helps borrowers determine the fixed monthly payment, considering the principal loan amount, interest rate, and tenure in months.

## Installation

You can install the EMI Calculator library using pip:

```shell
pip install emi_calculator
```
# **Usage**
 ```shell
from emi import emi_calculator
OR
import emi

 # Note* emi_calculator takes 3 arguments:
 #                1. loan amount
 #                2. interest rate
 #                3. tenure_month 
 #  the emi will result in float format 
 # you can use round function to round up what u want

# Input loan details
loan_amount = float(input('Enter loan amount: '))
interest_rate = float(input('Enter interest rate: '))
tenure_months = int(input('Enter tenure in months: '))

# Calculate EMI
calculate_emi = emi_calculator(loan_amount, interest_rate, tenure_months)
print(f"The Equated Monthly Installment (EMI) is: {calculate_emi:.2f}")
```

**Example**
Let's calculate the EMI for a loan of $10,000 with an annual interest rate of 5% and a tenure of 36 months:
 ```shell
from emi import emi_calculator

loan_amount = 10000
interest_rate = 5
tenure_months = 36

emi = emi_calculator(loan_amount, interest_rate, tenure_months)
print(f"The Equated Monthly Installment (EMI) is: {emi:.2f}")
```
**Output**:
````shell
The Equated Monthly Installment (EMI) is: 304.17
````
**Contributing**
Contributions are welcome! If you have any suggestions, improvements, or bug fixes, please create an issue or submit a pull request.

**License**
This project is licensed under the MIT License. See the LICENSE file for details.

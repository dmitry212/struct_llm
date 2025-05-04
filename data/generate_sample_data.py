import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

# Initialize Faker for generating realistic names and addresses
fake = Faker()

# Generate products data
products = [
    {
        'product_id': f'PROD{i:03d}',
        'product_name': name,
        'coverage_type': coverage,
        'term_length_years': term,
        'base_premium': round(random.uniform(50, 500), 2),
        'max_coverage_amount': round(random.uniform(100000, 1000000), 2)
    }
    for i, (name, coverage, term) in enumerate([
        ('Term Life Basic', 'Term Life', 10),
        ('Term Life Plus', 'Term Life', 20),
        ('Whole Life Standard', 'Whole Life', None),
        ('Whole Life Premium', 'Whole Life', None),
        ('Universal Life Flex', 'Universal Life', None),
        ('Universal Life Plus', 'Universal Life', None),
        ('Variable Life Growth', 'Variable Life', None),
        ('Variable Life Balanced', 'Variable Life', None),
        ('Indexed Universal Life', 'Indexed Universal Life', None),
        ('Final Expense', 'Whole Life', None)
    ])
]

# Generate customers data
customers = []
for i in range(100):
    birth_date = fake.date_of_birth(minimum_age=25, maximum_age=75)
    customers.append({
        'customer_id': f'CUST{i:03d}',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'date_of_birth': birth_date,
        'age': (datetime.now().date() - birth_date).days // 365
    })

# Generate orders data
orders = []
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

for day in range((end_date - start_date).days + 1):
    current_date = start_date + timedelta(days=day)
    # Generate 1-5 orders per day
    num_orders = random.randint(1, 5)
    
    for _ in range(num_orders):
        customer = random.choice(customers)
        product = random.choice(products)
        
        # Adjust premium based on age
        age_factor = 1 + (customer['age'] - 40) * 0.02  # 2% increase per year over 40
        premium = round(product['base_premium'] * age_factor, 2)
        
        # Adjust coverage based on age and product
        coverage_factor = 1 - (customer['age'] - 40) * 0.01  # 1% decrease per year over 40
        coverage_amount = round(product['max_coverage_amount'] * coverage_factor, 2)
        
        orders.append({
            'order_id': f'ORD{len(orders):06d}',
            'customer_id': customer['customer_id'],
            'product_id': product['product_id'],
            'order_date': current_date.date(),
            'premium_amount': premium,
            'coverage_amount': coverage_amount,
            'payment_status': random.choice(['Paid', 'Pending', 'Failed']),
            'policy_status': random.choice(['Active', 'Pending', 'Cancelled'])
        })

# Convert to DataFrames and save as CSV
pd.DataFrame(products).to_csv('data/products.csv', index=False)
pd.DataFrame(customers).to_csv('data/customers.csv', index=False)
pd.DataFrame(orders).to_csv('data/orders.csv', index=False)

print("Sample data generated successfully!") 
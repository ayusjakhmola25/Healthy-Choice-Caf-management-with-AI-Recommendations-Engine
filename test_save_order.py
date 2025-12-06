import requests

# Test the save-order endpoint with user_id for guest order
response = requests.post('http://127.0.0.1:3000/save-order', json={
    'user_id': None,  # Guest order
    'name': 'Test Guest',
    'mobile': '1234567890',
    'email': 'test@example.com',
    'order_data': '[{"name":"Test Item","quantity":1,"price":100}]',
    'total_amount': 150,
    'payment_method': 'Card Payment',
    'diet_preference': 'diet'
})

print('Guest Order Test:')
print('Response status:', response.status_code)
print('Response JSON:', response.json())

# Test with a logged-in user (assuming user_id 1 exists)
response2 = requests.post('http://127.0.0.1:3000/save-order', json={
    'user_id': 1,  # Logged-in user
    'name': 'Test User',
    'mobile': '0987654321',
    'email': 'user@example.com',
    'order_data': '[{"name":"Test Item","quantity":1,"price":100}]',
    'total_amount': 150,
    'payment_method': 'Cash on Delivery',
    'diet_preference': 'non-diet'
})

print('\nLogged-in User Order Test:')
print('Response status:', response2.status_code)
print('Response JSON:', response2.json())

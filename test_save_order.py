import requests

# Test the save-order endpoint with diet_preference
response = requests.post('http://127.0.0.1:3000/save-order', json={
    'name': 'Test Guest',
    'mobile': '1234567890',
    'email': 'test@example.com',
    'order_data': '[{"name":"Test Item","quantity":1,"price":100}]',
    'total_amount': 150,
    'payment_method': 'Card Payment',
    'diet_preference': 'diet'
})

print('Response status:', response.status_code)
print('Response JSON:', response.json())


name = 'Test Project'
version = 0.1
age = 10

### default value used here
# database = {
#   'port': 1000,
#   'address': '192.168.0.1'
# }

selectors = [
    {
      'uri': 'amazon.com',
      'gold': {
        'price': 12.90,
        'product_name': 'Diapers'
      },
      'version': (0,0),
    },
    {
      'uri': 'amazon.com',
      'gold': {
        'price': 0.99,
        'product_name': 'candy'
      },
      'version': (0,0),
    },
    {
      'uri': 'newegg.com',
      'gold': {
        'price': 15.0,
        'product_name': 'headphones'
      },
      'version': (0,0),
    },
]

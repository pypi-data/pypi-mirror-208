# jprint
A simple tool for pretty priting json strings and python dictionaries to the console.


## Python Dictionary Example
```python

from jprint import jprint


example_dict = {
    "name": "John Doe",
    "age": 30,
    "city": "New York",
    "hobbies": ["reading", "traveling", "photography"]
}

jprint(example_dict)
```

<!-- ![Python Image](images/python_img.png) -->
![](https://raw.githubusercontent.com/gnulnx/jprint/main/images/python_img.png?token=GHSAT0AAAAAAB6XJL5JKQJX3HBELAZ4VMVEZB2YBXA)


## JSON String Example
```python
from jprint import jprint

json_string = '''
    {
        "name": "Alice",
        "age": 32,
        "email": "alice@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90012"
        },
        "phone_numbers": [
            {
                "type": "home",
                "number": "555-1234"
            },
            {
                "type": "work",
                "number": "555-5678"
            }
        ]
    }
    '''

jprint(json_string, indent=2)
```

![Json Image](https://raw.githubusercontent.com/gnulnx/jprint/main/images/json_img.png?token=GHSAT0AAAAAAB6XJL5ITD2PDRN26LXXB7MSZB2YCFQ)

## Under The Covers

jprint makes use of the pygmyents library for colored output and json.dumps() for other formatting. 
You can pass jprint any of the parameters that you would pass to json.dumps
# SEVEN API endpoint package

This package was meant to help the end users to utilise the API endpoints of Seven. 
In the current verison you can use the following endpoints:

- Store Fields
- Store Data
- Process Fields
- Process Data
- Costs
- Reports

Each of these categories are represented by a class. You can initiate a class instance and use the .call_api() method to get a response.

## Installation

You can use your package manager to install from PyPI.

If you are using pip:
```
python3 -m pip install seven-api-sdk
```

## Examples

```
import seven_api_sdk
import json

password = "YOUR_SECRET_PASSWORD"
username = "YOUR_USERNAME"
client_id = "YOUR_CLIENT_ID"
client_name = "YOUR_TENANT_NAME"


handler = seven_api_sdk.StoreFields(username=username,password=password,client_id=client_id,client_name=client_name)
data = handler.call_api()

print (json.dumps(data,indent=4))

#You can specify parameters for certain endpoints
handler = seven_api_sdk.ProcessData(username=username,password=password,client_id=client_id,client_name=client_name,parameter="proc_by_storeID")
data = handler.call_api()
print (json.dumps(data,indent=4))
```
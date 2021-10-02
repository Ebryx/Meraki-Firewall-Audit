# Meraki Firewall Audit


This script pull out required information from Meraki Devices that is needed for configuration review/audit. \
Sample Meraki API Key is included in `meraki_config.py` file. \
Update your API key and Organization ID before running this script.

> Sample API Key:
```
MERAKI_API_KEY = "6bec40cf957de430a6f1f2baa056b99a4fac9ea0"
MERAKI_ORGID = "549236"
```

<br/>

**Install Dependencies**
```
pip3 install pandas openpyxl xlsxwriter meraki
```
<br/>

**Run Script**
```
python3 meraki-audit.py
```
<br/>

**Output**

Script will generate multiple Excel files for end analyst.
```
<organization_id>.xlsx - This file will contain information related to organization wide.
<network_name>.xlsx - This file will contain information specific to network.
```

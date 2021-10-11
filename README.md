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

**Docker Setup**

*Install Docker*

```
apt install docker.io
```

<br/>

*Clone Project*

```
git clone https://github.com/Ebryx/Meraki-Firewall-Audit
cd Meraki-Firewall-Audit/
```

<br/>

*Create Docker Image*

```
sudo docker build . -t meraki-app
```

<br/>

*Run Docker Container*

```
sudo docker run --rm -it  -v `pwd`/output/:/script/output meraki-app bash
```

<br/>

*Run Script Inside Docker Container*

```
root@docker/script# python meraki-audit.py
```

<br/>

*Output*

Output files will be generated in Output Folder of Host machine.

---

**Without Docker**

*Tested On*
```
Ubuntu 18.04 - Python 3.9.7
```
<br/>

*Install Dependencies*
```
pip3 install pandas openpyxl xlsxwriter meraki
```
<br/>

*Run Script*
```
python3 meraki-audit.py
```
<br/>

*Output*

Script will generate multiple Excel files for end analyst.
```
<organization_id>.xlsx - Contains information related to organization wide.
<network_name>.xlsx - Contains information specific to network.

~ For script output debugging
output.txt - Contains json response of every API call made.
default.log - Contains console's output and error.
```

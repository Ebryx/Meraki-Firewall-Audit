import meraki
import os, json, sys
import pandas as pd
from meraki_config import MERAKI_API_KEY, MERAKI_ORGID, MERAKI_BASE_URL

# pip3 install pandas openpyxl xlsxwriter meraki

# python3 meraki-audit.py

class Utility:
    fileName = ""
    writerForNetwork = None
    writerForOrganization = None

    def createExcelFile(self, networkName):
        fileName = "".join(e for e in networkName if e.isalnum() or e.isspace()) 
        self.fileName = "_".join(fileName.split()) + '.xlsx'
        self.writerForNetwork = pd.ExcelWriter(os.path.join("output", self.fileName), engine='xlsxwriter')

    def createExcelFileForOrg(self):
        self.writerForOrganization = pd.ExcelWriter(os.path.join("output", MERAKI_ORGID+'.xlsx'), engine='xlsxwriter')

    def outputExcelSheet(self, operation, data):
        pdObj = pd.json_normalize(data)

        pdObjList = None
        if operation == "Wireless_L3_Rules" and len(pdObj.columns) >= 2:
            for x in range(0,len(pdObj.columns)):
                temp = pd.json_normalize(pdObj.iloc[:, x]) # separate every column
                if x == 0:
                    pdObjList = temp
                else:
                    pdObjList = pdObjList.append(temp)    
            pdObj = pdObjList
        elif operation == "L7_Firewall_Rules_App_Cat":
            pdObj = pd.json_normalize([self.flatten_json(x) for x in data])
         
        if self.writerForNetwork == None:
            pdObj.to_excel(self.writerForOrganization, sheet_name=operation)
        # else append to existing network excel file
        else:
            pdObj.to_excel(self.writerForNetwork, sheet_name=operation)

    def flatten_json(self, nested_json, exclude=['']):
        """Flatten json object with nested keys into a single level.
            Args:
                nested_json: A nested json object.
                exclude: Keys to exclude from output.
            Returns:
                The flattened json object if successful, None otherwise.
        """
        out = {}

        def flatten(x, name='', exclude=exclude):
            if type(x) is dict:
                for a in x:
                    if a not in exclude: flatten(x[a], name + a + '_')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(nested_json)
        return out

class Logger(object):
    def __init__(self, filename=os.path.join("output", "default.log")):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.terminal.flush()

    def __getattr__(self, attr):
        return getattr(self.terminal, attr)

    def flush(self):
        pass


class MerakiClass:

    dashboard = None
    orgid = MERAKI_ORGID
    utilityObj = None

    def __init__(self ):
        MerakiClass.utilityObj=Utility()

        MerakiClass.dashboard = meraki.DashboardAPI(
            api_key=MERAKI_API_KEY,
            base_url=MERAKI_BASE_URL,
            output_log=False,
            log_file_prefix=os.path.basename(__file__)[:-3],
            log_path='',
            print_console=False
        )

    def listNetwork(self, file):
        response = MerakiClass.dashboard.organizations.getOrganizationNetworks( MerakiClass.orgid, total_pages = 'all' )
        file.write("Networks\n")
        file.write("json="+json.dumps(response, indent=4)+"\n")
        file.write("\n")
        
        MerakiClass.utilityObj.outputExcelSheet("networks_list",response)

        return response

    def listNetworkDevices(self, network_id):
        return MerakiClass.dashboard.networks.getNetworkDevices(network_id)

    def listAdmins(self, file):
        myOrgAdmins= MerakiClass.dashboard.organizations.getOrganizationAdmins(MerakiClass.orgid)
        file.write("# Organisation Dashboard Administrators\n")
        # /organizations/{organizationId}/admins
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-organization-admins\n")
        file.write(f"Organization ID: {MerakiClass.orgid}\n")
        file.write("json="+json.dumps(myOrgAdmins, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("dashboard_admins",myOrgAdmins)

    def getOrganizationLoginSecurity(self,file):
        myRules= MerakiClass.dashboard.organizations.getOrganizationLoginSecurity(MerakiClass.orgid)
        file.write("# Organization Login Security\n")
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-organization-login-security\n")
        file.write("json="+json.dumps(myRules, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("organization_login_security",myRules)

    def getSNMPVersion(self,file):
        file.write("# SNMP Version\n")
        SNMPVersion=MerakiClass.dashboard.organizations.getOrganizationSnmp(MerakiClass.orgid)
        # /organizations/{organizationId}/snmp
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-organization-snmp\n")
        file.write("json="+json.dumps(SNMPVersion, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("SNMP_Version",SNMPVersion)

    def listApplianceSecurityMalware(self,file,network_id):
        malwareSettings=MerakiClass.dashboard.appliance.getNetworkApplianceSecurityMalware(network_id)
        file.write("# Appliance Malware Settings\n")
        # /networks/{networkId}/appliance/security/malware
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-security-malware\n")
        file.write("json="+json.dumps(malwareSettings, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("malware_settings",malwareSettings)

    def listApplianceSecurityIntrusion(self,file,network_id):
        intrusionSettings=MerakiClass.dashboard.appliance.getNetworkApplianceSecurityIntrusion(network_id)
        file.write("# Intrusion Settings for MX network\n")
        #  /networks/{networkId}/appliance/security/intrusion
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-security-intrusion\n")
        file.write("json="+json.dumps(intrusionSettings, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("intrusion_settings",intrusionSettings)

    def listMxL3FirewallRules(self,file,network_id):
        myRules=MerakiClass.dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(network_id)
        file.write("# MX L3 Firewall Rules\n")
        #/networks/{networkId}/appliance/firewall/l3FirewallRules
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-firewall-l-3-firewall-rules\n")
        file.write("json="+json.dumps(myRules, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("Mx_L3_Firewall_Rules",myRules["rules"])

    def listCellularFirewallRules(self,file,network_id):
        myRules=MerakiClass.dashboard.appliance.getNetworkApplianceFirewallCellularFirewallRules(network_id)
        file.write("# MX cellular firewall\n")
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-firewall-cellular-firewall-rules\n")
        file.write("json="+json.dumps(myRules, indent=4)+"\n")
        file.write("\n")
        MerakiClass.utilityObj.outputExcelSheet("Cellular_Firewall_Rules",myRules["rules"])

    def listL7FirewallRules(self,file,network_id):
        myRules=MerakiClass.dashboard.appliance.getNetworkApplianceFirewallL7FirewallRules(network_id)
        file.write("# MX L7 firewall rules\n")
        # /networks/{networkId}/appliance/firewall/l7FirewallRules
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-firewall-l-7-firewall-rules\n")
        file.write("json="+json.dumps(myRules, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("L7_Firewall_Rules",myRules["rules"])

        # Return the L7 firewall application categories and their associated applications for an MX network
        myRules=MerakiClass.dashboard.appliance.getNetworkApplianceFirewallL7FirewallRulesApplicationCategories(network_id)
        file.write("# MX l7 firewall rules application categories\n")
        # /networks/{networkId}/appliance/firewall/l7FirewallRules
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-firewall-l-7-firewall-rules-application-categories\n")
        file.write("json="+json.dumps(myRules, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("L7_Firewall_Rules_App_Cat",myRules["applicationCategories"])

    def getSwitchPorts(self,file,swDevices):
        data = None
        for swDevice in swDevices:
            try:
                switchPorts=MerakiClass.dashboard.switch.getDeviceSwitchPorts(swDevice["serial"])
                if data == None:
                    data = switchPorts
                else:
                    for x in switchPorts:
                        data.append(x)
            except:
                # not a switch device
                pass

        file.write("# Device Switch Ports\n")
        # /devices/{serial}/switch/ports
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-device-switch-ports\n")
        file.write("json="+json.dumps(data, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("Switch_Ports",data)

    def getSwitchAccessControlLists(self,file,network_id):
        ACL=MerakiClass.dashboard.switch.getNetworkSwitchAccessControlLists(network_id)
        file.write("# Switch Access Control Lists\n")
        # /networks/{networkId}/switch/accessControlLists
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-switch-access-control-lists\n")
        file.write("json="+json.dumps(ACL, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("Switch_ACL",ACL["rules"])

    def listSwitchAccessPolicies(self,file,network_id):
        accessPolicies=MerakiClass.dashboard.switch.getNetworkSwitchAccessPolicies(network_id)
        file.write("# Access policies of a switch network\n")
        #  /networks/{networkId}/switch/accessPolicies
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-switch-access-policies\n")
        file.write("json="+json.dumps(accessPolicies, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("Switch_Access_Policies",accessPolicies)

    def wirelessL3FirewallRules(self,file,network_id,ssidsNumber):

        data = []
        for number in ssidsNumber:
            try:
                firewallRules=MerakiClass.dashboard.wireless.getNetworkWirelessSsidFirewallL3FirewallRules(network_id, number)
                data.append(firewallRules["rules"])
            except:
                pass

        file.write("# Get Network Wireless Ssid Firewall L3 Firewall Rules\n")
        #  /networks/{networkId}/wireless/ssids/{number}/firewall/l3FirewallRules
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-wireless-ssid-firewall-l-3-firewall-rules\n")
        file.write("json="+json.dumps(data, indent=4)+"\n")
        file.write("\n")

        MerakiClass.utilityObj.outputExcelSheet("Wireless_L3_Rules",data)

    def listWirelessSSIDs(self,file,network_id):
        ssids=MerakiClass.dashboard.wireless.getNetworkWirelessSsids(network_id)
        file.write("# Get Network Wireless Ssids\n")
        #  /networks/{networkId}/wireless/ssids
        file.write("# https://developer.cisco.com/meraki/api-v1/#!get-network-wireless-ssids\n")
        file.write("json="+json.dumps(ssids, indent=4)+"\n")
        file.write("\n")

        ssidsNumber = []
        for x in ssids:
            ssidsNumber.append(x["number"])

        MerakiClass.utilityObj.outputExcelSheet("Wireless_SSIDS",ssids)
        return ssidsNumber


#----------------------------------------------------------
if __name__ == '__main__':

    sys.stdout = Logger()
    sys.stderr = Logger()

    meraki_obj = MerakiClass()
    
    with open(os.path.join("output", 'output.txt'), 'w') as file:

        # create excel sheet for organization
        meraki_obj.utilityObj.createExcelFileForOrg()

        networks = meraki_obj.listNetwork(file)
        meraki_obj.listAdmins(file)
        meraki_obj.getOrganizationLoginSecurity(file)
        meraki_obj.getSNMPVersion(file)

        # save excel sheet
        meraki_obj.utilityObj.writerForOrganization.save()

        # Iterate through networks
        total = len(networks)
        print(f'\nIterating through {total} networks\n')
        file.write(f'Iterating through {total} networks\n\n')


        for network in networks:
            network_id = network["id"]
            network_name = network["name"]

            # Create diretory for each network
            meraki_obj.utilityObj.createExcelFile(network["name"])
            
            
            print(f"Processing network: {network_id} - {network_name}\n")
            file.write(f"Processing network: {network_id} - {network_name}\n\n")

            try:
                meraki_obj.listApplianceSecurityMalware(file, network_id)
            except meraki.exceptions.APIError as e:
                print("Appliance Security Malware Error: " + network_id, e)
            
            try:
                meraki_obj.listApplianceSecurityIntrusion(file, network_id)
            except meraki.exceptions.APIError as e:
                print("MX Network Security Intrusion Settings Error: " + network_id, e)


            # #####################################################
            # ## Firewall Rules
            # #####################################################
            try:
                meraki_obj.listMxL3FirewallRules(file,network_id)
            except meraki.exceptions.APIError as e:
                print('Mx L3 Firewall Rules Error' + network_id, e)
            
            try:
               meraki_obj.listL7FirewallRules(file,network_id)
            except meraki.exceptions.APIError as e:
               print("Mx L7 Firewall Rules Error" + network_id, e)
                        
            try:
               meraki_obj.listCellularFirewallRules(file,network_id)
            except meraki.exceptions.APIError as e:
               print("Cellular Firewall Rules Error" + network_id, e)

            # #####################################################
            # ## Switch
            # #####################################################

            # get devives list
            try:
                swDevices = meraki_obj.listNetworkDevices(network_id)
                if len(swDevices) > 0:
                    meraki_obj.getSwitchPorts(file, swDevices)
                else:
                    print(f"No Switch Device for Network {network_id}")
            except Exception as e:
                print("Get Switch Ports Error - " + network_id, e)

            try:
                meraki_obj.getSwitchAccessControlLists(file,network_id)
            except meraki.exceptions.APIError as e:
                print("Switch Access Control Lists Error" + network_id, e)
            
            try:
                meraki_obj.listSwitchAccessPolicies(file,network_id)
            except meraki.exceptions.APIError as e:
                print("Switch Access Policies Error" + network_id, e)


            #####################################################
            ## Wireless Devices
            #####################################################

            ssidsNumber = []
            try:
                ssidsNumber = meraki_obj.listWirelessSSIDs(file,network_id)
            except meraki.exceptions.APIError as e:
                print("Wireless SSIDs Lists Error" + network_id, e)
            
            try:
                meraki_obj.wirelessL3FirewallRules(file,network_id,ssidsNumber)
            except meraki.exceptions.APIError as e:
                print("wireless L3 Firewall Rules Error" + network_id, e)


            meraki_obj.utilityObj.writerForNetwork.save()

            file.write("============================================\n")
            file.write("============================================\n")
            file.write("\n")


    # end-with file handler



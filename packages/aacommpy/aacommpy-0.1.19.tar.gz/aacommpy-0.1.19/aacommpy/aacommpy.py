import clr
import os
# path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'Agito.AAComm.5.5.0','lib','net48','AAComm.dll')
path = os.path.dirname(__file__)
# clr.AddReference(path)
from AAComm import CommAPI, ConnectResult, ConnectionData


class CommAPIClient:
    def __init__(self):
        clr.AddReference(path)
        self.api = CommAPI()
        status = self.api.StartAACommServer()
        if status != "":
            raise Exception("Failed to start AACommServer: " + status)
    
    def connect(self, ip_address, port):
        cData = ConnectionData()
        cData.ControllerType = Shared.ProductTypes.AGM800_ID
        cData.CommChannelType = Shared.ChannelType.Ethernet
        cData.ET_IP_1, cData.ET_IP_2, cData.ET_IP_3, cData.ET_IP_4 = ip_address.split('.')
        cData.ET_Port = port
        res = self.api.Connect(cData)
        return res

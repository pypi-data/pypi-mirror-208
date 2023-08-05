import clr
import os
import time

path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'Agito.AAComm.5.5.0', 'lib', 'net48', 'AAComm.dll')
clr.AddReference(path)

from AAComm import Services
from AAComm import CommAPI
from AAComm import Shared

api = CommAPI()

status = CommAPI.StartAACommServer()

if status != "":
    print(status)
else:
    # Access the static variable IsAACommServerRunning
    is_running = CommAPI.IsAACommServerRunning
    print(f"AACommServer is running: {is_running}")

cData = Services.ConnectionData()
cData.ControllerType = Shared.ProductTypes.AGM800_ID
cData.CommChannelType = Shared.ChannelType.Ethernet
cData.ET_IP_1 = 172
cData.ET_IP_2 = 1
cData.ET_IP_3 = 1
cData.ET_IP_4 = 101
cData.ET_Port = 5000

res = api.Connect(cData)
print(res)

# from System import EventHandler
# from AAComm.Services import AACommEventArgs

# def on_reply_received(sender, event_args):
#     print("Reply received:", event_args.Message)


# OnReplyReceived = EventHandler[AACommEventArgs](on_reply_received)
# msg = Services.AACommMessage(OnReplyReceived, "AMotorOn")


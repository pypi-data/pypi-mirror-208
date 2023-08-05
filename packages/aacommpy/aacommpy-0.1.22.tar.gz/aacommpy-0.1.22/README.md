Hu Hieu

General:
The AACommPY functions and properties names should mirror the C# library names.
I'm not sure about the namespaces: "Shared", Extensions", etc - how should these be handled in AACommPY?
The documentation should comply with the existing AAComm documentation (feel free to use it as reference, and copy-paste when needed)
let me know if/what more details you need

//create a CommAPI instance
var api = new CommAPI();

//start the AACommServer (note, the function has an optional parameter, please refer to the AAComm doc.)
//the function returns a status string, (Success if the string is empty)
AAComm.CommAPI.StartAACommServer();

//create and set object that defines HW channel parameters. In this case: Ethernet
var cData = new Services.ConnectionData()
cData.ControllerType = Shared.ProductTypes.AGM800_ID;
cData.CommChannelType = Shared.ChannelType.Ethernet
cDdata.ET_IP_1 = 172;
cDdata.ET_IP_2 = 1;
cDdata.ET_IP_3 = 1;
cDdata.ET_IP_4 = 101;
cData.ET_Port = 5000;

//Connect to the HW device
ConnectResult res = api.Connect(data);

----------------------------------------------------------------------------------------------------------------------------------

//create a "message" to ASYNC send to the HW (note, AACommMessage has multiple CTOR's)
//this is a NON-blocking call, control is immediately returned to the executing thread
var msg = new AACommMessage(OnReplyReceived, "AMotorOn");
api.Send(msg);

private void OnReplyDerived(object sender, AACommEventArgs e)
{
      //upon reply from HW, this callback is invoked!
}

----------------------------------------------------------------------------------------------------------------------------------

//create a "message" to SYNCsend to the HW (note, AACommMessage has multiple CTOR's)
//this is a BLOCKING call, function returns only after the HW has replied.
//execution time varies from 1 msec to 120 seconds (for very specific commands)
var msg = new AACommMessage("AMotorOn");
AACommEventArgs reply = api.SendReceive(msg);
//check controller 'reply' at reply.MessageReceived!


----------------------------------------------------------------------------------------------------------------------------------

//disconnect the comms object:
api.Disconnect()

----------------------------------------------------------------------------------------------------------------------------------

Download FW

            //please see AAComm documentation for usage/parameters/events details
            var dlFW = new AAComm.Extensions.AACommDownloadFW();

            //dlFW.OnDownloadStarted    += ()       => MyHandle, i.e. update UI
            //dlFW.OnProgress           += progress => MyHandle, i.e. update UI
            //dlFW.OnStatus             += status   => MyHandle, i.e. update UI
            //dlFW.OnProcessEnded       += result   => MyHandle, i.e. update UI

            dlFW.StartDownloadingSafe(
                api,                        //AAComm object, must be disconnected
                connectionData,             //an object specifying the connected controller type and connection
                "FullPath_MyFW_File.bin",   //full path of the FW data file
                "FullPath_MyFW_File.ver",   //full path of the FW version file
                "ContactAgitoForPassword",  //FW DL password
                false,                      //validates controller actual vs. defined in new FW Current Ratings (NA in BOOT mode, NA for AGM800)
                AACommFwInfo.Targets.Legacy);

            //The process always ends with invocation of 'OnProcessEnded',
            //with the parameter being the download state (empty string for success, error description otherwise)

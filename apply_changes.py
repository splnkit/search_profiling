import shutil
import os
import subprocess

app_list = [ app for app in os.listdir(".") if app.startswith("TA") or app.startswith("S") ]
print app_list
destination_root = "/Users/gburgett/Desktop/Workspace/Splunk_Bin/splunk_dd"
# destination_root = "/Users/gburgett/Downloads/test_apply"
destination = destination_root + "/etc/apps/%s" 
restart_command = destination_root + "/bin/splunk restart --answer-yes --accept-license"
# #create a backup directory
# shutil.copytree(SOURCE, BACKUP)
# print os.listdir(BACKUP)
for app in app_list:
    try:
        shutil.rmtree(destination % app)
    except:
        print "App not present"
    shutil.copytree("./%s" % app, destination % app)


#return_code = subprocess.call(restart_command, shell=True) 
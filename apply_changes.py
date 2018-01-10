import shutil
import os
app_list = [ app for app in os.listdir(".") if app.startswith("TA") or app.startswith("SA") ]
print app_list
destination = "/tmp/newfolder/"
# for files in source:
#     if files.endswith(".txt"):
#         shutil.copy(files,destination)
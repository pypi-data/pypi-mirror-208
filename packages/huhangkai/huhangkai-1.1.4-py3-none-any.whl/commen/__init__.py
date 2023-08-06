import os
import sys
admin_host = "http://47.96.124.102/api"
# admin_host = "http://127.0.0.1:8000"

projects_path = os.getcwd()
projects_path_list = projects_path.split(os.path.sep)
if "site-packages" in projects_path_list and "commen" in projects_path_list:
    projects_path = os.path.join(*projects_path_list[:projects_path_list.index("site-packages") - 2])
elif "service" in projects_path_list:
    projects_path = os.path.join(*projects_path_list[:projects_path_list.index("service")])
elif "testcase" in projects_path_list:
    projects_path = os.path.join(*projects_path_list[:projects_path_list.index("testcase")])
if ":" in projects_path:
    projects_path = projects_path.replace(":", ":" + os.path.sep)
else:
    projects_path = os.path.sep + projects_path
files_path = os.path.join(projects_path, "files")
service_path = os.path.join(projects_path, "service")
testcase_path = os.path.join(projects_path, "testcase")

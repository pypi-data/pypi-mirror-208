from jinjafy.jinjafy import jinjafy_comment
from jinjafy.jinjafy import jinjafy_template
from jinjafy.jinja_matlab_load import matlab_load
# from slider import latexmk
from jinjafy.textools import mat2table
import subprocess
# import os
import platform
# from subprocess import subprocess


def execute_command(command, shell=True):
    """
    This is a super dodgy command from way back in the early 3.x days. I *think* all uses are better served by regular
    subprocess.check_output(..., shell=True), but I am not completely sure, and various people have updated the function
    to make it work on linux/mac; I know that giving inputs as lists was required at some point (perhaps for args with spaces?).

    Current behavior will be subprocess.check_output, and if that works it can just be removed. Until and unless this turns out to be
    useful again, I think the function is best avoided.
    """
    # if not isinstance(command, list):
    #     command = [command]
    #
    # if not platform.uname()[0] == "Linux":
    #     result = subprocess.run(command, stdout=subprocess.PIPE, shell=shell)
    #     out = result.stdout
    # else:
    #     cmd = " ".join(command)
    #     out = subprocess.check_output(cmd, shell=shell)
    # s = out.decode("utf-8")
    # OK = True
    # return s, OK

    if isinstance(command, list):
        command = " ".join(command)
    # if not isinstance(command, list):
    #     command = [command]

    # if not platform.uname()[0] == "Linux":
    #     result = subprocess.run(command, stdout=subprocess.PIPE, shell=shell)
    #     out = result.stdout
    # else:
    #     cmd = " ".join(command)
    out = subprocess.check_output(command, shell=shell)
    s = out.decode("utf-8")
    OK = True
    return s, OK


# def get_system_name():
#     if is_win():
#         return "Win"
#     if is_compute():
#         return "thinlinc.compute.dtu.dk"
#     if is_cogsys_cluster():
#         return "cogys cluster"

# def execute_command(command, shell=True):
#     if not isinstance(command, list):
#         command = [command]
#     # if not is_compute():
#     # result = subprocess.run(command, stdout=subprocess.PIPE, shell=shell)
#     # out = result.stdout
#     # else:
#     out = subprocess.check_output(command, shell=shell)
#     s = out.decode("utf-8")
#     OK = True
#     return s, OK
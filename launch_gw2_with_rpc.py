import ctypes
import os.path
import subprocess

rpc_path = "gw2rpc.exe"
gw2_64_path = "../../Gw2-64.exe"
gw2_path = "../../Gw2.exe"
tasklist = subprocess.check_output(['tasklist'], shell=True)


def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def check_gw():
    if os.path.isfile(gw2_64_path):
        if b"Gw2-64.exe" not in tasklist:
            subprocess.Popen([gw2_64_path])
            print("Started 64")
    elif os.path.isfile(gw2_path):
        if b"Gw2.exe" not in tasklist:
            subprocess.Popen([gw2_path])
            print("Started 32")
    else:
        Mbox('Error', 'Gw2 not found. Please move the RPC files into '
             'addons\RPC\ in your GW2 installation folder.', 0)


def check_rpc():
    if os.path.isfile(rpc_path):
        if b"gw2rpc.exe" not in tasklist:
            subprocess.Popen([rpc_path])
            print("Started rpc")
    else:
        Mbox('Error', 'gw2rpc.exe not found. Please move the RPC files into '
             'addons\RPC\ in your GW2 installation folder.', 0)


if __name__ == "__main__":
    check_gw()
    check_rpc()

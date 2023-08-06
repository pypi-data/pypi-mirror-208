import os
import sys
import platform
from cos_uploader.common import basedir

def main():
    if platform.system() == "Windows":
        install_windiws_shortcut()
    base = basedir()
    config_path = os.path.join(base, "config.toml")
    if not os.path.exists(config_path):
        config_source = os.path.join(os.path.dirname(__file__), "config.toml")
        with open(config_source, "r", encoding="utf-8") as f:
            config = f.read()
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config)
        print(f"Copied example config file to {config_path}")
        print("Please edit it before using cos-uploader")


def install_windiws_shortcut():
    binary_path = os.path.join(os.path.dirname(sys.argv[0]), "cos-uploader.exe")
    script = f"""
    $shortcut = (New-Object -COM WScript.Shell).CreateShortcut("$($env:APPDATA)\Microsoft\Windows\SendTo\COS Uploader.lnk")
    $shortcut.TargetPath = "{binary_path}"
    $shortcut.Arguments = "--windows-sendto"
    $shortcut.Save()
    """
    import subprocess
    result = subprocess.run(["powershell", script], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    print("Installed COS Uploader to SendTo menu")

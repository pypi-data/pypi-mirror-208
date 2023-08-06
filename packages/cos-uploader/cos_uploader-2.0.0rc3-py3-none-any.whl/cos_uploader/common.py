import os
import sys
import toml

def basedir() -> str:
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if not home:
        print("ERROR: Home Directory Not Found", file=sys.stderr)
        sys.exit(1)
    base = os.path.join(home, ".cos-uploader")
    if not os.path.exists(base):
        os.mkdir(base)
    return base


def load_config() -> dict:
    base = basedir()
    if not os.path.exists(os.path.join(base, "config.toml")):
        print("ERROR: Config File Not Found", file=sys.stderr)
        print("Please run 'cos-uploader-install' first", file=sys.stderr)
        sys.exit(1)
    config = toml.load(os.path.join(base, "config.toml"))
    config["base"] = base
    return config

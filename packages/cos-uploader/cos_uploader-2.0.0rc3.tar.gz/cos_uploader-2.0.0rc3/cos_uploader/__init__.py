import os
import sys
import uuid
import time
import json
import argparse
import datetime
import traceback
import urllib.parse
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from cos_uploader.common import load_config


def progress_callback(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end="", file=sys.stderr, flush=True)


def get_filename(file, config):
    current_time = datetime.datetime.now() if not config["utc-time"] else datetime.datetime.utcnow()
    filename, extension = os.path.splitext(os.path.basename(file))
    params = {
        "uuid": str(uuid.uuid4()),
        "name": filename,
        "ext": extension,
        "y": current_time.strftime("%Y"),
        "mo": current_time.strftime("%m"),
        "d": current_time.strftime("%d"),
        "h": current_time.strftime("%H"),
        "min": current_time.strftime("%M"),
        "s": current_time.strftime("%S"),
        "ts": int(time.time()),
    }
    return config["prefix"] + config["filename"].format(**params)


def get_file_urls(config, key):
    domains_enabled = list(filter(
        lambda domain_type: domain_type in ["cdn", "cos", "web", "accelerate"],
        config["domains"]["enabled"]))
    if (len(domains_enabled) == 0):
        domains_enabled = ["cos"]

    domains = {}
    if "cos" in domains_enabled:
        domains["cos"] = "{bucket}.cos.{region}.myqcloud.com".format(**config)
    if "cdn" in domains_enabled:
        domains["cdn"] = config["domains"]["cdn"].format(**config)
    if "web" in domains_enabled:
        domains["web"] = config["domains"]["web"].format(**config)
    if "accelerate" in domains_enabled:
        domains["accelerate"] = "{bucket}.cos.accelerate.myqcloud.com".format(**config)

    urls = {
        domain_type: f"https://{domain}/{urllib.parse.quote(key, encoding='utf-8')}"
        for domain_type, domain in domains.items()}
    default_url = urls[domains_enabled[0]]
    return urls, default_url


def upload_to_cos(file, config, typora):
    if not (os.path.exists(file)):
        return None if typora else print(f"ERROR: File Not Found: {file}", file=sys.stderr)
    if os.path.isdir(file):
        return None if typora else print(f"WARNING: Skipping Folder: {file}", file=sys.stderr)

    client = CosS3Client(CosConfig(
        Region="accelerate" if config["oversea-upload"] else config["region"],
        SecretId=config["secret-id"],
        SecretKey=config["secret-key"]))
    key = get_filename(file, config)
    response = client.upload_file(
        Bucket=config["bucket"],
        LocalFilePath=file,
        Key=key,
        MAXThread=5,
        EnableMD5=True,
        progress_callback=progress_callback)

    file_url, default_file_url = get_file_urls(config, key)
    if typora:
        print(default_file_url)
    else:
        print("Upload Success!")
        print("{:9} {}".format("Filename:", file))
        print("{:9} {}".format("COS URL:", file_url["cos"])) if "cos" in file_url else None
        print("{:9} {}".format("CDN URL:", file_url["cdn"])) if "cdn" in file_url else None
        print("{:9} {}".format("Web URL:", file_url["web"])) if "web" in file_url else None
        print("{:9} {}".format("Acc URL:", file_url["accelerate"])) if "accelerate" in file_url else None
        print("-" * 60)
    
    history_time = datetime.datetime.now().strftime("%Y-%m")
    history_file = os.path.join(config["base"], f"history-{history_time}.ndjson")
    history = {
        "args": sys.argv,
        "file": file,
        "key": key,
        "url": file_url,
        "time": int(time.time()),
        "response": response,
    }
    with open(history_file, "a+", encoding="utf-8") as hf:
        hf.write(json.dumps(history, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description='Upload files to Tencent Cloud COS')
    parser.add_argument("files", metavar="FILE", type=str, nargs="+")
    parser.add_argument("--typora", dest="typora", action="store_true")
    parser.add_argument("--windows-sendto", dest="windows_sendto", action="store_true")
    args = parser.parse_args()

    config = load_config()    
    for file in args.files:
        try:
            upload_to_cos(file, config, args.typora)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            traceback.print_exc()
            continue
    if args.windows_sendto:
        input("Done! Press Enter to close this window...")


if __name__ == "__main__":
    main()

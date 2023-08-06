import os
import sys
import json
import argparse
import datetime
from cos_uploader.common import load_config

def main():
    parser = argparse.ArgumentParser(description='Show upload history')
    parser.add_argument("-m", "--month", dest="month", type=str, default=datetime.datetime.now().strftime("%m"))
    parser.add_argument("-y", "--year", dest="year", type=str, default=datetime.datetime.now().strftime("%Y"))
    parser.add_argument("-d", "--domain-type", dest="domain", type=str, default="cos", choices=["cos", "cdn", "web", "accelerate"])
    parser.add_argument("-r", "--raw", dest="raw", action="store_true")
    parser.add_argument("-n", "--limit", dest="limit", type=int, default=0, help="Limit the number of results, if set to 0, all results will be shown")
    args = parser.parse_args()

    year = int(args.year)
    month = int(args.month)
    if year < 2000 or year > 2100 or month < 1 or month > 12:
        print("ERROR: Invalid Year or Month", file=sys.stderr)
        sys.exit(1)
    year = str(year)
    month = str(month).zfill(2)

    config = load_config()
    file = os.path.join(config["base"], f"history-{year}-{month}.ndjson")
    if not os.path.exists(file):
        print(f"ERROR: History File '{file}' Not Found, maybe you have not uploaded any files in {year}-{month} ?", file=sys.stderr)
        sys.exit(1)
    
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        if args.limit == 0:
            lines = f.readlines()
        else:
            for _ in range(args.limit):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
    lines.reverse()
    for line in lines:
        data = json.loads(line)
        file = data.get("file")
        time = datetime.datetime.fromtimestamp(data.get("time", 0)).strftime("%Y-%m-%d %H:%M:%S %Z")
        url = data.get("url", {}).get(args.domain)
        print(f"Date: {time}")
        print(f"File: {file}")
        print(f"URL: {url}")
        if args.raw:
            print(f"RAW: {line}")
        print("-" * 60)

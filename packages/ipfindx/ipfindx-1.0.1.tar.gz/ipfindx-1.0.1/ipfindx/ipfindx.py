#!/usr/bin/python3

import argparse
import requests
import json

print('\033[;92m')
# Parse command line arguments
parser = argparse.ArgumentParser(description='Get IP address information.')
parser.add_argument('-i', '--ip', type=str, required=True, help='IP address')
parser.add_argument('-o', '--output', type=str, help='Output file name')
args = parser.parse_args()

# Make API request
url = f"http://ip-api.com/json/{args.ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
res = requests.get(url)
data = json.loads(res.text)

# Print banner
print("""\033[;92m
╭━━┳━━━┳━━━╮╱╱╱╱╱╭┳━╮╭━╮
╰┫┣┫╭━╮┃╭━━╯╱╱╱╱╱┃┣╮╰╯╭╯
╱┃┃┃╰━╯┃╰━━┳┳━╮╭━╯┃╰╮╭╯
╱┃┃┃╭━━┫╭━━╋┫╭╮┫╭╮┃╭╯╰╮
╭┫┣┫┃╱╱┃┃╱╱┃┃┃┃┃╰╯┣╯╭╮╰╮
╰━━┻╯╱╱╰╯╱╱╰┻╯╰┻━━┻━╯╰━╯V:1.0.1
////////\033[;93mMrHacker-X\033[;92m///////
""")

# Print the key-value pairs to the console
for key, value in data.items():
    print(f"\033[1;92m[+]\033[1;93m {key}:\033[1;92m {value}")

# Save the output to a file
if args.output:
    filename = args.output
else:
    filename = f"{args.ip}.txt"
with open(filename, "w") as f:
    for key, value in data.items():
        f.write(f"{key}: {value}\n")
print(f"\n\033[1;92m[✔] \033[1;93mOutput saved to:\033[1;92m {filename}")

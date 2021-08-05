#!/usr/bin/python3

import configparser
import datetime
import sys
import holidays
import urllib3
import json
import subprocess

power = None
config = configparser.ConfigParser()
config.read('/etc/tv_off.conf')

now = datetime.datetime.now()

# Hour
if now.hour < int(config['hour'].get('on', 0)) or \
        now.hour >= int(config['hour'].get('off', 24)) or \
        now in holidays.CZ():
    power = False
else:
    # Employee
    http = urllib3.PoolManager()

    logins = config['employee'].get('logins', '').split(',')

    for login in logins:
        try:
            r = http.request(
                'GET',
                'https://neznam.szn.cz/api/v2/zamestnanec/%s/status' % login,
                headers={
                    'AUTHORIZATION2': config['employee']['neznam_token']
                })
        except urllib3.exceptions.RequestError as re:
            print("[ERROR] Request error: %s" % re)
            power = None
            break

        if r.status != 200:
            print("[ERROR] Not HTTP 200: %s" % r.status)
            power = None
            break

        try:
            j = json.loads(r.data.decode('utf-8'))
        except ValueError as ve:
            print("[ERROR] Parsing JSON: %s" % ve)
            power = None
            break

        if j['data']['employee_sensor'] and \
                config['employee']['sensor'] in j['data']['employee_sensor'] and \
                j['data']['employee_is_present'] == True and \
                j['data']['employee_in_work'] == 1:
            print("%s is in work" % login)
            power = True
            break
        else:
            power = False

if power is not None:
    if power:
        cmd = config['cec-client'].get('power_on_cmd', 'on') + " 0"
        print("Turning TV on")
    else:
        cmd = "standby 0"
        print("Turning TV off")

    print(cmd)
    if config['cec-client'].get('pipe', None):
        with open(config['cec-client']['pipe'], 'w') as f:
            f.write(cmd)
    else:
        p = subprocess.Popen(['cec-client','-s'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        p.stdin.write(('%s\n' % cmd).encode('utf-8'))
        print(p.communicate()[0])
        p.stdin.close()
else:
    print("Don't know what to do, doing nothing")

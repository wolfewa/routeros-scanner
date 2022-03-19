# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import json
import paramiko

from commands.fwnat import FWNat
from commands.dns import DNS
from commands.files import Files
from commands.fwrules import FW
from commands.ports import Ports
from commands.proxy import Proxy
from commands.scheduler import Scheduler
from commands.socks import Socks
from commands.users import Users
from commands.version import Version


def main(args):
    all_data = {}
    commands = [Version(), Scheduler(), Files(), FWNat(), Proxy(), Socks(), DNS(), Users(), Ports(), FW()]

    print(f'Mikrotik ip address: {args.ip}\n')

    with paramiko.SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #updated the connection call to be an if elif for the different options of user name password, user name and supplied key file and a default of username and default public key 
        if args.password != '':
            ssh_client.connect(hostname=args.ip, port=args.port, username=args.userName, password=args.password)
        elif args.keyFile != '':
            ssh_client.connect(hostname=args.ip, port=args.port, username=args.userName, pkey=args.keyFile)
        else:
            ssh_client.connect(hostname=args.ip, port=args.port, username=args.userName) #use defalue pblic key auth ~/.ssh


        for command in commands:
            res = command.run_ssh(ssh_client)
            all_data[command.__name__] = res

        if args.J:
            print(json.dumps(all_data, indent=4))
        else:
            print_txt_results(all_data)


def print_txt_results(res):
    for command in res:
        print(f'{command}:')
        for item in res[command]:
            if res[command][item]:
                print(f'\t{item}:')
                if type(res[command][item]) == list:
                    data = '\n\t\t'.join(json.dumps(i) for i in res[command][item])
                else:
                    data = res[command][item]
                print(f'\t\t{data}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', help='The tested Mikrotik IP address', required=True)
    parser.add_argument('-p', '--port', help='The tested Mikrotik SSH port', required=True)
    parser.add_argument('-u', '--userName', help='User name with admin Permissions', required=True)
    parser.add_argument('-ps', '--password', help='The password of the given user name', default='')
    parser.add_argument('-kf', '--keyFile', help='The path to the public key file', default='') #Added argument for passing information on key file 
    parser.add_argument('-J', help='Print the results as json format', action='store_true')
    args = parser.parse_args()

    main(args)

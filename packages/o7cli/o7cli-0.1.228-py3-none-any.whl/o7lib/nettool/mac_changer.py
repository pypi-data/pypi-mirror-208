"""MAC Changer for Windows, Linux and MacOS"""
import subprocess
import argparse
import re


def get_arguments():
    """Method to get arguments from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC address', required=True)
    parser.add_argument('-m', '--mac', dest='new_mac', help='New MAC address', required=True)
    return parser.parse_args()

def change_mac(interface : str, new_mac : str):
    """Method to change MAC address"""
    # Notes
    # 1. The command 'ifconfig' is used to display the current MAC address of the interface
    # In docker, container needs to run with --privileged flag
    print(f'[+] Changing MAC address for {interface} to {new_mac}')
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

def get_current_mac(interface : str) -> str:
    """Method to get MAC address"""

    ifconfig_result = subprocess.check_output(["ifconfig", interface]).decode("utf-8")
    mac_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfig_result)

    if mac_search_result:
        return mac_search_result.group(0)

    print("[-] Could not read MAC address.")
    return None


if __name__ == '__main__':

    args  = get_arguments()

    current_mac = get_current_mac(args.interface)
    print(f'Current MAC = {current_mac}')

    change_mac(args.interface, args.new_mac)

    current_mac = get_current_mac(args.interface)

    if current_mac.upper() == args.new_mac.upper():
        print(f'[+] MAC address was successfully changed to {current_mac}')
    else:
        print('[-] MAC address did not get changed.')

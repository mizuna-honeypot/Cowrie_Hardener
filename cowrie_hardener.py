#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import random
import string
import sys
import shutil

# --- Configuration ---
# Please specify the 'etc' directory according to your Cowrie installation path
COWRIE_ETC_PATH = 'etc/'
# List of weak default usernames (root is excluded for special handling)
WEAK_USERNAMES = ['phil', 'admin', 'user', 'guest', 'test']

# --- Automatic Path Generation ---
COWRIE_CONFIG_PATH = os.path.join(COWRIE_ETC_PATH, 'cowrie.cfg')
USERDB_PATH = os.path.join(COWRIE_ETC_PATH, 'userdb.txt')
HONEYFS_PATH = os.path.abspath(os.path.join(COWRIE_ETC_PATH, '..', 'honeyfs'))
FAKE_PASSWD_PATH = os.path.join(HONEYFS_PATH, 'etc', 'passwd')

# --- Random Data Generation Functions ---
def generate_ssh_banner():
    versions = ['8.2p1', '8.9p1', '9.2p1', '9.7p1']
    distros = ['Ubuntu-10ubuntu2.10', 'Debian-10+deb11u1', '']
    return f"SSH-2.0-OpenSSH_{random.choice(versions)} {random.choice(distros)}".strip()

def generate_hostname():
    prefixes = ['web', 'db', 'app', 'srv', 'host', 'dev']
    domains = ['internal', 'local', 'corp', 'lan']
    return f"{random.choice(prefixes)}{random.randint(1, 200)}.{random.choice(domains)}"
    
def generate_kernel_version():
    bases = ['5.15.0', '6.1.0', '6.6.0']
    sub_versions = random.randint(50, 150)
    return f"{random.choice(bases)}-{sub_versions}-generic"

def generate_random_string(length=16):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def generate_random_credentials(length=14):
    username = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    password_chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.choice(password_chars) for i in range(length))
    return username, password

def backup_file(filepath):
    """Creates a backup of a file. Warns if the file does not exist."""
    if not os.path.exists(filepath):
        print(f"⚠️  Warning: File not found: {filepath}. Skipping backup.")
        return False
    backup_path = f"{filepath}.bak.{random.randint(1000,9999)}"
    try:
        shutil.copy2(filepath, backup_path)
        print(f"✅ Backup created successfully: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

# --- Main Processing Functions ---
def update_cowrie_cfg():
    """Updates cowrie.cfg to spoof system information."""
    print("\n📝 Hardening `cowrie.cfg` settings...")
    if not os.path.exists(COWRIE_CONFIG_PATH):
        print("  -> `cowrie.cfg` not found, skipping process.")
        return

    backup_file(COWRIE_CONFIG_PATH)
    config = configparser.ConfigParser()
    config.read(COWRIE_CONFIG_PATH)

    if config.has_section('ssh'):
        config.set('ssh', 'accept_root_password', 'false')
        print("  -> Disabled special root login (accept_root_password=false).")
        
        new_banner = generate_ssh_banner()
        config.set('ssh', 'version_string', new_banner)
        print(f"  -> Changed SSH banner to: {new_banner}")
        
        new_host = generate_hostname()
        config.set('ssh', 'hostname', new_host)
        print(f"  -> Changed hostname to: {new_host}")
    
    if not config.has_section('shell'):
        config.add_section('shell')
        print("  -> [shell] section not found, creating a new one.")
    new_kernel = generate_kernel_version()
    config.set('shell', 'kernel_version', new_kernel)
    print(f"  -> Spoofed kernel version to: {new_kernel}")

    if config.has_section('proxy'):
        random_user = generate_random_string()
        random_pass = generate_random_string()
        config.set('proxy', 'backend_user', random_user)
        config.set('proxy', 'backend_pass', random_pass)
        print(f"  -> Randomized default proxy credentials.")

    with open(COWRIE_CONFIG_PATH, 'w') as f:
        config.write(f)
    print("  -> Successfully saved changes to `cowrie.cfg`.")

def update_userdb():
    """Cleans weak users from userdb.txt, changes the root password, and adds a new random user. Creates the file if it doesn't exist."""
    print("\n🔑 Cleaning and hardening `userdb.txt`...")
    lines = []
    
    if os.path.exists(USERDB_PATH):
        # If the file exists, back it up and read its content
        backup_file(USERDB_PATH)
        with open(USERDB_PATH, 'r') as f:
            lines = f.readlines()
    else:
        # If the file doesn't exist, print a message indicating it will be created
        print(f"  -> `userdb.txt` not found. A new file will be created.")

    # Create a list excluding weak users and root
    strong_users = [line for line in lines if line.strip() and line.strip().split(':')[0] not in WEAK_USERNAMES + ['root']]
    
    if lines: # Only display a message if the original file had content
        print(f"  -> Removed {len(lines) - len(strong_users)} weak/default user(s).")

    # Generate and add a new root password and a new random user
    _, root_password = generate_random_credentials()
    new_username, new_password = generate_random_credentials()
    
    strong_users.append(f"root:x:{root_password}\n")
    strong_users.append(f"{new_username}:x:{new_password}\n")
    
    # Write the final list back to the file
    with open(USERDB_PATH, 'w') as f:
        f.writelines(strong_users)
        
    print("  -> Changed `root` password to a strong, random one.")
    print("  -> Added a new random user.")
    return {"root": root_password, "new_user": (new_username, new_password)}
    
def update_honeyfs(new_username):
    """Removes traces of weak users from the fake /etc/passwd in honeyfs."""
    print("\n📂 Cleaning up the fake file system (`honeyfs`)...")
    if not os.path.exists(FAKE_PASSWD_PATH): return
    if not backup_file(FAKE_PASSWD_PATH): return

    with open(FAKE_PASSWD_PATH, 'r') as f:
        lines = f.readlines()

    strong_lines = [line for line in lines if line.strip().split(':')[0] not in WEAK_USERNAMES]
    print("  -> Removed traces of weak users from the fake /etc/passwd.")

    if new_username:
        uid = random.randint(1001, 2000)
        strong_lines.append(f"{new_username}:x:{uid}:{uid}:{new_username},,,:/home/{new_username}:/bin/bash\n")
        print("  -> Added the new user's entry to the fake /etc/passwd for consistency.")

    with open(FAKE_PASSWD_PATH, 'w') as f:
        f.writelines(strong_lines)
    print("  -> Successfully saved changes to the fake /etc/passwd.")

def main():
    print("🚀 Starting Cowrie Hardening Tool [Auto-Create Edition]...")
    
    update_cowrie_cfg()
    new_creds = update_userdb()
    
    if new_creds and new_creds.get("new_user"):
        update_honeyfs(new_creds["new_user"][0])

    if new_creds:
        print("\n" + "="*50)
        print("✨ New secure login credentials have been generated ✨")
        print(f"   New password for root: {new_creds['root']}")
        print(f"   Additional username: {new_creds['new_user'][0]}")
        print(f"   Password for additional user: {new_creds['new_user'][1]}")
        print("="*50 + "\n")
        
    print("\n🎉 All hardening processes have been completed!")
    print("🔴【CRITICAL】You must restart the Cowrie service to apply these changes.")
    print("   Example: sudo systemctl restart cowrie")
    
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ Error: This script modifies system files and must be run with administrative privileges (sudo).")
        sys.exit(1)
    
    if not os.path.exists(COWRIE_ETC_PATH):
         print(f"❌ Error: Configuration directory not found: {COWRIE_ETC_PATH}")
         print("   Please correct the 'COWRIE_ETC_PATH' variable in the script to point to your Cowrie's 'etc' directory.")
         sys.exit(1)
         
    main()

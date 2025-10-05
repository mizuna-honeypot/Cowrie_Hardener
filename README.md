# Cowrie Hardener 🛡️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)

An automated hardening script to erase the fingerprints of your Cowrie honeypot and evade detection.

---
## Overview

Cowrie is an excellent SSH honeypot, but its default settings are widely known. Attackers and researchers can easily identify a server as a honeypot by scanning for these Cowrie-specific "fingerprints."

`cowrie_hardener.py` was developed to win the **cat-and-mouse game** against honeypot detection tools. By running this script just once, you can automatically patch Cowrie's known weaknesses and disguise your honeypot as a legitimate server.

---
## Key Features

This tool automatically hardens the following items:

* ✅ **Randomizes SSH Banner**: Replaces the default SSH version string with a more common and realistic one.
* ✅ **Randomizes Hostname**: Changes the default hostname (e.g., `svr04`) to a random name like `web112.internal`.
* ✅ **Spoofs Kernel Version**: Disguises the known, outdated kernel version with a more modern version string.
* ✅ **Eliminates Weak Credentials**: Completely removes default users like `phil:phil` and `admin:admin` from `userdb.txt`.
* ✅ **Strengthens Root Password**: Keeps the `root` user but sets its password to a strong, random string.
* ✅ **Disables Backdoor Login**: Disables the special setting (`accept_root_password`) that allows login with `root:root`.
* ✅ **Neutralizes Proxy Credentials**: Randomizes the default credentials for the separate proxy authentication path.
* ✅ **Maintains Filesystem Consistency**: Erases traces of default users from the fake `/etc/passwd` file.

---
## Prerequisites

* Python 3.x
* A running Cowrie honeypot environment.

---
## Usage

**⚠️ WARNING: This script directly modifies system configuration files. Always create a backup of your entire `etc` directory before running it.**

1.  **Clone the repository or download the script.**
    ```bash
    git clone https://github.com/mizuna-honeypot/cowrie_hardener.git
    cd cowrie_hardener
    ```

2.  **Edit the path in the script.**
    Open the `cowrie_hardener.py` file and modify the `COWRIE_ETC_PATH` variable at the top to the absolute path of your Cowrie's `etc` directory.
    ```python
    # Example: If Cowrie is installed in /opt/cowrie/
    COWRIE_ETC_PATH = '/opt/cowrie/etc/'
    ```

3.  **Run the script with administrative privileges.**
    ```bash
    sudo python3 cowrie_hardener.py
    ```

4.  **Restart the Cowrie service.**
    **【CRITICAL】** You must restart Cowrie to apply the changes.
    ```bash
    # If using systemd
    sudo systemctl restart cowrie

    # Or, if running directly with Cowrie's scripts
    # /path/to/your/cowrie/bin/cowrie restart
    ```

---
## Contributing

Bug reports, feature requests, and pull requests are welcome.

---
## Disclaimer

* Use this tool at your own risk. The author is not responsible for any damage.
* It is strongly recommended to back up your configuration files before execution.

---
## License

This project is licensed under the [MIT License](LICENSE).

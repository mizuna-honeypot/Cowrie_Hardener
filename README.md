# Cowrie Hardener 🛡️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)

Cowrieハニーポットの「指紋（フィンガープリント）」を自動的に消去し、検知を回避するための堅牢化ツールです。

---
## 概要

Cowrieは非常に優れたSSHハニーポットですが、そのデフォルト設定は広く知られています。そのため、攻撃者や研究者は、Cowrie特有の設定（「指紋」）をスキャンすることで、それが本物のシステムではなくハニーポットであることを見抜いてしまいます。

この`cowrie_hardener.py`は、ハニーポット検知ツールとの**「いたちごっこ（Cat and Mouse Game）」**に勝利するために開発されました。このスクリプトを一度実行するだけで、Cowrieの既知の弱点を自動的に修正し、あなたのハニーポットを本物のサーバーのように偽装します。

---
## 主な機能

このツールは、以下の項目を自動で堅牢化（ハーデニング）します。

* ✅ **SSHバナーのランダム化**: デフォルトのSSHバージョン文字列を、より一般的で現実的なものに置き換えます。
* ✅ **ホスト名のランダム化**: デフォルトのホスト名（`svr04`など）を、`web112.internal`のようなランダムな名前に変更します。
* ✅ **カーネルバージョンの偽装**: 既知の古いカーネルバージョンを、よりモダンなバージョン文字列に偽装します。
* ✅ **弱い認証情報の排除**: `phil:phil`や`admin:admin`のようなデフォルトユーザーを`userdb.txt`から完全に削除します。
* ✅ **`root`パスワードの強化**: `root`ユーザーは残しつつ、パスワードを強力なランダム文字列に設定します。
* ✅ **隠し設定の無効化**: `root:root`でログインできてしまう特殊な設定（`accept_root_password`）を無効化します。
* ✅ **プロキシ認証情報の無効化**: 別の認証経路であるプロキシ用のデフォルト認証情報をランダム化します。
* ✅ **偽ファイルシステムの一貫性維持**: 偽の`/etc/passwd`ファイルからデフォルトユーザーの痕跡を消去します。

---
## 必要なもの

* Python 3.x
* Cowrieハニーポットの稼働環境

---
## 使い方

**⚠️ 警告: このスクリプトはシステムの設定ファイルを直接書き換えます。実行前に必ず`etc`ディレクトリ全体のバックアップを取得してください。**

1.  **リポジトリをクローンまたはスクリプトをダウンロードします。**
    ```bash
    git clone https://github.com/mizuna-honeypot/cowrie_hardener.git
    cd cowrie_hardener
    ```

2.  **スクリプト内のパスを編集します。**
    `cowrie_hardener.py`ファイルを開き、冒頭にある`COWRIE_ETC_PATH`の値を、あなたの環境のCowrieの`etc`ディレクトリの絶対パスに修正してください。
    ```python
    # 例: Cowrieが/opt/cowrie/にインストールされている場合
    COWRIE_ETC_PATH = '/opt/cowrie/etc/'
    ```

3.  **管理者権限でスクリプトを実行します。**
    ```bash
    sudo python3 cowrie_hardener.py
    ```

4.  **Cowrieサービスを再起動します。**
    **【最重要】** 変更を適用するには、必ずCowrieを再起動してください。
    ```bash
    # Systemdの場合
    sudo systemctl restart cowrie

    # または、Cowrieのスクリプトで直接実行する場合
    # /path/to/your/cowrie/bin/cowrie restart
    ```
---
## 貢献 (Contributing)

バグ報告、機能追加の提案、プルリクエストなどを歓迎します。

---
## 注意事項

* このツールは自己責任で使用してください。いかなる損害についても作者は責任を負いません。
* 実行前に必ず設定ファイルのバックアップを取ることを強く推奨します。

---
## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import random
import string
import sys
import shutil

# --- 設定 ---
# Cowrieのインストールパスに合わせて、etcディレクトリの「絶対パス」を指定してください
# 例: COWRIE_ETC_PATH = '/home/ubuntu/cowrie/etc/'
COWRIE_ETC_PATH = 'etc/'
WEAK_USERNAMES = ['phil', 'admin', 'user', 'guest', 'test']

# --- パスの自動生成 ---
COWRIE_CONFIG_PATH = os.path.join(COWRIE_ETC_PATH, 'cowrie.cfg')
USERDB_PATH = os.path.join(COWRIE_ETC_PATH, 'userdb.txt')
HONEYFS_PATH = os.path.abspath(os.path.join(COWRIE_ETC_PATH, '..', 'honeyfs'))
FAKE_PASSWD_PATH = os.path.join(HONEYFS_PATH, 'etc', 'passwd')

# --- ランダムデータ生成関数 ---
def generate_ssh_banner():
    versions = ['8.9p1', '9.2p1', '9.7p1']
    distros = ['Ubuntu-10ubuntu2.12', 'Debian-10+deb11u2', '']
    return f"SSH-2.0-OpenSSH_{random.choice(versions)} {random.choice(distros)}".strip()

def generate_hostname():
    prefixes = ['web', 'db', 'app', 'srv', 'host', 'dev']
    return f"{random.choice(prefixes)}{random.randint(10, 200)}"

def generate_prompt(hostname):
    user = "admin"
    return f"{user}@{hostname}:~$"

def generate_kernel_version():
    bases = ['5.15.0', '6.2.0', '6.5.0']
    sub_versions = random.randint(80, 150)
    return f"{random.choice(bases)}-{sub_versions}-generic"

def generate_random_string(length=16):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def generate_random_credentials(length=14):
    username = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    password_chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.choice(password_chars) for i in range(length))
    return username, password

def backup_file(filepath):
    if not os.path.exists(filepath):
        print(f"⚠️  警告: ファイルが見つかりません: {filepath}。")
        return False
    backup_path = f"{filepath}.bak.{random.randint(1000,9999)}"
    try:
        shutil.copy2(filepath, backup_path)
        print(f"✅ バックアップを作成しました: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ バックアップ作成中にエラーが発生しました: {e}")
        return False

# --- メイン処理関数 ---
def update_cowrie_cfg():
    print("\n📝 `cowrie.cfg` の設定を強化します...")
    
    if not os.path.exists(COWRIE_CONFIG_PATH):
        dist_path = os.path.join(COWRIE_ETC_PATH, 'cowrie.cfg.dist')
        if os.path.exists(dist_path):
            try:
                shutil.copy2(dist_path, COWRIE_CONFIG_PATH)
                print(f"  -> `cowrie.cfg` をテンプレートから作成しました。")
            except Exception as e:
                print(f"❌ `cowrie.cfg`の作成に失敗しました: {e}")
                return
        else:
            print("  -> `cowrie.cfg`もテンプレートも見つかりません。スキップします。")
            return

    backup_file(COWRIE_CONFIG_PATH)
    config = configparser.ConfigParser()
    config.read(COWRIE_CONFIG_PATH)

    new_host = generate_hostname()
    
    # 【最終改善】[honeypot]セクションのホスト名も偽装する
    if config.has_section('honeypot'):
        config.set('honeypot', 'hostname', new_host)
        print(f"  -> メインホスト名を偽装しました: {new_host}")

    if config.has_section('ssh'):
        config.set('ssh', 'accept_root_password', 'true')
        print("  -> [収集モード] `root`の特別ログインを有効化しました。")
        
        config.set('ssh', 'version_string', generate_ssh_banner())
        # SSHのホスト名はメインホスト名と一致させる
        config.set('ssh', 'hostname', new_host)
        print(f"  -> SSH関連のホスト名も一致させました。")
    
    if not config.has_section('shell'):
        config.add_section('shell')
    
    config.set('shell', 'kernel_version', generate_kernel_version())
    config.set('shell', 'prompt', generate_prompt(new_host))
    print("  -> カーネルバージョンとシェルプロンプトを偽装しました。")

    if config.has_section('proxy'):
        config.set('proxy', 'backend_user', generate_random_string())
        config.set('proxy', 'backend_pass', generate_random_string())
        print(f"  -> プロキシのデフォルト認証情報をランダム化しました。")

    with open(COWRIE_CONFIG_PATH, 'w') as f:
        config.write(f)
    print("  -> `cowrie.cfg` への変更を保存しました。")

def update_userdb():
    print("\n🔑 `userdb.txt` を設定し、`root`でのログインを許可します...")
    lines = []
    if os.path.exists(USERDB_PATH):
        backup_file(USERDB_PATH)
        with open(USERDB_PATH, 'r') as f: lines = f.readlines()
    else:
        print(f"  -> `userdb.txt`が見つかりません。新しいファイルを作成します。")

    strong_users = [l for l in lines if l.strip() and l.strip().split(':')[0] not in WEAK_USERNAMES + ['root']]
    if lines: print(f"  -> {len(lines) - len(strong_users)}件の弱い/デフォルトユーザーを削除しました。")
    
    strong_users.append("root:x:*\n")
    print("  -> [収集モード] `root`が任意のパスワードを受け入れるように設定しました。")
    
    new_username, new_password = generate_random_credentials()
    strong_users.append(f"{new_username}:x:{new_password}\n")
    print("  -> 現実味を出すために、新しいランダムなユーザーを追加しました。")
    
    with open(USERDB_PATH, 'w') as f: f.writelines(strong_users)
    return new_username
    
def update_honeyfs(new_username):
    print("\n📂 偽ファイルシステム (`honeyfs`) をクリーンアップします...")
    if not os.path.exists(FAKE_PASSWD_PATH): return
    backup_file(FAKE_PASSWD_PATH)
    with open(FAKE_PASSWD_PATH, 'r') as f: lines = f.readlines()
    strong_lines = [l for l in lines if l.strip().split(':')[0] not in WEAK_USERNAMES]
    if new_username:
        uid = random.randint(1001, 2000)
        strong_lines.append(f"{new_username}:x:{uid}:{uid}:{new_username},,,:/home/{new_username}:/bin/bash\n")
    with open(FAKE_PASSWD_PATH, 'w') as f: f.writelines(strong_lines)
    print("  -> 偽/etc/passwdから弱いユーザーの痕跡を削除しました。")

def main():
    print("🚀 Cowrie堅牢化ツール【最終・完全版】を開始します...")
    
    update_cowrie_cfg()
    new_user = update_userdb()
    update_honeyfs(new_user)
        
    print("\n🎉 全ての堅牢化処理が完了しました！")
    print("✨ [収集モード]で設定完了。`root`で任意のパスワードでログイン可能です。")
    print("🔴【最重要】変更を適用するには、必ずCowrieサービスを再起動してください。")
    
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ エラー: 管理者権限(sudo)で実行してください。")
        sys.exit(1)
    if not os.path.exists(COWRIE_ETC_PATH):
         print(f"❌ エラー: 設定ディレクトリが見つかりません: {COWRIE_ETC_PATH}")
         print("   スクリプト内の 'COWRIE_ETC_PATH' を正しい絶対パスに修正してください。")
         sys.exit(1)
    main()

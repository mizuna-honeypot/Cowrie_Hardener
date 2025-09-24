#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import random
import string
import sys
import shutil

# --- 設定項目 ---
# Cowrieのインストールパスに合わせて etc ディレクトリを指定してください
COWRIE_ETC_PATH = '/home/ubuntu/cowrie/etc/'
# 弱いとされるデフォルトのユーザー名リスト (rootは特別扱いするため除外)
WEAK_USERNAMES = ['phil', 'admin', 'user', 'guest', 'test']

# --- パスの自動生成 ---
COWRIE_CONFIG_PATH = os.path.join(COWRIE_ETC_PATH, 'cowrie.cfg')
USERDB_PATH = os.path.join(COWRIE_ETC_PATH, 'userdb.txt')
HONEYFS_PATH = os.path.abspath(os.path.join(COWRIE_ETC_PATH, '..', 'honeyfs'))
FAKE_PASSWD_PATH = os.path.join(HONEYFS_PATH, 'etc', 'passwd')

# --- ランダムデータ生成関数 ---
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
    """汎用的なランダム文字列を生成する"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def generate_random_credentials(length=14):
    username = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    password_chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.choice(password_chars) for i in range(length))
    return username, password

def backup_file(filepath):
    if not os.path.exists(filepath):
        print(f"⚠️  警告: ファイルが見つかりません: {filepath}。スキップします。")
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
    """cowrie.cfgを更新してシステム情報を偽装する"""
    print("\n📝 `cowrie.cfg` の設定を強化します...")
    if not backup_file(COWRIE_CONFIG_PATH): return

    config = configparser.ConfigParser()
    config.read(COWRIE_CONFIG_PATH)

    # [ssh]セクション
    if config.has_section('ssh'):
        config.set('ssh', 'accept_root_password', 'false')
        print("  -> `root`の特別ログインを無効化しました (accept_root_password=false)。")
        
        new_banner = generate_ssh_banner()
        config.set('ssh', 'version_string', new_banner)
        print(f"  -> SSHバナーを変更しました: {new_banner}")
        
        new_host = generate_hostname()
        config.set('ssh', 'hostname', new_host)
        print(f"  -> ホスト名を変更しました: {new_host}")
    
    # [shell] セクション
    if not config.has_section('shell'):
        config.add_section('shell')
        print("  -> [shell]セクションが見つからなかったため、新規作成しました。")
    new_kernel = generate_kernel_version()
    config.set('shell', 'kernel_version', new_kernel)
    print(f"  -> カーネルバージョンを偽装しました: {new_kernel}")

    # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
    # 【追加機能】プロキシ認証情報を無効化する
    # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
    if config.has_section('proxy'):
        random_user = generate_random_string()
        random_pass = generate_random_string()
        config.set('proxy', 'backend_user', random_user)
        config.set('proxy', 'backend_pass', random_pass)
        print(f"  -> プロキシのデフォルト認証情報をランダム化しました。")

    with open(COWRIE_CONFIG_PATH, 'w') as f:
        config.write(f)
    print("  -> `cowrie.cfg` の保存が完了しました。")

def update_userdb():
    """userdb.txtから弱いユーザーを削除し、rootのパスワードを変更し、新しいユーザーを追加する"""
    print("\n🔑 `userdb.txt` をクリーンアップ＆強化します...")
    if not backup_file(USERDB_PATH): return None

    with open(USERDB_PATH, 'r') as f:
        lines = f.readlines()
    
    strong_users = [line for line in lines if line.strip().split(':')[0] not in WEAK_USERNAMES + ['root']]
    print(f"  -> {len(lines) - len(strong_users)}件の弱い/デフォルトユーザーを削除しました。")

    _, root_password = generate_random_credentials()
    new_username, new_password = generate_random_credentials()
    
    strong_users.append(f"root:x:{root_password}\n")
    strong_users.append(f"{new_username}:x:{new_password}\n")
    
    with open(USERDB_PATH, 'w') as f:
        f.writelines(strong_users)
        
    print("  -> `root`のパスワードを強力なものに変更しました。")
    print("  -> 新しいランダムなユーザーを追加しました。")
    return {"root": root_password, "new_user": (new_username, new_password)}
    
def update_honeyfs(new_username):
    """honeyfs内の偽/etc/passwdから弱いユーザーの痕跡を削除する"""
    print("\n📂 偽ファイルシステム (`honeyfs`) をクリーンアップします...")
    if not os.path.exists(FAKE_PASSWD_PATH): return
    if not backup_file(FAKE_PASSWD_PATH): return

    with open(FAKE_PASSWD_PATH, 'r') as f:
        lines = f.readlines()

    strong_lines = [line for line in lines if line.strip().split(':')[0] not in WEAK_USERNAMES]
    print("  -> 偽/etc/passwdから弱いユーザーの痕跡を削除しました。")

    if new_username:
        uid = random.randint(1001, 2000)
        strong_lines.append(f"{new_username}:x:{uid}:{uid}:{new_username},,,:/home/{new_username}:/bin/bash\n")
        print("  -> 偽/etc/passwdに新しいユーザーのエントリを追加しました。")

    with open(FAKE_PASSWD_PATH, 'w') as f:
        f.writelines(strong_lines)
    print("  -> 偽/etc/passwdの保存が完了しました。")

def main():
    print("🚀 Cowrie 【真・完成版】堅牢化ツールを開始します...")
    
    update_cowrie_cfg()
    new_creds = update_userdb()
    
    if new_creds and new_creds.get("new_user"):
        update_honeyfs(new_creds["new_user"][0])

    if new_creds:
        print("\n" + "="*50)
        print("✨ 新しい安全なログイン情報が生成されました ✨")
        print(f"   rootの新しいパスワード: {new_creds['root']}")
        print(f"   追加ユーザー名: {new_creds['new_user'][0]}")
        print(f"   追加ユーザーのパスワード: {new_creds['new_user'][1]}")
        print("="*50 + "\n")
        
    print("\n🎉 全ての堅牢化処理が完了しました！")
    print("🔴【最重要】変更を適用するには、必ずCowrieサービスを再起動してください。")
    print("   例: sudo systemctl restart cowrie")
    
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ エラー: このスクリプトはシステムファイルを書き換えるため、管理者権限(sudo)で実行してください。")
        sys.exit(1)
    
    if not os.path.exists(COWRIE_ETC_PATH):
         print(f"❌ エラー: 設定ディレクトリが見つかりません: {COWRIE_ETC_PATH}")
         print("   スクリプト内の 'COWRIE_ETC_PATH' をCowrieの'etc'ディレクトリの正しいパスに修正してください。")
         sys.exit(1)
         
    main()

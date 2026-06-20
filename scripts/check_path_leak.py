#!/usr/bin/env python3
import sys
import subprocess
import os

def main():
    # リポジトリのルートディレクトリを取得
    # スクリプトの位置 (scripts/check_path_leak.py) から2階層上
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    parent_dir = os.path.dirname(repo_root)

    # ユーザー名を取得してホームディレクトリや "Users/ユーザー名" のパターンを作成
    username = os.environ.get('USERNAME') or os.environ.get('USER')
    home_dir = os.path.expanduser('~')

    leak_patterns = []

    # リポジトリルートより上の親ディレクトリパスをパターンに追加
    if parent_dir:
        leak_patterns.append(parent_dir.lower())
        # スラッシュ/バックスラッシュのバリエーションを追加
        leak_patterns.append(parent_dir.replace('\\', '/').lower())
        leak_patterns.append(parent_dir.replace('/', '\\').lower())

    # ホームディレクトリのパスをパターンに追加
    if home_dir:
        leak_patterns.append(home_dir.lower())
        leak_patterns.append(home_dir.replace('\\', '/').lower())
        leak_patterns.append(home_dir.replace('/', '\\').lower())

    # "Users/ユーザー名" や "Users\ユーザー名" を追加
    if username:
        leak_patterns.append(f"users/{username}".lower())
        leak_patterns.append(f"users\\{username}".lower())

    # 重複を除去してクリーンアップ
    leak_patterns = list(set([p for p in leak_patterns if p]))

    # jj diff --git を実行して差分を取得
    try:
        diff_output = subprocess.check_output(
            ["jj", "diff", "--git"],
            cwd=repo_root,
            stderr=subprocess.STDOUT
        ).decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError as e:
        print(f"Error running jj diff: {e.output.decode('utf-8', errors='ignore')}")
        sys.exit(1)
    except FileNotFoundError:
        print("jj command not found. Skipping path leak check.")
        sys.exit(0)

    # 追加された行 (+) に漏洩パターンが含まれているかチェック
    leaked_lines = []
    current_file = "Unknown file"

    for line in diff_output.splitlines():
        if line.startswith('+++ b/'):
            current_file = line[6:]
        elif line.startswith('+') and not line.startswith('+++'):
            content = line[1:].lower()
            for pattern in leak_patterns:
                if pattern in content:
                    leaked_lines.append((current_file, line))
                    break

    if leaked_lines:
        print("=== ⚠️ 警告: ローカル絶対パスの漏洩を検知しました ===")
        print("以下の変更行に、リポジトリルートより上の階層（ホームディレクトリ等）を示すパスが含まれています:")
        for file, line in leaked_lines:
            print(f"ファイル: {file}")
            print(f"  行: {line}")
        print("====================================================")
        sys.exit(1)

    print("=== ローカル絶対パス漏洩チェック: OK ===")
    sys.exit(0)

if __name__ == '__main__':
    main()

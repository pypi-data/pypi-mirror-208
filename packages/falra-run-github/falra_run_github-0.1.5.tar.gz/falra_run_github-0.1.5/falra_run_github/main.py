import argparse
import os
import shutil
import subprocess
import requests
import sys
import ast
import time
from shlex import quote as shlex_quote


def is_git_installed():
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_git():
    try:
        print("Install git...")
        subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
        print("git install success!")
    except subprocess.CalledProcessError as e:
        print("git install failed, error:")
        print(e)
        sys.exit(1)


# 2023-04-21 this version can download full source code files
def download_files_from_github(repo_url, local_path, token):

    # Check if git is installed or not
    try:
        if not is_git_installed():
            print("Git is not installed！ Trigger auto git install from apt-get..")
            install_git()
        else:
            print("Git installed！")
    except Exception as e:
        print(f"""[download_files_from_github] git install check fail.. skip! error:{e}""")

    # 檢查本地路徑是否存在，如果不存在則創建，存在則刪除乾淨
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    else:
        clean_user_repo(repo_path=local_path)

    # 將存儲庫URL更改為使用訪問令牌
    repo_url = repo_url.replace("https://", f"https://{token}@")

    try:
        # 執行 git clone
        print("Git clone ...start")
        os.system(f"""git clone {repo_url} {local_path}""")
        print("Git clone ...success")
    except Exception as e:
        print(f"""[download_files_from_github] git clone fail.. skip! error:{e}""")


def download_github_repo(repo_url, access_token, repo_name, work_dir=""):
    # 解析出 repo 的 owner 和 name
    _, owner, name = repo_url.rstrip('/').rsplit('/', 2)

    # 創建新目錄來存儲 repo 的內容
    if not os.path.exists("user-repo"):
        os.mkdir("user-repo")

    if work_dir == "":
        work_dir = repo_name

    work_path = os.path.join("user-repo", work_dir)
    if not os.path.exists(work_path):
        os.mkdir(work_path)

    # 下載每個文件並存儲到本地
    try:
        download_files_from_github(repo_url=repo_url, local_path=work_path, token=access_token)
    except Exception as e:
        # 如果 下載 產生錯誤，將錯誤訊息寫到檔案中
        print(f"""[Github download ERROR!!] repo_url:  {repo_url}. ERROR_msg：{e}""")


def install_requirements(repo_name, requirements_file_path="requirements.txt"):
    # 獲取 main.py 的路徑
    repo_name = os.path.join("user-repo", repo_name)
    # todo: install requirements
    # 檢查 main.py 是否存在
    if not os.path.exists(requirements_file_path):
        print("reauirement install failed, requirements.txt not found")
    return

def run_main_py(work_dir, output_file="falra_output.txt", py_name="main.py", arg=[]):
    # 獲取 main.py 的路徑
    repo_name = os.path.join("user-repo", work_dir)
    # 已經更改為進入 repo 子資料夾去執行 main.py
    main_path = py_name
    #main_path = os.path.join(repo_name, py_name)

    # 設置子資料夾的路徑
    sub_dir = repo_name

    # 儲存當前工作目錄
    current_dir = os.getcwd()

    # 更改工作目錄到子資料夾
    os.chdir(sub_dir)

    # 檢查 main.py 是否存在
    if not os.path.exists(main_path):
        print("Error: main.py not found")
        return

    # 清除上一次的 falra_output.txt
    if os.path.exists(output_file):
        os.remove(output_file)
    # 執行命令
    print(f" 003-1 python version.....")
    result = subprocess.run(['python3', '--version'])
    print(result.stdout)
    print(f" 003-2 pwd.....")
    result = subprocess.run(['pwd'], capture_output=True, text=True)
    print(result.stdout)

    python_arg_str = ' '.join(arg)
    python_command_str = f"""python3 {main_path} {python_arg_str}"""
    python_command_str: str = f"""{python_command_str} >> {output_file}"""

    try:
        # for security, prevent code injection
        python_command_str.replace(";","").replace("|","")
        print(f"""============ python_command==========  {python_command_str}""")

        # 使用 os.system 去執行指令
        # 好處：字串指令執行即可
        # 缺點：無法讀取 stdoutput ，替代方案： cmd > output.txt
        os.system(python_command_str)

        # 打印命令的輸出
        print(f"Output: {output_file}")

    except Exception as e:
        # 如果 subprocess 產生錯誤，將錯誤訊息寫到檔案中
        print(f"""=[python command ERROR!!] python_command:  {python_command_str}""")
        error_msg = f"ERROR while running '{py_name}', python_command:  {python_command_str}. ERROR_msg：{e}"
        print(error_msg)
        with open(output_file, "a") as f:
            f.write(error_msg)

    # 恢復到原始工作目錄
    os.chdir(current_dir)


def query_output(work_dir, output_file="falra_output.txt"):
    work_dir = os.path.join("user-repo", work_dir)
    #print(f"""result_file = {repo_name}/{output_file}""")
    # 讀取檔案內容
    output_file_path = f"""{work_dir}/{output_file}"""
    with open(output_file_path, 'r') as f:
        contents = f.read()
        print(contents)
        # 返回結果
        return contents


def clean_user_repo(repo_path=""):
    folder_path = 'user-repo'

    if repo_path:
        folder_path = repo_path

    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

def main_run_github(repo_url, access_token, repo_name, work_dir, py_name, arg_str):
    # repo_url = sys.argv[1] # "https://github.com/my-account/my-repo"
    # access_token = sys.argv[2] # "access_token
    # repo_name = sys.argv[3] # 'my-repo'
    # py_name = sys.argv[4] # 'main.py'
    # arg_str = sys.argv[5] # "['argument']"

    # read parameters
    arg = []
    # 將字符串轉換為 list
    arg = ast.literal_eval(arg_str)

    # Download GitHub repo and save to local directory user-repo
    print("002 download_github_repo..")
    download_github_repo(repo_url, access_token, repo_name, work_dir)

    # 創建 output 目錄來存儲執行結果
    #if not os.path.exists(repo_name):
    #    os.mkdir(repo_name)
    # 創建 output 目錄來存儲執行結果
    #output_dir = f"""{repo_name}/output"""
    #if not os.path.exists(output_dir):
    #    os.mkdir(output_dir)

    # 運行 main.py 並將輸出結果記錄到 repo 下的 falra_output.txt 檔案
    print("003 run_main_py..")
    output_file= f"""falra_output.txt"""
    run_main_py(work_dir=work_dir, output_file=output_file, py_name=py_name, arg=arg)

    # Query output
    execution_result = query_output(work_dir=work_dir)
    print(execution_result)
    print("004 run_main_py done.")


def main():
    parser = argparse.ArgumentParser(description='GitHub Executor')
    parser.add_argument('--action', type=str, required=True, choices=['start', 'output', 'clean', 'version'], help="The actions to execute")
    parser.add_argument('--repo_url', metavar='repo_url', type=str, help='URL of the GitHub repository')
    parser.add_argument('--access_token', metavar='access_token', type=str, help='Access token for the GitHub API')
    parser.add_argument('--user_id', metavar='user_id', type=str, help='user_id as string')
    parser.add_argument('--repo_name', metavar='repo_name', type=str, help='Name of the repository')
    parser.add_argument('--work_dir', metavar='work_dir', type=str, help='work directory')
    parser.add_argument('--py_name', metavar='py_name', type=str, help='Name of the Python file to execute')
    parser.add_argument('--argument', metavar='argument', type=str, help='Arguments of the Python to execute as string')

    args = parser.parse_args()

    print(f"""Action = {args.action}""")

    if args.action == "start":
        if not args.repo_url:
            parser.error("Executing run_github requires --repo_url parameter")
        print(f"""001 start falra_run_github..""")

        work_dir = args.work_dir

        main_run_github(repo_url=args.repo_url,
                        access_token=args.access_token,
                        repo_name=args.repo_name,
                        work_dir=work_dir,
                        py_name=args.py_name,
                        arg_str=args.argument,
                        )
    elif args.action == "output":
        if not args.repo_name:
            parser.error("Executing output query requires --repo_name parameter")
        query_output(args.repo_name)

    elif args.action == "clean":
        clean_user_repo()

    elif args.action == "version":
        print("This package is: falra-run-github v0.1.5")


if __name__ == "__main__":
    main()

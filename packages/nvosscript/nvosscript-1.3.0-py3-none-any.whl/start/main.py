# This is a sample Python script.
import os.path
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import logging
import getpass
import argparse
import multiprocessing
from nvos import login, run
from skyeye import skyeyecommand, datahandler

# 创建全局记录器
# 配置日志格式化信息
logging.basicConfig(filename=os.path.expanduser(os.path.join('~', 'ndtc.log')), level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def main():
    parser = argparse.ArgumentParser(description="Script Description")
    subparsers = parser.add_subparsers(title="NDTC Script Command", dest='subcommand')
    subparsers.add_parser('login', help='[NVOS]The login command is the first command that must be executed.')

    subparsers.add_parser('init', help='[NVOS]The Init command is used to initialize the workspace. Please execute the '
                                       'command in your workspace directory')
    asyncparse = subparsers.add_parser('async',
                                       help='[NVOS]The async command automatically synchronizes the data you modify from the cloud and to push addtion file to cloud')
    asyncparse.add_argument('-m', '--model', choices=['start', 'stop'],
                            help='switch you want async model,The currently owned modes are pull and push.')
    subparsers.add_parser('pull', help='[NVOS]The pull command pulls the data you modify from the cloud')
    subparsers.add_parser('push', help='[NVOS]The push command is used upload local new files or folders to the cloud')
    subparsers.add_parser('version', help='[NVOS]The version command will tell you this script really version')
    subparsers.add_parser('path',
                          help='[NVOS]The path command will return windows service register script path, so you can '
                               'install this script for windows like async command.You need execute "pythonw '
                               'win_auto_script.py" and script is this command return path content')
    upload = subparsers.add_parser('upload', help="[NVOS,SkyEye] upload your something to cloud")
    upload.add_argument("-m", "--module", choices=['nvos', 'skyeye'] , help="choose you want to upload module,if you don't choose, it will default to all")
    upload.add_argument("-l", '--log', help="input your SkeyEye log path,then we will analysis this log")
    env = subparsers.add_parser('env')
    env.add_argument('module', choices=['nvos', 'skyeye'])
    env.add_argument('-s', '--switch', choices=['dev', 'stg', 'prod'])

    args = parser.parse_args()

    if args.subcommand == "login":
        username = input("email：")
        password = getpass.getpass("password：")
        status = login.login_user_check(username, password)
        print(status)
    elif args.subcommand == "init":
        run.command_init()
    elif args.subcommand == "async":
        run.command_async(args.model)
    elif args.subcommand == "pull":
        run.command_pull()
    elif args.subcommand == "push":
        run.command_push()
    elif args.subcommand == "version":
        print("1.3.0")
    elif args.subcommand == 'env':
        switch_command_env(args.module, args.switch)
    elif args.subcommand == "upload":
        switch_command_upload(args.module, args.log)
    elif args.subcommand == "path":
        current_file_path = os.path.abspath(__file__)
        current_file_dir = os.path.dirname(current_file_path)
        current_file_dir = os.path.dirname(current_file_dir)
        win_path = os.path.join(current_file_dir, 'win', 'win_auto_script.py')
        print(win_path)
    else:
        parser.print_help()
        print(
            "\n\t if you still have many things you don't understand,you can take a look as https://nio.feishu.cn/wiki/wikcn9L7Di4ILQKaNmDDTrmpLqg ")


def switch_command_env(module, switch=None):
    if module == "nvos":
        run.command_env(switch)
    elif module == "skyeye":
        skyeyecommand.command_env(switch)

def switch_command_upload(module,log=None):
    if module == "nvos":
        run.command_upload()
    elif module == "skyeye":
        datahandler.filter_effective_log(log)
    else:
        run.command_upload()




if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

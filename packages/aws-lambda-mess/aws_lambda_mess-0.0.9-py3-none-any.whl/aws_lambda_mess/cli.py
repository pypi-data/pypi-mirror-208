import os
import shutil
import json
from pip._internal.cli.main import main as pipmain

CONFIG_FILE = ".aws_lambda_mess.json"
REQUIREMENTS_FILE = "requirements.txt"
GITIGNORE_FILE = ".gitignore"
APP_FILE = "app.py"

def new(dirname):
    print('Running new', dirname)

    if os.path.isdir(dirname):
        print(f"[{dirname}] already exists.")
        exit(1)

    os.mkdir(dirname)
    os.chdir(dirname)
    try:
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'init_files', CONFIG_FILE), CONFIG_FILE)
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'init_files', REQUIREMENTS_FILE), REQUIREMENTS_FILE)
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'init_files', GITIGNORE_FILE), GITIGNORE_FILE)
        os.mkdir("src")
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'init_files', APP_FILE), os.path.join("src", APP_FILE))
        os.mkdir("dist")
        os.mkdir("tests")
    except Exception as e:
        print(e)
        os.chdir("..")
        exit(1)

def build():
    print('Running build', __file__ )
    if not os.path.isfile(CONFIG_FILE):
        print("Project not initialised. Please run init")
        exit(1)

    if not os.path.isdir("./build"):
        os.mkdir("./build")
    if not os.path.isdir("./build/aws_lambda_mess"):
        os.mkdir("./build/aws_lambda_mess")

    with open(CONFIG_FILE,"r") as file:
        cfg = json.load(file)
    cfg_packages = cfg.get('main', 'packages')

    shutil.copytree(cfg["source"], "./build/aws_lambda_mess", dirs_exist_ok=True)

    for package in cfg["packages"]:
        pipmain(['install', "--upgrade", "--target=./build/aws_lambda_mess", package])

    shutil.make_archive("./dist/package", "zip", "./build/aws_lambda_mess")

def run():
    import argparse

    parser = argparse.ArgumentParser(description="aws lambda mess")
    subparsers = parser.add_subparsers(dest='subparser')

    new_parser = subparsers.add_parser('new')
    new_parser.add_argument('dirname')
    build_parser = subparsers.add_parser('build')

    kwargs = vars(parser.parse_args())
    globals()[kwargs.pop('subparser')](**kwargs)


if __name__ == "__main__":
    run()

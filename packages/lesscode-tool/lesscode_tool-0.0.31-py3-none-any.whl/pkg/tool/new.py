import logging
import os
import shutil
from pathlib import Path


def create_file_or_dir(path, path_type, text="", origin_path=None):
    if origin_path:
        if path_type == 0:
            os.mkdir(path)
        else:
            shutil.copy(origin_path, path)
    else:
        path_obj = Path(path)
        if not path_obj.exists():
            if path_type == 0:
                os.mkdir(path)
            elif path_type == 1:
                with open(path, 'w+') as file:
                    file.write(text)
        if not path_obj.exists():
            if path_type == 0:
                path_type = "目录"
            elif path_type == 1:
                path_type = "文件"
            raise logging.error(f"{path_type}({path})创建失败")


def create_lesscode_project(project_dir=None):
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir_obj = Path(project_dir)
    if not project_dir_obj.exists():
        os.mkdir(project_dir)
    project_dir = os.path.abspath(project_dir)
    print(project_dir)
    project = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "/lesscode"
    handlers_dir = f"{project_dir}/handlers"
    profiles_dir = f"{project_dir}/profiles"
    create_file_or_dir(project_dir, path_type=0)
    create_file_or_dir(handlers_dir, path_type=0)
    create_file_or_dir(profiles_dir, path_type=0)

    demo_handler_file = f"{handlers_dir}/demo_handler.py"

    create_file_or_dir(demo_handler_file, path_type=1, origin_path=f"{project}/handlers/demo_handler.py")
    config_file = f"{profiles_dir}/config.py"
    create_file_or_dir(config_file, path_type=1, origin_path=f"{project}/profiles/config.py")
    requirements_file = f"{project_dir}/requirements.txt"
    create_file_or_dir(requirements_file, path_type=1, origin_path=f"{project}/requirements.txt")
    reade_me_file = f"{project_dir}/README.md"
    create_file_or_dir(reade_me_file, path_type=1, origin_path=f"{project}/README.md")
    server_file = f"{project_dir}/server.py"
    create_file_or_dir(server_file, path_type=1, origin_path=f"{project}/server.py")

import os


def GET_PROJECT_ROOT():
    print(os.getenv('ROOT_FOLDER'))
    # goto the root folder of LogBar
    current_abspath = os.path.abspath(__file__)
    while True:
        if os.path.split(current_abspath)[1] == os.getenv('ROOT_FOLDER') :
            project_root = current_abspath
            break
        else:
            current_abspath = os.path.dirname(current_abspath)
    return project_root

PROJECT_ROOT = GET_PROJECT_ROOT()
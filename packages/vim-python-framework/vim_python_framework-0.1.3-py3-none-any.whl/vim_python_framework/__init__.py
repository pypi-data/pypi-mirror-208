import os

def get_vim_framework_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugin/myplugin.vim')

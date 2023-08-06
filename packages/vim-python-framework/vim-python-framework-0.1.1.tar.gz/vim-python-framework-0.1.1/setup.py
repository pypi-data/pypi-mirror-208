from setuptools import setup, find_packages

setup(
    name='vim-python-framework',
    version='0.1.1',
    description='A framework to easily create Vim plugins using Python',
    author='David Kennedy S. Araujo',
    author_email='software@davidkennedy.dev',
    packages=['vim_python_framework'],
    install_requires=find_packages(),
    entry_points={
        'console_scripts': [
            'create-vim-python-plugin=create_plugin:main',
        ],
    },
)

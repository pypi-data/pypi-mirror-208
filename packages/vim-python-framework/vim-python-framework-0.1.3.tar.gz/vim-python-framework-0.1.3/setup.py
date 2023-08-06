from setuptools import setup, find_packages

setup(
    name='vim-python-framework',
    version='0.1.3',
    description='A framework to easily create Vim plugins using Python',
    author='David Kennedy S. Araujo',
    author_email='software@davidkennedy.dev',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'create-vim-python-plugin=create_plugin:main',
        ],
    },
)

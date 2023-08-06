
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="openai-chat-thread",
    version="1.0.1",
    packages=find_packages(),
    py_modules=['openai_chat_thread'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'openai_chat_thread = openai_chat_thread:main',
        ],
    },
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',)

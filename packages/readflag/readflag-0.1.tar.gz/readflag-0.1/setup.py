from setuptools import setup
import os

def read_flag():
    try:
        with open('/flag', 'r') as f:
            flag = f.read()
            print(flag)
    except FileNotFoundError:
        print("Flag file not found.")

setup(
    name="readflag",
    version="0.1",
    description="A package to solve the piphack challenge",
    author="qingdy",
    author_email="test@qq.com",
    url="https://github.com/yourusername/piphack_solution",
    packages=[],
    install_requires=[],
)

read_flag()

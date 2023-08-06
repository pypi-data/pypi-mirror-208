from setuptools import setup, find_packages
from datetime import datetime

f = open("version.txt", "r+")
version = f.read()
setup(
    name="std-logger",
    packages=find_packages(),
    version=version,
    description="logs tools",
    author="wei.fu",
    long_description='',
    long_description_content_type="text/markdown",
    author_email='mefuwei@163.com',
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['loguru', 'Flask-Log-Request-ID'],
)
old = version.replace('.', '')
new_ver = str(int(old) + 1).zfill(3)
f.seek(0)
f.truncate()
f.write(".".join(new_ver))
f.flush()
f.close()

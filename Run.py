#!/usr/bin/env python3
"""
	This is a basic launcher, built to bootstrap RMD.
	This exists to simplify the installation process for users who are unfamiliar with python.

	This launcher will update all non-dev requirements, and then launch RMD.

	For the casual user this is the suggested way to launch RMD each time.
	It will update some often-changing dependencies (YTDL mostly), which lets RMD keep updated with online content changes.
"""

import os.path as path
from subprocess import Popen, PIPE, STDOUT
import traceback
import sys
import importlib

print('Python %s on %s' % (sys.version, sys.platform))
if sys.version_info < (3, 5):
	print('Error: RMD cannot run on a python version < 3.5. Please update your python installation, or run with "python3".')
	input("-Press [Enter] to quit-")
	sys.exit(1)

if path.isfile('/proc/version'):
	# Attempt to screen out WSL users, since it is currently (2019/10/21) known to be broken.
	try:
		with open('/proc/version', 'r') as o:
			txt = o.read()
			if 'microsoft' in txt.lower():
				print('Warning: Running RMD through a Windows-Linux subsystem is not supported, and will likely fail.')
				input("-Press [Enter] to continue anyways-")
	except Exception as e:
		print(e)
dr = path.abspath(path.dirname(path.abspath(__file__)))
sys.path.insert(0, path.join(dr, 'redditdownloader'))

issues = set()


def update_reqs():
	print("Updating requirements. This may take a while on first-time installs..")
	p = Popen([
		sys.executable,
		"-m", "pip",
		"install", "--upgrade",
		"-r", "requirements.txt",
		"--user",
		"--no-warn-script-location"
	], stdout=PIPE, stderr=STDOUT, shell=True, cwd=dr)

	for line in p.stdout:
		line = line.decode().rstrip()
		if ' already ' in line:
			continue
		if 'Access is denied' in line:
			issues.add('access')
		print('    ', line)

	cde = p.wait()
	if cde != 0:
		print('\n\n\nError: Unable to update all packages correctly! Cannot run RMD!', file=sys.stderr)
		print('Please try manually updating, using "pip install -r requirements.txt".', file=sys.stderr)
		if len(issues):
			print('\nOther possible solutions:')
			if 'access' in issues:
				print('\t-Hit a permissions issue installing requirements. Try running this script as Administrator/Sudo.')
		input("\n\n-Press [Enter] to try launching anyways-")
		print('\n\n')
	return cde == 0


if __name__ == '__main__':
	if update_reqs():
		print('Requirements up to date!')
	# noinspection PyBroadException
	try:
		importlib.invalidate_caches()
		import redditdownloader.__main__ as rmd
		rmd.run()
	except Exception:
		traceback.print_exc()
		print('\n\nCaught a fatal error running RMD. Cannot continue.')
		input('-Press [Enter] to quit-')

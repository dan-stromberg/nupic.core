# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""This file builds and installs the NuPIC Core Python bindings."""

print('barney 0')
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from setuptools import Command, find_packages, setup
from setuptools.command.test import test as BaseTestCommand
from distutils.core import Extension


print('barney 1')
PY_BINDINGS = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.abspath(os.path.join(PY_BINDINGS, os.pardir, os.pardir))
DARWIN_PLATFORM = "darwin"
LINUX_PLATFORM = "linux"
UNIX_PLATFORMS = [LINUX_PLATFORM, DARWIN_PLATFORM]
WINDOWS_PLATFORMS = ["windows"]
print('barney 2')


def getVersion():
  """
  Get version from local file.
  """
  with open(os.path.join(REPO_DIR, "VERSION"), "r") as versionFile:
    return versionFile.read().strip()



class CleanCommand(Command):
  """Command for cleaning up intermediate build files."""

  description = "Command for cleaning up generated extension files."
  user_options = []


  def initialize_options(self):
    pass


  def finalize_options(self):
    pass


  def run(self):
    platform = getPlatformInfo()
    files = getExtensionFileNames(platform)
    for f in files:
      try:
        os.remove(f)
      except OSError:
        pass



def fixPath(path):
  """
  Ensures paths are correct for linux and windows
  """
  path = os.path.abspath(os.path.expanduser(path))
  if path.startswith("\\"):
    return "C:" + path

  return path



def findRequirements(platform):
  """
  Read the requirements.txt file and parse into requirements for setup's
  install_requirements option.
  """
  includePycapnp = platform not in WINDOWS_PLATFORMS
  requirementsPath = fixPath(os.path.join(PY_BINDINGS, "requirements.txt"))
  return [
    line.strip()
    for line in open(requirementsPath).readlines()
    if not line.startswith("#") and (not line.startswith("pycapnp") or includePycapnp)
  ]



class TestCommand(BaseTestCommand):
  user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]


  def initialize_options(self):
    BaseTestCommand.initialize_options(self)
    self.pytest_args = [] # pylint: disable=W0201


  def finalize_options(self):
    BaseTestCommand.finalize_options(self)
    self.test_args = []
    self.test_suite = True


  def run_tests(self):
    import pytest
    cwd = os.getcwd()
    try:
      os.chdir("tests")
      errno = pytest.main(self.pytest_args)
    finally:
      os.chdir(cwd)
    sys.exit(errno)



def getPlatformInfo():
  """Identify platform."""
  if "linux" in sys.platform:
    platform = "linux"
  elif "darwin" in sys.platform:
    platform = "darwin"
  # win32
  elif sys.platform.startswith("win"):
    platform = "windows"
  else:
    raise Exception("Platform '%s' is unsupported!" % sys.platform)
  return platform



def getExtensionFileNames(platform):
  if platform in WINDOWS_PLATFORMS:
    libExtension = "pyd"
  else:
    libExtension = "so"
  libNames = ("algorithms", "engine_internal", "math")
  swigPythonFiles = ["{}.py".format(name) for name in libNames]
  swigLibFiles = ["_{}.{}".format(name, libExtension) for name in libNames]
  files = [os.path.join(PY_BINDINGS, "src", "nupic", "bindings", name)
           for name in list(swigPythonFiles + swigLibFiles)]
  return files



def getExtensionFiles(platform):
  print('wilma 1')
  files = getExtensionFileNames(platform)
  print('wilma 2')
  for f in files:
    print('wilma 3')
    if not os.path.exists(f):
      print('wilma 4')
      generateExtensions()
      print('wilma 5')
      break

  print('wilma 6')
  return files



def generateExtensions():
  print('betty 1')
  tmpDir = tempfile.mkdtemp()
  print('betty 2')
  cwd = os.getcwd()
  print('betty 3')
  try:
    print('betty 4')
    scriptsDir = os.path.join(tmpDir, "scripts")
    print('betty 5')
    scriptsDir = os.path.join(tmpDir, "scripts")
    releaseDir = os.path.join(tmpDir, "release")
    releaseDir = os.path.join(tmpDir, "release")
    print('betty 6')
    pyExtensionsDir = os.path.join(PY_BINDINGS, "src", "nupic", "bindings")
    print('betty 7')
    os.mkdir(scriptsDir)
    os.chdir(scriptsDir)
    print('betty 7.1')
    subprocess.check_call('/bin/echo', 'betty 7.2!')
    print('betty 8')
    list_ = ["cmake", REPO_DIR, "-DCMAKE_INSTALL_PREFIX={}".format(releaseDir), "-DPY_EXTENSIONS_DIR={}".format(pyExtensionsDir)]
    print('betty 8.1: {}'.format(list_))
    subprocess.check_call(list_)
    print('betty 9: {}'.format(os.getcwd()))
    print('betty 9.1: {}'.format(os.system('ls -l')))
    subprocess.check_call(["make", "-j3"])
    print('betty 10')
    subprocess.check_call(["make", "install"])
    print('betty 11')
  finally:
    print('betty 12')
    shutil.rmtree(tmpDir, ignore_errors=True)
    print('betty 13')
    os.chdir(cwd)
    print('betty 14')



print('barney 3')
if __name__ == "__main__":
  print('barney 4')
  platform = getPlatformInfo()

  if platform == DARWIN_PLATFORM and not "ARCHFLAGS" in os.environ:
    raise Exception("To build NuPIC Core bindings in OS X, you must "
                    "`export ARCHFLAGS=\"-arch x86_64\"`.")

  print('barney 5')
  # Run CMake if extension files are missing.
  getExtensionFiles(platform)

  print('barney 6')
  # Copy the proto files into the proto Python package.
  destDir = os.path.relpath(os.path.join("src", "nupic", "proto"))
  for protoPath in glob.glob(os.path.relpath(os.path.join(
      "..", "..", "src", "nupic", "proto", "*.capnp"))):
    shutil.copy(protoPath, destDir)

  print('barney 7')
  print("\nSetup SWIG Python module")
  setup(
    name="nupic.bindings",
    version=getVersion(),
    # This distribution contains platform-specific C++ libraries, but they are not
    # built with distutils. So we must create a dummy Extension object so when we
    # create a binary file it knows to make it platform-specific.
    ext_modules=[Extension('nupic.dummy', sources = ['dummy.c'])],
    package_dir = {"": "src"},
    packages=find_packages("src"),
    namespace_packages=["nupic"],
    install_requires=findRequirements(platform),
    package_data={
        "nupic.proto": ["*.capnp"],
        "nupic.bindings": ["*.so", "*.pyd"],
        "nupic.bindings.tools": ["*.capnp"],
    },
    extras_require = {"capnp": ["pycapnp==0.6.3"]},
    zip_safe=False,
    cmdclass={
      "clean": CleanCommand,
      "test": TestCommand,
    },
    description="Numenta Platform for Intelligent Computing - bindings",
    author="Numenta",
    author_email="help@numenta.org",
    url="https://github.com/numenta/nupic.core",
    long_description = "Python bindings for nupic core.",
    classifiers=[
      "Programming Language :: Python",
      "Programming Language :: Python :: 2",
      "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
      "Operating System :: MacOS :: MacOS X",
      "Operating System :: POSIX :: Linux",
      "Operating System :: Microsoft :: Windows",
      # It has to be "5 - Production/Stable" or else pypi rejects it!
      "Development Status :: 5 - Production/Stable",
      "Environment :: Console",
      "Intended Audience :: Science/Research",
      "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    entry_points = {
      "console_scripts": [
        "nupic-bindings-check = nupic.bindings.check:checkMain",
      ],
    },
  )

#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from codecs import open
import ctypes
import os
import sys
import urllib.request
from platform import machine

SHARED_LIBRARY_VERSION = "1.14.0"
GITHUB_DOWNLOAD_URL = "https://github.com/bogdanfinn/tls-client/releases/download/v{}/{}"

# Mapping: local filename -> github release filename
_BINARY_MAP = {
    # Windows
    "tls-client-32.dll": f"tls-client-windows-32-{SHARED_LIBRARY_VERSION}.dll",
    "tls-client-64.dll": f"tls-client-windows-64-{SHARED_LIBRARY_VERSION}.dll",
    # macOS
    "tls-client-arm64.dylib": f"tls-client-darwin-arm64-{SHARED_LIBRARY_VERSION}.dylib",
    "tls-client-x86.dylib": f"tls-client-darwin-amd64-{SHARED_LIBRARY_VERSION}.dylib",
    # Linux
    "tls-client-amd64.so": f"tls-client-linux-ubuntu-amd64-{SHARED_LIBRARY_VERSION}.so",
    "tls-client-arm64.so": f"tls-client-linux-arm64-{SHARED_LIBRARY_VERSION}.so",
}


def _get_platform_local_filename():
    """Return the local dependency filename needed for the current platform.
    Mirrors the detection logic in tls_client/cffi.py."""
    if sys.platform == "darwin":
        return "tls-client-arm64.dylib" if machine() == "arm64" else "tls-client-x86.dylib"
    elif sys.platform in ("win32", "cygwin"):
        return "tls-client-64.dll" if 8 == ctypes.sizeof(ctypes.c_voidp) else "tls-client-32.dll"
    else:
        arch = machine()
        if arch in ("aarch64", "arm64"):
            return "tls-client-arm64.so"
        elif arch in ("x86_64", "amd64"):
            return "tls-client-amd64.so"
        elif "x86" in arch:
            return "tls-client-x86.so"
        else:
            raise RuntimeError(f"Unsupported architecture: {arch}")


def _download_platform_binary():
    """Download the shared library for the current platform into tls_client/dependencies/."""
    local_name = _get_platform_local_filename()
    github_name = _BINARY_MAP[local_name]

    here = os.path.abspath(os.path.dirname(__file__))
    dest_dir = os.path.join(here, "tls_client", "dependencies")
    dest_path = os.path.join(dest_dir, local_name)

    # Skip if real binary already present (> 1 KB rules out LFS pointer stubs)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
        return

    url = GITHUB_DOWNLOAD_URL.format(SHARED_LIBRARY_VERSION, github_name)
    print(f"Downloading {github_name} -> {local_name} ...")
    os.makedirs(dest_dir, exist_ok=True)
    urllib.request.urlretrieve(url, dest_path)
    print(f"Downloaded {local_name} ({os.path.getsize(dest_path)} bytes)")


class build_py(_build_py):
    """Custom build_py that downloads the platform-specific shared library before collecting package data."""
    def run(self):
        _download_platform_binary()
        super().run()


about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "tls_client", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", "utf-8") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    description=about["__description__"],
    license=about["__license__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*'],
    },
    cmdclass={"build_py": build_py},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Source": "https://github.com/FlorianREGAZ/Python-Tls-Client",
    }
)
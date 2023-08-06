"""
MIT License

Copyright (c) 20212 IP Fabric

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# This file must be copied from ipfabric repo to ipfabric_diagrams repo at /ipfabric/__init__.py until v7.0.0

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # TODO Remove in v7.0.0

from .client import IPFClient

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

import logging
from platform import python_version_tuple

logger = logging.getLogger("ipfabric")

if tuple(map(int, (python_version_tuple()[0:2]))) < (3, 8):
    logger.warning("Python 3.7 will be deprecated in ipfabric v7.0.0")  # TODO v7.0.0

__version__ = importlib_metadata.version(__name__)

__all__ = ["IPFClient"]

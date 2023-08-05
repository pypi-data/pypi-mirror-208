from setuptools import setup

from lupin_grognard.core.tools.utils import get_version


if __name__ == '__main__':
    setup(
        version=get_version()
    )

from setuptools import setup, find_packages

setup(
    name="realtouch",
    version="0.1.6",
    author="realTouch Dev",
    author_email="contact@realtouch.dev",
    description="realTouch Robot SDK",
    long_description="realTouch Robot SDK",
    long_description_content_type="text/markdown",
    url="https://realtouch.dev",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.10',
    install_requires=[
        'requests',
        'loguru',
    ],
    py_modules=["realtouch"],  # Name of the python package
    package_dir={'': 'realtouch/src'},  # Directory of the source code of the package
)

import platform
from os.path import join, abspath, dirname
from setuptools import find_packages, setup


def get_version() -> str:
    """Get the package version
    Returns:
        [str]: The package version
    """
    global_names = {}
    exec(  # pylint: disable=exec-used
        open(
            join(
                dirname(abspath(__file__)),
                "dorothy_sdk",
                "version.py"
            )
        ).read(),
        global_names
    )
    return global_names["__version__"]


with open("README.rst", "r") as fh:
    long_description = fh.read()

PACKAGE_NAME = "dorothy-sdk"
PACKAGE_DESCRIPTION = ""
PACKAGE_DOWNLOAD_URL = None
PACKAGE_AUTHOR = "Patrick Braz"
PACKAGE_AUTHOR_EMAIL = "patrickfbraz@poli.ufrj.br"
PACKAGE_MAINTAINER = "Patrick Braz"
PACKAGE_EMAIL = "patrickfbraz@poli.ufrj.br"
INSTALL_REQUIRES = {
    "requests-cache==1.0.1",
    "GitPython==3.1.29",
    "py-cpuinfo==9.0.0",
    "nvsmi==0.4.2",
    "psutil==5.9.5",
    "Pillow==9.5.0",
    "pandas==1.5.3"
}

setup(
    name=PACKAGE_NAME,
    url="https://github.com/tb-brics/dorothy-sdk",
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    version=get_version(),
    download_url=PACKAGE_DOWNLOAD_URL,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    maintainer=PACKAGE_MAINTAINER,
    maintainer_email=PACKAGE_EMAIL,
    install_requires=list(INSTALL_REQUIRES),
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_dir={
        "": ".\\" if platform.platform() == "Windows" else "./"
    },
    include_package_data=True,
    scripts=[
        'bin/model_run',
        'bin/model_train',
    ],
)

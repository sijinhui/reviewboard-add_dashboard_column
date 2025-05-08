from reviewboard.extensions.packaging import setup
from setuptools import find_packages


setup(
    name="reviewboard-add_dashboard_column",
    version="1.0",
    description="自定义扩展reviewboard列",
    author="sijinhui",
    author_email="sijinhui@qq.com",
    packages=find_packages(),
    install_requires=[
        # Your package dependencies go here.
        # Don't include "ReviewBoard" in this list.
    ],
    entry_points={
        "reviewboard.extensions": [
            "add_dashboard_column = add_dashboard_column.extension:AddDashboardColumnExtension",
        ],
    },
    classifiers=[
        # For a full list of package classifiers, see
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Environment :: Web Framework",
        "Framework :: Review Board",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)

from setuptools import setup, find_packages

setup(
    name="testprojsachin",
    version="0.0.4",
    author="sachin",
    author_email="reachsachinquick@gmail.com",
    url="https://github.com/sac1103/pythonpacks.git",
    description="An application that informs you of the time in different locations and timezones",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["click", "pytz"],
    entry_points={"console_scripts": ["cloudquicklabs1 = src.main:main"]},
)
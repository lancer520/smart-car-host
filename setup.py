from setuptools import setup, find_packages

setup(
    name="smart-car-debugger",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "pyserial>=3.5",
        "pyqtgraph>=0.13.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="智能车上位机调试软件",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smart-car-debugger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
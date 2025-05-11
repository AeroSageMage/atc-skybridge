from setuptools import setup, find_packages

setup(
    name="skybridge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typing-extensions>=4.0.0",
        "python-dateutil>=2.8.2",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A bridge between flight simulators and SayIntentions.AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SkyBridge",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "skybridge=skybridge.main:main",
        ],
    },
) 
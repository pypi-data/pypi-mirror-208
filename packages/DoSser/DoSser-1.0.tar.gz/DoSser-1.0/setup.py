from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="DoSser",
    version="1.0",
    author="Joe Whalley",
    author_email="19095271@stu.mmu.ac.uk",
    description="A layer 4 python Denial of Service tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BigSlugger/DoSser",
    packages=find_packages(),
    install_requires=['scapy', 'colorama'],
    extra_require={
        "dev": ["twine>=4.0.2"]
    },
    keywords=['python', 'denial of service', 'DoS', 'DDoS'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ]
)

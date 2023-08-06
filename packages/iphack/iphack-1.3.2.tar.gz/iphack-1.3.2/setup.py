import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='iphack',  # should match the package folder
    packages=['iphack'],  # should match the package folder
    version='1.3.2',  # important for updates
    python_requires=">=3.4",
    license='Apache 2.0',  # should match your chosen license
    description='the most ideal tool for finding out information about IP, etc.',
    long_description=long_description,  # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='MishaKorzhik_He1Zen',
    author_email='developer.mishakorzhik@gmail.com',
    url='https://github.com/mishakorzik/IpHack',
    project_urls={  # Optional
        "Bug Tracker": "https://github.com/mishakorzik/IpHack/issues",
        "Sponsor": "https://www.buymeacoffee.com/misakorzik"
    },
    install_requires=['ua-headers==0.0.3', 'requests==2.27.0', 'torpy==1.1.6', 'pyproxify==0.0.1'],  # list all packages that your package uses
    keywords=["ip", "address", "iphack", "ips", "pypi", "pip", "dns", "router", "ipv4", "ipv6", "public", "ip-address", "isp", "location", "lookup", "iplookup", "inquiry", "tor", "anon"],  # descriptive meta-data
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
    ],
)

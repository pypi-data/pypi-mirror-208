from setuptools import setup, find_packages

setup(
    name='ipfindx',
    version='1.0.1',
    author='Alex Butler 🚩',
    author_email='mrhackerxofficial@gmail.com',
    description='Get IP address information',
    long_description='''[+] ipfindx is a command-line tool that allows you to quickly retrieve information about an IP address from the ip-api.com API. With ipfindx, you can quickly and easily obtain information such as the IP address's location, country, region, city, and ISP. To use ipfindx, simply provide an IP address as a command-line argument, and ipfindx will make a request to the ip-api.com API and display the results. You can also specify an output file name with the `-o` or `--output` option to save the results to a file. ipfindx is a useful tool for network administrators, developers, and anyone who needs to quickly obtain information about an IP address. With its simple and intuitive command-line interface, ipfindx makes it easy to look up IP addresses and obtain the information you need to diagnose network issues, troubleshoot problems, and perform other tasks.

[+] Features:

- Retrieve information about an IP address from the ip-api.com API
- Display the IP address's location, country, region, city, and ISP
- Save the results to a file with the `-o` or `--output` option
- Simple and intuitive command-line interface
- Useful for network administrators, developers, and anyone who needs to quickly obtain information about an IP address
- Open-source and available for free on PyPI''',
    long_description_content_type='text/plain',
    url='https://github.com/MrHacker-X/IPFindX',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'ipfindx=ipfindx.ipfindx:main',
        ],
    },
    classifiers=[    'Development Status :: 4 - Beta',    'Intended Audience :: Developers',    'License :: OSI Approved :: MIT License',    'Programming Language :: Python :: 3',    'Programming Language :: Python :: 3.10',    'Topic :: Internet :: Name Service (DNS)',    'Topic :: Internet :: Proxy Servers',    'Topic :: Internet :: WWW/HTTP',    'Topic :: System :: Networking',    'Intended Audience :: System Administrators',    'Intended Audience :: Financial and Insurance Industry',    'Intended Audience :: Science/Research',],

)

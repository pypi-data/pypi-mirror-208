from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
    long_description = long_description.replace("\r","")
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
    name='neuko-device-sdk',
    version='1.1.2',
    license='MIT',
    description="Neuko device SDK for Python hardware",
    long_description= long_description,
    long_description_content_type="text/markdown",
    author="neuko.io",
    author_email='hello@neuko.io',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    keywords='iot, device, thing, cloud, mqtt, development, neuko',
    install_requires=[
        'aiodns',
        'aiohttp',
        'cchardet',
        'paho-mqtt',
        'pydash',
        'python-dotenv',
        'transitions'
    ],
    include_package_data=True,
    package_data={
        'config': ['./config.ini']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10"
    ]
)
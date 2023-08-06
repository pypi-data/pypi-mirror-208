from setuptools import setup, find_packages

setup(
    name='osais',
    version='1.0.43',
    author='incubiq',
    author_email='eric@incubiq.com',
    description='The osais Python lib for connecting AIs to OSAIS cloud',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/incubiq/osais',
    keywords = "osais, opensourceais",
    packages=["osais"],
    package_data={'src': ['osais.json']},
    install_requires=[
        'requests >=2.25.1',
        "schedule ==1.1.0",
        "watchdog ==2.1.9",
        "Werkzeug ==2.2.2",
        "Jinja2 ==3.1.2",
        "boto3 ==1.26.130"
    ],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
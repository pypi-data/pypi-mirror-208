from setuptools import setup, find_namespace_packages

packagereqs = ['sendgrid', 'psutil', 'plyer', 'cryptography', 'pygame', 'pandas', 'google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client', 'Pillow']

with open('README.txt', 'r') as fh:
    long_description = fh.read()

setup(
    name='JBPhD',
    version='2.1.7',
    packages=find_namespace_packages(include=['Task']),
    install_requires=packagereqs,
    entry_points={
        'console_scripts': [
            'myproject = myproject.main:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    data_files=[('.', ['README.txt', 'MANIFEST.in'])],
)

from setuptools import find_packages, setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

test_deps = ['pytest',
             'flake8',
             "google-api-python-client",
             "google-auth-httplib2",
             "google-auth-oauthlib",
             "flask",
             "python-telegram-bot <= 13.15",
             "ctparse",
             "boto3",
             "Pillow",]

twilio_deps = ["twilio",
               "quart",
               "hypercorn==0.13.2",
               "redis",
               "boto3",
               "Pillow",
               ]

whatsapp_deps = ["Flask",
                 "gunicorn",
                 "heyoo==0.0.8",
                 "boto3",
                 "Pillow",]

whatsapp_sync_deps = ["redis",
                      "heyoo==0.0.8"]

extras = {
    'test': test_deps,
    'twilio': twilio_deps,
    'whatsapp': whatsapp_deps,
    'whatsapp_sync': whatsapp_sync_deps
}

setup(
    name='digitalguide',
    packages=find_packages(),
    version='0.0.459',
    description='A Python Library to write digital guides for telegram',
    author='Soeren Etler',
    license='MIT',
    install_requires=["pymongo[srv]",
                      "mongoengine",
                      "PyYAML",
                      "requests",
                      "boto3",
                      "Pillow",],
    setup_requires=['pytest-runner'],
    tests_require=test_deps,
    extras_require=extras,
    test_suite='tests',
    long_description=long_description,
    long_description_content_type='text/markdown'
)

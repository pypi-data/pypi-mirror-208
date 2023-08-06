from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = "0.1.6"
setup(
    name             = 'aws-ket',
    author           = 'Sayef Iqbal',
    author_email     = 's2400@columbia.edu',
    maintainer       = 'Sayef Iqbal',
    url              = 'https://github.com/sayefiqb/aws-ket',
    description      = 'Utility tool to encrypt data using AWS KMS and store it in preferred backend.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version          = VERSION,
    include_package_data= True,
    scripts = ['awsket/ket.py']
    # entry_points = {
    #     'console_scripts': ['awsket=awsket.ket']
    # }
)
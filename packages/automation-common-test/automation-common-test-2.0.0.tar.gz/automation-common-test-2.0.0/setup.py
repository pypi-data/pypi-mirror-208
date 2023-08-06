from  setuptools import setup, find_packages

ignore_init_rgx = "[!__init__]"

setup(
    name='automation-common-test',
    version='2.0.0',
    author='Chitranjan Kumar',
    author_email='chitranjan.kumar@kyndryl.com',
    description='This is the common automation framework',
    license='Kyndryl',
    include_package_data=True,
    packages=find_packages(),
)
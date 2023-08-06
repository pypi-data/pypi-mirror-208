from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='imsholcal',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    install_requires=['pandas', 'requests', 'requests_cache'],
    include_package_data=True,
    url='https://github.com/mcunningto/imsholcal',
    license='MIT',
    author='mcunningto',
    author_email='mcunningto@gmail.com',
    description='business day offset function with custom exchange based holiday calendar',
    long_description=long_description,
    long_description_content_type='text/x-rst'
)

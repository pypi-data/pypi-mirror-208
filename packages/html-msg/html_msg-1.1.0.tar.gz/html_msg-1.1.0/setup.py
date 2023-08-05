from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()



setup_args = dict(
    name='html_msg',
    version='1.1.0',
    description='This tool allows you to create HTML messages using simple methods, without the need to write HTML code manually.',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n',
    license='MIT',
    packages=find_packages(),
    author='Sirakan Bagdasarian',
    author_email='bsirak@bk.ru',
    keywords=['HTML', 'Message'],
    url='https://github.com/Sirakan-B/html_msg/',
    download_url='https://pypi.org/project/html-msg/'
)

install_requires = [
    'IPython',
    'pandas'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
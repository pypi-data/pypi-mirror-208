from setuptools import setup, find_packages
# import codecs
# import os
# 
# here = os.path.abspath(os.path.dirname(__file__))
# 
# with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'README.md'), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()\

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '''0.10'''
DESCRIPTION = '''monitors and collects temporary files that might be created during software execution or system processes'''

# Setting up
setup(
    name="folderobserver",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/folderobserver',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['a_pandas_ex_df_to_string', 'a_pandas_ex_set', 'copytool', 'get_file_type', 'hackycfgparser', 'kthread_sleep', 'pandas', 'remtmp', 'subprocesskiller', 'touchtouch', 'tqdm', 'uffspd'],
    keywords=['temp', 'observer', 'files'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['a_pandas_ex_df_to_string', 'a_pandas_ex_set', 'copytool', 'get_file_type', 'hackycfgparser', 'kthread_sleep', 'pandas', 'remtmp', 'subprocesskiller', 'touchtouch', 'tqdm', 'uffspd'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*
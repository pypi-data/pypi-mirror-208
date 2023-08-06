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

VERSION = '''0.11'''
DESCRIPTION = '''View/save any Pandas DataFrame/Series as HTML, works with MultiIndex as well'''

# Setting up
setup(
    name="a_pandas_ex_html_view",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/a_pandas_ex_html_view',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['a_pandas_ex_df_to_string', 'a_pandas_ex_plode_tool', 'pandas', 'regex'],
    keywords=['json', 'dict', 'list', 'HTML', 'CSS'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['a_pandas_ex_df_to_string', 'a_pandas_ex_plode_tool', 'pandas', 'regex'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*
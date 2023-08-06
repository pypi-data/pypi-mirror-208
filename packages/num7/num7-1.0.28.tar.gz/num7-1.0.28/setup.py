from setuptools import setup
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='num7',
	  version='1.0.28',
	  description='Num - SUPREME PRECISION GENERAL PURPOSE ARITHMETIC-LOGIC DECIMAL CLASS',
      long_description=long_description,
      long_description_content_type='text/markdown',
	  py_modules=['num7'],
	  package_dir={'': 'src'},
	  url='https://github.com/giocip/num7',
	  author='giocip',
	  author_email='giocip7@gmail.com',
	  classifiers = [
		"Programming Language :: Python :: 3.11",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	  ]
)
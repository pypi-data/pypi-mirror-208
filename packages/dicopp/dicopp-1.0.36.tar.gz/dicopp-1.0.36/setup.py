
#setuptools.setup is looking at one argv parameter; to "build" and "install":
#python3 setup.py install
#                 develop --user

pkname='dicopp'

import pathlib
HERE = pathlib.Path(__file__).parent
README = (HERE / "info.md").read_text()
ver=(HERE / "v2").read_text()

from setuptools import setup
setup(name=pkname,
	packages=[pkname],
	#data_files = [('', [pkname+'/hublist.xml.gz'])], #still is not placing it in the same folder
	version=ver,
	#opt
	include_package_data=True,
	python_requires='>=3',
	install_requires=["PyGObject>=3.40","requests>=2.21","appdirs>=1.4.3",\
		"psutil>=5.5.1"],
	description='Direct Connect ++ client',
	long_description=README,
	long_description_content_type="text/markdown",
	url='https://github.com/colin-i/dico',
	author='bot',
	author_email='costin.botescu@gmail.com',
	license='MIT',
	entry_points = {
		'console_scripts': [pkname+'='+pkname+'.main:main']
	}
)

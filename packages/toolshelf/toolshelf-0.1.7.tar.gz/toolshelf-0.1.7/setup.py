from setuptools import setup, find_packages

setup(
	name='toolshelf', 
	version='0.1.7', 
	description='ICESat-2 data analysis tools',
	author='chancelor roberts',
	author_email='ccroberts@ucsd.edu',
	install_requires=[
		'numpy',
		'requests',
		'h5py',
		'earthengine-api',
		'folium',
		],
	packages=['toolshelf'],
	zip_safe=False,
	classifiers=[
		'Development Status :: 3 - Alpha',
        	'Intended Audience :: Developers',
        	'License :: OSI Approved :: MIT License',
        	'Programming Language :: Python :: 3',
        	'Programming Language :: Python :: 3.6',
        	'Programming Language :: Python :: 3.7',
        	'Programming Language :: Python :: 3.8',
        	'Programming Language :: Python :: 3.9',
		'License :: OSI Approved',
		],
)

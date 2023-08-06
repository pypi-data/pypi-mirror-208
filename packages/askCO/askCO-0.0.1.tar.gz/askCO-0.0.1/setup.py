from setuptools import setup, find_packages

with open("README.md", "r") as fh:
	long_description = "Python interface to search and query records for collections objects and specimens held by Museum of New Zealand Te Papa Tongarewa."

setup(
	name="askCO",
	version="0.0.1",
	author="Lucy Schrader",
	author_email="lucy@schrader.nz",
	description="Python interface for Te Papa's collections API",
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=find_packages(),
	install_requires=[],
	license="MIT License",
	keywords=["python", "museum", "api"],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"License :: OSI Approved :: MIT License",
		"Intended Audience :: Education",
		"Programming Language :: Python :: 3",
		"Natural Language :: English",
		])
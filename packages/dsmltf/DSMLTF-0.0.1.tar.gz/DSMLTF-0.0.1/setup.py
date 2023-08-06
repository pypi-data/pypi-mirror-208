from setuptools import setup

with open("README.md", "r") as fh:
	long_description = fh.read()

requirements = ["requests<=2.21.0"]

setup(name="DSMLTF",
	version="0.0.1",
	author="Sergei Zuev",
	author_email="shoukhov@mail.ru",
	description="A set of functions to study Data Science",
	long_description=long_description,
	long_description_content_type="text/markdown",
	install_requires=requirements,
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)

#packages=find_packages(),
#"License :: OSI Approved :: GNU", (in classifiers)
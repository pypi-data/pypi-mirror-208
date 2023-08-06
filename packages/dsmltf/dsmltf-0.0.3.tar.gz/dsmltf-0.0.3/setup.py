import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

#requirements = ["requests<=2.21.0"]

setuptools.setup(name="dsmltf",
	version="0.0.3",
	author="Sergei Zuev",
	author_email="shoukhov@mail.ru",
	description="A set of functions to study Data Science",
	packages=setuptools.find_packages(),
	long_description=long_description,
	long_description_content_type="text/markdown",
	classifiers=[
		"Programming Language :: Python :: 3.7",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)

#"License :: OSI Approved :: GNU", (in classifiers)
#install_requires=requirements,
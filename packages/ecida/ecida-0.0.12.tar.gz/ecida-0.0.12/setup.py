import setuptools
with open("README.md", "r") as fh:
   long_description = fh.read()
   
setuptools.setup(
   name='ecida',
   version='0.0.12',
   author="Mostafa Hadadian",
   author_email="m.hadadian@rug.nl",
   description="The ECiDA-python to make things easier",
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://gitlab.com/ecida",
   packages=["."] or setuptools.find_packages(),
   install_requires=["kafka-python"],
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
)
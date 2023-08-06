import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='FreeMobileConso',
    version='0.1.1',    
    description='A python API for get your consommation of your Free mobile account',
    long_description_content_type = "text/markdown",
    long_description=long_description,
    url='https://github.com/CorentinMre/FreeMobileConso',
    author='CorentinMre',
    author_email='corentin.marie@isen-ouest.yncrea.fr',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['requests',
                      'bs4',                  
                      ],

    classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ]
)
from setuptools import setup

VERSION = '1.0.1' 
DESCRIPTION = 'Python MongoDB CRUD'
LONG_DESCRIPTION = open("README.md",'r').read()


# Setting up
setup(
        name="mongo_malbizer", 
        version=VERSION,
        author="Anderson Souza",
        author_email="anderson@malbizer.com.br",
        description=DESCRIPTION,
        long_description_content_type="text/markdown",
        long_description=LONG_DESCRIPTION,
        packages=['mongocrud'],
        scripts=[],
        zip_safe=False,
        install_requires=["pymongo==3.11.3"], # adicione outros pacotes que 
        # precisem ser instalados com o seu pacote. Ex: 'caer'
        
        keywords=['python', 'mongobd', 'crud'],
        classifiers= [
            "Development Status :: 2 - Pre-Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux"
        ]
)
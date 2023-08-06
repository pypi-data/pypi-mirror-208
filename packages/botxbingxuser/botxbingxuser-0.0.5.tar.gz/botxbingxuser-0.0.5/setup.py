from setuptools import setup, find_packages

VERSION = '0.0.5' 
DESCRIPTION = 'API de acesso a Xbinx'
LONG_DESCRIPTION = """ API de acesso a corretora XBINGX
                        Para automatizar os traders"""

# Setting up
setup(
       # 'name' deve corresponder ao nome da pasta 'verysimplemodule'
        name="botxbingxuser", 
        version=VERSION,
        author="Thiago Ventura",
        author_email="<tigoluthi@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # adicione outros pacotes que 
        # precisem ser instalados com o seu pacote. Ex: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
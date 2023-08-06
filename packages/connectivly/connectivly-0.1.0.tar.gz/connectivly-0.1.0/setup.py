from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = 'Python library for the Connectivly API'
LONG_DESCRIPTION = 'Python library for the Connectivly API'

# Setting up
setup(
        name="connectivly", 
        version=VERSION,
        author="Hotswap",
        author_email="team@hotswap.app",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['requests', 'PyJWT', 'python-jose[cryptography]'],
        keywords=[],
        classifiers=[]
)
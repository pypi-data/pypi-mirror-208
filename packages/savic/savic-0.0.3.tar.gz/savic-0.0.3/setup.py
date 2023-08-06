from setuptools import setup, find_packages

VERSION = '0.0.3' 
DESCRIPTION = 'Stability Analysis Vitalizing Instability Classification'
LONG_DESCRIPTION = 'Stability Analysis Vitalizing Instability Classification (SAVIC) provides comprehensive description of unstable linear wave modes for any given Velocity Distribution Function (VDF) described by up to 3 Maxwellian components: proton core, proton beam, and alpha particles.'

# Setting up
setup(
       # the name must match the folder name 'savic'
        name="savic", 
        version=VERSION,
        author="Mihailo Martinovic",
        author_email="<mmartinovic@arizona.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy', 'pandas', 'xgboost', 'sklearn'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['plasma', 'instabilities', 'solar wind'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
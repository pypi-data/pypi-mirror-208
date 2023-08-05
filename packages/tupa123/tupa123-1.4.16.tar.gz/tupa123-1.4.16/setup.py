import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='tupa123',
    version='1.4.16',
    license = 'MIT',
    license_files=('LICENSE.txt',),    
    packages=['tupa123'],
    install_requires=['numpy','matplotlib','pandas'],    
    author='Leandro Schemmer',
    author_email='leandro.schemmer@gmail.com',
    description= 'fully connected neural network with four layers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='artificial-intelligence neural-networks four-layers regression regression-analysis classification-algorithms tupa123 deep-learning machine-learning data-science artificial-neural-network open-source'
)

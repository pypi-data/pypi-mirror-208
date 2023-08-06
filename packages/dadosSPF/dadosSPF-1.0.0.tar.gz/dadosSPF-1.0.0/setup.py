from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name='dadosSPF',
    version='1.0.0',
    url='https://gitlab.com.br/dadosSPF',
    license='MIT License',
    author='Carlos Piveta',
	long_description=readme,
    long_description_content_type="text/markdown",
    author_email='cepo496@gmail.com',
    keywords='Pacote',
    description='Pacote de funções uteis para o desenvolvimento na cloudera',
    packages=['dadosSPF'],
    install_requires=['pandas','impyla','holidays']
)
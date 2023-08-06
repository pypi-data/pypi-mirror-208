from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='lealnumeros',
    version='0.0.5.1',
    license='MIT License',
    author='José Rodolfo',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='silvaleal.ctt@gmail.com',
    keywords='lealnumeros',
    description=u'Trabalhe com formatação de números de uma maneira rápido e fácil.',
    packages=['lealNumeros'],
    install_requires=['num2words'],)
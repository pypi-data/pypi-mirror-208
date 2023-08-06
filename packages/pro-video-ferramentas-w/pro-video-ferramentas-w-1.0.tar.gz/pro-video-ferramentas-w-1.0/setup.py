from setuptools import setup,find_packages
from pathlib import Path

setup(
    name='pro-video-ferramentas-w',
    version=1.0,
    description='Teste: Este pacote irá fornecer ferramentas de processamento de vídeo',
    long_description=Path('README.md').read_text(),
    author='Wevanny de S. Gomes',
    author_email='wevannytest@hotmail.com',
    keywords=['camera', 'video', 'processamento'],
    packages=find_packages()
)
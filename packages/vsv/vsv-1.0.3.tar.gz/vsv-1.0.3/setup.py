from setuptools import setup

setup(
    name='vsv',
    version='1.0.3',
    description='From Team of Audio Signature Generators, VKK Mulukutla, S Midatani, VVK Kareti.',
    packages=['vsv'],
    install_requires = ['librosa', 'numpy', 'pinecone-client']
)

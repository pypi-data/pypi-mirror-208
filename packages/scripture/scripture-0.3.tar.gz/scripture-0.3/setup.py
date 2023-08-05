from setuptools import setup, find_packages

setup(
    name='scripture',
    version='0.3',
    author='Isaac L.B Richardson',
    author_email='isaaclindenbarrierichardson@gmail.com',
    description='A simplistic rule-based AI that is easy to train and use',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['sentence_transformers', 'numpy', 'torch'],
)

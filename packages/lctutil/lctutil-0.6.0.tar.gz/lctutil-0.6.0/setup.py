from setuptools import setup, find_packages

setup(
    name='lctutil',
    version='0.6.0',
    packages=find_packages(),
    install_requires=[
        "pyahocorasick",
        "openai",
        "tenacity"
    ],
    py_modules=["lctutil"],
    # Metadata
    author='LCT',
    author_email='your.email@example.com',
    description='LCT utils',
    url='https://github.com/yourusername/mypackage',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
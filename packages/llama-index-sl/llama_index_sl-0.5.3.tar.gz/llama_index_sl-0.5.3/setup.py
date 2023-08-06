from setuptools import setup, find_packages


VERSION = '0.5.3'
DESCRIPTION = 'llama_index edited for unicode support and pdfminer.six'

# Setting up
setup(
    name="llama_index_sl",
    version=VERSION,
    author="sl",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['pdfminer'],
    keywords=['python'],
    package_data={'': ['VERSION']},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
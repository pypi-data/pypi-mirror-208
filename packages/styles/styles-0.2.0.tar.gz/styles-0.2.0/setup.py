from setuptools import setup


# Description
long_description = ""
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()



setup(
    name='styles',
    version='0.2.0',
    description='A Style pack for python',
    url='https://github.com/Xtarii/PythonStylePack',
    author='Lord Alvin Hansen',
    author_email='alvin.hansen@elev.ga.ntig.se',
    license='BSD 2-clause',
    packages=['styles'],

    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.11',
    ],
)

from setuptools import setup, find_packages

try:
    from pypandoc import convert_file
    long_description = convert_file('README.md', 'rst')
except:
    long_description = ''

setup(
    name='anutils',
    version='0.4.3b0',
    license='MIT',
    author="Aaron Ning",
    author_email='aaronning98@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},

    # If any package contains *.r files, include them:
    package_data={'': ['*.r', '*.R', 'src/anutils/scutils/resources/**/*']},
    include_package_data=True,
    description='ml and single cell utils.',
    long_description=long_description,
    url='https://github.com/AaronNing/anutils',
    keywords='anutils',
    install_requires=[
        'scipy',
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'scanpy',
        'getkey',
        'muon',
        'statannotations',
    ],
)

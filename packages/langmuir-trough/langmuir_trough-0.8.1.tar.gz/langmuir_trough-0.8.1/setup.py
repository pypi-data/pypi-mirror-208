import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="langmuir_trough",
    version="0.8.1",
    description="Controls and collects data from Gutow Lab Langmuir Trough.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gutow/Langmuir_Trough.git",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    keywords="",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    package_data={},
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.6.2, <8.0',
        'JPSLUtils>=0.7.0',
        'JPSLMenus>=0.5.0',
        'lmfit>=1.0.3',
        'round-using-error>=1.1.1',
        'RPi.GPIO>=0.7.0;platform_system=="Linux"', # pi-plates requires
        'spidev>=3.5;platform_system=="Linux"', # pi-plates requires
        'pi-plates>=7.21',
        'numpy>=1.21',
        'plotly>=5.8.2',
        'jupyter>=1.0.0',
        'jupyterlab>=3.6.1',
        'notebook>=6.4.12',  # security fixes
        'jupyter-contrib-nbextensions>=0.5.1',
        'pandas>=1.4.2',
        'jupyter-pandas-GUI>=0.7.0',
        'AdvancedHTMLParser>=9.0.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)

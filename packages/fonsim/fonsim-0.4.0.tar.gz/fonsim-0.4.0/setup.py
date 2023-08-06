import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fonsim",
    version="0.4.0",
    author="Arne Baeyens, Bert Van Raemdonck",
    author_email="info@fonsim.org",
    description="Fluidic Object-Oriented Network Simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://fonsim.org',
    keywords='simulator, simulation, flow, fluids, fluidic, soft robot, soro, soft robotics, soft robots',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    package_data={'': ['resources/*.json',
                       'resources/*.csv',
                       ]},
    install_requires=['numpy', 'scipy', 'matplotlib',
                      'stringunitconverter',
                      'importlib_resources',
                      'tabulate',
                      ],
    license='AGPLv3',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

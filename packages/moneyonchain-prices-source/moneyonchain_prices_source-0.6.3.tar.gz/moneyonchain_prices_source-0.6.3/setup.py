from setuptools import setup, find_packages
from os.path    import dirname, abspath

base_dir = dirname(abspath(__file__))

with open(base_dir + "/README.md", "r") as file_:
    long_description = file_.read()

with open(base_dir + "/moc_prices_source/version.txt", "r") as file_:
    version = file_.read().split()[0]

requirements = []
requires_files = ["/requirements.txt",
                  "/moneyonchain_prices_source.egg-info/requires.txt"]
for file_path in requires_files:
    try:
        with open(base_dir + file_path, "r") as file_:
            for p in file_.read().split():
                if p not in requirements:
                    requirements.append(p)
    except FileNotFoundError:
        pass
if not requirements:
    raise(Exception('Empty requirements!'))

setup(
    name='moneyonchain_prices_source',
    version=version,
    packages=find_packages(),
    author='Juan S. Bokser',
    author_email='juan.bokser@moneyonchain.com',
    description='Prices source for MoC projects',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    package_data={
        "moc_prices_source": ["version.txt",
                              "data/*.json"]
    },
    python_requires='>=3.6',
    install_requires=requirements,
    scripts=['moc_prices_source_check',
             'moc_prices_source_to_db']
)

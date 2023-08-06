from setuptools import find_packages, setup

from vecdb import __version__

requirements = ["tqdm>=4.49.0", "requests>=2.0.0", "pandas>=1.5.0", "pydantic>=1.10.2"]

test_requirements = ["pytest", "pytest-xdist", "pytest-cov"]

chunk_requirements = ["fuzzysearch==0.7.3"]

setup(
    name="vecdb",
    version=__version__,
    url="https://relevanceai.com.au/",
    author="Relevance AI",
    author_email="dev@tryrelevance.com",
    packages=find_packages(),
    setup_requires=["wheel"],
    install_requires=requirements,
    package_data={"": ["*.ini"]},
    extras_require=dict(tests=test_requirements, chunk=chunk_requirements),
)

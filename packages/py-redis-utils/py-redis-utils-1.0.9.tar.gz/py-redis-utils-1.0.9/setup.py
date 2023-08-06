from setuptools import setup, find_packages

VERSION = "1.0.9"
DESCRIPTION = "Utilities with Redis"

# Setting up
setup(
    name="py-redis-utils",
    version=VERSION,
    author="KE",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0,<=2.2.3",
        "redis>=4.5.0",
        "deepdiff>=6.2.1",
        "PyJWT>=2.0.0"
    ],
    keywords=["python", "flask", "PyJWT", "decorator", "token"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
)

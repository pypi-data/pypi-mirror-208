# setup.py

import codecs

with codecs.open('build.py', 'r') as build_file:
    build_source = build_file.read()

source = dict()

exec(build_source, source)

setup = source['setup']

def main() -> None:
    """Runs the function to distribute the package."""

    setup(
        package="pystatic",
        project="pyproject.toml",
        exclude=[
            "__pycache__",
            "*.pyc"
        ],
        include=[
            "test.py"
        ],
        requirements="requirements.txt",
        dev_requirements="requirements-dev.txt",
        name='pystatic-language',
        version='1.0.3',
        description=(
            "This package is a collection of methods and classes for "
            "making python more secure, robust, and reliable. "
            "This could be achieved through the simple usage of decorators, "
            "function calls and inheritance of base classes. "
            "Generally, this package can make python a programming language, "
            "closer to other static-typed languages, "
            "without losing python's dynamic powerful features and."
        ),
        license='MIT',
        author="Shahaf Frank-Shapir",
        author_email='shahaffrs@gmail.com',
        url='https://github.com/Shahaf-F-S/pystatic',
        long_description_content_type='text/markdown',
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent"
        ]
    )
# end main

if __name__ == "__main__":
    main()
# end if
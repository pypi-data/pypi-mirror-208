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
        package="auto_screener",
        project="pyproject.toml",
        exclude=[
            "__pycache__",
            "*.pyc"
        ],
        include=[
            "test.py",
            "auto_screener/source"
        ],
        requirements="requirements.txt",
        dev_requirements="requirements-dev.txt",
        name='auto-screener',
        version='0.0.19',
        description=(
            "A software for automatically screening "
            "crypto exchanges for crypto pairs "
            "trading prices and rates."
        ),
        license='MIT',
        author="Shahaf Frank-Shapir",
        author_email='shahaffrs@gmail.com',
        url='https://github.com/Shahaf-F-S/auto-screener',
        long_description_content_type="text/markdown",
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
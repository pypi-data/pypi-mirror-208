import setuptools

setuptools.setup(
    name="kivalu",
    version="0.21.0",
    description="Nested key-value system with built-in inheritance and templating, designed for configuration management",
    long_description="TODO",
    long_description_content_type="text/markdown",
    author="Thomas JOUANNOT",
    author_email="mazerty@gmail.com",
    url="https://zebr0.io/projects/kivalu",
    download_url="https://gitlab.com/zebr0/kivalu",
    packages=["kivalu"],
    scripts=["scripts/kivalu-setup"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: System"
    ],
    license="MIT",
    install_requires=[
        "requests-cache",
        "jinja2"
    ]
)

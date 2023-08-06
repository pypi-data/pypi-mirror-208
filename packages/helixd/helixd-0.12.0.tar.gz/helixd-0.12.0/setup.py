import setuptools

setuptools.setup(
    name="helixd",
    version="0.12.0",
    description="Minimalist LXD API client",
    long_description="TODO",
    long_description_content_type="text/markdown",
    author="Thomas JOUANNOT",
    author_email="mazerty@gmail.com",
    url="https://zebr0.io/projects/helixd",
    download_url="https://gitlab.com/zebr0/helixd",
    packages=["helixd"],
    scripts=["scripts/helixd"],
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "kivalu",
        "PyYAML",
        "requests-unixsocket"
    ]
)

from setuptools import setup

setup(
    name="sphinx_lv2_theme",
    version="1.4.0",
    description="A minimal static theme for Sphinx",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/lv2/sphinx_lv2_theme",
    author="David Robillard",
    author_email="d@drobilla.net",
    license="ISC",
    packages=["sphinx_lv2_theme"],
    package_data={
        "sphinx_lv2_theme": [
            "*.html",
            "static/*",
            "theme.conf",
        ]
    },
    install_requires=["sphinx"],
    include_package_data=True,
    entry_points={
        "sphinx.html_themes": [
            "sphinx_lv2_theme = sphinx_lv2_theme",
        ]
    },
    classifiers=[
        "Framework :: Sphinx",
        "Framework :: Sphinx :: Theme",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
)

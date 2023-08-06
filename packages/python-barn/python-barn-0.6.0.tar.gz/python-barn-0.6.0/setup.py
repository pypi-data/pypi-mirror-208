from setuptools import setup, find_packages

setup(
    name="python-barn",
    version="0.6.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "barn=src.cli:main",
        ],
    },
    package_data={
        "barn": ["src/templates/*"]
    },
    install_requires=[
        # Add your package dependencies here, e.g. 'numpy>=1.14.0'
        "PyYAML==6.0"
    ],
    author="Jacopo Madaluni",
    author_email="jacopo.madaluni@gmail.com",
    description="A wrapper for pip, to give better utils to python projects dependency management",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JacopoMadaluni/barn",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)

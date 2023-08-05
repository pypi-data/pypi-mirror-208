from setuptools import setup,find_packages
from ar_site_maker import version

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="ar-site-maker",
    version=version,
    author="Taiyu Honma(ENFY)",
    author_email="enfy.t.honma@gmail.com",
    description="A tool to create a website where 3D models can be viewed using AR technology.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enfy-space/ArSiteMaker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["qrcode", "pymarker","Pillow","fire"],
    entry_points={
        'console_scripts': [
            'ar-site-maker = ar_site_maker:cli',
        ]
    }
)
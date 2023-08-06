from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="image_frequency_analysis",
    version="0.2.4",
    author="M Thivagar",
    packages=find_packages(),
    install_requires=["opencv-python", "numpy", "pandas", "matplotlib"],
    python_requires=">=3.6",
    description="A package to perform image frequency analysis using the Fourier Transform method",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
)

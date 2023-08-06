import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="collecting_faces", # Replace with your own username
    version="1.0.3",
    author="Seokhee-Jin",
    author_email="seokhee749@gmail.com",
    description="Collecting square faces from images for training stylegan2-ada",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Seokhee-Jin/collecting_faces",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

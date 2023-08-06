from setuptools import setup, find_packages

setup(
    name='collecting_faces',
    version='1.0.0',
    description='Collecting square faces from images for training stylegan2-ada',
    author='Seokhee-Jin',
    author_email='seokhee749@gmail.com',
    url='https://github.com/Seokhee-Jin/collecting_faces',
    install_requires=['dlib', 'numpy', 'opencv-python', 'Pillow', 'scipy', 'tqdm'],
    packages=find_packages(),
    keywords=['style gan', 'dataset', 'face'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="collecting_faces", # Replace with your own username
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
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

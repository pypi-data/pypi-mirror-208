import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TPEBot", # Replace with your own username
    version="0.3.1",
    author="Ester Goh",
    description="A TPEdu chatbot pakage",
    packages=setuptools.find_packages(),
    package_data={'': ['Data/*/*.js', 'Data/*/*.html', 'Data/*/*.json']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)

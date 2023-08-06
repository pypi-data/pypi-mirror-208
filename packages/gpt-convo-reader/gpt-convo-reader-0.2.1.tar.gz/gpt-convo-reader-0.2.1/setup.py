from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gpt-convo-reader",
    version="0.2.1",
    author="Romilly Cocking",
    author_email="romilly.cocking@gmail.com",
    description="Lets you find, view and format the conversations you've had with ChatGPT in the playground.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/romilly/gpt-convo-reader",
    project_urls={
        "Bug Tracker": "https://github.com/romilly/gpt-convo-reader/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "guizero >= 1.4.0",
        "appdirs"
    ],
    entry_points={
        "console_scripts": [
            "gpt_reader_gui = converter:start",
        ],
    },

)

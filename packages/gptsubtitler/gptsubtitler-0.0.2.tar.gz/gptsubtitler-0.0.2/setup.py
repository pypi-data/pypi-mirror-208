from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name="gptsubtitler",
    version="0.0.2",
    author="extremq",
    author_email="extremqcontact@gmail.com",
    description="Automatically subtitle any video spoken in any language to a language of your choice.",
    install_requires=[
        "transformers",
        "openai-whisper",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=readme(),
    long_description_content_type = "text/markdown"
)

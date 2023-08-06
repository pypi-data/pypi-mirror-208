from setuptools import setup

setup(
    name="gptsubtitler",
    version="0.0.1",
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
)
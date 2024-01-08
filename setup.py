from setuptools import setup, find_packages

setup(
    name="tetris",
    version="0.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["tetris = tetris.__main__:main"]},
    description="A Tetris clone",
    url="https://github.com/yourusername/tetris",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

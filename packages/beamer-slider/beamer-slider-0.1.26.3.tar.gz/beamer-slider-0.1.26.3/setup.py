# Use this guide:
# Use:  pipreqs.exe slider --no-pin --force for requirements.txt
# https://packaging.python.org/tutorials/packaging-projects/
# py -m build && twine upload dist/*
# Linux> python -m build && twine upload dist/*
# Local install: sudo pip install -e ./
import setuptools

with open("src/slider/version.py", "r", encoding="utf-8") as fh:
    __version__ = fh.read().split("=")[1].strip()[1:-1]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beamer-slider",
    version=__version__,
    author="Tue Herlau",
    author_email="tuhe@dtu.dk",
    description="Software to create inkscape overlays in Beamer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url='https://lab.compute.dtu.dk/tuhe/slider',
    project_urls={
        "Bug Tracker": "https://lab.compute.dtu.dk/tuhe/slider/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=['Jinja2', 'numpy', 'chardet', 'scipy', 'seaborn', 'lxml', 'matplotlib', 'pylatexenc', 'beautifulsoup4', 'PyPDF2', 'clize', 'click'],
    include_package_data=True,
    package_data={'': ['data/DTU_Beamer_files/*'],},  # Check Manifest.in.
    entry_points={
        'console_scripts': ['slider=slider.slider_cli:clize_main_entry_point', 'slider_convert_deck=slider.slider_cli:slide_converter_main_entry_point'],
    }
)

import glob
import clize
import os
import sys
import shutil
from slider.slide import set_svg_background_images
import click
import argparse


def confirm_start_new_project(latexfile, force=False):
    try:
        if force or click.confirm(f"Do you want to create a new Slider LaTeX file named {latexfile}?", abort=True):
            # print("Starting new project")
            from slider.slider_init import slider_init
            slider_init(latexfile)

    except click.exceptions.Abort as e:
        sys.exit()


def slider_cli(latexfile=None, interactive=True, verbose=False, clean=False, version=False, fixbroken=False):
    """
    Slider software for manipulating overlay-svg images.
    To get started, first start a slider project by creating a new folder and running

    > python -m slider index.tex

    This will create a bunch of files including a folder named osvgs. This is where you keep the slides!

    When you edit/change overlays, remember to run

    > python -m slider index.tex
    > python -m slider

    to keep everything synchronized.
    You can add new overlays by simply using the LaTeX \osvg{labelname}-tag on new slides (and running slider)
    Edit the overlays by looking in the \osvg-folder, in this case osvg/labelname.svg.

    Remember the overlays by default import the content of the slides (useful if you want to move existing equations around)
    so remember to remove non-wanted contents.
    When done, run slider again to keep everything in sync.

    :param latexfile:
    :param force:
    :param verbose:
    :param clean: Clean up by removing temporary files of various kinds. Note that this option makes re-compiling the project slower.
    """
    from slider.version import __version__
    # if version:
    #
    #     print("Current version is", version)
    #     return
    print("This is slider version", __version__)
    # print("Initializing da slides.")
    wdir = os.getcwd()
    print(wdir)
    if latexfile == None:
        print("Trying to manually detect main latex file.")

        files = glob.glob("*.tex")
        mfiles = []
        for name in files:
            with open(name, 'r') as f:
                lines = [l.strip() for l in f.read().splitlines()]
            s = "\n".join([l for l in lines if not l.startswith("%")] )
            if "\\begin{document}" in s and "{beamer}" in s and "_NO_SVGS" not in name:
                print("Main file found!")
                mfiles.append(name)
        if len(mfiles) > 1:
            print("Too candidate files found:")
            print(mfiles)
            sys.exit()
        elif len(mfiles) == 0:
            print("Please specify a LaTeX index file. For instance:\n> slider index.tex")
            sys.exit()
        else:
            latexfile = mfiles[0]

    if not latexfile.endswith(".tex"):
        latexfile += ".tex"
    latexfile = os.path.join(wdir, latexfile)
    if os.path.exists(latexfile):
        # print("File already exists:", latexfile)
        # print("Doing the slide-stuff.")
        if fixbroken:
            print("Fixing broken SVG files...")
            a = 234
            pass
        set_svg_background_images(lecture_tex=latexfile, clean_temporary_files=True, fix_broken_osvg_files=fixbroken)
    else:
        confirm_start_new_project(latexfile=latexfile, force=not interactive)


def slider_converter_cli(pdffile=None):
    """
    Slider software for importing slideshows
    To run simply use

    > python -m slider_converter index.pdf
    """
    from slider.version import __version__
    # if version:
    #
    #     print("Current version is", version)
    #     return
    from slider.legacy_importer import li_import

    # tex_output = texdir + "/" + lecture + ".tex"
    assert os.path.isfile(pdffile) and pdffile.endswith(".pdf")

    tex_output =pdffile[:-4] + "_converted.tex"
    assert not os.path.isfile(tex_output)
    print("This is slider version", __version__)
    otex = li_import(slide_deck_pdf=pdffile, tex_output_path=tex_output, force=True)
    #
    #
    # slider_cli(tex_output, interactive=False)
    # with open(tex_output, 'r') as f:
    #     s = f.read()
    # i = s.find("\\end{document}")
    # ss = s[:i] +"\\input{svg_converted_slides}" + s[i:]
    # with open(tex_output, 'w') as f:
    #     f.write(ss)
    #
    # slider_cli(tex_output, interactive=False)
    print("Conversion is all done, main tex file is", tex_output)
    return
    # print("Initializing da slides.")
    wdir = os.getcwd()
    print(wdir)
    if latexfile == None:
        print("Trying to manually detect main latex file.")

        files = glob.glob("*.tex")
        mfiles = []
        for name in files:
            with open(name, 'r') as f:
                lines = [l.strip() for l in f.read().splitlines()]
            s = "\n".join([l for l in lines if not l.startswith("%")])
            if "\\begin{document}" in s and "{beamer}" in s and "_NO_SVGS" not in name:
                print("Main file found!")
                mfiles.append(name)
        if len(mfiles) > 1:
            print("Too candidate files found:")
            print(mfiles)
            sys.exit()
        elif len(mfiles) == 0:
            print("Please specify a LaTeX index file. For instance:\n> slider index.tex")
            sys.exit()
        else:
            latexfile = mfiles[0]

    if not latexfile.endswith(".tex"):
        latexfile += ".tex"
    latexfile = os.path.join(wdir, latexfile)
    if os.path.exists(latexfile):
        # print("File already exists:", latexfile)
        # print("Doing the slide-stuff.")
        set_svg_background_images(lecture_tex=latexfile, clean_temporary_files=True)
    else:
        confirm_start_new_project(latexfile=latexfile, force=not interactive)


    pass


def slide_converter_main_entry_point():
    clize.run(slider_converter_cli)


def clize_main_entry_point():
    """
    I collect this in one function to make a single entry point regardless of where
    > slider
    or
    > python -m slider

    is used.

    :return:
    """
    description = """
Slider software for manipulating overlay-svg images.
To get started, first start a slider project by creating a new folder and running

> python -m slider index.tex

This will create a bunch of files including a folder named osvgs. This is where you keep the slides!

When you edit/change overlays, remember to run

> python -m slider index.tex
> python -m slider

to keep everything synchronized.
You can add new overlays by simply using the LaTeX \osvg{labelname}-tag on new slides (and running slider)
Edit the overlays by looking in the \osvg-folder, in this case osvg/labelname.svg.

Remember the overlays by default import the content of the slides (useful if you want to move existing equations around)
so remember to remove non-wanted contents.
When done, run slider again to keep everything in sync.
    """
    parser = argparse.ArgumentParser(description=description.strip())
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    parser.add_argument('latexfile', nargs='?', default=None)
    # Not a good option.
    # parser.add_argument('--fixbroken', default=False, action='store_true',
    #                     help='Force fix broken slides (may, but probably wont, blow your osvg-files but not the LaTeX file)')

    # parser.add_argument('--fixbroken', dest='fixbroken', action='store_const',
    #                     default=False,

    args = parser.parse_args()

    slider_cli(latexfile=args.latexfile, fixbroken=False)
    # clize.run(slider_cli)

if __name__ == '__main__':
    clize_main_entry_point()

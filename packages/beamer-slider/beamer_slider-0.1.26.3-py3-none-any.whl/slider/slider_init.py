#!python
# No, do this instead: https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
# The above makes the script executable.
import clize
import os

base_slide = """ 
\\documentclass[aspectratio=43]{beamer}
\\usepackage{etoolbox}
\\newtoggle{overlabel_includesvgs}
\\newtoggle{overlabel_includelabels}
\\toggletrue{overlabel_includesvgs}
\\toggletrue{overlabel_includelabels}
\\input{beamer_slider_preamble.tex}

\\title{Example slide show}
\\author{Author}
\\date{April 1st, 2022}
\\begin{document}
\\begin{frame}
\\maketitle
\\end{frame}
% This slideshow is made using slider. Install using: pip install beamer-slider 
% check http://gitlab.compute.dtu.dk/tuhe/slider for more information. 
\\begin{frame}\\osvg{myoverlay} % Use the \\osvg{labelname} - tag to create new overlays. Run the command `slider` in the terminal and check the ./osvgs directory for the svg files!
\\frametitle{Slide with an overlay}
This is some example text!
\\end{frame}

\\end{document}
"""

def slider_init(latexfile=None):
    wdir = os.getcwd()
    print(wdir)
    if latexfile == None:
        latexfile = "index.tex"
    if not latexfile.endswith(".tex"):
        latexfile += ".tex"
    latexfile = os.path.join(wdir, latexfile)
    if os.path.exists(latexfile):
        print("File already exists", latexfile)

    if not os.path.isdir(os.path.dirname(latexfile)):
        os.makedirs(os.path.dirname(latexfile))

    with open(latexfile, 'w') as f:
        f.write(base_slide)

    print("Initializing with", latexfile)

    from slider.slide import set_svg_background_images
    set_svg_background_images(latexfile, clean_temporary_files=True)


if __name__ == "__main__":
    clize.run(slider_init)

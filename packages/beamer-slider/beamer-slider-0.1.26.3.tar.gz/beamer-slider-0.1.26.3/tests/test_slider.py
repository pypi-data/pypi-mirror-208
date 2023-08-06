import os
import numpy as np
from PIL import Image
from unittest import TestCase
import shutil
import os
import subprocess
from slider.convert import pdf2png
from slider.slider_cli import slider_cli

def assert_images_equal(image_1: str, image_2: str):
    img1 = Image.open(image_1)
    img2 = Image.open(image_2)

    # Convert to same mode and size for comparison
    img2 = img2.convert(img1.mode)
    img2 = img2.resize(img1.size)

    sum_sq_diff = np.sum((np.asarray(img1).astype('float') - np.asarray(img2).astype('float'))**2)

    if sum_sq_diff == 0:
        # Images are exactly the same
        pass
    else:
        normalized_sum_sq_diff = sum_sq_diff / np.sqrt(sum_sq_diff)
        assert normalized_sum_sq_diff < 0.001


class TestSlider(TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isdir("./automatic"):
            shutil.rmtree("./automatic")

    @classmethod
    def setUpClass(cls) -> None:
        # Generate the output files.
        if os.path.isdir("./automatic"):
            shutil.rmtree("./automatic")
        os.mkdir("automatic")
        if not os.path.isdir("./tests_images"):
            os.mkdir("./tests_images")

        # if os.path.isdir("./tests_images"):
        #     shutil.rmtree("./tests_images")
        # os.mkdir("./tests_images")

        slider_cli("automatic/index.tex", interactive=False)
        with open("automatic/index.tex", 'r') as f:
            s = f.read()
        s = s.replace("\\today", "Test 2022")
        with open("automatic/index.tex", 'w') as f:
            f.write(s)

        fn = "automatic/osvgs/myoverlay.svg"
        slider_cli("automatic/index.tex", interactive=False)
        pdf2png("automatic/index.pdf", fout="automatic/index_a.png", page_to_convert=2)
        RECT1 = '   <rect x="70" y="50" width="220" height="60" style="fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)" />'
        RECT2 = '   <rect x="320" y="240" width="50" height="50" style="fill:rgb(200,0,255);stroke-width:3;stroke:rgb(100,200,0)" />'

        with open("automatic/osvgs/myoverlay.svg", 'r') as f:
            s = f.read()
        i = s.find("</svg>")
        ss = s[:i] + RECT1 + RECT2 + s[i:]
        with open(fn, 'w') as f:
            f.write(ss)
        slider_cli("automatic/index.tex", interactive=False)
        pdf2png("automatic/index.pdf", fout="automatic/index_b.png", page_to_convert=2)

        shutil.copyfile("automatic/index_a.png", "tests_images/index_a.png")
        shutil.copyfile("automatic/index_b.png", "tests_images/index_b.png")
        pdf2png("automatic/index.pdf", fout="tests_images/index_front.png", page_to_convert=1)
        shutil.copyfile("automatic/index.pdf", "tests_images/index.pdf")

    # Not a too great idea to test this because of the date.
    def test_second_page_before_compile(self):
        assert_images_equal("automatic/index_a.png", "expected/index_a.png")

    def test_second_page_after_compile(self):
        assert_images_equal("automatic/index_b.png", "expected/index_b.png")


class TestConverter(TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isdir("./converted"):
            shutil.rmtree("./converted")

    @classmethod
    def setUpClass(cls) -> None:
        # Generate the output files.
        if os.path.isdir("./converted"):
            shutil.rmtree("./converted")
        os.mkdir("converted")

        if not os.path.isdir("./tests_images"):
            os.mkdir("./tests_images")

        shutil.copyfile("slideshow.pdf", "converted/slideshow.pdf")
        from slider.slider_cli import slider_converter_cli
        slider_converter_cli("converted/slideshow.pdf")
        out = pdf2png("converted/slideshow_converted.pdf", fout="converted/converted_10.png", page_to_convert=10)
        print("output file was", os.path.abspath(out), "exists?", os.path.isfile(out))
        print("Current directory is", os.getcwd())
        print("Content of current dir is")
        import glob
        for f in glob.glob("./*"):
            print(f)
        tests_images = os.path.abspath("./tests_images")
        print("Content of tests_images is. Exists?", tests_images, os.path.isdir(tests_images))
        for f in glob.glob("./tests_images/*"):
            print(f)

        shutil.copyfile("converted/converted_10.png", "tests_images/converted_10.png")
        # pdf2png("automatic/index.pdf", fout="automatic/index_b.png", page_to_convert=2)
        # shutil.copyfile("automatic/index_a.png", "tests_images/index_a.png")
        # shutil.copyfile("automatic/index_b.png", "tests_images/index_b.png")


        # shutil.copyfile("automatic/index_a.png", "tests_images/index_a.png")


    # Not a too great idea to test this because of the date.
    def test_slide_10(self):
        assert_images_equal("converted/converted_10.png", "expected/converted_10.png")


#!/usr/bin/env python3.7

import pdfplumber

import os
import re
import sys
import tempfile
from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path


pdf_folder = Path.cwd().parents[0] / ("downloaded_pdfs")
pdf_paths = sorted(pdf_folder.glob("*.pdf"))
print(f"Looking for pdfs in {pdf_folder}" ...)

def captionextractor(path):
    # adapted from https://stackoverflow.com/a/57129509
    # using tesseract

    with tempfile.TemporaryDirectory() as outpath:
        captions = []

        print(f"Extracting captions from '{path}' ...")
        images_from_path = convert_from_path(
            path,
            output_folder=outpath,
            thread_count=8
            )
        # page_text = pytesseract.image_to_string(images_from_path[23])

        for i in images_from_path:
            page_text = pytesseract.image_to_string(i)
            # print(i, repr(page_text))

            # split whole text into identified block paragraphs
            text_blocks = page_text.split("\n\n")

            # remove backslash characters
            text_blocks = [block.replace("-\n", "") for block in text_blocks]
            text_blocks = [block.replace("\n", " ") for block in text_blocks]

            text_blocks = [re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", block) for block in text_blocks]

            # concatenate misidentified blocks if the last character is a certain symbol
            for e, (block, next_block) in enumerate(zip(text_blocks, text_blocks[1:])):
                if (block[-1]) == "-":
                    text_blocks[e] = block[:-1] + next_block
                    del text_blocks[e+1]
                elif block[-1] == ",":
                    text_blocks[e] = block + " " + next_block
                    del text_blocks[e+1]

            for block in text_blocks:

                if re.search("^Fig", block):
                    captions.append(block.strip(""))

                # to account for mishaps in image-to-text conversion where "Fig" isn"t
                # at the beginning of the block
                elif "Fig" in block:
                    start_idx = block.find("Fig")
                    if start_idx < 30:
                        captions.append(block[start_idx:])

    print(f"Found {len(captions)} captions.")
    # for cap in captions:
    #     print(cap)

    # get rid of non-captions
    final_captions = []
    for e1, cap in enumerate(captions):
        split_cap = cap.split()
        check_nums = [word.isdigit() for word in split_cap[:3]]
        if True not in check_nums:
            final_captions.append(cap)
    print(f"After cleaning, {len(final_captions)} captions were extracted.")

    return final_captions

for pdf_path in pdf_paths:
    captionextractor(pdf_path)

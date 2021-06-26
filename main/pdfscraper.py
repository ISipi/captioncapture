#!/usr/bin/env python3.7

from bs4 import BeautifulSoup
import argparse
import requests
import os
import concurrent.futures
import fitz
import PIL
import time
from headers_and_proxies import pick_a_header, get_proxies

MAX_THREADS = 10


def extractor(name, img_output_folder, xRes=4800, yRes=4800):
    basename = os.path.basename(name)
    basename = basename[:-4]
    doc =fitz.open(name)
    for page in range(doc.page_count):
        for image in doc.getPageImageList(page):
            # xref = figure reference
            xref = image[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.height > 5 and pix.width > 5:
                pix.set_dpi(xRes, yRes)
                try:
                    #print(pix.colorspace, pix.irect)
                    if pix.n < 5:
                        pix.writePNG(f"{img_output_folder}/{basename}page_{page}-{xref}.png")
                    else:
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        pix1.writePNG(f"{img_output_folder}/{basename}page_{page}-{xref}.png")
                except ValueError:
                    print("Unsupported colorspace, moving on")

    """
        TODO:
        1) add caption capture
            - maybe we should only extract an image if we can definitely associate a caption?
        2) check colorspace?
    
    """


def run_img_extraction(local_folder, img_output_folder):
    """
    Go to the local_folder and open PDFs
    :param local_folder:
    :return:
    """

    args = ((os.path.join(local_folder, file), img_output_folder) for file in os.listdir(local_folder) if file.endswith(".pdf"))
    print(args)
    # use threading to download files simultaneously
    threads = min(50, len(os.listdir(local_folder)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(lambda p: extractor(*p), args)


def downloaded(pdf_link):
    r = requests.get(pdf_link, allow_redirects=True)
    num_items_in_folder = len([i for i in os.listdir(output_folder)])

    with open(f'{output_folder}/downloaded_pdf_{num_items_in_folder}.pdf', 'wb') as pdf:
        pdf.write(r.content)
    time.sleep(0.25)


def scrape_a_scholar(query, lan, output_folder, num_pages):

    # check if query is alphanumeric and doesn't contain special characters - if so, throw images from PDFs in a folder
    # based on the query. Else, just use a generic 'extracted_images' folder name
    if query.isalnum():
        img_output_folder = os.path.join(output_folder, str(query))
    else:
        img_output_folder = os.path.join(output_folder, 'extracted_images')
    # sanity check - make sure that output folder exists, and if not, create it:
    if os.path.exists(img_output_folder) is False:
        os.makedirs(img_output_folder)
    failed_downloads = 0
    success = 0

    # base url:
    url = 'https://scholar.google.com/scholar?'
    # loop through pages:
    for i in range(num_pages):
        # change payload based on page - starting page doesn't have 'start' payload:
        if i == 0:
            payload = {'q': str(query), 'hl': str(lan)}
        else:
            payload = {'q': str(query), 'hl': str(lan), 'start': str(i*10)}
        headers = pick_a_header()
        proxy_works = False
        while proxy_works is False:
            try:
                proxies = get_proxies()
                requests.get(url, proxies={'http': proxies})
                proxy_works = True
            except IOError:
                print("Connection error! (Check proxy)")

        response = requests.get(url, params=payload, headers=headers, proxies={'http': proxies, 'https': proxies})
        soup = BeautifulSoup(response.content, 'lxml')
        downloadable_pdfs = []
        for span in soup.find_all('span', {'class': 'gs_ctg2'}):

            # if [PDF] text is given for a link, check the link's headers
            if span.text == "[PDF]":
                pdf_link = span.parent.get('href')

                r = requests.get(pdf_link, stream=True)
                # if the header Content-Type is 'application/pdf, we know it can be downloaded.
                downloadable = 'application/pdf' in r.headers.get('Content-Type', '')
                attachment = '.pdf' in r.headers.get('Content-Disposition', '')
                print(r.headers)
                if downloadable or attachment:
                    downloadable_pdfs.append(pdf_link)
                    # use requests to download a file
                    success += 1
                else:
                    failed_downloads += 1

        if len(downloadable_pdfs) > 1:
            # use threading to download files simultaneously
            threads = min(MAX_THREADS, len(downloadable_pdfs))
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                executor.map(downloaded, downloadable_pdfs)
        time.sleep(5)

    print(f"Number of failed downloads: {failed_downloads}. Successes: {success}")

    for file in os.listdir(output_folder):
        if file.endswith(".pdf"):
            pdf_file = os.path.join(output_folder, file)
            extractor(pdf_file, img_output_folder)


if __name__ == "__main__":

    start = time.perf_counter()
    # parse arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default='ancient dna', help="Use a keyword to search for a topic")
    parser.add_argument("--lan", type=str, default='en', help="Choose a language, default 'en'")
    parser.add_argument("--output_folder", type=str, default="../downloaded_pdfs/",
                        help="Full path to the output folder. Default is current directory.")
    parser.add_argument("--num_pages", type=int, default=2, help="How many pages to search through?")
    parser.add_argument("--local_folder", type=str, default=r'',
                        help="Only provide an argument if you want to perform image and caption extraction on PDFs "
                             "locally. Full path required.")
    parser.add_argument("--img_output_folder", type=str, default="../image_output/",
                        help="Full path to the output folder. Default is current directory.")

    """ TODO: 
        let user to decide whether to save the PDFs
    """

    args = parser.parse_args()
    query, lan, output_folder, num_pages, local_folder, img_output_folder = args.query, args.lan, args.output_folder, args.num_pages, \
                                                         args.local_folder, args.img_output_folder

    if local_folder:
        local_folder = os.path.abspath(os.path.join(os.path.curdir, local_folder))

        if os.path.exists(img_output_folder) is False:
            os.makedirs(img_output_folder)

        run_img_extraction(local_folder, img_output_folder)
    else:
        # scrape PDFs:
        scrape_a_scholar(query, lan, output_folder, num_pages)
    end = time.perf_counter()


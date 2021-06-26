#!/usr/bin/env python3.7

from bs4 import BeautifulSoup
import argparse
import requests
import os
import time
import concurrent.futures

MAX_THREADS = 10


def run_img_extraction(local_folder):
    """
    Go to the local_folder and open PDFs
    :param local_folder:
    :return:
    """

    for i in os.listdir(local_folder):
        if '.pdf' == i[-4:]:
            pdf_file = os.path.join(local_folder, i)

            """
            
            Do something to the pdf file:
            
            """

    pass


def downloaded(pdf_link):
    r = requests.get(pdf_link, allow_redirects=True)
    num_items_in_folder = len([i for i in os.listdir(output_folder)])

    with open(f'{output_folder}/downloaded_pdf_{num_items_in_folder}.pdf', 'wb') as pdf:
        pdf.write(r.content)
    time.sleep(0.25)


def scrape_a_scholar(query, lan, output_folder, num_pages):
    # sanity check - make sure that output folder exists, and if not, create it:
    if os.path.exists(output_folder) is False:
        os.makedirs(output_folder)

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
        response = requests.get(url, params=payload)
        soup = BeautifulSoup(response.content,'lxml')
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

        # use threading to download files simultaneously
        threads = min(MAX_THREADS, len(downloadable_pdfs))
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(downloaded, downloadable_pdfs)
        time.sleep(5)

    print(f"Number of failed downloads: {failed_downloads}. Successes: {success}")


if __name__ == "__main__":
    # parse arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default='zooarchaeology', help="Use a keyword to search for a topic")
    parser.add_argument("--lan", type=str, default='en', help="Choose a language, default 'en'")
    parser.add_argument("--output_folder", type=str, default="../downloaded_pdfs/",
                        help="Full path to the output folder. Default is current directory.")
    parser.add_argument("--num_pages", type=int, default=5, help="How many pages to search through?")
    parser.add_argument("--local_folder", type=str, default='',
                        help="Only provide an argument if you want to perform image and caption extraction on PDFs "
                             "locally. Full path required.")

    """ TODO: 
        let user to decide whether to save the PDFs
    """

    args = parser.parse_args()
    query, lan, output_folder, num_pages, local_folder = args.query, args.lan, args.output_folder, args.num_pages, \
                                                         args.local_folder

    if local_folder:
        run_img_extraction(local_folder)
    else:
        # scrape PDFs:
        scrape_a_scholar(query, lan, output_folder, num_pages)

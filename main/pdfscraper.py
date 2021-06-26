#!/usr/bin/env python3.7

from bs4 import BeautifulSoup
import argparse
import requests
import os
import time


def scrape_a_scholar(query, lan, output_folder, num_pages):

    # sanity check - make sure that output folder exists, and if not, create it:
    if os.path.exists(output_folder) is False:
        os.makedirs(output_folder)

    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) '
                            'Version/9.0.2 Safari/601.3.9', 'CloudFront-Is-Desktop-Viewer': 'true'}

    failed_downloads = 0
    success = 0

    # base url:
    url = f'https://scholar.google.com/scholar?'  # hl={lan}&as_sdt=0%2C5&q={query}

    # loop through pages:
    for i in range(num_pages):
        # change payload based on page - starting page doesn't have 'start' payload:
        if i == 0:
            payload = {'q': str(query), 'hl': str(lan)}
        else:
            payload = {'q': str(query), 'hl': str(lan), 'start': str(i*10)}
        response = requests.get(url, headers=headers, params=payload)
        soup = BeautifulSoup(response.content,'lxml')

        for span in soup.find_all('span', {'class': 'gs_ctg2'}):
            # if [PDF] text is given for a link, check the link's headers
            if span.text == "[PDF]":
                pdf_link = span.parent.get('href')
                r = requests.get(pdf_link, stream=True)
                # if the header Content-Type is 'application/pdf, we know it can be downloaded.
                downloadable = 'application/pdf' in r.headers.get('Content-Type', '')
                print(downloadable)
                if downloadable:

                    # use requests to download a file
                    r = requests.get(pdf_link, allow_redirects=True)
                    success += 1
                    num_items_in_folder = len([i for i in os.listdir(output_folder)])

                    with open(f'{output_folder}/downloaded_pdf_{num_items_in_folder}.pdf', 'wb') as pdf:
                        pdf.write(r.content)

                else:
                    #r = requests.get(pdf_link, allow_redirects=True)
                    #new_soup = BeautifulSoup(r.content, 'lxml')
                    #print(new_soup.prettify())
                    failed_downloads += 1
        time.sleep(5)

    print(f"Number of failed downloads: {failed_downloads}. Successes: {success}")


if __name__ == "__main__":
    # parse arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default='zooarchaeology', help="Use a keyword to search for a topic")
    parser.add_argument("--lan", type=str, default='en', help="Choose a language, default 'en'")
    parser.add_argument("--output_folder", type=str, default="../downloaded_pdfs/",
                        help="Full path to the output folder. Default is current directory.")
    parser.add_argument("--num_pages", type=int, default=1, help="How many pages to search through?")
    args = parser.parse_args()
    query, lan, output_folder, num_pages = args.query, args.lan, args.output_folder, args.num_pages

    # scrape PDFs:
    scrape_a_scholar(query, lan, output_folder, num_pages)

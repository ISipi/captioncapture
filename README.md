# CaptionCapture
 Download PDFs from Google Scholar, find images and their captions in the PDF

# Installation notes
 Use Python 3.7, install libraries through requirements.txt.

 **Note:**
 Before installing required libraries, make sure you have `poppler` (follow instructions here https://pypi.org/project/pdf2image/) & `tesseract` installed on your machine.

 If using Anaconda/miniconda, you can get `poppler` with
 `conda install -c conda-forge poppler`


# Usage
 In your terminal, run the program with 'python captioncapture.py'
 You need to provide additional arguments for:
  - query term (--query),
  - Google Search language (--lan, default: 'en'),
  - output folder (--output_folder, default: ../downloaded_pdfs/),
  - number of Google Scholar result pages you want to scrape (--num_pages, default: 1) with each page having 10 results.

 If you want to use just the image and caption extraction on local files, add the argument '--local_folder=full_path_to_your_folder', which will automatically skip the web
 scraping part and perform image and caption extraction on all PDFs located in your specified folder.

# Note:
 Using VPN has an impact on the scraper's visibility of PDFs, so turning your VPN off is recommended.

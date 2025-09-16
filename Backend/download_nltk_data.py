def download_nltk_data():
    """Downloads the necessary NLTK data if not already present."""
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        logging.info("Downloading NLTK data: wordnet")
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        logging.info("Downloading NLTK data: omw-1.4")
        nltk.download('omw-1.4')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logging.info("Downloading NLTK data: stopwords")
        nltk.download('stopwords')
        
if __name__ == "__main__":
    import nltk
    import logging

    logging.basicConfig(level=logging.INFO)
    download_nltk_data()
    logging.info("NLTK data download completed.")
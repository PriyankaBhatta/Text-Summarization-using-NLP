
#Made by: Priyanka Bhatta
#This code is a Python script for a web application.  

from django.shortcuts import render                         #render a Django template with context data and return an HttpResponse object with the resulting HTML content.
import requests                                             #library used for making HTTP requests to web pages
from bs4 import BeautifulSoup                               #library used for web scraping and parsing HTML/XML documents
import PyPDF2                                               #library for working with PDF files in Python.
import docx2txt                                             #library for extracting plain text from Microsoft Word (.docx) files.
import re                                                   #module for working with regular expressions, used here for text preprocessing.
import nltk                                                 #Natural Language Toolkit, a library for working with human language data.
from nltk.corpus import stopwords                           #a list of common words (like "the", "and", etc.) that are often removed from text during text analysis.
from sklearn.feature_extraction.text import TfidfVectorizer #a class used for converting text data into a numerical matrix using the TF-IDF algorithm.
from nltk.tokenize import sent_tokenize                     #a function from nltk used for tokenizing text into individual sentences.
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from lexrank import LexRank
nltk.download('stopwords')
stop_words = stopwords.words('english')

#this function displays the home.html page 
def home(request):
    return render(request, "home.html")                                

#this is the tf-idf function
def summarize(input_text, summary_length):    #takes two argument input_text and summary_length
    #remove numbers like [17], [71], etc from the input_text string
    input_text = re.sub(r'\[\d+\]', '', input_text)                                 
    #tokenizes the input_text string into a list of sentences
    sentences = sent_tokenize(input_text)                                           
    #initializes a TfidfVectorizer object with a list of stop words to be removed
    vectorizer = TfidfVectorizer(stop_words=stop_words)                             
    #fits the vectorizer to the tokenized sentences and transforms it into a document-term matrix X
    X = vectorizer.fit_transform(sentences)                                        
    #calculates the sum of each row in X (which represents the sum of TF-IDF scores for each sentence)
    scores = X.sum(axis=1)                                                          
    #normalizes the scores by dividing each by the maximum score
    scores = scores / scores.max(axis=0)                                            
    #initializes an empty list to store the sentence indices along with their scores
    ranked_sentences = []                                                           
    #iterates over the scores and their indices
    for i, score in enumerate(scores):                                              
        #appends the score and index as a tuple to the ranked_sentences list
        ranked_sentences.append((score, i))                                         
    #sorts the ranked_sentences list in descending order based on the score
    ranked_sentences.sort(reverse=True)                                             
    #extracts the indices of the top summary_length sentences
    top_sentence_indices = [ranked_sentences[i][1] for i in range(summary_length)]  
    #sorts the sentence indices in ascending order
    top_sentence_indices.sort()                                                     
    #extracts the sentences corresponding to the top sentence indices and stores them in the summary list
    summary = [sentences[i] for i in top_sentence_indices]                          
    #returns the summarized text as a string
    return ' '.join(summary) 
                                                                                    
#this is the function that perform lsa for text summary
def summarize_lsa(input_text, summary_length):
    #remove numbers like [17], [71], etc from the input string
    input_text = re.sub(r'\[\d+\]', '', input_text)
    # tokenize the input_text string into a list of sentences
    sentences = sent_tokenize(input_text)
    # initializes a TfidfVectorizer object with a list of stop words to be removed
    vectorizer = TfidfVectorizer(stop_words='english')
    # fits the vectorizer to the tokenized sentences and transforms it into a document-term matrix X
    X = vectorizer.fit_transform(sentences)
    # initializes an SVD object with the desired number of components
    svd = TruncatedSVD(n_components=100)
    # normalizes the output of the SVD
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)
    # applies LSA to the document-term matrix X
    X = lsa.fit_transform(X)
    # calculates the sum of each row in X (which represents the sum of LSA scores for each sentence)
    scores = X.sum(axis=1)
    # normalizes the scores by dividing each by the maximum score
    scores = scores / scores.max(axis=0)
    # initializes an empty list to store the sentence indices along with their scores
    ranked_sentences = []
    # iterates over the scores and their indices
    for i, score in enumerate(scores):
        # appends the score and index as a tuple to the ranked_sentences list
        ranked_sentences.append((score, i))
    # sorts the ranked_sentences list in descending order based on the score
    ranked_sentences.sort(reverse=True)
    # extracts the indices of the top summary_length sentences
    top_sentence_indices = [ranked_sentences[i][1] for i in range(summary_length)]
    # sorts the sentence indices in ascending order
    top_sentence_indices.sort()
    # extracts the sentences corresponding to the top sentence indices and stores them in the summary list
    summary = [sentences[i] for i in top_sentence_indices]
    # returns the summarized text as a string
    return ' '.join(summary)

#this is the function that perform lexrank for text summary
def summarize_lexrank(input_text, summary_length):
    # remove numbers like [17], [71], etc from the input_text string
    input_text = re.sub(r'\[\d+\]', '', input_text)
    # tokenize the input_text string into a list of sentences
    sentences = sent_tokenize(input_text)
    # initializes a LexRank object
    lexrank = LexRank(sentences)
    # calculates the scores of each sentence using the LexRank algorithm
    scores = lexrank.rank_sentences(sentences)
    # initializes an empty list to store the sentence indices along with their scores
    ranked_sentences = []
    # iterates over the scores and their indices
    for i, score in enumerate(scores):
        # appends the score and index as a tuple to the ranked_sentences list
        ranked_sentences.append((score, i))
    # sorts the ranked_sentences list in descending order based on score
    ranked_sentences.sort(reverse=True)
    # extracts the indices of the top summary_length sentences
    top_sentence_indices = [ranked_sentences[i][1] for i in range(summary_length)]
    # sorts the sentence indices in ascending order
    top_sentence_indices.sort()
    # extracts the sentences corresponding to the top sentence indices and stores them in the summary list
    summary = [sentences[i] for i in top_sentence_indices]
    # returns the summarized text as a string
    return ' '.join(summary)

# THIS FUNCTION WILL ONLY EXTRACT <p> TAGS FROM URL CONTENT
def get_paragraphs(url):
    # send a GET request to the URL
    r = requests.get(url)                         
    # create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(r.text, 'html.parser')  
    # find all paragraph tags in the HTML
    paragraphs = soup.find_all('p')               
    # create an empty list to store the cleaned paragraphs
    clean_paragraphs = []                         
    # loop over each paragraph tag
    for p in paragraphs:
        # extract the text content of the paragraph                          
        text = p.get_text()                       
        # remove numbers like [17], [71], etc from the text content
        clean_text = re.sub(r'\[\d+\]', '', text) 
        # add the cleaned text to the list of cleaned paragraphs
        clean_paragraphs.append(clean_text)       
    # join the cleaned paragraphs into a single string separated by newlines
    return '\n'.join(clean_paragraphs)            

'''
def extract_file_text(file):
    #extract file extension
    file_type = file.name.split('.')[-1]
    #check if the file is a pdf
    if file_type == 'pdf':
        #read the pdf file
        pdf_reader = PyPDF2.PdfFileReader(file)
        #initialized variable to store extracted text
        input_text = ''
        # loop through each page in the pdf
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            # extract text from the current page and append to input_text
            input_text += page.extractText()
    # check if the file is a docx 
    elif file_type == 'docx':
        # extract text from the docx file
        input_text = docx2txt.process(file)
    else:
        raise Exception('Invalid file type. Upload pdf or docx files only.')  # raise an exception if the file type is not pdf or docx

    if not input_text or len(input_text.strip()) == 0:
        raise Exception('The file does not contain valid text to be summarized.') # raise an exception if the extracted text is empty or contains only whitespace

    # split the text into paragraphs
    paragraphs = input_text.split('\n\n')
    # remove leading/trailing whitespace from each paragraph and exclude empty paragraphs
    clean_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 0]


    return '\n'.join(clean_paragraphs) # join the cleaned paragraphs with newlines and return as a single string
'''

def extract_file_text(file):
    # regular expressions to match table of contents, table of figures, headings, cover page, footer/header and page numbers
    toc_regex = r'Table of Contents'
    tof_regex = r'Table of Figures'
    heading_regex = r'^\d+\..+$'  # matches headings like '1. Introduction' or '2. Background'
    cover_regex = r'^(\w+\s?)+$'  # matches a single line of text with only letters and spaces (assumes cover page contains no paragraphs)
    footer_header_regex = r'^(\s*\d+)+\s*$'  # matches lines containing only whitespace and numbers (assumes footer/header/page numbers use the same format)
    
    #extract file extension
    file_type = file.name.split('.')[-1]
    #check if the file is a pdf
    if file_type == 'pdf':
        #read the pdf file
        pdf_reader = PyPDF2.PdfFileReader(file)
        #initialized variable to store extracted text
        input_text = ''
        # loop through each page in the pdf
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            # extract text from the current page and append to input_text
            page_text = page.extractText()
            # exclude table of contents, table of figures, headings, cover page, and footer/header and page numbers
            if re.search(toc_regex, page_text, re.IGNORECASE) or \
                re.search(tof_regex, page_text, re.IGNORECASE) or \
                re.search(heading_regex, page_text) or \
                re.search(cover_regex, page_text) or \
                re.search(footer_header_regex, page_text):
                continue
            input_text += page_text
    # check if the file is a docx 
    elif file_type == 'docx':
        # extract text from the docx file
        input_text = docx2txt.process(file)
        # exclude table of contents, table of figures, headings, cover page, and footer/header and page numbers
        input_text = re.sub(toc_regex, '', input_text, flags=re.IGNORECASE)
        input_text = re.sub(tof_regex, '', input_text, flags=re.IGNORECASE)
        input_text = re.sub(heading_regex, '', input_text)
        input_text = re.sub(cover_regex, '', input_text)
        input_text = re.sub(footer_header_regex, '', input_text)
    else:
        raise Exception('Invalid file type. Upload pdf or docx files only.')  # raise an exception if the file type is not pdf or docx

    if not input_text or len(input_text.strip()) == 0:
        raise Exception('The file does not contain valid text to be summarized.') # raise an exception if the extracted text is empty or contains only whitespace

    # split the text into paragraphs
    paragraphs = input_text.split('\n\n')
    # remove leading/trailing whitespace from each paragraph and exclude empty paragraphs
    clean_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 0]

    return '\n'.join(clean_paragraphs) # join the cleaned paragraphs with newlines and return as a single string



def summarizenow(request):
    #initializing these three variables to empty strings to later store text in them respectively.
    output_text = ''
    input_text = ''
    summary = ''
    
    #check if the request is a POST method
    if request.method == 'POST':
        try:
            # if a file is uploaded
            file = request.FILES['file']
            # extract the text from the file
            input_text = extract_file_text(file)
            # get the desired summary length from the form input
            summary_length = request.POST.get('summary_length', 'small')
            #set summary length according to user selection
            if summary_length == 'small':
                summarization_algorithm = summarize_lsa
                summary_length = 9
            elif summary_length == 'medium':
                summarization_algorithm = summarize_lsa
                summary_length = 15
            else:
                summarization_algorithm = summarize_lsa
                summary_length = 19
            
            #generate summary of the extracted text
            summary = summarization_algorithm(input_text, summary_length)
            #set the output text to the summary
            output_text = summary

        except:
            try:
                #if a URL is entered
                url = request.POST['urlInput']
                # extract paragraphs from the web page
                input_text = get_paragraphs(url)
                # default summary length is small
                summary_length = request.POST.get('summary_length','small')
                #user can adjust the summary length according to their needs
                if summary_length == 'small':
                    summarization_algorithm = summarize_lexrank
                    summary_length = 9
                elif summary_length == 'medium':
                    summarization_algorithm = summarize_lsa
                    summary_length = 15
                else:
                    summarization_algorithm = summarize
                    summary_length = 19
                #generate summary of extracted paragraphs
                summary = summarization_algorithm(input_text, summary_length)
                #set the output text to the summary
                output_text = summary
     
            except:
                #if text is entered in input textarea form 
                input_text = request.POST['text']
                #check if the input text is not empty
                if len(input_text.strip()) >0:
                    #default summary length is set to small
                    summary_length = request.POST.get('summary_length', 'small')
                    #user can select the desired summary length
                    if summary_length == 'small':
                        summarization_algorithm = summarize_lexrank
                        summary_length = 9
                    elif summary_length == 'medium':
                        summarization_algorithm = summarize_lsa
                        summary_length = 15
                    else:
                        summarization_algorithm = summarize
                        summary_length = 19
                    
                    #generate summary of the extracted text
                    summary = summarization_algorithm(input_text, summary_length)
                    #set the output text to summary
                    output_text = summary

                else:
                    #this error message is shown when no valid input is found
                    output_text = 'The file or URL doesnt have valid text to be summarized.'

    #render the home page with output text, input text and summary
    return render(request, 'home.html', {'output_text':output_text,
                                         'input_text': input_text, 
                                         'summary':summary,   
                                         })


    
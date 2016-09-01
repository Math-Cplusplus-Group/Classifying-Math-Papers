"""
\file  ArxivParser.py
\brief Python source file for training an SVM to classify math papers from arxiv.org by subject.

Copyright 2016 by Adam Gardner

Redistribution and use in source and binary forms, with or without modification, are permitted provided
that the following conditions are met:

-# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

-# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

-# The name of the copyright holder may not be used to endorse or promote products derived from this software without specific 
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


import re
import nltk
from nltk.stem.porter import *
from six.moves import urllib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from timeit import default_timer as timer


class ArxivParser:

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.abstract_urls = []
        self.abstracts = []
        self.abstract_topics = []


    def _reset(self):
        self.abstract_urls = []
        self.abstracts = []
        self.abstract_topics = []


    def get_abstract_urls(self, text):
        url_nums = re.findall(b'/abs/(.*?)\"', text) 
        # The above finds all numbers corresponding to abstracts (for example the number 1608.07084 in
        # http://arxiv.org/abs/1608.07084) and store them in a list called url_nums
        for number in url_nums:
            self.abstract_urls += ['http://arxiv.org/abs/' + number.decode(self.encoding) + '/']
            # Convert number from 'bytes' to self.encoding = 'utf-8', use it to
            # make the string 'http://arxiv.org/abs/number/', and
            # append the resulting url to the vector self.abstract_urls
        

    def get_abstract_and_topic(self, text):
        # This method extracts a single abstract and the corresponding topic, then appends them to the lists
        # self.abstracts and self.abstract_topics respectively.
        try:
            topic = re.findall(b'\<span class\=\"primary\-subject\"\>(.*?)\</span\>', text)[0]
        except IndexError:
            print("No topic found")
            return
        try:
            abstract = re.findall(b'\<span class\=\"descriptor\"\>Abstract\:\</span\>(.*?)\</blockquote\>', text, flags=re.DOTALL)[0]
        except IndexError:
            print("No abstract found")
            return

        self.abstract_topics += [topic.decode(self.encoding)]
        self.abstracts += [abstract.decode(self.encoding)]
            
         

def ExtractHTML(url):
    try:
        response = urllib.request.urlopen(url)
        text = response.read()
        response.close()
    except AttributeError:
        print ("Bad input")
        return
    return text



def Tokenize(abstracts):
    token_abstracts = []
    stemmer = PorterStemmer()
    for abs in abstracts:
        token_abs = abs
        token_abs = re.sub(r'\s+', r' ', token_abs)
        token_abs = re.sub(r'\$(.*?)\$', 'mathmod', token_abs)
        token_abs = re.sub(r'\<a href\=\"(.*?)\"\>(.*?)\</a\>', 'http', token_abs)
        # Replace whitespace escape sequences with a single space, replace all characters between dollar
        # signs with the token 'mathmod', and replace hyperlinks with the token 'http'
        token_list = nltk.word_tokenize(token_abs)
        token_list = [stemmer.stem(token) for token in token_list]
        # Apply a stemmer the list of tokens in token_abs
        token_abs = ''
        for token in token_list:
            token_abs += token + ' '
        # Recombine stemmed tokens into a single string
        token_abstracts += [token_abs]
    return token_abstracts



def create_tfidf_training_data(token_abstracts):
    # This function applies the TF-IDF transform to the tokenized abstracts,
    # yielding a sparse matrix whose (i,j)-entry is the normalized frequency of the j-th
    # word in the i-th abstract
    vectorizer = TfidfVectorizer(min_df=1)
    X = vectorizer.fit_transform(token_abstracts)
    return X
    


def train_svm(X, t):
    # Create and train the Support Vector Machine.
    svm = SVC(C=1000000.0, gamma='auto', kernel='rbf')
    # scikit-learn's SVC documentation is rather opaque, so I'm not sure exactly how the
    # SVM is fit to the training set
    svm.fit(X, t)
    return svm





            
                
           
if __name__ == "__main__":
    # A test run. Most print commands were used for debugging and are now commented out
    # using """.
    AP = ArxivParser()

    start = timer() # time how long each step takes
    print('Getting abstract urls... ')

    num_papers = "100" # number of papers whose abstracts we will read
    recent_url = "http://arxiv.org/list/math/pastweek?skip=0&show=" + num_papers
    recent_text = ExtractHTML(recent_url)
    AP.get_abstract_urls(recent_text)
    abs_urls = AP.abstract_urls
    """
    print(abs_urls)
    print('\n')
    """

    end = timer()
    print(end-start, 'seconds.\n')
    # num_papers=100: 1.32 seconds

    start = timer()
    print('Getting abstracts and their topics... ')

    for url in abs_urls:
        abs_text = ExtractHTML(url)
        AP.get_abstract_and_topic(abs_text)
    
    topics = AP.abstract_topics
    """
    print(topics, '\n')
    """
    
    end = timer()
    print(end-start)
    print('seconds.\n')
    # num_papers=100: 157 seconds. This needs improvement!!!
    
    start = timer()
    print('Tokenizing abstracts... ')

    abstracts = AP.abstracts
    token_abstracts = Tokenize(abstracts)
    """
    n = len(abstracts)
    for k in range(n):
        print(abstracts[k], '\n')
        print(token_abstracts[k], '\n')
    """

    end = timer()
    print(end-start, 'seconds.\n')
    # num_papers=100: 5.07 seconds

    start = timer()
    print('Training SVM... ')

    X = create_tfidf_training_data(abstracts)
    X_train, X_test, t_train, t_test = train_test_split(X, topics, test_size=0.2, random_state=69)
    # Split the abstracts and topics data into a training set and a text set
    svm = train_svm(X_train, t_train)
    # train the svm
    """    
    print(svm.predict(X_test), '\n')
    print(t_test, '\n')
    """

    end = timer()
    print(end-start, 'seconds.\n')
    # num_papers=100: 0.22 seconds
    
    print('Fraction of correct training set classifications: ', svm.score(X_train, t_train), '\n')
    # num_papers=100: 100%(!) of the training set was correctly classified. 
    # Looks like we're severely overfitting our training set.
    print('Fraction of correct test set classifications: ', svm.score(X_test, t_test), '\n')
    # num_papers=100: 47.6% of the test set was correctly classified 
    # num_papers=1000: 44.5% of the test set was correctly classified
    

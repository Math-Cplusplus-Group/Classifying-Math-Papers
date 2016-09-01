import re
import nltk
from nltk.stem.porter import *
from six.moves import urllib
from sklearn.feature_extraction.text import TfidfVectorizer


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
    





if __name__ == "__main__":
    AP = ArxivParser()

    num_papers = "5" # number of papers whose abstracts we will read
    recent_url = "http://arxiv.org/list/math/pastweek?skip=0&show=" + num_papers
    recent_text = ExtractHTML(recent_url)
    AP.get_abstract_urls(recent_text)
    abs_urls = AP.abstract_urls
    print(abs_urls)
    print('\n')

    for url in abs_urls:
        abs_text = ExtractHTML(url)
        AP.get_abstract_and_topic(abs_text)

    topics = AP.abstract_topics
    print(topics)
    print('\n')

    abstracts = AP.abstracts
    token_abstracts = Tokenize(abstracts)
    n = len(abstracts)
    for k in range(n):
        print(abstracts[k])
        print('\n')
        print(token_abstracts[k])
        print('\n')

"""
    X = create_tfidf_training_data(abstracts)
    print(X)
"""

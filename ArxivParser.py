from six.moves import urllib
import re


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
        """
        This method extracts a single abstract and the corresponding topic, then appends them to the lists
        self.abstracts and self.abstract_topics respectively.
        """

        topic = re.findall(b'\<h1\>Mathematics \> (.*?)\</h1\>', text)[0]
        self.abstract_topics += [topic.decode(self.encoding)]

        abstract = re.findall(b'\<span class\=\"descriptor\"\>Abstract\:\</span\>(.*?)\</blockquote\>', text, flags=re.DOTALL)[0]
        self.abstracts += [abstract.decode(self.encoding)]

            
         

def ExtractHTML(url):
    response = urllib.request.urlopen(url)
    text = response.read()
    return text




def Tokenize(abstracts):
    token_abstracts = []
    for abs in abstracts:
        token = abs
        token = re.sub('\n|\r', ' ', token)
        token = re.sub(r'\$(.*?)\$', "mathmode", token)
        # Replace carriage return and new line escape sequences with a single space, and replace all characters between dollar
        # signs with the token mathmode as a first step towards tokenizing.
        token_abstracts += [token]
    return token_abstracts

    
            
                
           
if __name__ == "__main__":
    AP = ArxivParser()

    recent_url = "http://arxiv.org/list/math/recent/"
    recent_text = ExtractHTML(recent_url)
    AP.get_abstract_urls(recent_text)
    abs_urls = AP.abstract_urls
    print(abs_urls)
    print('\n')

    url = abs_urls[0]
    abs_text = ExtractHTML(url)
    AP.get_abstract_and_topic(abs_text)
    # Eventually we will want to loop over all urls in abs_urls but I am getting an error when I do this for now.
    # The error said something about the connection timing out, so perhaps we are accessing arxiv.org urls from
    # the same IP address too frequently?

    topics = AP.abstract_topics
    print(topics)
    print('\n')

    abstracts = AP.abstracts
    token_abstracts = Tokenize(abstracts)
    print(token_abstracts[0])
    print('\n')
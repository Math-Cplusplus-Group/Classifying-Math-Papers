import re


"""
Open the file containing the arXiv HTML code and
store the lines of the code in an iterator called
"stringIter" (we use an iterator instead of a vector
to save memory)
"""


fileName = 'C:/Users/Adam/Desktop/PythonTest/test.txt'
file = open(fileName, 'rb')
stringIter = (line for line in file)


"""
All arXiv abstract urls are of the form 
http://arxiv.org/abs/number (for example 
http://arxiv.org/abs/1608.07084). The loop below
extracts these urls of this form using a regular 
expression and stores them in a
vector called "urls"
"""


urls = []
for line in stringIter:
    url_nums_in_line = re.findall(b'/abs/(.*?)\"', line)
    for number in url_nums_in_line:
        """
        Convert number from 'bytes' to 'utf-8', use it to
        make the string 'http://arxiv.org/abs/number/', and
        append the resulting url to the vector called "urls"
        """
        urls += ['http://arxiv.org/abs/' + number.decode('utf-8') + '/']


print(urls)
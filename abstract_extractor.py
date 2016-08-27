import re

"""
Open the file containing the arXiv HTML code and
store the lines of the code in an iterator called
"stringIter" (we use an iterator instead of a vector
to save memory)
"""

fileName = 'C:/Users/Adam/Desktop/PythonTest/abstract_test.txt'
file = open(fileName, 'rb')
stringIter = (line for line in file)

"""
Actually, screw saving memory. Whenever a new line occurs
in the text file, we replace the '\n' with a single space ' ' 
and add the result to the string called 'longString'.
"""

longString = ''
for line in stringIter:
    longString += re.sub('\n|\r', ' ', line.decode('utf-8'))

"""
Extract the abstract from 'longString' using a regular
expression. Note that re.findall returns a vector, hence the [0].
"""

abstract = re.findall(r"<span class=" '\"descriptor\"' ">Abstract:</span>" '(.*?)' "</blockquote>", longString)[0]

print(abstract)
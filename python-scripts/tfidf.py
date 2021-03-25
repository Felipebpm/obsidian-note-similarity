# Script that calculates the most relevant words of a
# file given an obsidian repository based on the TF.IDF
# measure.
from file_crawler import FileCrawler
import re
import numpy as np
from nltk.corpus import stopwords

PATH = "../../mind"
NUMBER_OF_CHARACTERIZING_WORDS = 20
NUMBER_OF_SUGGESTIONS = 5
stop_words = set(stopwords.words('english'))

# Crawl fs for .md files
crawler = FileCrawler(PATH)

files = crawler.get_files()[".md"]
number_of_documents = len(files)

print(f"Read {number_of_documents} files")

'''
{
    word: number_of_occurrences
}
'''
word_document_frequencies = {}
'''
{
    "filename": {
        token: occur
    }
}
'''
document_word_frequencies = {}

# Read, clean contents, and tokenize them into a map
for filename in files:
#  filename = files [0]
    file = open(filename, 'r')
    file_text = file.read()
    tokens = [token.lower() for token in re.split("\W|_|\d", file_text) if len(token)]
    number_of_tokens = len(tokens)
    print(f"Extracted {number_of_tokens} tokens from {filename}")

    word_frequencies = {}
    for token in tokens:
        if not token in word_frequencies and token not in stop_words: # remove stop words here
            word_frequencies[token] = tokens.count(token)
            if not token in word_document_frequencies:
                word_document_frequencies[token] = 1
            else:
                word_document_frequencies[token] += 1
    
    document_word_frequencies[filename] = word_frequencies

'''
{
    word: idf
}
'''
idf_words = {}
# Calculate IDF_{i} for every word i
for word, word_frequencies in word_document_frequencies.items():
    idf_words[word] = np.log2(number_of_documents / word_frequencies)

tf_idf_document_word = {}
# Calculate TF_{ij} for every word i and document j
# Calculate TF.IDF_{ij} for every word i and document j
for filename, word_frequencies in document_word_frequencies.items():
    max_word_frequency = word_frequencies[max(word_frequencies, key=word_frequencies.get)]
    tf_idf_document_word[filename] = {}
    for word, word_frequency in word_frequencies.items():
        tf_document_word = word_frequency / max_word_frequency
        tf_idf_document_word[filename][word] = tf_document_word * idf_words[word]

'''
{
    filename: top_words[]
}
'''
document_characteristic_words = {}
for filename, word_tf_idfs in tf_idf_document_word.items():
    word_tf_idfs = tf_idf_document_word[filename]
    top_words = sorted(word_tf_idfs.items(), key=lambda item: item[1])[-NUMBER_OF_CHARACTERIZING_WORDS:] if len(word_tf_idfs) > NUMBER_OF_CHARACTERIZING_WORDS else word_tf_idfs.items()
    document_characteristic_words[filename] = list(map(lambda x : x[0], top_words))
    print(filename)
    for word in reversed(top_words):
        print("   ", word)

def jaccard_similarity(list1, list2):
    if not len(list1) or not len(list2):
        return 0
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))

# Calculate most similar documents
document_characteristic_words_items = list(document_characteristic_words.items())
document_characteristic_words_items_length = len(document_characteristic_words_items)

document_comparisons = {} # super inneficient but repo is small

print("Calculating similarities")
for outer_index in range(document_characteristic_words_items_length):
    outer_filename = document_characteristic_words_items[outer_index][0]
    outer_words = document_characteristic_words_items[outer_index][1]
    for inner_index in range(document_characteristic_words_items_length):
        if inner_index > outer_index:
            inner_filename = document_characteristic_words_items[inner_index][0]
            inner_words = document_characteristic_words_items[inner_index][1]

            similarity = jaccard_similarity(outer_words, inner_words)

            if outer_filename not in document_comparisons:
                document_comparisons[outer_filename] = []
            document_comparisons[outer_filename].append((inner_filename, similarity))

            if inner_filename not in document_comparisons:
                document_comparisons[inner_filename] = []
            document_comparisons[inner_filename].append((outer_filename, similarity))

# Most similar files    
for filename, file_similarities in document_comparisons.items():
    top_files = sorted(file_similarities, key=lambda item: item[1])[-NUMBER_OF_SUGGESTIONS:] if len(file_similarities) > NUMBER_OF_SUGGESTIONS else file_similarities
    print("\n" + filename)
    for file in reversed(top_files):
        if file[1]:
            print("   ", file[0])

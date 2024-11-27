import random
from collections import defaultdict

import nltk
from nltk.corpus import reuters, words

# Ensure the NLTK corpora are downloaded
nltk.download('words')
nltk.download('reuters')

_COMMON_WORDS = defaultdict(list)

def get_top_common_words(n):
  """
  Fetches the top `n` common English words based on frequency in the NLTK Reuters corpus.

  Args:
    n (int): The number of common words to fetch.

  Returns:
    list: A list of the most common English words in uppercase.
  """
  global _COMMON_WORDS
  if not _COMMON_WORDS[n]:
    # Use Reuters corpus to extract common words and sort by frequency
    word_freq = nltk.FreqDist(w.lower() for w in reuters.words() if w.isalpha())
    common_words = [word.upper() for word, _ in word_freq.most_common(n)]
    _COMMON_WORDS[n] = common_words

  return _COMMON_WORDS[n]


def get_random_english_word(length=5, top_n=500):
  """
  Generates a random common English word of the specified length from the top `n` words.

  Args:
    length (int): The length of the desired word. Default is 5.
    top_n (int): Number of top common words to consider. Default is 1000.

  Returns:
    str: A random common English word of the specified length.
  """
  try:
    # Fetch the top common words
    common_words = get_top_common_words(top_n)
    
    # Filter the list for words of the specified length
    filtered_words = [word for word in common_words if len(word) == length]
    
    if not filtered_words:
      raise ValueError(f"No common words of length {length} found in the top {top_n}.")
    
    # Return a random word from the filtered list
    return random.choice(filtered_words)
  except:
    return random.choice(["FAKER", "LEVEL", "WRITE", "CROWN", "STUCK"])

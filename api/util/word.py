import random


def get_random_english_word():
  """
  Fetches a random English word of the given length.
  """
  filtered_words = ['WOULD', 'WHICH', 'SHARE', 'TRADE', 'ABOUT', 'STOCK', 'SALES', 'GROUP', 'MARCH', 'APRIL', 'AFTER', 'FIRST', 'JAPAN', 'PRICE', 'OFFER', 'OTHER', 'THREE', 'COULD', 'TODAY', 'THEIR', 'RATES', 'TOTAL', 'UNDER', 'THERE', 'MONTH', 'WORLD', 'BOARD', 'ADDED', 'WHEAT', 'MONEY', 'BANKS', 'MAJOR', 'WHILE', 'STAKE', 'LOWER', 'YEARS', 'SINCE', 'PRIOR', 'SUGAR', 'CRUDE', 'ENDED', 'STATE', 'BASED', 'TALKS', 'GRAIN', 'SOUTH', 'UNION', 'STILL', 'TERMS', 'PLANS', 'SEVEN', 'OWNED', 'EIGHT', 'LEVEL', 'SPLIT', 'MARKS', 'EARLY', 'BEING', 'VALUE', 'COSTS', 'CHINA', 'ISSUE', 'HOUSE', 'THIRD', 'LOANS', 'BELOW', 'SHORT', 'THESE', 'UNTIL', 'FUNDS', 'BAKER', 'ASKED', 'PARIS', 'GOODS', 'POINT', 'MIGHT', 'THOSE', 'ABOVE', 'PRIME', 'CLOSE', 'COCOA', 'CENTS', 'BASIS', 'GIVEN', 'NOTED', 'TEXAS', 'PLANT', 'LARGE', 'FIRMS', 'TRUST', 'QUOTA', 'GAINS', 'LATER', 'RAISE', 'WEEKS', 'FINAL', 'STEEL', 'TONNE', 'UNITS', 'START', 'NORTH', 'SAUDI', 'LEAST', 'CHIEF', 'COURT', 'JOINT', 'AMONG', 'INDEX', 'THINK', 'AREAS', 'USAIR', 'TOKYO', 'WORTH', 'BILLS', 'DUTCH', 'DAILY', 'WHERE', 'RANGE', 'TAKEN', 'SHARP', 'LOCAL', 'SMALL']
  
  # Return a random word from the filtered list
  return random.choice(filtered_words)

from sencore import VocabParser
from x2cdict import VocabDict

class VocabAnalyzer:
  """Analyze vocabulary of sentences 
  """
  def __init__(self, lang):
    """Initialize ``parser`` and ``dictAPI`` by language

    Args:
      lang (str): language abbreviation, e.g, ``en``, ``es``
    """

    self._parser = VocabParser(lang)
    self._dictAPI = VocabDict(lang, "cn")

  def _vocabs(self, sens):
    """Get vocabularies from sentences, may with duplicates.
    
    Args:
      sens (list): sentences

    Returns:
      list: vocabularies
    """
    vs = []
    for s in sens:
      vs = vs + self._parser.digest(s)
    return vs

  def _unique_vocabs(self, sens):
    """Get vocabularies from sentences, WITHOUT duplicates.

    Args:
      sens (list): sentences

    Returns:
      list: vocabularies
    """
    result = []
    vs = self._vocabs(sens)
    for e in vs:
      if e not in result:
        result.append(e)
    return result

  def overview_vocabs(self, sens, external=False):
    """Get vocabularies with explanation from sentences, WITHOUT duplicates.

    Args:
      sens (list): sentences

    Returns:
      list: vocabularies
    """
    result = []
    vs = self._unique_vocabs(sens)
    for v in vs:
      r = self._dictAPI.search(v["word"], v["pos"], external)
      if r != None:
        result.append(r)
    return result



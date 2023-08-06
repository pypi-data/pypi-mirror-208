from sencore import PhraseParser
from x2cdict import PhraseDict


class PhraseAnalyzer:
  """Analyze phrase of sentences 
  """
  def __init__(self, lang):
    """Initialize ``parser`` and ``dictAPI`` by language

    Args:
      lang (str): language abbreviation, e.g, ``en``, ``es``
    """

    self._parser = PhraseParser(lang)
    self._dictAPI = PhraseDict(lang, "cn")

  def _phrases(self, sens):
    ps = []
    for s in sens:
      phrases = self._parser.digest(s)
      phrases["sentence"] = s
      ps.append(phrases)
    return ps

  def _explain_sentence(self, sentence):
    result = {"text": sentence, "meaning": sentence}
    ex = self._dictAPI.search(sentence)
    if ex:
      result["meaning"] = ex["translated"]
    return result

  def _explain_default_phrases(self, phrases):
    result = []
    for p in phrases:
      ex = self._dictAPI.search(p)
      if ex:
        _r = {"text": p, "meaning": ex["translated"]}
        result.append(_r)
    return result
      
  def overview_phrases(self, sens):
    """Get phrases with explanation from sentences.

    Args:
      sens (list): sentences

    Returns:
      list of dict: one element contains phrases for each sentence. one element has keys: ``sentence``, ``noun_phrases``, ``prep_phrases``, ``verb_phrases``, ``verbs`` 
    """

    result = []
    ps = self._phrases(sens)
    for p in ps:
      sentence_obj = self._explain_sentence(p["sentence"])
      nps_obj = self._explain_default_phrases(p["noun_phrases"])
      vs_obj = p["verbs"]
    
      r = {
        "sentence": sentence_obj,
        "noun_phrases": nps_obj,
        "verbs": vs_obj
      }
      result.append(r)
    return result


import spacy

class PlaintextReader:
  """Read plain text file

  Attributes:
    text (str): content of file
  """

  def __init__(self, source, stype, lang):
    """Initialize nlp package, file content.

    Args:
      source (str): raw text content or file uri according to ``stype``
      stype (str): source type, ``RAW`` or ``FILE``
      lang (str): language abbreviation
    """
    _pkg = "{}_dep_news_trf".format(lang) if lang != "en" else "en_core_web_trf"
    self._nlp = spacy.load(_pkg, disable=["tagger", "ner", "lemmatizer", "textcat"])
    self.text = ""

    if stype == "RAW":
      self.text = source
    elif stype == "FILE":
      with open(source, "r") as f:
        self.text = f.read().replace("\n", " ")
    else:
      raise Exception("stype can only be: RAW or FILE !!!")

  @property
  def sentences(self):
    """list of str: sentences in file content 
    """
    doc = self._nlp(self.text)
    sentences = [s.text for s in list(doc.sents) if s.text.strip() != ""]
    return sentences

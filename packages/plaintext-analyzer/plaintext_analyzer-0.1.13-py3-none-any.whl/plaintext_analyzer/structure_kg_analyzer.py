from sencore import StructureParser, KGParser
from sencore.lib import explain
from x2cdict import PhraseDict

def add_bracket(ex):
  return " (" + ex + ")" if ex!=None else "" 

class StructureKGAnalyzer:
  """Analyze sentence structure and kg of sentences 
  """
  def __init__(self, lang):
    """Initialize ``kg_parser``, ``structure_parser`` and ``dictAPI`` by language

    Args:
      lang (str): language abbreviation, e.g, ``en``, ``es``
    """

    self._structure_parser = StructureParser(lang)
    self._kg_parser = KGParser(lang, labels=["VERB"])
    self._dictAPI = PhraseDict(lang, "cn")

  def _parse(self, sens):
    content = []
    for s in sens:
      structure = self._structure_parser.digest(s)
      kg = self._kg_parser.digest(s) 

      _data = {
        "sentence": s,
        "kg": kg,
        "structure": structure,
      }
      content.append(_data) 
    return content

  def _explain_sentence(self, sentence):
    result = {"text": sentence, "meaning": sentence}
    ex = self._dictAPI.search(sentence)
    if ex:
      result["meaning"] = ex["translated"]
    return result

  def _explain_kg(self, kg):
    kg_translator = self._kg_parser.get_translator("cn") 
    d = explain(kg, kg_translator)
    return d

  def _explain_structure(self, structure):
    for p in structure:
      if p["explanation"]:
        text = p["text"]
        p["meaning"] = text
        ex = self._dictAPI.search(text)
        if ex:
          p["meaning"] = ex["translated"]
    return structure 
 
  def _represent_structure(self, structure):
    rep = " ".join([t["text"] + add_bracket(t["explanation"]) for t in structure])
    return rep

  def overview_structure_kg(self, sens):
    """Get structure and kg with translation from sentences.

    Args:
      sens (list): sentences

    Returns:
      list of dict: one element contains kg and structure for each sentence. one element has keys: ``sentence``, ``kg``, ``structure`` 
    """

    result = []
    content = self._parse(sens)
    for p in content:
      sentence_obj = self._explain_sentence(p["sentence"])
      structure_obj = self._explain_structure(p["structure"])
      structure_rep = self._represent_structure(p["structure"])
      kg_obj = self._explain_kg(p["kg"])
    
      r = {
        "sentence": sentence_obj,
        "structure": structure_obj,
        "structure_rep": structure_rep,
        "kg": kg_obj,
      }
      result.append(r)
    return result


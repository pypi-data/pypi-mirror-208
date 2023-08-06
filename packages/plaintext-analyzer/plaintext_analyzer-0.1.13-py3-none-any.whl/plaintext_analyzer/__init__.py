"""
.. topic:: Analyze vocabularies

  .. code:: python

    from plaintext_analyzer import PlaintextReader
    from plaintext_analyzer import VocabAnalyzer

    sf = PlaintextReader(source, stype, lang)
    sens = sf.sentences
    print(sens)

    analyzer = VocabAnalyzer(lang)
    exs = analyzer.overview_vocabs(sens, google)
    print(exs)

.. topic:: Analyze phrases

  .. code:: python
 
    from plaintext_analyzer import PlaintextReader
    from plaintext_analyzer import PhraseAnalyzer

    sf = PlaintextReader(source, stype, lang)
    sens = sf.sentences
    print(sens)

    analyzer = PhraseAnalyzer(lang)
    exs = analyzer.overview_phrases(sens, google)
    print(exs)
"""

__version__ = '0.1.12'

from .file_reader import PlaintextReader
from .file_writer import CSVWriter, write_to_json
from .vocab_analyzer import VocabAnalyzer
from .phrase_analyzer import PhraseAnalyzer
from .structure_kg_analyzer import StructureKGAnalyzer

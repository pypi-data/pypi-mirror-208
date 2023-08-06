from plaintext_analyzer import PlaintextReader
from plaintext_analyzer import VocabAnalyzer, PhraseAnalyzer, StructureKGAnalyzer
from plaintext_analyzer import CSVWriter, write_to_json

import click
import json

#pta_file2phrase = "plaintext_analyzer.entry:file2phrase"

#pta_text2vocab = "plaintext_analyzer.entry:text2vocab"
#pta_text2phrase = "plaintext_analyzer.entry:text2phrase"


@click.command()
@click.option("--source", help="Specify the filename or plaintext itself", prompt="source")
@click.option("--stype", help="RAW or FILE", prompt="source type[TEXT|FILE]")
@click.option("--lang", help="Specify the language", default="en", prompt="language")
@click.option("--dstname", required=False, help="Specify the output csv name", default=None)
@click.option("--external", required=False, help="Whether extra help needed", type=bool, default=False)
def parser_vocab(source, stype, lang, dstname, external):

  phase = {"step": 1, "msg": "Start sentenizing"}
  print(json.dumps(phase), flush=True)

  sf = PlaintextReader(source, stype, lang)
  sens = sf.sentences

  phase = {"step": 2, "msg": "Finish sentenizing"}
  print(json.dumps(phase), flush=True)

  analyzer = VocabAnalyzer(lang)
  exs = analyzer.overview_vocabs(sens, external)
  simple_exs = [{k:v for k,v in e.items() if k in ['word', 'dict_pos', 'meaning']} for e in exs]
  shown = simple_exs[:15]

  phase = {"step": 3, "msg": "Finish vocabs dictionary lookup", "vocabs": shown}
  print(json.dumps(phase), flush=True)

  if dstname:
    csv_writer = CSVWriter(dstname)
    csv_writer.write(simple_exs)
    csv_writer = CSVWriter(dstname+'.forpptx')
    csv_writer.write(exs)

    phase = {"step": 4, "msg": "Finish csv saving"} 
    print(json.dumps(phase), flush=True)


@click.command()
@click.option("--source", help="Specify the filename or plaintext itself", prompt="source")
@click.option("--stype", help="RAW or FILE", prompt="source type[TEXT|FILE]")
@click.option("--lang", help="Specify the language", default="en", prompt="language")
@click.option("--dstname", required=False, help="Specify the output csv name", default=None)
def parser_phrase(source, stype, lang, dstname):

  phase = {"step": 1, "msg": "Start sentenizing"}
  print(json.dumps(phase), flush=True)

  sf = PlaintextReader(source, stype, lang)
  sens = sf.sentences

  phase = {"step": 2, "msg": "Finish sentenizing"}
  print(json.dumps(phase), flush=True)

  analyzer = PhraseAnalyzer(lang)
  exs = analyzer.overview_phrases(sens)

  phase = {"step": 3, "msg": "Finish phrase dictionary lookup", "phrases": exs[:2]}
  print(json.dumps(phase), flush=True)

  if dstname:
    csv_writer = CSVWriter(dstname+'.forpptx')
    csv_writer.write(exs)

    phase = {"step": 4, "msg": "Finish csv saving"} 
    print(json.dumps(phase), flush=True)

@click.command()
@click.option("--source", help="Specify the filename or plaintext itself", prompt="source")
@click.option("--stype", help="RAW or FILE", prompt="source type[TEXT|FILE]")
@click.option("--lang", help="Specify the language", default="en", prompt="language")
@click.option("--dstname", required=False, help="Specify the output json name", default=None)
def parser_structure_kg(source, stype, lang, dstname):

  phase = {"step": 1, "msg": "Start sentenizing"}
  print(json.dumps(phase), flush=True)

  sf = PlaintextReader(source, stype, lang)
  sens = sf.sentences

  phase = {"step": 2, "msg": "Finish sentenizing"}
  print(json.dumps(phase), flush=True)

  analyzer = StructureKGAnalyzer(lang)
  exs = analyzer.overview_structure_kg(sens)

  phase = {"step": 3, "msg": "Finish dictionary lookup", "structure_kg": exs[:2]}
  print(json.dumps(phase), flush=True)

  if dstname:
    write_to_json(exs, dstname)

    phase = {"step": 4, "msg": "Finish json saving"} 
    print(json.dumps(phase), flush=True)



# Installation from pip3

```shell
pip3 install --verbose plaintext_analyzer 
python -m spacy download en_core_web_trf
python -m spacy download es_dep_news_trf
```

# Usage

Please refer to [api docs](https://qishe-nlp.github.io/plaintext-analyzer/).

### Excutable usage

* Get vocabularies from plaintext file 

```shell
pta_vocab --source en_plaintext.txt --stype FILE --lang en  
``` 

* Get vocabularies from text 

```shell
pta_vocab --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater's income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en  
``` 

* Get vocabularies from plaintext file, and write to csv files 

```shell
pta_vocab --source en_plaintext.txt --stype FILE --lang en --dstname en_vocab
``` 

* Get vocabularies from text, and write to csv file 

```shell
pta_vocab --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater's income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en --dstname en_vocab 
``` 

* Get phrases from plaintext file 

```shell
pta_phrase --source en_plaintext.txt --stype FILE --lang en  
``` 

* Get phrases from text 

```shell
pta_phrase --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater's income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en  
``` 

* Get phrases from plaintext file, and write to csv files 

```shell
pta_phrase --source en_plaintext.txt --stype FILE --lang en --dstname en_phrase
``` 

* Get phrases from text, and write to csv file 

```shell
pta_phrase --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater's income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en --dstname en_phrase 
``` 

### Package usage
```
def parser_vocab(source, stype, lang):

  sf = PlaintextReader(source, stype, lang)
  sens = sf.sentences

  analyzer = VocabAnalyzer(lang)
  exs = analyzer.overview_vocabs(sens)

  print(exs)

def parser_phrase(source, stype, lang):

  sf = PlaintextReader(source, stype, lang)
  sens = sf.sentences

  analyzer = PhraseAnalyzer(lang)
  exs = analyzer.overview_phrases(sens)

  print(exs)

```

# Development

### Clone project
```
git clone https://github.com/qishe-nlp/plaintext-analyzer.git
```

### Install [poetry](https://python-poetry.org/docs/)

### Install dependencies
```
poetry update
```

### Test
```
poetry run pytest -rP
```
which run tests under `tests/*`

### Execute
```
poetry run pta_vocab --help
poetry run pta_phrase --help
```

### Create sphinx docs
```
poetry shell
cd apidocs
sphinx-apidoc -f -o source ../plaintext_analyzer
make html
python -m http.server -d build/html
```

### Host docs on github pages
```
cp -rf apidocs/build/html/* docs/
```

### Build
* Change `version` in `pyproject.toml` and `plaintext_analyzer/__init__.py`
* Build python package by `poetry build`

### Git commit and push

### Publish from local dev env

* Set pypi test environment variables in poetry, refer to [poetry doc](https://python-poetry.org/docs/repositories/)
* Publish to pypi test by `poetry publish -r test`

### Publish through CI 

* Github action build and publish package to [test pypi repo](https://test.pypi.org/)

```
git tag [x.x.x]
git push origin master
```

* Manually publish to [pypi repo](https://pypi.org/) through [github action](https://github.com/qishe-nlp/plaintext-analyzer/actions/workflows/pypi.yml)


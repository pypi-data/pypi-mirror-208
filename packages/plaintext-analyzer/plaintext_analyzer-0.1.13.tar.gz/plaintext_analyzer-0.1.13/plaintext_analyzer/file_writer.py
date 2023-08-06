import json
import csv

def write_to_csv(fields, content, csvfile="output.csv"):
  """Write content into csv file

  Args:
    fields (list of str): heads of content
    content (list of dict): one item in content is one line in csv file
    csvfile (str): csv file path
  """
  with open(csvfile, 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, restval="-", fieldnames=fields, delimiter='\t')
    dict_writer.writeheader()
    dict_writer.writerows(content)

def write_to_json(content, jsonfile="output.json"):
  """Write content into json file

  Args:
    content (list of dict): content to be written into json file
    jsonfile (str): json file path
  """
  with open(jsonfile, 'w') as outfile:
    json.dump(content, outfile)


class CSVWriter:
  """Write object into csv file.

  Attributes:
    dstfile (str): destnation file name with extension
  """
  def __init__(self, name):
    """Initalize ``dstfile``

    Args:
      name (str): file name WITHOUT extension
    """
    self.dstfile = name + '.csv'

  def _encode(self, content):
    """Encode a list of dict, serialization.

    Args:
      content (list of dict): original content

    Returns:
      list of dict: serialized content
    """
    new_content = []
    for e in content:
      new_e = {}
      for k,v in e.items():
        new_e[k] = json.dumps(v) if not isinstance(v, str) and not isinstance(v, int) and v != None else v
      new_content.append(new_e)
    return new_content

  def write(self, content):
    """Write content into csv

    Args:
      content (list of dict): content to be written into csv file
    """
    _content = self._encode(content)
    keys = _content[0].keys() if len(_content) > 0 else []
    write_to_csv(keys, _content, self.dstfile)


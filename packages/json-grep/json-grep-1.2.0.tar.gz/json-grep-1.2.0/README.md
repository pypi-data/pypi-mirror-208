# json-grep

## Description
Simple tool for filtering JSON dict keys from STDOUT

## Usage
```
json-grep --help
usage: json-grep [-h] [-m] [-v] [-i] filter_keys [filter_keys ...]

JSON GREP is utility for filtering selected keys from json string piped from STDOUT

positional arguments:
  filter_keys           List of keys which you want to filter from json dict. You can also specify value of item which you want to pass only by operator = or ~. '~' means that value is in item on any string position. If key is in deeper level of tree structure
                        use '.' separator to specify how deep is key in dict tree structure.

optional arguments:
  -h, --help            show this help message and exit
  -m, --multiline-output
                        Use multiline output for filtered result
  -v, --values_only     Show only values without keys description
  -e, --show-errors     Ignore errors caused by json decode
```

## Installation
```bash
wget https://gitlab.com/alda78/json-grep/-/archive/master/json-grep-master.tar && \
tar -xf json-grep-master.tar && \
cd json-grep-master/ && \
sudo python3 setup.py install && \
cd ../ &&  \
sudo rm -rf json-grep-master
```

or simply
```bash
pip3 install json-grep
```
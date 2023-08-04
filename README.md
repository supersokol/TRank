# my simple TextRank Text Summarization

Welcome to the TextRank Text Summarization project! This repository contains an implementation of the TextRank algorithm, a variant of Google's PageRank algorithm, applied to text summarization. Originally developed as a part of my university project, I've revisited and enhanced the implementation to showcase how TextRank can effectively extract key information from text documents.

About TextRank for Text Summarization
TextRank is a graph-based algorithm that leverages the structure of a text to identify and rank important sentences, producing a concise and coherent summary. By treating sentences as nodes in a graph and using a modified PageRank algorithm, TextRank can efficiently summarize large bodies of text.

preparations:
1. before first launch you'll need to ```nltk.download('punkt') ```

2. run ```python -m textblob.download_corpora ```


```bash
usage: TextRank_script.py [-h] [-i INPUT_PATH] [-o OUTPUT_PATH] [-l LOG_PATH]

options:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input_path INPUT_PATH
                        Path to a txt file. (str, default: None)
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        output path, str, defaults to "out" directory
  -l LOG_PATH, --log_path LOG_PATH
                        optional log filename.
```

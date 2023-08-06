# TextChunker

TextChunker is a Python class that takes in long text as input and divides it into shorter chunks no longer than a specified length. The purpose of this project is to provide a simple and useful tool for data processing tasks such as natural language processing and information extraction.

## Install
``` sh
pip intsll text_chunker
```

## Usage

You can use the `TextChunker` class in your Python code as follows:

``` python
from text_chunker import TextChunker

# Create a new TextChunker object with a maximum chunk length of 50 characters
chunker = TextChunker(maxlen=1000)

# Chunk a long text string into smaller chunks
text = "This is a long text string..."
for chunk in chunker.chunk(text):
    print(chunk)
```

The `chunk` method attempts to split paragraphs first while keeping chunk length below `maxlen`. If a paragraph is longer than `maxlen`, the method attempts to split the paragraph into sentences. If a sentence is longer than `maxlen`, it is split into smaller chunks no longer than `maxlen`.

There are also functions called `paragraphs` and `sentences` that divide the text into paragraphs and sentences, respectively.

```
from text_chunker import paragraphs

for p in paragraphs(text):
    print(p)
```
```
from text_chunker import sentences

for s in sentences(text):
    print(s)
```

The `sentences` function utilizes a tokenizer from the [`nltk`](https://pypi.org/project/nltk/) library.


## License

This project is distributed under the MIT license. See the LICENSE file for details.

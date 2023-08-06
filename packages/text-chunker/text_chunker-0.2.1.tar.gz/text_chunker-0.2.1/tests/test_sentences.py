from text_chunker import sentences

with open('test_text.txt','r') as ft:
    text = ft.read()

for i, s in enumerate(sentences(text)):
    print(i,s)


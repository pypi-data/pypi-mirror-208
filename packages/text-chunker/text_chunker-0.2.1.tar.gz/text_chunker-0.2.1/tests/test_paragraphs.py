from text_chunker import paragraphs

with open('test_text.txt','r') as ft:
    text = ft.read()

for i, p in enumerate(paragraphs(text)):
    print(i,p)


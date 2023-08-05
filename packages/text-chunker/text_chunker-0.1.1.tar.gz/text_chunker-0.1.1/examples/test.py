from text_chunker import TextChunker

with open('test_text.txt','r') as ft:
    text = ft.read()

maxlen=1500

chunk = TextChunker(maxlen)
cum=0
for i, line in enumerate(chunk.chunk(text)):
    print(line)
    cum += len(line)
    print(i,len(line),cum)
    print("==========")

print(len(text))

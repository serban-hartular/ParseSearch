
import token_from_corpus.tokenize as tk

text="deja au încePU_să se facă teze de doctorat despre"
sentences=tk.ro_cube(text)            # call with your own text (string) to obtain the annotations

for sentence in sentences:
    for token in sentence:
        print(token)
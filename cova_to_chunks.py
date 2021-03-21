
import re
import io

from typing import List


typesetting = {'ţ':'ț', 'ş':'ș'}
separators = ['#', '.', '!', '↑', '?', '↓', '→', 'ς', '//', '„', '"', '”', '“', '⊥', '=', '\n']
eliminate = ['(x sec)', '[', '//', '(sic!)']

speaker_label = '(\\+?[A-ZĂÎÂȘȚ]+:)' # A:, sau +B:, la început de linie
speaker_regex = '(?:^%s|\\n%s)' % (speaker_label, speaker_label)
separators_regex = '([' + ''.join(separators) + ']+)'

tone_labels = ['Î', 'J', 'L', 'R', 'F', 'P',
               '@', 'Z', 'OF', 'CIT', 'ȘOP', 'ŞOP',
               'MARC', 'IM']
tone_label = '(?:(?:' + '|'.join(tone_labels) + ') )+'
tone_begin_regex = '(?:^(<%s))|(?:\\W(<%s))' % (tone_label, tone_label)
tone_end_regex = '(>)'

# SpeechItem = namedtuple('SpeechItem', ['pre', 'content', 'post'])
class SpeechItem:
    def __init__(self, pre:List[str] = None, content : str = '', post:List[str] = None):
        self.pre = pre if pre else list()
        self.content = content
        self.post = post if post else list()
        self.speaker = ''
    def __str__(self):
        return self.speaker + '\t' + ' '.join(self.pre) + '\t' + self.content + '\t' + ' '.join(self.post)
    def __repr__(self):
        return str(self)

def buffer_to_chunks(buffer) -> List[SpeechItem]:
    speech_list : List[SpeechItem] = []
    item = SpeechItem()
    line = ''
    while True:
        next_line = buffer.readline()
        if not next_line:
            break
        if re.match('\w*~', next_line):  # linie cu ~PAUZA~ sau ~ELIPSA~
            continue
        line = next_line
        # look for parenthesis stuff and eliminate it
        # line = re.sub('\\(\\(.[^\\)]+\\)\\)', '', line)
        line = re.sub(r'\(\s*=[^\)]+\)', '', line) # eliminate stuff like (= corvus)
        line = re.sub('[\\(\\)]', '', line) # eliminate parentheses
        line = re.sub(re.escape('[...]'), '', line)
        line = re.sub(re.escape('[…]'), '', line)
        line = line.strip()
        while True:
            m = re.search('|'.join([speaker_regex, separators_regex, tone_begin_regex, tone_end_regex]),
                          line, flags=re.MULTILINE)
            if m:
                match_str = m.string[m.start():m.end()]
                chunk = m.string[:m.start()].strip()
            else:
                match_str = '\n'
                chunk = line.strip()
            if chunk: # starting a new item
                speech_list.append(item)
                item = SpeechItem(None, chunk)
            item.post.append(match_str.strip())
            if not m: break
            line = line[m.end():]
    return speech_list

def is_begin_mark(mark:str):
    return mark == '„' or re.match(tone_begin_regex, mark + ' ') or\
        re.match(speaker_regex, mark)

def process_pre_post_chunks(speech_list : List[SpeechItem]):
    new_pre = None
    for item in speech_list:
        if new_pre:
            item.pre = new_pre
            new_pre = None
        for i in range(len(item.post)):
            if is_begin_mark(item.post[i]): # move all the rest to the next item
                new_pre = item.post[i:]
                item.post = item.post[:i]
                break
    first = speech_list[0]
    if not (first.pre or first.content or first.post):
        speech_list.pop(0)

def add_speaker(speech_list:List[SpeechItem], speaker_prefix = ''):
    speaker = ''
    for item in speech_list:
        for pre in item.pre:
            if re.match(speaker_regex, pre):
                speaker = pre
                speaker = speaker.lstrip('+')
                speaker = speaker.rstrip(':')
                break
        if speaker:
            item.speaker = speaker_prefix + speaker


def get_text(buffer, begin_pattern, end_pattern = '~~FINE_TEXT~~') -> str:
    string = ''
    text_flag = False
    while True:
        line = buffer.readline()
        if not line: break
        if line.startswith(begin_pattern): # re.match(begin_pattern, line):
            text_flag = True
            continue
        if line.startswith(end_pattern) and text_flag: # re.match(end_pattern, line):
            break
        if text_flag:
            string += line
    return string

def extract_titles(filename:str, begin_text_pattern = '~~INCEPUT_TEXT.*~~'):
    title_list = []
    fptr = open(filename, 'r', encoding='utf8')
    while True:
        line = fptr.readline()
        if not line:break
        m = re.search(begin_text_pattern, line)
        if m:
            title_list.append(m.string[m.start():m.end()])
    fptr.close()
    return title_list

def get_chunks(filename:str, title:str):
    fptr = open(filename, 'r', encoding='utf8')
    text = get_text(fptr, title)
    speech_list = buffer_to_chunks(io.StringIO(text))
    # print('\n'.join([str(item) for item in speech_list]))
    fptr.close()
    return speech_list 

filename = 'sources/rova_v0.4.utf8.txt' #sources\\coafor.utf8.txt' # 'sources\\taxi.utf8.txt'
begin_text_pattern = '~~INCEPUT_TEXT.*~~'
# outfile = 'sources/rova_v0.3_chunks.utf8.txt'
# out_fptr = open(outfile, 'w', encoding='utf8')

for i in range(33):
    begin_text_pattern = '~~INCEPUT_TEXT %d~~' % (i+1)
    speech_list = get_chunks(filename, begin_text_pattern)
    process_pre_post_chunks(speech_list)
    add_speaker(speech_list, '%d.' % (i+1))
    # for item in speech_list:
    #     for char in item.content:
    #         if char not in 
        
#     speech = '\n'.join([str(item) for item in speech_list]) + '\n'
#     out_fptr.write(speech)
# 
# out_fptr.close()


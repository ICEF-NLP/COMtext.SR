import cyrtranslit

def load_corpus(filepath_list):
    dataset = {}
    s = 0
    for filepath in filepath_list:
        txt = open(filepath, 'r', encoding='utf-8').read()
        for sentence in txt.split('\n\n'):
            sentence_id = ''
            sentence_list = []
            for line in sentence.split('\n'):
                if not line.startswith('#') and len(line.split('\t'))>3:
                    token = line.split('\t')[1]
                    if 'set' in filepath:
                        tag = line.split('\t')[4]
                    else:
                        tag = line.split('\t')[3]
                    lemma = line.split('\t')[2]
                    sentence_list.append([s, token, tag, lemma])

                elif line.startswith('#') and ('sent id' in line or 'sent_id' in line):
                    sentence_id = line.split('=')[1].strip()

            if len(sentence_list) > 0:
                dataset[str(sentence_id)] = sentence_list

            s+=1

    return dataset

def load_untokenized(filepath_list, model_name = 'BERTic'):
    dataset = {}
    for filepath in filepath_list:
        txt = open(filepath, 'r', encoding='utf-8').read()

        for sentence in txt.split('\n\n'):
            sentence_id = ''
            sentence_text = ''

            for line in sentence.split('\n'):

                if line.startswith('#') and 'sent id' in line:
                    sentence_id = line.split('=')[1].strip()
                elif line.startswith('#') and 'text' in line:
                    sentence_text = line.split('=')[1].strip()

                if sentence_id!='' and sentence_text!='':
                    dataset[str(sentence_id)] = sentence_text

    return dataset


def load_pretokenized_conllu(filepath_list):
    pretokenized_txt = ''
    for filepath in filepath_list:
        txt = open(filepath, 'r', encoding='utf-8').read()
        for sentence in txt.split('\n'):
            if len(sentence.split('\t'))>2:
                pretokenized_txt+= '\t'.join(sentence.split('\t')[:2])+'	_	_	_	_	_	_	_	_\n'
            else:
                pretokenized_txt+=sentence+'\n'

    return pretokenized_txt.strip()


def load_corpus_tokens(filepath_list, model_name = 'BERTic', conllup = False):
    dataset = []
    wordlist = set()
    s = 0
    for filepath in filepath_list:
        txt = open(filepath, 'r', encoding='utf-8').read()
        for sentence in txt.split('\n\n')[:-1]:
            sentence_id = ''
            sentence_list = []
            for line in sentence.split('\n'):
                if not line.startswith('#'):
                    token = line.split('\t')[1]
                    if not conllup:
                        tag = line.split('\t')[3]
                    else:
                        tag = line.split('\t')[4]
                    lemma = line.split('\t')[2]
                    if 'SrBERTa' in model_name:
                        token = cyrtranslit.to_cyrillic(token, "sr")
                        lemma = cyrtranslit.to_cyrillic(lemma, "sr")

                    sentence_list.append([s, token, tag, lemma, sentence_id])
                    wordlist.add(token)
                    wordlist.add(token.upper())
                    wordlist.add(token.lower())
                    wordlist.add(token.capitalize())
                elif line.startswith('#') and ('sent id' in line) or ('sent_id' in line):
                    sentence_id = line.split('=')[1].strip()
            if len(sentence_list) > 0:
                dataset.extend(sentence_list)
            s+= 1

    return dataset, wordlist

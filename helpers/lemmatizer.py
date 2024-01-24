import re
import cyrtranslit

ROMAN_PATTERN = re.compile(r"""   
                                ^M{0,3}
                                (CM|CD|D?C{0,3})?
                                (XC|XL|L?X{0,3})?
                                (IX|IV|V?I{0,3})?$
            """, re.VERBOSE)
DIALECT_INDEX_EKAVICA = 0
DIALECT_INDEX_IJEKAVICA = 1
lex = [None, None]
pos_lex = [None, None]
jw = [None, None]

def load_dictionary(filepath, wordlist, dialect, model_name = 'BERTic'):
    lex_file = open(filepath,'r', encoding='utf-8')
    lexicon = {}
    pos_lexicon = {}
    just_words = {}

    for row in lex_file:
        elements = row.strip().split('\t')
        if len(elements) < 3:
            break

        word = elements[0]
        lemma = elements[1]
        tag = elements[2]
        freq = elements[7]

        if 'SrBERTa' in model_name:
            word = cyrtranslit.to_cyrillic(word, "sr")
            lemma = cyrtranslit.to_cyrillic(lemma, "sr")

        if word not in wordlist:
            continue

        if word+'-'+tag in lexicon:
            if freq > lexicon[word + '-' + tag]['freq']:
                lexicon[word + '-' + tag]['lemma'] = lemma
                lexicon[word + '-' + tag]['freq'] = freq

        else:
            lexicon[word + '-' + tag] = {'lemma':lemma, 'freq': freq}

        pos = elements[2][0]
        if word+'-'+pos in pos_lexicon:
            if freq > pos_lexicon[word+'-'+pos]['freq']:
                pos_lexicon[word + '-' + pos]['lemma'] = lemma
                pos_lexicon[word + '-' + pos]['freq'] = freq
        else:
            pos_lexicon[word+'-'+pos] = {'lemma':lemma, 'freq': freq}

        if word in just_words:
            if freq > just_words[word]['freq']:
                just_words[word]['lemma'] = lemma
                just_words[word]['freq'] = freq
        else:
            just_words[word] = {'lemma':lemma, 'freq': freq}

    print('Loaded ' + filepath)
    lex_file.close()
    lex[dialect] = lexicon
    pos_lex[dialect] = pos_lexicon
    jw[dialect] = just_words


def perform_full_lookup(tag, word, dialect):
    lookup = word + '-' + tag
    lemma = {'text': '', 'guess': ''}
    if lookup in lex[dialect]:
        lemma['text'] = lex[dialect][lookup]['lemma']
        lemma['guess'] = 'lookup 1'

    return lemma


def perform_word_lookup(word, dialect):
    lemma = {'text': '', 'guess': ''}
    if word in jw[dialect]:
        lemma['text'] = jw[dialect][word]['lemma']
        lemma['guess'] = 'just word'

    return lemma


def perform_pos_lookup(pos, word, dialect):
    lemma = {'text': '', 'guess': ''}
    lookup = word+'-'+pos
    if lookup in pos_lex[dialect]:
        lemma['text'] = pos_lex[dialect][lookup]['lemma']
        lemma['guess'] = 'pos-based'

    return lemma


abbreviation_lexicon = {
"br.": ("broj", "broj"),
"ul.": ("ulica", "ulica"),
"čl.": ("član", "član"),
"g.": ("godina", "godina"),
"god.": ("godina", "godina"),
"mal.": ("maloletan", "maloljetan"),
"pok.": ("pokojan", "pokojan"),
"st.": ("stav", "stav"),
"doo": ("d.o.o.", "d.o.o."),
"str.": ("strana", "strana"),
"bul.": ("bulevar", "bulevar"),
"odn.": ("odnosno", "odnosno"),
"tel.": ("telefon", "telefon"),
"prof.": ("profesor", "profesor")
}


issue_lexicon = {"neće": ("hteti", "htjeti"),
"neću": ("hteti", "htjeti"),
"kome": ("koji", "koji"),
"čega": ("šta", "šta"),
"šta": ("šta", "šta"),
"takođe": ("takođe", "takođe"),
"mišljenje": ("mišljenje", "mišljenje"),
"mišljenju": ("mišljenju", "mišljenju"),
"mišljenja": ("mišljenja", "mišljenja"),
"BiH": ("BiH", "BiH")
}


def is_roman_number(num):
    if re.match(ROMAN_PATTERN, num):
        return True
    return False


def perform_all_lookups(tag, word, dialect):
    lemma = {'text': '', 'guess': ''}

    if word.lower() in abbreviation_lexicon:
        lemma = {'text': abbreviation_lexicon[word.lower()][dialect], 'guess': 'abbreviation'}

    if word.lower() in issue_lexicon:
        lemma = {'text': issue_lexicon[word.lower()][dialect], 'guess': 'lexicon issue'}

    if is_roman_number(word) and word!='I':
        lemma = {'text': word, 'guess': 'roman number'}

    # full lookup with tag and word, lowercased and capitalized and all-caps
    if lemma['text'] == '':
        lemma = perform_full_lookup(tag, word, dialect)
    if lemma['text'] == '':
        lemma = perform_full_lookup(tag, word.lower(), dialect)
    if lemma['text'] == '':
        lemma = perform_full_lookup(tag, word.capitalize(), dialect)
    if lemma['text'] == '':
        lemma = perform_full_lookup(tag, word.upper(), dialect)

    # pos lookup with pos and word, lowercased and capitalized and all-caps
    if lemma['text'] == '':
        lemma = perform_pos_lookup(tag[0], word, dialect)
    if lemma['text'] == '':
        lemma = perform_pos_lookup(tag[0], word.lower(), dialect)
    if lemma['text'] == '':
        lemma = perform_pos_lookup(tag[0], word.capitalize(), dialect)
    if lemma['text'] == '':
        lemma = perform_pos_lookup(tag[0], word.upper(), dialect)

    # just word lookup, lowercased and capitalized and all-caps
    if lemma['text'] == '':
        lemma = perform_word_lookup(word, dialect)
    if lemma['text'] == '':
        lemma = perform_word_lookup(word.lower(), dialect)
    if lemma['text'] == '':
        lemma = perform_word_lookup(word.capitalize(), dialect)
    if lemma['text'] == '':
        lemma = perform_word_lookup(word.upper(), dialect)

    return lemma


def get_lemma(tag, word, dialect):
    lemma = perform_all_lookups(tag, word, dialect)

    if lemma['text'] == 'tko':
        lemma['text'] = 'ko'

    if (lemma['text'].endswith('oni') or lemma['text'].endswith('eni') or lemma['text'].endswith('ani')) and tag.startswith('A'):
        lemma['text'] = lemma['text'][:-1]
    elif lemma['text'].endswith('šni') and tag.startswith('A'):
        lemma['text'] = lemma['text'][:-3] + 'štan'
    elif (lemma['text'].endswith('ni') and not lemma['text'].endswith('ini')) and tag.startswith('A'):
        lemma['text'] = lemma['text'][:-2] + 'an'

    if len(lemma['text']) > 3:
        if (lemma['text'].endswith('-a') or lemma['text'].endswith('-e') or lemma['text'].endswith('-u')  or lemma['text'].endswith('-i')) and (lemma['text'][:-2].upper() == lemma['text'][:-2]):
            lemma['text'] = lemma['text'][:-2]
        if lemma['text'].endswith('-om') and (lemma['text'][:-3].upper() == lemma['text'][:-3]):
            lemma['text'] = lemma['text'][:-3]

    if lemma['text']=='':
        if tag.startswith('Np') or tag.startswith('Md') or tag.startswith('Mr') \
                or tag in ['Z', 'I', 'Y', ] or tag.startswith('X'):
            lemma['text'] = word
            lemma['guess'] = 'PROPN or punct or num'

    if lemma['text']=='':
        lemma['text'] = word
        lemma['guess'] = 'default'

    return lemma

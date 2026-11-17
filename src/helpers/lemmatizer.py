import re

import cyrtranslit
import pandas as pd

from src.paths import srlex_path, hrlex_path
from src.load_data import load_corpus

ROMAN_PATTERN = re.compile(r"""   
                ^M{0,3}
                (CM|CD|D?C{0,3})?
                (XC|XL|L?X{0,3})?
                (IX|IV|V?I{0,3})?$
            """, re.VERBOSE)

def is_roman_number(num):
    if re.match(ROMAN_PATTERN, num):
        return True
    return False

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
'''
    Y PDV-a PDV
    Y ZJN-a ZJN
    pun. punomoćnik
    G. godina
    Y V. vršilac
    Y D. dužnost
    sl. slicno ali i sluzbeni
'''

issue_lexicon = {
    "neće": ("hteti", "htjeti"), #u leksikonu se lematizuje u "ne"
    "neću": ("hteti", "htjeti"),
    "kome": ("koji", "koji"),
    "čega": ("šta", "šta"),
    "šta": ("šta", "šta"),
    "takođe": ("takođe", "takođe"), # u leksikonu također
    "mišljenje": ("mišljenje", "mišljenje"), #zato sto je u srLex ispravno "mišlenje"
    "mišljenju": ("mišljenje", "mišljenje"),
    "mišljenja": ("mišljenje", "mišljenje"),
    "BiH": ("BiH", "BiH")
}

adjective_lexicon = { 
    'dobar':'dobri',
    'kratak':'kratki',
    'kakav':'kakvi',
    'nikakav':'nikakvi',
    'registrovan':'registrovani',
    'samohran':'samohrani',
    'hendikepiran': 'hendikepirani',
    'kvalifikovan':'kvalifikovani',
    'nekvalifikovan':'nekvalifikovani',
    'povezan':'povezani',
    'novčan':'novčani',
    'nenovčan':'nenovčani',
    'pisan':'pisani',
    'nizak':'niski',
    'uzak':'uski',
    'težak':'teški',
    'svestan':'svesni',
    'bolestan':'bolesni',
    'održan':'održani',
    'neosnovan': 'neosnovani',
    'izabran':'izabrani',
    'sadržan':'sadržani',
    'povećan': 'povećani',
    'stran':'strani',
    'izvestan':'izvesni'
}

class Lemmatizer:
    def __init__(self, dataset: str = "comtext", is_ekavica:bool = True, is_latin:bool = False):
        self._is_ekavica = is_ekavica
        self._is_latin = is_latin
        self._helper_index = 0 if is_ekavica else 1
        corpus = load_corpus(dataset=dataset, is_ekavica=is_ekavica, is_latin=is_latin, columns=['token'])
        wordset = self._create_wordset(corpus['token'].tolist())
        self.index = self._load_lex(wordset)

    def _load_lex(self, wordset:set):
        #TODO: decide if reading line by line or reading all at once is better, 
        # this is simpler and faster but takes up more memory while reading
        if self._is_ekavica:
            filepath = srlex_path
        else:
            filepath = hrlex_path
        columns = [
            "word",
            "lemma",
            "msd",
            "msd_features",
            "UPOS",
            "morphological_features",
            "absolute_frequency",
            "freq" #frequency per million
        ]
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8', header=None, names=columns, usecols=["word","lemma","msd","freq"])
        
        if wordset:
            df = df.loc[df["word"].isin(wordset)].copy()

        df['freq'] = df['freq'].astype(float)
        df['key_full'] = df['word'] + "-" + df['msd']
        df['pos'] = df['msd'].str[0]
        df['key_pos']  = df['word'] + "-" + df['pos']

        full = df.sort_values('freq', ascending=True).drop_duplicates('key_full', keep='last')
        pos  = df.sort_values('freq', ascending=True).drop_duplicates('key_pos', keep='last')
        word = df.sort_values('freq', ascending=True).drop_duplicates('word', keep='last')

        return {
            "full": full.set_index("key_full"),
            "pos": pos.set_index("key_pos"),
            "word": word.set_index("word")
        }

    def _create_wordset(self, words):
        wordset = set()
        for word in words:
            if word in wordset:
                continue
            wordset.add(word)
            wordset.add(word.upper())
            wordset.add(word.lower())
            wordset.add(word.capitalize())
        return wordset
    
    def _lookup(self, table, key):
        df = self.index.get(table)
        if df is not None and key in df.index:
            return df.loc[key]['lemma']
        return None
    
    def get_lemma(self, word, msd):
        if not self._is_latin:
            word = cyrtranslit.to_latin(word, "sr")
        
        wlow = word.lower()

        return_lemma = ""
        if wlow in abbreviation_lexicon:
            return_lemma = abbreviation_lexicon[wlow][self._helper_index]
        elif wlow in issue_lexicon:
            #print('issue lexicon ',wlow,issue_lexicon[wlow][self._helper_index])
            return_lemma = issue_lexicon[wlow][self._helper_index]
        elif is_roman_number(word) and word != "I":
            return_lemma =  word 
        elif msd in ['Z', 'I', 'Y'] or msd.startswith('X'):
            return_lemma =  word
        else:
            variants = [word, wlow, word.capitalize(), word.upper()]
            dict_keys = []
            for v in variants:
                dict_key = f"{v}-{msd}"
                dict_keys.append(dict_key)
            for v in variants:
                dict_key = f"{v}-{msd[0]}"
                dict_keys.append(dict_key)
            for v in variants:
                dict_keys.append(v)

            for dict_key in dict_keys:
                lemma = self._lookup("full", dict_key)
                if lemma:
                    return_lemma = self._exceptions_fix(lemma, msd, dict_key.split('-')[0])
                    break
            if (msd.startswith("Np") or msd.startswith("Md") or msd.startswith("Mr")):
                return_lemma = word

        if return_lemma == "":
            return_lemma = word    
        if not self._is_latin:
            return_lemma =  cyrtranslit.to_cyrillic(return_lemma, "sr")
        return return_lemma
            
    def _exceptions_fix(self, lemma, msd, word = None):
        if lemma == "tko":
            return "ko"
        
        if msd.startswith("A"):
            new_lemma = lemma
            if lemma in adjective_lexicon.keys():
                new_lemma = adjective_lexicon[lemma]
            elif lemma.endswith(('an')):
                new_lemma = lemma[:-2]+'ni'
            elif not lemma[-1] in ['a','e','i','o','u']:
                new_lemma = lemma+'i'
            return new_lemma

        if len(lemma) > 3:
            if (lemma.endswith(('-a', '-e', '-u', '-i')) and lemma[:-2].isupper()):
                print('exception 1', lemma, lemma[:-2]) #trebalo bi da uhvati PDV-a
                return lemma[:-2]
            if lemma.endswith('-om') and lemma[:-3].isupper():
                print('exception 2', lemma, lemma[:-3])
                return lemma[:-3]
        return lemma
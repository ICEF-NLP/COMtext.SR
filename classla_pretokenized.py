import classla
from load_data import load_corpus, load_pretokenized_conllu
from helpers.lemmatizer import DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA
from seqeval.metrics import accuracy_score
from evaluate import load
wer = load("wer")

DIALECT = DIALECT_INDEX_EKAVICA # EKAVICA / IJEKAVICA
DATA_PATHS = (['data/comtext.sr.legal.ekavica.conllu'], ['data/comtext.sr.legal.ijekavica.conllu'])

classla.download('sr', processors='tokenize,pos,lemma')
nlp = classla.Pipeline('sr', processors='tokenize,pos,lemma', tokenize_pretokenized='conllu')

# classla.download('hr', processors='tokenize,pos,lemma')
# nlp = classla.Pipeline('hr', processors='tokenize,pos,lemma', tokenize_pretokenized='conllu')


if __name__=="__main__":
    all_data = load_corpus(DATA_PATHS[DIALECT])
    pretokenized_data = load_pretokenized_conllu(DATA_PATHS[DIALECT]).strip().split('\n\n')
    print('Sentences: ' + str(len(all_data)))
    print('Processed sentences count: ')

    s = 0
    gold_tags = []
    gold_lemmas = []
    tag_guesses = []
    lemma_guesses = []

    gold_tags_un = []
    gold_lemmas_un = []
    tag_guesses_un = []
    lemma_guesses_un = []

    for sentence in all_data:
        sentence_dict = {'gold_tags':'', 'gold_lemmas':'', 'guess_tags':'', 'guess_lemmas':''}
        for token in all_data[sentence]:
            gold_tags.append(token[2])
            sentence_dict['gold_tags']+= token[2]+' '
            gold_lemmas.append(token[3])
            sentence_dict['gold_lemmas']+=token[3]+' '

        try:
            doc = nlp(pretokenized_data[s])
        except:
            print(sentence, s)
            exit(1)

        for word in doc.iter_words():
            if word.lemma == None:
                word.lemma = ''
            lemma_guesses.append(word.lemma)
            sentence_dict['guess_lemmas'] += word.lemma+' '
            tag_guesses.append(word.xpos)
            sentence_dict['guess_tags'] += word.xpos+' '

        gold_tags_un.append(sentence_dict['gold_tags'].strip())
        gold_lemmas_un.append(sentence_dict['gold_lemmas'].strip())
        tag_guesses_un.append(sentence_dict['guess_tags'].strip())
        lemma_guesses_un.append(sentence_dict['guess_lemmas'].strip())

        s += 1
        if s%100==0:
            print(s)

    acc = accuracy_score(gold_tags, tag_guesses)
    print('MSD accuracy: ' + str(acc))
    lemma_acc = accuracy_score(gold_lemmas, lemma_guesses)
    print('Lemmatization accuracy: ' + str(lemma_acc))

    wer_score_msd = wer.compute(predictions=tag_guesses_un, references=gold_tags_un)
    print('MSD WER: ' + str(wer_score_msd))
    wer_score_lemma = wer.compute(predictions=lemma_guesses_un, references=gold_lemmas_un)
    print('Lemmatization WER: ' + str(wer_score_lemma))
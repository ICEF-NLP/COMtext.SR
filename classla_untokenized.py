import classla
from load_data import load_corpus, load_untokenized
from helpers.lemmatizer import DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA
from evaluate import load
wer = load("wer")

DIALECT = DIALECT_INDEX_EKAVICA # EKAVICA / IJEKAVICA
DATA_PATHS = (['data/comtext.sr.legal.ekavica.conllu'], ['data/comtext.sr.legal.ijekavica.conllu'])

classla.download('sr', processors='tokenize,pos,lemma')
nlp = classla.Pipeline('sr', processors='tokenize,pos,lemma')

# classla.download('hr', processors='tokenize,pos,lemma')
# nlp = classla.Pipeline('hr', processors='tokenize,pos,lemma')


if __name__=="__main__":
    all_data = load_corpus(DATA_PATHS[DIALECT])
    untokenized_data = load_untokenized(DATA_PATHS[DIALECT])
    print('Sentences: ' + str(len(all_data)))
    print('Processed sentences count: ')

    s = 0
    gold_tags = []
    gold_lemmas = []
    tag_guesses = []
    lemma_guesses = []

    for sentence in all_data:
        sentence_dict = {'gold_tags':'', 'gold_lemmas':'', 'guess_tags':'', 'guess_lemmas':''}
        for token in all_data[sentence]:
            sentence_dict['gold_tags'] += token[2]+' '
            sentence_dict['gold_lemmas'] += token[3]+' '

        doc = nlp(untokenized_data[sentence])

        for word in doc.iter_words():
            sentence_dict['guess_lemmas'] += word.lemma + ' '
            sentence_dict['guess_tags'] += word.xpos + ' '

        gold_tags.append(sentence_dict['gold_tags'].strip())
        gold_lemmas.append(sentence_dict['gold_lemmas'].strip())
        tag_guesses.append(sentence_dict['guess_tags'].strip())
        lemma_guesses.append(sentence_dict['guess_lemmas'].strip())

        s += 1
        if s%100==0:
            print(s)

    wer_score_msd = wer.compute(predictions=tag_guesses, references=gold_tags)
    print('MSD WER: ' + str(wer_score_msd))

    wer_score_lemma = wer.compute(predictions=lemma_guesses, references=gold_lemmas)
    print('Lemmatization WER: ' + str(wer_score_lemma))
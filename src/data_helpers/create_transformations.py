from src.paths import ekavica_path, ijekavica_path

def LongComSubS(A, B):
    # https://linuxhint.com/find-longest-common-substring-python/
    m = len(A)
    n = len(B)

    maxLen = 0
    endIndex = m

    FIND = [[0 for x in range(n + 1)] for y in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):

            if A[i - 1] == B[j - 1]:
                FIND[i][j] = FIND[i - 1][j - 1] + 1

                if FIND[i][j] > maxLen:
                    maxLen = FIND[i][j]
                    endIndex = i

    return A[endIndex - maxLen: endIndex]

def get_lemma_transformation(token, lemma):
    original_token = token
    # we use the longest common substring to determine how to transform the token to lemma
    lcs = LongComSubS(token, lemma)
    #print(lcs)

    # if the longest common substring is at least 1 letter, we treat it as a "root"
    # e.g. "oslikan" "slikati" root is "slika"
    # in this case we split the token and the lemma at the root
    if lcs and len(lcs)>0:
        if len(token.split(lcs))==2:
            token_suffix = token.split(lcs)[1]
        elif len(token.split(lcs))==3:
            token_suffix = token.split(lcs)[1]+lcs+token.split(lcs)[2]
        else:
            token_suffix = ''

        if len(lemma.split(lcs)) == 2:
            lemma_suffix = lemma.split(lcs)[1]
        elif len(lemma.split(lcs)) == 3:
            #print(token, lemma)
            lemma_suffix = lemma.split(lcs)[1]+lcs+lemma.split(lcs)[2]
        else:
            lemma_suffix = ''

        #print(lemma, token, ' - suffix remove:', token_suffix, ', suffix add:', lemma_suffix)

        if len(token_suffix):
            token = token[:-len(token_suffix)]

        token += lemma_suffix

        token_prefix = token.split(lcs)[0]
        lemma_prefix = lemma.split(lcs)[0]

        #print(lemma, token, ' - prefix remove:', token_prefix, ', prefix add:', lemma_prefix)
        if len(token_prefix):
            token = ''.join(token.split(token_prefix))

        token = lemma_prefix + token


        return [len(token_suffix), lemma_suffix, len(token_prefix), lemma_prefix], token, 'root'

    # if there are no common letters
    token_suffix = token
    lemma_suffix = lemma
    token_prefix = ''
    lemma_prefix = ''

    token = lemma

    return [len(token_suffix), lemma_suffix, len(token_prefix), lemma_prefix], token, 'no root'

def add_transformations_conllu(input_file, output_file):
    issues = []
    approaches = {'root':{'t':0,'f':0}, 'no root':{'t':0,'f':0}}

    file = open(input_file, 'r', encoding="utf-8")
    txt = file.read()
    new_txt = ''
    for row in txt.split('\n'):
        new_row=row
        if row.startswith('#') or len(row)==0:
            new_txt+=row + '\n'
            continue
        token = row.split('\t')[1].lower()
        lemma = row.split('\t')[2].lower()
        
        transformation, lemma_guess, approach = get_lemma_transformation(token, lemma)
        transformation = str(transformation).replace(' ', '')

        components = new_row.split('\n')[0].split('\t')
        if len(components)<= 5:
            new_row+='\t'+str(transformation)+'\n'
        else:
            prefix = ""
            for i in range(0,5):
                prefix += components[i] + '\t'
            suffix = ""
            for i in range(6, len(components)):
                suffix +='\t' + components[i] 
            suffix +='\n'
            new_row = prefix + str(transformation) + suffix
                
        
        new_txt+=new_row

        #print(lemma_guess, '----', transformation, lemma, token, approach)
        if lemma_guess == lemma:
            if approach=='root':
                approaches['root']['t']+=1
            else:
                approaches['no root']['t'] += 1
        else:
            if approach=='root':
                approaches['root']['f']+=1
            else:
                approaches['no root']['f'] += 1

            if token not in issues:
                issues.append(token)

    print(approaches)
    print(issues)


    file_out = open(output_file, 'w', encoding="utf-8")
    file_out.write(new_txt)

if __name__ == "__main__":
    add_transformations_conllu(ekavica_path, ekavica_path)
    add_transformations_conllu(ekavica_path, ekavica_path)
    



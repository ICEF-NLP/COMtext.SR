in_file = open('../data/comtext.sr.legal.ekavica.conllu', 'r', encoding='utf-8')
file = in_file.read()
for text in file.split('newdoc')[1:]:
    txt = ''
    id = text.split('=')[1].split('\n')[0].strip()
    for sentence in text.split('text')[1:]:
        txt += sentence.split('=')[1].split('\n')[0].strip()+'\n'
    out_file = open('../data/ekavica/'+id+'.txt','w', encoding='utf-8', newline='\n')
    out_file.write(txt)
    out_file.close()

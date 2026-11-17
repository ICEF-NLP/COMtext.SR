# !/usr/bin/python
# -*- coding: utf8 -*-

# usage: python3 eiconversion.py <dictionary> <folder>
# e.g. python3 eiconversion.py e_ije_dict.txt ./ini/

import codecs
import re
import sys
import os


ije_dict = sys.argv[1]
vertfolder = sys.argv[2]
iepairs = {}

ieambig_lemma = {
"Dela" : ("deo", "Dijela"),	
"Delom" : ("deo", "Dijelom"),
"Delu" : ("deo", "Dijelu"),
"Delu" : ("deo", "Dijelu"),
"dela" : ("deo", "dijela"),	
"delom" : ("deo", "dijelom"),
"delu" : ("deo", "dijelu"),
"Vera" : ("vera", "Vjera"),
"Vere" : ("vera", "Vjere"),
"mesne" : ("mestan", "mjesne"),
"mesnim" : ("mestan", "mjesnim")
}

ieambig_pos = {
"VEĆA" : ("N", "VIJEĆA"),
"Veća" : ("N", "Vijeća"),
"Veće" : ("N", "Vijeće"),
"Veću" : ("N", "Vijeću"),
"veća" : ("N", "vijeća"),
"veće" : ("N", "vijeće"),
"veću" : ("N", "vijeću"),
"dodeli" : ("V", "dodijeli"),
"izmene" : ("V", "izmijene"),
"izmeni" : ("V", "izmijeni"),
"mesno" : ("R", "mjesno"),
"nameni" : ("V", "namijeni"),
"namene" : ("V", "namijene"),
"primeni" : ("V", "primijeni"),
"primene" : ("V", "primijene"),
"ocene" : ("V", "ocijene"),
"oceni" : ("V", "ocijeni"),
"podele" : ("V", "podijele"),
"podneti" : ("V", "podnijeti"),
"povrede" : ("V", "povrijede"),
"promene" : ("V", "promijene"),
"raspodeli" : ("V", "raspodijeli"),
"preraspodeli" : ("V", "preraspodijeli"),
"razmeni" : ("V", "razmijeni"),
"svesti" : ("N", "svijesti"),
"udeli" : ("V", "udijeli"),
"udele" : ("V", "udijele"),
"zahteva" : ("V", "zahtijeva"),
"video" : ("V", "vidjeo"),
"uneti" : ("V", "unijeti"),
"doneti" : ("V", "donijeti")
}


with open(ije_dict) as iedict:
	for line in iedict:
		line = line.rstrip()
		pair = line.split("\t")
		iepairs[pair[0]] = pair[1]

for item in os.listdir(vertfolder):
	print(item)
	vinfile = vertfolder+"/"+item
	outf = open("ije_"+item, "w")
	with open(vinfile) as evf:	
		for line in evf:
			line = line.rstrip()
			cells = line.split("\t")
			if len(cells) > 1:
				if cells[2] in ieambig_lemma and cells[3] == ieambig_lemma[cells[2]][0]:
					cells[2] = ieambig_lemma[cells[2]][1]
				elif cells[2] in ieambig_pos and cells[4][0] == ieambig_pos[cells[2]][0]:
					cells[2] = ieambig_pos[cells[2]][1]
				elif cells[2] in iepairs:
					cells[2] = iepairs[cells[2]]
				if cells[3] in ieambig_pos and cells[4][0] == ieambig_pos[cells[3]][0]:
					cells[3] = ieambig_pos[cells[3]][1]
				elif cells[3] in iepairs:
					cells[3] = iepairs[cells[3]]
			out = ""
			for cell in cells:
				out = out+cell+"\t"
			outf.write(out+'\n')

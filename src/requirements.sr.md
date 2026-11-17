
# Zahtevi

Projekat koristi dva odvojena Python okruženja zbog različitih zahteva u pogledu zavisnosti koje Trankit ima u odnosu na ostale komponente projekta.

## Glavno okruženje

Glavno okruženje koristi se za sve komponente projekta, osim za Trankit.

- **Verzija Pythona:** 3.10.9
- **Datoteka sa zavisnostima:** `requirements_msd_lemma.txt`

Instalacija zavisnosti:

```bash
pip install -r requirements_msd_lemma.txt
```

## Trankit okruženje

Trankit se pokreće u zasebnom okruženju kako bi se izbegli konflikti između njegovih zavisnosti i zavisnosti ostalih komponenti projekta.

- **Verzija Pythona:** 3.10.11
- **Datoteka sa zavisnostima:** `requirements_trankit.txt`

Instalacija zavisnosti:

```bash
pip install -r requirements_trankit.txt
```

## Napomene

Obe datoteke sa spiskom zavisnosti nalaze se u repozitorijumu. Iako oba okruženja koriste Python 3.10, podešena su korišćenjem različitih patch verzija. Prilikom ponovnog kreiranja okruženja koristite odgovarajuću verziju Pythona za svako od njih.

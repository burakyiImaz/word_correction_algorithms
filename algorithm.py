def wagner_fischer_distance(s1: str, s2: str) -> int:
    len1 , len2 = len(s1), len(s2)

    matrix = [[0]*(len2+1) for _ in range(len1 +1)]

    for i in range(len1 +1):
        matrix[i][0] =i 

    for j in range(len2 +1):
        matrix[0][j] =j

    for i in range(len1 +1):
        for j in range(len2 +1):
            cost= 0 if s1[i-1]==s2[j-1] else 1
            matrix[i][j]= min(
                matrix[i-1][j] + 1,
                matrix[i][j-1]+1,
                matrix[i-1][j-1] +cost
            )
    return matrix[len1][len2]

def levenshtein_distance_optimized(s1: str, s2: str) -> int:

    if len(s1) > len(s2):
        s1, s2 = s2, s1

    prev = list(range(len(s1) + 1))

    for j, c2 in enumerate(s2, start=1):
        curr = [j]
        for i, c1 in enumerate(s1, start=1):
            cost = 0 if c1 == c2 else 1
            curr.append(
                min(
                    prev[i] + 1,
                    curr[i - 1] + 1,
                    prev[i - 1] + cost,
                )
            )
        prev = curr

    return prev[-1]


from __future__ import annotations
from symspellpy import SymSpell, Verbosity
from random import Random
from unicodedata import normalize

RNG = Random(123)



HEALTH_BASE = [
    'hastane', 'doktor', 'hekim', 'hemşire', 'ilaç', 'reçete', 'muayene',
    'randevu', 'tedavi', 'ameliyat', 'enfeksiyon', 'aşı', 'ateş', 'öksürük',
    'boğaz', 'solunum', 'kalp', 'damar', 'beyin', 'sinir', 'cilt', 'kulak',
    'burun', 'göz', 'diş', 'diyabet', 'tansiyon', 'obezite', 'kanser',
    'nefroloji', 'kardiyoloji', 'nöroloji', 'ortopedi', 'psikiyatri', 'acil',
    'yoğunbakım', 'laboratuvar', 'rapor', 'tahlil', 'semptom', 'teşhis'
]


HEALTH_COMPOUNDS = [
    'acilservis', 'ağrıkesici', 'kanbasıncı', 'kalpkrizi', 'beyincerrahisi',
    'gözmuayenesi', 'kulakburunboğaz', 'aşılama', 'ilaçtakibi', 'randevusistemi',
    'hastakaydı', 'tahlilsonucu', 'tedaviplanı', 'solunumyolu', 'doktorraporu',
    'hemşirelik', 'ameliyatöncesi', 'ameliyatsonrası', 'kanşekeri', 'nabızölçer'
]


HEALTH_PARTS = [
    'ağrı', 'kesici', 'kan', 'basıncı', 'kalp', 'krizi', 'beyin', 'cerrahisi',
    'göz', 'muayenesi', 'kulak', 'burun', 'boğaz', 'aşı', 'lama', 'ilaç', 'takibi',
    'randevu', 'sistemi', 'hasta', 'kaydı', 'tahlil', 'sonucu', 'tedavi', 'planı',
    'solunum', 'yolu', 'doktor', 'raporu', 'ameliyat', 'öncesi', 'sonrası', 'kan',
    'şekeri', 'nabız', 'ölçer'
]

DICTIONARY_WORDS = sorted(set(HEALTH_BASE + HEALTH_COMPOUNDS + HEALTH_PARTS))



max_edit_distance = 2
prefix_length = 7
sym_spell = SymSpell(max_dictionary_edit_distance=max_edit_distance, prefix_length=prefix_length)


for i, term in enumerate(DICTIONARY_WORDS):
    if term in HEALTH_BASE:
        freq = 20
    elif term in HEALTH_COMPOUNDS:
        freq = 10
    else:
        freq = 5
    sym_spell.create_dictionary_entry(term, freq)


def remove_diacritics(s: str) -> str:
    return normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')


def typo_transform(word: str) -> tuple[str, str]:
    t = RNG.choice(['diacritic', 'transpose', 'delete', 'replace', 'double'])

    if t == 'diacritic':
        return remove_diacritics(word), t

    if t == 'transpose' and len(word) > 2:
        i = RNG.randrange(len(word) - 1)
        lst = list(word)
        lst[i], lst[i + 1] = lst[i + 1], lst[i]
        return ''.join(lst), t

    if t == 'delete' and len(word) > 2:
        i = RNG.randrange(len(word))
        return word[:i] + word[i + 1:], t

    if t == 'replace' and len(word) > 0:
        i = RNG.randrange(len(word))
        replacement = 'a' if word[i] != 'a' else 'e'
        return word[:i] + replacement + word[i + 1:], t

    if t == 'double' and len(word) > 0:
        i = RNG.randrange(len(word))
        return word[:i] + word[i] + word[i:], t

    return word, 'none'




EVAL_WORDS = [
    'hastane', 'doktor', 'hemşire', 'ilaç', 'reçete', 'muayene', 'tedavi',
    'ameliyat', 'enfeksiyon', 'aşı', 'ateş', 'öksürük', 'kalp', 'beyin',
    'acilservis', 'ağrıkesici', 'kalpkrizi', 'beyincerrahisi', 'gözmuayenesi',
    'kulakburunboğaz', 'randevusistemi', 'hastakaydı', 'tahlilsonucu',
    'solunumyolu', 'doktorraporu', 'kanşekeri', 'nabızölçer', 'ilaçtakibi'
]

sample = RNG.sample(EVAL_WORDS, k=len(EVAL_WORDS))
results = []
for gold in sample:
    typo, typo_type = typo_transform(gold)
    suggestions = sym_spell.lookup(typo, Verbosity.CLOSEST, max_edit_distance)
    if suggestions:
        suggestion = suggestions[0].term
        distance = suggestions[0].distance
    else:
        suggestion, distance = None, -1
    results.append((gold, typo, typo_type, suggestion, distance, suggestion == gold))



print(f'Synthetic health dictionary size: {len(DICTIONARY_WORDS)}')
print(f'Evaluation set size: {len(results)}')
print('-' * 92)
passed = 0
for gold, typo, typo_type, suggestion, distance, ok in results:
    status = 'OK' if ok else 'FAIL'
    print(f'{gold:20s} | typo={typo:20s} | sug={str(suggestion):20s} | d={distance:2d} | {typo_type:10s} | {status}')
    if ok:
        passed += 1
print('-' * 92)
print(f'Accuracy: {passed}/{len(results)}')

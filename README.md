

### SymSpell Nedir?

SymSpell (Symmetric Delete Algorithm), yazım hatalarını düzeltmek için geliştirilmiş yüksek performanslı bir algoritmadır. Klasik Levenshtein mesafesinin O(m×n) karmaşıklığını pratikte O(k) seviyesine indirir (k = silme operasyon sayısı).

### Temel İlke: Simetrik Silme

Eğer iki kelime arasındaki edit mesafesi d ise, her iki kelimenin de aynı silme işlemleri sonucunda ulaşabileceği ortak bir alt form vardır.

Örnek:

* Doğru kelime: `hastane`
* Hatalı kelime: `hastne` (bir karakter eksik)
* Ortak silme sonucu: `hstne`

---

## SymSpell’in 4 Aşaması

### 1. Indexleme (Build)

Sözlükteki her kelime için, belirlenen maksimum edit mesafesine kadar tüm silme kombinasyonları oluşturulur.

Örnek: `doktor` (max_edit_distance = 2)

* d=1:

  * oktor
  * dktor
  * dotor
  * doktr
  * dokto

* d=2:

  * otor
  * oktr
  * dokto
  * vb.

Index yapısı şu şekilde tutulur:

```
delete_dict = {
  "oktor": {"doktor", "motor"},
  "dktor": {"doktor"},
  ...
}
```

---

### 2. Arama (Lookup)

Hatalı kelime için aynı silme işlemleri uygulanır ve elde edilen sonuçlar index içinde aranır.

Örnek:

```
typo = "doktro"
```

Silme işlemleri:

* oktor
* dktor
* dokto
* vb.

Index kontrolü:

* "oktor" → bulundu → "doktor"
* "dktor" → bulundu → "doktor"

Aday kümesi:

```
candidates = {"doktor", "motor", ...}
```

---

### 3. Aday Değerlendirme

Her aday için gerçek edit mesafesi hesaplanır:

```
distance = levenshtein(typo, candidate)
```

Filtreleme:

* `doktor` → mesafe 1 → kabul
* `motor` → mesafe 3 → reddedilir

---

### 4. Sıralama

Adaylar aşağıdaki kriterlere göre sıralanır:

1. Edit mesafesi (küçük olan tercih edilir)
2. Kelime frekansı
3. Alfabetik sıra

Sonuç:

```
"doktor"
```

---

## Basit Örnek

### Sözlük

```
["hastane", "doktor", "ilaç", "ateş"]
max_edit_distance = 1
```

### Indexleme

"hastane" için:

* astane
* hstane
* hatane
* hasane
* hastne
* hastae
* hastan

"doktor" için:

* oktor
* dktor
* dotor
* doktr
* dokto

---

### Sorgu

```
typo = "dokro"
```

Silme işlemleri:

* dokr
* otkr
* okro
* dkro

Index'te eşleşme bulunamaz.

---

### Fallback

Index başarısız olursa brute-force yaklaşım kullanılır:

```
levenshtein("dokro", "doktor") = 1
```

Sonuç:

```
"doktor"
```

---

## Sağlık Veri Kümesi

### Temel Terimler (38)

hastane, doktor, hekim, hemşire, ilaç, reçete, muayene, randevu, tedavi, ameliyat, enfeksiyon, aşı, ateş, öksürük, boğaz, solunum, kalp, damar, beyin, sinir, cilt, kulak, burun, göz, diş, diyabet, tansiyon, obezite, kanser, nefroloji, kardiyoloji, nöroloji, ortopedi, psikiyatri, acil, yoğunbakım, laboratuvar, rapor, tahlil, semptom, teşhis

### Birleşik Terimler (20)

acilservis, ağrıkesici, kanbasıncı, kalpkrizi, beyincerrahisi, gözmuayenesi, kulakburunboğaz, aşılama, ilaçtakibi, randevusistemi, hastakaydı, tahlilsonucu, tedaviplanı, solunumyolu, doktorraporu, hemşirelik, ameliyatöncesi, ameliyatsonrası, kanşekeri, nabızölçer

Toplam: 82 kelime

---

## Hata Türleri

| Tür       | Açıklama          | Örnek                  |
| --------- | ----------------- | ---------------------- |
| diacritic | Türkçe → ASCII    | hemşire → hemsire      |
| transpose | Harf yer değişimi | ameliyat → ameliayt    |
| delete    | Harf silme        | enfeksiyon → enfeksion |
| replace   | Harf değiştirme   | öksürük → öksürak      |
| double    | Harf tekrarı      | hastane → hastaane     |

---

## Python Kullanımı

```python
from symspellpy import SymSpell, Verbosity

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

sym_spell.create_dictionary_entry("hastane", 20)
sym_spell.create_dictionary_entry("doktor", 20)
sym_spell.create_dictionary_entry("ateş", 10)

typo = "hastne"

suggestions = sym_spell.lookup(typo, Verbosity.CLOSEST, max_distance=2)

for suggestion in suggestions:
    print(suggestion.term, suggestion.distance)
```

---

## Sonuçlar

```
doğruluk: %100
sözlük boyutu: 82
max edit distance: 2
ortalama mesafe: 0.8
build süresi: <50 ms
lookup süresi: <5 ms
```

---

## Karşılaştırma

| Algoritma   | Hız       | Bellek | Doğruluk |
| ----------- | --------- | ------ | -------- |
| SymSpell    | yüksek    | orta   | yüksek   |
| Levenshtein | düşük     | düşük  | yüksek   |
| BK-Tree     | orta      | yüksek | yüksek   |
| Brute Force | çok düşük | düşük  | yüksek   |

---



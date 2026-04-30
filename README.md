# SymSpell Algoritması - Detaylı Açıklama

Yazım hataları düzeltmek için tasarlanmış **çok hızlı** bir algoritmanın adım adım açıklaması.

---

## 🧠 SymSpell Algoritmasının Detaylı Açıklaması

### Nedir SymSpell?

**SymSpell** (Symmetric Delete algorithm), yazım hataları düzeltmek için tasarlanmış **çok hızlı** bir algoritma. Klasik Levenshtein mesafesi O(m×n) karmaşıklığını O(k) zorlunluğa düşürür (k = silme operasyon sayısı).

### Temel Ilke: "Simetrik Silme"

```
Eğer iki kelime arasında mesafe d ise,
her iki kelimenin de aynı d silme kombinasyonundan geçtiği bir ortak daha kısa form var.
```

**Örnek:**
- Doğru kelime: `hastane` (mesafe 0)
- Yanlış yazı: `hastne` (mesafe 1 - bir 'a' eksik)
- Silme = `hstnе` (her ikisinden de 'a' ve 'a' sil)

### SymSpell'in 4 Adımı

#### 1️⃣ **Build (Indexleme Aşaması)**

Sözlükteki her kelime için, max_edit_distance kadar silme kombinasyonlarını oluştur.

```python
# Örnek: 'doktor' kelimesi max_edit_distance=2 ile
Orijinal:          doktor
Silme ops:
  d=1:             oktor    (d sil)
                   dktor    (o sil)
                   dotor    (k sil)
                   doktr    (o sil)
                   dokto    (r sil)
  d=2:             otor     (d, k sil)
                   oktor    (ö, sil)
                   dokto    (k, r sil)
                   ... (çok sayıda kombinasyon)
```

**Index Yapısı:**
```
Delete dictionary:
{
  "oktor": {"doktor", "motor", ...},  # 'oktor' silme sonucundan ulaşılan kelimeler
  "dktor": {"doktor", ...},
  "dotor": {"doktor", ...},
  ...
}
```

#### 2️⃣ **Lookup (Arama Aşaması)**

Yanlış yazılan kelime geldi:

```python
# Typo: 'doktro' (yanlış - 'o' ve 'r' yer değiştirmiş)
```

**a) Aynı silmeleri yap:**
```
doktro → oktor (d sil)
      → dktor (o sil)
      → dokto (r sil)
      → ... (max_edit_distance kadar)
```

**b) Bu silme rezultatları indekste ara:**
```
"oktor" silmesi → indekste var mı? → "doktor" bulundu!
"dktor" silmesi → indekste var mı? → "doktor" bulundu!
...
```

**c) Adayları topla:**
```
candidates = {"doktor", "motor", ...}
```

#### 3️⃣ **Candidate Evaluation (Aday Değerlendirmesi)**

Bulduğumuz her aday için gerçek mesafeyi hesapla:

```python
for candidate in candidates:
    distance = levenshtein(typo, candidate)
    if distance <= max_edit_distance:
        keep_this_candidate(candidate, distance)
```

**Örneğimiz:**
```
levenshtein('doktro', 'doktor') = 1  ✓ (mesafe 2'den küçük)
levenshtein('doktro', 'motor')  = 3  ✗ (mesafe 2'den büyük)
```

#### 4️⃣ **Ranking (Sıralama)**

En iyi sonucu seç:
```
Kriter:
  1. Mesafe (küçük olanı seç)
  2. Frekans (aynı mesafe → daha sık olanı seç)
  3. Alfabetik sıra (tiebreaker)

Sonuç: "doktor" (mesafe=1, yüksek frekans)
```

---

## 🎓 Basit Örnek Adım Adım

### Senaryo: Sağlık Sözlüğü

```python
sozluk = ["hastane", "doktor", "ilaç", "ateş"]
max_edit_distance = 1
```

### Aşama 1: INDEX OLUŞTURMA

```
Kelime: "hastane" (7 harf)
─────────────────────────────

Silme Kombinasyonları (d=1):
  astane    (h silinir)
  hstane    (a silinir)
  hatane    (s silinir)
  hasane    (t silinir)
  hastne    (a silinir)
  hastae    (n silinir)
  hastan    (e silinir)

Index:
delete_dict["astane"]  → {"hastane"}
delete_dict["hstane"]  → {"hastane"}
delete_dict["hatane"]  → {"hastane"}
...
```

```
Kelime: "doktor"
─────────────────
Silme Kombinasyonları (d=1):
  oktor     (d silinir)
  dktor     (o silinir)
  dotor     (k silinir)
  doktr     (o silinir)
  dokto     (r silinir)

Index:
delete_dict["oktor"]  → {"doktor"}
delete_dict["dokto"]  → {"doktor"}
...
```

### Aşama 2: SORGU (Yanlış yazı geldi)

```
Typo: "dokro" (k ve r yanlış yerleştirilmiş)
      ^^^^^^
```

**Adım 2.1: Typo'dan silmeler:**
```
dokro → dokr  (o silinir)
      → dokr  (o silinir) [tekrar]
      → otkro → otkr (d silinir)
         →  okro (t silinir)
         →  dkro (o silinir)
         → dokro (hiç silme yok)
```

**Adım 2.2: İndekste ara:**
```
Silme "{dokr}":       → Indekste yok ❌
Silme "{otkr}":       → Indekste yok ❌
Silme "{okro}":       → Indekste yok ❌
Silme "{dkro}":       → Indekste yok ❌
Silme "{dokro}":      → Indekste yok ❌

[Hmm, burada isabet yok çünkü "dokro" 1 mesafe uzak]
```

**NOT:** Eğer mesafe 2 olsaydı:
```
d=2: "dokro" → "dkro" (o,o sil) → Mayıs indekste "doktor" olurdu!
```

### Aşama 3: FALLBACK (İsabet yoksa)

SymSpell'in gücü: Eğer silme indeksi isabet vermezse, mesafe hesapla:

```python
for word in sozluk:
    d = levenshtein("dokro", word)
    if d <= max_edit_distance:
        candidates.add(word)

# Sonuç:
levenshtein("dokro", "hastane") = 6 ❌ (çok uzak)
levenshtein("dokro", "doktor")  = 1 ✓ (seç!)
levenshtein("dokro", "ilaç")    = 5 ❌ (çok uzak)
```

**Final:** `"dokro"` → **`"doktor"`** (mesafe 1)

---

## 🏥 Sağlık Veri Kümesi

### Temel Sağlık Terimleri (38)
```
hastane, doktor, hekim, hemşire, ilaç, reçete, muayene, randevu, tedavi,
ameliyat, enfeksiyon, aşı, ateş, öksürük, boğaz, solunum, kalp, damar,
beyin, sinir, cilt, kulak, burun, göz, diş, diyabet, tansiyon, obezite,
kanser, nefroloji, kardiyoloji, nöroloji, ortopedi, psikiyatri, acil,
yoğunbakım, laboratuvar, rapor, tahlil, semptom, teşhis
```

### Birleşik Terimler (20)
```
acilservis, ağrıkesici, kanbasıncı, kalpkrizi, beyincerrahisi,
gözmuayenesi, kulakburunboğaz, aşılama, ilaçtakibi, randevusistemi,
hastakaydı, tahlilsonucu, tedaviplanı, solunumyolu, doktorraporu,
hemşirelik, ameliyatöncesi, ameliyatsonrası, kanşekeri, nabızölçer
```

**Toplam: 82 kelime**

### Typo Türleri (5)

| Tür | Açıklama | Örnek |
|-----|----------|-------|
| **diacritic** | Türkçe → ASCII | hemşire → hemsire |
| **transpose** | İki karakter yer değiş | ameliyat → ameliayt |
| **delete** | Bir karakter sil | enfeksiyon → enfeksion |
| **replace** | Bir karakter değiş | öksürük → öksürak |
| **double** | Bir karakter twice | hastane → hastaane |

---

## 💻 Kullanım Örnekleri

### Python Kodu

```python
from symspellpy import SymSpell, Verbosity

# SymSpell oluştur
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

# Sözlük kelimelerini ekle (frekansla)
sym_spell.create_dictionary_entry("hastane", 20)
sym_spell.create_dictionary_entry("doktor", 20)
sym_spell.create_dictionary_entry("ateş", 10)

# Yanlış kelimeyi sorgula
typo = "hastne"  # (a eksik)
suggestions = sym_spell.lookup(typo, Verbosity.CLOSEST, max_distance=2)

# Sonuç
for suggestion in suggestions:
    print(f"{suggestion.term} (mesafe: {suggestion.distance})")
    # Output: hastane (mesafe: 1)
```

### Notebook'ta Çalıştırma

[symspell_dataset_correction.ipynb](symspell_dataset_correction.ipynb) — 2. hücre:
- Sentetik sağlık veri kümesi
- SymSpellPy ile indexleme
- 28 örnek test
- Doğruluk: **28/28 (100%)**

---

## 📊 Sonuçlar

### Test Örnekleri

```
Synthetic health dictionary size: 82
Evaluation set size: 28
────────────────────────────────────────────────────────────────────────────────
doktor              | typo=doktor           | sug=doktor          | d= 0 | OK
enfeksiyon          | typo=enfeksion        | sug=enfeksiyon      | d= 1 | OK
hemşire             | typo=hemsire          | sug=hemşire         | d= 1 | OK
doktorraporu        | typo=doktorraporu     | sug=doktorraporu    | d= 0 | OK
...
Accuracy: 28/28 ✓
```

### Performans

| Metrik | Değer |
|--------|-------|
| Doğruluk | 100% |
| Sözlük Boyutu | 82 kelime |
| Max Edit Distance | 2 |
| Ortalama Mesafe | 0.8 |
| Build Zamanı | < 50ms |
| Lookup Zamanı (per query) | < 5ms |

---

## 🔍 SymSpell vs Alternatifler

| Algoritma | Mesafe Hesaplama | Hız | Bellek | Doğruluk |
|-----------|-------------------|------|--------|----------|
| **SymSpell** | Delete Index + Lev | ⭐⭐⭐⭐⭐ | Medium | Yüksek |
| Levenshtein | Full Matrix | ⭐⭐ | Low | Yüksek |
| BK-Tree | Hierarchical | ⭐⭐⭐ | High | Yüksek |
| Naive Brute Force | Tüm kelimeleri test | ⭐ | Low | Yüksek |

**SymSpell'in Avantajları:**
1. **Hız:** O(1) indexing + O(k) silme operasyonu
2. **Bellekçi:** Silme kombinasyonlarını saklar, tüm kelimeleri test etmez
3. **Real-time:** Milyonlarca kelime için saniyeler içinde

---

## 🚀 Genişletme Fikirleri

1. **N-gram similarity:** Fonetik benzerlikleri dikkate al
2. **Contexual correction:** Cümle bağlamını kullan
3. **Domain-specific weights:** Sağlıkta sık hataları daha ağır cezalandır
4. **Multi-language:** Türkçe-İngilizce hibrid düzeltme
5. **Spell-as-you-type:** Gerçek zamanlı öneriler

---

## 📚 Referanslar

- SymSpell Paper: https://blog.faroo.com/2012/06/07/improved-edit-distance-based-spelling-correction/
- Levenshtein Distance: https://en.wikipedia.org/wiki/Levenshtein_distance
- SymSpellPy Library: https://github.com/mammothb/symspellpy

---

## 📝 Notlar

- Tüm kod **Türkçe karakter desteği** ile yazılmıştır
- Sentetik veri kümesi tekrarlanabilirlik için **seed=123** kullanır
- Üretim ortamında gerçek sağlık terminolojisi sözlüğü kullanılmalıdır

---

**Geliştirici:** Burak Yılmaz  
**Tarih:** 2026  

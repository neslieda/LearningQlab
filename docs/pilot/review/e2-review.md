# Bağımsız inceleme: E.2 Kuantum fiziği

> Tarih: 2026-10-11. İncelenen dosya: [e2-quantum-physics-pilot-questions.md](../e2-quantum-physics-pilot-questions.md).
> Yöntem: önce cevapları çıkarılmış öğrenci görünümü üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtarla karşılaştırma,
> sonra yazım standardı, müfredat analizi (E.2 satırı) ve biçim profiline göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.
> Kullanılan sabitler: h = 6.63 × 10⁻³⁴ J s, c = 3.00 × 10⁸ m s⁻¹, e = 1.60 × 10⁻¹⁹ C, m<sub>e</sub> = 9.11 × 10⁻³¹ kg.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | A (foton 4.01 eV; E<sub>max</sub> = 1.11 eV) | A | Evet |
| 2 | B (λ ∝ 1/√m → 1/2) | B | Evet |
| 3 | D (Δλ = 4.86 pm; λ′ = 7.86 pm) | D | Evet |
| 4 | C; başka savunulabilir seçenek görmedim | C | Evet |
| 5 (a) | E<sub>k</sub> = 2.40 × 10⁻¹⁷ J; p = 6.61 × 10⁻²⁴ kg m s⁻¹; λ = 1.003 × 10⁻¹⁰ m | 1.00 × 10⁻¹⁰ m | Evet |
| 5 (b) | Halkalar kırınım/girişim desenidir; kırınım dalga özelliğidir | Aynı | Evet |
| 5 (c) | Momentum artar → λ azalır → kırınım açıları küçülür → çaplar azalır | Aynı | Evet |
| 5 (d) | 1.24 × 10⁴ eV (λ = 1.0 × 10⁻¹⁰ m ile) | 1.2 × 10⁴ eV | Evet |
| 6 (a) | eV<sub>s</sub> = hf − Φ → V<sub>s</sub> = (h/e)f − Φ/e; eğim h/e sabit | Aynı | Evet |
| 6 (b) | 0.04 / 0.38 = %10.5 ≈ %11 | %11 (10 ve 10.5 kabul) | Evet |
| 6 (c) | h = 6.66 × 10⁻³⁴; Δ = 0.64 × 10⁻³⁴ → (6.7 ± 0.6) × 10⁻³⁴ J s | (6.7 ± 0.6) × 10⁻³⁴ J s | Evet |
| 6 (d) | Φ/e = eğim × f₀ = 2.11 → 2.1 eV | 2.1 eV | Evet |
| 6 (e) | Sistematik hata: tüm V<sub>s</sub> aynı miktarda büyük, doğru kendine paralel kayar, eğim ve h değişmez | Aynı | Evet |

## Özel olarak istenen denetimler

**Soru 4 (dalga modelinin açıklayamadığı gözlem) — tam olarak bir doğru seçenek var: C.**

- A (akım ∝ şiddet): dalga modelinde de şiddet arttıkça birim zamanda aktarılan enerji ve dolayısıyla koparılan elektron sayısı artar;
  bu gözlem dalga modeliyle çelişmez.
- B (ışıktan elektronlara enerji aktarımı): dalgalar enerji taşır; çelişki yok.
- D (elektronların bir kinetik enerji **aralığı** olması): elektronların metal içinde farklı derinlik ve bağlanma enerjilerinde olması
  her iki modelde de bir aralık verir. Dalga modelinin açıklayamadığı şey aralığın varlığı değil, **en büyük** kinetik enerjinin
  şiddetten bağımsız olup frekansa bağlı olmasıdır; D bunu söylemiyor. Bu yüzden D savunulabilir bir ikinci doğru değildir.
- Yazarın kuşkusu yerinde bir dikkat ama seçenekler şu haliyle tek cevaplı. D'yi yanlışlıkla "E<sub>max</sub> şiddetten bağımsızdır"
  yönünde değiştirmek soruyu iki doğrulu yapar; değiştirilmemeli.

**Soru 6 (Paper 1B) — tablodan en küçük kareler ile yeniden hesap:**

| Büyüklük | Benim hesabım | Dosyadaki değer |
|---|---|---|
| En iyi doğru eğimi | 4.160 × 10⁻¹⁵ V s | 4.16 × 10⁻¹⁵ V s |
| Düşey eksen kesimi | −2.112 V | −2.11 V |
| f-ekseni kesimi | 5.077 × 10¹⁴ Hz | 5.08 × 10¹⁴ Hz |
| En büyük eğim, (6.0; 0.34) → (8.0; 1.25) | 4.55 × 10⁻¹⁵ V s | 4.55 × 10⁻¹⁵ V s |
| En küçük eğim, (6.0; 0.42) → (8.0; 1.17) | 3.75 × 10⁻¹⁵ V s | 3.75 × 10⁻¹⁵ V s |
| h = e × eğim | 6.656 × 10⁻³⁴ J s | 6.66 × 10⁻³⁴ J s |
| Δh = e × (4.55 − 3.75)/2 × 10⁻¹⁵ | 0.64 × 10⁻³⁴ J s | 0.64 × 10⁻³⁴ J s |
| Φ = eğim × f₀ | 2.113 eV | 2.11 eV |

Ek denetim: en büyük ve en küçük eğimli doğrular beş noktanın **hepsinin** belirsizlik çubuğundan geçiyor (en büyük sapma 0.0375 V
< 0.04 V); en iyi doğrunun artıkları en çok 0.012 V. Veri iç tutarlı. Bulunan h kabul edilen değeri (6.63 × 10⁻³⁴) belirsizlik içinde
kapsıyor. Eşik frekansı 5.08 × 10¹⁴ Hz (≈ 590 nm) ve Φ ≈ 2.1 eV, alkali metal katot için gerçekçi (güven: yüksek).

## Bulgular

KRİTİK ya da ORTA bulgu yok.

### 1. DÜŞÜK — Soru 5 (a): "Show that" için istenen anlamlı basamak

- **Yer:** Soru 5 (a) markscheme, Notes ("at least 2 s.f.").
- **Açıklama:** Hedef değer "about 1.0 × 10⁻¹⁰ m" iki anlamlı basamakla verilmiş. "Show that" parçasında öğrencinin verilen değeri
  yeniden yazması değil, bir basamak fazlasını göstermesi beklenir (E.1 Soru 6 (a) ve E.4 Soru 5 (b)'de böyle yapılmış). Answers
  sütununda zaten 1.00 × 10⁻¹⁰ yazıyor; Notes bununla çelişiyor.
- **Öneri:** "Answer must be given to at least 3 s.f. (1.00 × 10⁻¹⁰) for MP3."

### 2. DÜŞÜK — Soru 6 (c)–(d): 1B'de öğrenci eğimi kendisi bulmuyor (yazarın bildirdiği eksik)

- **Yer:** Soru 6, (b) ile (c) arasındaki paragraf; Biçim uyumu tablosu.
- **Açıklama:** Biçim profiline göre 1B'de en uygun doğruyu öğrenci çizer; burada eğimler ve kesim metinde verilmiş. Yazar bunu açıkça
  "uygun değil" diye işaretlemiş; bulguyu doğruluyorum, yeni bir sorun değil. Verilen sayılar tabloyla tutarlı.
- **Öneri:** Grafik şablonu hazır olunca (c) ve (d) yazarın notundaki gibi yeniden yazılsın.

### 3. DÜŞÜK — Soru 5 (d): ara değer ile sonuç

- **Yer:** Soru 5 (d) markscheme ve formül zinciri son satırı.
- **Açıklama:** Formül zinciri λ = 1.003 × 10⁻¹⁰ m ile de λ = 1.0 × 10⁻¹⁰ m ile de "1.24 × 10⁴ eV" yazıyor; ikincisi 12 431 eV,
  ilki 12 399 eV. İkisi de 1.24 × 10⁴'e yuvarlanır, yani yanlış değil; yalnızca parantezdeki tekrar bilgi vermiyor.
- **Öneri:** Parantezi "(λ = 1.0 × 10⁻¹⁰ m ile 1.243 × 10⁴ eV)" yap ya da kaldır.

## Sorun bulunmayan denetimler

- **Müfredat sınırı ve düzey:** hepsi HL etiketli (E.2 yalnızca HL). Compton formülü ve h/m<sub>e</sub>c soruda verilmiş; türetim
  istenmiyor. Türev/integral yok. "Predict" müfredat analizindeki AO3 komut sözcükleri listesinde var.
- **Çeldiriciler:** Soru 1 (2.9; 4.0; 6.9 eV), Soru 2 (1/4; 1; 2), Soru 3 (3.00; 4.86; 5.43 pm) yeniden üretildi; yazılan yanılgılar o
  değerleri veriyor. Soru 5 (a)'daki alternatif v = 7.3 × 10⁶ m s⁻¹ doğru (7.26 × 10⁶).
- **Puanlar:** Soru 5: 3 + 2 + 2 + 2 = 9; Soru 6: 2 + 1 + 3 + 2 + 2 = 10; her satırdaki ✓ sayısı parça puanına eşit; parça puanları 1–3.
- **Biçim:** seçenekler artan sırada ve aynı birimde; olumsuz kökte "cannot" koyu; doğru cevap konumları A, B, D, C; 1B tablo başlığı
  "büyüklük / birim ± belirsizlik" biçiminde.

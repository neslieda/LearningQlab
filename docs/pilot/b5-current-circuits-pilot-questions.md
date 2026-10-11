# Pilot soru seti: B.5 Akım ve devreler

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü B.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; PDF açılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Nikrom özdirenci 1.1 × 10⁻⁶ Ω m alındı ve soruda verildi.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; nitel maddeler (Soru 5c, 5d'nin gerekçesi) kodla
> denetlenemez; nikrom özdirenci ve LDR direnç değerleri genel bilgiden alındı, bir kaynaktan teyit edilmedi; Soru 5'te telin
> direncinin sıcaklıkla değişmediği varsayıldı (soruda yazılı) — gerçek bir ısıtma telinde bu yaklaşık olarak geçerlidir; devre
> şemaları çizilmedi, yalnızca sözle tarif edildi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (B.5) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Özdirenç; direncin uzunluk ve kesit alanına bağlılığı (orantı) | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | İç direnç; dış dirençte harcanan güç | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Değişken direnç (LDR) ile gerilim bölücü | AO3 | — | 1 | Orta |
| 4 | Paper 1A | SL | Seri ve paralel bağlama; paralel kolda akım paylaşımı | AO2 | — | 1 | Orta |
| 5 | Paper 2 | SL | Özdirenç; emk, iç direnç ve uç gerilimi; güç; paralel bağlamanın etkisinin değerlendirilmesi | AO2–AO3 | Show that, Calculate, Explain, Determine | 9 | Orta–zor |

Bu set B.5'in tamamını kapsamaz. Eksik kalanlar: emk kaynağı olarak kimyasal pil ve güneş pilinin karşılaştırılması; devre şeması
çizimi ve sembolleri; akımın yük akış hızı olarak tanımı (I = Δq/Δt); Ohm yasası ve ohmik olmayan davranış (I–V karakteristiği);
termistör ve potansiyometre; ideal olmayan ölçü aleti içeren devre; emk ve iç direncin grafikten belirlenmesi.

Kapsam sınırı kontrolü: yalnızca doğru akım devreleri; tüm ölçü aletleri ideal ve bu soruda yazılı (Soru 3); kullanılan tek değişken
direnç LDR (izinli listede). Türev ya da integral yok.

---

## Soru 1 — Paper 1A

A metal wire X has resistance *R*. Wire Y is made of the same metal and is at the same temperature as X. Y has **twice** the length
and **twice** the diameter of X.

What is the resistance of Y?

A. *R* ⁄ 2
B. *R*
C. 2*R*
D. 4*R*

**Cevap: A**

**Çözüm.** *R* = ρ*L*/*A* ve *A* ∝ *d*². Uzunluk 2 kat, kesit alanı 4 kat: direnç 2 / 4 = 1⁄2 katına iner.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Kesit alanı çapla doğru orantılı alınır (*A* ∝ *d*): 2 / 2 = 1 |
| C | Çapın etkisi yok sayılır; yalnızca uzunluk hesaba katılır: 2*R* |
| D | Direnç hem uzunlukla hem çapla artıyor sayılır: 2 × 2 = 4 |

---

## Soru 2 — Paper 1A

A battery of emf 6.0 V and internal resistance 0.50 Ω is connected to a resistor of resistance 2.5 Ω.

What is the power dissipated in the 2.5 Ω resistor?

A. 2.0 W
B. 10 W
C. 12 W
D. 14 W

**Cevap: B**

**Çözüm.** *I* = ε / (*R* + *r*) = 6.0 / 3.0 = 2.0 A. Dirençte harcanan güç = *I*²*R* = 2.0² × 2.5 = 10 W.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | İç dirençte harcanan güç hesaplanır: 2.0² × 0.50 = 2.0 W |
| C | Bataryanın toplam gücü verilir: ε*I* = 6.0 × 2.0 = 12 W |
| D | İç direnç yok sayılır: ε²/*R* = 36 / 2.5 = 14.4 W |

---

## Soru 3 — Paper 1A

A light-dependent resistor (LDR) and a fixed resistor of resistance 10 kΩ are connected in series with a battery of emf 9.0 V and
negligible internal resistance. An ideal voltmeter is connected across the fixed resistor. In bright light the resistance of the
LDR is 2.0 kΩ.

> **Şekil:** Tek gözlü seri devre: 9.0 V batarya, LDR ve 10 kΩ sabit direnç art arda bağlı. Voltmetre yalnızca 10 kΩ direncin
> uçlarına paralel bağlı.

What is the reading on the voltmeter in bright light?

A. 1.5 V
B. 1.8 V
C. 4.5 V
D. 7.5 V

**Cevap: D**

**Çözüm.** Gerilim bölücü: *V* = 9.0 × 10 / (10 + 2.0) = 7.5 V.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | LDR'nin uçlarındaki gerilim hesaplanır: 9.0 × 2.0 / 12 = 1.5 V |
| B | Gerilim, dirençlerin birbirine oranıyla bulunur (toplama bölünmez): 9.0 × 2.0 / 10 = 1.8 V |
| C | Seri bağlı iki elemanın gerilimi eşit paylaştığı varsayılır: 9.0 / 2 = 4.5 V |

---

## Soru 4 — Paper 1A

A resistor of resistance 6.0 Ω is connected in series with a parallel combination of a 12 Ω resistor and a 4.0 Ω resistor. The
arrangement is connected to a battery of emf 18 V and negligible internal resistance.

> **Şekil:** 18 V bataryanın bir ucundan çıkan iletken önce 6.0 Ω dirençten geçer, sonra iki kola ayrılır: bir kolda 12 Ω, öbür kolda
> 4.0 Ω direnç vardır. Kollar yeniden birleşir ve bataryanın öbür ucuna döner.

What is the current in the 4.0 Ω resistor?

A. 0.50 A
B. 1.0 A
C. 1.5 A
D. 2.0 A

**Cevap: C**

**Çözüm.** Paralel bölüm: (12 × 4.0) / (12 + 4.0) = 3.0 Ω. Toplam direnç 9.0 Ω; ana kol akımı 18 / 9.0 = 2.0 A. Paralel bölümün
gerilimi 2.0 × 3.0 = 6.0 V. 4.0 Ω dirençteki akım = 6.0 / 4.0 = 1.5 A.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Akım dirençle doğru orantılı paylaştırılır (ya da 12 Ω dirençteki akım verilir): 2.0 × 4.0 / 16 = 0.50 A |
| B | Akımın iki kola eşit bölündüğü varsayılır: 2.0 / 2 = 1.0 A |
| D | Ana kol akımı verilir; kollara ayrılma hesaba katılmaz: 2.0 A |

---

## Soru 5 — Paper 2 (9 puan)

A student builds a hot-wire cutter for foam. A nichrome wire of diameter 0.20 mm is connected to a battery of emf 6.0 V and internal
resistance 1.2 Ω. The resistance of the wire is 4.8 Ω and can be assumed to be constant.

Resistivity of nichrome = 1.1 × 10⁻⁶ Ω m

**(a)** Show that the length of the wire is about 0.14 m. [2]

**(b)** Calculate the power dissipated in the wire. [2]

**(c)** Explain why the potential difference across the terminals of the battery is less than 6.0 V when the wire is connected. [2]

To cut faster, the student connects a second, identical nichrome wire in parallel with the first. The student predicts that the
total power dissipated in the two wires will be double the value in (b).

> **Şekil:** Bataryanın (emk 6.0 V, iç direnç 1.2 Ω) uçları arasına, her biri 4.8 Ω olan iki nikrom tel birbirine paralel bağlıdır.

**(d)** Determine whether the prediction of the student is correct. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *A* = π × (0.10 × 10⁻³)² «= 3.14 × 10⁻⁸ m²» ✓<br>*L* = *RA*/ρ = 4.8 × 3.14 × 10⁻⁸ / 1.1 × 10⁻⁶ = 0.137 «m» ✓ | *Answer 0.14 m is given; award the second mark only if 0.137 or the complete substitution is seen.*<br>*Award [1 max] if the diameter is used as the radius (0.55 m).* | 2 |
| 5. | b | | *I* = 6.0 / (4.8 + 1.2) «= 1.0 A» ✓<br>*P* = 1.0² × 4.8 = 4.8 «W» ✓ | *Award [1 max] for 7.5 W (internal resistance ignored).* | 2 |
| 5. | c | | there is a current in the battery so there is a potential difference across / energy is dissipated in the internal resistance ✓<br>terminal pd = emf − *Ir* «= 6.0 − 1.0 × 1.2 = 4.8 V» **OR** less energy per unit charge is available to the external circuit ✓ | *OWTTE* | 2 |
| 5. | d | | resistance of the parallel wires = 2.4 «Ω» **AND** *I* = 6.0 / (2.4 + 1.2) «= 1.67 A» ✓<br>total power in the wires = 1.67² × 2.4 = 6.7 «W» ✓<br>this is less than 2 × 4.8 = 9.6 «W», so the prediction is not correct «because the larger current increases the pd across the internal resistance / the terminal pd falls to 4.0 V / the power in each wire falls to 3.3 W» ✓ | *Allow ECF from (b).*<br>**ALTERNATIVE for the second mark:** terminal pd = 4.0 V, power in each wire = 4.0² / 4.8 = 3.3 «W» ✓<br>*The third mark requires a numerical comparison and a conclusion.* | 3 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `d = 0.20e-3 m`, `R = 4.8 ohm`, `emf = 6.0 V`, `r = 1.2 ohm`; sabit `rho = 1.1e-6 ohm m` | |
| `A` | `pi*(d/2)**2` | 3.14 × 10⁻⁸ m² |
| `L` | `R*A/rho` | 0.137 m |
| `I1` | `emf/(R + r)` | 1.00 A |
| `P1` | `I1**2*R` | 4.80 W |
| `V_term1` | `emf - I1*r` | 4.80 V |
| `R_par` | `R/2` | 2.40 Ω |
| `I2` | `emf/(R_par + r)` | 1.67 A |
| `P2` | `I2**2*R_par` | 6.67 W |
| `V_term2` | `emf - I2*r` | 4.00 V |
| Karşılaştırma | `P2 < 2*P1` | 6.67 W < 9.60 W → öngörü yanlış |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + (şekil) + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–4 uygun (artan) |
| 1A: olumsuzluk / kritik sözcük koyu | Soru 1 ("twice") uygun; olumsuz kök yok |
| 1A: doğru cevap konumu dengeli | A, B, D, C |
| 1A: şekil olmadan çözülebilir | Soru 3 ve 4'te devre, soru metninde tam olarak sözle tanımlı; `> **Şekil:**` tarifi yalnızca yardımcı. Devre şemaları çizilmedi |
| 1A: yuvarlak, temiz sayılar | Soru 1–4 uygun; Soru 2'de D çeldiricisi 14.4 → 14 W yuvarlandı |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 2, 3; toplam 9) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | Soru 5 uygun: (a) Show that, (c) Explain, (d) Determine |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE, ALTERNATIVE | Soru 5 uygun |
| Değer–birim yazımı (Ω m), 2 anlamlı basamak | Uygun |
| Ölçü aletleri ideal, aksi belirtilmedikçe | Soru 3'te "ideal voltmeter" açıkça yazılı |
| Paper 2: cevap kutusu, noktalı satırlar | Bu taslakta yok; yayın şablonunda eklenecek |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından bağımsız bir kör çözücü tarafından cevaplar görülmeden çözüldü (devreler yalnızca sözlü
tariften); tüm cevap anahtarları ve markscheme sonuçları bağımsız olarak yeniden üretildi (KRİTİK ve ORTA bulgu yok). Ayrıntı:
[review/b5-review.md](review/b5-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

İnceleme sonucu yapılan değişiklikler (sayısal değer değişmedi; anahtarlar aynı):

- **Soru 2, DÜŞÜK-1:** "A cell of emf 6.0 V" → "A battery of emf 6.0 V" (tek bir kimyasal pil için 6.0 V alışılmadık). Cevap B
  (10 W) ve çeldiriciler değişmedi.
- **Soru 5 (d), DÜŞÜK-2:** markscheme'in üçüncü maddesine kabul edilen gerekçe olarak "the power in each wire falls to 3.3 W"
  eklendi (4.0² / 4.8 = 3.33 W).
- **DÜŞÜK-3 (SL kısa soruda 9 puan) ve DÜŞÜK-4 (devre şemalarının çizilmemesi):** değişiklik yapılmadı; ilki uzman teyidi bekleyen
  kayıt, ikincisi şekil üretimi gelene kadar çözülemez ve "Biçim uyumu"nda zaten işaretli.

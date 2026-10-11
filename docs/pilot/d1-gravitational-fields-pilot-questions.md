# Pilot soru seti: D.1 Kütle çekim alanları

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü D.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; senaryolar yazarın kurgusudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Kullanılan sabit: G = 6.67 × 10⁻¹¹ N m² kg⁻² (veri kitapçığı değeri uzmanca teyit
> edilmeli).
> **Bağımsız kontrol:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. dosya sonu).
> **Doğrulanmayan:** (1) uzman incelemesi yapılmadı; (2) gök cismi verileri (Mars, Ay, Titan kütle ve
> yarıçapları) yazarın genel bilgisinden 2–3 anlamlı basamakla alındı, bir kaynaktan teyit edilmedi; (3) Titan'ın 1500 km yükseklikte
> ölçülebilir sürükleme yaratacak kadar atmosferi olduğu varsayımı teyit edilmedi (soru yalnızca nitel sonuç ister); (4) "yörünge hızı
> formülü" ek HL sayıldığı için Soru 5 bütünüyle HL etiketlendi — (a) ve (b) parçalarının SL'de sorulup sorulamayacağı uzmanca
> teyit edilmeli; (5) bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (D.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Alan şiddetinin merkezden uzaklıkla ters kare değişimi; yükseklik–uzaklık ayrımı | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | Kepler'in üçüncü yasası (çembersel yörünge) | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | İki cismi birleştiren doğru üzerinde bileşke alan şiddeti | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Kütle çekim potansiyeli (sonsuzda sıfır); W = mΔV | AO2 | — | 1 | Orta–zor |
| 5 | Paper 2 | HL | Yörünge hızı; periyot; yörünge enerjisi ve kaçış; atmosfer sürüklemesinin nitel etkisi | AO2–AO3 | Show that, Calculate, Determine, Explain | 9 | Orta–zor |

Bu set D.1'in tamamını kapsamaz. Eksik kalanlar: Kepler'in birinci ve ikinci yasaları, nokta kütle yaklaşımının koşulu, alan çizgileri,
alan şiddeti = potansiyel gradyanı, eşpotansiyel yüzeyler, kaçış hızı formülünün doğrudan kullanımı.

Kapsam sınırı kontrolü: tüm yörüngeler çembersel; bileşke alan yalnızca iki cismi birleştiren doğru üzerinde (Soru 3); potansiyel
sonsuzda sıfır (Soru 4, 5); türev ya da integral yok; sürükleme yalnızca nitel (Soru 5d).

---

## Soru 1 — Paper 1A

The gravitational field strength at the surface of Mars is 3.7 N kg⁻¹. The radius of Mars is 3.4 × 10⁶ m. A probe is at a height of
6.8 × 10⁶ m **above the surface** of Mars.

What is the gravitational field strength due to Mars at the position of the probe?

A. 0.41 N kg⁻¹
B. 0.93 N kg⁻¹
C. 1.2 N kg⁻¹
D. 1.9 N kg⁻¹

**Cevap: A**

**Çözüm.** Merkezden uzaklık r = R + h = 3.4 × 10⁶ + 6.8 × 10⁶ = 1.02 × 10⁷ m = 3R. Alan şiddeti 1/r² ile değişir:
g = 3.7 / 3² = 0.41 N kg⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Yükseklik merkezden uzaklık sanılır (r = 2R): 3.7 / 2² = 0.93 N kg⁻¹ |
| C | Doğru uzaklık (3R) alınır ama alan 1/r ile değişir sanılır: 3.7 / 3 = 1.2 N kg⁻¹ |
| D | Hem yükseklik uzaklık sanılır hem 1/r kullanılır: 3.7 / 2 = 1.9 N kg⁻¹ |

---

## Soru 2 — Paper 1A

Two small moons X and Y move in circular orbits around the same planet. The orbital radius of X is *r* and its orbital period is
4.0 days. The orbital radius of Y is 4*r*.

What is the orbital period of Y?

A. 8.0 days
B. 10 days
C. 16 days
D. 32 days

**Cevap: D**

**Çözüm.** Kepler'in üçüncü yasası: T² ∝ r³, yani T ∝ r^(3/2). T<sub>Y</sub> = 4.0 × 4^(3/2) = 4.0 × 8 = 32 gün.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | T ∝ √r alınır: 4.0 × 4^(1/2) = 8.0 gün |
| B | Üsler ters çevrilir (T³ ∝ r²): 4.0 × 4^(2/3) = 10.1 ≈ 10 gün |
| C | T ∝ r alınır: 4.0 × 4 = 16 gün |

---

## Soru 3 — Paper 1A

Two stars P and Q form a binary system. The mass of P is 2.0 × 10³⁰ kg and the mass of Q is 6.0 × 10³⁰ kg. The distance between the
centres of the stars is 4.0 × 10¹¹ m. Point Z is on the line joining the centres, midway between the stars.

G = 6.67 × 10⁻¹¹ N m² kg⁻²

What is the magnitude of the resultant gravitational field strength at Z?

A. 1.7 × 10⁻³ N kg⁻¹
B. 3.3 × 10⁻³ N kg⁻¹
C. 6.7 × 10⁻³ N kg⁻¹
D. 1.3 × 10⁻² N kg⁻¹

**Cevap: C**

**Çözüm.** Z'nin her iki yıldıza uzaklığı 2.0 × 10¹¹ m. Alanlar zıt yönlüdür (her biri kendi yıldızına doğru), bu yüzden büyüklükler
çıkarılır: g = G(M<sub>Q</sub> − M<sub>P</sub>) / r² = 6.67 × 10⁻¹¹ × 4.0 × 10³⁰ / (2.0 × 10¹¹)² = 6.7 × 10⁻³ N kg⁻¹, Q'ya doğru.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Alanlar çıkarılır ama uzaklık olarak yıldızlar arası uzaklığın tamamı alınır: 6.67 × 10⁻¹¹ × 4.0 × 10³⁰ / (4.0 × 10¹¹)² = 1.7 × 10⁻³ |
| B | Alanlar toplanır ve uzaklık olarak tamamı alınır: 6.67 × 10⁻¹¹ × 8.0 × 10³⁰ / (4.0 × 10¹¹)² = 3.3 × 10⁻³ |
| D | Uzaklık doğru, ama alanların zıt yönlü olduğu görülmez ve büyüklükler toplanır: 6.67 × 10⁻¹¹ × 8.0 × 10³⁰ / (2.0 × 10¹¹)² = 1.3 × 10⁻² |

---

## Soru 4 — Paper 1A (HL)

The gravitational potential at the surface of the Moon is −2.8 MJ kg⁻¹. The radius of the Moon is *R*. A probe of mass 160 kg is
moved from rest on the surface of the Moon to rest at a point that is a distance 4*R* from the **centre** of the Moon.

What is the minimum energy required to move the probe?

A. 1.1 × 10⁸ J
B. 3.4 × 10⁸ J
C. 4.2 × 10⁸ J
D. 4.5 × 10⁸ J

**Cevap: B**

**Çözüm.** Potansiyel 1/r ile değişir: 4R'de V = −2.8 / 4 = −0.70 MJ kg⁻¹. ΔV = −0.70 − (−2.8) = +2.1 MJ kg⁻¹.
W = mΔV = 160 × 2.1 × 10⁶ = 3.36 × 10⁸ ≈ 3.4 × 10⁸ J.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Potansiyel farkı yerine son noktadaki potansiyelin büyüklüğü kullanılır: 160 × 0.70 × 10⁶ = 1.12 × 10⁸ ≈ 1.1 × 10⁸ J |
| C | Potansiyel 1/r² ile değişir sanılır: V = −2.8 / 16 = −0.175; 160 × 2.625 × 10⁶ = 4.2 × 10⁸ J |
| D | Yüzeydeki potansiyelin tamamı alınır (sonsuza götürme enerjisi): 160 × 2.8 × 10⁶ = 4.48 × 10⁸ ≈ 4.5 × 10⁸ J |

---

## Soru 5 — Paper 2 (HL, 9 puan)

Titan is a moon of Saturn. An orbiter of mass 900 kg moves in a circular orbit at a height of 1.50 × 10⁶ m above the surface of Titan.

mass of Titan = 1.35 × 10²³ kg
radius of Titan = 2.57 × 10⁶ m
G = 6.67 × 10⁻¹¹ N m² kg⁻²

**(a)** Show that the orbital speed of the orbiter is about 1.5 km s⁻¹. [2]

**(b)** Calculate the orbital period of the orbiter. [2]

**(c)** Determine the minimum additional energy that must be supplied to the orbiter for it to escape from the gravitational field
of Titan. Ignore the gravitational effect of Saturn. [2]

The outer atmosphere of Titan exerts a small drag force on the orbiter. The orbit remains approximately circular.

**(d)** Explain, without calculation, the effect of the drag force on the speed of the orbiter. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *GMm*/*r*² = *mv*²/*r* **OR** *v* = √(*GM*/*r*), with *r* = 2.57 × 10⁶ + 1.50 × 10⁶ «= 4.07 × 10⁶ m» ✓<br>*v* = √(6.67 × 10⁻¹¹ × 1.35 × 10²³ / 4.07 × 10⁶) = 1.49 × 10³ «m s⁻¹» ✓ | *Answer must be given to at least 3 s.f. or the full substitution shown.*<br>*Award [1] max if the correct relation is used with r = 1.50 × 10⁶ m or r = 2.57 × 10⁶ m «the given value is then not reached».* | 2 |
| 5. | b | | *T* = 2π*r*/*v* = 2π × 4.07 × 10⁶ / 1.49 × 10³ ✓<br>*T* = 1.7 × 10⁴ «s» ✓ | *Allow use of v = 1.5 × 10³ m s⁻¹.*<br>*Allow 4.8 «h».* | 2 |
| 5. | c | | total energy = ½*mv*² − *GMm*/*r* = −*GMm*/2*r* **OR** = −½*mv*² ✓<br>«total energy must be raised to zero, so» energy = 1.0 × 10⁹ «J» ✓ | *Allow ECF from (a).*<br>*Award [1] max for* 2.0 × 10⁹ J *«kinetic energy ignored».* | 2 |
| 5. | d | | total energy of the orbiter decreases «work is done against drag / energy is transferred to thermal energy» ✓<br>orbital radius decreases «as *E* = −*GMm*/2*r* becomes more negative» ✓<br>speed increases as *v* = √(*GM*/*r*) / *v* ∝ 1/√*r* ✓ | *OWTTE*<br>*Do not award MP3 for "speed decreases because drag opposes motion".* | 3 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `M = 1.35e23 kg`, `R = 2.57e6 m`, `h = 1.50e6 m`, `m = 900 kg`, sabit `G = 6.67e-11` | |
| `r` | `R + h` | 4.07 × 10⁶ m |
| `v` | `sqrt(G*M/r)` | 1487 m s⁻¹ |
| `T` | `2*pi*r/v` | 1.72 × 10⁴ s (v = 1.5 × 10³ ile 1.70 × 10⁴ s) |
| `E_total` | `-G*M*m/(2*r)` | −9.96 × 10⁸ J |
| `E_escape` | `-E_total` | 9.96 × 10⁸ J ≈ 1.0 × 10⁹ J (v = 1.5 × 10³ ile 1.01 × 10⁹ J) |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–4 uygun (artan) |
| 1A: kritik sözcük koyu | Soru 1 ("above the surface"), Soru 4 ("centre") |
| 1A: doğru cevap konumu dengeli | A, D, C, B |
| 1A: seçenekler yuvarlamadan sonra birbirinden farklı | Kontrol edildi (python) |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 2, 3; toplam 9) |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanabilir | Soru 5(a) → (b), (c) uygun |
| Paper 2: en az bir AO3 parça | Soru 5(a) Show that, (c) Determine, (d) Explain |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE | Soru 5 uygun |
| Şekil | Bu dosyadaki hiçbir soru şekil gerektirmez |
| Sabitlerin verilmesi | G, gereken sorularda (3, 5) soru metninde verildi |
| Değer–birim yazımı (N kg⁻¹, m s⁻¹), 2–3 anlamlı basamak | Uygun |
| Paper 1B | Bu dosyada yok; D teması için 1B sorusu [D.3 dosyasında](d3-motion-in-em-fields-pilot-questions.md) |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından farklı bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları ve
çeldirici değerleri bağımsız olarak yeniden üretildi ve eşleşti. KRİTİK ya da ORTA bulgu yok. Ayrıntı:
[review/d1-review.md](review/d1-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

İncelemeye yanıt olarak yapılan değişiklikler:

- **Soru 4:** sonda kütlesi 150 kg → 160 kg. Doğru sonuç 3.15 × 10⁸ J iki anlamlı basamakta yuvarlama sınırındaydı; yeni değer
  3.36 × 10⁸ ≈ 3.4 × 10⁸ J. Seçenekler 1.1 / 3.2 / 3.9 / 4.2 → 1.1 / 3.4 / 4.2 / 4.5 (× 10⁸ J); doğru cevap yine B. Tüm seçenekler
  `python3` ile yeniden hesaplandı.
- **Soru 5(a) markscheme:** yanlış *r* için "scores zero" notu yumuşatıldı: doğru ilişki yanlış *r* ile kullanılırsa en çok 1 puan.
- **Değiştirilmeyen:** Soru 5'in bütünüyle HL etiketi (inceleyen de güvenli tarafta buldu); uzman teyidi bekliyor.

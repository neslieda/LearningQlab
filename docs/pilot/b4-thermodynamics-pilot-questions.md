# Pilot soru seti: B.4 Termodinamik

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
> **B.4 yalnızca HL düğümüdür; bu dosyadaki hiçbir soru SL havuzuna girmez.**
>
> **Kaynak:** yalnızca müfredat düğümü B.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; PDF açılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Soru 6'da soruda verilen 460 J değeri, izotermal sıkıştırma için
> *nRT* ln(*V*<sub>A</sub>/*V*<sub>C</sub>) = −458 J hesabının iki anlamlı basamağa yuvarlanmış halidir (bu hesap öğrenciden istenmez).
> İşaret kuralı her yerde Clausius: *Q* sisteme verilen enerji, *W* sistemin yaptığı iş, *Q* = Δ*U* + *W*.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; nitel maddeler (Soru 6d'nin yorumu) kodla denetlenemez;
> Soru 3'teki sayma modelinin rehberin "basit sayma modeli" ile kastettiği düzeyde olduğu uzmanca teyit edilmedi; Soru 6(d)'de
> çevrimin en yüksek ve en düşük sıcaklıkları arasında Carnot sınırıyla karşılaştırmanın rehberin beklediği ifade biçimi olduğu teyit
> edilmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (B.4) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Birinci yasa ve işaret kuralı (Q = ΔU + W) | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | HL | Adyabatik süreç, PV^(5/3) = sabit | AO2 | — | 1 | Orta |
| 3 | Paper 1A | HL | Entropi ve mikrodurum sayısı, S = k ln Ω (basit sayma modeli) | AO3 | — | 1 | Orta–zor |
| 4 | Paper 1A | HL | Isı makinesinin verimi; Carnot veriminden ayrımı | AO2 | — | 1 | Kolay |
| 5 | Paper 1A | HL | İzotermal süreçte birinci yasa ve ΔS = ΔQ/T | AO3 | — | 1 | Orta |
| 6 | Paper 2 | HL | İzobarik, adyabatik ve izotermal adımlı çevrim; W = PΔV; birinci yasa; verim; Carnot sınırı ve ikinci yasa | AO2–AO3 | Show that, Determine, Discuss | 9 | Orta–zor |

Bu set B.4'ün tamamını kapsamaz. Eksik kalanlar: izokorik süreç; P–V diyagramında çevrimin çizimi ve kapalı alanın iş olarak yorumu;
ikinci yasanın Clausius ve Kelvin biçimlerinin ifadesi; tersinmezlik ve yalıtılmış sistemde entropi artışı; çevrenin entropi
değişimi; adyabatik süreçte sıcaklık–hacim ilişkisinin sayısal kullanımı.

Kapsam sınırı kontrolü: tüm nicel sorular tek atomlu ideal gaz içindir ve bu, soru metninde yazılıdır; işaret kuralı Clausius;
mikrodurumlar yalnızca dört parçacıklı iki bölmeli sayma modeliyle (Soru 3); izotermal işin logaritmalı formülü öğrenciden istenmez
(Soru 5 ve 6'da enerji değerleri verilir). Türev ya da integral yok.

---

## Soru 1 — Paper 1A

Thermal energy of 500 J is supplied to a monatomic ideal gas. At the same time, the gas is compressed and 200 J of work is done
**on** the gas.

What is the change in the internal energy of the gas?

A. −700 J
B. −300 J
C. +300 J
D. +700 J

**Cevap: D**

**Çözüm.** Clausius işaret kuralı: *Q* = +500 J (sisteme verilen), *W* = −200 J (iş gazın üzerine yapıldı, gazın yaptığı iş negatif).
Δ*U* = *Q* − *W* = 500 − (−200) = +700 J.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Büyüklük doğru, işaret ters: iki enerji girişi de iç enerjiyi azaltıyor sayılır: −700 J |
| B | Hem *W*'nin işareti yanlış alınır hem sonuç ters çevrilir (Δ*U* = *W* − *Q* = 200 − 500): −300 J |
| C | Gazın üzerine yapılan iş, gazın yaptığı iş gibi alınır (*W* = +200 J): 500 − 200 = +300 J |

---

## Soru 2 — Paper 1A

A monatomic ideal gas at pressure *P* is compressed adiabatically to **one eighth** of its initial volume.

What is the final pressure of the gas?

A. 512*P*
B. 32*P*
C. 8*P*
D. 4*P*

**Cevap: B**

**Çözüm.** *PV*<sup>5/3</sup> = sabit → *P*₂ = *P* × (*V*₁/*V*₂)<sup>5/3</sup> = *P* × 8<sup>5/3</sup> = *P* × 2⁵ = 32*P*.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Üs 5⁄3 yerine 3 alınır: 8³ = 512 |
| C | Süreç izotermal sayılır (*PV* = sabit): 8*P* |
| D | Sıcaklık oranı basınç oranı sanılır (*TV*<sup>2/3</sup> = sabit): 8<sup>2/3</sup> = 4 |

---

## Soru 3 — Paper 1A

Four distinguishable particles are in a box. Each particle can be in the left half or in the right half of the box. A microstate
is specified by stating which half each particle is in. A macrostate is specified by stating only the number of particles in each
half. The entropy of a macrostate is *S* = *k* ln Ω, where Ω is the number of microstates of that macrostate and *k* is the
Boltzmann constant.

What is the entropy of the macrostate with two particles in each half **minus** the entropy of the macrostate with all four
particles in the left half?

A. *k* ln 2
B. *k* ln 4
C. *k* ln 6
D. *k* ln 16

**Cevap: C**

**Çözüm.** Başlangıç makrodurumu (4 solda) tek mikroduruma sahiptir: Ω₁ = 1, *S*₁ = *k* ln 1 = 0. Son makrodurum (2 solda, 2 sağda)
için soldaki iki parçacığı seçmenin yolu sayısı Ω₂ = 4! / (2! 2!) = 6. Δ*S* = *k* ln 6 − *k* ln 1 = *k* ln 6.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Mikrodurum sayısı olarak bölme sayısı (2) alınır |
| B | Mikrodurum sayısı olarak parçacık sayısı (4) alınır |
| D | Son makrodurumun değil, tüm olası mikrodurumların sayısı alınır: 2⁴ = 16 (serbest genleşme okuması, 4*k* ln 2; soru metni makrodurumu açıkça tanımladığı için bu okuma dışlanır) |

---

## Soru 4 — Paper 1A

In each cycle, a heat engine absorbs 800 J of thermal energy from a hot reservoir at 500 K and transfers 600 J of thermal energy to
a cold reservoir at 300 K.

What is the efficiency of the heat engine?

A. 0.25
B. 0.33
C. 0.40
D. 0.75

**Cevap: A**

**Çözüm.** Çevrim başına yapılan iş = 800 − 600 = 200 J. Verim = yararlı iş / alınan enerji = 200 / 800 = 0.25.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | İş, alınan enerji yerine atılan enerjiye oranlanır: 200 / 600 = 0.33 |
| C | Gerçek verim yerine Carnot verimi hesaplanır: 1 − 300 / 500 = 0.40 |
| D | Atılan enerjinin alınana oranı verim sanılır: 600 / 800 = 0.75 |

---

## Soru 5 — Paper 1A

A monatomic ideal gas expands slowly (reversibly) and isothermally at a temperature of 300 K. The gas does 600 J of work during
the expansion.

What is the change in the entropy of the gas?

A. −2.0 J K⁻¹
B. 0
C. +0.50 J K⁻¹
D. +2.0 J K⁻¹

**Cevap: D**

**Çözüm.** İzotermal süreçte ideal gazın iç enerjisi değişmez: Δ*U* = 0, bu yüzden *Q* = *W* = +600 J (gaza verilen).
Δ*S* = Δ*Q* / *T* = 600 / 300 = +2.0 J K⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Gaz iş yaptığı için enerji kaybettiği düşünülür; *Q* negatif alınır: −600 / 300 = −2.0 |
| B | "Sıcaklık değişmiyor, öyleyse enerji alışverişi ve entropi değişimi yok" düşüncesi (izotermal ile adyabatik karıştırılır) |
| C | Oran ters kurulur: 300 / 600 = 0.50 |

---

## Soru 6 — Paper 2 (9 puan)

A fixed mass of a monatomic ideal gas is taken through a cycle A → B → C → A.

- In state A the pressure is 1.0 × 10⁵ Pa, the volume is 2.0 × 10⁻³ m³ and the temperature is 300 K.
- A → B is an isobaric expansion to a volume of 5.0 × 10⁻³ m³. The temperature at B is 750 K.
- B → C is an adiabatic expansion. The temperature at C is 300 K.
- C → A is an isothermal compression.

> **Şekil:** Basınç–hacim (*P*–*V*) diyagramı; ölçekli değil. A'dan B'ye sağa doğru yatay doğru (sabit basınç). B'den C'ye sağa ve
> aşağı inen dik eğri (adyabatik). C'den A'ya sola ve yukarı çıkan, daha az dik eğri (izotermal). Çevrim saat yönünde dolaşılır.

**(a)** Show that the thermal energy supplied to the gas during A → B is 750 J. [3]

**(b)** Determine the work done by the gas during B → C. [2]

During C → A, 460 J of thermal energy is transferred from the gas to the surroundings.

**(c)** Determine the efficiency of the cycle. [2]

**(d)** Discuss whether your answer to (c) is consistent with the second law of thermodynamics. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *W* = *P*Δ*V* = 1.0 × 10⁵ × 3.0 × 10⁻³ «= 300 J» ✓<br>Δ*U* = 3⁄2 *P*Δ*V* **OR** 3⁄2 *nR*Δ*T* «with *nR* = 0.667 J K⁻¹» = 450 «J» ✓<br>*Q* = Δ*U* + *W* = 450 + 300 «= 750 J» ✓ | *The third mark is for the explicit use of the first law.*<br>*n = 0.080 mol if calculated.* | 3 |
| 6. | b | | *Q* = 0 so *W* = −Δ*U* ✓<br>Δ*U* = −450 «J» «same temperature change as A → B, reversed» so *W* = «+» 450 «J» ✓ | *Accept* Δ*U* = 3⁄2 *nR* (300 − 750) *for the second mark.*<br>*Allow ECF from (a).* | 2 |
| 6. | c | | net work = 750 − 460 **OR** 300 + 450 − 460 «= 290 J» ✓<br>efficiency = 290 / 750 = 0.39 ✓ | *Allow ECF from (b).*<br>*Thermal energy is supplied only during A → B.* | 2 |
| 6. | d | | Carnot efficiency «between 750 K and 300 K» = 1 − 300 / 750 = 0.60 ✓<br>0.39 is less than 0.60, so the cycle is consistent with / does not violate the second law ✓ | *Allow ECF from (c).*<br>*Accept an argument that some thermal energy is rejected to the surroundings, so not all the energy supplied is converted to work «Kelvin form», for the second mark only.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `P_A = 1.0e5 Pa`, `V_A = 2.0e-3 m^3`, `V_B = 5.0e-3 m^3`, `T_A = 300 K`, `Q_CA = -460 J` | |
| `T_B` | `T_A*V_B/V_A` | 750 K (soruda verilen değerle tutarlı) |
| `W_AB` | `P_A*(V_B - V_A)` | 300 J |
| `dU_AB` | `1.5*P_A*(V_B - V_A)` | 450 J |
| `Q_AB` | `dU_AB + W_AB` | 750 J |
| `W_BC` | `-dU_BC = dU_AB` | 450 J |
| `W_net` | `Q_AB + Q_CA` | 290 J |
| `eta` | `W_net/Q_AB` | 0.387 |
| `eta_Carnot` | `1 - T_A/T_B` | 0.60 |
| Tutarlılık kontrolü (öğrenciden istenmez) | `V_C = V_B*(T_B/T_A)**1.5`; `Q_CA = nR*T_A*ln(V_A/V_C)` | *V*<sub>C</sub> = 1.98 × 10⁻² m³; *Q*<sub>CA</sub> = −458 J; verim 0.389 |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–5 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1, 3, 4, 5 artan; Soru 2 azalan |
| 1A: olumsuzluk / kritik sözcük koyu | Soru 1 ("on"), Soru 2 ("one eighth") ve Soru 3 ("minus") uygun; olumsuz kök yok |
| 1A: doğru cevap konumu dengeli | D, B, C, A, D |
| 1A: şekil olmadan çözülebilir | Soru 1–5 şekil gerektirmiyor |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 6 uygun (3, 2, 2, 2; toplam 9) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | Soru 6 uygun: (a) Show that; (b), (c) Determine; (d) Discuss |
| Paper 2: şekil | Soru 6'da *P*–*V* diyagramı `> **Şekil:**` ile tarif edildi; tüm veriler metinde, soru şekil olmadan çözülebilir. Çizim üretilmedi |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF | Soru 6 uygun |
| Değer–birim yazımı (J K⁻¹), 2 anlamlı basamak | Uygun |
| Düzey etiketi | Tüm sorular HL; SL kâğıdında kullanılamaz |
| Paper 2: cevap kutusu, noktalı satırlar | Bu taslakta yok; yayın şablonunda eklenecek |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından bağımsız bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları ve
markscheme sonuçları (Soru 6 çevriminin adım adım enerji dengesi dahil) bağımsız olarak yeniden üretildi (KRİTİK bulgu yok).
Ayrıntı: [review/b4-review.md](review/b4-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

İnceleme sonucu yapılan değişiklikler (sayısal değer değişmedi; anahtarlar aynı):

- **Soru 3, ORTA-1:** soru metni yeniden yazıldı. Makrodurum artık açıkça tanımlı ("only the number of particles in each half"),
  *S* = *k* ln Ω tanımı kökte veriliyor ve soru cümlesi iki belirli makrodurumun entropi farkını istiyor. Böylece serbest genleşme
  okuması (*k* ln 16) dışlanıyor. Cevap C (*k* ln 6) ve seçenekler değişmedi. Kök yaklaşık 85 kelime; profildeki en uzun kök
  sınırına (≈ 90) yakın.
- **Soru 5, DÜŞÜK-1:** "expands isothermally" → "expands slowly (reversibly) and isothermally"; Δ*S* = Δ*Q*/*T* kullanımının koşulu
  artık yazılı. Cevap D (+2.0 J K⁻¹) değişmedi.
- **DÜŞÜK-2 (460 J ↔ 458 J), DÜŞÜK-3 (Carnot karşılaştırmasının ifade biçimi), DÜŞÜK-4 (şeklin yalnızca sözle tarifi):** değişiklik
  yapılmadı; inceleme bunları sorun olarak değil kayıt olarak yazmış, somut düzeltme önermiyor.

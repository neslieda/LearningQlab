# Pilot soru seti: B.3 Gaz yasaları

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
> B teması için istenen tek Paper 1B (veri temelli) sorusu bu dosyadadır (Soru 6).
>
> **Kaynak:** yalnızca müfredat düğümü B.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; PDF açılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Soru 6'daki en uygun doğru (en küçük kareler) ve tüm belirsizlik çubuklarından
> geçen en dik / en yatık doğrular da tablodaki veriden kodla hesaplandı. Sabitler: R = 8.31 J K⁻¹ mol⁻¹, k<sub>B</sub> = 1.38 × 10⁻²³ J K⁻¹,
> N<sub>A</sub> = 6.02 × 10²³ mol⁻¹; gereken soruda verildi; veri kitapçığı değerleri uzmanca teyit edilmeli.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; nitel maddeler (Soru 3, 5c, 5e, 6a–c, 6g) kodla
> denetlenemez; Soru 6'nın verisi kurgusaldır (ideal gaz davranışına ölçüm saçılması eklenerek yazıldı), gerçek bir deneyden alınmadı;
> "root mean square speed" teriminin rehberin P = ⅓ρv² için kullandığı terimle aynı olduğu teyit edilmedi (Soru 4); bilinen bir sınav
> sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (B.3) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | PV = NkT ile molekül sayısı; kelvin sıcaklığı | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | Tek atomlu ideal gazın iç enerjisi (U = 3⁄2 PV) | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | İdeal gaz yaklaşımının geçerlilik koşulları | AO1 | — | 1 | Kolay |
| 4 | Paper 1A | SL | P = ⅓ρv² ile orantı akıl yürütmesi | AO3 | — | 1 | Orta |
| 5 | Paper 2 | SL | İdeal gaz yasası, sabit hacim; kinetik kuramla basınç; iç enerji değişimi; modelin sınırı | AO2–AO3 | Show that, Calculate, Explain, Suggest | 9 | Orta |
| 6 | Paper 1B | SL | Sabit hacimde basınç–sıcaklık verisi; doğrusal ile doğru orantılı ayrımı; dış değerleme; belirsizlik | AO2–AO3 | State, Outline, Discuss, Determine, Comment, Suggest | 11 | Orta–zor |

Bu set B.3'ün tamamını kapsamaz. Eksik kalanlar: basıncın tanımı (P = F/A) ile hesap; mol–kütle–molar kütle dönüşümleri; sabit
sıcaklık (PV = sabit) ve sabit basınç (V/T = sabit) süreçleri; P–V diyagramının çizimi ve yorumu; ideal gaz modelinin varsayımlarının
sayılması; P = ⅓ρv² ile doğrudan sayısal hesap.

Kapsam sınırı kontrolü: süreçler yalnızca sabit hacim (Soru 5, 6) ve ideal gaz yasasının tek durumda uygulanması (Soru 1, 2, 4);
adyabatik ya da başka süreç yok. Türev ya da integral yok.

---

## Soru 1 — Paper 1A

A sealed flask of volume 2.0 × 10⁻³ m³ contains an ideal gas at a pressure of 1.5 × 10⁵ Pa and a temperature of 27 °C.

Boltzmann constant = 1.38 × 10⁻²³ J K⁻¹

What is the number of gas molecules in the flask?

A. 7.2 × 10²²
B. 6.0 × 10²³
C. 8.1 × 10²³
D. 2.2 × 10²⁵

**Cevap: A**

**Çözüm.** *T* = 27 + 273 = 300 K. *N* = *PV* / *kT* = (1.5 × 10⁵ × 2.0 × 10⁻³) / (1.38 × 10⁻²³ × 300) = 300 / 4.14 × 10⁻²¹ =
7.2 × 10²².

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Kapta bir mol gaz olduğu varsayılır; Avogadro sabiti cevap olarak verilir: 6.0 × 10²³ |
| C | Sıcaklık kelvine çevrilmez: 300 / (1.38 × 10⁻²³ × 27) = 8.05 × 10²³ |
| D | Sıcaklık hesaba katılmaz: *PV* / *k* = 300 / 1.38 × 10⁻²³ = 2.17 × 10²⁵ |

---

## Soru 2 — Paper 1A

A monatomic ideal gas is in a container of volume 0.040 m³ at a pressure of 2.0 × 10⁵ Pa.

What is the internal energy of the gas?

A. 5.3 kJ
B. 8.0 kJ
C. 12 kJ
D. 24 kJ

**Cevap: C**

**Çözüm.** *U* = 3⁄2 *NkT* = 3⁄2 *PV* = 1.5 × 2.0 × 10⁵ × 0.040 = 1.2 × 10⁴ J = 12 kJ. Sıcaklık ve madde miktarı gerekmez.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Çarpan ters alınır: 2⁄3 *PV* = 5.33 kJ |
| B | İç enerji *PV*'ye eşit sayılır: 8.0 kJ |
| D | *P* = ⅓ρ*v*² ifadesindeki 3 çarpanı enerjiye taşınır: 3*PV* = 24 kJ |

---

## Soru 3 — Paper 1A

The behaviour of a real gas is compared with the predictions of the ideal gas model.

Under which conditions is the ideal gas model the best approximation for a real gas?

A. high pressure and high temperature
B. high pressure and low temperature
C. low pressure and low temperature
D. low pressure and high temperature

**Cevap: D**

**Çözüm.** Düşük basınçta (düşük yoğunlukta) moleküller birbirinden uzaktır; molekül hacmi kabın hacmine göre ihmal edilir. Yüksek
sıcaklıkta moleküllerin kinetik enerjisi, moleküller arası kuvvetlerin potansiyel enerjisine göre büyüktür. İkisi birlikte ideal gaz
varsayımlarını en iyi karşılar.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Yalnızca sıcaklık koşulu doğru; yüksek basınçta molekül hacminin ihmal edilemeyeceği gözden kaçar |
| B | İki koşul da ters; gazın sıvılaşmaya en yakın olduğu durum "ideal" sanılır |
| C | Yalnızca basınç koşulu doğru; düşük sıcaklıkta moleküller arası kuvvetlerin önem kazandığı gözden kaçar |

---

## Soru 4 — Paper 1A

Containers X and Y hold different ideal gases at the same pressure. The density of the gas in X is four times the density of the
gas in Y.

What is the ratio (root mean square speed of the molecules in X) / (root mean square speed of the molecules in Y)?

A. 1⁄4
B. 1⁄2
C. 2
D. 4

**Cevap: B**

**Çözüm.** *P* = ⅓ρ*v*² → *v* = √(3*P*/ρ). Basınç aynı olduğundan *v* ∝ 1/√ρ. Oran = 1/√4 = 1⁄2.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Karekök alınmaz (*v* ∝ 1/ρ): 1⁄4 |
| C | Orantı ters kurulur (*v* ∝ √ρ): 2 |
| D | Hem ters kurulur hem karekök alınmaz (*v* ∝ ρ): 4 |

---

## Soru 5 — Paper 2 (9 puan)

A rigid steel cylinder of volume 0.012 m³ contains helium at a pressure of 1.5 × 10⁷ Pa and a temperature of 17 °C. Helium is a
monatomic gas and is assumed to behave as an ideal gas.

Gas constant *R* = 8.31 J K⁻¹ mol⁻¹

**(a)** Show that the amount of helium in the cylinder is about 75 mol. [2]

The cylinder is left in sunlight and the temperature of the helium rises to 46 °C.

**(b)** Calculate the new pressure of the helium. [2]

**(c)** Explain, using the kinetic model of a gas, why the pressure of the helium increases. [2]

**(d)** Calculate the increase in the internal energy of the helium. [2]

**(e)** Suggest why the ideal gas model may **not** be accurate for the helium in this cylinder. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *T* = 290 «K» ✓<br>*n* = (1.5 × 10⁷ × 0.012) / (8.31 × 290) = 74.7 «mol» ✓ | *Answer 75 mol is given; award the second mark only if 74.7 or the complete substitution is seen.* | 2 |
| 5. | b | | *P*/*T* = constant **OR** *P*₂ = 1.5 × 10⁷ × 319 / 290 ✓<br>*P*₂ = 1.65 × 10⁷ «Pa» ✓ | *Allow use of PV = nRT with n = 75 mol (gives 1.66 × 10⁷ Pa).*<br>*Award [1 max] if Celsius temperatures are used (4.1 × 10⁷ Pa).* | 2 |
| 5. | c | | the average speed / kinetic energy of the atoms increases ✓<br>collisions with the walls are more frequent **OR** the change in momentum in each collision is greater ✓<br>so the «average» force on the walls increases «and the area is unchanged» ✓ | *OWTTE* | 2 max |
| 5. | d | | Δ*U* = 3⁄2 *nR*Δ*T* = 1.5 × 75 × 8.31 × 29 ✓<br>Δ*U* = 2.7 × 10⁴ «J» ✓ | *Allow ECF from (a) and (b).*<br>**ALTERNATIVE:** Δ*U* = 3⁄2 *V*Δ*P* = 1.5 × 0.012 × 1.5 × 10⁶ ✓ = 2.7 × 10⁴ «J» ✓ | 2 |
| 5. | e | | the pressure / density is high so the volume of the atoms is not negligible «compared with the volume of the cylinder» **OR** the atoms are close together so the forces between them are not negligible ✓ | *OWTTE*<br>*Do not accept "helium is a real gas" without a reason.* | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `V = 0.012 m^3`, `P1 = 1.5e7 Pa`, `T1 = 290 K`, `T2 = 319 K`; sabit `R = 8.31 J/(K mol)` | |
| `n` | `P1*V/(R*T1)` | 74.7 mol |
| `P2` | `P1*T2/T1` | 1.65 × 10⁷ Pa |
| `dU` | `1.5*n*R*(T2 - T1)` | 2.70 × 10⁴ J (n = 75 mol ile 2.71 × 10⁴ J) |

---

## Soru 6 — Paper 1B (11 puan)

A student investigates how the pressure of a gas depends on its temperature. A sealed flask of air is connected by a short narrow
tube to a pressure gauge. The flask is fully immersed in a water bath. The student changes the temperature *θ* of the water, waits
several minutes and then records *θ* and the pressure *P* of the air.

> **Şekil:** Su banyosuna tamamen batırılmış, ağzı tıpayla kapatılmış cam balon. Tıpadan çıkan kısa ve dar bir boru, su yüzeyinin
> üstündeki bir basınç göstergesine bağlıdır. Suda bir termometre ve bir karıştırıcı vardır. Şekil ölçekli değildir.

| *θ* / °C ± 0.5 °C | *P* / kPa ± 1 kPa |
|---|---|
| 10.0 | 98 |
| 30.0 | 106 |
| 50.0 | 112 |
| 70.0 | 119 |
| 90.0 | 126 |

**(a)** State **one** quantity, other than those in the table, that must stay constant during the investigation. [1]

**(b)** Outline why the student waits several minutes before taking each pair of readings. [1]

The student plots a graph of *P* against *θ* with uncertainty bars for *P*. The uncertainty bars for *θ* are too small to draw.
The line of best fit has a gradient of 0.345 kPa °C⁻¹ and an intercept on the *P*-axis of 95.0 kPa.

**(c)** The student states that *P* is directly proportional to *θ*. Discuss, using the data, whether this statement is correct. [2]

**(d)** The line of best fit is extrapolated to *P* = 0. Determine the temperature *θ*₀, in °C, at which the line predicts that the
pressure is zero. [2]

The lines of maximum and minimum gradient that pass through all the uncertainty bars are (values rounded to four significant
figures):

| Line | Gradient / kPa °C⁻¹ | Intercept on *P*-axis / kPa |
|---|---|---|
| maximum gradient | 0.3667 | 94.00 |
| minimum gradient | 0.3250 | 95.75 |

**(e)** Determine the absolute uncertainty in *θ*₀. [2]

**(f)** The accepted value of absolute zero is −273 °C. Comment on whether the result of the experiment is consistent with this
value. [1]

**(g)** Suggest **one** change to the investigation that would reduce the uncertainty in *θ*₀. Give a reason for your answer. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | volume «of the air / flask» **OR** mass / amount / number of molecules of air ✓ | | 1 |
| 6. | b | | so that the air «in the flask» reaches the temperature of the water / thermal equilibrium ✓ | *OWTTE* | 1 |
| 6. | c | | the line does not pass through the origin / the intercept is 95 kPa, not zero **OR** *P*/*θ* is not constant, with two values calculated «e.g. 98 / 10 = 9.8 and 126 / 90 = 1.4» ✓<br>so the statement is not correct; the relationship is linear but not directly proportional «*P* is proportional to the kelvin temperature» ✓ | *The first mark requires reference to the data or the intercept.* | 2 |
| 6. | d | | 0 = 95.0 + 0.345 *θ*₀ **OR** *θ*₀ = −95.0 / 0.345 ✓<br>*θ*₀ = −275 «°C» ✓ | *Award [1 max] if the negative sign is missing.* | 2 |
| 6. | e | | *θ*₀ = −94.00 / 0.3667 = −256 «°C» **AND** *θ*₀ = −95.75 / 0.3250 = −295 «°C» ✓<br>uncertainty = (295 − 256) / 2 = «±» 19 «°C» ✓ | *Accept 20 °C.*<br>*Accept the difference between either value and the best-fit value (19 or 20 °C).* | 2 |
| 6. | f | | consistent, because −273 °C lies within the range of the result «−295 °C to −255 °C» ✓ | *Allow ECF from (d) and (e).*<br>*A conclusion without reference to the range does not gain the mark.* | 1 |
| 6. | g | | use a wider range of temperatures «e.g. include an ice bath or a freezing mixture» ✓<br>so that the extrapolation is shorter / the gradient is determined more precisely ✓<br>**OR**<br>use a pressure gauge with a smaller uncertainty / better resolution ✓<br>so that the uncertainty bars are smaller and the range of possible lines is narrower ✓ | *OWTTE*<br>*The second mark is for a reason linked to the change.*<br>*Do not accept "repeat the readings" without a link to the uncertainty in P.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | veri tablosu; `dP = 1 kPa` | |
| `m_best`, `c_best` | en küçük kareler doğrusu | 0.345 kPa °C⁻¹, 94.95 kPa |
| `theta0` | `-c_best/m_best` | −275.2 °C (soruda verilen 95.0 ile −275.4 °C) |
| `m_max`, `c_max` | tüm belirsizlik çubuklarından geçen en dik doğru | 0.3667 kPa °C⁻¹, 94.00 kPa |
| `m_min`, `c_min` | tüm belirsizlik çubuklarından geçen en yatık doğru | 0.325 kPa °C⁻¹, 95.75 kPa |
| `theta0_max` | `-c_max/m_max` | −256.4 °C (soruda verilen 0.3667 ile −256.3 °C) |
| `theta0_min` | `-c_min/m_min` | −294.6 °C |
| `d_theta0` | `(theta0_max - theta0_min)/2` | 19.1 °C ≈ 19 °C (tek anlamlı basamakla 20 °C) |

### Şekil notu

Öğrenciye gösterilecek sürümde tablo ile birlikte belirsizlik çubuklu *P*–*θ* grafiği yer alır; yatay eksen dış değerleme
yapılabilmesi için −300 °C'ye kadar uzatılır. Grafik aynı veriden kodla üretilir (D-14). En dik doğru (30 °C; 105 kPa) ve
(90 °C; 127 kPa) çubuk uçlarından, en yatık doğru (10 °C; 99 kPa) ve (90 °C; 125 kPa) çubuk uçlarından geçer; soruda verilen eğim ve
kesim değerleri bunların dört anlamlı basamağa yuvarlanmış halidir. Sonuç: *θ*₀ = (−275 ± 19) °C ya da (−280 ± 20) °C.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi + alt alta A–D | Soru 1, 2, 4 "What is …?"; Soru 3 "Under which conditions …?" (seyrek "Which" biçimi) |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1, 2, 4 uygun (artan); Soru 3 iki değişkenli kısa sözel seçenek |
| 1A: tablo seçenekli biçim doğrulanamadı | Soru 3 tablo yerine "… and …" kalıplı kısa seçeneklerle yazıldı |
| 1A: doğru cevap konumu dengeli | A, C, D, B |
| 1A: şekil olmadan çözülebilir | Soru 1–4 şekil gerektirmiyor |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 2, 2, 1; toplam 9) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | Soru 5 uygun: (a) Show that, (c) Explain, (e) Suggest |
| Paper 2: olumsuzluk sözcüğü koyu | Soru 5(e) ("not") uygun |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, max, ECF, OWTTE | Soru 5 ve Soru 6 uygun (Soru 6 da dört sütunlu biçimde) |
| 1B: yaklaşık 10 puanlık deney sorusu, alt parçalar 1–3 puan | Soru 6 uygun (1, 1, 2, 2, 2, 1, 2; toplam 11) |
| 1B: tablo başlığı "büyüklük / birim ± belirsizlik" | Soru 6 uygun; hangi belirsizlik çubuğunun çizilmediği metinde söyleniyor |
| 1B: düzenek şeması | Yalnızca `> **Şekil:**` tarifi var; çizim üretilmedi. Soru şekil olmadan çözülebilir |
| 1B: öğrenci verilen grafiğe en uygun doğruyu çizer, eğimi ve kesimi kendisi bulur | **Soru 6 uygun değil:** grafik üretilemediği için eğim ve kesim değerleri metinde verildi. Grafik şablonu hazır olunca (d) ve (e) parçaları yeniden yazılmalı |
| 1B: parça yapısı (a), (b) altında (i)–(iv) | Soru 6 yalnızca (a)–(g) düzeyinde; alt numaralandırma kullanılmadı |
| Değer–birim yazımı (kPa °C⁻¹), anlamlı basamak | Uygun; en uygun doğrunun eğimi ve kesimi 3, en dik / en yatık doğrularınki 4 anlamlı basamakla verildi (dış değerleme yuvarlamaya duyarlı; 3 basamak çubuk uçlarını aşıyordu) |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından bağımsız bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları ve
markscheme sonuçları (Soru 6'nın veri işlemesi dahil) bağımsız olarak yeniden üretildi (KRİTİK ve ORTA bulgu yok). Ayrıntı:
[review/b3-review.md](review/b3-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

İnceleme sonucu yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 6 (e), DÜŞÜK-2:** en dik / en yatık doğruların değerleri 0.367 / 94.0 ve 0.325 / 95.8 → 0.3667 / 94.00 ve 0.3250 / 95.75
  yapıldı; "values rounded to four significant figures" notu eklendi. Önceki değerler çubuk uçlarını 0.03–0.05 kPa aşıyordu; yeni
  değerlerde en yatık doğru uçlara tam oturuyor, en dik doğru 90 °C'de yalnızca 0.003 kPa aşıyor (0.36666… yuvarlaması).
  *θ*₀ değerleri −256.1 / −294.8 °C → −256.3 / −294.6 °C; yarı aralık 19.3 °C → 19.1 °C.
- **Soru 6 (e), DÜŞÜK-3:** markscheme cevabı "20 «°C», accept 19 or 19.5" → "19 «°C», accept 20" oldu; en uygun değerden farkla
  ilgili not "19 or 20 °C" olarak düzeltildi. Formül zinciri ve şekil notu buna göre güncellendi.
- **Soru 4, DÜŞÜK-1 ("root mean square speed" terimi):** değişiklik yapılmadı; inceleme de terimin fizik olarak doğru olduğunu ve
  uzman teyidine kadar kalmasını öneriyor.
- **DÜŞÜK-4 (1B'de eğimin metinde verilmesi) ve DÜŞÜK-5 (SL kısa soruda 9 puan):** değişiklik yapılmadı; ilki grafik şablonu
  gelene kadar çözülemez ve "Biçim uyumu"nda zaten işaretli, ikincisi uzman teyidi bekleyen kayıt.

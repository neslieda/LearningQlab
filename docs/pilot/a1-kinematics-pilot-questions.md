# Pilot soru seti: A.1 Kinematik

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set, müfredat analizinden ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)) özgün soru üretme yaklaşımının
> elle yapılmış bir denemesidir. Ürün hattı kurulduğunda aynı iş Blueprint → üretim → kod kontrolü → kör çözüm → inceleme adımlarından geçer.
>
> **Kaynak:** yalnızca müfredat düğümü A.1 ve genel fizik. Hiçbir sınav sorusu girdi olarak kullanılmadı.
> **Sayısal doğrulama:** tüm sonuçlar ayrı bir hesapla yeniden üretildi (g = 9.8 m s⁻² alındı; veri kitapçığı değeri uzmanca teyit edilmeli).
> **Bağımsız kontrol:** beş soru da yazarından farklı bir kör çözücü tarafından cevaplar görülmeden çözüldü; anahtarlar, çeldirici
> hesapları ve markscheme değerleri uyuştu ([review/recheck-2026-10-11.md](review/recheck-2026-10-11.md)).
> **Doğrulanmayan:** uzman incelemesinden geçmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Yol ile yer değiştirme farkı; ortalama hız | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Aşağı açılı eğik atışın bileşenlerle çözümü | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Akışkan direncinin ivmeye nitel etkisi | AO2 | — | 1 | Orta |
| 4 | Paper 2 | SL | Yatay atış; hız bileşenleri; dirençli hareketin nitel etkisi | AO1–AO3 | State, Calculate, Determine, Explain | 9 | Orta |
| 5 | Paper 1B | SL | Serbest düşme verisinin işlenmesi; belirsizlik; sistematik hata | AO2–AO3 | Outline, Calculate, Determine, Explain | 10 | Orta–zor |

Bu set A.1'in tamamını kapsamaz. Eksik kalanlar: anlık hızın grafikten belirlenmesi, değişken ivmeli hareketin grafik yorumu, yukarı
açılı atış, limit hız.

---

## Soru 1 — Paper 1A

A cyclist rides 600 m due east in 60 s and then 800 m due north in 140 s.

What is the magnitude of the average velocity of the cyclist for the whole journey?

A. 5.0 m s⁻¹
B. 7.0 m s⁻¹
C. 7.9 m s⁻¹
D. 10 m s⁻¹

**Cevap: A**

**Çözüm.** Yer değiştirme = √(600² + 800²) = 1000 m. Toplam süre = 200 s. Ortalama hızın büyüklüğü = 1000 / 200 = 5.0 m s⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Yer değiştirme yerine toplam yol kullanılır: 1400 / 200 (ortalama sürat) |
| C | İki bölümün süratlerinin (10 ve 5.7 m s⁻¹) aritmetik ortalaması alınır |
| D | Yalnızca ilk bölümün sürati alınır |

---

## Soru 2 — Paper 1A

A stone is thrown from the top of a vertical cliff with a speed of 12 m s⁻¹ at an angle of 30° **below** the horizontal. The stone
is released 15 m above the sea. Air resistance is negligible.

What is the horizontal distance from the base of the cliff to the point where the stone hits the sea?

A. 13 m
B. 15 m
C. 18 m
D. 26 m

**Cevap: A**

**Çözüm.** Aşağı yön pozitif. Düşey ilk hız = 12 sin 30° = 6.0 m s⁻¹; yatay hız = 12 cos 30° = 10.4 m s⁻¹.
15 = 6.0t + 4.9t² → t = 1.24 s. Yatay uzaklık = 10.4 × 1.24 = 12.9 m ≈ 13 m.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Yatay bileşen yerine hızın tamamı kullanılır: 12 × 1.24 = 14.9 m |
| C | Düşey ilk hız yok sayılır (yatay atış gibi çözülür): t = 1.75 s, 10.4 × 1.75 = 18.2 m |
| D | Taş yukarı açıyla atılmış gibi çözülür: t = 2.47 s, 10.4 × 2.47 = 25.6 m |

---

## Soru 3 — Paper 1A

A ball is thrown vertically upwards. Air resistance is **not** negligible.

What is the magnitude of the acceleration of the ball immediately after it is released?

A. zero
B. less than *g*
C. *g*
D. greater than *g*

**Cevap: D**

**Çözüm.** Yukarı çıkarken direnç kuvveti aşağı yönlüdür, yani ağırlıkla aynı yöndedir. Bileşke kuvvet ağırlıktan büyüktür; ivmenin
büyüklüğü *g*'den büyüktür.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | "Atıldığı anda hızı en büyük, ivmesi yok" düşüncesi; hız ile ivmenin karıştırılması |
| B | Direncin her durumda ivmeyi azalttığı varsayılır (iniş için doğru, çıkış için yanlış) |
| C | Direnç yok sayılır; serbest düşme ivmesi alınır |

---

## Soru 4 — Paper 2 (9 puan)

A drone flies horizontally at a constant speed of 18 m s⁻¹ at a height of 44 m above level ground. It releases a small package.
Air resistance on the package is negligible in parts (a) to (c).

**(a)** State the horizontal component of the velocity of the package at the instant it is released. [1]

**(b)** Calculate the time taken for the package to reach the ground. [2]

**(c)** Determine the magnitude and the direction of the velocity of the package as it reaches the ground. [3]

In practice, air resistance on the package is not negligible.

**(d)** (i) Explain, without calculation, the effect of air resistance on the time taken for the package to reach the ground. [2]

 (ii) State how the horizontal component of the velocity of the package at the ground compares with your answer to (a). [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 4. | a | | 18 «m s⁻¹» ✓ | | 1 |
| 4. | b | | 44 = ½ × 9.8 × *t*² ✓<br>*t* = 3.0 «s» ✓ | | 2 |
| 4. | c | | *v*<sub>y</sub> = 9.8 × 3.0 «= 29 m s⁻¹» ✓<br>*v* = √(18² + 29²) = 34 «m s⁻¹» ✓<br>58° below the horizontal **OR** 32° to the vertical ✓ | *Allow ECF from (b).* | 3 |
| 4. | d | i | air resistance has an upward / vertical component «opposing the fall» ✓<br>vertical acceleration is less than *g* so the time is longer ✓ | *OWTTE* | 2 |
| 4. | d | ii | less «than 18 m s⁻¹» ✓ | | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `u = 18 m/s`, `H = 44 m`, sabit `g = 9.8 m/s^2` | |
| `t` | `sqrt(2*H/g)` | 3.00 s |
| `v_y` | `g*t` | 29.4 m s⁻¹ |
| `v` | `sqrt(u**2 + v_y**2)` | 34.4 m s⁻¹ |
| `angle` | `atan(v_y/u)` | 58.5° |

---

## Soru 5 — Paper 1B (10 puan)

A student investigates free fall. A steel ball is held by an electromagnet. When the current is switched off, a timer starts and
the ball falls a height *h* onto a trapdoor switch that stops the timer. The student repeats the measurement for each height and
records the mean time *t*.

| *h* / m | *t* / s ± 0.01 s |
|---|---|
| 0.200 | 0.20 |
| 0.400 | 0.29 |
| 0.600 | 0.35 |
| 0.800 | 0.40 |
| 1.000 | 0.45 |

The uncertainty in *h* is negligible.

**(a)** Outline why a graph of *h* against *t*² is expected to be a straight line through the origin. [2]

**(b)** Calculate the percentage uncertainty in *t*² for *h* = 1.000 m. [2]

The student plots *h* against *t*² with uncertainty bars. The gradient of the line of best fit is 5.0 m s⁻². The lines of maximum and
minimum gradient have gradients of 5.4 m s⁻² and 4.6 m s⁻².

**(c)** Determine the acceleration of free fall *g* given by this experiment, with its absolute uncertainty. [3]

**(d)** The accepted value of *g* is 9.8 m s⁻². Comment on whether the result of the experiment is consistent with the accepted value. [1]

**(e)** The electromagnet takes a short, constant time to release the ball after the timer has started. Explain the effect of this
on the value of *g* obtained. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *h* = ½*gt*² «as the ball starts from rest» ✓<br>*h* is proportional to *t*² **OR** gradient = ½*g* is constant ✓ | | 2 |
| 5. | b | | fractional uncertainty in *t* = 0.01 / 0.45 «= 0.022» ✓<br>doubled for *t*²: 4.4 % ✓ | *Accept 4 %.* | 2 |
| 5. | c | | *g* = 2 × gradient = 10 «m s⁻²» ✓<br>uncertainty in gradient = (5.4 − 4.6) / 2 = 0.4 «m s⁻²» ✓<br>*g* = (10.0 ± 0.8) «m s⁻²» ✓ | *Accept ± 1 m s⁻² if the answer is given as (10 ± 1).* | 3 |
| 5. | d | | consistent, as 9.8 m s⁻² lies within the range 9.2–10.8 m s⁻² ✓ | *Allow ECF from (c): the conclusion must follow from the candidate's own range.* | 1 |
| 5. | e | | measured times are greater than the true times of fall / this is a systematic error ✓<br>the gradient is smaller so the value of *g* obtained is too small ✓ | *OWTTE* | 2 |

### Şekil notu

Öğrenciye gösterilecek sürümde tablo ile birlikte belirsizlik çubuklu *h*–*t*² grafiği yer alır. Grafik aynı veriden kodla üretilir
(D-14). Tablodaki veriden hesaplanan en küçük kareler eğimi 4.98 m s⁻²; belirsizlik çubuklarının uçlarından geçen doğruların eğimleri
5.35 ve 4.56 m s⁻²'dir; soruda verilen 5.0, 5.4 ve 4.6 değerleri bunların iki anlamlı basamağa yuvarlanmış halidir.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–3 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–2 uygun (artan); Soru 3 sözel sıralı ölçek |
| 1A: olumsuzluk sözcüğü koyu | Soru 2 ("below") ve Soru 3 ("not") uygun |
| 1A: tablo seçenekli biçim örnekte doğrulanamadı | Soru 3 bu yüzden tek kavramlı, kısa seçenekli biçime çevrildi |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 4 uygun (1, 2, 3, 2, 1; toplam 9) |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF, OWTTE | Soru 4 ve Soru 5 uygun |
| 1B: yaklaşık 10 puanlık deney sorusu, alt parçalar 1–3 puan | Soru 5 uygun (2, 2, 3, 1, 2; toplam 10) |
| 1B: tablo başlığı "büyüklük / birim ± belirsizlik" | Soru 5 uygun |
| 1B: öğrenci verilen grafiğe en uygun doğruyu çizer ve eğimi kendisi bulur | **Soru 5 uygun değil:** grafik üretilemediği için eğimler metinde verildi. Grafik şablonu hazır olunca (c) parçası yeniden yazılmalı |
| Değer–birim yazımı (m s⁻¹), 2 anlamlı basamak | Uygun |

## Bu denemeden çıkan gözlemler

1. **Formül zinciri sayısal sorularda çalışıyor** (Soru 2, 4, 5). Nitel sorularda (Soru 3) kodla doğrulanacak bir şey yok; güvence
   eleştirmen ve uzmandan gelmeli.
2. **Çeldiriciler hesaplanabilir.** Soru 1 ve 2'de her yanlış seçenek belirli bir yanılgının formülünden çıkıyor; şemada çeldirici
   başına "yanılgı + formül" tutulursa kod bunları da doğrular.
3. **Veri temelli soru şekle bağlı.** Soru 5, grafik olmadan eksik kalıyor; şablondan grafik üretimi bu soru türü için ön koşul.
4. **Kapsam dengesi elle zor.** Beş soru A.1'in yarısını bile kapsamıyor; düğüm başına kazanım × hedef × soru türü tablosu Blueprint
   aşamasında tutulmalı.

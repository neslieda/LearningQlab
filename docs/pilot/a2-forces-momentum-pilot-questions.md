# Pilot soru seti: A.2 Kuvvet ve momentum

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set, [yazım standardına](AUTHORING_STANDARD.md) göre ve [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla elle yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü A.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav sorusu, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi
> (g = 9.8 m s⁻²; veri kitapçığı değeri uzmanca teyit edilmeli). Soru 5'teki malzeme değerleri (çelik ve gliserin yoğunluğu, gliserin
> viskozitesi) soruda verildi.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle
> bakılmadı; Soru 5'teki malzeme değerleri (7800 kg m⁻³, 1260 kg m⁻³, 1.4 Pa s) genel bilgiden alındı, bir kaynaktan teyit edilmedi;
> küre hacmi formülünün ve Stokes yasasının veri kitapçığındaki yazımı kontrol edilmedi.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.2) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Statik ve kinetik sürtünme ayrımı; dengede sürtünme kuvveti | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | İtme ve momentum değişimi; F = Δp/Δt (1 boyut, yön değişimi) | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Düşey çemberin en üst noktasında merkezcil kuvvet | AO2 | — | 1 | Orta |
| 4 | Paper 1A | SL | Patlamada momentum korunumu ve kinetik enerjinin paylaşımı | AO3 | — | 1 | Orta–zor |
| 5 | Paper 2 | SL | Ağırlık, kaldırma kuvveti ve Stokes sürüklemesi; kuvvet dengesi | AO2–AO3 | Show that, Calculate, Determine, Explain | 9 | Orta |

Bu set A.2'nin tamamını kapsamaz. Eksik kalanlar: serbest cisim diyagramı çizimi, eğik düzlemde bileşke kuvvet, gerilme, Hooke
yasası, Newton'ın üçüncü yasası çiftleri, esnek ve esnek olmayan çarpışmanın nicel çözümü (1 boyut), kuvvet–zaman grafiğinin altındaki
alan, açısal hız ve yatay çembersel hareket, düşey çemberin en alt noktası, düzgün olmayan çembersel hareket, 2 boyutlu çarpışma
(yalnızca HL).

---

## Soru 1 — Paper 1A

A crate of mass 12 kg is at rest on a horizontal warehouse floor. The coefficient of static friction between the crate and the floor
is 0.50 and the coefficient of dynamic friction is 0.40. A worker pushes the crate with a horizontal force of 40 N.

What is the magnitude of the friction force acting on the crate?

A. 40 N
B. 47 N
C. 59 N
D. 120 N

**Cevap: A**

**Çözüm.** Normal kuvvet = 12 × 9.8 = 118 N. En büyük statik sürtünme = 0.50 × 118 = 59 N. Uygulanan 40 N bundan küçüktür; sandık
durmaya devam eder ve sürtünme kuvveti uygulanan kuvvete eşittir: 40 N.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Sandık kayıyormuş gibi kinetik sürtünme hesaplanır: 0.40 × 118 = 47 N |
| C | Statik sürtünmenin her zaman en büyük değerinde olduğu sanılır: 0.50 × 118 = 59 N |
| D | Sürtünme kuvveti normal kuvvet (ağırlık) ile karıştırılır: 12 × 9.8 = 118 N ≈ 120 N |

---

## Soru 2 — Paper 1A

An ice-hockey puck of mass 0.16 kg slides without friction and hits the barrier at the edge of the rink at right angles with a speed
of 15 m s⁻¹. The puck rebounds along its original path with a speed of 10 m s⁻¹. The puck is in contact with the barrier for 0.020 s.

What is the magnitude of the average force exerted by the barrier on the puck?

A. 40 N
B. 80 N
C. 120 N
D. 200 N

**Cevap: D**

**Çözüm.** Hız yön değiştirir; momentum değişiminin büyüklüğü = 0.16 × (15 + 10) = 4.0 kg m s⁻¹.
Ortalama kuvvet = 4.0 / 0.020 = 200 N.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Momentumun vektör olduğu göz ardı edilir, süratler çıkarılır: 0.16 × (15 − 10) / 0.020 = 40 N |
| B | Yalnızca geri dönüş momentumu alınır: 0.16 × 10 / 0.020 = 80 N |
| C | Yalnızca geliş momentumu alınır (diskin durduğu varsayılır): 0.16 × 15 / 0.020 = 120 N |

---

## Soru 3 — Paper 1A

A toy car of mass 0.050 kg moves on the inside of a vertical circular track of radius 0.40 m. At the highest point of the track
the speed of the car is 3.2 m s⁻¹.

What is the magnitude of the force exerted by the track on the car at the highest point?

A. 0.49 N
B. 0.79 N
C. 1.3 N
D. 1.8 N

**Cevap: B**

**Çözüm.** En üst noktada ağırlık ve pistin tepki kuvveti *N* ikisi de merkeze (aşağı) yönlüdür: *N* + *mg* = *mv*²/*r*.
*mv*²/*r* = 0.050 × 3.2² / 0.40 = 1.28 N; *mg* = 0.49 N; *N* = 1.28 − 0.49 = 0.79 N.
(*v*² = 10.2 m² s⁻² > *gr* = 3.9 m² s⁻² olduğundan araba pistle temasını korur.)

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Tepki kuvvetinin ağırlığa eşit olduğu varsayılır (denge gibi düşünülür): 0.050 × 9.8 = 0.49 N |
| C | Ağırlık hesaba katılmaz; tepki kuvveti merkezcil kuvvetin tamamı sanılır: 1.28 N ≈ 1.3 N |
| D | En alt noktanın bağıntısı kullanılır (*N* = *mv*²/*r* + *mg*): 1.28 + 0.49 = 1.77 N ≈ 1.8 N |

---

## Soru 4 — Paper 1A

Two trolleys X and Y are at rest on a frictionless horizontal track with a compressed spring between them. The mass of X is *m* and
the mass of Y is 3*m*. The spring is released and the trolleys move apart.

What is the ratio (kinetic energy of X) / (kinetic energy of Y) after the trolleys have separated?

A. 1/3
B. 1
C. 3
D. 9

**Cevap: C**

**Çözüm.** Başlangıçta toplam momentum sıfırdır; ayrıldıktan sonra momentumların büyüklüğü eşittir (*p*). *E*<sub>k</sub> = *p*²/2*m*
olduğundan kinetik enerji kütleyle ters orantılıdır: oran = 3*m* / *m* = 3. (Eşdeğer yol: *v*<sub>X</sub> = 3*v*<sub>Y</sub>;
½*m*(3*v*)² / ½(3*m*)*v*² = 3.)

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Süratlerin eşit olduğu varsayılır; kinetik enerji kütleyle doğru orantılı alınır: *m* / 3*m* = 1/3 |
| B | "Eşit ve zıt" olan büyüklüğün momentum değil enerji olduğu sanılır; yay enerjisinin eşit paylaşıldığı düşünülür |
| D | Sürat oranı (3) doğru bulunur ama yalnızca karesi alınır, kütle oranı unutulur: 3² = 9 |

---

## Soru 5 — Paper 2 (9 puan)

A steel ball bearing of radius 2.0 mm is released in a tall cylinder of glycerol. After a short distance the ball falls at a constant
(terminal) speed.

The following data are available.

Density of steel = 7800 kg m⁻³
Density of glycerol = 1260 kg m⁻³
Viscosity of glycerol = 1.4 Pa s

**(a)** Show that the weight of the ball is about 2.6 × 10⁻³ N. [2]

**(b)** Calculate the buoyancy force acting on the ball. [2]

**(c)** Determine the terminal speed of the ball. [3]

The glycerol is now warmed. Its viscosity decreases and the change in its density is negligible.

**(d)** Explain the effect of warming the glycerol on the terminal speed of the ball. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *V* = <sup>4</sup>⁄<sub>3</sub> π × (2.0 × 10⁻³)³ «= 3.35 × 10⁻⁸ m³» ✓<br>*W* = 7800 × 3.35 × 10⁻⁸ × 9.8 = 2.56 × 10⁻³ «N» ✓ | *Answer must be shown to at least 3 s.f. or the full substitution must be seen.* | 2 |
| 5. | b | | *F*<sub>b</sub> = 1260 × 3.35 × 10⁻⁸ × 9.8 ✓<br>= 4.1 × 10⁻⁴ «N» ✓ | *Allow ECF for the volume from (a).* | 2 |
| 5. | c | | drag force = weight − buoyancy force «= 2.15 × 10⁻³ N» ✓<br>*v* = *F*<sub>d</sub> / (6π*ηr*) = 2.15 × 10⁻³ / (6π × 1.4 × 2.0 × 10⁻³) ✓<br>*v* = 0.041 «m s⁻¹» ✓ | *Allow ECF from (b).*<br>*Accept answers in the range 0.041 to 0.042 «m s⁻¹» (use of 2.6 × 10⁻³ N gives 0.041).*<br>*Award [2] max for 0.049 «m s⁻¹» (buoyancy force omitted).* | 3 |
| 5. | d | | weight and buoyancy force are unchanged, so the drag force at terminal speed is the same ✓<br>drag force is proportional to viscosity × speed, so a greater speed is needed **OR** terminal speed increases ✓ | *OWTTE*<br>*The second mark needs a reason linked to the drag force, not only the statement that the ball falls faster.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `r = 2.0e-3 m`, `rho_s = 7800 kg/m^3`, `rho_f = 1260 kg/m^3`, `eta = 1.4 Pa s`, sabit `g = 9.8 m/s^2` | |
| `V` | `4/3*pi*r**3` | 3.35 × 10⁻⁸ m³ |
| `W` | `rho_s*V*g` | 2.56 × 10⁻³ N |
| `F_b` | `rho_f*V*g` | 4.14 × 10⁻⁴ N |
| `F_d` | `W - F_b` | 2.15 × 10⁻³ N |
| `v` | `F_d/(6*pi*eta*r)` | 0.0407 m s⁻¹ |

Kontrol: Reynolds sayısı ≈ `rho_f*v*2*r/eta` = 0.15 (≪ 1); Stokes yasasının geçerli olduğu akış bölgesinde. Bu kontrol öğrenciden
istenmez.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–3 uygun (artan, N); Soru 4 birimsiz oran, artan |
| 1A: doğru cevap konumu dengeli | A, D, B, C |
| 1A: olumsuz kök | Kullanılmadı |
| 1A: bir ya da iki adımlı hesap | Soru 1–3 iki adım; Soru 4 cebirsel akıl yürütme, eşzamanlı denklem gerektirmez |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 3, 2; toplam 9). Not: SL örnek kâğıdında kısa sorular 4–6 puan gözlendi; 9 puan HL aralığının üst ucu, SL kısa sorusu için uzun; uzman teyidi gerekir |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanabilir | Soru 5 (a) uygun; (c) için kabul aralığı verildi |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF, OWTTE | Soru 5 uygun |
| Değer–birim yazımı (m s⁻¹, kg m⁻³), 2 anlamlı basamak | Uygun; Soru 1'de D seçeneği 2 anlamlı basamağa yuvarlandı (118 → 120 N) |
| Şekil | Hiçbir soru şekil gerektirmiyor; Soru 3 ve 5 öğrenci sürümünde şekille desteklenebilir |
| Kapsam sınırları (A.2) | 1 boyut; çarpışmada eşzamanlı denklem yok; düşey çemberde yalnızca en üst nokta; eğimli viraj yok |

## Bağımsız kontrol

Tarih: 2026-10-11. Kör çözücü, cevapları görmeden soruları çözdü ve tüm cevap anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti; KRİTİK ya da ORTA bulgu yok.
Ayrıntı: [review/a2-review.md](review/a2-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

Bulgular üzerine yapılan değişiklikler:

- Soru 5 (c) markscheme notu: "gives 0.0415" → "gives 0.041" (yuvarlanmamış kaldırma kuvvetiyle 0.0414; `python3` ile yeniden hesaplandı). Kabul aralığı değişmedi.
- "Biçim uyumu" tablosuna, 9 puanın SL kısa sorusu için uzun olduğu ve uzman teyidi gerektiği notu eklendi (A.3 ile aynı beyan).
- Soru 1 D seçeneği (118 → 120 N): incelemede değişiklik istenmedi; olduğu gibi bırakıldı.

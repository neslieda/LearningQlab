# Pilot soru seti: A.4 Katı cisim mekaniği

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set, [yazım standardına](AUTHORING_STANDARD.md) göre ve [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla elle yazıldı.
> A.4 yalnızca HL düğümüdür; tüm sorular HL etiketlidir ve SL havuzuna girmez.
>
> **Kaynak:** yalnızca müfredat düğümü A.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav sorusu, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi
> (g = 9.8 m s⁻²; veri kitapçığı değeri uzmanca teyit edilmeli). Belirli şekillerin eylemsizlik momenti formülleri soruda verildi.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle
> bakılmadı; Soru 5'te borunun kaymadan yuvarlanması için gereken sürtünme katsayısı koşulu soruda varsayım olarak verildi, ayrıca
> sınanmadı; Soru 1'deki düzgün kirişin ağırlığının orta noktadan etkimesinin "kütle merkezi hesabı yok" sınırıyla uyumlu sayıldığı
> yazarın yorumudur.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.4) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Tork ve dönme dengesi | AO2 | — | 1 | Orta |
| 2 | Paper 1A | HL | *τ* = *Iα* ve sabit açısal ivme denklemleri | AO2 | — | 1 | Orta |
| 3 | Paper 1A | HL | Açısal momentumun korunumu; nokta kütle için *mr*² | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Kaymadan yuvarlanmada öteleme ve dönme kinetik enerjisinin paylaşımı | AO3 | — | 1 | Orta–zor |
| 5 | Paper 2 | HL | Kaymadan yuvarlanma; enerji korunumu; açısal momentum; eylemsizlik momentinin harekete etkisi | AO1–AO3 | State, Show that, Calculate, Explain | 9 | Orta–zor |

Bu set A.4'ün tamamını kapsamaz. Eksik kalanlar: açısal itme (tork–zaman grafiğinin altındaki alan), açısal yer değiştirmenin sabit
açısal ivme denklemleriyle bulunması, birden çok nokta kütle için Σ*mr*² hesabı, öteleme ve dönme dengesinin birlikte uygulanması
(menteşe kuvveti), dönme kinetik enerjisinin açısal momentum korunurken değişimi, açıyla uygulanan kuvvetin torku (*Fr* sin *θ*).

---

## Soru 1 — Paper 1A

A uniform horizontal beam of length 3.0 m and weight 200 N is hinged to a wall at one end. The beam is held horizontal by a vertical
cable attached to the beam at a distance of 2.0 m from the hinge. A lamp of weight 150 N hangs from the free end of the beam.

> **Şekil:** Solda düşey duvar; duvara menteşeyle bağlı, sağa doğru uzanan 3.0 m'lik yatay kiriş. Menteşeden 2.0 m uzakta kirişten
> yukarı çıkan düşey kablo. Kirişin sağ (serbest) ucundan aşağı sarkan lamba. *Diagram not to scale.*

What is the tension in the cable?

A. 225 N
B. 350 N
C. 375 N
D. 525 N

**Cevap: C**

**Çözüm.** Menteşeye göre tork dengesi: *T* × 2.0 = 200 × 1.5 + 150 × 3.0 = 750 N m; *T* = 375 N.
(Menteşe kirişe aşağı yönlü 25 N uygular; bu kuvvetin menteşeye göre torku sıfırdır.)

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Kirişin kendi ağırlığı hesaba katılmaz: 150 × 3.0 / 2.0 = 225 N |
| B | Tork yerine yalnızca düşey kuvvet dengesi yazılır, menteşe kuvveti yok sayılır: 200 + 150 = 350 N |
| D | Kirişin ağırlığının orta nokta yerine serbest uçtan etkidiği varsayılır: (200 × 3.0 + 150 × 3.0) / 2.0 = 525 N |

---

## Soru 2 — Paper 1A

A flywheel is a uniform solid disc of mass 8.0 kg and radius 0.25 m that can rotate about a fixed frictionless axle through its
centre. The moment of inertia of the disc about the axle is ½*MR*². The flywheel is at rest. A constant force of 6.0 N is then applied
tangentially at the rim of the disc.

What is the angular speed of the flywheel after 5.0 s?

A. 15 rad s⁻¹
B. 30 rad s⁻¹
C. 60 rad s⁻¹
D. 120 rad s⁻¹

**Cevap: B**

**Çözüm.** *I* = ½ × 8.0 × 0.25² = 0.25 kg m². *τ* = *FR* = 6.0 × 0.25 = 1.5 N m. *α* = *τ*/*I* = 6.0 rad s⁻².
*ω* = *αt* = 6.0 × 5.0 = 30 rad s⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Verilen ½ çarpanı atlanır, *I* = *MR*² = 0.50 kg m² alınır: *α* = 3.0 rad s⁻², *ω* = 15 rad s⁻¹ |
| C | Kuvvet kolu olarak yarıçap yerine çap alınır: *τ* = 6.0 × 0.50 = 3.0 N m, *α* = 12 rad s⁻², *ω* = 60 rad s⁻¹ |
| D | Tork yerine kuvvetin kendisi kullanılır (*α* = *F*/*I*): 6.0 / 0.25 = 24, × 5.0 = 120 |

---

## Soru 3 — Paper 1A

A horizontal turntable rotates freely about a vertical axis with an angular speed of 3.0 rad s⁻¹. The moment of inertia of the
turntable about the axis is 0.80 kg m². A small lump of clay of mass 2.0 kg is dropped vertically onto the turntable and sticks to it
at a distance of 0.50 m from the axis.

What is the angular speed of the turntable after the clay has stuck to it?

A. 1.8 rad s⁻¹
B. 2.4 rad s⁻¹
C. 3.0 rad s⁻¹
D. 4.9 rad s⁻¹

**Cevap: A**

**Çözüm.** Kil düşey düştüğü için eksene göre açısal momentumu yoktur; dış tork olmadığından sistemin açısal momentumu korunur.
Yeni eylemsizlik momenti = 0.80 + 2.0 × 0.50² = 1.30 kg m². *ω* = 0.80 × 3.0 / 1.30 = 1.8 rad s⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Açısal momentum yerine dönme kinetik enerjisinin korunduğu varsayılır: 3.0 × √(0.80 / 1.30) = 2.4 rad s⁻¹ |
| C | Düşey düşen kilin dönmeyi etkilemediği düşünülür; açısal sürat değişmez |
| D | Eylemsizlik momentlerinin oranı ters çevrilir: 3.0 × 1.30 / 0.80 = 4.9 rad s⁻¹ |

---

## Soru 4 — Paper 1A

A uniform solid sphere of mass *M* and radius *R* rolls without slipping along a horizontal surface. The moment of inertia of the
sphere about an axis through its centre is ⅖*MR*².

What is the ratio (translational kinetic energy of the sphere) / (total kinetic energy of the sphere)?

A. 2/7
B. 2/5
C. 1/2
D. 5/7

**Cevap: D**

**Çözüm.** Kaymadan yuvarlanmada *ω* = *v*/*R*. Dönme kinetik enerjisi = ½ × ⅖*MR*² × (*v*/*R*)² = ⅕*Mv*². Öteleme kinetik enerjisi
= ½*Mv*². Toplam = 7/10 *Mv*². Oran = (1/2) / (7/10) = 5/7.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | İstenen oran yerine dönme kinetik enerjisinin payı verilir: (1/5) / (7/10) = 2/7 |
| B | Eylemsizlik momentindeki katsayı doğrudan enerji oranı sanılır: 2/5 |
| C | Enerjinin öteleme ve dönme arasında her zaman eşit paylaşıldığı varsayılır: 1/2 |

---

## Soru 5 — Paper 2 (9 puan)

A thin-walled steel pipe of mass 12 kg and radius 0.15 m is released from rest at the top of a loading ramp. The pipe rolls without
slipping down the ramp. The centre of the pipe falls through a vertical height of 0.90 m. The moment of inertia of the pipe about its
central axis is *MR*². Air resistance is negligible.

**(a)** State the relationship between the linear speed *v* of the centre of the pipe and its angular speed *ω* when the pipe rolls
without slipping. [1]

**(b)** Show that the speed of the centre of the pipe at the bottom of the ramp is about 3.0 m s⁻¹. [3]

**(c)** Calculate the angular momentum of the pipe about its central axis at the bottom of the ramp. [2]

A uniform solid cylinder has the same mass and the same radius as the pipe. Its moment of inertia about its central axis is ½*MR*².
The cylinder is released from rest at the top of the same ramp and also rolls without slipping.

**(d)** Explain, without calculation, whether the cylinder takes a longer or a shorter time than the pipe to reach the bottom of
the ramp. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *v* = *ωR* ✓ | *Accept ω = v / R or the relation in words.* | 1 |
| 5. | b | | *Mgh* = ½*Mv*² + ½*Iω*² ✓<br>use of *I* = *MR*² **AND** *ω* = *v*/*R* to get *Mgh* = *Mv*² **OR** *v* = √(*gh*) ✓<br>*v* = √(9.8 × 0.90) = 2.97 «m s⁻¹» ✓ | *Third mark needs an answer to at least 3 s.f. (2.97) from a correct substitution.*<br>*Award [1] max for v = √(2gh) = 4.2 «m s⁻¹» (rotation ignored).* | 3 |
| 5. | c | | *ω* = 3.0 / 0.15 «= 20 rad s⁻¹» **OR** *L* = *Iω* = *MRv* ✓<br>*L* = 12 × 0.15² × 20 = 5.4 «kg m² s⁻¹» ✓ | *Accept answers in the range 5.3 to 5.4 «kg m² s⁻¹» (use of 2.97 m s⁻¹ gives 5.35).*<br>*Accept the unit N m s.* | 2 |
| 5. | d | | both lose the same gravitational potential energy / have the same total kinetic energy «at any given height» ✓<br>the cylinder has a smaller moment of inertia so a smaller fraction of its kinetic energy is rotational / a greater fraction is translational ✓<br>the cylinder has a greater linear speed «at every point on the ramp» so it takes a shorter time ✓ | *OWTTE*<br>*Do not award the third mark for "shorter time" without a reason.*<br>*Accept an argument using a greater linear acceleration for the cylinder for the third mark.*<br>*Accept a correct algebraic comparison of the speeds.* | 3 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `M = 12 kg`, `R = 0.15 m`, `h = 0.90 m`, `k = 1` (`I = k*M*R**2`), sabit `g = 9.8 m/s^2` | |
| `v` | `sqrt(2*g*h/(1 + k))` | 2.97 m s⁻¹ |
| `omega` | `v/R` | 19.8 rad s⁻¹ |
| `I` | `k*M*R**2` | 0.270 kg m² |
| `L` | `I*omega` | 5.35 kg m² s⁻¹ |

"Show that" değeriyle (3.0 m s⁻¹): `omega` = 20 rad s⁻¹, `L` = 5.40 kg m² s⁻¹. (d) için denetim (öğrenciden istenmez): içi dolu
silindirde `k = 0.5`, `v` = 3.43 m s⁻¹ > 2.97 m s⁻¹.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + (şekil) + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–3 uygun (artan; N, rad s⁻¹); Soru 4 kesir, artan |
| 1A: doğru cevap konumu dengeli | C, B, A, D |
| 1A: olumsuz kök | Kullanılmadı |
| 1A: kök uzunluğu | Soru 1–3 yaklaşık 50–60 kelime; profildeki aralığın (8–90) içinde, ortancanın üstünde |
| Şekil | Soru 1 metinle tarif edildi; soru şekil olmadan da çözülebilir. Öğrenci sürümü için şekil üretilmeli |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (1, 3, 2, 3; toplam 9) |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanır | Soru 5 (b) → (c) uygun; (c) için kabul aralığı verildi |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, OWTTE | Soru 5 uygun |
| Değer–birim yazımı (rad s⁻¹, kg m² s⁻¹), 2 anlamlı basamak | Uygun; Soru 1'de veriler ve seçenekler 3 anlamlı basamak (200 N, 150 N, 375 N) |
| Kapsam sınırları (A.4) | Belirli şekillerin *I* formülü Soru 2, 4, 5'te verildi; Soru 3'te tablanın *I* değeri sayısal verildi, kil nokta kütle; dönme + öteleme yalnızca kaymadan yuvarlanma; vektörel işlem ve kütle merkezi hesabı yok |

## Bağımsız kontrol

Tarih: 2026-10-11. Kör çözücü, cevapları görmeden soruları çözdü ve tüm cevap anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti; KRİTİK ya da ORTA bulgu yok.
Ayrıntı: [review/a4-review.md](review/a4-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

Bulgular üzerine yapılan değişiklikler:

- Soru 5 (b) markscheme: iki alternatifi ayıran "/" bölme işareti gibi okunuyordu; "*Mgh* = *Mv*² **OR** *v* = √(*gh*)" olarak yeniden yazıldı.
- Soru 5 (b): hedef değer "about 3 m s⁻¹" → "about 3.0 m s⁻¹"; not "en az 3 anlamlı basamak (2.97)" oldu. (c) değerleri yeniden hesaplandı: 2.97 ile 5.35, 3.0 ile 5.40 kg m² s⁻¹; kabul aralığı değişmedi.
- Soru 5 (d) markscheme notuna "Accept a correct algebraic comparison of the speeds" eklendi.
- Soru 1'in anlamlı basamağı (200 N, 150 N, 375 N): incelemede değişiklik istenmedi; olduğu gibi bırakıldı.

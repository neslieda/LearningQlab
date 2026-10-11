# Pilot soru seti: D.3 Elektromanyetik alanlarda hareket

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
> D teması için istenen tek Paper 1B sorusu bu dosyadadır (Soru 6).
>
> **Kaynak:** yalnızca müfredat düğümü D.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; senaryolar yazarın kurgusudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar, tüm sayısal çeldiriciler ve Soru 6'daki en uygun / en büyük / en küçük eğimler `python3`
> (yalnızca standart kütüphane) ile ayrı bir hesapla yeniden üretildi ve dosyadaki değerlerle eşleşti. Kullanılan sabitler:
> e = 1.60 × 10⁻¹⁹ C, elektron kütlesi 9.11 × 10⁻³¹ kg, g = 9.8 m s⁻² (veri kitapçığı değerleri uzmanca teyit edilmeli).
> **Bağımsız kontrol:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi. Kör çözücü Soru 6(e)'de KRİTİK bir fizik hatası
> buldu; parça değiştirildi (bkz. dosya sonu).
> **Doğrulanmayan:** (1) uzman incelemesi yapılmadı; yeniden yazılan Soru 6(e) ve değişen Soru 5 sayıları ikinci bir kör çözücüden geçti ve uyuştu (review/recheck-2026-10-11.md); (2) kuvvet ve alan yönleri (Soru 3, Soru 5c) sağ el
> kuralı ve ayrıca vektörel çarpımla (F = qv × B, F = IL × B) elle kontrol edildi, kodla değil; (3) Soru 6'nın verisi yazar tarafından
> B = 0.080 T ve L = 0.050 m için üretilmiş, küçük saçılma eklenmiş kurgusal veridir; gerçek bir deneyden gelmez; (4) Soru 6'da
> ±0.04 g belirsizliğin (okumanın dalgalanması) gerçek bir terazi için makul olup olmadığı teyit edilmedi; (5) bilinen bir sınav
> sorusuna benzerlik açısından uzman gözüyle bakılmadı — hız seçici ve akım terazisi bilinen deney türleridir, soru metinleri özgündür.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (D.3) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Düzgün manyetik alanda çembersel hareket; periyodun hızdan bağımsızlığı | AO2 | — | 1 | Orta–zor |
| 2 | Paper 1A | SL | Birbirine dik elektrik ve manyetik alanlarda sapmadan geçiş (v = E/B) | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Akım taşıyan iletkene etkiyen kuvvetin yönü (F = BIL sin θ) | AO2 | — | 1 | Kolay–orta |
| 4 | Paper 1A | SL | Yüklü parçacığın düzgün elektrik alandaki hareketi | AO2 | — | 1 | Orta |
| 5 | Paper 2 | SL | Dik alanlar; düzgün manyetik alanda çembersel yörünge; yük/kütle oranının belirlenmesi | AO1–AO3 | Show that, Explain, Determine, State | 9 | Orta–zor |
| 6 | Paper 1B | SL | F = BIL deneyi (akım terazisi): belirsizlik, eğimden B'nin belirlenmesi, sıfır hatasının (sistematik) eğime ve kesim noktasına etkisi | AO2–AO3 | Outline, Calculate, Determine, Comment, Explain, Suggest | 10 | Orta–zor |

Bu set D.3'ün tamamını kapsamaz. Eksik kalanlar: F = qvB sin θ ile θ ≠ 90° durumunda hesap, paralel teller arasındaki kuvvet
(büyüklük ve yön), düzgün elektrik alanda sapmanın nicel hesabı, yüklü parçacığa etkiyen manyetik kuvvetin yönü (tek başına).

Kapsam sınırı kontrolü: D.3 için rehberde açık bir sınır yok. Parçacığın potansiyel farkıyla hızlandırılması (W = qΔV) D.2'nin ek HL
içeriği olduğundan bu SL dosyasında bilerek kullanılmadı; Soru 5'te hız, dik alanlar koşulundan bulunur. Türev ya da integral yok.

---

## Soru 1 — Paper 1A

A charged particle moves at right angles to a uniform magnetic field in a vacuum. The particle moves in a circle with period *T*.
An identical particle enters the same field at right angles with **twice** the speed.

What is the period of the motion of the second particle?

A. *T*/2
B. *T*
C. 2*T*
D. 4*T*

**Cevap: B**

**Çözüm.** qvB = mv²/r → r = mv/(qB). T = 2πr/v = 2πm/(qB): periyot hızdan bağımsızdır. Hız iki katına çıkınca yarıçap da iki katına
çıkar; çevre ve hız aynı oranda arttığı için periyot değişmez.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Yarıçapın değişmediği sanılır; aynı çember iki kat hızla dolanılır: T/2 |
| C | Yarıçapın iki katına çıktığı görülür ama hızın da arttığı unutulur (T ∝ r): 2T |
| D | Yarıçap v² ile artar sanılır (r ∝ v², mv²/r ifadesinden yanlış çıkarım) ve hız artışı unutulur: 4T |

---

## Soru 2 — Paper 1A

A beam of electrons passes between two parallel plates that are 2.0 cm apart. The potential difference between the plates is 600 V.
A uniform magnetic field of strength 1.5 mT is applied at right angles to both the electric field and the beam. The electrons pass
between the plates without being deflected.

What is the speed of the electrons?

A. 5.0 × 10⁻⁸ m s⁻¹
B. 2.0 × 10⁵ m s⁻¹
C. 4.0 × 10⁵ m s⁻¹
D. 2.0 × 10⁷ m s⁻¹

**Cevap: D**

**Çözüm.** E = V/d = 600 / 0.020 = 3.0 × 10⁴ V m⁻¹. Sapmama koşulu: eE = evB → v = E/B = 3.0 × 10⁴ / 1.5 × 10⁻³ = 2.0 × 10⁷ m s⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Oran ters kurulur (v = B/E): 1.5 × 10⁻³ / 3.0 × 10⁴ = 5.0 × 10⁻⁸ |
| B | Levha aralığı metreye çevrilmez: E = 600 / 2.0 = 300; 300 / 1.5 × 10⁻³ = 2.0 × 10⁵ |
| C | Alan şiddeti yerine potansiyel farkı kullanılır (v = V/B): 600 / 1.5 × 10⁻³ = 4.0 × 10⁵ |

---

## Soru 3 — Paper 1A

A straight horizontal wire lies in the plane of the page and carries a current directed towards the right of the page. The wire is in
a uniform magnetic field that is directed **into** the page.

> **Şekil:** Sayfa düzleminde soldan sağa uzanan yatay bir tel; üzerinde sağa doğru akım oku (*I*). Telin çevresindeki bölge, sayfanın
> içine doğru düzgün manyetik alanı gösteren ⊗ simgeleriyle dolu. "Sayfanın üstü" tele dik ve sayfa düzlemindedir. Diagram not to scale.

What is the direction of the magnetic force on the wire?

A. towards the top of the page
B. towards the bottom of the page
C. out of the page
D. into the page

**Cevap: A**

**Çözüm.** Kullanılan kural: sağ el kuralı, F = IL × B (konvansiyonel akım yönü). Eksenler: x sağa, y sayfanın üstüne, z sayfadan
dışarı. Akım +x, alan −z: (+x) × (−z) = +y. Kuvvet sayfanın üstüne doğrudur. (Fleming sol el kuralı da aynı sonucu verir: işaret
parmağı alan = sayfanın içine, orta parmak akım = sağa, başparmak kuvvet = yukarı.)

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Kural ters elle uygulanır ya da akım yönü yerine elektron akış yönü alınır |
| C | Kuvvetin alana zıt yönde olduğu sanılır |
| D | Kuvvetin alan yönünde olduğu sanılır (elektrik alandaki F = qE ile karıştırma) |

---

## Soru 4 — Paper 1A

An electron enters a region of uniform electric field in a vacuum. The initial velocity of the electron is at right angles to the
electric field lines. There is no magnetic field.

Which describes the path of the electron in the field and the speed of the electron?

A. The path is a circular arc and the speed is constant.
B. The path is a circular arc and the speed increases.
C. The path is a parabola and the speed increases.
D. The path is a parabola and the speed is constant.

**Cevap: C**

**Çözüm.** Elektrik kuvveti büyüklük ve yön olarak sabittir (alan çizgilerine paralel, alana zıt yönde). Alana dik hız bileşeni
değişmez, alan doğrultusundaki bileşen düzgün artar: yörünge paraboldür (yatay atışa benzer). Kuvvet hareket doğrultusunda bileşene
sahip olduğu için iş yapar; sürat artar.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Elektrik alan, manyetik alanla karıştırılır (kuvvet her zaman hıza dik sanılır) |
| B | Yörünge manyetik alandaki gibi çember sanılır, ama alanın enerji verdiği doğru düşünülür |
| D | Yörünge doğru; ancak yalnızca alana dik hız bileşeni düşünülür ya da "kuvvet başlangıçta hıza dik, iş yapmaz" denir |

---

## Soru 5 — Paper 2 (9 puan)

A beam of electrons travels in a vacuum from left to right between two horizontal parallel plates. The plates are 2.5 cm apart and
the potential difference between them is 460 V. The upper plate is positive. A uniform magnetic field of strength 0.80 mT is applied
in the region between the plates, at right angles to the beam and to the electric field. The beam passes between the plates without
being deflected.

> **Şekil:** Sayfa düzleminde iki yatay paralel levha; üstteki "+", alttaki "−" işaretli; aralarındaki uzaklık 2.5 cm olarak
> etiketli. Elektron demeti levhaların ortasından soldan sağa doğru yatay bir okla gösterilmiş. Elektrik alan çizgileri üst levhadan
> alt levhaya (sayfanın altına doğru). Manyetik alanın yönü şekilde **gösterilmemiştir**; sayfa düzlemine diktir. Diagram not to scale.

**(a)** Show that the speed of the electrons is about 2.3 × 10⁷ m s⁻¹. [2]

**(b)** State the direction of the magnetic field. [1]

The potential difference between the plates is now reduced to zero. The magnetic field is unchanged. The beam follows a circular arc
of radius 0.16 m.

**(c)** Explain why the path of the electrons in the magnetic field is circular. [2]

**(d)** Determine the charge-to-mass ratio of the electron given by these measurements. [2]

The potential difference of 460 V is restored. The electrons are replaced by protons that enter the region with the same velocity as
the electrons.

**(e)** Explain whether the protons are deflected. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *E* = *V*/*d* = 460 / 0.025 «= 1.84 × 10⁴ V m⁻¹» ✓<br>«*eE* = *evB* so» *v* = *E*/*B* = 1.84 × 10⁴ / 0.80 × 10⁻³ = 2.30 × 10⁷ «m s⁻¹» ✓ | *The full substitution or the answer to 3 s.f. must be shown.* | 2 |
| 5. | b | | into the «plane of the» page ✓ | | 1 |
| 5. | c | | the «magnetic» force is always perpendicular to the velocity ✓<br>so the speed is constant / no work is done **AND** the force «of constant magnitude» acts as a centripetal force ✓ | *OWTTE* | 2 |
| 5. | d | | *evB* = *mv*²/*r* **OR** *e*/*m* = *v*/(*Br*) ✓<br>*e*/*m* = 2.3 × 10⁷ / (0.80 × 10⁻³ × 0.16) = 1.8 × 10¹¹ «C kg⁻¹» ✓ | *Allow ECF from (a).* | 2 |
| 5. | e | | both the electric force and the magnetic force reverse direction «as the charge has opposite sign» **OR** both forces have the same magnitude as before «same *E*, *v*, *B* and magnitude of charge» **AND** are still in opposite directions ✓<br>the forces still balance / *v* = *E*/*B* does not depend on charge or mass, so the protons are not deflected ✓ | *OWTTE*<br>*Award [0] for "not deflected" without reasoning.* | 2 |

**Yön çözümü (b).** Eksenler: x sağa (hız), y sayfanın üstüne, z sayfadan dışarı. E alanı −y (artı levhadan eksi levhaya). Elektron
(q = −e) üzerindeki elektrik kuvveti +y (artı levhaya doğru). Sapmama için manyetik kuvvet −y olmalı: F = qv × B = (−e)(v x̂ × B).
B = −z (sayfanın içine) için x̂ × (−ẑ) = +ŷ, (−e) ile çarpılınca −ŷ. Dolayısıyla alan sayfanın içine doğrudur. Sağ el kuralıyla kontrol:
artı yük için v sağa, B içeri → kuvvet yukarı; elektron için ters, yani aşağı. ✓

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `V = 460 V`, `d = 0.025 m`, `B = 0.80e-3 T`, `r = 0.16 m` | |
| `E` | `V/d` | 1.84 × 10⁴ V m⁻¹ |
| `v` | `E/B` | 2.30 × 10⁷ m s⁻¹ |
| `e_over_m` | `v/(B*r)` | 1.80 × 10¹¹ C kg⁻¹ |
| Tutarlılık kontrolü | `m_e*v/(e*B)` (e = 1.60e-19, m_e = 9.11e-31) | r = 0.164 m; soruda iki anlamlı basamakla 0.16 m verildi, bu yüzden bulunan e/m kabul edilen değerden (1.76 × 10¹¹ C kg⁻¹) yaklaşık %2 büyük |

---

## Soru 6 — Paper 1B (10 puan)

A student investigates the force on a current-carrying wire in a magnetic field. Two flat magnets are fixed to a steel yoke so that
there is an approximately uniform horizontal magnetic field between them. The yoke is placed on an electronic balance. A stiff
straight horizontal wire is clamped so that it passes between the magnets at right angles to the field. The wire does not touch the
magnets or the balance. The balance is set to zero when there is no current in the wire.

> **Şekil:** Düzenek şeması. Elektronik terazinin kefesinde U biçimli çelik boyunduruk; boyunduruğun iki iç yüzünde karşılıklı
> düz mıknatıslar (N ve S etiketli), aralarındaki alan yatay. Yatay, sert bir tel mıknatısların arasından alana dik geçer; tel iki
> yandan teraziye değmeyen ayrı bir sehpaya kelepçelenmiş ve bir güç kaynağı ile ampermetreye seri bağlı. Telin alan içindeki
> uzunluğu *L* (mıknatısların uzunluğu) olarak etiketli. Diagram not to scale.

The student varies the current *I* in the wire and records the change in the balance reading Δ*m*. The direction of the current is
chosen so that the balance reading increases.

| *I* / A | Δ*m* / g ± 0.04 g |
|---|---|
| 1.0 | 0.41 |
| 2.0 | 0.83 |
| 3.0 | 1.21 |
| 4.0 | 1.64 |
| 5.0 | 2.05 |

The uncertainty in *I* is negligible. The length of the wire in the field is *L* = (5.0 ± 0.1) cm.

**(a)** Outline why the balance reading changes when there is a current in the wire. [2]

**(b)** Calculate the percentage uncertainty in Δ*m* for *I* = 1.0 A. [1]

The student plots Δ*m* against *I* with uncertainty bars. The gradient of the line of best fit is 0.41 g A⁻¹. The lines of maximum
and minimum gradient have gradients of 0.43 g A⁻¹ and 0.39 g A⁻¹. Theory predicts that Δ*m* = *BIL*/*g*, where *B* is the magnetic
field strength between the magnets and *g* = 9.8 m s⁻².

**(c)** Determine *B*, with its absolute uncertainty. [3]

**(d)** The manufacturer states that the magnetic field strength between the magnets is 0.083 T. Comment on whether the result of
the experiment is consistent with this value. [1]

**(e)** A second student repeats the experiment but does **not** set the balance to zero. With no current in the wire the balance
reads a constant 0.15 g. This student plots the balance reading against *I* and determines *B* from the gradient of the graph.
Explain the effect of this on the value of *B* obtained. [2]

**(f)** Suggest **one** change to the experiment that would reduce the percentage uncertainty in *B*. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | the magnetic field exerts a «vertical» force on the current-carrying wire ✓<br>the wire exerts an equal and opposite force on the magnets «Newton's third law», which changes the force on the balance ✓ | *OWTTE* | 2 |
| 6. | b | | «0.04 / 0.41 × 100 =» 10 «%» ✓ | *Accept 9.8 %.* | 1 |
| 6. | c | | *B* = gradient × *g* / *L* = 0.41 × 10⁻³ × 9.8 / 0.050 = 0.080 «T» ✓<br>fractional uncertainty = 0.02/0.41 + 0.1/5.0 «= 0.049 + 0.020 = 0.069» ✓<br>*B* = (0.080 ± 0.006) «T» ✓ | *MP2: uncertainty in gradient is (0.43 − 0.39)/2 = 0.02 g A⁻¹.*<br>*Award [2] max if the gradient is not converted to kg A⁻¹ «80 T».* | 3 |
| 6. | d | | consistent, as 0.083 T lies within the range 0.074 T to 0.086 T ✓ | *Allow ECF from (c): the conclusion must follow from the candidate's own range.*<br>*Reasoning using the range is required.* | 1 |
| 6. | e | | every reading is larger by the same amount «0.15 g» / the line is shifted upwards / the intercept is no longer zero «systematic / zero error» ✓<br>the gradient is unchanged, so the value of *B* obtained is not affected ✓ | *OWTTE*<br>*Do not award MP2 for "no effect" without reference to the gradient.* | 2 |
| 6. | f | | use larger currents **OR** a longer length of wire in the field / longer magnets **OR** several turns of wire through the field «so that Δ*m* is larger» **OR** a balance with smaller uncertainty **OR** measure *L* with a more precise instrument ✓ | *Do not accept "repeat readings" without stating that a mean is taken.* | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `grad = 0.41e-3 kg/A`, `grad_max = 0.43e-3`, `grad_min = 0.39e-3`, `L = 0.050 m`, `dL = 0.001 m`, `u_dm = 0.04 g`, sabit `g = 9.8` | |
| `pct_dm` | `100*0.04/0.41` | %9.8 ≈ %10 |
| `B` | `grad*g/L` | 0.0804 T |
| `u_grad` | `(grad_max - grad_min)/2` | 0.02 × 10⁻³ kg A⁻¹ |
| `frac` | `u_grad/grad + dL/L` | 0.0488 + 0.0200 = 0.0688 |
| `u_B` | `B*frac` | 0.0055 T ≈ 0.006 T |
| Aralık | `B*(1-frac)`, `B*(1+frac)` | 0.0748 T – 0.0859 T (yuvarlanmış değerlerle 0.074–0.086 T) |
| (d) sağlamlık | 0.083 T; belirsizlik ±0.004, ±0.005, ±0.0055, ±0.006 T için aralıklar | 0.076–0.084, 0.075–0.085, 0.0749–0.0859, 0.074–0.086 T: hepsinde içeride |
| (e) sıfır hatası | tüm okumalara 0.15 g eklenip en küçük kareler doğrusu yeniden hesaplanır | eğim 0.409 g A⁻¹ (değişmez), kesim noktası 0.151 g |

### Şekil notu

Öğrenciye gösterilecek sürümde tablo ile birlikte belirsizlik çubuklu Δ*m*–*I* grafiği yer alır. Grafik aynı veriden kodla üretilir
(D-14). Tablodaki veriden hesaplanan en küçük kareler eğimi 0.409 g A⁻¹ (kesim noktası 0.001 g); ilk ve son noktanın belirsizlik
çubuklarının uçlarından geçen doğruların eğimleri 0.430 ve 0.390 g A⁻¹'dir ve bu iki doğru beş noktanın tümünün belirsizlik
çubuklarının içinden geçer (python ile kontrol edildi). Soruda verilen 0.41, 0.43 ve 0.39 değerleri bunların iki anlamlı basamağa
yuvarlanmış halidir.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi + alt alta A–D | Soru 1–3 "What is …?"; Soru 4 "Which …?" (profilde daha seyrek ama geçerli) |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–2 uygun (artan); Soru 3 yön ifadeleri; Soru 4 aynı kalıpta dört cümle (cümle biçimli seçenek profilde azınlıkta) |
| 1A: kritik sözcük koyu | Soru 1 ("twice"), Soru 3 ("into") |
| 1A: tablo seçenekli biçim örnekte doğrulanamadı | Soru 4 bu yüzden iki sütunlu tablo yerine cümle seçenekleriyle yazıldı |
| 1A: doğru cevap konumu dengeli | B, D, A, C |
| 1A: seçenekler yuvarlamadan sonra birbirinden farklı | Kontrol edildi (python) |
| Şekil | Soru 3, 5, 6: metinle tarif edildi; alan ve akım yönleri sözle de verildi. Soru 5(b)'de manyetik alan yönü bilerek gösterilmedi (istenen odur) |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 1, 2, 2, 2; toplam 9). SL örnek kâğıdında kısa sorular 4–6 puan; 9 puan HL aralığının üst sınırı — SL kâğıdı için iki soruya bölünebilir |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanabilir | Soru 5(a) → (d) uygun |
| Paper 2: en az bir AO3 parça | Soru 5(a) Show that, (c) ve (e) Explain, (d) Determine |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE | Soru 5 ve Soru 6 uygun |
| 1B: yaklaşık 10 puanlık deney sorusu, alt parçalar 1–3 puan | Soru 6 uygun (2, 1, 3, 1, 2, 1; toplam 10); (e) parçası değiştirildi, puanı ve toplam aynı kaldı |
| 1B: tablo başlığı "büyüklük / birim ± belirsizlik" | Soru 6 uygun |
| 1B: komut sözcükleri | Outline, Calculate, Determine, Explain, Suggest profilde var; "Comment" profildeki listede yok (A.1 örneğinde kullanıldığı için korundu) — uzman teyidi gerekir |
| 1B: öğrenci verilen grafiğe en uygun doğruyu çizer ve eğimi kendisi bulur | **Soru 6 uygun değil:** grafik üretilemediği için eğimler metinde verildi. Grafik şablonu hazır olunca (c) parçası yeniden yazılmalı |
| Değer–birim yazımı (m s⁻¹, g A⁻¹, C kg⁻¹), 2 anlamlı basamak | Uygun |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından farklı bir kör çözücü tarafından cevaplar görülmeden çözüldü. Soru 6(e) dışındaki tüm cevap
anahtarları, çeldirici değerleri, yön çözümleri (Soru 3, 5b) ve Soru 6'daki eğimler bağımsız olarak yeniden üretildi ve eşleşti.
**Soru 6(e) eşleşmedi ve değiştirildi.** Ayrıntı: [review/d3-review.md](review/d3-review.md). Bu kontrol uzman incelemesinin yerine
geçmez; değiştirilen parçalar ikinci bir kör çözümden geçmedi.

İncelemeye yanıt olarak yapılan değişiklikler:

- **Soru 6(e) — KRİTİK, parça değiştirildi.** Eski parça "tel alana tam dik değilse B'ye etkisi"ni soruyor, anahtar "kuvvet ve eğim
  küçülür, B küçük bulunur" diyordu. Yazar türetmeyi yeniden yaptı ve inceleyenle aynı sonuca vardı: tel düzdür ve uzunluğu *L* olan
  alan bölgesini baştan sona geçer; alanla θ açısı yaparsa alan içindeki uzunluğu *L*/sin θ olur ve
  F = BI(*L*/sin θ) sin θ = BIL değişmez (tel düşey düzlemde eğilse de kuvvetin düşey bileşeni yine BIL'dir). Eski anahtar yanlıştı;
  doğru düşünen öğrenci sıfır alırdı. Yeni parça: terazi sıfırlanmamıştır ve akım yokken sabit 0.15 g gösterir; öğrenci kesim
  noktasının kaydığını ama eğimin, dolayısıyla B'nin değişmediğini açıklar (2 puan, AO3). Kapsam tablosu güncellendi; puan toplamı
  10 olarak kaldı. `python3`: tüm okumalara 0.15 g eklenince eğim 0.409 g A⁻¹ (aynı), kesim noktası 0.151 g.
- **Soru 6(d) — ORTA.** Üretici değeri 0.085 T → 0.083 T. Eski değer sonuç aralığının sınırındaydı ve varılan yargı belirsizliğin
  nasıl yuvarlandığına bağlıydı. `python3`: 0.083 T, ±0.004, ±0.005, ±0.0055 ve ±0.006 T'nin hepsinde aralığın içinde. Nota
  "the conclusion must follow from the candidate's own range" eklendi; 6(c)'deki "Allow ± 0.005 T" notu kaldırıldı.
- **Soru 5(a):** levhalar arası potansiyel farkı 450 V → 460 V. Eski hız 2.25 × 10⁷ m s⁻¹, "about 2.3 × 10⁷" hedefinde yuvarlama
  sınırındaydı; yeni değer tam 2.30 × 10⁷ m s⁻¹. Buna bağlı olarak (d) sonucu 1.76 × 10¹¹ → 1.80 × 10¹¹ C kg⁻¹ (anahtar yine
  1.8 × 10¹¹), kabul aralığı notu ECF notuna indirildi, formül zinciri güncellendi.
- **Soru 5(e) markscheme:** MP1'in ikinci alternatifi artık yönleri de ister ("… **AND** are still in opposite directions").
- **Değiştirilmeyen:** Soru 5'in 9 puanlık SL kısa soru olması (istenen 4–9 aralığında; "Biçim uyumu" tablosunda bölünebileceği
  yazılı) ve Soru 6(d)'deki "Comment" komut sözcüğü (A.1 örneğiyle tutarlı). İkisi de uzman kararı bekliyor.

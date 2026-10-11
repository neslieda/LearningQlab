# Pilot soru seti: C.3 Dalga olayları

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneği](a1-kinematics-pilot-questions.md) ile aynı yapıda yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü C.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgündür.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile yeniden hesaplandı.
> Sabitler: havada ses hızı 340 m s⁻¹ (soruda verildi). Kırılma indisleri (plastik 1.6, su 1.3) ve lazer dalga boyu (633 nm) gerçekçi
> değerlerdir ve soruda verilir.
> **Doğrulanmayan:** (1) bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; (2) bilinen bir sınav sorusuna benzerlik açısından uzman
> gözüyle bakılmadı; (3) "yalnızca dik geliş" sınırı bu sette yarık ve ağ sorularına (Soru 2, 4, 5, 6) uygulandı; Snell yasası ve kritik
> açı doğası gereği eğik geliş içerdiğinden Soru 1 bu sınırın dışında sayılmadı — bu yorum uzmanca teyit edilmeli; (4) Soru 6 (c)(ii)'de
> beşinci mertebe saçak merkezî maksimumun dışında (ikincil maksimumda) kalır; sınır durumu bilerek önlendi; (5) nitel
> parçalar (Soru 6 a ve d) kodla doğrulanamaz.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (C.3) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Kritik açı; iki saydam ortam arasında tam yansıma | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | Çift yarık; s = λD/d ile orantı | AO2 | — | 1 | Kolay |
| 3 | Paper 1A | SL | Eşfazlı kaynaklar; yol farkı ve yıkıcı girişim koşulu | AO3 | — | 1 | Orta |
| 4 | Paper 1A | HL | Kırınım ağı; gözlenebilen en yüksek mertebe | AO2 | — | 1 | Orta |
| 5 | Paper 1A | HL | Tek yarık kırınımı; θ = λ/b ve merkezî maksimumun genişliği | AO2 | — | 1 | Orta |
| 6 | Paper 2 | HL | Yapıcı girişim; s = λD/d; tek yarığın çift yarık desenini biçimlendirmesi; çoklu yarık | AO2–AO3 | Explain, Show that, Calculate, Determine, State | 9 | Orta–zor |

Bu set C.3'ün tamamını kapsamaz. Eksik kalanlar: dalga cephesi ve ışın çizimi; yansıma ve iletim; Snell yasasıyla kırılma açısı ve
kırılmada hız–dalga boyu değişimi; açıklık ve engelde kırınımın nitel anlatımı; tek yarık şiddet deseninin taslağı; yarık genişliğinin
şiddete nitel etkisi; kırınım ağında açı hesabı (nλ = d sin θ).

---

## Soru 1 — Paper 1A

Light travels in a transparent plastic of refractive index 1.6. The light is incident on a boundary between the plastic and water.
The refractive index of water is 1.3.

What is the critical angle for light at this boundary?

A. 36°
B. 39°
C. 50°
D. 54°

**Cevap: D**

**Çözüm.** n₁ sin θ<sub>c</sub> = n₂ sin 90° → sin θ<sub>c</sub> = 1.3 / 1.6 = 0.8125 → θ<sub>c</sub> = 54.3° ≈ 54°.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Açı normalden değil yüzeyden ölçülür: 90° − 54.3° = 35.7° ≈ 36° |
| B | İkinci ortam hava sanılır: sin⁻¹(1 / 1.6) = 38.7° ≈ 39° |
| C | Suyun hava ile sınırındaki kritik açısı alınır: sin⁻¹(1 / 1.3) = 50.3° ≈ 50° |

---

## Soru 2 — Paper 1A

Monochromatic light is incident normally on two narrow parallel slits. Fringes are observed on a distant screen. The separation of
adjacent bright fringes is 2.0 mm. The separation of the slits is then doubled and the distance from the slits to the screen is
increased to three times its original value.

What is the new separation of adjacent bright fringes?

A. 0.33 mm
B. 1.3 mm
C. 3.0 mm
D. 12 mm

**Cevap: C**

**Çözüm.** s = λD / d. D üç katına, d iki katına çıkar: s yeni = 2.0 × 3 / 2 = 3.0 mm.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | s hem D hem d ile ters orantılı alınır: 2.0 / (3 × 2) = 0.33 mm |
| B | D ve d'nin rolleri değiştirilir (s ∝ d / D): 2.0 × 2 / 3 = 1.3 mm |
| D | s hem D hem d ile doğru orantılı alınır: 2.0 × 3 × 2 = 12 mm |

---

## Soru 3 — Paper 1A

Two loudspeakers X and Y emit sound of the same frequency and are in phase. A microphone is placed at a point P that is 2.00 m from
X and 2.68 m from Y. The speed of sound in air is 340 m s⁻¹.

What is the lowest frequency for which the intensity of the sound at P is a minimum?

A. 125 Hz
B. 250 Hz
C. 500 Hz
D. 750 Hz

**Cevap: B**

**Çözüm.** Yol farkı = 2.68 − 2.00 = 0.68 m. Yıkıcı girişim için yol farkı = (n + ½)λ; en düşük frekans en büyük dalga boyuna karşılık
gelir: λ/2 = 0.68 m → λ = 1.36 m → f = 340 / 1.36 = 250 Hz.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Yıkıcı girişim için yol farkı çeyrek dalga boyu alınır: λ = 2.72 m → 340 / 2.72 = 125 Hz |
| C | Yapıcı girişim koşulu kullanılır (yol farkı = λ): 340 / 0.68 = 500 Hz |
| D | Bir sonraki minimum alınır (yol farkı = 3λ/2); bu frekansta da minimum vardır ama en düşük değildir: 3 × 340 / (2 × 0.68) = 750 Hz |

---

## Soru 4 — Paper 1A

Monochromatic light of wavelength 600 nm is incident normally on a diffraction grating that has 400 lines per millimetre.

What is the highest order of maximum that can be observed?

A. 4
B. 5
C. 8
D. 9

**Cevap: A**

**Çözüm.** d = 1.0 × 10⁻³ / 400 = 2.5 × 10⁻⁶ m. nλ = d sin θ ve sin θ ≤ 1 → n ≤ d / λ = 2.5 × 10⁻⁶ / (600 × 10⁻⁹) = 4.17. En yüksek tam
sayı 4'tür (sin θ₄ = 0.96).

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | 4.17 yukarı yuvarlanır; n = 5 için sin θ = 1.2 > 1 olur, bu mertebe oluşmaz |
| C | Merkezin iki yanındaki maksimumların sayısı verilir: 2 × 4 = 8 |
| D | Ekranda görülen toplam maksimum sayısı verilir: 2 × 4 + 1 = 9 |

---

## Soru 5 — Paper 1A

Monochromatic light of wavelength 600 nm is incident normally on a single rectangular slit of width 0.10 mm. A diffraction pattern
is observed on a screen that is 2.0 m from the slit.

What is the width of the central maximum on the screen?

A. 6.0 mm
B. 12 mm
C. 24 mm
D. 48 mm

**Cevap: C**

**Çözüm.** İlk minimumun açısı θ = λ / b = 600 × 10⁻⁹ / (0.10 × 10⁻³) = 6.0 × 10⁻³ rad. Merkezden ilk minimuma uzaklık = θD =
6.0 × 10⁻³ × 2.0 = 12 mm. Merkezî maksimum iki yandaki ilk minimumlar arasındadır: 2 × 12 = 24 mm.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | İlk minimum için θ = λ / 2b alınır (çift yarıktaki yarım dalga boyu koşuluyla karıştırma) ve iki katı alınmaz: 6.0 mm |
| B | Merkezden ilk minimuma uzaklık (yarı genişlik) verilir: λD / b = 12 mm |
| D | İki katına alma iki kez uygulanır: 4λD / b = 48 mm |

---

## Soru 6 — Paper 2 (9 puan)

A technician tests a metal foil in which two narrow parallel slits have been cut. Light of wavelength 633 nm from a laser is
incident normally on the foil. A pattern of bright and dark fringes is observed on a screen that is 3.0 m from the foil.

> **Şekil:** Soldan gelen lazer demeti, iki paralel yarığı olan ince bir levhaya dik düşer; levhanın 3.0 m sağında levhaya paralel bir
> ekran. Ekranda eşit aralıklı parlak saçaklar; merkezî saçak işaretli. "diagram not to scale". Soru şekil olmadan çözülebilir.

**(a)** Explain how a bright fringe is formed on the screen. [2]

The distance on the screen between the centre of the central bright fringe and the centre of the fourth bright fringe from it is
15.2 mm.

**(b)** Show that the separation of the slits is about 0.5 mm. [2]

Each slit has a width of 0.11 mm. The intensity of the double-slit fringes is modulated by the single-slit diffraction pattern of
each slit. Use a slit separation of 0.50 mm.

**(c)** (i) Calculate the angle between the centre of the pattern and the first minimum of the single-slit diffraction pattern. [1]

 (ii) Determine the number of bright fringes that are observed within the central maximum of the single-slit diffraction
pattern. [3]

The foil is replaced by a foil that has many parallel slits with the same separation and the same width.

**(d)** State **one** change in the appearance of the bright fringes. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | light from the two slits is coherent **AND** superposes / interferes «at the screen» ✓<br>path difference is a whole number of wavelengths / waves arrive in phase, so the interference is constructive ✓ | *OWTTE*<br>*Accept "zero phase difference" for "in phase".* | 2 |
| 6. | b | | *s* = 15.2 / 4 = 3.8 «mm» ✓<br>*d* = 633 × 10⁻⁹ × 3.0 / 3.8 × 10⁻³ **OR** 5.0 × 10⁻⁴ «m» ✓ | *Answer must be seen to at least 2 s.f. or the substitution must be shown.* | 2 |
| 6. | c | i | *θ* = 633 × 10⁻⁹ / 0.11 × 10⁻³ = 5.8 × 10⁻³ «rad» ✓ | *Accept 0.33°.* | 1 |
| 6. | c | ii | angular separation of fringes = *λ* / *d* = 1.27 × 10⁻³ «rad» **OR** ratio *d* / *b* = 4.5 seen ✓<br>fringes of order up to 4 lie inside the central maximum «4 × 1.27 × 10⁻³ < 5.8 × 10⁻³ < 5 × 1.27 × 10⁻³» ✓<br>9 «bright fringes» ✓ | *Allow ECF from (c)(i).*<br>*Accept width of central maximum ÷ fringe separation:* 2 × 3.0 × 5.75 × 10⁻³ = 34.5 mm; 34.5 / 3.8 = 9.1, *giving 9.*<br>*Award [2 max] for an answer of 4 (one side only), 8 (central fringe omitted) or 11 (fifth order included).* | 3 |
| 6. | d | | bright fringes are narrower / sharper **OR** brighter / more intense ✓ | *Accept "fringes stay at the same positions" only if a change in width or intensity is also stated.* | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `lam = 633e-9 m`, `D = 3.0 m`, `y4 = 15.2e-3 m`, `b = 0.11e-3 m`, `d_given = 0.50e-3 m` | |
| `s` | `y4/4` | 3.8 × 10⁻³ m |
| `d` | `lam*D/s` | 5.00 × 10⁻⁴ m |
| `theta_1` | `lam/b` | 5.75 × 10⁻³ rad (0.33°) |
| `dtheta` | `lam/d_given` | 1.27 × 10⁻³ rad |
| `ratio` | `theta_1/dtheta` (= `d_given/b`) | 4.55 → zarfın içindeki en yüksek mertebe 4 |
| `N` | `2*floor(ratio) + 1` | 9 |
| Denetim (genişlik yolu) | `2*D*theta_1/(lam*D/d_given)` | 34.5 mm / 3.80 mm = 9.09 → 9 |

Yarık genişliği bilerek *d*/*b* tam sayı olmayacak biçimde seçildi (4.55): beşinci mertebe (6.33 × 10⁻³ rad) ilk minimumun
(5.75 × 10⁻³ rad) dışında, ikincil maksimumda kalır; mertebe sayma ve genişlik ÷ aralık yolları aynı sonucu (9) verir. (b)'de ölçüm
dördüncü saçağa kadar yapılır; bu saçak merkezî maksimumun içindedir (şiddeti düşüktür, merkezî saçağın yaklaşık %2'si).

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–5 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–5 uygun (artan) |
| 1A: doğru cevap harfleri dengeli | D, C, B, A, C |
| 1A: şekil olmadan çözülebilir | Soru 1–5 şekil gerektirmez |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 6 uygun (2, 2, 1, 3, 1; toplam 9) |
| Paper 2: "Show that" kalıbı ve en az bir AO3 parçası | Soru 6 (a) Explain, (b) Show that, (c)(ii) Determine; (c) verilen 0.50 mm değerini kullanır |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE | Soru 6 uygun |
| Paper 2: şekil | **Eksik:** düzenek yalnızca sözle tarif edildi; şiddet deseni grafiği yok |
| Müfredat sınırı: dik geliş; tek renkli ışık ve dikdörtgen yarık; yarık genişliğinin şiddete etkisi nitel | Soru 2, 4, 5, 6 "incident normally"; Soru 5 "single rectangular slit"; şiddet hesabı sorulmadı |
| Düzey etiketi | Soru 4, 5, 6 HL (kırınım ağı, tek yarık, modülasyon, çoklu yarık); Soru 1–3 SL |
| Değer–birim yazımı, 2 anlamlı basamak | Uygun; Soru 3'te uzaklıklar 3 anlamlı basamak (yol farkı 0.68 m iki anlamlı basamak kalsın diye) |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, cevapları görmeyen bağımsız bir kör çözücü tarafından çözüldü; çözücü tüm cevap
anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti (KRİTİK bulgu yok). Bulgular:
[review/c3-review.md](review/c3-review.md). Bu, uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile, dosyanın son metni üzerinden yeniden denetlendi):

- **Soru 6 (c) (ORTA):** yarık genişliği 0.10 mm → 0.11 mm. Böylece *d*/*b* 5.0 (sınır durumu; 9, 10 ve 11 cevaplarının üçü de doğal) → 4.55 oldu; mertebe sayma ve genişlik ÷ saçak aralığı yollarının ikisi de 9 verir.
- **Soru 6 (c)(i):** 6.3 × 10⁻³ rad (0.36°) → 5.8 × 10⁻³ rad (0.33°).
- **Soru 6 (c)(ii):** cevap 9 olarak kaldı; markscheme'in ikinci maddesi "fifth-order fringe is missing" → "fringes of order up to 4 lie inside the central maximum"; genişlik ÷ aralık yolu (34.5 / 3.8 = 9.1) kabul notu olarak eklendi; [2 max] notu güncellendi. Formül zinciri ve durum notu (4) buna göre değişti.
- **Değişmeyen:** (b) ve 15.2 mm verisi; Soru 5'teki (Paper 1A) 0.10 mm'lik yarık ayrı bir sorudur ve aynı kaldı.
- **Uygulanmayan:** Soru 6 (a)'da "coherent" koşulunun ayrı bir kabul notuna taşınması ve Soru 4'ün C/D çeldiricileri. İncelemede "şüphe" olarak geçiyor ve değişiklik zorunlu görülmüyor; uzman kararına bırakıldı.

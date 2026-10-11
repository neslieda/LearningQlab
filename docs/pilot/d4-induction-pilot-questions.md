# Pilot soru seti: D.4 İndüksiyon

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
> D.4 yalnızca HL düğümüdür; bu dosyadaki tüm sorular HL etiketlidir.
>
> **Kaynak:** yalnızca müfredat düğümü D.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; senaryolar yazarın kurgusudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Bu dosyada fiziksel sabit kullanılmadı.
> **Bağımsız kontrol:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. dosya sonu).
> **Doğrulanmayan:** (1) uzman incelemesi yapılmadı; (2) indüklenen akım ve kuvvet yönleri (Soru 2) Lenz
> yasası, sağ el kavrama kuralı ve ayrıca F = IL × B vektörel çarpımıyla elle kontrol edildi, kodla değil; (3) Soru 4, tepe emk'nin
> dönme frekansıyla doğru orantılı olduğu bilgisini ister — müfredat analizindeki "dönme frekansının etkisi" kazanımına dayanır;
> ε₀ = NBAω ifadesinin veri kitapçığında olup olmadığı teyit edilmedi, bu yüzden soru yalnızca oran ister; (4) Soru 5'te 0.40 T'lik
> düzgün alanın 0.20 m genişlikte bir bölgede elde edilebilirliği (güçlü kalıcı mıknatıs dizisi) gerçekçilik açısından teyit edilmedi;
> (5) bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (D.4) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Alana giren dikdörtgen bobinde emk (ε = BvL, N sarım) | AO2 | — | 1 | Orta |
| 2 | Paper 1A | HL | Lenz yasası: indüklenen akımın ve kuvvetin yönü | AO2 | — | 1 | Orta–zor |
| 3 | Paper 1A | HL | Dönen bobinde akı bağlantısı ile emk arasındaki ilişki | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Dönme frekansının sinüzoidal emk'ye etkisi | AO2 | — | 1 | Orta |
| 5 | Paper 2 | HL | Hareketli iletkende emk; indüklenen akım ve kuvvet; Lenz yasası ve enerji korunumu; Faraday yasası | AO2–AO3 | Calculate, Determine, Show that, Explain | 9 | Orta–zor |

Bu set D.4'ün tamamını kapsamaz. Eksik kalanlar: manyetik akının tanımı ve açıya bağlı hesabı (Φ = BA cos θ), Faraday yasasıyla
akı–zaman verisinden emk hesabı, öz indüksiyonun nitel anlatımı, sinüzoidal emk grafiğinin çizimi.

Kapsam sınırı kontrolü: nicel işlem yalnızca alana giren dikdörtgen bobin / çerçevenin alana dik hareket eden kenarı için (Soru 1, 5);
dönen bobin soruları (Soru 3, 4) yalnızca nitel ilişki ve oran ister; öz indüksiyon, indüktans ve RL devresi yok; türev ya da integral
yok.

---

## Soru 1 — Paper 1A (HL)

A rectangular coil has 20 turns and sides of length 0.10 m and 0.20 m. The coil moves at a constant speed of 0.50 m s⁻¹ into a region
of uniform magnetic field of strength 0.30 T. The plane of the coil is at right angles to the field. The leading side of the coil has
length 0.10 m and is at right angles to the velocity. The coil is partly inside the field.

> **Şekil:** Sayfa düzleminde dikdörtgen bir bobin (kısa kenar 0.10 m düşey, uzun kenar 0.20 m yatay) sağa doğru *v* hızıyla
> hareket ediyor. Sağ tarafta, sayfaya dik düzgün manyetik alan bölgesi (⊗ simgeleri) düşey bir sınır çizgisiyle başlıyor. Bobinin
> sağdaki 0.10 m'lik kenarı alanın içinde, soldaki kenarı dışında. Diagram not to scale.

What is the emf induced in the coil?

A. 0.015 V
B. 0.12 V
C. 0.30 V
D. 0.60 V

**Cevap: C**

**Çözüm.** Yalnızca alan içindeki öndeki kenar akı çizgilerini keser. Her sarımda ε = BvL = 0.30 × 0.50 × 0.10 = 0.015 V; 20 sarım
seri olduğundan ε = 20 × 0.015 = 0.30 V. (Eşdeğer: akı bağlantısının değişim hızı N B L v.)

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Sarım sayısı unutulur: 0.30 × 0.50 × 0.10 = 0.015 V |
| B | Emk yerine tam akı bağlantısı hesaplanır (NBA): 20 × 0.30 × 0.10 × 0.20 = 0.12 |
| D | Hıza dik kenar yerine hıza paralel kenar kullanılır: 20 × 0.30 × 0.50 × 0.20 = 0.60 V |

---

## Soru 2 — Paper 1A (HL)

A rectangular conducting loop lies in the plane of the page. Part of the loop is in a region of uniform magnetic field that is
directed **into** the page. The loop is pulled to the right, out of the field region, at constant speed.

> **Şekil:** Sayfa düzleminde dikdörtgen bir iletken çerçeve. Sol tarafta, sayfanın içine doğru düzgün manyetik alan bölgesi
> (⊗ simgeleri) düşey bir sınır çizgisiyle bitiyor; sınırın sağında alan yok. Çerçevenin sol kenarı alanın içinde, sağ kenarı dışında.
> Çerçeveye sağa doğru bir hız oku (*v*) çizilmiş. Akım yönleri sayfaya bakan gözlemciye göre tanımlanır. Diagram not to scale.

Which describes the direction of the induced current in the loop, as seen by an observer looking at the page, and the direction of
the magnetic force on the loop?

A. The current is clockwise and the force is to the left.
B. The current is clockwise and the force is to the right.
C. The current is anticlockwise and the force is to the left.
D. The current is anticlockwise and the force is to the right.

**Cevap: A**

**Çözüm.** Çerçeve alandan çıkarken sayfanın içine doğru olan akı azalır. Lenz yasası: indüklenen akım bu azalmaya karşı koyar, yani
çerçevenin içinde sayfanın içine doğru alan oluşturur. Sağ el kavrama kuralı (parmaklar akım yönünde kıvrılır, başparmak halkanın
içindeki alanı gösterir): sayfanın içine doğru alan için akım saat yönündedir.
Kuvvet: saat yönündeki akım, alan içindeki sol kenarda sayfanın üstüne doğrudur (+y). F = IL × B = (+y) × (−z) = −x: sola doğru.
Üst ve alt kenarların alan içindeki parçalarına etkiyen kuvvetler eşit ve zıttır. Kuvvet harekete karşıdır; enerji korunumuyla uyumlu.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Akım yönü doğru; ancak kuvvetin hareketi desteklediği sanılır (enerji korunumuna aykırı) ya da el kuralı ters uygulanır |
| C | İndüklenen alanın dış alana her zaman zıt olduğu sanılır (akının azaldığı gözden kaçar); kuvvet için "harekete karşı" doğru hatırlanır |
| D | Hem indüklenen alan dış alana zıt sanılır, hem bu akıma kural uygulanarak kuvvet bulunur: anticlockwise akım sol kenarda aşağı, (−y) × (−z) = +x, sağa |

---

## Soru 3 — Paper 1A (HL)

A rectangular coil rotates at a constant rate in a uniform magnetic field. The axis of rotation lies in the plane of the coil and is
at right angles to the field.
At one instant the plane of the coil is **parallel** to the magnetic field lines.

Which describes the magnitudes of the magnetic flux linkage and of the induced emf at this instant?

A. The flux linkage is zero and the emf is zero.
B. The flux linkage is zero and the emf is a maximum.
C. The flux linkage is a maximum and the emf is zero.
D. The flux linkage is a maximum and the emf is a maximum.

**Cevap: B**

**Çözüm.** Bobin düzlemi alan çizgilerine paralelken bobinden hiç alan çizgisi geçmez: akı bağlantısı sıfırdır. Aynı anda bobinin
kenarları alan çizgilerini dik keser; akı bağlantısı en hızlı bu anda değişir. Faraday yasasına göre emk, akı bağlantısının değişim
hızıyla orantılıdır, dolayısıyla en büyük değerindedir.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Emk'nin akı bağlantısının kendisiyle orantılı olduğu sanılır (değişim hızıyla değil) |
| C | Bobin düzleminin alana paralel olması ile dik olması karıştırılır |
| D | Hem konum karıştırılır hem emk akıyla orantılı sanılır |

---

## Soru 4 — Paper 1A (HL)

A coil rotates at a constant rate in a uniform magnetic field. The emf induced in the coil varies sinusoidally with a maximum value
of 6.0 V and a period of 40 ms. The frequency of rotation of the coil is then doubled. No other change is made.

Which gives the new maximum emf and the new period?

A. 3.0 V and 80 ms
B. 6.0 V and 20 ms
C. 12 V and 40 ms
D. 12 V and 20 ms

**Cevap: D**

**Çözüm.** Frekans iki katına çıkınca periyot yarıya iner: 20 ms. Akı bağlantısının en büyük değeri değişmez ama aynı değişim yarı
sürede gerçekleşir; akı bağlantısının en büyük değişim hızı, dolayısıyla tepe emk iki katına çıkar: 12 V.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Frekans ile periyot karıştırılır (periyot iki katına çıkar) ve emk'nin de buna göre yarıya indiği düşünülür |
| B | Tepe emk'nin yalnızca B, alan ve sarım sayısına bağlı olduğu sanılır; periyot doğru |
| C | Emk'nin arttığı bilinir ama emk'nin periyodunun dönme periyoduyla birlikte değiştiği görülmez |

---

## Soru 5 — Paper 2 (HL, 9 puan)

A rectangular aluminium frame is fixed flat on top of a small cart. The frame is a single loop of resistance 0.050 Ω. The cart is
pulled along a horizontal track at a constant speed of 1.5 m s⁻¹. The frame enters a region of uniform magnetic field of strength
0.40 T that is directed vertically downwards. The leading side of the frame has length 0.20 m and is at right angles to the velocity.
The region of field is longer than the frame.

> **Şekil:** Yukarıdan görünüş. Dikdörtgen çerçeve (öndeki ve arkadaki kenarlar 0.20 m, harekete dik; yan kenarlar daha uzun,
> harekete paralel) sağa doğru 1.5 m s⁻¹ hızla hareket ediyor. Sağda, sayfanın içine doğru (yukarıdan bakana göre aşağı doğru)
> düzgün manyetik alan bölgesi (⊗ simgeleri) düşey bir sınır çizgisiyle başlıyor. Çerçevenin öndeki kenarı alanın içinde, arkadaki
> kenarı dışında. Diagram not to scale.

**(a)** Calculate the emf induced in the frame while it is entering the field. [2]

**(b)** Determine the magnitude of the force that must be applied to the cart to keep its speed constant while the frame is entering
the field. Friction and air resistance are negligible. [3]

**(c)** Show that, while the frame is entering the field, the rate at which the applied force does work and the rate at which energy
is dissipated in the frame are both about 0.29 W. [2]

The frame is now completely inside the region of magnetic field and is still moving at 1.5 m s⁻¹.

**(d)** Explain why there is no current in the frame. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *ε* = *BvL* = 0.40 × 1.5 × 0.20 ✓<br>*ε* = 0.12 «V» ✓ | | 2 |
| 5. | b | | *I* = *ε*/*R* = 0.12 / 0.050 «= 2.4 A» ✓<br>«magnetic» force on the leading side = *BIL* = 0.40 × 2.4 × 0.20 ✓<br>«applied force equals the magnetic force as the speed is constant, so» *F* = 0.19 «N» ✓ | *Allow ECF from (a).* | 3 |
| 5. | c | | rate of work done by applied force = *Fv* = 0.192 × 1.5 = 0.288 «W» ✓<br>rate of energy dissipation = *I*²*R* = 2.4² × 0.050 = 0.288 «W» **OR** *εI* = 0.12 × 2.4 = 0.288 «W» ✓ | *Both values must be calculated.*<br>*Allow 0.285 W «0.28–0.29 W» for Fv if the rounded F = 0.19 N is used.*<br>*Allow Fv = BILv = εI for MP1 if one of the two powers is evaluated as 0.29 W.* | 2 |
| 5. | d | | the magnetic flux «linkage» through the frame is constant / is not changing ✓<br>«by Faraday's law» the induced emf is zero, so there is no current ✓ | *OWTTE*<br>**OR** *equal emfs are induced in the leading and trailing sides ✓ they act in opposite senses around the loop so the net emf is zero ✓* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `B = 0.40 T`, `v = 1.5 m/s`, `L = 0.20 m`, `R = 0.050 ohm` | |
| `emf` | `B*v*L` | 0.12 V |
| `I` | `emf/R` | 2.4 A |
| `F` | `B*I*L` | 0.192 N ≈ 0.19 N |
| `P_mech` | `F*v` | 0.288 W |
| `P_elec` | `I**2*R` | 0.288 W |

**Yön notu (soruda istenmiyor, tutarlılık için).** Çerçeve alana girerken sayfanın içine doğru akı artar; Lenz yasasına göre
indüklenen akım çerçevenin içinde sayfadan dışarı doğru alan oluşturur: yukarıdan bakana göre saat yönünün tersine. Bu akım öndeki
kenarda sayfanın üstüne doğrudur (+y); F = IL × B = (+y) × (−z) = −x: manyetik kuvvet sola, yani harekete karşıdır. Uygulanan kuvvet
bu yüzden sağa doğrudur.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi + alt alta A–D | Soru 1 "What is …?"; Soru 2–4 "Which …?" (profilde daha seyrek ama geçerli) |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1 uygun (artan); Soru 2–3 aynı kalıpta dört cümle; Soru 4 aynı kalıpta dört değer çifti (emk'ye göre artan) |
| 1A: tablo seçenekli biçim örnekte doğrulanamadı | Soru 2–4 bu yüzden iki sütunlu tablo yerine cümle / çift biçiminde yazıldı; **cümle biçimli seçenek profilde azınlıkta, bu dosyada 4 sorunun 3'ü** — uzman tablo biçimini onaylarsa dönüştürülmeli |
| 1A: kritik sözcük koyu | Soru 2 ("into"), Soru 3 ("parallel") |
| 1A: doğru cevap konumu dengeli | C, A, B, D |
| 1A: seçenekler yuvarlamadan sonra birbirinden farklı | Kontrol edildi (python) |
| Şekil | Soru 1, 2, 5: metinle tarif edildi; alan yönü ve hareket yönü sözle de verildi |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 3, 2, 2; toplam 9) |
| Paper 2: "Show that" kalıbı | Soru 5(c): sayısal hedef verildi (0.29 W); iki nicelik ayrı ayrı hesaplanır |
| Paper 2: en az bir AO3 parça | Soru 5(b) Determine, (c) Show that, (d) Explain |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF, OWTTE | Soru 5 uygun |
| Değer–birim yazımı (m s⁻¹), 2 anlamlı basamak | Uygun |
| Paper 1B | Bu dosyada yok; D teması için 1B sorusu [D.3 dosyasında](d3-motion-in-em-fields-pilot-questions.md) |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından farklı bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları,
çeldirici değerleri ve Soru 2 ile Soru 5'teki akım / kuvvet yönleri (iki bağımsız yolla) yeniden üretildi ve eşleşti. KRİTİK ya da
ORTA bulgu yok. Ayrıntı: [review/d4-review.md](review/d4-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

İncelemeye yanıt olarak yapılan değişiklikler:

- **Soru 3 (kök):** dönme ekseninin bobin düzleminde olduğu eklendi ("The axis of rotation lies in the plane of the coil and is at
  right angles to the field").
- **Soru 5(c) (soru):** "Show that" parçasına sayısal hedef verildi: iki gücün de yaklaşık 0.29 W olduğu gösterilir.
- **Soru 5(c) (markscheme):** "0.19 × 1.5 = 0.29" (aritmetik olarak 0.285) → "0.192 × 1.5 = 0.288"; yuvarlanmış F = 0.19 N ile
  0.285 W kabul notu eklendi. `python3`: 0.192 × 1.5 = 0.288; 2.4² × 0.050 = 0.288; 0.12 × 2.4 = 0.288.
- **Değiştirilmeyen:** Soru 2–4'ün cümle / çift biçimli seçenekleri. İki sütunlu tablo biçimi biçim profilinde doğrulanmadığı için
  uzman kararına bırakıldı (inceleyen de aynı görüşte).

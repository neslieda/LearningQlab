# Pilot soru seti: A.3 İş, enerji ve güç

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set, [yazım standardına](AUTHORING_STANDARD.md) göre ve [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla elle yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü A.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav sorusu, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi
> (g = 9.8 m s⁻²; veri kitapçığı değeri uzmanca teyit edilmeli). Soru 5'teki dizel enerji yoğunluğu soruda verildi.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle
> bakılmadı; dizel yakıtın enerji yoğunluğu (3.6 × 10¹⁰ J m⁻³) ve pompanın toplam verimi (%12) genel bilgiye dayalı makul değerlerdir,
> bir kaynaktan teyit edilmedi; rehberin "enerji yoğunluğu"nu hacim başına mı (J m⁻³) kütle başına mı (J kg⁻¹) tanımladığı kontrol
> edilmedi.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.3) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | İş = *Fs* cos *θ*; bir kuvvetin işi ile net işin ayrımı | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Güç = *Fv*; verim | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Mekanik enerji ve korunumsuz kuvvetin (sürtünme) işi | AO2 | — | 1 | Orta |
| 4 | Paper 1A | SL | Esneklik potansiyel enerjisinin uzamaya bağlılığı | AO3 | — | 1 | Orta–zor |
| 5 | Paper 2 | SL | Güç, kinetik ve yerçekimi potansiyel enerjisi; verim; enerji yoğunluğu; Sankey diyagramı | AO1–AO3 | Show that, Determine, State, Explain | 9 | Orta |

Bu set A.3'ün tamamını kapsamaz. Eksik kalanlar: iş–kinetik enerji teoreminin doğrudan uygulanması, kuvvet–yer değiştirme grafiğinin
altındaki alan, mekanik enerjinin korunduğu (sürtünmesiz) durumlar, Sankey diyagramının çizimi ya da okunması, farklı yakıtların
enerji yoğunluklarının karşılaştırılması.

---

## Soru 1 — Paper 1A

A traveller pulls a wheeled suitcase at constant speed along a level platform. The strap makes an angle of 60° with the horizontal and
the traveller exerts a force of 25 N along the strap. The suitcase moves a distance of 40 m.

What is the work done by the traveller on the suitcase?

A. 0 J
B. 500 J
C. 870 J
D. 1000 J

**Cevap: B**

**Çözüm.** *W* = *Fs* cos *θ* = 25 × 40 × cos 60° = 500 J.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | "Sabit sürat, o hâlde iş yapılmaz" düşüncesi; net iş (sıfır) ile tek bir kuvvetin işi karıştırılır |
| C | Yer değiştirmeye dik bileşen kullanılır: 25 × 40 × sin 60° = 866 J ≈ 870 J |
| D | Açı göz ardı edilir: 25 × 40 = 1000 J |

---

## Soru 2 — Paper 1A

An electric winch raises a load of mass 150 kg vertically at a constant speed of 0.40 m s⁻¹. The electrical power supplied to the
winch is 840 W.

What is the efficiency of the winch?

A. 7.1 %
B. 30 %
C. 43 %
D. 70 %

**Cevap: D**

**Çözüm.** Yararlı güç = *Fv* = *mgv* = 150 × 9.8 × 0.40 = 588 W. Verim = 588 / 840 = 0.70 = %70.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Kuvvet yerine kütle kullanılır (*g* unutulur): 150 × 0.40 / 840 = 0.071 |
| B | Yararlı kesir yerine kaybedilen kesir verilir: (840 − 588) / 840 = 0.30 |
| C | Verim, kaybedilen gücün yararlı güce oranı sanılır: 252 / 588 = 0.43 |

---

## Soru 3 — Paper 1A

A parcel of mass 2.0 kg is released from rest at the top of a delivery chute. The chute is 5.0 m long and its top is 1.5 m vertically
above its bottom. The parcel reaches the bottom of the chute with a speed of 4.0 m s⁻¹.

What is the average friction force acting on the parcel as it slides down the chute?

A. 2.7 N
B. 3.2 N
C. 5.9 N
D. 8.9 N

**Cevap: A**

**Çözüm.** Kaybedilen potansiyel enerji = 2.0 × 9.8 × 1.5 = 29.4 J. Kazanılan kinetik enerji = ½ × 2.0 × 4.0² = 16.0 J.
Sürtünmeye karşı yapılan iş = 29.4 − 16.0 = 13.4 J. Sürtünme oluk boyunca (5.0 m) etkir: *f* = 13.4 / 5.0 = 2.7 N.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Kinetik enerjinin tamamı sürtünme işi sanılır: 16.0 / 5.0 = 3.2 N |
| C | Potansiyel enerjinin tamamının sürtünmeye gittiği varsayılır: 29.4 / 5.0 = 5.9 N |
| D | Enerji kaybı doğru bulunur ama yol yerine düşey yükseklik kullanılır: 13.4 / 1.5 = 8.9 N |

---

## Soru 4 — Paper 1A

A spring obeys Hooke's law. When the extension of the spring is *x*, the elastic potential energy stored in the spring is *E*. The
extension is then increased from *x* to 3*x*.

What is the **additional** work done on the spring?

A. 2*E*
B. 3*E*
C. 8*E*
D. 9*E*

**Cevap: C**

**Çözüm.** *E*<sub>p</sub> = ½*kx*² olduğundan 3*x* uzamada depolanan enerji 9*E*'dir. Ek iş = 9*E* − *E* = 8*E*.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Enerjinin uzamayla doğru orantılı olduğu sanılır ve ek uzama (2*x*) alınır: 2*E* |
| B | Enerjinin uzamayla doğru orantılı olduğu sanılır ve son değer verilir: 3*E* |
| D | Karesel bağıntı doğru kullanılır ama ek iş yerine son durumdaki toplam enerji verilir: 9*E* |

---

## Soru 5 — Paper 2 (9 puan)

A diesel-powered pump raises water from a river to an irrigation tank. The water is raised through a vertical height of 18 m at a
rate of 2.5 kg s⁻¹ and leaves the outlet pipe at the top with a speed of 4.0 m s⁻¹. The speed of the water in the river is negligible.

**(a)** Show that the rate at which the pump transfers energy to the water is about 460 W. [3]

This rate of energy transfer is the useful power output of the pump.

The overall efficiency of the pump is 12 %. The energy density of diesel fuel is 3.6 × 10¹⁰ J m⁻³.

**(b)** Determine the volume of diesel fuel used by the pump in 1.0 hour. [3]

**(c)** A Sankey diagram is drawn for the pump. State the value of the ratio
(width of the useful output arrow) / (width of the input arrow). [1]

The outlet pipe is replaced by a narrower nozzle so that the water leaves with a greater speed. The useful power output of the pump
and the height are unchanged.

**(d)** Explain the effect of this change on the mass of water delivered to the tank per second. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | rate of gain of gravitational potential energy = 2.5 × 9.8 × 18 «= 441 W» ✓<br>rate of gain of kinetic energy = ½ × 2.5 × 4.0² «= 20 W» ✓<br>total = 461 «W» ✓ | *Third mark needs the sum shown or an answer to at least 3 s.f.*<br>*Award [1] max for 441 «W» with no kinetic energy term.* | 3 |
| 5. | b | | input power = 460 / 0.12 «= 3.8 × 10³ W» ✓<br>energy supplied in 1.0 h = 3.8 × 10³ × 3600 «= 1.4 × 10⁷ J» ✓<br>volume = 1.4 × 10⁷ / 3.6 × 10¹⁰ = 3.8 × 10⁻⁴ «m³» ✓ | *Allow use of 461 W.*<br>*Accept 0.38 litre / 380 cm³.*<br>*Award [2] max if efficiency is multiplied instead of divided (5.5 × 10⁻⁶ m³).* | 3 |
| 5. | c | | 0.12 **OR** 12 : 100 **OR** 3/25 ✓ | | 1 |
| 5. | d | | each kilogram of water now gains more «kinetic» energy / more energy is transferred per unit mass ✓<br>power is unchanged, so less mass is delivered per second ✓ | *OWTTE*<br>*Do not award the second mark for "less" without reference to constant power or energy per second.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `mdot = 2.5 kg/s`, `H = 18 m`, `v = 4.0 m/s`, `eff = 0.12`, `rho_E = 3.6e10 J/m^3`, `t = 3600 s`, sabit `g = 9.8 m/s^2` | |
| `P_g` | `mdot*g*H` | 441 W |
| `P_k` | `0.5*mdot*v**2` | 20 W |
| `P_out` | `P_g + P_k` | 461 W |
| `P_in` | `P_out/eff` | 3.84 × 10³ W |
| `E_in` | `P_in*t` | 1.38 × 10⁷ J |
| `V_fuel` | `E_in/rho_E` | 3.84 × 10⁻⁴ m³ |

"Show that" değeriyle (460 W) aynı zincir: `P_in` = 3.83 × 10³ W, `V_fuel` = 3.83 × 10⁻⁴ m³; iki anlamlı basamakta sonuç aynıdır
(3.8 × 10⁻⁴ m³).

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–3 uygun (artan; J, %, N); Soru 4 cebirsel (*E*'nin katları), artan |
| 1A: doğru cevap konumu dengeli | B, D, A, C |
| 1A: vurgulanan kritik sözcük koyu | Soru 4 ("additional") uygun |
| 1A: bir ya da iki adımlı hesap | Soru 1–2 bir–iki adım; Soru 3 üç kısa adım (profildeki "bir ya da iki adım" gözleminin üst sınırında) |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (3, 3, 1, 2; toplam 9). Not: SL örnek kâğıdında kısa sorular 4–6 puan gözlendi; 9 puan HL aralığının üst ucu, SL için uzman teyidi gerekir |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanır | Soru 5 (a) → (b) uygun |
| Markscheme: dört sütunlu tablo, ✓, « », OR, OWTTE | Soru 5 uygun |
| Değer–birim yazımı (m s⁻¹, kg s⁻¹, J m⁻³), 2 anlamlı basamak | Uygun |
| Şekil | Hiçbir soru şekil gerektirmiyor; Soru 5 (c) Sankey diyagramını çizdirmez, yalnızca oran sorar (çizim cevap türü henüz yok) |
| Kapsam sınırları (A.3) | Yerçekimi potansiyel enerjisi yalnızca *mg*Δ*h*; türev/integral yok |

## Bağımsız kontrol

Tarih: 2026-10-11. Kör çözücü, cevapları görmeden soruları çözdü ve tüm cevap anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti; KRİTİK ya da ORTA bulgu yok.
Ayrıntı: [review/a3-review.md](review/a3-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

Bulgular üzerine yapılan değişiklikler:

- Soru 5 (a): "useful power output" yerine "the rate at which the pump transfers energy to the water" yazıldı ve bunun pompanın yararlı güç çıkışı olduğu ayrı bir cümleyle tanımlandı; böylece çıkıştaki kinetik enerjinin yararlı çıkışa dahil olduğu açık. Sayılar değişmedi (441 + 20 = 461 W).
- Soru 5 (c) markscheme: "about 1/8" (0.125) kaldırıldı, yerine tam eşdeğer "3/25" yazıldı.
- Soru 5'in 9 puan olması: dosyada zaten not edilmişti; ek değişiklik yapılmadı.

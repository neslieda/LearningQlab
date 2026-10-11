# Pilot soru seti: D.2 Elektrik ve manyetik alanlar

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü D.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; senaryolar yazarın kurgusudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Kullanılan sabitler: k = 8.99 × 10⁹ N m² C⁻², e = 1.60 × 10⁻¹⁹ C,
> proton kütlesi 1.67 × 10⁻²⁷ kg (veri kitapçığı değerleri uzmanca teyit edilmeli).
> **Bağımsız kontrol:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. dosya sonu).
> **Doğrulanmayan:** (1) uzman incelemesi yapılmadı; (2) Soru 3'teki alan yönleri sağ el kavrama kuralı ve
> ayrıca vektörel çarpımla (B ∝ I × r) elle kontrol edildi, kodla değil; (3) Soru 3 iki telin alanının nitel olarak üst üste
> bindirilmesini ister — müfredat analizindeki "düz tel" deseni sınırına girdiği varsayıldı, uzmanca teyit edilmeli; (4) Soru 5'te
> yüklü kürenin dışında nokta yük gibi davrandığı soruda varsayım olarak verildi; 2.5 μC yükün 0.15 m yarıçaplı kürede yüzey alanı
> 1.0 × 10⁶ N C⁻¹'dir (havanın delinme alanının altında, ama soru vakumda kurgulandı); (5) bilinen bir sınav sorusuna benzerlik
> açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (D.2) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Millikan deneyi: düzgün alanda yüklü damlanın dengesi; yükün kuantumlu olması | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | Paralel levhalar arasında alan şiddeti (E = V/d) ve yüke etkiyen kuvvet | AO2 | — | 1 | Kolay–orta |
| 3 | Paper 1A | SL | Akım taşıyan düz telin manyetik alan deseni ve yönü | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Nokta yüklerin elektrik potansiyeli (skaler toplam) | AO2 | — | 1 | Orta |
| 5 | Paper 2 | HL | Potansiyel ve alan şiddeti; W = qΔV; eşpotansiyel yüzeyler | AO2–AO3 | Show that, Calculate, Determine, Explain | 9 | Orta–zor |

Bu set D.2'nin tamamını kapsamaz. Eksik kalanlar: Coulomb yasasıyla kuvvet hesabı, yükün korunumu, sürtünme / etki / dokunma ile
yüklenme ve topraklama, elektrik alan çizgileri ve çizgi yoğunluğu, çubuk mıknatıs / çembersel halka / solenoid alan desenleri,
E = −ΔV/Δr (potansiyel gradyanı) ile hesap, eşpotansiyel desenlerinin çizimi.

Kapsam sınırı kontrolü: manyetik alan deseni yalnızca düz tel (Soru 3); potansiyel soruları en çok iki nokta yük içerir (Soru 4);
türev ya da integral yok.

---

## Soru 1 — Paper 1A

A small oil drop carries 3 excess electrons. The drop is held stationary in a vacuum between two horizontal parallel plates when the
potential difference between the plates is 600 V. The drop then gains 2 more electrons. The change in the mass of the drop is negligible.

What is the potential difference between the plates that holds the drop stationary now?

A. 200 V
B. 360 V
C. 600 V
D. 1000 V

**Cevap: B**

**Çözüm.** Denge: qV/d = mg, yani V ∝ 1/q (m, g, d sabit). Yük 3e'den 5e'ye çıkar: V = 600 × 3/5 = 360 V.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Gerilim, eklenen yükün ilk yüke oranı kadar azaltılır: 600 × (1 − 2/3) = 200 V |
| C | Damlanın ağırlığı değişmediği için gereken gerilimin de değişmediği düşünülür |
| D | Oran ters kurulur (V ∝ q): 600 × 5/3 = 1000 V |

---

## Soru 2 — Paper 1A

Two parallel metal plates are 15 mm apart in a vacuum. The potential difference between the plates is 3.0 kV. An alpha particle
(charge +2*e*) is at a point midway between the plates.

*e* = 1.60 × 10⁻¹⁹ C

What is the magnitude of the electric force on the alpha particle?

A. 1.4 × 10⁻¹⁷ N
B. 6.4 × 10⁻¹⁷ N
C. 3.2 × 10⁻¹⁴ N
D. 6.4 × 10⁻¹⁴ N

**Cevap: D**

**Çözüm.** E = V/d = 3.0 × 10³ / 0.015 = 2.0 × 10⁵ V m⁻¹ (levhalar arasında her yerde aynı). F = qE = 2 × 1.60 × 10⁻¹⁹ × 2.0 × 10⁵
= 6.4 × 10⁻¹⁴ N.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | E = V × d alınır: 3.0 × 10³ × 0.015 = 45; F = 3.2 × 10⁻¹⁹ × 45 = 1.4 × 10⁻¹⁷ N |
| B | Uzaklık metreye çevrilmez: E = 3.0 × 10³ / 15 = 200; F = 3.2 × 10⁻¹⁹ × 200 = 6.4 × 10⁻¹⁷ N |
| C | Alfa parçacığının yükü e alınır: 1.60 × 10⁻¹⁹ × 2.0 × 10⁵ = 3.2 × 10⁻¹⁴ N |

---

## Soru 3 — Paper 1A

Two long straight parallel wires X and Y are perpendicular to the page. Wire X is to the left of wire Y. The wires carry currents of
equal magnitude. The current in X is directed **into** the page and the current in Y is directed **out of** the page. Point P is
midway between the wires. The line XY is horizontal on the page.

> **Şekil:** Sayfa düzleminde yatay bir doğru üzerinde, soldan sağa X teli, P noktası, Y teli. X, sayfaya dik ve akımı sayfanın içine
> doğru (⊗ simgesi); Y, sayfaya dik ve akımı sayfadan dışarı doğru (⊙ simgesi). P, X ile Y'nin tam ortasında. "Sayfanın üstü" ve
> "sayfanın altı" yönleri XY doğrusuna diktir. Diagram not to scale.

What is the direction of the resultant magnetic field at P?

A. no direction (zero resultant field)
B. towards the top of the page
C. towards the bottom of the page
D. towards wire Y

**Cevap: C**

**Çözüm.** Kullanılan kural: sağ el kavrama kuralı (başparmak akım yönünde, parmaklar alan çizgilerinin dolanma yönünde).
X (akım sayfanın içine): alan çizgileri sayfaya bakan gözlemciye göre saat yönünde çemberlerdir; X'in sağındaki P'de alan sayfanın
altına doğrudur. Y (akım sayfadan dışarı): alan çizgileri saat yönünün tersinedir; Y'nin solundaki P'de alan yine sayfanın altına
doğrudur. İki alan aynı yönlüdür ve toplanır: bileşke sayfanın altına doğru.
Vektörel kontrol (x sağa, y sayfanın üstüne, z sayfadan dışarı; B ∝ I × r): X için (−z) × (+x) = −y; Y için (+z) × (−x) = −y.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | "Zıt yönlü eşit akımların alanları birbirini götürür" düşüncesi; P'nin tellerin zıt taraflarında olduğu göz ardı edilir |
| B | Kavrama kuralı ters uygulanır (sol el ya da dolanma yönü ters) |
| D | Manyetik alan, elektrik alandaki "artıdan eksiye" gibi bir telden ötekine doğru sanılır (alanın tele dik çemberler olduğu bilinmez) |

---

## Soru 4 — Paper 1A (HL)

Two point charges are 0.30 m apart in a vacuum. One charge is +6.0 nC and the other is −4.0 nC. Point P is on the line joining the
charges, midway between them.

*k* = 8.99 × 10⁹ N m² C⁻²

What is the electric potential at P?

A. 120 V
B. 600 V
C. 800 V
D. 4000 V

**Cevap: A**

**Çözüm.** Potansiyel skalerdir ve işaretiyle toplanır; P her iki yüke 0.15 m uzaklıktadır.
V = k(q₁ + q₂)/r = 8.99 × 10⁹ × (6.0 − 4.0) × 10⁻⁹ / 0.15 = 120 V.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Yükün işareti yok sayılır, büyüklükler toplanır: 8.99 × 10⁹ × 10.0 × 10⁻⁹ / 0.15 = 600 V |
| C | Potansiyel için 1/r² kullanılır (işaretli toplam): 8.99 × 10⁹ × 2.0 × 10⁻⁹ / 0.15² = 800 |
| D | Potansiyel yerine alan şiddeti hesaplanır (alanlar aynı yönlü, toplanır): 8.99 × 10⁹ × 10.0 × 10⁻⁹ / 0.15² = 4000 |

Not: denenen yanlış yollar doğru cevaba (120 V) düşmez: yalnızca ilk yük ve 0.30 m → 180 V; yalnızca ilk yük ve 0.15 m → 360 V; işaret yok sayılıp 0.30 m alınırsa → 300 V; işaretli toplam ve 0.30 m → 60 V; yalnızca ikinci yükün büyüklüğü → 240 V.

---

## Soru 5 — Paper 2 (HL, 9 puan)

An isolated metal sphere of radius 0.15 m is in a vacuum. The sphere carries a charge of +2.5 μC. For points on or outside its
surface, the sphere behaves as a point charge at its centre.

*k* = 8.99 × 10⁹ N m² C⁻²

**(a)** Show that the electric potential at the surface of the sphere is about 1.5 × 10⁵ V. [2]

**(b)** Calculate the electric field strength at the surface of the sphere. [2]

A proton is released from rest at the surface of the sphere.

charge of proton = 1.60 × 10⁻¹⁹ C
mass of proton = 1.67 × 10⁻²⁷ kg

**(c)** Determine the speed of the proton when it is 0.45 m from the centre of the sphere. [3]

A second proton is moved slowly around the sphere along a path that stays on one equipotential surface.

**(d)** Explain why the electric field does no work on this proton. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *V* = *kQ*/*r* = 8.99 × 10⁹ × 2.5 × 10⁻⁶ / 0.15 ✓<br>*V* = 1.498 × 10⁵ «V» **OR** 1.50 × 10⁵ «V» ✓ | *Answer must be given to at least 3 s.f. or the full substitution shown.* | 2 |
| 5. | b | | *E* = *kQ*/*r*² = 8.99 × 10⁹ × 2.5 × 10⁻⁶ / 0.15² **OR** *E* = *V*/*r* = 1.5 × 10⁵ / 0.15 ✓<br>*E* = 1.0 × 10⁶ «N C⁻¹ **OR** V m⁻¹» ✓ | | 2 |
| 5. | c | | potential at 0.45 m = «1.5 × 10⁵ / 3 =» 5.0 × 10⁴ «V» **OR** Δ*V* = 1.0 × 10⁵ «V» ✓<br>*q*Δ*V* = ½*mv*² **OR** 1.60 × 10⁻¹⁹ × 1.0 × 10⁵ = ½ × 1.67 × 10⁻²⁷ × *v*² ✓<br>*v* = 4.4 × 10⁶ «m s⁻¹» ✓ | *Allow ECF from (a).*<br>*Award [2] max if the potential at the surface «1.5 × 10⁵ V» is used as ΔV, giving* 5.4 × 10⁶ m s⁻¹. | 3 |
| 5. | d | | the potential is the same at all points of the path / Δ*V* = 0 ✓<br>*W* = *q*Δ*V* so *W* = 0 ✓ | *OWTTE*<br>**OR** *electric force «field» is perpendicular to the equipotential surface / to the displacement ✓ so the force has no component along the displacement ✓* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `Q = 2.5e-6 C`, `R = 0.15 m`, `r2 = 0.45 m`, `q = 1.60e-19 C`, `m = 1.67e-27 kg`, sabit `k = 8.99e9` | |
| `V_s` | `k*Q/R` | 1.498 × 10⁵ V |
| `E_s` | `k*Q/R**2` | 9.99 × 10⁵ N C⁻¹ ≈ 1.0 × 10⁶ N C⁻¹ |
| `V_2` | `k*Q/r2` | 4.99 × 10⁴ V |
| `dV` | `V_s - V_2` | 9.99 × 10⁴ V |
| `v` | `sqrt(2*q*dV/m)` | 4.37 × 10⁶ m s⁻¹ (ΔV = 1.0 × 10⁵ V ile 4.38 × 10⁶ m s⁻¹) |
| Çeldirici yol (c) | `sqrt(2*q*V_s/m)` | 5.36 × 10⁶ m s⁻¹ |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1, 2, 4 uygun (artan); Soru 3 dört kısa sözel ifade |
| 1A: kritik sözcük koyu | Soru 3 ("into", "out of") |
| 1A: doğru cevap konumu dengeli | B, D, C, A |
| 1A: seçenekler yuvarlamadan sonra birbirinden farklı | Kontrol edildi (python) |
| Şekil | Soru 3: metinle tarif edildi (akım yönleri ⊗ / ⊙ ve sözle); tellerin konumu (X solda) İngilizce kökte de yazıldığı için soru şekil olmadan çözülebilir |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 3, 2; toplam 9) |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanabilir | Soru 5(a) → (b), (c) uygun |
| Paper 2: en az bir AO3 parça | Soru 5(a) Show that, (c) Determine, (d) Explain |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF, OWTTE | Soru 5 uygun |
| Sabitlerin verilmesi | k, e ve proton kütlesi gereken sorularda soru metninde verildi |
| Değer–birim yazımı (N C⁻¹, m s⁻¹), 2 anlamlı basamak | Uygun |
| Paper 1B | Bu dosyada yok; D teması için 1B sorusu [D.3 dosyasında](d3-motion-in-em-fields-pilot-questions.md) |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından farklı bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları,
çeldirici değerleri ve Soru 3'teki alan yönü bağımsız olarak yeniden üretildi ve eşleşti. KRİTİK ya da ORTA bulgu yok. Ayrıntı:
[review/d2-review.md](review/d2-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

İncelemeye yanıt olarak yapılan değişiklikler:

- **Soru 3 (kök):** "Wire X is to the left of wire Y" ve "The line XY is horizontal on the page" eklendi; soru artık şekil tarifi
  olmadan da tek anlamlı. "Biçim uyumu" tablosundaki ilgili satır düzeltildi.
- **Soru 3 (seçenek A):** tam cümle "The resultant field is zero." → kısa ifade "no direction (zero resultant field)"; dört seçenek
  aynı biçimde.
- **Soru 4:** ikinci yük −2.0 nC → −3.0 nC. Eski sayılarla "işaret yok sayılır + r = 0.30 m" çifte hatası doğru cevabı (240 V)
  veriyordu; yeni sayılarla 270 V verir ve hiçbir seçenekle çakışmaz. Seçenekler 240 / 480 / 1600 / 3200 V → 180 / 540 / 1200 /
  3600 V; doğru cevap yine A. Tüm seçenekler `python3` ile yeniden hesaplandı (179.8, 539.4, 1198.7, 3596.0).
- **Soru 4, ikinci kontrol (recheck-2026-10-11):** −3.0 nC ile "yalnızca ilk yük ve 0.30 m" yanlış hesabı doğru cevabı (180 V)
  veriyordu. İkinci yük −4.0 nC yapıldı; seçenekler 120 / 600 / 800 / 4000 V, doğru cevap yine A (119.9, 599.3, 799.1, 3995.6).
  Bu son hali bağımsız çözücüden geçmedi; sayılar yalnızca yeniden hesaplandı.

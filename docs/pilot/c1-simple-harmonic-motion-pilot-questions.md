# Pilot soru seti: C.1 Basit harmonik hareket

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneği](a1-kinematics-pilot-questions.md) ile aynı yapıda yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü C.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgündür.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile yeniden hesaplandı;
> Soru 7'deki eğimler tablodaki veriden hesaplandı. g = 9.8 m s⁻² alındı (veri kitapçığı değeri uzmanca teyit edilmeli).
> **Doğrulanmayan:** (1) bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; (2) bilinen bir sınav sorusuna benzerlik açısından uzman
> gözüyle bakılmadı; (3) veri kitapçığındaki BHH denklemlerinin yazımı (x = x₀ sin(ωt + φ)) kitapçıktan teyit edilmedi, bu yüzden Soru 5'te
> denklem soru içinde verildi; (4) nitel sorular (Soru 3, Soru 6 d–e, Soru 7 a ve d) kodla doğrulanamaz; (5) Soru 7'nin grafiği
> üretilmedi.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (C.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Kütle–yay sisteminin periyodu; T ∝ √m | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | a = −ω²x; frekans–açısal frekans ilişkisi | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Enerji değişiminin nitel anlatımı (kinetik–potansiyel dönüşümünün zamanlaması) | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | v = ±ω√(x₀² − x²) | AO2 | — | 1 | Orta |
| 5 | Paper 1A | HL | Faz açısı; x = x₀ sin(ωt + φ) | AO3 | — | 1 | Zor |
| 6 | Paper 2 | SL | BHH koşulları; basit sarkaç periyodu; a = −ω²x; nitel enerji; küçük açı sınırı | AO1–AO3 | State, Show that, Calculate, Describe, Suggest | 9 | Orta |
| 7 | Paper 1B | SL | Kütle–yay periyodu verisinin işlenmesi; belirsizlik; doğrusallaştırma; sistematik hata | AO2–AO3 | State, Calculate, Determine, Suggest, Explain | 10 | Orta–zor |

Bu set C.1'in tamamını kapsamaz. Eksik kalanlar: yer değiştirme–zaman ve ivme–yer değiştirme grafiklerinin yorumu; hız denklemi
v = ωx₀ cos(ωt + φ); toplam ve potansiyel enerjinin nicel hesabı (HL); sarkaç periyodunun g'ye bağlılığı; iki salınıcı arasındaki faz farkı.

---

## Soru 1 — Paper 1A

A block of mass 0.20 kg hangs from a light vertical spring and oscillates with a period of 0.60 s. The block is replaced by a
block of mass 0.80 kg on the same spring.

What is the period of oscillation of the 0.80 kg block?

A. 0.30 s
B. 0.60 s
C. 1.2 s
D. 2.4 s

**Cevap: C**

**Çözüm.** T = 2π√(m/k), yani T ∝ √m. Kütle 4 katına çıkar; periyot √4 = 2 katına çıkar: 2 × 0.60 = 1.2 s.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Orantı ters çevrilir (T ∝ 1/√m): 0.60 / 2 = 0.30 s |
| B | Periyodun kütleden bağımsız olduğu düşünülür (basit sarkaçla karıştırma): 0.60 s |
| D | Karekök unutulur (T ∝ m): 0.60 × 4 = 2.4 s |

---

## Soru 2 — Paper 1A

A buoy floating on the sea moves vertically with simple harmonic motion of frequency 0.50 Hz and amplitude 0.40 m.

What is the magnitude of the acceleration of the buoy when its displacement from the equilibrium position is 0.20 m?

A. 0.63 m s⁻²
B. 2.0 m s⁻²
C. 3.9 m s⁻²
D. 32 m s⁻²

**Cevap: B**

**Çözüm.** ω = 2πf = 2π × 0.50 = 3.14 rad s⁻¹. |a| = ω²x = 3.14² × 0.20 = 1.97 ≈ 2.0 m s⁻².

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | ω'nın karesi alınmaz: ωx = 3.14 × 0.20 = 0.63 |
| C | Yer değiştirme yerine genlik kullanılır (en büyük ivme): 3.14² × 0.40 = 3.9 |
| D | 0.50 değeri periyot sanılır: ω = 2π / 0.50 = 12.6 rad s⁻¹; 12.6² × 0.20 = 31.6 ≈ 32 |

---

## Soru 3 — Paper 1A

A trolley attached to a horizontal spring oscillates on a frictionless track with simple harmonic motion of period *T*.

What is the shortest time between an instant when the kinetic energy of the trolley is a maximum and an instant when the elastic
potential energy of the spring is a maximum?

A. *T*/4
B. *T*/2
C. *T*
D. 2*T*

**Cevap: A**

**Çözüm.** Kinetik enerji denge konumunda, potansiyel enerji en büyük yer değiştirmede en büyüktür. Denge konumundan uç noktaya gidiş
çeyrek periyot sürer: T/4.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Bir uçtan öbür uca geçiş süresi alınır (bu, potansiyel enerjinin art arda iki en büyük değeri arasındaki süredir) |
| C | Enerji dönüşümünün yer değiştirmeyle aynı periyotta olduğu ve dönüşümün tam bir periyot sürdüğü düşünülür |
| D | Enerjinin periyodunun hareketin periyodunun iki katı olduğu sanılır (doğrusu yarısıdır) |

---

## Soru 4 — Paper 1A

A particle moves with simple harmonic motion of amplitude 0.10 m. The maximum speed of the particle is 2.0 m s⁻¹.

What is the speed of the particle when its displacement from the equilibrium position is 0.060 m?

A. 0.80 m s⁻¹
B. 1.2 m s⁻¹
C. 1.3 m s⁻¹
D. 1.6 m s⁻¹

**Cevap: D**

**Çözüm.** v<sub>max</sub> = ωx₀ → ω = 2.0 / 0.10 = 20 rad s⁻¹. v = ω√(x₀² − x²) = 20 × √(0.10² − 0.060²) = 20 × 0.080 = 1.6 m s⁻¹.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Hızın yer değiştirmeyle doğrusal azaldığı varsayılır: 2.0 × (1 − 0.60) = 0.80 |
| B | Hız yer değiştirmeyle doğru orantılı alınır (ivme ile karıştırma): 2.0 × 0.60 = 1.2 |
| C | Kareler alınmaz: 2.0 × √(1 − 0.60) = 1.26 ≈ 1.3 |

---

## Soru 5 — Paper 1A

The displacement *x* of a particle that moves with simple harmonic motion is given by *x* = *x*₀ sin(*ωt* + *φ*), where *x*₀ is the
amplitude. At time *t* = 0 the displacement of the particle is +*x*₀/2 and the particle is moving in the positive direction.

What is the phase angle *φ*?

A. π/6 rad
B. π/3 rad
C. 2π/3 rad
D. 5π/6 rad

**Cevap: A**

**Çözüm.** t = 0'da sin φ = 0.50 → φ = π/6 ya da 5π/6. Hız ωx₀ cos φ ile orantılıdır; pozitif yönde hareket için cos φ > 0 olmalıdır.
Bu yalnızca φ = π/6 için sağlanır (cos(5π/6) < 0).

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Sinüs yerine kosinüs kullanılır: cos φ = 0.50 → φ = π/3 (sin(π/3) = 0.87, yer değiştirme koşulunu sağlamaz) |
| C | B'deki hatanın üzerine yön için π − π/3 alınır (sin(2π/3) = 0.87, yer değiştirme koşulunu sağlamaz) |
| D | Yer değiştirme koşulu sağlanır (sin(5π/6) = 0.50) ama hareket yönü denetlenmez; bu fazda parçacık negatif yönde gider |

---

## Soru 6 — Paper 2 (9 puan)

A lamp of mass 1.5 kg hangs from the ceiling of a hall on a long light cable. The lamp is pulled a small distance to one side and
released. The lamp then swings and the time for 10 complete oscillations is 49 s. The lamp can be modelled as a simple pendulum.

**(a)** State, in terms of the acceleration of the lamp, the **two** conditions for its motion to be simple harmonic. [2]

**(b)** Show that the length of the pendulum is about 6 m. [2]

The amplitude of the oscillations is 0.30 m.

**(c)** Calculate the maximum acceleration of the lamp. [2]

**(d)** Describe the energy changes of the lamp as it moves from one extreme position to the other extreme position. Air resistance
is negligible. [2]

**(e)** The lamp is now released with an amplitude of 3.0 m. Suggest why the motion is no longer simple harmonic. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | acceleration / restoring force is proportional to the displacement «from the equilibrium position» ✓<br>acceleration / restoring force is directed towards the equilibrium position **OR** is opposite to the displacement ✓ | *Accept* a = −ω²x *only if the symbols are defined, for both marks.* | 2 |
| 6. | b | | *T* = 4.9 «s» ✓<br>*L* = 9.8 × 4.9² / 4π² **OR** 5.96 «m» ✓ | *Answer must be seen to at least 2 s.f. or the substitution must be shown.* | 2 |
| 6. | c | | *ω* = 2π / 4.9 «= 1.28 rad s⁻¹» ✓<br>*a* = 1.28² × 0.30 = 0.49 «m s⁻²» ✓ | *Allow ECF from an incorrect T in (b).*<br>*Allow* a = gx₀ / L *with L = 6 m, giving 0.49.* | 2 |
| 6. | d | | «gravitational» potential energy is transferred to kinetic energy as the lamp moves to the equilibrium position / lowest point ✓<br>kinetic energy is transferred back to «gravitational» potential energy **AND** the total energy is constant ✓ | *OWTTE* | 2 |
| 6. | e | | the restoring force / acceleration is not proportional to the displacement «for a large angle» ✓ | *Accept "the small-angle approximation is no longer valid".*<br>*OWTTE* | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `t10 = 49 s`, `N = 10`, `x0 = 0.30 m`, sabit `g = 9.8 m/s^2` | |
| `T` | `t10/N` | 4.90 s |
| `L` | `g*T**2/(4*pi**2)` | 5.96 m |
| `omega` | `2*pi/T` | 1.28 rad s⁻¹ |
| `a_max` | `omega**2*x0` | 0.493 m s⁻² |
| Denetim (soruda istenmez) | `asin(x0/L)` ve `asin(3.0/L)` | 2.9° ve 30° |

Kütle (1.5 kg) hiçbir hesapta kullanılmaz; bilerek verilen fazladan bilgidir (formül seçme becerisi).

---

## Soru 7 — Paper 1B (10 puan)

A student investigates how the period of oscillation of a load on a vertical spring depends on the mass of the load. Slotted
masses are placed on a hanger that is attached to the lower end of the spring. For each total mass *m* of slotted masses, the load
is displaced vertically and released, and the time *t* for 10 complete oscillations is measured with a stopwatch.

> **Şekil:** Bir destek çubuğuna bağlı düşey yay; yayın alt ucunda bir askı (hanger) ve üzerinde dilimli kütleler; yanında düşey cetvel
> ve denge konumunu gösteren işaret. "diagram not to scale".

| *m* / kg | *t* / s ± 0.2 s |
|---|---|
| 0.100 | 4.9 |
| 0.200 | 6.3 |
| 0.300 | 7.4 |
| 0.400 | 8.4 |
| 0.500 | 9.3 |

The uncertainty in *m* is negligible. The period of oscillation is *T*.

**(a)** State **one** reason why the student measures the time for 10 oscillations rather than the time for one oscillation. [1]

**(b)** (i) State the absolute uncertainty in *T*. [1]

 (ii) Calculate the percentage uncertainty in *T*² for *m* = 0.100 kg. [2]

The student expects that *T* = 2π√(*m*/*k*), where *k* is the spring constant. The student plots a graph of *T*² against *m* with
uncertainty bars. The gradient of the line of best fit is 1.56 s² kg⁻¹. The lines of maximum and minimum gradient have gradients of
1.70 s² kg⁻¹ and 1.42 s² kg⁻¹.

**(c)** Determine the spring constant *k*, with its absolute uncertainty. [3]

The line of best fit is straight but does **not** pass through the origin. Its intercept on the *T*² axis is +0.08 s².

**(d)** (i) Suggest a reason for the intercept. [1]

 (ii) Explain whether the intercept affects the value of *k* determined in (c). [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 7. | a | | the percentage / fractional uncertainty in *T* is reduced **OR** the «reaction time» uncertainty is shared between 10 oscillations ✓ | *OWTTE*<br>*Do not accept "more accurate" without reference to uncertainty.* | 1 |
| 7. | b | i | «±» 0.02 «s» ✓ | | 1 |
| 7. | b | ii | fractional uncertainty in *T* = 0.2 / 4.9 **OR** 0.02 / 0.49 «= 0.041» ✓<br>percentage uncertainty in *T*² = 2 × 4.1 = 8 «%» ✓ | *Allow ECF from (b)(i).*<br>*Accept 8.2 %.* | 2 |
| 7. | c | | *k* = 4π² / gradient = 4π² / 1.56 «= 25.3 N m⁻¹» ✓<br>uncertainty in gradient = (1.70 − 1.42) / 2 = 0.14 «s² kg⁻¹» **OR** 9 % ✓<br>*k* = (25 ± 2) «N m⁻¹» ✓ | *Accept the range method:* 4π²/1.42 = 27.8 *and* 4π²/1.70 = 23.2, *giving the half-range* (27.8 − 23.2)/2 = *± 2.3.*<br>*Third mark requires the uncertainty to 1 s.f. and a consistent number of decimal places.* | 3 |
| 7. | d | i | the mass of the hanger / of the spring also oscillates but is not included in *m* ✓ | *Accept "there is a constant extra mass" OWTTE.* | 1 |
| 7. | d | ii | the extra mass is constant / is a systematic error, so every point is shifted by the same amount «along the *m* axis» ✓<br>the gradient is unchanged, so *k* is not affected ✓ | *OWTTE*<br>*Second mark requires the reference to the gradient.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `dt = 0.2 s`, `N = 10`, `t(0.100 kg) = 4.9 s`, `grad = 1.56`, `grad_max = 1.70`, `grad_min = 1.42` (s² kg⁻¹) | |
| `dT` | `dt/N` | 0.02 s |
| `pct_T2` | `2*dt/t*100` | 8.2 % |
| `k` | `4*pi**2/grad` | 25.3 N m⁻¹ |
| `d_grad` | `(grad_max - grad_min)/2` | 0.14 s² kg⁻¹ (%9.0) |
| `dk` | `k*d_grad/grad` | 2.3 N m⁻¹ |
| Aralık denetimi | `4*pi**2/grad_min`, `4*pi**2/grad_max` | 27.8 ve 23.2 N m⁻¹; yarı aralık (27.8 − 23.2)/2 = 2.3 N m⁻¹ |

### Şekil notu

Öğrenciye gösterilecek sürümde tablo ile birlikte belirsizlik çubuklu *T*²–*m* grafiği yer alır; grafik aynı veriden kodla üretilir.
Tablodaki veriden hesaplanan değerler: *T*² = 0.240, 0.397, 0.548, 0.706, 0.865 s²; *T*² belirsizlikleri (2*T*Δ*T*) 0.020–0.037 s²;
en küçük kareler eğimi 1.558 s² kg⁻¹, kesim noktası 0.084 s²; belirsizlik çubuklarının uçlarından geçen doğruların eğimleri 1.704 ve
1.420 s² kg⁻¹. Soruda verilen 1.56, 1.70, 1.42 ve 0.08 değerleri bunların yuvarlanmış halidir. Veri, *k* = 25 N m⁻¹ ve tabloya
yazılmayan 0.050 kg'lık sabit ek kütle (askı) ile üretilip 0.1 s'ye yuvarlanmıştır; kesim noktası / eğim = 0.054 kg bununla tutarlıdır.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–5 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–5 uygun (artan) |
| 1A: doğru cevap harfleri dengeli | C, B, A, D, A |
| 1A: şekil olmadan çözülebilir | Soru 1–5 şekil gerektirmez |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 6 uygun (2, 2, 2, 2, 1; toplam 9). SL kâğıdında kısa soru 4–6 puan gözlendi; 9 puan HL aralığının üst sınırıdır — SL kâğıdı için (d) ya da (e) çıkarılabilir |
| Paper 2: "Show that" kalıbı ve en az bir AO3 parçası | Soru 6 (b) Show that, (e) Suggest |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE | Soru 6 ve Soru 7 uygun |
| 1B: yaklaşık 10 puanlık deney sorusu, alt parçalar 1–3 puan | Soru 7 uygun (1, 1, 2, 3, 1, 2; toplam 10) |
| 1B: tablo başlığı "büyüklük / birim ± belirsizlik" | Soru 7 uygun |
| 1B: öğrenci verilen grafiğe en uygun doğruyu çizer ve eğimi kendisi bulur | **Soru 7 uygun değil:** grafik üretilmediği için eğimler ve kesim noktası metinde verildi. Grafik şablonu hazır olunca (c) ve (d) yeniden yazılmalı |
| 1B: düzenek şeması | **Eksik:** yalnızca sözle tarif edildi (`> **Şekil:**`) |
| Müfredat sınırı: SL'de enerji nitel; faz açısı radyan; türev/integral yok | Soru 3 ve 6(d) nitel; Soru 5 radyan; hız ifadesi türevsiz, veri kitapçığı ilişkisi olarak kullanıldı |
| Düzey etiketi | Soru 4 ve 5 HL (ek HL içeriği); diğerleri SL |
| Değer–birim yazımı (m s⁻¹), 2 anlamlı basamak | Uygun |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, cevapları görmeyen bağımsız bir kör çözücü tarafından çözüldü; çözücü tüm cevap
anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti (KRİTİK bulgu yok). Bulgular:
[review/c1-review.md](review/c1-review.md). Bu, uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile, dosyanın son metni üzerinden yeniden denetlendi):

- **Soru 6 (a) (ORTA):** kök, yalnızca tanım koşullarını isteyecek biçimde yeniden yazıldı ("State, in terms of the acceleration of the lamp, …"). Markscheme değişmedi.
- **Soru 6 (DÜŞÜK):** "Biçim uyumu" tablosuna SL kısa sorusu için 9 puanın uzun olduğu notu eklendi.
- **Soru 7 (c) (DÜŞÜK):** markscheme notuna ve formül zincirine ± 2.3 değerinin yarı aralık olduğu, (27.8 − 23.2)/2, yazıldı.
- **Uygulanmayan:** Soru 3'ün D çeldiricisinin (2*T*) 3*T*/4 ile değiştirilmesi. İncelemede "şüphe" olarak geçiyor; 3*T*/4 belirli bir yanılgıya dayanmıyor ve *T*/4 ile aynı fiziksel durumu (denge–uç arası) çağrıştırdığı için daha zayıf bulundu. Uzman kararına bırakıldı.

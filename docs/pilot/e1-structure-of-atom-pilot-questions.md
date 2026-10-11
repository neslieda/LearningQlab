# Pilot soru seti: E.1 Atomun yapısı

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Yazım ölçütleri: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Yapı örneği: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Kaynak:** yalnızca müfredat düğümü E.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve genel
> fizik. Hiçbir sınav kâğıdı, markscheme, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgün kurgudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi. Kullanılan
> sabitler: h = 6.63 × 10⁻³⁴ J s, c = 3.00 × 10⁸ m s⁻¹, e = 1.60 × 10⁻¹⁹ C, k = 8.99 × 10⁹ N m² C⁻², R₀ = 1.20 × 10⁻¹⁵ m
> (veri kitapçığı değerleri uzmanca teyit edilmeli).
> **Doğrulanmayan:**
> - Bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. sondaki "Bağımsız kontrol"). Bilinen bir sınav sorusuna benzerlik
>   açısından uzman gözüyle bakılmadı.
> - Bellekten yazılan değerler: R₀ = 1.20 × 10⁻¹⁵ m (Soru 6), kalay-120 için Z = 50 (Soru 6), alfa enerjisi 5.5 MeV'in tipik bir alfa
>   kaynağı için gerçekçi olduğu. Soru 2'deki enerji düzeyleri gerçek bir elemente ait değildir; kurgusaldır ve soruda atom adı verilmez.
> - Soru 3'te soğuk sodyum buharının görünür bölgede soğurma çizgisi verdiği (temel düzeyden geçiş) genel bilgiye dayanır.
> - Soru 6 (c)(ii)'deki "sapma eşiği" kestirimi, alfa parçacığının kendi yarıçapını ve güçlü kuvvetin menzilini yok sayar; gerçek
>   eşik daha düşüktür (alfa yarıçapı eklenirse yaklaşık 18 MeV). Bu varsayım artık soru kökünde açıkça yazılıdır ve parça "Estimate"
>   ile sorulur; uzman bu basitleştirmenin kabul edilebilirliğini teyit etmeli.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (E.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Geiger–Marsden–Rutherford deneyinin nitel yorumu | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Kesikli enerji düzeyleri; foton enerjisi E = hf = hc/λ | AO2 | — | 1 | Orta |
| 3 | Paper 1A | SL | Soğurma tayfının oluşumu; tayftan bileşim | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | R = R₀A^(1/3); çekirdek yoğunluğunun A'dan bağımsızlığı | AO3 | — | 1 | Orta |
| 5 | Paper 1A | HL | Bohr modeli: E = −13.6/n² eV; geçiş enerjileri | AO2 | — | 1 | Orta |
| 6 | Paper 2 | HL | En yakın yaklaşma uzaklığı; çekirdek yarıçapı; yüksek enerjide Rutherford saçılmasından sapma | AO2–AO3 | Show, Calculate, Explain, Estimate | 8 | Orta–zor |

Bu set E.1'in tamamını kapsamaz. Eksik kalanlar: çekirdek gösterimi (proton, nötron, nükleon sayısı), yayma tayfının deneysel elde
edilişi, tayf çizgilerinden bileşim belirlemenin nicel örneği, Bohr modelinde açısal momentum kuantumlanması (mvr = nh/2π), çekirdek
yoğunluğunun sayısal hesabı.

---

## Soru 1 — Paper 1A

In the Geiger–Marsden–Rutherford experiment, alpha particles are directed at a thin gold foil. A few alpha particles are deflected
through angles greater than 90°.

Which feature of the atom is needed to explain these large deflections?

A. Most of the volume of the atom is empty space.
B. The positive charge is spread uniformly throughout the atom.
C. The electrons occupy discrete energy levels.
D. The positive charge and most of the mass are concentrated in a very small region.

**Cevap: D**

**Çözüm.** Bir alfa parçacığının geri saçılabilmesi için çok büyük bir itme kuvveti gerekir. Bu, ancak pozitif yükün küçük bir bölgede
toplanmasıyla (yakın geçişte çok güçlü alan) ve bu bölgenin alfa parçacığından çok daha büyük kütleli olmasıyla açıklanır.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Deneyin öbür gözlemiyle (parçacıkların çoğunun sapmadan geçmesi) karıştırılır; boşluk büyük açılı sapmayı açıklamaz |
| B | Düzgün dağılmış yük modeli (çekirdek öncesi model) alınır; bu model yalnızca çok küçük sapmalar verir |
| C | Tayf kanıtı ile saçılma kanıtı karıştırılır; enerji düzeyleri saçılma deneyinin sonucu değildir |

---

## Soru 2 — Paper 1A

The diagram shows three energy levels of an atom.

> **Şekil:** Üç yatay çizgiden oluşan enerji düzeyi diyagramı. En alttaki çizgi −5.80 eV, ortadaki −3.30 eV, en üstteki −1.20 eV olarak
> etiketlidir. Diyagram ölçekli değildir. (Soru, metinde verilen bu üç değerle şekil olmadan çözülebilir.)

The energies of the levels are −5.80 eV, −3.30 eV and −1.20 eV. Electron transitions take place between these levels.

What is the longest wavelength of the photons emitted in these transitions?

A. 270 nm
B. 497 nm
C. 592 nm
D. 1040 nm

**Cevap: C**

**Çözüm.** En uzun dalga boyu en küçük enerji farkına karşılık gelir. Farklar: 2.50 eV, 2.10 eV, 4.60 eV. En küçüğü 2.10 eV.
λ = hc / E = (6.63 × 10⁻³⁴ × 3.00 × 10⁸) / (2.10 × 1.60 × 10⁻¹⁹) = 5.92 × 10⁻⁷ m = 592 nm.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | En uzun dalga boyu için en büyük enerji farkı seçilir: 4.60 eV → 270 nm (λ ile E'nin ters orantısı gözden kaçar) |
| B | Yalnızca en alttaki iki düzey arasındaki geçiş düşünülür: 2.50 eV → 497 nm |
| D | Enerji farkı yerine en üst düzeyin enerjisinin büyüklüğü kullanılır: 1.20 eV → 1036 nm ≈ 1040 nm |

---

## Soru 3 — Paper 1A

White light from a hot filament passes through cool, low-pressure sodium vapour. The transmitted light is then dispersed by a
diffraction grating and viewed on a screen.

What is observed on the screen?

A. A continuous spectrum crossed by dark lines at certain wavelengths that sodium can emit
B. Bright lines on a dark background at certain wavelengths that sodium can emit
C. A continuous spectrum with no lines
D. A continuous spectrum with brighter lines at certain wavelengths that sodium can emit

**Cevap: A**

**Çözüm.** Buhardaki atomlar yalnızca enerji düzeyi farklarına eşit enerjili fotonları soğurur; bunlar atomun yayabildiği dalga
boyları arasındadır (soğuk buharda yalnızca temel düzeyden başlayan geçişler). Soğurulan enerji her yöne yeniden yayıldığı için gözlem doğrultusunda bu dalga boylarında şiddet azalır: sürekli tayf
üzerinde karanlık çizgiler (soğurma tayfı).

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Soğurma tayfı ile yayma tayfı karıştırılır; bu görüntü sıcak buharın tek başına verdiği tayftır |
| C | Düşük basınçlı gazın ışığa tümüyle saydam olduğu, fotonlarla etkileşmediği düşünülür |
| D | Buharın, geçen ışığa kendi çizgilerini "eklediği" düşünülür; yeniden yayımın her yöne olduğu gözden kaçar |

---

## Soru 4 — Paper 1A

Nucleus X has nucleon number 27 and nucleus Y has nucleon number 216.

What is the ratio (density of nucleus Y) / (density of nucleus X)?

A. 1/64
B. 1
C. 2
D. 8

**Cevap: B**

**Çözüm.** R = R₀A^(1/3) olduğundan hacim ∝ R³ ∝ A. Kütle de ∝ A. Yoğunluk = kütle / hacim, A'dan bağımsızdır; oran 1.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | R ∝ A alınır: kütle oranı 8, hacim oranı 8³ = 512; 8 / 512 = 1/64 |
| C | Hacim yerine yüzey alanına bölünür: yarıçap oranı 2, alan oranı 4; 8 / 4 = 2 |
| D | İki çekirdeğin hacmi eşit sayılır; yalnızca kütle oranı alınır: 216 / 27 = 8 |

---

## Soru 5 — Paper 1A

In the Bohr model of the hydrogen atom, the energy of the level with quantum number *n* is −13.6 / *n*² eV. Photon P is emitted in
the transition from *n* = 3 to *n* = 2. Photon Q is emitted in the transition from *n* = 2 to *n* = 1.

What is the ratio (energy of photon P) / (energy of photon Q)?

A. 5/27
B. 1/3
C. 4/9
D. 1

**Cevap: A**

**Çözüm.** E<sub>P</sub> = 13.6 (1/4 − 1/9) = 13.6 × 5/36 = 1.89 eV. E<sub>Q</sub> = 13.6 (1 − 1/4) = 13.6 × 3/4 = 10.2 eV.
Oran = (5/36) / (3/4) = 5/27 ≈ 0.19.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Düzey enerjisi 1/n ile orantılı alınır: (1/2 − 1/3) / (1 − 1/2) = 1/3 |
| C | Foton enerjileri yerine düzey enerjilerinin oranı alınır: E₃ / E₂ = (1/9) / (1/4) = 4/9 |
| D | Düzeylerin eşit aralıklı olduğu düşünülür; ardışık iki geçiş aynı enerjiyi verir |

---

## Soru 6 — Paper 2 (8 puan)

Alpha particles of kinetic energy 5.5 MeV are directed at a thin tin foil. One alpha particle approaches a nucleus of tin-120
(¹²⁰₅₀Sn) head-on and comes to rest momentarily before returning along its original path. The recoil of the tin nucleus is negligible.

Coulomb constant *k* = 8.99 × 10⁹ N m² C⁻²; *R*₀ = 1.20 × 10⁻¹⁵ m.

**(a)** Show that the distance of closest approach of this alpha particle to the centre of the tin nucleus is about 2.6 × 10⁻¹⁴ m. [3]

**(b)** Calculate the radius of a tin-120 nucleus. [1]

The kinetic energy of the alpha particles is now increased. Above a certain energy, the number of alpha particles scattered at
large angles is different from that predicted by Rutherford scattering.

**(c)** (i) Explain why deviations from Rutherford scattering occur at high alpha particle energies. [2]

 (ii) Assume that the deviations begin when the distance of closest approach is equal to the radius of the tin-120 nucleus and
 that the alpha particle can be treated as a point. Estimate, in MeV, the alpha particle energy at which the deviations begin. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | «at closest approach» initial kinetic energy = electric potential energy **OR** *E*<sub>k</sub> = *k*(2*e*)(50*e*) / *d* ✓<br>*E*<sub>k</sub> = 5.5 × 10⁶ × 1.60 × 10⁻¹⁹ «= 8.8 × 10⁻¹³ J» ✓<br>*d* = 8.99 × 10⁹ × 100 × (1.60 × 10⁻¹⁹)² / 8.8 × 10⁻¹³ = 2.62 × 10⁻¹⁴ «m» ✓ | *Charges 2e and 50e must be seen or implied for MP1.*<br>*Answer must be given to at least 3 s.f. for MP3.* | 3 |
| 6. | b | | *R* = 1.20 × 10⁻¹⁵ × 120^(1/3) = 5.92 × 10⁻¹⁵ «m» ✓ | *Accept 5.9 × 10⁻¹⁵ m.* | 1 |
| 6. | c | i | alpha particle gets close enough to the nucleus for the strong nuclear force to act «on it» ✓<br>so the force is no longer only electric repulsion / the alpha particle may be attracted or absorbed, «changing the scattering pattern» ✓ | *OWTTE* | 2 |
| 6. | c | ii | use of *E* ∝ 1/*d* with *d* = *R* **OR** *E* = *k*(2*e*)(50*e*) / *R* ✓<br>*E* = 5.5 × (2.62 × 10⁻¹⁴ / 5.92 × 10⁻¹⁵) ≈ 24 «MeV» ✓ | *Allow ECF from (b).*<br>*Accept answers in the range 23–25 MeV.*<br>*The stem fixes the criterion d = R(Sn); do not award MP2 for 18 MeV obtained with R(Sn) + R(α).* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `E_MeV = 5.5`, `Z = 50`, `A = 120`, sabitler `k = 8.99e9`, `e = 1.60e-19`, `R0 = 1.20e-15` | |
| `E_k` | `E_MeV*1e6*e` | 8.80 × 10⁻¹³ J |
| `d` | `k*2*Z*e**2/E_k` | 2.615 × 10⁻¹⁴ m |
| `R` | `R0*A**(1/3)` | 5.92 × 10⁻¹⁵ m |
| `E_dev` | `E_MeV*d/R` | 24.3 MeV |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?" / "Which …?") + alt alta A–D | Soru 1–5 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 2, 4, 5 uygun (artan); Soru 1 ve 3 cümle biçiminde seçenek (profilde azınlık biçim) |
| 1A: doğru cevap konumu dengeli | D, C, A, B, A |
| 1A: şekil olmadan çözülebilirlik | Soru 2'de şekil tarif edildi; değerler metinde de verildi |
| Kapsam sınırı: SL'de deney yalnızca nitel | Soru 1 nitel; nicel saçılma yalnızca HL etiketli Soru 6'da |
| Kapsam sınırı: saçılmada yalnızca elektriksel itme | Soru 6 (a) ve (c)(ii) yalnızca Coulomb potansiyel enerjisi kullanır; güçlü kuvvet (c)(i)'de yalnızca nitel |
| Kapsam sınırı: kimyasal semboller ezberlenmez | Soru 6'da sembol, Z ve A soruda verildi; Soru 3'te element adı yazıyla |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 6 uygun (3, 1, 2, 2; toplam 8) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | (a) Show that, (c)(i) Explain; (c)(ii) verilen yaklaşık değeri kullanır ve eşik ölçütü kökte varsayım olarak yazılıdır |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF, OWTTE | Soru 6 uygun |
| Değer–birim yazımı, anlamlı basamak | Uygun; Soru 2'de veriler 3 anlamlı basamak, cevap 3 anlamlı basamak |
| Düzey etiketi | Soru 1–3 SL; Soru 4–6 HL (ek HL içeriği) |

## Bağımsız kontrol

Tarih: 2026-10-11. Yazardan farklı bir kör çözücü soruları cevapları görmeden çözdü; tüm cevap anahtarlarını bağımsız olarak yeniden
üretti, çekirdek denklemlerini (nükleon sayısı ve yük korunumu) ve Paper 1B eğimlerini yeniden hesapladı. Bulgular:
[review/e1-review.md](review/e1-review.md). KRİTİK bulgu yok. Bu kontrol uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 6 (c)(ii) (ORTA):** eşik ölçütü köke eklendi ("distance of closest approach is equal to the radius of the tin-120 nucleus … alpha particle … treated as a point"). Cevap 24 MeV ve 23–25 MeV aralığı değişmedi; markscheme notuna, ölçüt kökte verildiği için R(Sn) + R(α) ile bulunan 18 MeV'in son puanı almadığı yazıldı.
- **Soru 6 (b) (DÜŞÜK):** cevap 5.9 × 10⁻¹⁵ m → 5.92 × 10⁻¹⁵ m; "Accept 5.9 × 10⁻¹⁵ m" notu eklendi. (c)(ii) satırı 2.62 × 10⁻¹⁴ / 5.92 × 10⁻¹⁵ ile yazıldı (24.3 MeV).
- **Soru 3 (DÜŞÜK):** A, B ve D seçeneklerinde "at wavelengths that sodium emits" → "at certain wavelengths that sodium can emit"; çözüm metni buna göre düzeltildi. Cevap A değişmedi.

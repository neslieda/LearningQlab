# Pilot soru seti: E.2 Kuantum fiziği

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Yazım ölçütleri: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Yapı örneği: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
> Bu dosya, E teması için istenen tek Paper 1B sorusunu da içerir (Soru 6).
>
> **Kaynak:** yalnızca müfredat düğümü E.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve genel
> fizik. Hiçbir sınav kâğıdı, markscheme, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgün kurgudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi. Kullanılan
> sabitler: h = 6.63 × 10⁻³⁴ J s, c = 3.00 × 10⁸ m s⁻¹, e = 1.60 × 10⁻¹⁹ C, elektron kütlesi 9.11 × 10⁻³¹ kg, Compton sabiti
> h/m<sub>e</sub>c = 2.43 × 10⁻¹² m (veri kitapçığı değerleri uzmanca teyit edilmeli).
> **Doğrulanmayan:**
> - Bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. sondaki "Bağımsız kontrol"). Bilinen bir sınav sorusuna benzerlik
>   açısından uzman gözüyle bakılmadı.
> - Soru 1 ve Soru 6'daki iş fonksiyonları (2.9 eV, yaklaşık 2.1 eV) belirli bir metale atfedilmedi; alkali ve toprak alkali metaller
>   için gerçekçi büyüklükte olduğu bellekten gelen genel bilgidir.
> - Soru 6'nın veri tablosu gerçek bir ölçüm değildir: φ = 2.1 eV ve h = 6.63 × 10⁻³⁴ J s ile üretilen kuramsal değerlere elle ±0.01–0.02 V
>   saçılma eklenmiştir. Eğim ve kesim değerleri bu tablodan kodla hesaplandı (bkz. Şekil notu).
> - Soru 5'te 150 V ile hızlandırılan elektron için göreli olmayan hesap kullanıldı (v ≈ 0.024c; düzeltme ihmal edilebilir). Grafit
>   filmde halka deseni oluştuğu genel bilgidir; halka çaplarının sayısal değeri sorulmaz.
> - Veri kitapçığında Compton formülünün ve h/m<sub>e</sub>c değerinin hangi biçimde verildiği teyit edilmedi; Soru 3'te ikisi de soruda yazıldı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (E.2) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Fotoelektrik denklem; iş fonksiyonu; en büyük kinetik enerji | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | HL | de Broglie dalga boyu; λ = h/p ile kinetik enerjinin birleştirilmesi | AO3 | — | 1 | Orta |
| 3 | Paper 1A | HL | Compton saçılması; dalga boyu kayması | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Fotoelektrik olayın dalga modeliyle açıklanamayan gözlemi; eşik frekansı | AO2 | — | 1 | Orta |
| 5 | Paper 2 | HL | Parçacık kırınımı; de Broglie dalga boyu; dalga–parçacık ikiliği | AO2–AO3 | Show, Outline, Predict, Calculate | 9 | Orta |
| 6 | Paper 1B | HL | Durdurma potansiyeli–frekans verisinden h ve iş fonksiyonu; belirsizlik; sistematik hata | AO2–AO3 | Outline, Calculate, Determine, Explain | 10 | Orta–zor |

Bu set E.2'nin tamamını kapsamaz. Eksik kalanlar: şiddetin fotoakıma etkisinin nicel yorumu, eşik frekansının doğrudan hesabı,
Compton saçılmasının ışığın parçacık doğasına kanıt olarak yorumlanması (saçılan fotonun enerji ve momentum kaybı), Compton
kaymasının açıya bağlılığının yapılandırılmış soruda işlenmesi.

---

## Soru 1 — Paper 1A

Light of wavelength 310 nm is incident on a clean metal surface in a vacuum. The work function of the metal is 2.9 eV.

What is the maximum kinetic energy of the electrons emitted from the surface?

A. 1.1 eV
B. 2.9 eV
C. 4.0 eV
D. 6.9 eV

**Cevap: A**

**Çözüm.** Foton enerjisi = hc / λ = (6.63 × 10⁻³⁴ × 3.00 × 10⁸) / (310 × 10⁻⁹) = 6.42 × 10⁻¹⁹ J = 4.0 eV.
E<sub>max</sub> = hf − Φ = 4.0 − 2.9 = 1.1 eV.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | İş fonksiyonunun elektronun aldığı enerji olduğu düşünülür |
| C | İş fonksiyonu çıkarılmaz; foton enerjisinin tamamı kinetik enerji sayılır: 4.0 eV |
| D | İş fonksiyonu çıkarılacağına eklenir: 4.0 + 2.9 = 6.9 eV |

---

## Soru 2 — Paper 1A

An alpha particle and a proton have the same kinetic energy. Both move at speeds much less than the speed of light. The mass of the
alpha particle is four times the mass of the proton.

What is the ratio (de Broglie wavelength of the alpha particle) / (de Broglie wavelength of the proton)?

A. 1/4
B. 1/2
C. 1
D. 2

**Cevap: B**

**Çözüm.** E<sub>k</sub> = p² / 2m → p = √(2mE<sub>k</sub>). λ = h / p ∝ 1 / √m (aynı E<sub>k</sub> için).
Oran = √(m<sub>p</sub> / m<sub>α</sub>) = √(1/4) = 1/2.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | λ ∝ 1/m alınır (hızların eşit olduğu varsayılır): 1/4 |
| C | Kinetik enerjisi eşit parçacıkların dalga boyunun da eşit olduğu düşünülür (foton için geçerli ilişki maddeye uygulanır) |
| D | Oran ters kurulur: √(m<sub>α</sub> / m<sub>p</sub>) = 2 |

---

## Soru 3 — Paper 1A

A photon of wavelength 3.00 pm is scattered by an electron that is initially at rest. The photon is scattered through an angle of
180°. The change in wavelength of a photon scattered through an angle *θ* is

Δ*λ* = (*h* / *m*<sub>e</sub>*c*)(1 − cos *θ*)

where *h* / *m*<sub>e</sub>*c* = 2.43 pm.

What is the wavelength of the scattered photon?

A. 3.00 pm
B. 4.86 pm
C. 5.43 pm
D. 7.86 pm

**Cevap: D**

**Çözüm.** Δλ = 2.43 × (1 − cos 180°) = 2.43 × 2 = 4.86 pm. Saçılan fotonun dalga boyu = 3.00 + 4.86 = 7.86 pm.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | cos 180° = +1 alınır; kayma sıfır çıkar |
| B | Dalga boyu kayması, saçılan fotonun dalga boyu sanılır: 4.86 pm |
| C | (1 − cos θ) çarpanı 1 alınır (90° için geçerli değer): 3.00 + 2.43 = 5.43 pm |

---

## Soru 4 — Paper 1A

Monochromatic light is incident on a metal surface and the emission of photoelectrons is investigated.

Which observation **cannot** be explained by the wave model of light?

A. The photoelectric current is proportional to the intensity of the light.
B. Energy is transferred from the light to electrons in the metal.
C. No electrons are emitted below a certain frequency, however intense the light.
D. The emitted electrons have a range of kinetic energies.

**Cevap: C**

**Çözüm.** Dalga modelinde enerji sürekli aktarılır; yeterince şiddetli (ya da yeterince uzun süreli) her ışık, frekansı ne olursa
olsun elektron koparabilmelidir. Şiddetten bağımsız bir eşik frekansı ancak enerjisi hf olan fotonlarla açıklanır.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Foton modelinin her öngörüsünün dalga modeliyle çeliştiği sanılır; şiddet arttıkça daha çok elektron çıkması dalga modeliyle de uyumludur |
| B | Enerji aktarımının yalnızca parçacık modeline özgü olduğu düşünülür; dalgalar da enerji taşır |
| D | Kinetik enerji aralığının foton kanıtı olduğu sanılır; elektronların metalde farklı derinlik ve bağlanma enerjilerinde olması her iki modelde de bir aralık verir |

---

## Soru 5 — Paper 2 (9 puan)

Electrons are accelerated from rest through a potential difference of 150 V in a vacuum tube. The electron beam passes through a
thin film of graphite and then strikes a fluorescent screen. A pattern of bright concentric rings is seen on the screen.

> **Şekil:** Havası boşaltılmış cam tüp. Solda elektron tabancası (katot ve anot arasında 150 V), ortada ince grafit film, sağda
> floresan ekran. Ekranda merkezdeki parlak noktanın çevresinde eşmerkezli parlak halkalar. Diyagram ölçekli değildir.

**(a)** Show that the de Broglie wavelength of the electrons is about 1.0 × 10⁻¹⁰ m. [3]

**(b)** Outline how the pattern on the screen provides evidence for the wave nature of electrons. [2]

The accelerating potential difference is increased.

**(c)** Predict, with a reason, the change in the diameters of the rings. [2]

**(d)** Calculate, in eV, the energy of a photon that has the same wavelength as the electrons in (a). [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | kinetic energy = *eV* = 1.60 × 10⁻¹⁹ × 150 «= 2.4 × 10⁻¹⁷ J» ✓<br>*p* = √(2*m*<sub>e</sub>*E*<sub>k</sub>) = √(2 × 9.11 × 10⁻³¹ × 2.4 × 10⁻¹⁷) «= 6.6 × 10⁻²⁴ kg m s⁻¹» **OR** *v* = 7.3 × 10⁶ «m s⁻¹» ✓<br>*λ* = 6.63 × 10⁻³⁴ / 6.61 × 10⁻²⁴ = 1.00 × 10⁻¹⁰ «m» ✓ | *Answer must be given to at least 3 s.f. (1.00 × 10⁻¹⁰) from a visible substitution for MP3.* | 3 |
| 5. | b | | the rings are a diffraction / interference pattern ✓<br>diffraction / interference is a property of waves **OR** particles alone would give a single spot / no rings ✓ | *OWTTE*<br>*Accept reference to the spacing of atoms in graphite being comparable to the wavelength for MP2.* | 2 |
| 5. | c | | «greater speed / momentum so» the de Broglie wavelength decreases ✓<br>diffraction angles are smaller so the diameters decrease ✓ | *MP2 requires the direction of the change in diameter.* | 2 |
| 5. | d | | *E* = *hc* / *λ* = 6.63 × 10⁻³⁴ × 3.00 × 10⁸ / 1.0 × 10⁻¹⁰ «= 1.99 × 10⁻¹⁵ J» ✓<br>= 1.2 × 10⁴ «eV» ✓ | *Allow ECF from (a).* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `V = 150 V`, sabitler `e = 1.60e-19`, `m_e = 9.11e-31`, `h = 6.63e-34`, `c = 3.00e8` | |
| `E_k` | `e*V` | 2.40 × 10⁻¹⁷ J |
| `p` | `sqrt(2*m_e*E_k)` | 6.61 × 10⁻²⁴ kg m s⁻¹ |
| `lambda` | `h/p` | 1.003 × 10⁻¹⁰ m |
| `E_photon` | `h*c/lambda/e` | 1.240 × 10⁴ eV (λ = 1.0 × 10⁻¹⁰ m ile 1.243 × 10⁴ eV) |

---

## Soru 6 — Paper 1B (10 puan)

A student investigates the photoelectric effect using a vacuum photocell. Light from one of five light-emitting diodes (LEDs), each
emitting light of a different frequency *f*, is incident on the metal cathode of the photocell. A variable potential difference is
applied so that the anode is negative with respect to the cathode. For each LED the student increases the potential difference
until the photoelectric current just falls to zero and records this stopping potential *V*<sub>s</sub>.

> **Şekil:** Devre şeması. Fotosel (katot ve anot), ona seri bağlı duyarlı bir ampermetre, fotosele paralel bağlı bir voltmetre ve
> potansiyometre üzerinden bağlı bir doğru akım kaynağı; anot kaynağın eksi ucuna bağlıdır. LED, katodu aydınlatır.

| *f* / 10¹⁴ Hz | *V*<sub>s</sub> / V ± 0.04 V |
|---|---|
| 6.0 | 0.38 |
| 6.5 | 0.60 |
| 7.0 | 0.79 |
| 7.5 | 1.02 |
| 8.0 | 1.21 |

The uncertainty in *f* is negligible.

**(a)** Outline why a graph of *V*<sub>s</sub> against *f* is expected to be a straight line. [2]

**(b)** Calculate the percentage uncertainty in *V*<sub>s</sub> for the lowest frequency. [1]

The student plots *V*<sub>s</sub> against *f* with uncertainty bars. The gradient of the line of best fit is 4.16 × 10⁻¹⁵ V s. The
lines of maximum and minimum gradient have gradients of 4.55 × 10⁻¹⁵ V s and 3.75 × 10⁻¹⁵ V s. The line of best fit crosses the
*f*-axis at 5.08 × 10¹⁴ Hz.

**(c)** Determine the value of the Planck constant given by this experiment, with its absolute uncertainty. [3]

**(d)** Determine, in eV, the work function of the cathode using the line of best fit. [2]

**(e)** The student later finds that the voltmeter reads 0.05 V when the potential difference across it is zero. Explain the effect
of this error on the value of the Planck constant obtained in (c). [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *eV*<sub>s</sub> = *hf* − *Φ* **OR** maximum kinetic energy = *eV*<sub>s</sub> AND *E*<sub>max</sub> = *hf* − *Φ* ✓<br>*V*<sub>s</sub> = (*h*/*e*)*f* − *Φ*/*e* so the gradient *h*/*e* is constant / this has the form *y* = *mx* + *c* ✓ | | 2 |
| 6. | b | | «0.04 / 0.38 × 100 =» 11 «%» ✓ | *Accept 10 % or 10.5 %.* | 1 |
| 6. | c | | *h* = *e* × gradient = 1.60 × 10⁻¹⁹ × 4.16 × 10⁻¹⁵ «= 6.66 × 10⁻³⁴ J s» ✓<br>uncertainty in gradient = (4.55 − 3.75) × 10⁻¹⁵ / 2 = 0.40 × 10⁻¹⁵ «V s» ✓<br>*h* = (6.7 ± 0.6) × 10⁻³⁴ «J s» ✓ | *MP3: uncertainty to 1 s.f. and value to the same decimal place.*<br>*Allow (6.66 ± 0.64) × 10⁻³⁴ for MP1 and MP2 only.* | 3 |
| 6. | d | | *Φ* = *hf*₀ **OR** *Φ*/*e* = gradient × intercept on the *f*-axis ✓<br>«4.16 × 10⁻¹⁵ × 5.08 × 10¹⁴ =» 2.1 «eV» ✓ | *Allow ECF from (c).*<br>*Allow use of h = 6.63 × 10⁻³⁴ J s, also giving 2.1 eV.* | 2 |
| 6. | e | | every reading of *V*<sub>s</sub> is too large by the same amount / the line is shifted «upwards» parallel to itself / systematic error ✓<br>the gradient is unchanged so the value of *h* is not affected ✓ | *OWTTE*<br>*Do not award MP2 for "h is too large".* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `grad = 4.16e-15`, `grad_max = 4.55e-15`, `grad_min = 3.75e-15`, `f0 = 5.08e14`, `dV = 0.04`, `V1 = 0.38`, sabit `e = 1.60e-19` | |
| `pct` | `dV/V1*100` | %10.5 |
| `h` | `e*grad` | 6.66 × 10⁻³⁴ J s |
| `d_grad` | `(grad_max - grad_min)/2` | 0.40 × 10⁻¹⁵ V s |
| `d_h` | `e*d_grad` | 0.64 × 10⁻³⁴ J s |
| `phi_eV` | `grad*f0` | 2.11 eV |

### Şekil notu

Öğrenciye gösterilecek sürümde tablo ile birlikte belirsizlik çubuklu *V*<sub>s</sub>–*f* grafiği yer alır. Grafik aynı veriden kodla
üretilir (D-14). Tablodaki veriden hesaplanan en küçük kareler eğimi 4.16 × 10⁻¹⁵ V s, düşey eksen kesimi −2.11 V, *f*-ekseni kesimi
5.08 × 10¹⁴ Hz'dir. İlk ve son noktanın belirsizlik çubuklarının uçlarından geçen doğruların eğimleri 4.55 × 10⁻¹⁵ ve 3.75 × 10⁻¹⁵ V s'dir.
Soruda verilen değerler bunlardır. Bulunan h = (6.7 ± 0.6) × 10⁻³⁴ J s kabul edilen değerle (6.63 × 10⁻³⁴ J s) tutarlıdır.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?" / "Which …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–3 uygun (artan); Soru 4 cümle biçiminde seçenek (profilde azınlık biçim) |
| 1A: olumsuzluk sözcüğü koyu | Soru 4 ("cannot") uygun |
| 1A: doğru cevap konumu dengeli | A, B, D, C |
| Kapsam sınırı: Compton formülünün türetimi yok | Soru 3'te formül ve sabit soruda verildi; yalnızca uygulama istenir |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (3, 2, 2, 2; toplam 9) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | (a) Show that, (c) Predict; (d) verilen yaklaşık değeri kullanır |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE | Soru 5 ve 6 uygun |
| 1B: yaklaşık 10 puanlık deney sorusu, alt parçalar 1–3 puan | Soru 6 uygun (2, 1, 3, 2, 2; toplam 10) |
| 1B: tablo başlığı "büyüklük / birim ± belirsizlik" | Soru 6 uygun |
| 1B: öğrenci verilen grafiğe en uygun doğruyu çizer ve eğimi kendisi bulur | **Soru 6 uygun değil:** grafik üretilemediği için eğimler ve eksen kesimi metinde verildi. Grafik şablonu hazır olunca (c) ve (d) yeniden yazılmalı |
| 1B: düzenek şeması | Yalnızca metinle tarif edildi; çizim üretilmedi |
| Değer–birim yazımı, anlamlı basamak | Uygun; 1B'de eğimler 3 anlamlı basamak verildi, sonuç belirsizliğe göre yuvarlanır |
| Düzey etiketi | Tüm sorular HL (E.2 yalnızca HL düğümü); Soru 6 SL Paper 1B havuzuna girmez |

## Bağımsız kontrol

Tarih: 2026-10-11. Yazardan farklı bir kör çözücü soruları cevapları görmeden çözdü; tüm cevap anahtarlarını bağımsız olarak yeniden
üretti, çekirdek denklemlerini (nükleon sayısı ve yük korunumu) ve Paper 1B eğimlerini yeniden hesapladı. Bulgular:
[review/e2-review.md](review/e2-review.md). KRİTİK bulgu yok. Bu kontrol uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 5 (a) (DÜŞÜK):** "Show that" notu "at least 2 s.f." → "at least 3 s.f. (1.00 × 10⁻¹⁰)".
- **Soru 5 (d) (DÜŞÜK):** formül zincirinin son satırı ayrıştırıldı: 1.240 × 10⁴ eV (tam λ) ve 1.243 × 10⁴ eV (λ = 1.0 × 10⁻¹⁰ m). Markscheme cevabı 1.2 × 10⁴ eV değişmedi.
- **Soru 6 (c)–(d) (DÜŞÜK):** değişiklik yapılmadı; eğimlerin metinde verilmesi zaten "Biçim uyumu" tablosunda "uygun değil" olarak yazılı ve grafik şablonuna bağlı.
- **Soru 4:** çözücü tek doğru cevabı (C) doğruladı ve D seçeneğinin değiştirilmemesini önerdi; değiştirilmedi.

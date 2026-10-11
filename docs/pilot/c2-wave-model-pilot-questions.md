# Pilot soru seti: C.2 Dalga modeli

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneği](a1-kinematics-pilot-questions.md) ile aynı yapıda yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü C.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgündür.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile yeniden hesaplandı.
> Sabitler: c = 3.00 × 10⁸ m s⁻¹; havada ses hızı 340 m s⁻¹ (kullanıldığı soruda verildi); deniz suyunda ses hızı 1500 m s⁻¹ (soruda
> verildi). Veri kitapçığı değerleri uzmanca teyit edilmeli.
> **Doğrulanmayan:** (1) bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; (2) bilinen bir sınav sorusuna benzerlik açısından uzman
> gözüyle bakılmadı; (3) Soru 2 ve Soru 5 (a), (c), (e) niteldir, kodla doğrulanamaz; (4) Soru 5'te su yüzeyi dalgasının "enine dalga"
> olarak modellenmesi bir basitleştirmedir (gerçekte parçacıklar yaklaşık çembersel hareket eder); uzman bu bağlamı uygun bulmayabilir.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (C.2) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | v = fλ; ses dalgasının hızı ortama bağlıdır | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Enine dalgada ortam parçacığının hareket yönü (konuma göre yer değiştirme) | AO3 | — | 1 | Orta |
| 3 | Paper 1A | SL | Boyuna dalga; zamana göre yer değiştirmeden periyot; sıkışma–seyrelme aralığı | AO2 | — | 1 | Orta |
| 4 | Paper 1A | SL | Elektromanyetik dalganın doğası; v = fλ, önekler | AO2 | — | 1 | Kolay |
| 5 | Paper 2 | SL | Enine dalga tanımı; v = fλ; konuma göre parçacık hareketi; dalganın enerji taşıması | AO1–AO3 | State, Calculate, Determine, Show that, Explain | 9 | Orta |

Bu set C.2'nin tamamını kapsamaz. Eksik kalanlar: yer değiştirme–konum ve yer değiştirme–zaman grafiklerinin çizimi ve birlikte
yorumu; ses dalgasında basınç–yer değiştirme ilişkisi; mekanik–elektromanyetik dalga farkının açıklanması (ortam gereksinimi);
elektromanyetik spektrum bölgelerinin mertebeleri.

---

## Soru 1 — Paper 1A

A dolphin emits a sound wave of frequency 150 kHz. The speed of sound in seawater is 1500 m s⁻¹.

What is the wavelength of the sound wave in seawater?

A. 0.010 m
B. 10 m
C. 100 m
D. 2000 m

**Cevap: A**

**Çözüm.** λ = v / f = 1500 / (150 × 10³) = 0.010 m.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | kHz öneki çevrilmez: 1500 / 150 = 10 m |
| C | Oran ters kurulur (f / v): 150 000 / 1500 = 100 |
| D | Ses dalgası elektromanyetik dalga gibi düşünülür, ışık hızı kullanılır: 3.00 × 10⁸ / (150 × 10³) = 2000 m |

---

## Soru 2 — Paper 1A

A transverse wave travels to the right along a horizontal rope. At one instant, a point P on the rope is at its equilibrium
position. At this instant the crest nearest to P is 0.10 m to the left of P and the trough nearest to P is 0.10 m to the right
of P. At a crest the rope is displaced upwards.

> **Şekil:** Yatay ipte sağa doğru ilerleyen sinüs biçimli dalganın bir anlık görüntüsü. P noktası denge çizgisinin üzerinde; solunda
> 0.10 m uzakta bir tepe, sağında 0.10 m uzakta bir çukur. Dalganın ilerleme yönü sağa dönük bir okla gösterilir. Soru, metindeki
> bilgiyle şekil olmadan çözülebilir.

What is the direction of motion of P at this instant?

A. to the left
B. to the right
C. downwards
D. upwards

**Cevap: D**

**Çözüm.** Dalga sağa ilerler; P'nin solundaki tepe kısa süre sonra P'ye ulaşır. Bu yüzden P yukarı doğru hareket etmektedir. Enine
dalgada parçacık yalnızca ilerleme yönüne dik doğrultuda hareket eder.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Parçacığın yaklaşan tepeye doğru (dalganın geldiği yöne) çekildiği düşünülür |
| B | Ortam parçacıklarının dalgayla birlikte ilerlediği sanılır |
| C | Anlık görüntü bir "yamaç" gibi okunur: ip tepeden çukura doğru indiği için P'nin de aşağı indiği düşünülür (dalga sola ilerleseydi doğru olurdu) |

---

## Soru 3 — Paper 1A

A sound wave travels through air. The speed of sound in air is 340 m s⁻¹. A graph of displacement against time is drawn for one
particle of the air. On the graph, the time between two adjacent instants at which the displacement is zero is 2.0 ms.

What is the distance between the centre of a compression and the centre of the nearest rarefaction?

A. 0.34 m
B. 0.68 m
C. 1.4 m
D. 2.7 m

**Cevap: B**

**Çözüm.** Art arda iki sıfır geçişi yarım periyottur: T = 4.0 ms. λ = vT = 340 × 4.0 × 10⁻³ = 1.36 m. Bir sıkışmanın merkezi ile en
yakın seyrelmenin merkezi arası yarım dalga boyudur: 0.68 m.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | 2.0 ms tam periyot sanılır: λ = 340 × 2.0 × 10⁻³ = 0.68 m; yarısı 0.34 m |
| C | Sıkışma–seyrelme aralığı tam dalga boyu alınır: 1.36 ≈ 1.4 m |
| D | 2.0 ms çeyrek periyot sanılır (T = 8.0 ms → λ = 340 × 8.0 × 10⁻³ = 2.72 m) ve sıkışma–seyrelme aralığı tam dalga boyu alınır: 2.7 m |

---

## Soru 4 — Paper 1A

A microwave oven produces electromagnetic waves of frequency 2.5 GHz.

What is the wavelength of these waves in air?

A. 1.4 × 10⁻⁷ m
B. 1.2 × 10⁻⁴ m
C. 0.12 m
D. 8.3 m

**Cevap: C**

**Çözüm.** Elektromanyetik dalga havada yaklaşık c hızıyla ilerler. λ = c / f = 3.00 × 10⁸ / (2.5 × 10⁹) = 0.12 m.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Elektromanyetik dalga için ses hızı kullanılır: 340 / (2.5 × 10⁹) = 1.4 × 10⁻⁷ m |
| B | G öneki 10¹² alınır: 3.00 × 10⁸ / (2.5 × 10¹²) = 1.2 × 10⁻⁴ m |
| D | Oran ters kurulur (f / c): 2.5 × 10⁹ / (3.00 × 10⁸) = 8.3 |

---

## Soru 5 — Paper 2 (9 puan)

Water waves travel across a lake towards the shore. A small fishing float on the surface moves up and down as the waves pass.
The wave can be modelled as a transverse wave. The float completes 12 oscillations in 30 s. The amplitude of the oscillations is
4.0 cm and the distance between adjacent crests is 3.5 m.

**(a)** State what is meant by a transverse wave. [1]

**(b)** Calculate the speed of the wave. [2]

A second float is 5.25 m from the first float, measured along the direction in which the wave travels.

**(c)** Determine the displacement of the second float at an instant when the first float is at a crest. [2]

**(d)** Show that the total distance moved by the first float in 30 s is about 2 m. [2]

**(e)** The shore is 21 m from the first float. A student predicts that the waves will carry the float to the shore in 15 s.
Explain why this prediction is incorrect. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the oscillations «of the particles of the medium» are perpendicular to the direction of energy transfer / of propagation of the wave ✓ | *Do not accept "the wave moves up and down".* | 1 |
| 5. | b | | *T* = 30 / 12 = 2.5 «s» **OR** *f* = 0.40 «Hz» ✓<br>*v* = 0.40 × 3.5 = 1.4 «m s⁻¹» ✓ | | 2 |
| 5. | c | | 5.25 / 3.5 = 1.5 «wavelengths» **OR** the floats oscillate in antiphase ✓<br>displacement = −4.0 «cm» **OR** 4.0 cm below the equilibrium position / at a trough ✓ | *Second mark requires the direction (sign or words).* | 2 |
| 5. | d | | distance in one oscillation = 4 × 4.0 «= 16 cm» ✓<br>12 × 16 = 192 «cm» **OR** 1.9 «m» ✓ | *Answer must be seen to at least 2 s.f. or the working must be shown.* | 2 |
| 5. | e | | a wave transfers energy, not matter / the medium is not transported ✓<br>the float «only» oscillates «vertically» about a fixed / mean position ✓ | *OWTTE*<br>*Award [1 max] for "21 m in 15 s is the speed of the wave, not of the float" without further explanation.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `N = 12`, `t = 30 s`, `A = 0.040 m`, `lam = 3.5 m`, `dx = 5.25 m` | |
| `T` | `t/N` | 2.5 s |
| `f` | `1/T` | 0.40 Hz |
| `v` | `f*lam` | 1.4 m s⁻¹ |
| `n_lam` | `dx/lam` | 1.5 (zıt faz) → yer değiştirme −4.0 cm |
| `d_total` | `N*4*A` | 1.92 m |
| Denetim (e) | `21/15` | 1.4 m s⁻¹ = dalga hızı; öğrencinin yanılgısı bu değere dayanır |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1, 3, 4 uygun (artan); Soru 2 dört yön (sözel) |
| 1A: doğru cevap harfleri dengeli | A, D, B, C |
| 1A: şekil olmadan çözülebilir | Soru 2'de şekil sözle tarif edildi; gerekli tüm bilgi metinde |
| 1A: yuvarlak, temiz sayılar | Uygun; Soru 1'de dört seçenek de düz yazımla, Soru 4'te seçenekler geniş bir aralığa yayıldığı için bilimsel gösterimle (C ve D düz) verildi |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (1, 2, 2, 2, 2; toplam 9). SL kâğıdında kısa soru 4–6 puan gözlendi; 9 puan HL aralığının üst sınırıdır — SL kâğıdı için (d) ya da (e) çıkarılabilir |
| Paper 2: "Show that" kalıbı ve en az bir AO3 parçası | Soru 5 (c) Determine, (d) Show that, (e) Explain |
| Markscheme: dört sütunlu tablo, ✓, « », OR, OWTTE | Soru 5 uygun |
| Paper 2: şekil | **Eksik:** Soru 5 için şekil tarif edilmedi; soru şekilsiz çözülebilir |
| Müfredat sınırı | Spektrum mertebesi ezberi istenmedi; "faz" kavramı (c)'de yalnızca "1.5 dalga boyu" üzerinden kullanıldı |
| Değer–birim yazımı (m s⁻¹), 2 anlamlı basamak | Uygun |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, cevapları görmeyen bağımsız bir kör çözücü tarafından çözüldü; çözücü tüm cevap
anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti (KRİTİK bulgu yok). Bulgular:
[review/c2-review.md](review/c2-review.md). Bu, uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile, dosyanın son metni üzerinden yeniden denetlendi):

- **Soru 1 (DÜŞÜK):** seçenekler tek biçime getirildi: 1.0 × 10⁻² m, 10 m, 1.0 × 10² m, 2.0 × 10³ m → 0.010 m, 10 m, 100 m, 2000 m. Değerler aynı, anahtar A.
- **Soru 3 (DÜŞÜK):** D çeldiricisinin dayanağı yeniden yazıldı (2.0 ms'nin çeyrek periyot sanılması ve tam dalga boyu alınması); sayı (2.7 m) değişmedi.
- **Soru 5 (DÜŞÜK):** SL için 9 puanın uzun olduğu notu "Biçim uyumu" tablosunda zaten vardı; soru bölünmedi. Bölme kararı (5 + 4 puan) sınav kâğıdı derlenirken verilmeli.
- **Uygulanmayan:** Soru 4'ün seçenekleri (1.4 × 10⁻⁷ m, 1.2 × 10⁻⁴ m, 0.12 m, 8.3 m) karışık yazımda bırakıldı; incelemede bulgu olarak geçmiyor ve 10⁻⁷ mertebesinin düz yazımı okunaksız olur.

# Pilot soru seti: B.2 Sera etkisi

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü B.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; PDF açılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Stefan-Boltzmann sabiti σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴ alındı ve gereken soruda
> verildi; veri kitapçığı değeri uzmanca teyit edilmeli.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; nitel sorular (Soru 3, Soru 5a ve 5c) kodla denetlenemez;
> gezegenler kurgusaldır, verileri gerçek bir gök cismine ait değildir; Soru 5(d)'deki "etkin yayıcılık" modelinin rehberin beklediği
> enerji dengesi modeliyle örtüştüğü uzmanca teyit edilmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle bakılmadı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (B.2) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Güneş sabiti, S/4 ortalaması ve albedo ile soğurulan ortalama şiddet | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | Denge sıcaklığı için enerji dengesi; orantı akıl yürütmesi | AO3 | — | 1 | Orta–zor |
| 3 | Paper 1A | SL | Sera gazlarının kızılötesi soğurması (rezonans modeli) | AO1 | — | 1 | Kolay |
| 4 | Paper 1A | SL | Albedonun enerji dengesinden belirlenmesi | AO2 | — | 1 | Orta |
| 5 | Paper 2 | SL | S/4 ortalaması; denge sıcaklığı; sera etkisi mekanizması; yayıcılık | AO2–AO3 | Explain, Show that, Determine | 9 | Orta–zor |

Bu set B.2'nin tamamını kapsamaz. Eksik kalanlar: başlıca sera gazlarının adları ve doğal / insan kaynaklı kaynakları; molekül enerji
düzeyleri modeliyle soğurma; artmış sera etkisinin nedenleri; yayıcılığın tanımdan doğrudan hesabı; yüzey–atmosfer alışverişini
ayrı ayrı içeren iki katmanlı enerji dengesi; albedonun günlük ve mevsimlik değişimi.

Kapsam sınırı kontrolü: enerji dengesi soruları tek katmanlı (Soru 1, 2, 4, 5b) ya da yüzey + etkin yayıcılık (Soru 5d) düzeyinde;
sınırın izin verdiği yüzey–atmosfer alışverişinin ötesine geçilmiyor. Türev ya da integral yok.

---

## Soru 1 — Paper 1A

A planet orbits a star. At the orbit of the planet, the intensity of the radiation from the star is 600 W m⁻². The albedo of the
planet is 0.30.

What is the mean power absorbed per unit area of the surface of the planet?

A. 45 W m⁻²
B. 105 W m⁻²
C. 150 W m⁻²
D. 420 W m⁻²

**Cevap: B**

**Çözüm.** Gezegen ışınımı π*R*² kesitiyle yakalar, enerji 4π*R*² yüzeye dağılır: ortalama gelen şiddet 600 / 4 = 150 W m⁻².
Soğurulan kesir 1 − 0.30 = 0.70. Soğurulan ortalama şiddet = 150 × 0.70 = 105 W m⁻².

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Albedo soğurulan kesir sanılır (yansıyan kısım hesaplanır): 600 × 0.30 / 4 = 45 |
| C | Albedo hesaba katılmaz: 600 / 4 = 150 |
| D | Yüzey üzerinde ortalama alınmaz (4'e bölünmez): 600 × 0.70 = 420 |

---

## Soru 2 — Paper 1A

A planet without an atmosphere radiates as a black body and has a uniform equilibrium surface temperature *T*. The planet is
moved to an orbit at **twice** the distance from its star. The albedo of the planet does not change.

What is the new equilibrium surface temperature of the planet?

A. *T* ⁄ 4
B. *T* ⁄ 2
C. *T* ⁄ √2
D. *T* ⁄ ⁴√2

**Cevap: C**

**Çözüm.** Yıldız ışınımının şiddeti uzaklığın karesiyle ters orantılıdır: yeni şiddet *S*/4. Enerji dengesi: (1 − α)*S*/4 = σ*T*⁴,
yani *T* ∝ *S*<sup>1/4</sup>. Yeni sıcaklık = *T* × (1⁄4)<sup>1/4</sup> = *T* / √2 (≈ 0.71*T*).

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Sıcaklık şiddetle doğru orantılı alınır (*T* ∝ *S*): *T* / 4 |
| B | Sıcaklık uzaklıkla ters orantılı alınır (*T* ∝ 1/*d*): *T* / 2 |
| D | Şiddet uzaklığın karesiyle değil kendisiyle ters orantılı alınır (*S* ∝ 1/*d*): *T* × (1⁄2)<sup>1/4</sup> ≈ 0.84*T* |

---

## Soru 3 — Paper 1A

Carbon dioxide in the atmosphere absorbs infrared radiation emitted by the surface of the Earth.

What is the reason that carbon dioxide molecules absorb this radiation strongly?

A. The frequency of the radiation matches a natural frequency of vibration of the molecules.
B. The photons of the radiation have enough energy to ionize the molecules.
C. The photons of the radiation have more energy than photons of visible light.
D. The molecules reflect the radiation back towards the surface.

**Cevap: A**

**Çözüm.** Rezonans modeli: kızılötesi ışınımın frekansı molekülün doğal titreşim frekansına yakın olduğunda enerji aktarımı en
büyüktür; molekül ışınımı soğurur ve sonra her yöne yeniden yayar.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Soğurma iyonlaşmayla karıştırılır; kızılötesi fotonun enerjisi iyonlaşma için çok küçüktür |
| C | Kızılötesi ile görünür ışığın foton enerjileri ters sıralanır (kızılötesinin frekansı daha düşüktür) |
| D | "Sera gazları ısıyı yansıtır" yanılgısı; süreç yansıma değil, soğurma ve her yöne yeniden yaymadır |

---

## Soru 4 — Paper 1A

The mean intensity of the radiation from a star that is incident on a planet, averaged over the whole surface of the planet, is
340 W m⁻². The planet is in thermal equilibrium and radiates a mean intensity of 238 W m⁻² into space.

What is the albedo of the planet?

A. 0.18
B. 0.30
C. 0.43
D. 0.70

**Cevap: B**

**Çözüm.** Dengede soğurulan şiddet yayılana eşittir: 238 W m⁻². Yansıyan (saçılan) şiddet = 340 − 238 = 102 W m⁻².
Albedo = yansıyan / gelen = 102 / 340 = 0.30.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Yansıyan güç, gelen ile yayılan şiddetlerin toplamına oranlanır: 102 / (340 + 238) = 0.18 |
| C | Yansıyan güç gelen yerine soğurulan güce oranlanır: 102 / 238 = 0.43 |
| D | Soğurulan kesir albedo sanılır: 238 / 340 = 0.70 |

---

## Soru 5 — Paper 2 (9 puan)

A planet orbits a star. At the orbit of the planet, the intensity of the radiation from the star is 880 W m⁻². The albedo of the
planet is 0.28.

Stefan-Boltzmann constant σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴

**(a)** Explain why the mean intensity of the radiation from the star, averaged over the whole surface of the planet, is
220 W m⁻². [2]

**(b)** Show that, if the planet had no atmosphere and radiated as a black body, its equilibrium surface temperature would be
about 230 K. [3]

The planet has an atmosphere that contains carbon dioxide. The measured mean surface temperature of the planet is 260 K.

**(c)** Explain how the carbon dioxide in the atmosphere causes the surface temperature to be higher than the value in (b). [2]

In a simple model, the planet together with its atmosphere radiates into space as a body of temperature 260 K and emissivity *e*.

**(d)** Determine *e*. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the planet intercepts the radiation over «its cross-sectional» area π*R*² ✓<br>this power is averaged over the «whole» surface area 4π*R*², «so the mean intensity is 880 / 4» ✓ | *OWTTE*<br>*Do not award marks for "880 / 4 = 220" without a reason.* | 2 |
| 5. | b | | absorbed intensity = 0.72 × 220 «= 158 W m⁻²» ✓<br>158.4 = 5.67 × 10⁻⁸ × *T*⁴ **OR** *T* = (158.4 / 5.67 × 10⁻⁸)<sup>1/4</sup> ✓<br>*T* = 229.9 «K» ✓ | *Answer 230 K is given; award the third mark only if 229.9 or the complete substitution is seen.* | 3 |
| 5. | c | | carbon dioxide absorbs «some of» the infrared radiation emitted by the surface ✓<br>and re-emits it in all directions, so part of it returns to the surface ✓<br>the surface receives more power «than from the star alone» and must be at a higher temperature to radiate enough for equilibrium ✓ | *OWTTE*<br>*Do not accept "reflects" or "traps heat" for the second mark.* | 2 max |
| 5. | d | | *e* × 5.67 × 10⁻⁸ × 260⁴ = 158 **OR** *e* = (230 / 260)⁴ ✓<br>*e* = 0.61 ✓ | *Allow ECF from (b).*<br>*Both routes give 0.61. Accept 0.62 from the absorbed intensity rounded to 160 W m⁻².*<br>*Do not award marks for e = 1 − albedo = 0.72.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `S = 880 W/m^2`, `albedo = 0.28`, `T_s = 260 K`; sabit `sigma = 5.67e-8 W/(m^2 K^4)` | |
| `I_mean` | `S/4` | 220 W m⁻² |
| `I_abs` | `(1 - albedo)*I_mean` | 158.4 W m⁻² |
| `T_eq` | `(I_abs/sigma)**0.25` | 229.9 K |
| `I_bb` | `sigma*T_s**4` | 259.1 W m⁻² |
| `e` | `I_abs/I_bb` | 0.611 (`(230/T_s)**4` yolu 0.612) |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1 artan; Soru 2 artan (0.25*T*, 0.50*T*, 0.71*T*, 0.84*T*); Soru 4 artan; Soru 3 cümle seçenekli (profilde azınlık biçimi) |
| 1A: olumsuzluk / kritik sözcük koyu | Soru 2 ("twice") uygun; olumsuz kök yok |
| 1A: doğru cevap konumu dengeli | B, C, A, B (D yok; Soru 4'teki çeldirici değişikliğinin sonucu, aşağıda "Bağımsız kontrol") |
| 1A: şekil olmadan çözülebilir | Soru 1–4 şekil gerektirmiyor |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 3, 2, 2; toplam 9) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | Soru 5 uygun: (a), (c) Explain; (b) Show that; (d) Determine |
| Markscheme: dört sütunlu tablo, ✓, « », OR, max, ECF, OWTTE | Soru 5 uygun; (c) "2 max" (üç maddeden ikisi) |
| Değer–birim yazımı (W m⁻²), 2–3 anlamlı basamak | Uygun |
| Paper 2: şekil | Soru 5(a) için kesit alanı / küre yüzeyi şeması yararlı olur ama gerekli değil; üretilmedi |
| Paper 2: cevap kutusu, noktalı satırlar | Bu taslakta yok; yayın şablonunda eklenecek |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından bağımsız bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları ve
markscheme sonuçları bağımsız olarak yeniden üretildi (KRİTİK bulgu yok). Ayrıntı: [review/b2-review.md](review/b2-review.md).
Bu kontrol uzman incelemesinin yerine geçmez.

İnceleme sonucu yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 5, ORTA-1 ve ORTA-2:** veri yeniden tasarlandı: albedo 0.25 → 0.28, ölçülen yüzey sıcaklığı 250 K → 260 K. Sonuçlar:
  soğurulan şiddet 165 → 158.4 W m⁻²; (b) 232.3 K → 229.9 K ("about 230 K" artık neredeyse tam); (d) 0.745 / 0.716 (yola bağlı) →
  her iki yoldan 0.61 (0.611 ve 0.612). Yanlış yöntem "e = 1 − albedo" artık 0.72 veriyor ve doğru cevapla çakışmıyor; markscheme
  notuna açıkça yazıldı. 0.72–0.75 kabul aralığı kaldırıldı. (a) değişmedi.
- **Soru 4, DÜŞÜK-1:** fiziksel olarak olanaksız 1.4 çeldiricisi 0.18 ile değiştirildi (102 / 578 = 0.176). Seçenekler artan sıraya
  alındı (0.18, 0.30, 0.43, 0.70); doğru cevap D → B. Tek doğru seçenek var; hiçbir iki seçenek yuvarlamadan sonra eşit değil.
  Yan etki: dosyadaki doğru cevap konumları B, C, A, D → B, C, A, B oldu.
- **DÜŞÜK-2 (SL kısa soruda 9 puan) ve DÜŞÜK-3 (etkin yayıcılık modelinin rehberle uyumu):** değişiklik yapılmadı; ikisi de uzman
  teyidi bekleyen kayıtlar.

# Pilot soru seti: E.5 Füzyon ve yıldızlar

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Yazım ölçütleri: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Yapı örneği: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Kaynak:** yalnızca müfredat düğümü E.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve genel
> fizik. Hiçbir sınav kâğıdı, markscheme, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; yıldızlar ve senaryolar kurgusaldır.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi. Kullanılan
> sabitler: σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴, Güneş'in ışınım gücü L☉ = 3.83 × 10²⁶ W, 1 pc = 3.26 ly, 1 ly = 9.46 × 10¹⁵ m (veri kitapçığı
> değerleri uzmanca teyit edilmeli).
> **Doğrulanmayan:**
> - Bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. sondaki "Bağımsız kontrol"). Bilinen bir sınav sorusuna benzerlik
>   açısından uzman gözüyle bakılmadı.
> - Bellekten gelen astrofizik bilgileri: 20 000 K sıcaklıkta bir ana kol yıldızının ışınım gücünün Güneş'inkinin binlerce katı olduğu
>   (Soru 3'te tek doğru cevabın dayanağı); 1.2 Güneş kütleli bir yıldızın kırmızı dev → gezegenimsi bulutsu → beyaz cüce yolunu
>   izlediği (Soru 6 (d)); Soru 6'daki kurgusal yıldızın (M = 1.2 M☉, L ≈ 1.9 L☉, T = 6200 K, R ≈ 1.2 R☉) ana kol için gerçekçi olduğu
>   (L ∝ M^3.5 yaklaşık ilişkisi ve R☉ = 6.96 × 10⁸ m bellekten; soruda kullanılmaz).
> - Soru 6'da görünür parlaklık ve b = L/4πd² ilişkisi müfredatta B.1 altında geçer; E.5'in "yıldız yarıçapının belirlenmesi" kazanımı
>   için gerekli olduğu varsayılarak kullanıldı ve kapsam tablosunda ikincil düğüm olarak yazıldı.
> - Soru 5 yalnızca basınç–kütle çekimi dengesini ölçer; büzülen çekirdeğin ısınması (müfredat analizinde açıkça yazmıyor) sorulmaz.
>   Füzyon hızı azalınca dışa doğru basıncın azaldığı bilgisi kökte verilir.
> - Soru 6 (d): yıldız kütlesi için sayısal eşiklerin (süpernova sınırı vb.) kapsamda olup olmadığı teyit edilmedi; kütle, bu eşiklerden
>   uzak olacak biçimde seçildi.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (E.5) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Iraklık açısıyla uzaklık; parsek–ışık yılı dönüşümü | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Yıldız yarıçapının ışınım gücü ve sıcaklıktan belirlenmesi (oran) | AO3 | — | 1 | Orta |
| 3 | Paper 1A | SL | HR diyagramının bölgeleri | AO2 | — | 1 | Orta |
| 4 | Paper 1A | SL | Füzyon koşulları: yüksek sıcaklığın gerekçesi | AO2 | — | 1 | Kolay |
| 5 | Paper 1A | SL | Yıldız dengesi: ışınım basıncı ve kütle çekimi | AO3 | — | 1 | Orta |
| 6 | Paper 2 | SL | Iraklık → uzaklık; birim dönüşümü; ışınım gücü (ikincil düğüm: B.1, b = L/4πd²); yarıçap; kütlenin evrime etkisi | AO2–AO3 | Show, Calculate, Determine, Outline | 9 | Orta |

Bu set E.5'in tamamını kapsamaz. Eksik kalanlar: füzyonda açığa çıkan enerjinin kütle farkından hesabı, yüksek yoğunluk (basınç)
koşulu, büyük kütleli yıldızların evrimi (süperdev, süpernova, nötron yıldızı, kara delik), HR diyagramında evrim yolunun çizimi,
AU dönüşümü, ıraklık yönteminin sınırı (yalnızca yakın yıldızlar).

---

## Soru 1 — Paper 1A

The parallax angle of a star measured from Earth is 0.040 arc-seconds. 1 pc = 3.26 ly.

What is the distance from Earth to the star?

A. 0.13 ly
B. 7.7 ly
C. 25 ly
D. 82 ly

**Cevap: D**

**Çözüm.** d (pc) = 1 / p (yay saniyesi) = 1 / 0.040 = 25 pc. 25 × 3.26 = 81.5 ≈ 82 ly.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Uzaklık ıraklık açısıyla doğru orantılı alınır: 0.040 × 3.26 = 0.13 |
| B | Dönüşüm ters yapılır: 25 / 3.26 = 7.7 |
| C | Parsek cinsinden bulunan değer ışık yılına çevrilmez: 25 |

---

## Soru 2 — Paper 1A

Star X has four times the luminosity of the Sun. The surface temperature of star X is half the surface temperature of the Sun.
Both stars radiate as black bodies.

What is the ratio (radius of star X) / (radius of the Sun)?

A. 0.5
B. 4
C. 8
D. 64

**Cevap: C**

**Çözüm.** L = σ(4πR²)T⁴ → R² ∝ L / T⁴. R² oranı = 4 / (½)⁴ = 64. Yarıçap oranı = √64 = 8.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Sıcaklık oranı ters çevrilmez: R² = 4 × (½)⁴ = 0.25 → 0.5 |
| B | Sıcaklığın üssü yanlış alınır (R ∝ √L / T): 2 / 0.5 = 4 |
| D | Karekök alınmaz; R² oranı verilir: 64 |

---

## Soru 3 — Paper 1A

On a Hertzsprung–Russell (HR) diagram, luminosity is plotted on the vertical axis and surface temperature on the horizontal axis.
A star has a surface temperature of 20 000 K and a luminosity of 0.01 *L*☉, where *L*☉ is the luminosity of the Sun.

> **Şekil:** HR diyagramı. Düşey eksen: ışınım gücü / L☉, logaritmik ölçek, 10⁻⁴ ile 10⁶ arası. Yatay eksen: yüzey sıcaklığı / K,
> soldan sağa azalan (40 000 K'den 2500 K'e). Ana kol sol üstten sağ alta uzanan bant; kırmızı devler ve süperdevler sağ üstte;
> beyaz cüceler sol altta. Bölgeler şekilde etiketlenmemiştir. (Soru şekil olmadan çözülebilir.)

Which type of star is this?

A. White dwarf
B. Main-sequence star
C. Red giant
D. Supergiant

**Cevap: A**

**Çözüm.** Yıldız Güneş'ten çok daha sıcak ama çok daha sönüktür; diyagramın sol alt bölgesindedir. Yüksek sıcaklıkta düşük ışınım
gücü çok küçük bir yüzey alanı gerektirir: beyaz cüce.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Ana kolun diyagramın her yerinden geçtiği düşünülür; bu sıcaklıktaki ana kol yıldızı Güneş'ten çok daha parlaktır |
| C | Düşük ışınım gücü "soğuk ve büyük" yıldızla ilişkilendirilir; kırmızı devler soğuk ve Güneş'ten parlaktır |
| D | Yüksek sıcaklık tek başına "çok büyük yıldız" olarak yorumlanır; süperdevlerin ışınım gücü çok yüksektir |

---

## Soru 4 — Paper 1A

Nuclear fusion of hydrogen takes place in the core of a main-sequence star, where the temperature is very high.

Why is a very high temperature needed for fusion?

A. To remove the electrons from the hydrogen atoms
B. To give nuclei enough kinetic energy to overcome their electric repulsion
C. To increase the binding energy per nucleon of the hydrogen nuclei
D. To produce enough radiation pressure to balance gravity

**Cevap: B**

**Çözüm.** Çekirdekler pozitif yüklüdür ve birbirini iter. Güçlü çekirdek kuvvetinin etkili olacağı kadar yaklaşabilmeleri için
kinetik enerjilerinin, yani sıcaklığın çok yüksek olması gerekir.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | İyonlaşma ile füzyon koşulu karıştırılır; iyonlaşma çok daha düşük sıcaklıklarda gerçekleşir |
| C | Bağlanma enerjisinin sıcaklıkla değiştiği düşünülür; bu, çekirdeğin sıcaklıktan bağımsız bir özelliğidir |
| D | Füzyonun sonucu (ışınım basıncı) füzyonun koşuluyla karıştırılır |

---

## Soru 5 — Paper 1A

A main-sequence star is in equilibrium. The rate of fusion in the core of the star then decreases, so that the outward force due to
radiation pressure in the core decreases.

What happens to the core as a result?

A. It contracts, because the gravitational force is now greater than the outward force due to pressure.
B. It expands, because the gravitational force is now less than the outward force due to pressure.
C. It stays the same size, because the gravitational force does not depend on the rate of fusion.
D. It expands, because a lower rate of fusion reduces the gravitational force on the core.

**Cevap: A**

**Çözüm.** Dengede içe doğru kütle çekimi ile dışa doğru basınç kuvveti eşittir. Füzyon hızı azalınca dışa doğru kuvvet azalır, kütle
çekimi değişmez; bileşke kuvvet içe doğrudur ve çekirdek büzülür.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Kuvvet dengesi ters kurulur: azalan basıncın genleşmeye yol açtığı düşünülür |
| C | Kütle çekiminin değişmemesinden dengenin de değişmediği sonucu çıkarılır; denge iki etkinin eşitliğidir |
| D | Kütle çekiminin füzyondan kaynaklandığı ya da füzyon hızıyla değiştiği düşünülür; kütle çekimi yıldızın kütlesine bağlıdır |

---

## Soru 6 — Paper 2 (9 puan)

Star K is a main-sequence star. Observations of star K from Earth give the following data.

| Parallax angle / arc-second | Apparent brightness / W m⁻² | Surface temperature / K |
|---|---|---|
| 0.125 | 9.5 × 10⁻¹⁰ | 6200 |

1 pc = 3.26 ly; 1 ly = 9.46 × 10¹⁵ m; *σ* = 5.67 × 10⁻⁸ W m⁻² K⁻⁴.

**(a)** Show that the distance from Earth to star K is about 2.5 × 10¹⁷ m. [2]

**(b)** Calculate the luminosity of star K. [2]

**(c)** Determine the radius of star K. [3]

**(d)** The mass of star K is 1.2 times the mass of the Sun. Outline the evolution of star K after it leaves the main sequence. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *d* = 1 / 0.125 = 8.0 «pc» ✓<br>*d* = 8.0 × 3.26 × 9.46 × 10¹⁵ = 2.47 × 10¹⁷ «m» ✓ | *Answer must be given to at least 3 s.f. for MP2.* | 2 |
| 6. | b | | *L* = 4π*d*²*b* = 4π × (2.47 × 10¹⁷)² × 9.5 × 10⁻¹⁰ ✓<br>*L* = 7.3 × 10²⁶ «W» ✓ | *Allow use of 2.5 × 10¹⁷ m, giving 7.5 × 10²⁶ W.* | 2 |
| 6. | c | | *L* = *σ*(4π*R*²)*T*⁴ rearranged **OR** *R* = √(*L* / 4π*σT*⁴) ✓<br>correct substitution: *R*² = 7.3 × 10²⁶ / (4π × 5.67 × 10⁻⁸ × 6200⁴) ✓<br>*R* = 8.3 × 10⁸ «m» ✓ | *Allow ECF from (b).*<br>*Accept answers in the range 8.2–8.5 × 10⁸ m.* | 3 |
| 6. | d | | «when hydrogen in the core is used up» it expands to become a red giant ✓<br>it ejects its outer layers / forms a planetary nebula AND the core remains as a white dwarf ✓ | *Do not accept supernova, neutron star or black hole.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `p = 0.125 arcsec`, `b = 9.5e-10 W/m^2`, `T = 6200 K`, sabitler `pc_ly = 3.26`, `ly_m = 9.46e15`, `sigma = 5.67e-8` | |
| `d_pc` | `1/p` | 8.00 pc |
| `d` | `d_pc*pc_ly*ly_m` | 2.467 × 10¹⁷ m |
| `L` | `4*pi*d**2*b` | 7.27 × 10²⁶ W (1.9 L☉) |
| `R` | `sqrt(L/(4*pi*sigma*T**4))` | 8.31 × 10⁸ m |
| Kontrol | `d = 2.5e17` ile | L = 7.46 × 10²⁶ W, R = 8.42 × 10⁸ m |
| Kontrol | (b)'nin yuvarlanmış değerleri `L = 7.3e26` ve `L = 7.5e26` ile | R = 8.33 × 10⁸ m ve 8.44 × 10⁸ m (ikisi de kabul aralığında) |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?" / "Which …?" / "Why …?") + alt alta A–D | Soru 1–5 uygun; Soru 4 "Why …?" kökü kullanır (profilde gözlenen iki kalıbın dışında, uzman teyidi gerekir) |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–2 uygun (artan); Soru 3 tek sözcüklü sınıf adları; Soru 4–5 cümle biçiminde seçenek; Soru 5'te dört seçenek de "sonuç, because gerekçe" yapısında |
| 1A: doğru cevap konumu dengeli | D, C, A, B, A |
| 1A: şekil olmadan çözülebilirlik | Soru 3'te HR diyagramı tarif edildi; soru yalnızca metindeki değerlerle çözülür |
| Kapsam sınırı: Sefe değişenleri yok | Hiçbir soruda geçmez; uzaklık yalnızca ıraklıkla |
| Kapsam sınırı: HR diyagramında düşey eksen ışınım gücü, yatay eksen sıcaklık | Soru 3 kökünde ve şekil tarifinde bu eksenler kullanıldı |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 6 uygun (2, 2, 3, 2; toplam 9). **Çekince:** 9 puan SL kısa sorusu için uzundur (SL örnek kâğıdında 4–6 puan gözlendi); SL için bölünmesi gerekebilir |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | (a) Show that, (c) Determine |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, kabul aralığı | Soru 6 uygun |
| Tablo başlığı "büyüklük / birim" | Soru 6 veri tablosu uygun: her sütun "büyüklük / birim" başlıklı, hücrelerde yalnızca sayı |
| Değer–birim yazımı, 2 anlamlı basamak | Uygun |
| Düzey etiketi | Tüm sorular SL |

## Bağımsız kontrol

Tarih: 2026-10-11. Yazardan farklı bir kör çözücü soruları cevapları görmeden çözdü; tüm cevap anahtarlarını bağımsız olarak yeniden
üretti, çekirdek denklemlerini (nükleon sayısı ve yük korunumu) ve Paper 1B eğimlerini yeniden hesapladı (bu dosyada çekirdek denklemi
ve 1B sorusu yok; kontrol, sayısal cevaplar ve çeldiricilerle sınırlıdır). Bulgular: [review/e5-review.md](review/e5-review.md).
KRİTİK bulgu yok. Bu kontrol uzman incelemesinin yerine geçmez. Aşağıdaki değişikliklerden sonra Soru 5 ve Soru 6 ikinci bir kör çözücüden geçti; cevaplar uyuştu
([review/recheck-2026-10-11.md](review/recheck-2026-10-11.md)).

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 5 (ORTA):** soru yeniden yazıldı. Sıcaklık seçeneklerden çıkarıldı; kökteki "immediately afterwards" kaldırıldı ve füzyon hızı
  azalınca dışa doğru basınç kuvvetinin azaldığı kökte verildi. Seçenekler artık yalnızca büzülme / genleşme / değişmeme ekseninde ve
  dördü de "sonuç, because gerekçe" yapısında. Cevap A (büzülür) değişmedi; eski C seçeneği ("büzülür ve soğur") kaldırıldı.
- **Soru 6 (d) (ORTA):** yıldız kütlesi 1.5 M☉ → 1.2 M☉ (1.4 M☉ değerinin altında; sınırı yanlışlıkla yıldızın toplam kütlesine uygulayan
  öğrenci de beyaz cüceye varır). Yıldızın ana kolda gerçekçi kalması için veriler birlikte değiştirildi: görünür parlaklık
  2.0 × 10⁻⁹ → 9.5 × 10⁻¹⁰ W m⁻², sıcaklık 6900 → 6200 K. Buna bağlı sonuçlar: L 1.5 × 10²⁷ → 7.3 × 10²⁶ W (2.5 × 10¹⁷ m ile
  1.6 × 10²⁷ → 7.5 × 10²⁶ W), R 9.7 × 10⁸ → 8.3 × 10⁸ m. (a) parçası değişmedi.
- **Soru 6 (c) (ORTA):** kabul aralığı, (b)'nin markscheme'deki yuvarlanmış değerlerini (7.3 ve 7.5 × 10²⁶ W → 8.33 ve 8.44 × 10⁸ m)
  kapsayacak biçimde 8.2–8.5 × 10⁸ m olarak belirlendi. Önerilen 9.6–10.0 × 10⁸ m aralığı eski veriye aitti; aynı ölçüt yeni veriye
  uygulandı.
- **Soru 6 sabitler (DÜŞÜK):** σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴ soruya eklendi.
- **Soru 6 veri tablosu (DÜŞÜK):** "Quantity / Value" → her sütunu "büyüklük / birim" başlıklı tek satırlı tablo.
- **Soru 6 (b) (DÜŞÜK):** kapsam tablosunda B.1 ikincil düğüm olarak yazıldı.
- **Soru 6 uzunluğu (DÜŞÜK):** "9 puan SL kısa sorusu için uzun" çekincesi "Biçim uyumu" tablosunda vurgulandı; soru bölünmedi.

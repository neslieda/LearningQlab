# Pilot soru seti: B.1 Isıl enerji aktarımı

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü B.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı; PDF açılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile ayrı bir hesapla
> yeniden üretildi ve dosyadaki değerlerle eşleşti. Kullanılan değerler: suyun özgül ısı kapasitesi 4200 J kg⁻¹ K⁻¹, alüminyum
> 900 J kg⁻¹ K⁻¹, suyun buharlaşma özgül gizli ısısı 2.26 × 10⁶ J kg⁻¹, buzun ısıl iletkenliği 2.2 W m⁻¹ K⁻¹. Hepsi soruda verilir;
> veri kitapçığı değerleri uzmanca teyit edilmeli.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; nitel markscheme maddeleri (Soru 5c) kodla denetlenemez;
> malzeme değerleri genel bilgiden alındı, bir kaynaktan teyit edilmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle
> bakılmadı; veri kitapçığındaki simge ve formül yazımıyla (ör. iletim denklemi) uyum kontrol edilmedi.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (B.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Q = mcΔT ile ısıl denge (iki cisim) | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | İletimle enerji aktarım hızı (nicel) | AO2 | — | 1 | Kolay |
| 3 | Paper 1A | SL | Wien yasası ile Stefan-Boltzmann yasasının birleştirilmesi; ışınım gücü | AO3 | — | 1 | Orta–zor |
| 4 | Paper 1A | SL | Hâl değişimi; Q = mcΔT ile Q = mL'nin sabit güçte birleştirilmesi | AO3 | — | 1 | Orta |
| 5 | Paper 2 | SL | Q = mcΔT, Q = mL; hâl değişiminde molekül modeli ve iç enerji; çevreye enerji kaybı | AO2–AO3 | Show that, Calculate, Explain, Determine | 8 | Orta |

Bu set B.1'in tamamını kapsamaz. Eksik kalanlar: yoğunluk; Kelvin–Celsius dönüşümü (ayrı bir soru olarak); sıcaklık ile ortalama
kinetik enerji ilişkisi (Ē = 3⁄2 kT); konveksiyonun nitel anlatımı; görünür parlaklık (b = L / 4πd²); Wien yasasıyla doğrudan
sıcaklık hesabı; ısıtma eğrisi grafiğinin yorumu.

Kapsam sınırı kontrolü: konveksiyon hiçbir soruda hesaplanmıyor (yalnızca nitel sınırı). Türev ya da integral yok.

---

## Soru 1 — Paper 1A

An aluminium block of mass 0.20 kg at a temperature of 90 °C is placed in 0.30 kg of water at 20 °C. The water is in an insulated
container of negligible heat capacity. No water evaporates.

Specific heat capacity of aluminium = 900 J kg⁻¹ K⁻¹
Specific heat capacity of water = 4200 J kg⁻¹ K⁻¹

What is the final temperature of the water?

A. 29 °C
B. 48 °C
C. 55 °C
D. 73 °C

**Cevap: A**

**Çözüm.** Bloğun verdiği enerji suyun aldığına eşittir: 0.20 × 900 × (90 − *T*) = 0.30 × 4200 × (*T* − 20).
180 (90 − *T*) = 1260 (*T* − 20) → *T* = (16 200 + 25 200) / 1440 = 28.75 °C ≈ 29 °C.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Özgül ısı kapasiteleri yok sayılır, yalnızca kütleyle ağırlıklı ortalama alınır: (0.20 × 90 + 0.30 × 20) / 0.50 = 48 °C |
| C | İki sıcaklığın aritmetik ortalaması alınır: (90 + 20) / 2 = 55 °C |
| D | Özgül ısı kapasiteleri yer değiştirilir: (0.20 × 4200 × 90 + 0.30 × 900 × 20) / (840 + 270) = 73.0 °C |

---

## Soru 2 — Paper 1A

A layer of ice of thickness 5.0 cm covers a pond. The upper surface of the ice is at −8.0 °C and the lower surface is at 0 °C.
The thermal conductivity of ice is 2.2 W m⁻¹ K⁻¹.

What is the rate of thermal energy transfer by conduction through each square metre of the ice?

A. 0.88 W
B. 3.5 W
C. 350 W
D. 1.2 × 10⁴ W

**Cevap: C**

**Çözüm.** Δ*Q*/Δ*t* = *kA*Δ*T*/Δ*x* = 2.2 × 1.0 × 8.0 / 0.050 = 352 W ≈ 350 W.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Kalınlığa bölmek yerine kalınlıkla çarpılır: 2.2 × 8.0 × 0.050 = 0.88 W |
| B | Kalınlık metreye çevrilmez: 2.2 × 8.0 / 5.0 = 3.52 W |
| D | Sıcaklık farkı yerine kelvine çevrilmiş tek bir sıcaklık kullanılır: 2.2 × 265 / 0.050 = 1.17 × 10⁴ W |

---

## Soru 3 — Paper 1A

Stars X and Y can be treated as black bodies. The radius of X is three times the radius of Y. The wavelength at which the emitted
intensity is a maximum for X is **half** the corresponding wavelength for Y.

What is the ratio (luminosity of X) / (luminosity of Y)?

A. 9⁄16
B. 36
C. 48
D. 144

**Cevap: D**

**Çözüm.** Wien yasası: λ<sub>max</sub>*T* = sabit, bu yüzden *T*<sub>X</sub> = 2*T*<sub>Y</sub>. Stefan-Boltzmann: *L* = σ*AT*⁴ ve *A* ∝ *r*².
Oran = 3² × 2⁴ = 9 × 16 = 144.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Wien yasası ters uygulanır (kısa dalga boyu daha soğuk sayılır): 9 × (1⁄2)⁴ = 9⁄16 |
| B | Işınım gücü *T*⁴ yerine *T*² ile orantılı alınır: 9 × 2² = 36 |
| C | Yüzey alanı *r*² yerine *r* ile orantılı alınır: 3 × 2⁴ = 48 |

---

## Soru 4 — Paper 1A

A solid sample is heated at a constant rate in an insulated container. While the sample is solid, its temperature rises at
0.50 K s⁻¹. After the sample reaches its melting point, it takes 300 s to melt completely. The specific heat capacity of the
solid is 800 J kg⁻¹ K⁻¹.

What is the specific latent heat of fusion of the sample?

A. 4.0 × 10² J kg⁻¹
B. 1.2 × 10⁵ J kg⁻¹
C. 2.4 × 10⁵ J kg⁻¹
D. 4.8 × 10⁵ J kg⁻¹

**Cevap: B**

**Çözüm.** Güç sabittir: *P* = *mc* (Δ*T*/Δ*t*) = *m* × 800 × 0.50 = 400*m*. Erime: *mL* = *P* × 300 → *L* = 400 × 300 =
1.2 × 10⁵ J kg⁻¹. Kütle sadeleşir; verilmemesi eksik değildir.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Yalnızca kütle başına güç hesaplanır, süreyle çarpılmaz: 800 × 0.50 = 400 |
| C | Isınma hızı kullanılmaz: 800 × 300 = 2.4 × 10⁵ |
| D | Isınma hızıyla çarpmak yerine bölünür: 800 × 300 / 0.50 = 4.8 × 10⁵ |

---

## Soru 5 — Paper 2 (8 puan)

An electric immersion heater of power 1.4 kW is placed in 0.80 kg of water in an insulated vessel. The initial temperature of the
water is 25 °C. The heat capacity of the vessel and of the heater is negligible.

Specific heat capacity of water = 4200 J kg⁻¹ K⁻¹
Specific latent heat of vaporization of water = 2.26 × 10⁶ J kg⁻¹

**(a)** Show that the time taken for the water to reach 100 °C is about 180 s. [2]

The heater stays switched on for a further 120 s after the water has reached 100 °C.

**(b)** Calculate the mass of water that vaporizes during this time. [2]

**(c)** Explain, with reference to the energy of the molecules, why the temperature of the water stays constant while it boils
even though energy is being supplied. [2]

The experiment is repeated with the same initial conditions, but the insulation is removed from the vessel. The time measured for
the water to reach 100 °C is now 200 s.

**(d)** Determine the average rate at which thermal energy is transferred from the water to the surroundings during this second experiment. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *Q* = 0.80 × 4200 × 75 «= 2.52 × 10⁵ J» ✓<br>*t* = 2.52 × 10⁵ / 1400 «= 180 s» ✓ | *Answer 180 s is given; award the second mark only if the complete substitution is seen.* | 2 |
| 5. | b | | energy supplied = 1400 × 120 «= 1.68 × 10⁵ J» ✓<br>*m* = 1.68 × 10⁵ / 2.26 × 10⁶ = 0.074 «kg» ✓ | *The vessel is insulated in (b): all the energy supplied vaporizes water.* | 2 |
| 5. | c | | the energy supplied increases the «intermolecular» potential energy of the molecules **OR** is used to separate the molecules / break intermolecular bonds ✓<br>the average «random» kinetic energy of the molecules does not change **AND** temperature is a measure of this average kinetic energy ✓ | *OWTTE* | 2 |
| 5. | d | | useful power = 2.52 × 10⁵ / 200 «= 1260 W» ✓<br>rate of loss = 1400 − 1260 = 140 «W» ✓ | *Allow ECF from (a).*<br>**ALTERNATIVE:** energy lost = 1400 × (200 − 180) «= 2.8 × 10⁴ J» ✓ rate = 2.8 × 10⁴ / 200 = 140 «W» ✓<br>*Both routes give 140 W; no accept range is needed.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `P = 1400 W`, `m = 0.80 kg`, `T1 = 25 °C`, `T2 = 100 °C`, `t_boil = 120 s`, `t_meas = 200 s`; sabit `c = 4200 J/(kg K)`, `L = 2.26e6 J/kg` | |
| `Q` | `m*c*(T2 - T1)` | 2.52 × 10⁵ J |
| `t` | `Q/P` | 180 s (tam) |
| `m_vap` | `P*t_boil/L` | 0.0743 kg |
| `P_useful` | `Q/t_meas` | 1260 W |
| `P_loss` | `P - P_useful` | 140 W (`P*(t_meas - t)/t_meas` yolu da 140 W) |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–4 uygun (artan) |
| 1A: olumsuzluk / kritik sözcük koyu | Soru 3 ("half") uygun; olumsuz kök yok |
| 1A: doğru cevap konumu dengeli | A, C, D, B |
| 1A: şekil olmadan çözülebilir | Soru 1–4 şekil gerektirmiyor |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 2, 2; toplam 8) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | Soru 5 uygun: (a) Show that, (c) Explain, (d) Determine |
| Markscheme: dört sütunlu tablo, ✓, « », OR, AND, ECF, OWTTE | Soru 5 uygun |
| Değer–birim yazımı (J kg⁻¹ K⁻¹), 2 anlamlı basamak | Uygun; Soru 2'de 1.2 × 10⁴ çeldiricisi bilimsel gösterimde |
| 1A: yuvarlak, temiz sayılar | Soru 3–4 temiz; Soru 1 (28.75 → 29) ve Soru 2 (352 → 350) yuvarlama gerektiriyor |
| Paper 2: cevap kutusu, noktalı satırlar | Bu taslakta yok; yayın şablonunda eklenecek |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, yazarından bağımsız bir kör çözücü tarafından cevaplar görülmeden çözüldü; tüm cevap anahtarları ve
markscheme sonuçları bağımsız olarak yeniden üretildi (KRİTİK bulgu yok). Ayrıntı: [review/b1-review.md](review/b1-review.md).
Bu kontrol uzman incelemesinin yerine geçmez.

İnceleme sonucu yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 5, ORTA-1:** "insulated vessel" ile çevreye enerji kaybı arasındaki çelişki giderildi; (d) artık yalıtımın çıkarıldığı
  ikinci bir deneyi anlatıyor. (a)–(c) yalıtımlı durumda kaldı; (b)'nin notuna bu yazıldı.
- **Soru 5, ORTA-2:** veri yeniden tasarlandı: ısıtıcı gücü 1.5 kW → 1.4 kW, test süresi 190 s → 200 s. Sonuçlar: (a) 168 s
  ("about 170 s") → 180 s (tam); (b) 0.080 kg → 0.074 kg; (d) 174 W / 158 W (yola bağlı) → her iki yoldan 140 W. 160–180 W kabul
  aralığı kaldırıldı.
- **DÜŞÜK-1 (SL kısa soruda 8 puan) ve DÜŞÜK-3 (Soru 1–2'de yuvarlama):** değişiklik yapılmadı; yazım standardı 4–9 puana izin
  veriyor, yuvarlama tek doğru cevabı etkilemiyor. Uzman teyidi için kayıt olarak kalıyor.

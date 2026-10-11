# Pilot soru seti: C.5 Doppler etkisi

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneği](a1-kinematics-pilot-questions.md) ile aynı yapıda yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü C.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgündür.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile yeniden hesaplandı.
> Sabitler: c = 3.00 × 10⁸ m s⁻¹; havada ses hızı 340 m s⁻¹ (kullanıldığı her soruda verildi). Veri kitapçığı değerleri uzmanca teyit
> edilmeli.
> **Doğrulanmayan:** (1) bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; (2) bilinen bir sınav sorusuna benzerlik açısından uzman
> gözüyle bakılmadı; (3) Soru 3 ve 4'te çeldiriciler doğru cevaba sayıca yakındır (680 / 671 Hz; 720 / 727 Hz) — bu bilinçli bir
> seçimdir (iki formülü ayırt etme) ama uzman bunu fazla ince bulabilir; (4) Soru 5'te 40.0 kHz'lik ultrason vericisi ve bir drone için
> 16 m s⁻¹ (yaklaşık 58 km h⁻¹) makul büyüklüklerdir ama bir kaynaktan teyit edilmedi; (5) Soru 5 (d)'de iki durumun farkı 0.1 kHz'dir
> ve 3 anlamlı basamakta görünür, ama dedektörün bu çözünürlükte ölçtüğü varsayılır;
> (6) nitel parçalar (Soru 2, Soru 5 a) kodla doğrulanamaz.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (C.5) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Işıkta Doppler: Δλ/λ ≈ v/c; tayf çizgisi kayması | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Ses için Doppler etkisinin nitel anlatımı (sabit hızla yaklaşan kaynak) | AO3 | — | 1 | Orta |
| 3 | Paper 1A | HL | Ses: hareketli kaynak formülü | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Ses: hareketli gözlemci formülü | AO2 | — | 1 | Orta |
| 5 | Paper 2 | HL | Dalga cepheleriyle açıklama; hareketli kaynak; hareketli gözlemci ile karşılaştırma | AO2–AO3 | Explain, Show that, Calculate, Discuss | 9 | Orta–zor |

Bu set C.5'in tamamını kapsamaz. Eksik kalanlar: dalga cephesi diyagramının çizimi; ışık için frekans kayması (Δf/f) ile hesap;
maviye kayma; tayf çizgisi kaymasından hız yönünün belirlenmesi; Doppler etkisinin uygulamaları (ör. dönen cisimlerde çizgi genişlemesi).

Sınır denetimi: hiçbir soruda kaynak ve gözlemci aynı anda hareket etmez. Soru 5 (d)'de iki ayrı durum karşılaştırılır (önce yalnızca
kaynak, sonra yalnızca gözlemci hareketli).

---

## Soru 1 — Paper 1A

A spectral line has a wavelength of 650 nm when measured in a laboratory on Earth. The same line is observed in the light from a
galaxy that is moving away from Earth at a speed of 6.0 × 10⁶ m s⁻¹.

What is the wavelength of the line observed in the light from the galaxy?

A. 637 nm
B. 650 nm
C. 663 nm
D. 676 nm

**Cevap: C**

**Çözüm.** Δλ / λ ≈ v / c = 6.0 × 10⁶ / 3.00 × 10⁸ = 0.020. Δλ = 0.020 × 650 = 13 nm. Kaynak uzaklaştığı için dalga boyu artar:
650 + 13 = 663 nm.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Kaymanın yönü ters alınır (yaklaşan kaynak gibi): 650 − 13 = 637 nm |
| B | Kaynağın hareketinin yalnızca frekansı değiştirdiği, dalga boyunun aynı kaldığı düşünülür |
| D | Kayma iki katı alınır (ışığın "gidiş–dönüş" yaptığı düşüncesi): 650 + 2 × 13 = 676 nm |

---

## Soru 2 — Paper 1A

A train moves at a constant speed directly towards a stationary observer. The train sounds a horn that emits sound of constant
frequency *f*. The air is still.

What describes the frequency of the sound heard by the observer while the train is approaching?

A. Higher than *f* and increasing
B. Higher than *f* and constant
C. Equal to *f*
D. Lower than *f* and constant

**Cevap: B**

**Çözüm.** Kaynak gözlemciye doğru hareket ederken ardışık dalga cepheleri öndeki bölgede birbirine yaklaşır; gözlemcideki dalga boyu
kısalır, ses hızı değişmez, frekans *f*'den büyük olur. Kayma kaynağın hızına bağlıdır, uzaklığına değil; hız sabit ve doğrudan
gözlemciye yönelik olduğundan duyulan frekans sabittir.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Frekansın uzaklık azaldıkça arttığı sanılır (artan şey ses şiddetidir; frekans ile şiddet karıştırılır) |
| C | Frekansın yalnızca kaynağa ait olduğu, hareketle değişmediği düşünülür |
| D | Kaymanın yönü ters alınır (uzaklaşan kaynak) |

---

## Soru 3 — Paper 1A

A siren on a vehicle emits sound of frequency 600 Hz. The vehicle moves at 40.0 m s⁻¹ directly towards a stationary observer. The
speed of sound in air is 340 m s⁻¹.

What is the frequency of the sound heard by the observer?

A. 529 Hz
B. 537 Hz
C. 671 Hz
D. 680 Hz

**Cevap: D**

**Çözüm.** Hareketli kaynak, yaklaşma: f′ = f v / (v − u<sub>s</sub>) = 600 × 340 / (340 − 40) = 680 Hz.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Hareketli gözlemci formülü ve ters yön (uzaklaşma): 600 × (340 − 40) / 340 = 529 Hz |
| B | Doğru formül, ters yön (uzaklaşan kaynak): 600 × 340 / (340 + 40) = 537 Hz |
| C | Hareketli gözlemci formülü kullanılır: 600 × (340 + 40) / 340 = 671 Hz. Işık için geçerli yaklaşık bağıntı (Δf/f ≈ v/c) sese uygulanırsa da aynı değer çıkar: 600 + 600 × 40 / 340 = 671 Hz |

---

## Soru 4 — Paper 1A

A stationary siren emits sound of frequency 800 Hz. A motorcyclist moves at 34.0 m s⁻¹ directly away from the siren. The speed of sound
in air is 340 m s⁻¹.

What is the frequency of the sound heard by the motorcyclist?

A. 720 Hz
B. 727 Hz
C. 880 Hz
D. 889 Hz

**Cevap: A**

**Çözüm.** Hareketli gözlemci, uzaklaşma: f′ = f (v − u<sub>o</sub>) / v = 800 × (340 − 34) / 340 = 720 Hz.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Hareketli kaynak formülü kullanılır (uzaklaşma): 800 × 340 / (340 + 34) = 727 Hz |
| C | Doğru formül, ters yön (yaklaşan gözlemci): 800 × (340 + 34) / 340 = 880 Hz |
| D | Hareketli kaynak formülü ve ters yön: 800 × 340 / (340 − 34) = 889 Hz |

Not: 34.0 m s⁻¹ yaklaşık 122 km h⁻¹'tir; bir motosikletli için gerçekçidir. Hız düşürülmedi, çünkü daha küçük hızlarda anahtar ile
hareketli kaynak çeldiricisi arasındaki fark %1'in altına iner.

---

## Soru 5 — Paper 2 (9 puan)

A technician tests a small drone that carries an ultrasound transmitter. The transmitter emits sound of frequency 40.0 kHz. The
drone flies horizontally at a constant speed directly towards a stationary detector. The detector records a frequency of 42.0 kHz.
The speed of sound in air is 340 m s⁻¹ and the air is still.

> **Şekil:** Solda drone (kaynak), sağda sabit dedektör; drone'dan dedektöre yönelen hız oku. Drone'un çevresinde, merkezleri sola
> doğru kaymış çemberler olarak dalga cepheleri: dedektör tarafında sık, arka tarafta seyrek. "diagram not to scale". Soru şekil olmadan
> çözülebilir.

**(a)** Explain, with reference to wavefronts, why the frequency recorded by the detector is higher than 40.0 kHz. [2]

**(b)** Show that the speed of the drone is about 16 m s⁻¹. [2]

The drone now flies directly away from the detector at the same speed. Use a speed of 16 m s⁻¹ for the drone.

**(c)** Calculate the frequency recorded by the detector. [2]

**(d)** A student suggests that the detector would also record 42.0 kHz if the drone were stationary and the detector moved towards
the drone at 16 m s⁻¹. Discuss this suggestion. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the drone / source moves towards the detector between emitting successive wavefronts, so the wavefronts are closer together / the wavelength «at the detector» is shorter ✓<br>the speed of sound «in air» is unchanged, so more wavefronts arrive per unit time / *f* = *v* / *λ* is greater ✓ | *OWTTE*<br>*Do not award the second mark if the speed of sound is said to increase.* | 2 |
| 5. | b | | 42.0 = 40.0 × 340 / (340 − *u*) ✓<br>*u* = 340 × (1 − 40.0 / 42.0) **OR** 16.2 «m s⁻¹» ✓ | *Use of the moving-observer equation gives 17.0 m s⁻¹, which does not match the target, and scores [0].*<br>*Answer must be seen to at least 3 s.f. or the rearrangement must be shown.* | 2 |
| 5. | c | | *f* = 40.0 × 340 / (340 + 16) ✓<br>= 38.2 «kHz» ✓ | *Accept u = 16.2 m s⁻¹, which also gives 38.2 kHz.* | 2 |
| 5. | d | | moving observer: *f* = 40.0 × (340 + 16) / 340 = 41.9 «kHz» ✓<br>this is less than 42.0 kHz / the two situations are described by different equations «because the motion is relative to the air» ✓<br>the suggestion is incorrect, although the difference is small «0.1 kHz» because the speed is much less than the speed of sound ✓ | *Third mark requires a conclusion supported by the values.*<br>*OWTTE* | 3 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `f = 40.0 kHz`, `f_obs = 42.0 kHz`, `v = 340 m/s`, `u_given = 16 m/s` | |
| `u` | `v*(1 - f/f_obs)` | 16.19 m s⁻¹ |
| `f_away` | `f*v/(v + u_given)` | 38.20 kHz (u = 16.19 ile 38.18 kHz) |
| `f_moving_observer` | `f*(v + u_given)/v` | 41.88 kHz |
| `f_moving_source` | `f*v/(v - u_given)` | 41.98 kHz |
| `diff` | `f_moving_source - f_moving_observer` | 0.09 kHz (3 anlamlı basamakta 42.0 − 41.9 = 0.1 kHz) |
| Denetim (yanlış formül) | `v*(f_obs/f - 1)` | 17.0 m s⁻¹ — "about 16" hedefini tutmaz; (b)'de puan almaz |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun (Soru 2: "What describes …?") |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1, 3, 4 uygun (artan); Soru 2 kısa sözel ifadeler, yüksekten düşüğe sıralı |
| 1A: doğru cevap harfleri dengeli | C, B, D, A |
| 1A: şekil olmadan çözülebilir | Soru 1–4 şekil gerektirmez |
| 1A: yuvarlak, temiz sayılar | Doğru cevaplar temiz (663 nm, 680 Hz, 720 Hz); çeldiriciler 3 anlamlı basamağa yuvarlandı |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 2, 3; toplam 9) |
| Paper 2: "Show that" kalıbı ve en az bir AO3 parçası | Soru 5 (a) Explain, (b) Show that, (d) Discuss; (c) ve (d) verilen 16 m s⁻¹ değerini kullanır (kökte "Use a speed of 16 m s⁻¹") |
| Markscheme: dört sütunlu tablo, ✓, « », OR, OWTTE | Soru 5 uygun |
| Paper 2: şekil | **Eksik:** dalga cephesi diyagramı yalnızca sözle tarif edildi |
| Müfredat sınırı: kaynak ve gözlemci birlikte hareket etmez | Uygun; yankı (hem kaynak hem gözlemci rolü) içeren bağlam bilerek kullanılmadı |
| Düzey etiketi | Soru 3, 4, 5 HL (ses için hareketli kaynak / gözlemci formülleri); Soru 1 ve 2 SL |
| Değer–birim yazımı, anlamlı basamak | Uygun; Soru 5'te frekanslar 3 anlamlı basamak (kayma küçük olduğu için gerekli) |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, cevapları görmeyen bağımsız bir kör çözücü tarafından çözüldü; çözücü tüm cevap
anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti (KRİTİK bulgu yok). Bulgular:
[review/c5-review.md](review/c5-review.md). Bu, uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile, dosyanın son metni üzerinden yeniden denetlendi):

- **Soru 5 (b) (ORTA):** kaydedilen frekans 41.2 kHz → 42.0 kHz; hedef "about 10 m s⁻¹" → "about 16 m s⁻¹". Doğru (hareketli kaynak) formül 16.19 m s⁻¹, yanlış (hareketli gözlemci) formül 17.0 m s⁻¹ verir; hedef artık iki yolu ayırır (eskiden 9.90 ve 10.2, ikisi de "about 10").
- **Soru 5 (c):** 38.9 kHz → 38.2 kHz; kökten önce "Use a speed of 16 m s⁻¹ for the drone" eklendi (DÜŞÜK bulgu 5: markscheme ile "same speed" ifadesi artık örtüşüyor).
- **Soru 5 (d) (ORTA):** karşılaştırma 41.18 / 41.21 kHz (3 anlamlı basamakta ikisi de 41.2) → 41.9 / 42.0 kHz; fark verilerin duyarlığında görünür. Markscheme sonucu "not exactly correct" → "incorrect, although the difference is small".
- **Soru 5 bağlamı:** kaynak yarasa → ultrason vericisi taşıyan küçük drone. 16 m s⁻¹ bir yarasa için tartışmalı, bir drone için makul (yaklaşık 58 km h⁻¹); fizik aynı. Köke "the air is still" eklendi.
- **Soru 4 (ORTA):** "cyclist" → "motorcyclist"; sayılar ve seçenekler aynı (720, 727, 880, 889 Hz).
- **Soru 3 ve 4 (DÜŞÜK):** hızlar 3 anlamlı basamakla yazıldı: 40 → 40.0 m s⁻¹, 34 → 34.0 m s⁻¹. Soru 3'ün C çeldiricisine ikinci yanılgı yolu (Δf/f ≈ v/c bağıntısının sese uygulanması) eklendi.
- **Uygulanmayan:** Soru 4'te gözlemci hızının 68 m s⁻¹ yapılması (inceleme "zorunlu değil" diyor; mevcut seçenekler 3 anlamlı basamakta ayrık) ve Soru 1'in D çeldiricisi ("şüphe"; sayı tutarlı).

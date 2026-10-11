# Pilot soru seti: A.5 Galileo ve özel görelilik

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set, [yazım standardına](AUTHORING_STANDARD.md) göre ve [A.1 örneğinin](a1-kinematics-pilot-questions.md) yapısıyla elle yazıldı.
> A.5 yalnızca HL düğümüdür; tüm sorular HL etiketlidir ve SL havuzuna girmez.
>
> **Kaynak:** yalnızca müfredat düğümü A.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav sorusu, ders kitabı sorusu ya da internet kaynağı girdi olarak kullanılmadı.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi
> (c = 3.00 × 10⁸ m s⁻¹; veri kitapçığı değeri uzmanca teyit edilmeli). Soru 5'te iki olay arasındaki uzay-zaman aralığının iki
> çerçevede eşit çıktığı ayrıca denetlendi.
> **Doğrulanmayan:** bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; bilinen bir sınav sorusuna benzerlik açısından uzman gözüyle
> bakılmadı; rehberin uzay-zaman aralığı için kullandığı işaret kuralı ((*c*Δ*t*)² − Δ*x*²) ve Lorentz dönüşümlerinin veri
> kitapçığındaki yazımı kontrol edilmedi; Soru 4'te açının *ct* ekseninden ölçülmesi müfredat analizindeki "tan *θ* = *v*/*c*"
> ifadesine dayanır.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.5) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Öz zaman ve zaman genişlemesi; hangi çerçevenin öz zamanı ölçtüğü | AO2 | — | 1 | Orta |
| 2 | Paper 1A | HL | Göreli hız toplama (Galileo toplamasıyla karşılaştırma) | AO2 | — | 1 | Orta |
| 3 | Paper 1A | HL | Uzay-zaman aralığının değişmezliği | AO3 | — | 1 | Orta–zor |
| 4 | Paper 1A | HL | Uzay-zaman diyagramında dünya çizgisinin açısı (tan *θ* = *v*/*c*) | AO2 | — | 1 | Kolay |
| 5 | Paper 2 | HL | Öz uzunluk; *γ*; öz zaman; Lorentz dönüşümü ve eşzamanlılığın göreliliği | AO1–AO3 | State, Show that, Calculate, Determine | 9 | Orta–zor |

Bu set A.5'in tamamını kapsamaz. Eksik kalanlar: Galileo dönüşümü ve referans çerçevesi kavramı, görelilik postülalarının ifadesi,
boy kısalmasının doğrudan hesabı, müon bozunması kanıtı, uzay-zaman diyagramının çizimi ve diyagram üzerinde eşzamanlılık,
konum için Lorentz dönüşümü (*x*′ = *γ*(*x* − *vt*)).

---

## Soru 1 — Paper 1A

Two space buoys X and Y are at rest relative to each other. In the reference frame of the buoys the distance between X and Y is
9.0 × 10⁸ m. A probe travels in a straight line from X to Y at a constant speed of 0.60*c* relative to the buoys.

What is the time taken for the probe to travel from X to Y as measured by a clock on the probe?

A. 3.0 s
B. 4.0 s
C. 5.0 s
D. 6.3 s

**Cevap: B**

**Çözüm.** Şamandıra çerçevesinde süre = 9.0 × 10⁸ / (0.60 × 3.00 × 10⁸) = 5.0 s. İki olay (X'ten geçiş, Y'den geçiş) sondanın
bulunduğu yerde gerçekleşir; sondanın saati öz zamanı ölçer. *γ* = 1/√(1 − 0.60²) = 1.25. Öz zaman = 5.0 / 1.25 = 4.0 s.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Sondanın sürati yerine ışık sürati kullanılır: 9.0 × 10⁸ / 3.00 × 10⁸ = 3.0 s |
| C | Göreli etki uygulanmaz; şamandıra çerçevesindeki süre verilir: 5.0 s |
| D | Öz zamanın hangi çerçevede ölçüldüğü karıştırılır; *γ* ile bölmek yerine çarpılır: 5.0 × 1.25 = 6.25 s ≈ 6.3 s |

---

## Soru 2 — Paper 1A

A spacecraft moves directly away from the Earth at a speed of 0.60*c* relative to the Earth. The spacecraft launches a probe in its
direction of motion. The speed of the probe relative to the spacecraft is 0.70*c*.

What is the speed of the probe relative to the Earth?

A. 1.3*c*
B. *c*
C. 0.92*c*
D. 0.17*c*

**Cevap: C**

**Çözüm.** Göreli hız toplama: *u* = (0.60*c* + 0.70*c*) / (1 + 0.60 × 0.70) = 1.30*c* / 1.42 = 0.92*c*.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Galileo hız toplaması kullanılır: 0.60*c* + 0.70*c* = 1.3*c* |
| B | "Toplam *c*'yi aşıyor, o hâlde sürat *c* olur" düşüncesi; kütleli bir cisim *c* süratine ulaşamaz |
| D | Formül ters işaretle uygulanır (sonda geriye fırlatılmış gibi): (0.70*c* − 0.60*c*) / (1 − 0.42) = 0.17*c* |

---

## Soru 3 — Paper 1A

In an inertial reference frame S, two events are separated by a distance Δ*x* = 3.0 m and by a time interval Δ*t* such that
*c*Δ*t* = 5.0 m. In another inertial reference frame S′ the two events occur at the same position.

What is *c*Δ*t*′, where Δ*t*′ is the time interval between the events in S′?

A. 8.0 m
B. 5.8 m
C. 5.0 m
D. 4.0 m

**Cevap: D**

**Çözüm.** Uzay-zaman aralığı değişmezdir: (*c*Δ*t*′)² − (Δ*x*′)² = (*c*Δ*t*)² − (Δ*x*)². Δ*x*′ = 0 olduğundan
(*c*Δ*t*′)² = 5.0² − 3.0² = 16 m²; *c*Δ*t*′ = 4.0 m. (S′, S'ye göre 0.60*c* ile hareket eder; Δ*t*′ öz zamandır.)

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Aralık karesiz ve toplanarak hesaplanır: 5.0 + 3.0 = 8.0 m |
| B | Aralık Öklid uzaklığı gibi artı işaretiyle hesaplanır: √(5.0² + 3.0²) = 5.8 m |
| C | Zaman aralığının bütün çerçevelerde aynı olduğu varsayılır (Galileo görüşü): 5.0 m |

---

## Soru 4 — Paper 1A

A spacetime diagram is drawn for an inertial reference frame S, with the *x* axis horizontal and the *ct* axis vertical. Both axes
have the same scale. A particle moves along the *x* direction at a constant speed of 0.50*c* relative to S.

What is the angle between the worldline of the particle and the *ct* axis?

A. 27°
B. 30°
C. 45°
D. 63°

**Cevap: A**

**Çözüm.** Dünya çizgisinin *ct* ekseniyle yaptığı açı için tan *θ* = *v*/*c* = 0.50; *θ* = 27°.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | tan yerine sin kullanılır: sin⁻¹(0.50) = 30° |
| C | Her dünya çizgisinin ışığınki gibi 45° olduğu sanılır (ışık çizgisiyle karıştırma) |
| D | Açı *ct* ekseni yerine *x* ekseninden ölçülür: tan⁻¹(1 / 0.50) = 63° |

---

## Soru 5 — Paper 2 (9 puan)

A long space platform has two ends, P and Q. The proper length PQ of the platform is 480 m. A shuttle moves at a constant velocity of
0.80*c* relative to the platform, parallel to PQ, in the direction from P to Q. The shuttle passes end P (event 1) and later passes
end Q (event 2).

> **Şekil:** Yatay, uzun bir platform; sol ucu P, sağ ucu Q olarak etiketli; iki uç arasında "480 m" ölçü oku. Platformun hemen
> üstünde, P'nin yakınında, sağa (P'den Q'ya) doğru "0.80*c*" etiketli hız okuyla çizilmiş mekik. *Diagram not to scale.*

**(a)** State what is meant by proper length. [1]

**(b)** Show that the Lorentz factor *γ* for the shuttle relative to the platform is about 1.7. [1]

**(c)** Calculate the time between event 1 and event 2 in the reference frame of the platform. [2]

**(d)** Determine the time between event 1 and event 2 as measured by a clock on the shuttle. [2]

A lamp at P and a lamp at Q each emit one flash of light. In the reference frame of the platform the two flashes are emitted at the
same time.

**(e)** Determine, for the reference frame of the shuttle, which lamp (at P or at Q) flashes first and the time interval between
the two flashes. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the length of an object measured in the reference frame in which the object is at rest ✓ | *OWTTE* | 1 |
| 5. | b | | *γ* = 1 / √(1 − 0.80²) = 1.67 ✓ | *Substitution or an answer to at least 3 s.f. must be seen.* | 1 |
| 5. | c | | Δ*t* = 480 / (0.80 × 3.00 × 10⁸) ✓<br>= 2.0 × 10⁻⁶ «s» ✓ | | 2 |
| 5. | d | | **ALTERNATIVE 1**<br>shuttle clock measures the proper time «both events occur at the shuttle» so Δ*t*′ = Δ*t* / *γ* ✓<br>Δ*t*′ = 2.0 × 10⁻⁶ / 1.67 = 1.2 × 10⁻⁶ «s» ✓<br>**ALTERNATIVE 2**<br>length of platform in shuttle frame = 480 / 1.67 «= 288 m» ✓<br>Δ*t*′ = 288 / (0.80 × 3.00 × 10⁸) = 1.2 × 10⁻⁶ «s» ✓ | *Allow ECF from (c).*<br>*Award [1] max for 3.3 × 10⁻⁶ «s» (multiplying by γ).* | 2 |
| 5. | e | | use of Δ*t*′ = *γ*(Δ*t* − *v*Δ*x*/*c*²) with Δ*t* = 0 **AND** Δ*x* = 480 «m» ✓<br>«magnitude of» Δ*t*′ = 1.67 × 0.80 × 480 / (3.00 × 10⁸) = 2.1 × 10⁻⁶ «s» ✓<br>the lamp at Q flashes first ✓ | *Accept answers in the range 2.1 × 10⁻⁶ to 2.2 × 10⁻⁶ «s» (use of γ = 1.7 gives 2.18 × 10⁻⁶).*<br>*Award the third mark only if it is supported by the sign of Δt′ or by a simultaneity argument; do not award it for a bare statement.*<br>*Accept "the lamp the shuttle is moving towards" for "the lamp at Q".* | 3 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `beta = 0.80`, `L0 = 480 m`, sabit `c = 3.00e8 m/s` | |
| `gamma` | `1/sqrt(1 - beta**2)` | 1.667 |
| `dt` | `L0/(beta*c)` | 2.00 × 10⁻⁶ s |
| `dt_proper` | `dt/gamma` | 1.20 × 10⁻⁶ s |
| `L` (denetim) | `L0/gamma` | 288 m; `L/(beta*c)` = 1.20 × 10⁻⁶ s |
| `dt_flash` | `gamma*(0 - beta*L0/c)` | −2.13 × 10⁻⁶ s (Q lambası − P lambası; eksi işaret: Q lambası önce) |

Denetim (öğrenciden istenmez): olay 1 ve 2 arasındaki aralık platform çerçevesinde (*c*Δ*t*)² − Δ*x*² = 600² − 480² = 1.296 × 10⁵ m²;
mekik çerçevesinde (*c*Δ*t*′)² = 360² = 1.296 × 10⁵ m². İki değer eşittir.

(e) için yön gerekçesi: P ucu *x* = 0, Q ucu *x* = +480 m alınır; mekik +*x* yönünde (P'den Q'ya) hareket eder.
*t*′ = *γ*(*t* − *vx*/*c*²) dönüşümünde platform çerçevesinde eşzamanlı (*t* = 0) iki olaydan *x* değeri büyük olan (Q lambası) daha
küçük *t*′ alır; yani mekiğin yaklaştığı lamba (Q) önce yanar.

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1 ve 4 artan (s, derece); Soru 2 ve 3 azalan (*c*'nin katı, m) |
| 1A: doğru cevap konumu dengeli | B, C, D, A |
| 1A: olumsuz kök | Kullanılmadı |
| Şekil | Soru 4 uzay-zaman diyagramını sözle tanımlar; şekil olmadan çözülür. Soru 5 metinle tarif edildi (P ve Q uçları, mekiğin yönü); soru şekil olmadan da çözülür, öğrenci sürümü için şekil üretilmeli |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (1, 1, 2, 2, 3; toplam 9) |
| Paper 2: "Show that" kalıbı; sonraki parça verilen değeri kullanabilir | Soru 5 (b) → (d), (e) uygun; (e) için kabul aralığı verildi |
| Markscheme: dört sütunlu tablo, ✓, « », AND, ECF, OWTTE, ALTERNATIVE 1 / 2 | Soru 5 uygun |
| Değer–birim yazımı, 2 anlamlı basamak; süratler *c* cinsinden | Uygun |
| Kapsam sınırları (A.5) | Türetim istenmedi; zaman ekseni *ct*; dünya çizgisi sabit hızlı; yalnızca eylemsiz çerçeveler |
| Terminoloji | "proper time", "proper length", "worldline", "reference frame" rehber terimleri olarak kullanıldı; "Lorentz factor" teriminin rehberdeki karşılığı teyit edilmedi |

## Bağımsız kontrol

Tarih: 2026-10-11. Kör çözücü, cevapları görmeden soruları çözdü ve tüm cevap anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti; KRİTİK ya da ORTA bulgu yok.
Ayrıntı: [review/a5-review.md](review/a5-review.md). Bu kontrol uzman incelemesinin yerine geçmez.

Bulgular üzerine yapılan değişiklikler:

- Soru 5: platformun uçları "rear/front" yerine P ve Q olarak adlandırıldı; kökte mekiğin P'den Q'ya gittiği açıkça yazıldı ve şekil tarifi eklendi. (e) "which lamp (at P or at Q)" oldu; markscheme, formül zinciri ve yön gerekçesi buna göre güncellendi (doğru cevap: Q lambası). Sayılar değişmedi; `python3` ile yeniden hesaplandı (2.13 × 10⁻⁶ s; *γ* = 1.7 ile 2.18 × 10⁻⁶ s).
- Soru 5 (e) markscheme notu: "third mark is independent" kaldırıldı; üçüncü puan artık yalnızca Δ*t*′ işareti ya da eşzamanlılık gerekçesiyle verilir, gerekçesiz yön tahmini puan almaz.
- "Biçim uyumu" tablosundaki şekil satırı Soru 5'i kapsayacak biçimde güncellendi.
- **Uygulanmayan:** Soru 2'de B seçeneğinin (*c*) *c*'nin altında bir değerle değiştirilmesi önerisi (inceleme "şart değil" diyor). Gerekçe: "toplam *c*'yi aşarsa sürat *c* olur" gerçek ve yaygın bir yanılgı; önerilen alternatif (toplamın *γ*'ya bölünmesi) hangi çerçevenin *γ*'sı olduğu belirsiz, tanımlı bir öğrenci hatasına dayanmıyor ve standart her çeldiricinin belirli bir yanılgıya dayanmasını istiyor. Sorunun ayırt ediciliğinin düşük olabileceği uzman incelemesine bırakıldı.

# Pilot soru seti: C.4 Duran dalgalar ve rezonans

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Bu set [yazım standardına](AUTHORING_STANDARD.md) göre, [A.1 örneği](a1-kinematics-pilot-questions.md) ile aynı yapıda yazıldı.
>
> **Kaynak:** yalnızca müfredat düğümü C.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve
> genel fizik. Hiçbir sınav kâğıdı, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgündür.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` (yalnızca standart kütüphane) ile yeniden hesaplandı.
> Sabitler: havada ses hızı 340 m s⁻¹ (soruda verildi). Tel üzerindeki dalga hızları (120 ve 260 m s⁻¹) soruda verilir.
> **Doğrulanmayan:** (1) bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi; (2) bilinen bir sınav sorusuna benzerlik açısından uzman
> gözüyle bakılmadı; (3) bir ucu kapalı boruda harmoniklerin adlandırılması (yalnızca tek sayılı harmonikler: birinci, üçüncü, beşinci)
> rehberden teyit edilmedi; bu yüzden Soru 2 harmonik numarası kullanmadan soruldu; (4) Soru 4'teki "sönüm artınca en büyük genliğin
> görüldüğü frekans biraz düşer" ifadesi genlik rezonansı için doğrudur; rehberin bu ayrıntıyı ne ölçüde beklediği teyit edilmedi;
> (5) nitel sorular (Soru 3, 4 ve Soru 5 a, d, e) kodla doğrulanamaz.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (C.4) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | İki ucu sabit telde n. harmoniğin dalga boyu ve frekansı | AO2 | — | 1 | Kolay |
| 2 | Paper 1A | SL | Bir ucu kapalı boruda izinli duran dalga desenleri | AO3 | — | 1 | Orta |
| 3 | Paper 1A | SL | Duran dalgada faz: düğümün iki yanındaki noktalar | AO2 | — | 1 | Orta |
| 4 | Paper 1A | SL | Sönümün en büyük genliğe ve rezonans frekansına nitel etkisi | AO2 | — | 1 | Orta |
| 5 | Paper 2 | SL | Duran dalganın oluşumu; birinci harmonik; düğüm–karın deseni; rezonans; sönüm | AO1–AO3 | Outline, Show that, State, Calculate, Explain | 9 | Orta |

Bu set C.4'ün tamamını kapsamaz. Eksik kalanlar: iki ucu açık boruda desenler; duran dalgada genliğin konuma göre değişimi; duran dalga
ile ilerleyen dalganın karşılaştırılması; doğal frekans ile zorlayıcı frekans ilişkisinin grafikle yorumu; hafif, kritik ve ağır sönümün
yer değiştirme–zaman davranışı; rezonansın yararlı ve zararlı örnekleri.

Terminoloji denetimi: sette yalnızca "first harmonic", "third harmonic" kullanıldı; rehberin kaçınılmasını istediği "temel ton / üst ton" karşılıkları hiçbir soru metninde ve markscheme'de yer almaz. Uç düzeltmesi,
basınç düğümü ve ikiden fazla dalganın üst üste binmesi yoktur.

---

## Soru 1 — Paper 1A

A string of length 0.75 m is fixed at both ends. The speed of waves on the string is 120 m s⁻¹.

What is the frequency of the third harmonic of the string?

A. 80 Hz
B. 160 Hz
C. 240 Hz
D. 480 Hz

**Cevap: C**

**Çözüm.** Üçüncü harmonikte tel üzerinde üç yarım dalga boyu vardır: λ = 2L / 3 = 0.50 m. f = v / λ = 120 / 0.50 = 240 Hz.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Birinci harmoniğin frekansı verilir: λ = 2L = 1.5 m → 120 / 1.5 = 80 Hz |
| B | Dalga boyu telin uzunluğuna eşit alınır (ikinci harmonik): 120 / 0.75 = 160 Hz |
| D | Üçüncü harmonikte λ = L / 3 alınır (yarım dalga boyu ile tam dalga boyu karıştırılır): 120 / 0.25 = 480 Hz |

---

## Soru 2 — Paper 1A

A tube of length 0.17 m is closed at one end and open at the other end. The air in the tube vibrates in its first harmonic at a
frequency of 500 Hz. The speed of sound in air is 340 m s⁻¹.

What is the next higher frequency at which a standing wave can be formed in the tube?

A. 1000 Hz
B. 1500 Hz
C. 2500 Hz
D. 3000 Hz

**Cevap: B**

**Çözüm.** Kapalı uçta yer değiştirme düğümü, açık uçta karın vardır. Birinci harmonik: L = λ/4 → f₁ = 340 / (4 × 0.17) = 500 Hz. Bir
sonraki izinli desen: L = 3λ/4 → λ = 0.227 m → f = 3 × 500 = 1500 Hz.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Bir ucu kapalı boruda da birinci harmoniğin tüm tam katlarının oluştuğu sanılır: 2 × 500 = 1000 Hz (bu desen kapalı uçta düğüm koşulunu sağlamaz) |
| C | Bir izinli desen atlanır (L = 5λ/4): 5 × 500 = 2500 Hz; bu frekansta duran dalga oluşur ama "bir sonraki" değildir |
| D | İki ucu açık boru bağıntısı üçüncü harmonik için kullanılır: 3 × 340 / (2 × 0.17) = 3000 Hz |

---

## Soru 3 — Paper 1A

A standing wave of wavelength 0.80 m is formed on a string. Point X on the string is 0.10 m to the left of a node. Point Y on the
string is 0.10 m to the right of the same node.

What is the phase difference between the oscillations of X and Y?

A. 0
B. π/4 rad
C. π/2 rad
D. π rad

**Cevap: D**

**Çözüm.** Komşu düğümler arası λ/2 = 0.40 m'dir; X ve Y aynı düğümün iki yanındaki komşu ilmeklerdedir. Duran dalgada bir ilmek içindeki
tüm noktalar eş fazlıdır; komşu ilmekteki noktalar zıt fazlıdır. Faz farkı π rad.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Duran dalgadaki tüm noktaların eş fazlı olduğu düşünülür (yalnızca aynı ilmek için doğru) |
| B | İlerleyen dalga bağıntısı bir noktanın düğüme uzaklığıyla kullanılır: 2π × 0.10 / 0.80 = π/4 |
| C | İlerleyen dalga bağıntısı X–Y uzaklığıyla kullanılır: 2π × 0.20 / 0.80 = π/2 |

---

## Soru 4 — Paper 1A

A lightly damped system is driven by a periodic force. The frequency of the driving force is varied and the amplitude of the
system is measured. The damping of the system is then increased, but the damping remains light.

What is the effect of the increased damping on the maximum amplitude and on the frequency at which the maximum amplitude occurs?

A. The maximum amplitude decreases and it occurs at a slightly lower frequency.
B. The maximum amplitude decreases and it occurs at a slightly higher frequency.
C. The maximum amplitude increases and it occurs at a slightly lower frequency.
D. The maximum amplitude increases and it occurs at a slightly higher frequency.

**Cevap: A**

**Çözüm.** Sönüm arttıkça sistem her salınımda daha çok enerji kaybeder; rezonanstaki en büyük genlik küçülür ve rezonans eğrisi
genişler. En büyük genliğin görüldüğü frekans doğal frekansın biraz altına kayar.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Genlik etkisi doğru, frekans kayması ters yönde düşünülür ("sönüm sistemi sertleştirir") |
| C | Frekans etkisi doğru; sönümün rezonans tepesini "keskinleştirip yükselttiği" sanılır |
| D | Her iki etki de ters düşünülür |

Not: seçenekler cümle biçimindedir; biçim profiline göre bu tür azınlıktadır ama kullanılır. İki büyüklük birlikte sorulduğu için tablo
biçimli seçenek yerine cümle tercih edildi (tablo biçimi doğrulanamadı).

---

## Soru 5 — Paper 2 (9 puan)

A steel wire is stretched between two fixed supports that are 0.65 m apart. A vibrator attached to the wire close to one support
is connected to a signal generator. The speed of waves on the wire is 260 m s⁻¹.

> **Şekil:** Bir tezgâh üzerinde iki sabit destek arasına gerilmiş yatay tel; destekler arası 0.65 m olarak işaretli; sol desteğin
> hemen yanında tele bağlı titreştirici ve ona bağlı sinyal üreteci. "diagram not to scale". Soru şekil olmadan çözülebilir.

**(a)** Outline how a standing wave is formed on the wire. [2]

**(b)** Show that the frequency of the first harmonic of the wire is 200 Hz. [2]

The frequency of the signal generator is set to 600 Hz and a standing wave is observed on the wire.

**(c)** (i) State the number of antinodes on the wire. [1]

 (ii) Calculate the distance between adjacent nodes. [1]

The frequency of the signal generator is now increased slowly from 150 Hz to 250 Hz.

**(d)** Explain why the amplitude of vibration at the centre of the wire becomes very large at one frequency in this range. [2]

**(e)** The damping of the wire is increased. State the effect of this on the maximum amplitude observed in (d). [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | waves «from the vibrator» travel along the wire and are reflected at the fixed end(s) ✓<br>the incident and reflected waves / waves travelling in opposite directions superpose ✓ | *OWTTE*<br>*Accept "interfere" for "superpose".* | 2 |
| 5. | b | | *λ* = 2 × 0.65 = 1.3 «m» ✓<br>*f* = 260 / 1.3 «= 200 Hz» ✓ | *Both the wavelength and the substitution must be shown; the answer alone scores [0] because it is given.* | 2 |
| 5. | c | i | 3 ✓ | | 1 |
| 5. | c | ii | 0.65 / 3 = 0.22 «m» ✓ | *Allow ECF from (c)(i).*<br>*Accept* λ/2 = 260 / (2 × 600) = 0.22 «m». | 1 |
| 5. | d | | the driving frequency equals the natural frequency / first harmonic frequency of the wire «about 200 Hz» ✓<br>resonance occurs **OR** energy is transferred to the wire at the maximum rate, «so the amplitude is a maximum» ✓ | *OWTTE*<br>*Accept "the centre of the wire is an antinode of the first harmonic" as supporting detail, not as a marking point.* | 2 |
| 5. | e | | the maximum amplitude decreases ✓ | | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `L = 0.65 m`, `v = 260 m/s`, `f_gen = 600 Hz` | |
| `lam_1` | `2*L` | 1.30 m |
| `f_1` | `v/lam_1` | 200 Hz |
| `n` | `f_gen/f_1` | 3 → 3 karın, 4 düğüm (uçlar dahil) |
| `node_sep` | `L/n` | 0.217 m |
| Denetim | `v/f_gen/2` | 0.217 m |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1–3 uygun (artan); Soru 4 cümle biçiminde, dört seçenek aynı kalıpta |
| 1A: doğru cevap harfleri dengeli | C, B, D, A |
| 1A: şekil olmadan çözülebilir | Soru 1–4 şekil gerektirmez |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (2, 2, 1, 1, 2, 1; toplam 9). SL kâğıdında kısa soru 4–6 puan gözlendi; SL kâğıdı için (c) ya da (e) çıkarılabilir |
| Paper 2: "Show that" kalıbı ve en az bir AO3 parçası | Soru 5 (b) Show that (sonuç tam 200 Hz olduğu için "about" kullanılmadı), (d) Explain |
| Markscheme: dört sütunlu tablo, ✓, « », OR, ECF, OWTTE | Soru 5 uygun |
| Paper 2: çizim parçası (Draw / Sketch) | **Eksik:** duran dalga deseni çizdiren parça yazılmadı; şekil şablonu gerektirir |
| Müfredat sınırı: "first harmonic"; uç düzeltmesi yok; yalnızca yer değiştirme düğümleri; sönüm nitel | Uygun; sönüm etkisi Soru 4 ve 5(e)'de yalnızca nitel |
| Değer–birim yazımı (m s⁻¹), 2 anlamlı basamak | Uygun; frekans seçenekleri tam sayı Hz |

## Bağımsız kontrol

Tarih: 2026-10-11. Bu dosya, cevapları görmeyen bağımsız bir kör çözücü tarafından çözüldü; çözücü tüm cevap
anahtarlarını ve markscheme sonuçlarını bağımsız olarak yeniden üretti (KRİTİK bulgu yok). Bulgular:
[review/c4-review.md](review/c4-review.md). Bu, uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile, dosyanın son metni üzerinden yeniden denetlendi):

- **Soru 5 (b) (DÜŞÜK):** hesap tam 200 Hz verdiği için kökten "about" çıkarıldı ("… is about 200 Hz" → "… is 200 Hz"); markscheme'de ikinci madde yerine koymayı zorunlu kılacak biçimde yazıldı. Veri değiştirilmedi, çünkü hız değişirse 600 Hz üçüncü harmoniğe tam denk gelmez ve (c) bozulur.
- **Soru 5 (DÜŞÜK):** SL için 9 puanın uzun olduğu notu "Biçim uyumu" tablosunda zaten vardı; soru bölünmedi. Bölme kararı sınav kâğıdı derlenirken verilmeli.
- **Uygulanmayan:** Soru 3'te faz farkının radyan yerine derece ya da sözel biçimde yazılması. İnceleme "uzman teyit edene kadar değişiklik gerekmez" diyor; müfredat analizinde C.4 satırı "faz"ı SL kazanımı olarak veriyor ve çeldiriciler (π/4, π/2) hesaplanabilir yanılgılara dayanıyor. Uzman teyidine bırakıldı.

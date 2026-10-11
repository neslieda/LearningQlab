# Pilot soru seti: E.4 Fisyon

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Yazım ölçütleri: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Yapı örneği: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Kaynak:** yalnızca müfredat düğümü E.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve genel
> fizik. Hiçbir sınav kâğıdı, markscheme, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgün kurgudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi. Kullanılan
> sabitler: 1 u = 1.661 × 10⁻²⁷ kg = 931.5 MeV c⁻², e = 1.60 × 10⁻¹⁹ C (veri kitapçığı değerleri uzmanca teyit edilmeli). Soru 5'teki
> tepkimede nükleon sayısı (1 + 235 = 140 + 94 + 2) ve yük (92 = 54 + 38) korunumu elle kontrol edildi.
> **Doğrulanmayan:**
> - Bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. sondaki "Bağımsız kontrol"). Bilinen bir sınav sorusuna benzerlik
>   açısından uzman gözüyle bakılmadı.
> - **Bellekten yazılan çekirdek verileri (kaynaktan teyit edilmeli):** atom kütleleri uranyum-235 235.04393 u, ksenon-140 139.92165 u,
>   stronsiyum-94 93.91536 u, nötron 1.008665 u; Z değerleri (U 92, Xe 54, Sr 38) (Soru 5). Bu kütlelerle bulunan 185 MeV, fisyon başına
>   tipik değerle (yaklaşık 200 MeV, ürünlerin sonraki bozunmaları dahil) uyumludur; ancak tek tek kütleler teyit edilmedi.
>   U-235 + n → Xe-140 + Sr-94 + 2n gerçek bir fisyon kanalıdır ve ders kitaplarında sık geçen bir örnektir; soru metni ve bağlam özgündür.
> - Soru 1'deki nükleon başına bağlanma enerjileri (7.6 ve 8.5 MeV) bağlanma enerjisi eğrisinden bellekle alınmış yuvarlak, gerçekçi
>   değerlerdir; belirli bir çekirdeğe atfedilmedi.
> - Soru 3'teki "fisyon başına ortalama 2.5 nötron" değeri U-235 için bellekten gelen yaklaşık değerdir.
> - Soru 5 (c): tepkime başına 185 MeV yalnızca tek bir fisyon kanalına aittir; gerçek reaktörde ortalama farklıdır. Soru bunu
>   "assume" ile varsayım olarak verir.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (E.4) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Fisyonda açığa çıkan enerjinin nükleon başına bağlanma enerjisinden hesabı | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | Yavaşlatıcının işlevi; kontrol çubuğu, ısı değiştirici ve zırhlamadan ayrımı | AO2 | — | 1 | Kolay |
| 3 | Paper 1A | SL | Zincirleme tepkime; sabit güçte çalışma koşulu | AO3 | — | 1 | Orta |
| 4 | Paper 1A | SL | Fisyon ürünlerinin yönetimi | AO2 | — | 1 | Kolay |
| 5 | Paper 2 | SL | Nötronla uyarılmış fisyon; kütle farkından enerji; güç–yakıt tüketimi; yavaşlatmanın gerekçesi | AO1–AO3 | State, Show, Determine, Explain | 9 | Orta–zor |

Bu set E.4'ün tamamını kapsamaz. Eksik kalanlar: kendiliğinden fisyon, kontrol çubuklarının güç ayarındaki rolünün ayrıntısı, ısı
değiştiricinin işlevi, zırhlamanın gerekçesi, fisyon ürünlerinin uzun süreli depolanması ve yarı ömürle ilişkisi, kritik kütle kavramı
(müfredat analizinde açıkça geçmediği için bilerek dışarıda bırakıldı).

---

## Soru 1 — Paper 1A

A nucleus of nucleon number 240 has a binding energy per nucleon of 7.6 MeV. It undergoes fission into two nuclei, each of nucleon
number 120 and binding energy per nucleon 8.5 MeV. No neutrons are released.

What is the energy released in this fission?

A. 2040 MeV
B. 216 MeV
C. 108 MeV
D. 0.90 MeV

**Cevap: B**

**Çözüm.** Ürünlerin toplam bağlanma enerjisi = 2 × 120 × 8.5 = 2040 MeV. Başlangıç çekirdeğinin = 240 × 7.6 = 1824 MeV.
Açığa çıkan enerji = 2040 − 1824 = 216 MeV (= 240 × 0.90).

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Ürünlerin toplam bağlanma enerjisi, açığa çıkan enerji sanılır: 240 × 8.5 = 2040 MeV |
| C | Yalnızca bir ürün çekirdek hesaba katılır: 120 × 0.90 = 108 MeV |
| D | Nükleon başına fark verilir; nükleon sayısıyla çarpılmaz: 8.5 − 7.6 = 0.90 MeV |

---

## Soru 2 — Paper 1A

An engineer is choosing a material for the moderator of a thermal fission reactor.

Which property is the most important for this material?

A. Its nuclei absorb neutrons readily.
B. It has a high thermal conductivity so that energy is transferred quickly to the coolant.
C. It has a high density so that gamma radiation is absorbed.
D. Its nuclei have a small mass and slow neutrons down without absorbing them.

**Cevap: D**

**Çözüm.** Yavaşlatıcının işi, fisyondan çıkan hızlı nötronları çarpışmalarla yavaşlatmaktır. Çarpışma başına enerji aktarımı,
hedef çekirdeğin kütlesi nötronunkine yakın olduğunda en büyüktür; nötronların soğurulmaması da gerekir.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Yavaşlatıcı ile kontrol çubuğu karıştırılır; nötron soğurmak kontrol çubuğunun işidir |
| B | Yavaşlatıcı ile ısı değiştirici / soğutucu karıştırılır |
| C | Yavaşlatıcı ile zırhlama karıştırılır |

---

## Soru 3 — Paper 1A

In a fission reactor, each fission of a uranium-235 nucleus releases 2.5 neutrons on average. The reactor operates at a constant
power output.

What is the average number of neutrons from each fission that go on to cause a further fission?

A. 2.5
B. 1.5
C. 1
D. 0

**Cevap: C**

**Çözüm.** Güç sabitse saniyedeki fisyon sayısı sabittir; bunun için her fisyon ortalama tam bir yeni fisyona yol açmalıdır. Kalan
ortalama 1.5 nötron kontrol çubuklarında ve başka çekirdeklerde soğurulur ya da reaktörden kaçar.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Çıkan nötronların hepsinin yeni fisyon başlattığı düşünülür; bu durumda tepkime hızı üstel artar |
| B | Soğurulan ya da kaçan nötron sayısı (2.5 − 1) sorulanla karıştırılır |
| D | "Sabit güç" ifadesi zincirleme tepkimenin durduğu biçiminde yorumlanır |

---

## Soru 4 — Paper 1A

Fuel rods removed from a fission reactor are stored under several metres of water for a number of years.

What are the purposes of the water?

A. To remove the thermal energy released by the decay of fission products and to absorb radiation
B. To slow down neutrons and to keep the chain reaction going in the rods
C. To absorb neutrons and to make the fission products stable
D. To dissolve the fission products and to dilute them

**Cevap: A**

**Çözüm.** Kullanılmış yakıttaki fisyon ürünleri radyoaktiftir; bozunmaları hem ısı üretir hem de iyonlaştırıcı ışınım yayar. Su,
ısıyı uzaklaştırır ve ışınımı soğurarak zırh görevi yapar.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Havuzdaki su reaktördeki yavaşlatıcıyla karıştırılır; depolamada amaç tepkimeyi sürdürmek değildir |
| C | Radyoaktif bozunmanın dış etkiyle (nötron soğurarak) durdurulabileceği düşünülür |
| D | Katı yakıt çubukları içindeki ürünlerin suda çözülerek uzaklaştırıldığı düşünülür |

---

## Soru 5 — Paper 2 (9 puan)

One possible fission reaction in a nuclear reactor is

¹₀n + ²³⁵₉₂U → ¹⁴⁰₅₄Xe + ⁹⁴₃₈Sr + 2 ¹₀n

The following data are available. The masses given for uranium, xenon and strontium are atomic masses.

| Particle | Mass / u |
|---|---|
| uranium-235 | 235.04393 |
| xenon-140 | 139.92165 |
| strontium-94 | 93.91536 |
| neutron | 1.008665 |

1 u is equivalent to 931.5 MeV.

**(a)** State what is meant by neutron-induced fission. [1]

**(b)** Show that the energy released in this reaction is about 185 MeV. [3]

The reactor produces thermal power of 2.4 GW. Assume that each fission releases 185 MeV and that the mass of a uranium-235 atom is
235 u, where 1 u = 1.661 × 10⁻²⁷ kg.

**(c)** Determine the mass of uranium-235 that undergoes fission in the reactor in one day. [3]

**(d)** The neutrons released in the reaction have high kinetic energies. Explain why these neutrons must be slowed down for the
chain reaction to be sustained. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | a «heavy» nucleus absorbs a neutron and splits into two «smaller» nuclei «and neutrons» ✓ | *Both the absorption of a neutron and the splitting are required.* | 1 |
| 5. | b | | mass difference = 235.04393 + 1.008665 − 139.92165 − 93.91536 − 2 × 1.008665 ✓<br>= 0.19826 «u» ✓<br>energy = 0.19826 × 931.5 = 184.7 «MeV» ✓ | *Allow MP1 for a correct mass difference using one net neutron.*<br>*Answer must be given to at least 3 s.f. for MP3.* | 3 |
| 5. | c | | energy per fission = 185 × 10⁶ × 1.60 × 10⁻¹⁹ «= 2.96 × 10⁻¹¹ J» ✓<br>fissions per day = 2.4 × 10⁹ × 86 400 / 2.96 × 10⁻¹¹ «= 7.0 × 10²⁴» ✓<br>mass = 7.0 × 10²⁴ × 235 × 1.661 × 10⁻²⁷ = 2.7 «kg» ✓ | *Allow ECF from (b) if a value other than 185 MeV is used.* | 3 |
| 5. | d | | the probability of a neutron causing fission of uranium-235 is much greater for slow / thermal neutrons ✓<br>«without slowing» too few neutrons cause further fissions / fewer than one neutron per fission causes another fission «so the reaction dies away» ✓ | *OWTTE*<br>*Accept "fast neutrons are more likely to escape or be absorbed without causing fission" for MP2.* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `m_U = 235.04393`, `m_Xe = 139.92165`, `m_Sr = 93.91536`, `m_n = 1.008665` (u); `P = 2.4e9 W`; `E_f = 185 MeV`; sabitler `u_MeV = 931.5`, `e = 1.60e-19`, `u_kg = 1.661e-27` | |
| `dm` | `m_U + m_n - m_Xe - m_Sr - 2*m_n` | 0.198255 u |
| `E` | `dm*u_MeV` | 184.7 MeV |
| `E_J` | `E_f*1e6*e` | 2.96 × 10⁻¹¹ J |
| `rate` | `P/E_J` | 8.11 × 10¹⁹ s⁻¹ |
| `n_day` | `rate*86400` | 7.01 × 10²⁴ |
| `mass` | `n_day*235*u_kg` | 2.73 kg |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?" / "Which …?") + alt alta A–D | Soru 1–4 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1 ve 3 uygun (azalan); Soru 2 ve 4 cümle biçiminde seçenek (profilde azınlık biçim); Soru 4'te dört seçenek de iki ögeli ("To … and to …") |
| 1A: doğru cevap konumu dengeli | B, D, C, A |
| Kapsam: E.4 için açık sınır yok | Sorular "ölçülen çekirdek" maddeleriyle sınırlı tutuldu; kritik kütle ve zenginleştirme sorulmadı |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 5 uygun (1, 3, 3, 2; toplam 9). **Çekince:** 9 puan SL kısa sorusu için uzundur (SL örnek kâğıdında 4–6 puan gözlendi). SL havuzu için (a)+(b) [4] ve (c)+(d) [5] olarak ikiye bölme seçeneği uzman kararına bırakıldı |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | (b) Show that, (c) Determine, (d) Explain; (c) verilen yaklaşık değeri kullanır |
| Markscheme: dört sütunlu tablo, ✓, « », ECF, OWTTE | Soru 5 uygun |
| Tablo başlığı "büyüklük / birim" | Soru 5 kütle tablosu uygun ("Mass / u"); kütlelerin atom kütlesi olduğu tablonun üstünde yazılı |
| Değer–birim yazımı, 2 anlamlı basamak | Uygun; kütleler kütle farkı için gereken basamak sayısıyla verildi |
| Düzey etiketi | Tüm sorular SL |

## Bağımsız kontrol

Tarih: 2026-10-11. Yazardan farklı bir kör çözücü soruları cevapları görmeden çözdü; tüm cevap anahtarlarını bağımsız olarak yeniden
üretti, çekirdek denklemlerini (nükleon sayısı ve yük korunumu) ve Paper 1B eğimlerini yeniden hesapladı. Bulgular:
[review/e4-review.md](review/e4-review.md). KRİTİK bulgu yok. Bu kontrol uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 5 veri tablosu (DÜŞÜK):** tablonun üstüne "The masses given for uranium, xenon and strontium are atomic masses." eklendi. Başlık "Mass / u" olarak kaldı, çünkü tabloda nötron da var. Sayılar değişmedi (Δm = 0.198255 u, 184.7 MeV, 2.73 kg yeniden hesaplandı).
- **Soru 5 uzunluğu (DÜŞÜK):** "Biçim uyumu" tablosundaki not güçlendirildi: 9 puan SL kısa sorusu için uzun; (a)+(b) [4] ve (c)+(d) [5] bölme seçeneği yazıldı. Soru bölünmedi; uzman kararı bekliyor.
- **Soru 4 (DÜŞÜK):** B, C ve D seçenekleri A gibi iki ögeli biçime getirildi ("so that" → "and to"); yapı farkı artık doğru cevabı ele vermiyor. Cevap A ve çeldirici yanılgıları değişmedi.

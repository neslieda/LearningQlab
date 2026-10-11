# Pilot soru seti: E.3 Radyoaktif bozunma

> **Durum: İNCELENMEMİŞ TASLAK.** Tarih: 2026-10-11. Fizik uzmanı onayı olmadan öğrenciye gösterilmez (CLAUDE.md kural 13).
> Yazım ölçütleri: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Yapı örneği: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Kaynak:** yalnızca müfredat düğümü E.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), biçim profili ve genel
> fizik. Hiçbir sınav kâğıdı, markscheme, ders kitabı ya da internet sorusu girdi olarak kullanılmadı; senaryolar özgün kurgudur.
> **Sayısal doğrulama:** tüm sayısal cevaplar ve tüm sayısal çeldiriciler `python3` ile ayrı bir hesapla yeniden üretildi. Kullanılan
> sabit: 1 u = 931.5 MeV c⁻² (veri kitapçığı değeri uzmanca teyit edilmeli). Bozunma denklemlerinde nükleon sayısı ve yük korunumu
> elle kontrol edildi (Soru 2: 22 = 22, 11 = 10 + 1; Soru 6: 131 = 131, 53 = 54 − 1).
> **Doğrulanmayan:**
> - Bağımsız kör çözücüden geçti; uzman incelemesinden geçmedi (bkz. sondaki "Bağımsız kontrol"). Bilinen bir sınav sorusuna benzerlik
>   açısından uzman gözüyle bakılmadı.
> - **Bellekten yazılan çekirdek verileri (kaynaktan teyit edilmeli):** lityum-7 çekirdek kütlesi 7.01436 u (atom kütlesi 7.01600 u'dan
>   üç elektron kütlesi çıkarılarak), proton 1.00728 u, nötron 1.00866 u (Soru 3); sodyum-22'nin β⁺ ile neon-22'ye bozunduğu ve Z
>   değerleri (Na 11, Ne 10, Mg 12) (Soru 2); iyot-131'in yarı ömrü 8.0 gün, β⁻ ile ksenon-131'e bozunduğu, Z değerleri (I 53, Xe 54)
>   (Soru 6). Soru 3'ün sonucu (5.6 MeV) lityum-7 için bilinen nükleon başına bağlanma enerjisiyle uyumludur, ancak bu da bellekten.
> - Soru 1 ve Soru 4'teki kaynaklar adsızdır; yarı ömürler kurgusaldır.
> - Soru 6'da iyot-131 bozunmasına eşlik eden gama yayımı sorulmaz; (d) parçası, ürün çekirdeğin belirli bir enerji düzeyine giden
>   bozunmalarla sınırlanarak yazıldı.

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (E.3) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Sayım hızı, arka plan ışınımı, yarı ömür (tam sayı yarı ömür) | AO2 | — | 1 | Orta |
| 2 | Paper 1A | SL | β⁺ bozunma denklemi; nötrino | AO2 | — | 1 | Kolay |
| 3 | Paper 1A | SL | Kütle açığı; bağlanma enerjisi; nükleon başına bağlanma enerjisi | AO2 | — | 1 | Orta |
| 4 | Paper 1A | HL | Bozunma sabiti; T½ = ln 2/λ; A = λN | AO2 | — | 1 | Orta |
| 5 | Paper 1A | HL | Kesikli çekirdek enerji düzeylerinin kanıtı | AO2 | — | 1 | Kolay |
| 6 | Paper 2 | HL | λ ve A = λN; N = N₀e^(−λt) ile keyfi zaman aralığı; sürekli β tayfı | AO2–AO3 | Show, Calculate, Determine, Explain | 9 | Orta–zor |

Bu set E.3'ün tamamını kapsamaz. Eksik kalanlar: izotop kavramı, nükleon başına bağlanma enerjisi eğrisinin yorumu, güçlü çekirdek
kuvvetinin özellikleri, bozunmanın rastgele ve kendiliğinden doğası, α ve γ denklemleri, giricilik ve iyonlaştırma karşılaştırması,
E = mc² ile bozunma enerjisi hesabı, nötron/proton oranı ve kararlılık (HL). SL düzeyinde yapılandırılmış (Paper 2) soru bu sette yok.

---

## Soru 1 — Paper 1A

A detector is placed at a fixed distance from a radioactive source and records a count rate of 180 min⁻¹. When the source is
removed, the detector records a background count rate of 20 min⁻¹. The half-life of the source is 3.0 hours.

What count rate does the detector record, with the source in place, 6.0 hours later?

A. 20 min⁻¹
B. 40 min⁻¹
C. 45 min⁻¹
D. 60 min⁻¹

**Cevap: D**

**Çözüm.** Kaynağa ait sayım hızı = 180 − 20 = 160 min⁻¹. 6.0 saat = 2 yarı ömür → 160 / 4 = 40 min⁻¹. Dedektör arka planla birlikte
40 + 20 = 60 min⁻¹ kaydeder.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Bozunma doğrusal sanılır: iki yarı ömürde kaynağın tümüyle tükendiği, yalnızca arka planın kaldığı düşünülür |
| B | Arka plan çıkarılır ama sonuca geri eklenmez: 160 / 4 = 40 |
| C | Arka plan hiç hesaba katılmaz: 180 / 4 = 45 |

---

## Soru 2 — Paper 1A

A nucleus of sodium-22 (²²₁₁Na) decays by β⁺ (positron) emission. The symbols for neon and magnesium are Ne and Mg.

Which are the other two products of this decay?

A. ²²₁₂Mg and an antineutrino
B. ²²₁₂Mg and a neutrino
C. ²²₁₀Ne and a neutrino
D. ²²₁₀Ne and an antineutrino

**Cevap: C**

**Çözüm.** β⁺ bozunmasında bir proton nötrona dönüşür: proton sayısı 1 azalır (11 → 10), nükleon sayısı değişmez (22). Pozitronla
birlikte bir nötrino yayılır: ²²₁₁Na → ²²₁₀Ne + e⁺ + ν.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | β⁻ bozunmasının ürünleri yazılır (Z artar, antinötrino) |
| B | Yük korunumu yanlış uygulanır: pozitron yayımında Z'nin arttığı düşünülür |
| D | Çekirdek doğru, ancak eşlik eden parçacık β⁻ bozunmasındaki gibi antinötrino alınır |

---

## Soru 3 — Paper 1A

The mass of a lithium-7 nucleus (⁷₃Li) is 7.01436 u. The mass of a proton is 1.00728 u and the mass of a neutron is 1.00866 u.
1 u is equivalent to 931.5 MeV.

What is the binding energy per nucleon of lithium-7?

A. 5.6 MeV
B. 9.8 MeV
C. 13 MeV
D. 39 MeV

**Cevap: A**

**Çözüm.** Kütle açığı = 3 × 1.00728 + 4 × 1.00866 − 7.01436 = 0.04212 u. Bağlanma enerjisi = 0.04212 × 931.5 = 39.2 MeV.
Nükleon başına = 39.2 / 7 = 5.6 MeV.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Nükleon sayısı yerine nötron sayısına bölünür: 39.2 / 4 = 9.8 MeV |
| C | Nükleon sayısı yerine proton sayısına bölünür: 39.2 / 3 = 13.1 MeV |
| D | Toplam bağlanma enerjisi verilir; nükleon sayısına bölünmez: 39.2 MeV |

---

## Soru 4 — Paper 1A

A freshly prepared sample contains 4.0 × 10¹² nuclei of a radioactive nuclide. The half-life of the nuclide is 20 minutes.

What is the initial activity of the sample?

A. 1.7 × 10⁹ Bq
B. 2.3 × 10⁹ Bq
C. 3.3 × 10⁹ Bq
D. 1.4 × 10¹¹ Bq

**Cevap: B**

**Çözüm.** T½ = 20 × 60 = 1200 s. λ = ln 2 / T½ = 5.78 × 10⁻⁴ s⁻¹. A = λN = 5.78 × 10⁻⁴ × 4.0 × 10¹² = 2.3 × 10⁹ Bq.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Bir yarı ömürdeki ortalama aktiflik alınır: (N/2) / T½ = 2.0 × 10¹² / 1200 = 1.7 × 10⁹ |
| C | ln 2 çarpanı unutulur (λ = 1/T½): 4.0 × 10¹² / 1200 = 3.3 × 10⁹ |
| D | Yarı ömür saniyeye çevrilmez: (ln 2 / 20) × 4.0 × 10¹² = 1.4 × 10¹¹ (dakika başına bozunma, Bq değil) |

---

## Soru 5 — Paper 1A

Several observations are made about the decay of a particular radioactive nuclide.

Which observation provides evidence that nuclei have discrete energy levels?

A. The beta particles emitted have a continuous range of energies.
B. The activity of a sample decreases exponentially with time.
C. The gamma photons emitted have only certain specific energies.
D. The moment at which an individual nucleus decays cannot be predicted.

**Cevap: C**

**Çözüm.** Gama fotonu, çekirdeğin iki enerji düzeyi arasındaki geçişte yayılır; fotonların yalnızca belirli enerjilere sahip olması
düzeylerin kesikli olduğunu gösterir (atom tayflarındaki çizgilere benzer biçimde).

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Sürekli β tayfı düzey kanıtı sanılır; bu gözlem enerjinin üçüncü bir parçacıkla (nötrino) paylaşıldığını gösterir |
| B | Üstel azalma düzeylerle ilişkilendirilir; bu, bozunma olasılığının sabit olmasının sonucudur |
| D | Rastgelelik ile kuantumlanma karıştırılır; öngörülemezlik enerji düzeyleri hakkında bilgi vermez |

---

## Soru 6 — Paper 2 (9 puan)

A hospital stores a sealed sample of iodine-131. Iodine-131 decays by beta-minus emission to xenon-131:

¹³¹₅₃I → ¹³¹₅₄Xe + e⁻ + ν̄

The half-life of iodine-131 is 8.0 days. When the sample is delivered, the activity of the iodine-131 is 3.2 × 10⁵ Bq.

**(a)** Show that the decay constant of iodine-131 is about 1.0 × 10⁻⁶ s⁻¹. [2]

**(b)** Calculate the number of iodine-131 nuclei in the sample when it is delivered. [2]

The sample may be treated as ordinary waste when its activity has fallen to 5.0 × 10⁴ Bq.

**(c)** Determine, in days, the time after delivery at which the sample may be treated as ordinary waste. [3]

**(d)** For decays to a given energy level of the xenon-131 nucleus, the energy released is the same, but the beta particles are
emitted with a continuous range of kinetic energies. Explain this observation. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *T*½ = 8.0 × 24 × 3600 «= 6.91 × 10⁵ s» ✓<br>*λ* = ln 2 / 6.91 × 10⁵ = 1.00 × 10⁻⁶ «s⁻¹» ✓ | *Answer must be given to at least 3 s.f. (1.00 × 10⁻⁶) from a visible substitution for MP2.* | 2 |
| 6. | b | | *N* = *A* / *λ* **OR** 3.2 × 10⁵ / 1.0 × 10⁻⁶ ✓<br>*N* = 3.2 × 10¹¹ ✓ | | 2 |
| 6. | c | | 5.0 × 10⁴ = 3.2 × 10⁵ e^(−*λt*) **OR** number of half-lives = ln 6.4 / ln 2 «= 2.68» ✓<br>*t* = ln 6.4 / 1.0 × 10⁻⁶ «= 1.86 × 10⁶ s» ✓<br>*t* = 21 «days» ✓ | *Accept answers in the range 21–22 days.*<br>*Award [1 max] for "between 2 and 3 half-lives / between 16 and 24 days" with no further working.* | 3 |
| 6. | d | | an antineutrino is also emitted «in each decay» ✓<br>the energy released is shared between the beta particle and the antineutrino «and the recoiling nucleus» in varying proportions ✓ | *OWTTE*<br>*Accept "neutrino" for "antineutrino".* | 2 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `T_days = 8.0`, `A0 = 3.2e5 Bq`, `A1 = 5.0e4 Bq` | |
| `T` | `T_days*24*3600` | 6.912 × 10⁵ s |
| `lam` | `ln(2)/T` | 1.003 × 10⁻⁶ s⁻¹ |
| `N0` | `A0/lam` | 3.19 × 10¹¹ (λ = 1.0 × 10⁻⁶ s⁻¹ ile 3.2 × 10¹¹) |
| `t` | `ln(A0/A1)/lam` | 1.851 × 10⁶ s |
| `t_days` | `t/86400` | 21.4 gün (λ = 1.0 × 10⁻⁶ s⁻¹ ile 21.5 gün) |

---

## Biçim uyumu

Sorular [biçim profiline](../formats/dp-physics-2025-format-profile.md) göre gözden geçirildi (2026-10-11).

| Kural | Durum |
|---|---|
| 1A: bağlam + ayrı tek soru cümlesi ("What is …?" / "Which …?") + alt alta A–D | Soru 1–5 uygun |
| 1A: dört seçenek aynı türde, aynı birimde, büyüklük sırasında | Soru 1, 3, 4 uygun (artan); Soru 2 çekirdek + parçacık çifti; Soru 5 cümle biçiminde seçenek |
| 1A: doğru cevap konumu dengeli | D, C, A, B, C |
| 1A: tablo seçenekli biçim örnekte doğrulanamadı | Soru 2 iki bilgiyi tek satırlık seçenekte verir ("… and a neutrino"); tablo kullanılmadı |
| Kapsam sınırı: SL'de yalnızca tam sayı yarı ömür | Soru 1 (SL) tam 2 yarı ömür; keyfi süre yalnızca HL etiketli Soru 6 (c)'de |
| Kapsam sınırı: zayıf çekirdek kuvveti kapsamda değil | Hiçbir soru ve markscheme maddesi zayıf kuvvete başvurmaz |
| Kapsam sınırı: türev ve integral yok | Soru 4 ve 6 yalnızca A = λN ve üstel/logaritma kullanır |
| Kimyasal semboller ezberlenmez | Soru 2, 3 ve 6'da semboller ve Z değerleri soruda verildi |
| Paper 2: alt parça puanı en çok 3; kısa soru 4–9 puan | Soru 6 uygun (2, 2, 3, 2; toplam 9) |
| Paper 2: en az bir AO3 parçası; "Show that" kalıbı | (a) Show that, (c) Determine, (d) Explain; (b) ve (c) verilen yaklaşık değeri kullanır |
| Markscheme: dört sütunlu tablo, ✓, « », OR, OWTTE, kabul aralığı | Soru 6 uygun |
| Değer–birim yazımı, 2 anlamlı basamak | Uygun; Soru 3'te kütleler 6 anlamlı basamak (kütle açığı için gerekli), cevap 2 anlamlı basamak |
| Düzey etiketi | Soru 1–3 SL; Soru 4–6 HL (ek HL içeriği) |

## Bağımsız kontrol

Tarih: 2026-10-11. Yazardan farklı bir kör çözücü soruları cevapları görmeden çözdü; tüm cevap anahtarlarını bağımsız olarak yeniden
üretti, çekirdek denklemlerini (nükleon sayısı ve yük korunumu) ve Paper 1B eğimlerini yeniden hesapladı. Bulgular:
[review/e3-review.md](review/e3-review.md). KRİTİK bulgu yok. Bu kontrol uzman incelemesinin yerine geçmez.

Bulgulara karşılık yapılan değişiklikler (değişen her sayı `python3` ile yeniden hesaplandı):

- **Soru 6 (a) (DÜŞÜK):** "Show that" notu "at least 2 s.f." → "at least 3 s.f. (1.00 × 10⁻⁶)".
- **Soru 6 (d) (DÜŞÜK):** kök "The energy released in each decay is the same, but …" → "For decays to a given energy level of the xenon-131 nucleus, the energy released is the same, but …". Markscheme değişmedi.
- **SL Paper 2 sorusu yok (DÜŞÜK):** bu turda uygulanmadı. Bulgu bir düzeltme değil, yeni bir soru isteğidir; kapsam tablosunun altındaki eksik listesinde yazılı kalır ve sonraki yazım turuna bırakıldı.

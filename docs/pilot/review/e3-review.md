# Bağımsız inceleme: E.3 Radyoaktif bozunma

> Tarih: 2026-10-11. İncelenen dosya: [e3-radioactive-decay-pilot-questions.md](../e3-radioactive-decay-pilot-questions.md).
> Yöntem: önce cevapları çıkarılmış öğrenci görünümü üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtarla karşılaştırma,
> sonra yazım standardı, müfredat analizi (E.3 satırı) ve biçim profiline göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.
> Kullanılan sabit: 1 u = 931.5 MeV c⁻².

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | D (160 → 40, + 20 arka plan = 60 min⁻¹) | D | Evet |
| 2 | C (²²₁₀Ne ve nötrino) | C | Evet |
| 3 | A (Δm = 0.04212 u; 39.23 MeV; 5.60 MeV/nükleon) | A | Evet |
| 4 | B (λ = ln 2 / 1200 s; A = 2.31 × 10⁹ Bq) | B | Evet |
| 5 | C | C | Evet |
| 6 (a) | λ = ln 2 / 6.912 × 10⁵ s = 1.003 × 10⁻⁶ s⁻¹ | 1.00 × 10⁻⁶ s⁻¹ | Evet |
| 6 (b) | N = 3.19 × 10¹¹ (λ = 1.0 × 10⁻⁶ ile 3.2 × 10¹¹) | 3.2 × 10¹¹ | Evet |
| 6 (c) | t = ln 6.4 / λ = 21.4 gün (2.68 yarı ömür) | 21 gün (21–22 kabul) | Evet |
| 6 (d) | Antinötrino da yayılır; enerji β, antinötrino (ve geri tepen çekirdek) arasında değişen oranda paylaşılır | Aynı | Evet |

## Bulgular

KRİTİK ya da ORTA bulgu yok.

### 1. DÜŞÜK — Soru 6 (a): "Show that" için istenen anlamlı basamak

- **Yer:** Soru 6 (a) markscheme, Notes ("at least 2 s.f.").
- **Açıklama:** Hedef "about 1.0 × 10⁻⁶ s⁻¹" iki anlamlı basamak; "Show that" parçasında bir basamak fazlası istenmeli. Answers
  sütunu 1.00 × 10⁻⁶ yazıyor, Notes 2 a.b. yeterli diyor (E.2 Soru 5 (a) ile aynı tutarsızlık; E.1 ve E.4'te 3 a.b. isteniyor).
- **Öneri:** "Answer must be given to at least 3 s.f. (1.00 × 10⁻⁶) for MP2."

### 2. DÜŞÜK — Soru 6 (d): "The energy released in each decay is the same"

- **Yer:** Soru 6 (d) kökü.
- **Açıklama:** Parçanın fiziği doğru. Ancak gerçek iyot-131 için bu cümle tam doğru değil: β⁻ bozunması ksenon-131'in farklı uyarılmış
  düzeylerine gider, yani β + antinötrinoya kalan enerji her bozunmada aynı değildir. Yazar gama yayımını bilerek dışarıda bıraktığını
  not etmiş; yine de belirli bir gerçek nüklit adıyla verilen bir önermenin uzmanca görülmesi iyi olur (güven: yüksek).
- **Öneri:** "For decays to a given energy level of the xenon-131 nucleus, the energy released is the same, but …" ya da parçayı adsız
  bir "beta-minus emitter" için sor.

### 3. DÜŞÜK — Kapsam dengesi: SL düzeyinde yapılandırılmış soru yok (yazarın bildirdiği eksik)

- **Yer:** Kapsam tablosu altındaki not.
- **Açıklama:** Standardın "konu başına en az 1 Paper 2" koşulu karşılanıyor (Soru 6), ama o soru HL. E.3'ün SL çekirdeği (7 saat)
  için Paper 2 sorusu yok. Hata değil, kapsam boşluğu.
- **Öneri:** Sonraki turda SL etiketli kısa bir Paper 2 sorusu (tam sayı yarı ömür + bozunma denklemi + giricilik) eklenmesi.

## Özel olarak istenen denetimler

- **Çekirdek denklemleri:** Soru 2: ²²₁₁Na → ²²₁₀Ne + e⁺ + ν; nükleon 22 = 22, yük 11 = 10 + 1; β⁺ ile nötrino — doğru. Soru 6:
  ¹³¹₅₃I → ¹³¹₅₄Xe + e⁻ + ν̄; nükleon 131 = 131, yük 53 = 54 − 1; β⁻ ile antinötrino — doğru.
- **Alıntılanan veriler (bellekle karşılaştırma):**

| Veri | Dosyada | Benim bildiğim | Güven |
|---|---|---|---|
| Li-7 çekirdek kütlesi | 7.01436 u | atom 7.016003 u − 3 × 0.000549 u = 7.014357 u | Yüksek |
| Proton, nötron kütlesi | 1.00728 u, 1.00866 u | 1.007276 u, 1.008665 u | Yüksek |
| Li-7 nükleon başına bağlanma enerjisi | 5.6 MeV | ≈ 5.61 MeV | Yüksek |
| Z: Na, Ne, Mg | 11, 10, 12 | aynı | Yüksek |
| Na-22 bozunma türü | β⁺ → Ne-22 | β⁺ (ve elektron yakalama) → Ne-22 | Yüksek |
| I-131 yarı ömrü; ürün | 8.0 gün; Xe-131 | 8.02 gün; Xe-131 | Yüksek |
| Z: I, Xe | 53, 54 | aynı | Yüksek |

- **Atom/çekirdek kütlesi karışması:** Soru 3'te lityum için **çekirdek** kütlesi, proton için çıplak proton kütlesi kullanılmış;
  elektron kütleleri tutarlı biçimde dışarıda. Karışma yok.
- **Düzey:** Soru 1 (SL) tam 2 yarı ömür; Soru 2–3 SL çekirdeği. Bozunma sabiti ve A = λN (Soru 4), kesikli çekirdek düzeyleri
  (Soru 5), keyfi zaman aralığı ve sürekli β tayfı (Soru 6) HL etiketli — doğru. Zayıf kuvvete başvurulmuyor; türev/integral yok.
- **Çeldiriciler:** Soru 1 (20; 40; 45), Soru 3 (9.8; 13.1; 39.2 MeV), Soru 4 (1.67 × 10⁹; 3.33 × 10⁹; 1.39 × 10¹¹) yeniden üretildi.
- **Tek doğru cevap:** Soru 5'te A (sürekli β tayfı) nötrinonun kanıtıdır, düzeylerin değil; B ve D rastgelelikle ilgilidir. Yalnızca C.
- **Puanlar:** Soru 6: 2 + 2 + 3 + 2 = 9; her satırdaki ✓ sayısı parça puanına eşit; parça puanları 1–3. (c)'deki kabul aralığı hem
  21.4 (tam λ) hem 21.5 (yuvarlanmış λ) değerini kapsıyor.

# Bağımsız inceleme: D.1 Kütle çekim alanları

> Tarih: 2026-10-11. İncelenen dosya: [d1-gravitational-fields-pilot-questions.md](../d1-gravitational-fields-pilot-questions.md).
> Yöntem: önce cevapsız öğrenci kopyası üzerinden kör çözüm (python3, G = 6.67 × 10⁻¹¹), sonra anahtar ile karşılaştırma, sonra kural
> kontrolü (yazım standardı, müfredat analizi D.1 satırı, biçim profili). Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | r = 3R; g = 3.7/9 = 0.411 N kg⁻¹ → A | A | Evet |
| 2 | T ∝ r^(3/2); 4.0 × 8 = 32 gün → D | D | Evet |
| 3 | G(6.0 − 2.0) × 10³⁰ / (2.0 × 10¹¹)² = 6.67 × 10⁻³ N kg⁻¹ (Q'ya doğru) → C | C | Evet |
| 4 | ΔV = 2.8 × (1 − 1/4) = 2.1 MJ kg⁻¹; W = 3.15 × 10⁸ J → B | B | Evet |
| 5(a) | r = 4.07 × 10⁶ m; v = 1487 m s⁻¹ | 1.49 × 10³ m s⁻¹ | Evet |
| 5(b) | T = 1.72 × 10⁴ s (v = 1.5 × 10³ ile 1.70 × 10⁴ s) | 1.7 × 10⁴ s | Evet |
| 5(c) | −E_toplam = GMm/2r = 9.96 × 10⁸ J (v = 1.5 × 10³ ile 1.01 × 10⁹ J) | 1.0 × 10⁹ J | Evet |
| 5(d) | Toplam enerji azalır → yarıçap küçülür → v = √(GM/r) artar | Aynı üç madde | Evet |

Tüm çeldirici değerleri yeniden hesaplandı (0.925, 1.23, 1.85; 8.0, 10.1, 16; 1.67 × 10⁻³, 3.34 × 10⁻³, 1.33 × 10⁻²; 1.05 × 10⁸,
3.94 × 10⁸, 4.20 × 10⁸; 5(c) için 1.99 × 10⁹ J) ve dosyadaki değerlerle eşleşti.

## Bulgular

KRİTİK: yok. ORTA: yok.

1. **DÜŞÜK — Soru 4, doğru seçenek B.** Tam sonuç 3.15 × 10⁸ J; iki anlamlı basamağa yuvarlamada tam sınırda (3.1 / 3.2). En yakın
   seçenek tartışmasız B'dir, tek doğru cevap korunuyor; yalnızca görünüm sorunu. *Öneri:* kütleyi 160 kg yapmak (3.36 × 10⁸ → 3.4 × 10⁸;
   çeldiriciler 1.1, 4.2 ve 4.5 × 10⁸ olur, yeniden hesaplanmalı) ya da olduğu gibi bırakmak.
2. **DÜŞÜK (şüphe, hata değil) — Soru 5 düzey etiketi.** (a) ve (b), F = GMm/r² ile merkezcil kuvvetten SL bilgisiyle de çözülebilir;
   (c) ve (d) kesin HL. Sorunun bütününün HL etiketlenmesi güvenli taraftadır; yazarın notundaki uzman teyidi isteği yerinde.
3. **DÜŞÜK — Soru 5(a) markscheme notu.** MP1 "r = R + h **AND** ilişki" biçiminde; yanlış r kullanan ama doğru ilişkiyi yazan öğrenci
   için notta "scores zero" deniyor. Tutarlı, ama sert; uzman tercihine bırakılabilir.

## Kontrol edilenler (sorun bulunmadı)

- Müfredat sınırı: tüm yörüngeler çembersel; bileşke alan yalnızca birleştiren doğru üzerinde (Soru 3); potansiyel sonsuzda sıfır;
  sürükleme yalnızca nitel (5d, "without calculation"); türev / integral yok.
- Düzey: Soru 1–3 SL içerik (ters kare, Kepler 3, alan şiddeti); Soru 4 (potansiyel, W = mΔV) ve Soru 5 (yörünge enerjisi, kaçış) HL.
- Puanlar: 5(a) 2, (b) 2, (c) 2, (d) 3 = 9; her parçada ✓ sayısı puana eşit; alt parça ≤ 3.
- "Show that": 1487 m s⁻¹ ≈ 1.5 km s⁻¹; (b) ve (c) hem tam hem verilen değerle anahtardaki sonuca yuvarlanıyor.
- Seçenekler: aynı birim, artan sıra, birbirinden farklı; her soruda tek doğru seçenek.
- Veriler: Mars (g ≈ 3.7 N kg⁻¹, R ≈ 3.39 × 10⁶ m), Ay yüzey potansiyeli (GM/R ≈ 2.82 MJ kg⁻¹), Titan (M ≈ 1.35 × 10²³ kg,
  R ≈ 2.57 × 10⁶ m) bildiğim değerlerle uyumlu. Soru 3'te alan yönü (ağır yıldız Q'ya doğru) doğru.

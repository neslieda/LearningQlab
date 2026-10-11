# Bağımsız inceleme: E.1 Atomun yapısı

> Tarih: 2026-10-11. İncelenen dosya: [e1-structure-of-atom-pilot-questions.md](../e1-structure-of-atom-pilot-questions.md).
> Yöntem: önce cevapları çıkarılmış öğrenci görünümü üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtarla karşılaştırma,
> sonra yazım standardı, müfredat analizi (E.1 satırı) ve biçim profiline göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.
> Kullanılan sabitler: h = 6.63 × 10⁻³⁴ J s, c = 3.00 × 10⁸ m s⁻¹, e = 1.60 × 10⁻¹⁹ C, k = 8.99 × 10⁹ N m² C⁻², R₀ = 1.20 × 10⁻¹⁵ m.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | D | D | Evet |
| 2 | C (en küçük fark 2.10 eV → 592 nm) | C | Evet |
| 3 | A | A | Evet |
| 4 | B (yoğunluk A'dan bağımsız) | B | Evet |
| 5 | A (5/27) | A | Evet |
| 6 (a) | d = k(2e)(50e)/E = 2.615 × 10⁻¹⁴ m | 2.62 × 10⁻¹⁴ m | Evet |
| 6 (b) | R = 5.92 × 10⁻¹⁵ m | 5.9 × 10⁻¹⁵ m | Evet |
| 6 (c)(i) | Alfa, güçlü çekirdek kuvvetinin menziline girer; kuvvet artık yalnızca Coulomb itmesi değildir | Aynı iki madde | Evet |
| 6 (c)(ii) | En yakın yaklaşma = R alınırsa 24.3 MeV; alfa yarıçapı da eklenirse (R<sub>Sn</sub> + R<sub>α</sub> = 7.82 × 10⁻¹⁵ m) 18.4 MeV | 24 MeV (kabul aralığı 23–25) | Kısmen — bkz. bulgu 1 |

Tüm çoktan seçmeli sorularda tek doğru seçenek buldum; çeldirici hesaplarının hepsini yeniden ürettim (Soru 2: 270 / 497 / 1036 nm;
Soru 4: 1/64, 2, 8; Soru 5: 1/3, 4/9, 1) ve yazılan yanılgılar gerçekten o değerleri veriyor.

## Bulgular

### 1. ORTA — Soru 6 (c)(ii): eşik ölçütü soruda yazmıyor; markscheme aralığı makul bir alternatif çözümü dışlıyor

- **Yer:** Soru 6 (c)(ii) kökü ve markscheme satırı ("Accept answers in the range 23–25 MeV").
- **Açıklama:** Soru "sapmaların başladığı enerji"yi istiyor ama hangi ölçütün kullanılacağını söylemiyor. Anahtar, en yakın yaklaşma
  uzaklığını kalay çekirdeğinin yarıçapına eşitliyor (24.3 MeV; yeniden hesapladım, doğru). Aynı derecede savunulabilir bir kestirim,
  iki çekirdeğin yüzeylerinin değdiği durumu alır: d = R₀(120^(1/3) + 4^(1/3)) = 7.82 × 10⁻¹⁵ m → E = 18.4 MeV. Bu fiziksel olarak
  daha iyi bir kestirimdir (yazar da başlık notunda gerçek eşiğin daha düşük olduğunu söylüyor), ancak 23–25 MeV aralığının dışında
  kalır ve markscheme'e göre son puanı alamaz. Hata değil; eksik varsayım + dar kabul aralığı.
- **Öneri (ikisinden biri):** (a) Köke varsayımı ekle: "Assume that deviations begin when the distance of closest approach is equal to
  the radius of the tin nucleus." (b) Ya da Notes'a ekle: "Accept use of R(Sn) + R(α) giving about 18 MeV."

### 2. DÜŞÜK — Soru 6 (b): anlamlı basamak

- **Yer:** Soru 6 (b) markscheme.
- **Açıklama:** R₀ ve A üç anlamlı basamakla verilmiş, cevap 5.9 × 10⁻¹⁵ m (2 a.b.) yazılmış; (c)(ii) bu yuvarlanmış değeri kullanıyor
  (24.2 yerine 24.3 farkı kabul aralığının içinde, sonuç değişmiyor).
- **Öneri:** "5.92 × 10⁻¹⁵ «m»" yaz, Notes'a "Accept 5.9 × 10⁻¹⁵" ekle.

### 3. DÜŞÜK — Soru 3: "wavelengths that sodium emits" ifadesi

- **Yer:** Soru 3 seçenek A, B, D.
- **Açıklama:** Soğuk buhar yalnızca taban düzeyinden başlayan geçişleri soğurur; sodyumun yaydığı her dalga boyunda karanlık çizgi
  oluşmaz. Tek doğru cevap değişmiyor (A), ama ifade "bazı" yerine "tüm" yayma çizgileri diye okunabilir.
- **Öneri:** "at certain wavelengths that sodium can emit".

## Sorun bulunmayan denetimler

- **Müfredat sınırı ve düzey:** Soru 1 (SL) yalnızca nitel; Soru 2–3 SL çekirdeği (kesikli düzeyler, E = hf, soğurma tayfı). Çekirdek
  yarıçapı/yoğunluğu (Soru 4), Bohr modeli (Soru 5), en yakın yaklaşma ve Rutherford'dan sapma (Soru 6) HL etiketli — doğru. Saçılma
  hesabı yalnızca elektriksel itme kullanıyor; güçlü kuvvet yalnızca nitel. Türev/integral yok. Sn için sembol ve Z soruda verilmiş.
- **Veriler:** Z(Sn) = 50 doğru (güven: yüksek); R₀ = 1.20 × 10⁻¹⁵ m veri kitapçığı değeriyle uyumlu (güven: yüksek); 5.5 MeV tipik
  bir alfa kaynağı için gerçekçi (Am-241 ≈ 5.49 MeV; güven: yüksek).
- **Puanlar:** Soru 6 parçaları 3 + 1 + 2 + 2 = 8; her satırdaki ✓ sayısı parça puanına eşit; hiçbir parça 3'ü geçmiyor.
- **Biçim:** sayısal seçenekler artan sırada ve aynı birimde; doğru cevap konumları D, C, A, B, A; formül zinciri tablosu hesaplarımla
  aynı (8.80 × 10⁻¹³ J; 2.615 × 10⁻¹⁴ m; 5.92 × 10⁻¹⁵ m; 24.3 MeV).

# Bağımsız inceleme: C.3 Dalga olayları

> Tarih: 2026-10-11. İncelenen dosya: [c3-wave-phenomena-pilot-questions.md](../c3-wave-phenomena-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtar ve markscheme ile
> karşılaştırma, sonra yazım standardı, müfredat analizi (C.3 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | sin θc = 1.3/1.6 = 0.8125 → 54.3° → **D** | D | Evet |
| 2 (1A) | s = λD/d → 2.0 × 3/2 = 3.0 mm → **C** | C | Evet |
| 3 (1A) | Yol farkı 0.68 m = λ/2 → λ = 1.36 m → f = 250 Hz → **B** | B | Evet |
| 4 (1A) | d = 2.5 × 10⁻⁶ m; n ≤ d/λ = 4.17 → 4 → **A** | A | Evet |
| 5 (1A) | θ = λ/b = 6.0 × 10⁻³ rad; yarı genişlik 12 mm; tam genişlik 24 mm → **C** | C | Evet |
| 6 (a) | İki yarıktan gelen (eşfazlı) ışık ekranda üst üste biner; yol farkı nλ ise aynı fazda varır → yapıcı girişim | Aynı | Evet |
| 6 (b) | s = 15.2/4 = 3.8 mm; d = 633 × 10⁻⁹ × 3.0 / 3.8 × 10⁻³ = 5.00 × 10⁻⁴ m | 5.0 × 10⁻⁴ m | Evet |
| 6 (c)(i) | θ = λ/b = 6.33 × 10⁻³ rad (0.36°) | 6.3 × 10⁻³ rad | Evet |
| 6 (c)(ii) | d/b = 5.0 → 5. mertebe zarfın minimumunda, şiddeti sıfır → n = −4 … +4 → 9 saçak. Kör çözümde "genişlik / saçak aralığı = 10" yolunun da doğal olduğunu not ettim | 9 | Evet (Bulgu 1) |
| 6 (d) | Saçaklar daralır / keskinleşir ve parlaklaşır; konumları değişmez | Aynı | Evet |

Çeldiriciler yeniden hesaplandı: S1 90 − 54.3 = 35.7°; asin(1/1.6) = 38.7°; asin(1/1.3) = 50.3°. S2 0.33; 1.33; 12. S3 125; 500; 750.
S4 sin θ₄ = 0.96, n = 5 için 1.2 > 1; 8 ve 9 sayım hataları. S5 6.0; 12; 48 mm. Hepsi yazılan hesaptan çıkıyor; her 1A sorusunda tek
doğru seçenek var.

Kural denetimi: Soru 1–3 SL (kritik açı, çift yarık, yol farkı) ve Soru 4–6 HL (kırınım ağı, tek yarık, modülasyon, çoklu yarık) —
etiketler doğru. Yarık ve ağ sorularının hepsinde "incident normally" var; Soru 5'te "single rectangular slit" ve tek renkli ışık var.
Yarık genişliğinin şiddete etkisi nicel sorulmuyor; şiddet hesabı yok. Türev/integral yok. Seçenekler aynı birimde, artan sırada.
Soru 6 puanları 2+2+1+3+1 = 9; markscheme ✓ sayıları parça puanlarıyla eşleşiyor. Veriler gerçekçi (633 nm He–Ne lazer; n = 1.6
plastik, n = 1.3 su; 400 çizgi/mm ağ; 0.10 mm yarık).

## Bulgular

KRİTİK bulgu yok. Soru 6 (c)(ii)'de anahtar fizik olarak doğru, ama soru sınır durumuna denk geliyor.

### 1. ORTA — Soru 6 (c)(ii): girişim mertebesi tam olarak tek yarık minimumuna denk geliyor

- **Yer:** Soru 6 (c)(ii) ve markscheme satırı; veriler d = 0.50 mm, b = 0.10 mm (d/b = 5.0 tam).
- **Açıklama:** Fizik açısından savunulabilir tek sayı 9'dur: 5. mertebe saçak zarfın sıfır şiddetli noktasında olduğundan görülmez
  ve "merkezî maksimumun içinde" de değildir (sınırındadır). Ancak sınır durumu üç farklı cevap üretir:
  - 9 — eksik mertebe fark edilirse (anahtar);
  - 11 — n ≤ 5 koşulu "dahil" sayılırsa (markscheme [2 max] veriyor);
  - 10 — öğrenci merkezî maksimumun ekrandaki genişliğini saçak aralığına bölerse: 2 × 3.0 × 6.33 × 10⁻³ = 38.0 mm;
    38.0 / 3.80 = 10.0. Bu çok yaygın bir yoldur ve markscheme'de hiç ele alınmamış.
  Ayrıca öğrenci (b)'de bulduğu 0.4997 mm değerini kullanırsa d/b = 4.997 çıkar ve eksik mertebe tartışması hiç doğmaz; soru bunu
  "Use a slit separation of 0.50 mm" ile engelliyor ama sonuç tek bir yuvarlamaya bağlı kalıyor. Yazarın kendi notu (4) de kurumun
  beklentisinin teyit edilmediğini söylüyor. Gerçek deneyde yarık genişliğindeki %1'lik sapma 5. mertebeyi zayıf da olsa görünür
  kılar; "tam çakışma" ideal bir durumdur.
- **Öneri A (sınır durumundan kaçın, önerilen):** yarık genişliğini **0.11 mm** yap, d = 0.50 mm kalsın.
  - (c)(i): θ = 633 × 10⁻⁹ / 0.11 × 10⁻³ = **5.8 × 10⁻³ rad** (0.33°).
  - (c)(ii): d/b = 4.55 → zarfın içindeki en yüksek mertebe 4 → **9 saçak**. Genişlik / aralık yolu da 34.5 mm / 3.80 mm = 9.09 → 9
    verir; yani her iki yol aynı sayıya çıkar. 5. mertebe (6.33 × 10⁻³ rad) ilk minimumun dışında, ikincil maksimumda kalır.
  - Markscheme'in ikinci maddesi şöyle olur: "fringes of order up to 4 lie inside the central maximum «4 × 1.27 × 10⁻³ < 5.8 × 10⁻³ <
    5 × 1.27 × 10⁻³»". (b) parçası ve 15.2 mm verisi değişmez.
  - Kaçınılacak değerler: b = 0.125 mm (d/b = 4.0) ve b = 0.10 mm (5.0) yine sınır durumudur.
- **Öneri B (sınır durumunu koru, açıkça sor):** veriler kalır; (c)(ii) ikiye bölünür: "Show that the fifth-order bright fringe is not
  observed. [2]" ve "State the number of bright fringes observed within the central maximum. [1]". Böylece eksik mertebe sorunun
  kendisi olur, tuzak olmaktan çıkar. Markscheme'e "10 (width ÷ fringe spacing without considering the missing order) scores [0]
  for the last part" notu eklenir.
- Hangi öneri seçilirse seçilsin, mevcut markscheme'e 10 cevabının nasıl puanlanacağı yazılmalı.

### Şüphe (hata değil)

- "Yalnızca dik geliş" sınırının Soru 1 (kritik açı) için uygulanmaması: Snell yasası ve kritik açı müfredat satırında açıkça yer
  aldığı için yazarın yorumu makul; yine de uzman teyidi gerekir (yazar da not etmiş).
- Soru 6 (a) markscheme'inin ilk maddesi "coherent AND superposes" istiyor; yalnızca "superpose" yazan öğrenci puanı kaçırır. Uzman
  "coherent" koşulunu ayrı bir kabul notuna taşımak isteyebilir.
- Soru 4'ün C ve D çeldiricileri (8 ve 9) aynı hatanın iki biçimi (mertebe yerine maksimum sayısı vermek); değerler tutarlı,
  değişiklik zorunlu değil.

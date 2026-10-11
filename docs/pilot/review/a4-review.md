# Bağımsız inceleme: A.4 Katı cisim mekaniği

> Tarih: 2026-10-11. İncelenen dosya: [a4-rigid-body-mechanics-pilot-questions.md](../a4-rigid-body-mechanics-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; g = 9.8 m s⁻²), sonra anahtar ve
> markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (A.4 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | Menteşeye göre tork: T × 2.0 = 200 × 1.5 + 150 × 3.0 = 750 N m; T = 375 N → **C** | C | Evet |
| 2 (1A) | I = 0.25 kg m²; τ = 1.5 N m; α = 6.0 rad s⁻²; ω = 30 rad s⁻¹ → **B** | B | Evet |
| 3 (1A) | I′ = 0.80 + 2.0 × 0.50² = 1.30 kg m²; ω = 0.80 × 3.0 / 1.30 = 1.85 rad s⁻¹ → **A** | A | Evet |
| 4 (1A) | Dönme ⅕Mv², öteleme ½Mv²; oran = 5/7 → **D** | D | Evet |
| 5 (a) | v = ωR | v = ωR | Evet |
| 5 (b) | Mgh = ½Mv² + ½(MR²)(v/R)² = Mv²; v = √(9.8 × 0.90) = 2.97 m s⁻¹ | 2.97 m s⁻¹ | Evet |
| 5 (c) | L = Iω = MRv = 12 × 0.15 × 2.97 = 5.35 kg m² s⁻¹ (3.0 m s⁻¹ ile 5.40) | 5.4 (aralık 5.3–5.4) | Evet |
| 5 (d) | Aynı potansiyel enerji kaybı; silindirin I'sı küçük → kinetik enerjinin daha büyük payı öteleme → her noktada daha hızlı → daha kısa süre | Aynı üç madde | Evet |

Çeldiriciler yeniden hesaplandı: S1 A 225 N, B 350 N, D 525 N; S2 A 15, C 60, D 120 rad s⁻¹; S3 B 2.35, D 4.875 rad s⁻¹; S4 A 2/7.
Hepsi tabloda yazan yanılgıdan çıkıyor. S1'de menteşe kuvveti (25 N, aşağı) ve S5 notundaki √(2gh) = 4.2 m s⁻¹ doğrulandı.

## Bulgular

**KRİTİK:** yok. **ORTA:** yok.

### DÜŞÜK

1. **Soru 5 (b), markscheme ikinci madde.** "to get *Mgh* = *Mv*² / *v* = √(*gh*)" satırındaki "/" alternatif ayırıcısı olarak
   kullanılmış, ama bir formül satırında bölme işareti gibi okunuyor (*Mv*²/*v*). *Öneri:* "to get *Mgh* = *Mv*² **OR**
   *v* = √(*gh*)".

2. **Soru 5 (b), hedef değerin duyarlılığı.** "about 3 m s⁻¹" tek anlamlı basamak; markscheme notu "en az 2 anlamlı basamak (3.0)"
   istiyor ve (c) 3.0 ile hesaplıyor. Tutarlı çalışıyor ((c) aralığı 5.3–5.4 her iki değeri kapsıyor), ama diğer setlerde hedef 2
   anlamlı basamakla verilmiş. *Öneri:* "about 3.0 m s⁻¹" yazılsın, not "en az 3 anlamlı basamak (2.97)" olsun.

3. **Soru 1, anlamlı basamak.** Veriler "200 N", "150 N" (anlamlı basamak sayısı belirsiz), seçenekler 3 anlamlı basamak. Dosya
   bunu not ediyor. Değişiklik şart değil.

### Şüphe (doğrulanmış hata değil)

- **Soru 1 ve "kütle merkezi hesabı yok" sınırı.** Düzgün kirişin ağırlığının orta noktadan etkimesi bir kütle merkezi *hesabı*
  değil, bilinen bir sonuç; sınırın içinde sayıyorum. Yazar da bunu kendi yorumu olarak işaretlemiş; uzman teyidi yerinde olur.
- **Soru 5 (d), "without calculation".** Markscheme enerji paylaşımı üzerinden nitel bir gerekçe istiyor; cebirsel v = √(2gh/(1+k))
  yazan öğrencinin puan alıp almayacağı belirtilmemiş. *Öneri:* nota "Accept a correct algebraic comparison" eklenebilir.

## Hata bulunmayan denetimler

- Tek doğru seçenek: dört 1A sorusunda da yalnızca bir seçenek savunulabilir.
- Müfredat sınırı: belirli şekillerin I formülü S2, S4, S5'te soruda verilmiş; S3'te tablanın I değeri sayısal, kil nokta kütle
  (mr²); dönme + öteleme yalnızca kaymadan yuvarlanma; vektörel işlem yok; türev/integral yok. Düzey etiketi HL doğru.
- Seçenekler aynı birimde ve artan sırada (S4 kesirleri: 0.286, 0.400, 0.500, 0.714); doğru cevap konumları C, B, A, D.
- Soru 5: alt parça puanları 1, 3, 2, 3; markscheme ✓ sayıları 1, 3, 2, 3; toplam 9. "Show that" değeri hem tam (2.97) hem verilen
  (3.0) değerle (c)'de kabul aralığına düşüyor.
- Yön ve işaret: S1'de kablo torku saat yönünün tersine, iki ağırlığın torku saat yönünde; menteşe kuvveti aşağı çıkıyor ve bu
  fiziksel olarak tutarlı (kablo, yüklerin ağırlık merkezinin iç tarafında). S3'te düşey düşen kilin eksene göre açısal momentumu
  sıfır.
- Şekil: S1'in şekil tarifi öğrenci kopyasında mevcut ve soru şekilsiz de çözülüyor.
- Gerçekçilik: 12 kg, 0.15 m yarıçaplı çelik boru; 8.0 kg volan; 0.80 kg m² tabla. Makul.

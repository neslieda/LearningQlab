# Bağımsız inceleme: A.3 İş, enerji ve güç

> Tarih: 2026-10-11. İncelenen dosya: [a3-work-energy-power-pilot-questions.md](../a3-work-energy-power-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; g = 9.8 m s⁻²), sonra anahtar ve
> markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (A.3 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | W = 25 × 40 × cos 60° = 500 J → **B** | B | Evet |
| 2 (1A) | P_yararlı = 150 × 9.8 × 0.40 = 588 W; verim = 588 / 840 = 0.70 → **D** | D | Evet |
| 3 (1A) | mgh = 29.4 J; E_k = 16.0 J; sürtünme işi 13.4 J; f = 13.4 / 5.0 = 2.68 N → **A** | A | Evet |
| 4 (1A) | E ∝ x²; 9E − E = 8E → **C** | C | Evet |
| 5 (a) | 2.5 × 9.8 × 18 + ½ × 2.5 × 4.0² = 441 + 20 = 461 W | 461 W | Evet |
| 5 (b) | P_giriş = 461 / 0.12 = 3.84 × 10³ W; E = 1.38 × 10⁷ J; V = 3.84 × 10⁻⁴ m³ (460 W ile 3.83 × 10⁻⁴) → 3.8 × 10⁻⁴ m³ | 3.8 × 10⁻⁴ m³ | Evet |
| 5 (c) | 0.12 | 0.12 (ya da 12 : 100, yaklaşık 1/8) | Evet |
| 5 (d) | Güç ve yükseklik aynı; kilogram başına aktarılan enerji (gh + ½v²) artar → saniyede taşınan kütle azalır | Aynı iki madde | Evet |

Çeldiriciler yeniden hesaplandı: S1 C 866 J, D 1000 J; S2 A 0.0714, B 0.30, C 0.4286; S3 B 3.2 N, C 5.88 N, D 8.93 N; S4 A, B, D
cebirsel. Hepsi tabloda yazan yanılgıdan çıkıyor. S5 (b) notundaki 5.5 × 10⁻⁶ m³ (verim çarpılırsa) 5.52 × 10⁻⁶ olarak doğrulandı.

## Bulgular

**KRİTİK:** yok. **ORTA:** yok.

### DÜŞÜK

1. **Soru 5 (a), "useful power output" ifadesi.** Sulama pompasında çıkış suyunun kinetik enerjisinin "yararlı" sayılıp
   sayılmayacağı öğrenci için kendiliğinden açık değil; yalnızca yükseltme alınırsa 441 W çıkar. Hedef değer (≈ 460 W) ve verilen
   çıkış sürati doğru yolu işaret ediyor, markscheme de 441 W için [1] max diyor; bu yüzden çözülebilir, ama ifade netleştirilebilir.
   (d) parçası da aynı tanıma dayanıyor. *Öneri:* "Show that the rate at which the pump transfers energy to the water is about
   460 W. This is the useful power output of the pump."

2. **Soru 5, puan toplamı.** SL etiketli soru 9 puan; biçim profili SL kısa sorularını 4–6 puan olarak gözlemlemiş. Dosya bunu
   kendisi not ediyor ve uzman teyidi istiyor; ek bir işlem gerekmez, kayıt için yazıldı.

3. **Soru 5 (c), "about 1/8".** 1/8 = 0.125, verimden (0.12) %4 farklı. Kabul edilebilir bir yuvarlama, ama "State the value"
   için gereksiz gevşek. *Öneri:* "0.12 **OR** 12 : 100 **OR** 3/25" yeterli.

### Şüphe (doğrulanmış hata değil)

- **Soru 3, adım sayısı.** Üç kısa adım (potansiyel enerji, kinetik enerji, fark / yol); profildeki "bir ya da iki adım" gözleminin
  üstünde. Dosya bunu not ediyor. Sayılar temiz olduğu için sorun görmüyorum.
- **Enerji yoğunluğu birimi.** J m⁻³ kullanılmış; rehberin tanımı yazar tarafından da teyit edilmemiş. Uzman teyidi gerekir.

## Hata bulunmayan denetimler

- Tek doğru seçenek: dört 1A sorusunda da yalnızca bir seçenek savunulabilir. S1'de "0 J" net iş yanılgısıdır, doğru sayılamaz.
- Müfredat sınırı: yerçekimi potansiyel enerjisi yalnızca mgΔh; türev/integral yok; Sankey yalnızca oran olarak soruluyor. Düzey
  etiketi SL doğru.
- Seçenekler aynı birimde ve artan sırada; doğru cevap konumları B, D, A, C; S4'te "additional" koyu.
- Soru 5: alt parça puanları 3, 3, 1, 2; markscheme ✓ sayıları 3, 3, 1, 2; toplam 9. "Show that" değeri (460 W) ile tam değer
  (461 W) (b)'de aynı 2 anlamlı basamaklı sonucu veriyor (3.8 × 10⁻⁴ m³).
- Yön ve işaret: S1'de kuvvetin yer değiştirme doğrultusundaki bileşeni cos 60°; S3'te sürtünme yol boyunca (5.0 m) etkiyor.
- Gerçekçilik: dizel enerji yoğunluğu (3.6 × 10¹⁰ J m⁻³ ≈ 36 MJ litre⁻¹) genel bilgiyle tutarlı; %12 toplam verim küçük bir dizel
  pompa için makul; saatte 0.38 litre yakıt makul. (d)'deki senaryo (dar ağız, daha yüksek sürat, daha az kütle akışı) kütle
  korunumuyla çelişmiyor.
- Şekil gerektiren soru yok; eksik bilgi yok.

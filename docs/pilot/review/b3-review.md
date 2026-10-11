# Bağımsız inceleme: B.3 Gaz yasaları

> Tarih: 2026-10-11. İncelenen dosya: [b3-gas-laws-pilot-questions.md](../b3-gas-laws-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; R = 8.31 J K⁻¹ mol⁻¹,
> k = 1.38 × 10⁻²³ J K⁻¹), sonra anahtar ve markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (B.3 satırı) ve
> biçim profiline göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | N = PV / kT = 300 / (1.38 × 10⁻²³ × 300) = 7.25 × 10²² → **A** | A | Evet |
| 2 (1A) | U = 3⁄2 PV = 1.5 × 2.0 × 10⁵ × 0.040 = 12 kJ → **C** | C | Evet |
| 3 (1A) | Düşük basınç, yüksek sıcaklık → **D** | D | Evet |
| 4 (1A) | P = ⅓ρv², P aynı → v ∝ 1/√ρ → 1⁄2 → **B** | B | Evet |
| 5 (a) | T = 290 K; n = 1.8 × 10⁵ / (8.31 × 290) = 74.7 mol | 74.7 mol | Evet |
| 5 (b) | P₂ = 1.5 × 10⁷ × 319 / 290 = 1.65 × 10⁷ Pa | 1.65 × 10⁷ Pa | Evet |
| 5 (c) | Sıcaklık artınca ortalama sürat / kinetik enerji artar; duvara çarpmalar sıklaşır ve çarpma başına momentum değişimi büyür; hacim sabitken duvara kuvvet artar | Aynı (3 maddeden 2) | Evet |
| 5 (d) | ΔU = 3⁄2 nRΔT = 2.70 × 10⁴ J (n = 75 mol ile 2.71 × 10⁴ J); 3⁄2 VΔP = 2.70 × 10⁴ J | 2.7 × 10⁴ J | Evet |
| 5 (e) | Basınç / yoğunluk çok yüksek: atom hacmi ve atomlar arası kuvvetler ihmal edilemez | Aynı | Evet |
| 6 (a) | Gazın hacmi ya da gaz miktarı (kütle) | Aynı | Evet |
| 6 (b) | Balondaki havanın suyla ısıl dengeye gelmesi için | Aynı | Evet |
| 6 (c) | Doğru değil: doğru orijinden geçmiyor (kesim 95 kPa, belirsizlik 1 kPa); P/θ sabit değil (9.8 ↔ 1.4); ilişki doğrusal, P kelvin sıcaklığıyla orantılı | Aynı | Evet |
| 6 (d) | θ₀ = −95.0 / 0.345 = −275 °C | −275 °C | Evet |
| 6 (e) | −94.0 / 0.367 = −256 °C; −95.8 / 0.325 = −295 °C; yarı aralık 19.3 °C ≈ 20 °C | 20 °C (19, 19.5 kabul) | Evet |
| 6 (f) | −273 °C, (−275 ± 20) °C aralığının içinde → tutarlı | Aynı | Evet |
| 6 (g) | Daha geniş sıcaklık aralığı (dış değerleme kısalır) ya da daha duyarlı basınç ölçer (çubuklar küçülür) | Aynı | Evet |

Yeniden hesaplananlar: S1 çeldiricileri B 6.0 × 10²³, C 8.05 × 10²³, D 2.17 × 10²⁵; S2 A 5.33, B 8.0, D 24 kJ; S5 (b) notundaki
1.66 × 10⁷ Pa (n = 75 mol ile 1.657 × 10⁷) ve 4.1 × 10⁷ Pa (Celsius ile 4.06 × 10⁷). Hepsi doğru.

Soru 6 verisi bağımsız olarak yeniden işlendi: en küçük kareler eğimi 0.3450 kPa °C⁻¹, kesim 94.95 kPa, θ₀ = −275.2 °C. Tüm
±1 kPa çubuklarından geçen en dik doğru (30 °C; 105) ve (90 °C; 127) uçlarından: eğim 0.3667, kesim 94.00, θ₀ = −256.4 °C. En yatık
doğru (10 °C; 99) ve (90 °C; 125) uçlarından: eğim 0.3250, kesim 95.75, θ₀ = −294.6 °C. Yarı aralık 19.1 °C (verilen yuvarlak
değerlerle 19.3 °C). Dosyadaki değerler ve "Şekil notu" bununla uyuşuyor.

Kural denetimi: SL etiketi doğru; yalnızca sabit hacim ve ideal gaz yasası kullanılıyor; türev/integral/logaritma yok; seçenekler
aynı türde ve artan sırada; her 1A sorusunda tek doğru seçenek; Soru 5 puanları 2 + 2 + 2 + 2 + 1 = 9, Soru 6 puanları
1 + 1 + 2 + 2 + 2 + 1 + 2 = 11; markscheme madde sayıları parça puanlarıyla (ve "2 max" notuyla) eşleşiyor.

Yazarın işaretlediği noktalar:

- **"Root mean square speed" (Soru 4).** Fizik olarak doğru terim: P = ⅓ρ⟨v²⟩ ifadesindeki sürat karelerin ortalamasının
  kareköküdür; cevap terimden bağımsız olarak 1⁄2'dir. Rehberin bu formüldeki v için kullandığı sözcük bu incelemede de
  doğrulanamadı (aşağıda DÜŞÜK-1).
- **1.5 × 10⁷ Pa'da helyumun ideal sayılması (Soru 5).** Kök "is assumed to behave as an ideal gas" diyor ve (e) parçası bu
  varsayımı sorguluyor; soru kendi içinde tutarlı. Kendi kaba tahminim (helyumun ikinci virial katsayısı ≈ 12 cm³ mol⁻¹, genel
  bilgiden, teyitsiz): sapma yaklaşık %7; yani (e)'nin beklediği cevap gerçekçi, (a)–(d) ise açık varsayım altında geçerli.

## Bulgular

**KRİTİK:** yok. **ORTA:** yok.

### DÜŞÜK

1. **Soru 4, terim (şüphe, doğrulanmış hata değil).** "root mean square speed" teriminin rehberde / veri kitapçığında P = ⅓ρv²
   için kullanılan ifadeyle aynı olduğu teyit edilemedi. Cevap etkilenmiyor. *Öneri:* uzman teyidine kadar kalsın; rehber farklı
   bir ifade kullanıyorsa soru cümlesi ona uydurulsun.

2. **Soru 6 (e), verilen en dik / en yatık doğrular yuvarlama yüzünden çubukların ucunu çok az aşıyor.** 0.367 × 90 + 94.0 =
   127.03 kPa (çubuk üst ucu 127) ve 0.325 × 10 + 95.8 = 99.05 kPa (çubuk üst ucu 99). Bu doğrular iki çubuk ucuna dayandığı için
   üç anlamlı basamağa her yuvarlama bir ucu taşırır. θ₀ üzerindeki etkisi 0.3 °C; cevap değişmiyor. *Öneri:* metinde
   "(values rounded to three significant figures)" notu eklensin ya da değerler 0.3667 / 94.00 ve 0.3250 / 95.75 verilsin
   (o zaman −256.4 °C ve −294.6 °C, yarı aralık 19 °C; markscheme "19 «°C», accept 20" olur).

3. **Soru 6 (e) notu, "larger difference from the best-fit value (20 °C)".** Verilen değerlerle farklar 294.8 − 275.4 = 19.4 °C
   ve 275.4 − 256.1 = 19.2 °C; ikisi de 19 °C'ye yuvarlanır. 20 °C yalnızca önce tam sayıya yuvarlanmış θ₀ değerleriyle
   (295 − 275) çıkar. Kabul edilen cevaplar (19, 19.5, 20) zaten bunu kapsıyor; notun sayısı "19 or 20 °C" yapılabilir.

4. **Soru 6, biçim.** Biçim profiline göre 1B'de en uygun doğruyu öğrenci çizer; burada eğim ve kesim metinde verildi. Dosya bunu
   "Biçim uyumu"nda kendisi uygun değil olarak işaretliyor; kayıt için yazıldı.

5. **Soru 5, puan toplamı.** SL etiketli soru 9 puan; biçim profili SL kısa sorularını 4–6 puan olarak gözlemlemiş. Yazım
   standardı 4–9'a izin veriyor; uzman teyidi için kayıt.

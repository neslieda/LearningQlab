# Bağımsız inceleme: B.2 Sera etkisi

> Tarih: 2026-10-11. İncelenen dosya: [b2-greenhouse-effect-pilot-questions.md](../b2-greenhouse-effect-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴), sonra
> anahtar ve markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (B.2 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | 600 / 4 × (1 − 0.30) = 105 W m⁻² → **B** | B | Evet |
| 2 (1A) | Şiddet 1/4'e düşer; T ∝ S^(1/4) → T / √2 → **C** | C | Evet |
| 3 (1A) | Rezonans: ışınım frekansı molekülün doğal titreşim frekansıyla eşleşir → **A** | A | Evet |
| 4 (1A) | Soğurulan = yayılan = 238; albedo = (340 − 238) / 340 = 0.30 → **D** | D | Evet |
| 5 (a) | Gezegen πR² kesitiyle yakalar, güç 4πR² yüzeye dağılır → 880 / 4 = 220 W m⁻² | Aynı iki madde | Evet |
| 5 (b) | 0.75 × 220 = 165 W m⁻²; T = (165 / σ)^(1/4) = 232.3 K | 232 K | Evet |
| 5 (c) | CO₂ yüzeyin yaydığı kızılötesini soğurur, her yöne yeniden yayar; bir kısmı yüzeye döner; denge için yüzey daha sıcak olmalı | Aynı (3 maddeden 2) | Evet |
| 5 (d) | e = 165 / (σ × 250⁴) = 165 / 221.5 = 0.745; (232.3 / 250)⁴ = 0.745; (230 / 250)⁴ = 0.716 | 0.74 ya da 0.75; aralık 0.72–0.75 | Evet |

Enerji dengesi baştan sona sayısal olarak doğrulandı: S/4 = 220; soğurulan 165 W m⁻²; T_eq = 232.26 K; σ × 250⁴ = 221.48 W m⁻²;
e = 0.74497. Çeldiriciler yeniden hesaplandı: S1 A 45, C 150, D 420; S2 A 0.25T, B 0.50T, D 0.841T; S4 A 1.43, B 0.70, C 0.429.
Hepsi tabloda yazan yanılgıdan çıkıyor. Her soruda tek doğru seçenek var.

Kural denetimi: SL etiketi doğru; enerji dengesi tek katmanlı / etkin yayıcılık düzeyinde (sınır içinde); türev/integral yok;
Soru 5 parça puanları 2 + 3 + 2 + 2 = 9; (c) üç maddeden "2 max" doğru yazılmış; seçenekler sıralı (S1, S2 artan; S4 azalan).
Soru 2'deki ters kare yasası B.1'deki görünür parlaklık (b = L / 4πd²) kazanımına dayanıyor; müfredat içinde, soru tek cevaplı.
Soru 4'teki 340 W m⁻² ve albedo 0.30 Dünya için bilinen değerlerle uyumlu; diğer gezegenler kurgusal ve makul.

## Bulgular

**KRİTİK:** yok.

### ORTA

1. **Soru 5 (d), yanlış yoldan doğru sayı: e = 1 − albedo = 0.75.** Bu veriyle σ × 250⁴ = 221.5 W m⁻² neredeyse tam olarak
   S/4 = 220 W m⁻²'ye eşit. Bu yüzden e = (1 − α)(S/4) / (σT⁴) ≈ 1 − α çıkıyor. "Yayıcılık = 1 − albedo" yazan (fiziksel olarak
   yanlış akıl yürüten) öğrenci 0.75 buluyor ve bu, markscheme'in kabul ettiği cevaplardan biri. Yalnızca sonuç yazan öğrenci için
   doğru ile yanlış yöntem ayırt edilemiyor. *Öneri:* aşağıdaki ORTA-2 düzeltmesindeki veri (yüzey sıcaklığı 260 K) bu rastlantıyı
   da kaldırır.

2. **Soru 5 (d), iki yolun farklı sonuç vermesi ve kabul aralığı (yazarın işaretlediği nokta).** Parça iyi tanımlı: model cümlesi
   (gezegen + atmosfer, 250 K sıcaklıkta ve e yayıcılığında bir cisim gibi ışır) ile enerji dengesi eσT⁴ = soğurulan şiddet tek
   bir denklem verir. Tam değer 0.745; (b)'deki yuvarlanmış 230 K ile (230/250)⁴ = 0.716. Dördüncü kuvvet 232 → 230 yuvarlamasını
   %4'e büyütüyor; 0.72–0.75 aralığı bu nedenle gerekçeli ve doğru hesaplanmış, ama 2 anlamlı basamakta üç farklı kabul edilen
   cevap (0.72, 0.74, 0.75) var. Ayrıca 0.74497 kesin yuvarlamayla 0.74'tür; "0.75" yalnızca 0.745 ara değerinden gelir.
   *Öneri (yeniden hesaplandı):* albedo 0.28, ölçülen yüzey sıcaklığı 260 K. O zaman (a) değişmez (220 W m⁻²); (b) soğurulan
   0.72 × 220 = 158.4 W m⁻², T = 229.9 K ("about 230 K" neredeyse tam); (d) e = 158.4 / (σ × 260⁴) = 158.4 / 259.1 = 0.611 ve
   (230/260)⁴ = 0.612 → iki yol da 0.61. 1 − α = 0.72 artık cevapla karışmaz. Kabul aralığına gerek kalmaz.

### DÜŞÜK

1. **Soru 4, seçenek A (albedo 1.4).** Albedo tanım gereği 0–1 arasındadır; bu seçenek hesap yapmadan elenir ve soru fiilen üç
   seçenekli olur. Tek doğru cevap etkilenmiyor; çeldiricinin yanılgısı (oranın ters kurulması) gerçek ve değer doğru
   (340 / 238 = 1.43). *Öneri:* A yerine 0.18 (yansıyan güç, gelen + yayılan toplamına oranlanır: 102 / 578 = 0.176) ya da benzer
   0–1 arası bir değer; seçenekler yeniden sıralanmalı ve doğru cevap konumu dengesi yeniden kontrol edilmeli.

2. **Soru 5, puan toplamı.** SL etiketli soru 9 puan; biçim profili SL kısa sorularını 4–6 puan olarak gözlemlemiş. Yazım
   standardı 4–9'a izin veriyor; uzman teyidi için kayıt.

3. **Soru 5 (d), model uyumu (şüphe, doğrulanmış hata değil).** "Etkin yayıcılık" modelinin rehberin beklediği enerji dengesi
   modeliyle örtüşüp örtüşmediğini dosya da doğrulanmamış olarak işaretliyor; bu incelemede de kaynakla teyit edilemedi. Fizik
   olarak tutarlı; uzman teyidi gerekir.

# Bağımsız inceleme: B.4 Termodinamik

> Tarih: 2026-10-11. İncelenen dosya: [b4-thermodynamics-pilot-questions.md](../b4-thermodynamics-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; Clausius işaret kuralı
> Q = ΔU + W), sonra anahtar ve markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (B.4 satırı) ve biçim profiline
> göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | Q = +500 J, W = −200 J; ΔU = Q − W = +700 J → **D** | D | Evet |
| 2 (1A) | P₂ = P × 8^(5/3) = 32P → **B** | B | Evet |
| 3 (1A) | Ω₁ = 1, Ω₂ = 4! / (2! 2!) = 6; ΔS = k ln 6 → **C** (D için aşağıda ORTA-1) | C | Evet |
| 4 (1A) | W = 800 − 600 = 200 J; verim = 200 / 800 = 0.25 → **A** | A | Evet |
| 5 (1A) | ΔU = 0 → Q = W = +600 J; ΔS = 600 / 300 = +2.0 J K⁻¹ → **D** | D | Evet |
| 6 (a) | W = PΔV = 300 J; ΔU = 3⁄2 PΔV = 450 J; Q = 750 J | 750 J | Evet |
| 6 (b) | Q = 0; ΔU = 3⁄2 nR (300 − 750) = −450 J; W = +450 J | 450 J | Evet |
| 6 (c) | Net iş = 750 − 460 = 290 J; verim = 290 / 750 = 0.387 ≈ 0.39 | 0.39 | Evet |
| 6 (d) | Carnot sınırı (750 K ve 300 K arasında) = 1 − 300 / 750 = 0.60; 0.39 < 0.60 → ikinci yasayla tutarlı | Aynı | Evet |

### Soru 6 çevriminin adım adım denetimi (Clausius kuralı; nR = P_A V_A / T_A = 0.6667 J K⁻¹, n = 0.0802 mol)

| Adım | Q (gaza verilen) | W (gazın yaptığı) | ΔU | Not |
|---|---|---|---|---|
| A → B (izobarik genleşme) | +750 J | +300 J | +450 J | T_B = 300 × 5.0 / 2.0 = 750 K; verilen değerle tutarlı |
| B → C (adyabatik genleşme) | 0 | +450 J | −450 J | V_C = V_B (750 / 300)^(3/2) = 1.976 × 10⁻² m³; P_C = 1.01 × 10⁴ Pa (iki yoldan aynı) |
| C → A (izotermal sıkıştırma) | −458.1 J (soruda 460 J) | −458.1 J | 0 | nRT ln(V_A / V_C) = 200 × ln(0.1012) = −458.1 J |
| Toplam | +291.9 J (460 ile +290 J) | +291.9 J (460 ile +290 J) | 0 | Çevrim kapanıyor; verim 0.389 (460 ile 0.387) → 0.39 |

Soruda verilen 460 J, 458 J'ün iki anlamlı basamağa doğru yuvarlanmış halidir; tüm işaretler doğru. Carnot karşılaştırması
çevrimin en yüksek (750 K) ve en düşük (300 K) sıcaklıklarıyla yapılmış; doğru sıcaklıklar bunlar.

Çeldiriciler yeniden hesaplandı: S1 A −700, B −300, C +300; S2 A 8³ = 512, C 8, D 8^(2/3) = 4; S3 A ln 2, B ln 4, D 2⁴ = 16;
S4 B 0.333, C 0.40, D 0.75; S5 A −2.0, C 0.50. Hepsi tabloda yazan yanılgıdan çıkıyor.

Kural denetimi: tüm sorular HL etiketli (doğru); nicel sorular tek atomlu ideal gaz; işaret kuralı Clausius; izotermal işin
logaritmalı formülü öğrenciden istenmiyor (enerji değerleri veriliyor); türev/integral yok; mikrodurumlar dört parçacık, iki bölme;
Soru 6 puanları 3 + 2 + 2 + 2 = 9 ve markscheme madde sayıları eşleşiyor; seçenekler aynı türde ve sıralı. Soru 4'te entropi
kontrolü: −800 / 500 + 600 / 300 = +0.4 J K⁻¹ > 0 ve 0.25 < Carnot 0.40; veri ikinci yasayla tutarlı.

## Bulgular

**KRİTİK:** yok.

### ORTA

1. **Soru 3, seçenek D (k ln 16) savunulabilir bir ikinci okumaya açık.** Sayım doğru: son makrodurum (2 + 2) için Ω = 6,
   başlangıç için Ω = 1, anahtar k ln 6. Ancak aynı düzenek (parçacıklar önce sol yarıda, sonra kutunun tamamında) termodinamikte
   serbest genleşmedir ve gazın entropi değişimi Nk ln 2 = 4k ln 2 = k ln 16'dır; "sistemin entropisi" sözünü erişilebilir tüm
   mikrodurumlar üzerinden okuyan iyi bir öğrenci D'yi seçebilir. Soru "macrostate" sözcüğünü hiç kullanmıyor; yalnızca
   "Later, there are two particles in each half" diyor. Kesin bir hata değil (anahtar, verilen tanımla tek tutarlı cevap), ama
   ayrım metinde açık değil. *Öneri:* son iki cümle şöyle olsun: "The entropy of a macrostate is *S* = *k* ln Ω, where Ω is the
   number of microstates of that macrostate. What is the entropy of the macrostate with two particles in each half minus the
   entropy of the macrostate with all four particles in the left half?" Rehberin "basit sayma modeli" ile hangi okumayı kastettiği
   uzmanca teyit edilmeli (dosya da bunu doğrulanmamış olarak işaretliyor).

### DÜŞÜK

1. **Soru 5, tersinirlik varsayımı yazılı değil.** ΔS = ΔQ/T yalnızca tersinir (yavaş) süreçte gazın entropi değişimini verir;
   tersinmez bir izotermal genleşmede gaz 600 J iş yapsa da ΔS daha büyük olur. Müfredat düzeyinde beklenen cevap değişmiyor.
   *Öneri:* "expands slowly (reversibly) and isothermally".

2. **Soru 6 (c), verilen 460 J ile tam değer 458 J.** Verim 0.387 ↔ 0.389; ikisi de 0.39. Sorun yok; kayıt için.

3. **Soru 6 (d), beklenen ifade biçimi (şüphe).** Carnot sınırıyla karşılaştırmanın rehberin beklediği biçim olduğu dosyada da
   doğrulanmamış olarak işaretli; fizik olarak doğru. Kelvin biçimiyle verilen cevabın yalnızca ikinci puanı alması makul.

4. **Soru 6, şekil.** P–V diyagramı yalnızca sözle tarif edilmiş; tüm veriler metinde olduğu için soru şekilsiz çözülebiliyor
   (kör çözümde eksik bilgi çıkmadı).

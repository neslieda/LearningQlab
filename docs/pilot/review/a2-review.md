# Bağımsız inceleme: A.2 Kuvvet ve momentum

> Tarih: 2026-10-11. İncelenen dosya: [a2-forces-momentum-pilot-questions.md](../a2-forces-momentum-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; g = 9.8 m s⁻²), sonra anahtar ve
> markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (A.2 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | En büyük statik sürtünme 0.50 × 12 × 9.8 = 58.8 N > 40 N; sandık durur, sürtünme = 40 N → **A** | A | Evet |
| 2 (1A) | Δp = 0.16 × (15 + 10) = 4.0 kg m s⁻¹; F = 4.0 / 0.020 = 200 N → **D** | D | Evet |
| 3 (1A) | N + mg = mv²/r; N = 1.28 − 0.49 = 0.79 N → **B** | B | Evet |
| 4 (1A) | Momentum büyüklükleri eşit; E_k = p²/2m; oran = 3 → **C** | C | Evet |
| 5 (a) | V = 3.351 × 10⁻⁸ m³; W = 2.56 × 10⁻³ N (≈ 2.6 × 10⁻³ N) | 2.56 × 10⁻³ N | Evet |
| 5 (b) | F_b = 1260 × V × 9.8 = 4.14 × 10⁻⁴ N | 4.1 × 10⁻⁴ N | Evet |
| 5 (c) | F_d = 2.148 × 10⁻³ N; v = 0.0407 m s⁻¹ (verilen 2.6 × 10⁻³ N ile 0.0414) → 0.041 m s⁻¹ | 0.041 m s⁻¹ (aralık 0.041–0.042) | Evet |
| 5 (d) | Ağırlık ve kaldırma kuvveti değişmez → terminal hızda sürükleme aynı; η azalınca aynı sürükleme için daha büyük hız → terminal hız artar | Aynı iki madde | Evet |

Çeldiriciler de yeniden hesaplandı: S1 B 47.0 N, C 58.8 N, D 117.6 N; S2 A 40 N, B 80 N, C 120 N; S3 A 0.49 N, C 1.28 N, D 1.77 N;
S4 A 1/3, D 9. Hepsi tabloda yazan yanılgıdan çıkıyor. S5 (c) notundaki "kaldırma kuvveti atlanırsa 0.049" değeri 0.0485 olarak
doğrulandı.

## Bulgular

**KRİTİK:** yok. **ORTA:** yok.

### DÜŞÜK

1. **Soru 5, puan toplamı ve "Biçim uyumu" tablosu.** Soru SL etiketli ve 9 puan. Biçim profili (§4) SL örnek kâğıdında kısa
   soruların 4–6 puan olduğunu söylüyor; 4–9 aralığı HL gözlemi. A.3 dosyası aynı durumu "uzman teyidi gerekir" diye not etmiş, A.2
   dosyası ise kayıtsız "uygun" diyor. Yazım standardı 4–9'a izin verdiği için hata değil, tutarsız beyan.
   *Öneri:* A.2 biçim tablosuna A.3'teki notun aynısı eklensin (ya da soru SL için 6 puana indirilsin, ör. (b) ile (c) birleştirilerek).

2. **Soru 5 (c), markscheme notu.** "use of 2.6 × 10⁻³ N gives 0.0415" değeri yalnızca kaldırma kuvveti 4.1 × 10⁻⁴ N'a
   yuvarlanırsa çıkar; yuvarlanmamış 4.14 × 10⁻⁴ N ile sonuç 0.0414'tür. Kabul aralığı (0.041–0.042) her iki durumu da kapsıyor,
   puanlamayı etkilemez. *Öneri:* "gives 0.041" yazılsın.

3. **Soru 1, D seçeneği.** Yanılgı 117.6 N verir; seçenek 120 N'a yuvarlanmış (dosya bunu not ediyor). Diğer seçenekler 2 anlamlı
   basamakta olduğu için tutarlı; yalnızca bilgi notu, değişiklik gerekmez.

### Şüphe (doğrulanmış hata değil)

- **Soru 5, veri kitapçığı.** Küre hacmi ve Stokes yasası (F_d = 6πηrv) öğrenciye verilmiyor; veri kitapçığında bulundukları
  varsayılıyor. Yazar da bunu "doğrulanmayan" olarak işaretlemiş; uzman teyidi gerekir.
- **Soru 4.** A.2 düğümünde ("patlama ve enerji") ama kinetik enerji bağıntısı A.3'ün kazanımı. Müfredat satırı patlamada enerjiyi
  A.2'ye koyduğu için kapsam içinde sayıyorum.

## Hata bulunmayan denetimler

- Tek doğru seçenek: dört 1A sorusunda da yalnızca bir seçenek savunulabilir.
- Müfredat sınırı: çarpışma/patlama 1 boyutlu, eşzamanlı denklem yok; düşey çemberde yalnızca en üst nokta; eğimli viraj yok;
  türev/integral yok. Düzey etiketi SL doğru.
- Seçenekler aynı birimde ve artan sırada; doğru cevap konumları A, D, B, C.
- Soru 5: alt parça puanları 2, 2, 3, 2; markscheme ✓ sayıları 2, 2, 3, 2; toplam 9. "Show that" değeri (2.6 × 10⁻³ N) hem tam hem
  yuvarlak değerle (c)'de aynı 2 anlamlı basamaklı sonucu veriyor.
- Yön ve işaret: S2'de momentum değişimi yön değiştirme ile toplanıyor; S3'te en üst noktada N ve mg ikisi de merkeze doğru; S5'te
  ağırlık aşağı, kaldırma ve sürükleme yukarı. Hepsi doğru.
- Gerçekçilik: çelik ve gliserin yoğunlukları ile gliserin viskozitesi genel bilgiyle tutarlı; Reynolds sayısı ≈ 0.15, Stokes
  bölgesinde. Disk kütlesi, oyuncak araba ve sandık verileri makul. S3'te v² = 10.2 > gr = 3.9, temas korunuyor.
- Şekil gerektiren soru yok; eksik bilgi yok.

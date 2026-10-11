# Bağımsız inceleme: C.4 Duran dalgalar ve rezonans

> Tarih: 2026-10-11. İncelenen dosya: [c4-standing-waves-resonance-pilot-questions.md](../c4-standing-waves-resonance-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtar ve markscheme ile
> karşılaştırma, sonra yazım standardı, müfredat analizi (C.4 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | f₁ = 120 / (2 × 0.75) = 80 Hz; üçüncü harmonik 240 Hz → **C** | C | Evet |
| 2 (1A) | Bir ucu kapalı boru: yalnızca tek katlar; f₁ = 340/(4 × 0.17) = 500 Hz ✓; sonraki 3 × 500 = 1500 Hz → **B** | B | Evet |
| 3 (1A) | X ve Y aynı düğümün iki yanındaki komşu ilmeklerde → zıt faz, π rad → **D** | D | Evet |
| 4 (1A) | Sönüm artınca en büyük genlik azalır; tepe doğal frekansın biraz altına kayar → **A** | A | Evet |
| 5 (a) | Dalga tel boyunca ilerler, sabit uçta yansır; gelen ve yansıyan dalgalar üst üste biner | Aynı | Evet |
| 5 (b) | λ = 2 × 0.65 = 1.30 m; f = 260/1.30 = 200 Hz | 200 Hz | Evet |
| 5 (c)(i) | 600/200 = 3. harmonik → 3 karın | 3 | Evet |
| 5 (c)(ii) | 0.65/3 = 0.217 ≈ 0.22 m | 0.22 m | Evet |
| 5 (d) | Zorlayıcı frekans telin doğal (birinci harmonik, 200 Hz) frekansına eşit olur → rezonans, enerji aktarımı en büyük | Aynı | Evet |
| 5 (e) | En büyük genlik azalır | Aynı | Evet |

Çeldiriciler yeniden hesaplandı: S1 80; 160; 480 Hz. S2 1000; 2500; 3 × 340/(2 × 0.17) = 3000 Hz. S3 2π × 0.10/0.80 = π/4;
2π × 0.20/0.80 = π/2. Hepsi yazılan yanılgıdan çıkıyor; her soruda tek doğru seçenek var.

Özel olarak istenen denetimler:

- **Arama:** dosyada "fundamental" ve "overtone" sözcükleri **geçmiyor** (büyük–küçük harf duyarsız arama, 0 eşleşme). "end correction"
  ve "pressure" de geçmiyor. Türkçe "uç düzeltmesi" ve "basınç düğümü" yalnızca yazarın "bunlar kullanılmadı" diyen iki denetim
  satırında (satır 30–31 ve 198) geçiyor; hiçbir soru metninde ya da markscheme'de yok.
- **Bir ucu kapalı boru (Soru 2):** f₁ = v/4L = 500 Hz verilerle tutarlı. Yalnızca tek sayılı katlar oluşur; "next higher frequency"
  1500 Hz doğru. Soru harmonik numarası kullanmadan sorulmuş, böylece "ikinci mi üçüncü mü harmonik" adlandırma tartışması soruya
  girmiyor. Kökteki "first harmonic" müfredat diliyle uyumlu. 2500 Hz'de de duran dalga oluşur ama "next" sözcüğü tek cevabı sabitliyor.
- **Sönüm ve en büyük genliğin frekansı (Soru 4):** hıza orantılı sönümde yer değiştirme genliğinin tepesi doğal frekansın altındadır
  ve sönüm arttıkça daha da düşer; anahtar (A) doğru. Soru yalnızca yön soruyor ("slightly lower / higher"), hesap istemiyor; müfredat
  satırındaki "sönümün genliğe ve rezonans frekansına etkisi" kazanımı ve "nitel" sınırı içinde kalıyor. Soru 5 (e) de nitel.
- İkiden fazla dalganın üst üste binmesi yok; yalnızca yer değiştirme düğümleri kullanılmış.

Kural denetimi: tüm sorular SL (C.4 yalnızca SL) — etiket doğru. Türev/integral yok. Sayısal seçenekler aynı birimde ve artan sırada.
Soru 5 puanları 2+2+1+1+2+1 = 9; markscheme ✓ sayıları parça puanlarıyla eşleşiyor. Veriler gerçekçi (çelik telde 260 m s⁻¹,
0.65 m tel; 0.17 m boru).

## Bulgular

KRİTİK ve ORTA bulgu yok. Doğrulanmış hata yok.

### 1. DÜŞÜK — Soru 5 (b): "Show that … about 200 Hz" hedefi tam değere eşit

- **Yer:** Soru 5 (b).
- **Açıklama:** Hesap tam 200 Hz veriyor (260/1.30). "Show that" kalıbında hedef genellikle yuvarlanmış bir değerdir ve öğrenci daha
  fazla basamak göstererek kanıtlar; burada gösterilecek fazladan basamak yok, "about" sözcüğü boşta kalıyor.
- **Öneri:** Ya "about" sözcüğünü kaldır ("Show that the frequency of the first harmonic of the wire is 200 Hz"), ya da hızı
  255 m s⁻¹ yap: f₁ = 255/1.30 = 196 Hz ("about 200 Hz"). İkinci seçenekte 600 Hz üçüncü harmoniğe tam denk gelmez (588 Hz), bu yüzden
  birinci seçenek daha az değişiklik gerektirir.

### 2. DÜŞÜK — Soru 5: SL etiketli kısa soru 9 puan

- **Yer:** Soru 5 başlığı; yazar "Biçim uyumu" tablosunda zaten not etmiş.
- **Açıklama:** Biçim profilinde SL kısa soruları 4–6 puan.
- **Öneri:** SL sürümü için iki soruya böl: (a)(b)(c) = 6 puan (duran dalga) ve (d)(e) + ek bir parça (rezonans/sönüm).

### 3. DÜŞÜK — Soru 3: SL sorusunda faz farkı radyanla soruluyor

- **Yer:** Soru 3 seçenekleri (0, π/4 rad, π/2 rad, π rad).
- **Açıklama:** Duran dalgada faz C.4'ün SL kazanımı; ancak müfredat analizinde radyan cinsinden faz açısı C.1'in HL ek içeriğinde
  anılıyor. SL öğrencisi "in phase / antiphase" dilini bilir; π rad ifadesini de büyük olasılıkla tanır, ama bu teyit edilmedi.
- **Öneri:** Uzman teyit edene kadar değişiklik gerekmez; istenirse seçenekler "0", "90°", "180°" biçiminde ya da "in phase / antiphase"
  içeren sözel biçimde yazılabilir. Bu bir şüphedir, doğrulanmış hata değildir.

### Şüphe (hata değil)

- Soru 4'te sönümün tepe frekansını düşürmesi fizik olarak doğru; rehberin bu ayrıntıyı SL'de ne ölçüde beklediği yazarın da
  belirttiği gibi teyit edilmedi. Müfredat analizindeki kazanım satırı ("rezonans frekansına etkisi") soruyu destekliyor.
- Soru 5 (d): titreştirici bir desteğe yakın; tel için o uç yaklaşık düğüm sayılıyor. Kökte "fixed supports" yazdığı için öğrenci
  açısından belirsizlik yok.

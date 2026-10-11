# Bağımsız inceleme: D.4 İndüksiyon

> Tarih: 2026-10-11. İncelenen dosya: [d4-induction-pilot-questions.md](../d4-induction-pilot-questions.md).
> Yöntem: önce cevapsız öğrenci kopyası üzerinden kör çözüm (python3), sonra anahtar ile karşılaştırma, sonra kural kontrolü.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | ε = NBvL = 20 × 0.30 × 0.50 × 0.10 = 0.30 V → C | C | Evet |
| 2 | Akım saat yönünde, kuvvet sola (aşağıda türetildi) → A | A | Evet |
| 3 | Düzlem alana paralel: akı bağlantısı sıfır, emk en büyük → B | B | Evet |
| 4 | ε₀ ∝ f → 12 V; T → 20 ms → D | D | Evet |
| 5(a) | ε = BvL = 0.12 V | 0.12 V | Evet |
| 5(b) | I = 2.4 A; F = BIL = 0.192 ≈ 0.19 N | 0.19 N | Evet |
| 5(c) | Fv = 0.288 W; I²R = εI = 0.288 W | 0.29 W = 0.29 W | Evet |
| 5(d) | Akı sabit → emk sıfır; ya da ön ve arka kenar emk'leri eşit ve çevrimde zıt | Aynı | Evet |

Çeldiriciler yeniden hesaplandı (Soru 1: 0.015, 0.12, 0.60) ve eşleşti.

## Yön kontrolleri

Eksenler: x sağa, y sayfanın üstüne, z sayfadan dışarı.

- **Soru 2 (iki bağımsız yol).** B = −ẑ, alan bölgesi solda, çerçeve +x̂ yönünde çekiliyor.
  (i) Lenz: içeri doğru akı azalıyor → indüklenen akım çerçeve içinde içeri doğru (−ẑ) alan üretmeli → sayfaya bakana göre saat yönünde.
  (ii) Yük üzerindeki kuvvet: alan içindeki sol kenarda artı yüke v × B = x̂ × (−ẑ) = +ŷ → sol kenarda akım yukarı → üst kenarda sağa →
  saat yönünde. İki yol aynı sonucu veriyor.
  Kuvvet: sol kenar I = +ŷ: ŷ × (−ẑ) = −x̂, sola. Üst kenarın alan içindeki parçası (I = +x̂): x̂ × (−ẑ) = +ŷ; alt kenarınki
  (I = −x̂): −ŷ; birbirini götürür. Sağ kenar alanın dışında. Bileşke sola, harekete karşı. Anahtar (A) doğru.
  Geometri: İngilizce kök "directed into the page" ve "pulled to the right, out of the field region" diyor; bu, akının azaldığını ve
  hareket yönünü belirlemeye yeter. Şekil tarifi (alan solda, sol kenar içeride) bununla tutarlı; tek anlamlı.
- **Soru 5 yön notu.** Girerken içeri akı artıyor → indüklenen alan dışarı → yukarıdan bakana göre saat yönünün tersine; öndeki (sağ)
  kenarda akım +ŷ; ŷ × (−ẑ) = −x̂: manyetik kuvvet sola. Yük yoluyla kontrol: ön kenarda v × B = +ŷ → aynı. Not doğru. Kök
  "vertically downwards", şekil "yukarıdan görünüş, ⊗" — birbirini tutuyor.
- **Soru 1.** Yön istenmiyor; alan yönü (⊗ ya da ⊙) cevabı etkilemiyor.

## Bulgular

KRİTİK: yok. ORTA: yok.

1. **DÜŞÜK — Soru 5(c), markscheme MP1: "Fv = 0.19 × 1.5 = 0.29 W".** 0.19 × 1.5 = 0.285 (yuvarlama sınırında); 0.29 sonucu
   yuvarlanmamış F = 0.192 N'dan gelir (0.288 W). Yuvarlanmış 0.19 N kullanan öğrenci 0.285 W ile 0.288 W'ı karşılaştırır ve "eşit"
   demekte tereddüt edebilir. *Öneri:* satırı "*Fv* = 0.192 × 1.5 = 0.29 «W»" yapmak ve nota "Allow 0.28–0.29 W from rounded F" eklemek;
   cebirsel yol (Fv = BILv = εI) zaten kabul ediliyor.
2. **DÜŞÜK — Soru 5(c), "Show that" biçimi.** Verilen yaklaşık bir sayı yok; iki niceliğin eşitliği isteniyor (yazar da not etmiş).
   Sonraki parça bu değere bağlı olmadığından zincirleme risk yok. Uzman tercihine bağlı.
3. **DÜŞÜK — Soru 3, kök.** "The axis of rotation is at right angles to the field" dönme ekseninin bobin düzleminde olduğunu söylemiyor
   (şekil de yok). Olağan okuma açık, cevap değişmez. *Öneri:* "about an axis in the plane of the coil that is at right angles to the field".
4. **DÜŞÜK — Soru 2–4 seçenek biçimi.** Dört sorudan üçü cümle / çift biçiminde (yazar da not etmiş); tablo biçimi uzmanca
   onaylanırsa dönüştürülebilir. Soru 4'te C ve D aynı emk değerini taşıdığından "artan sıra" ikinci büyüklükle (40 ms, 20 ms)
   azalan; önemsiz.

## Kontrol edilenler (sorun bulunmadı)

- Müfredat sınırı: nicel işlem yalnızca alana giren dikdörtgen bobin / çerçeve (Soru 1, 5); dönen bobin soruları yalnızca nitel ilişki
  ve oran (Soru 3, 4); öz indüksiyon, indüktans, RL yok; türev / integral yok.
- Düzey: tüm sorular HL (D.4 yalnızca HL) — doğru.
- Puanlar: 5(a) 2, (b) 3, (c) 2, (d) 2 = 9; ✓ sayıları parça puanlarına eşit; alt parça ≤ 3.
- Her çoktan seçmelide tek doğru seçenek; Soru 1'de seçenekler aynı birimde ve artan.
- Gerçekçilik: 0.050 Ω, yaklaşık 1 m çevreli alüminyum çerçeve için ≈ 0.5 mm² kesit demektir (makul); 2.4 A ve 0.19 N makul.
  0.40 T'lik geniş düzgün alan güçlü ama kurgusal bir düzenek için kabul edilebilir (yazar da not etmiş).

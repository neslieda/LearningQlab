# Bağımsız inceleme: D.3 Elektromanyetik alanlarda hareket

> Tarih: 2026-10-11. İncelenen dosya: [d3-motion-in-em-fields-pilot-questions.md](../d3-motion-in-em-fields-pilot-questions.md).
> Yöntem: önce cevapsız öğrenci kopyası üzerinden kör çözüm (python3; e = 1.60 × 10⁻¹⁹ C, m_e = 9.11 × 10⁻³¹ kg, g = 9.8), sonra
> anahtar ile karşılaştırma, sonra kural kontrolü. Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | T = 2πm/(qB), hızdan bağımsız → B | B | Evet |
| 2 | E = 600/0.020 = 3.0 × 10⁴; v = E/B = 2.0 × 10⁷ m s⁻¹ → D | D | Evet |
| 3 | I = +x, B = −z; (+x) × (−z) = +y: sayfanın üstüne → A | A | Evet |
| 4 | Sabit kuvvet → parabol; kuvvetin hız doğrultusunda bileşeni oluşur → sürat artar → C | C | Evet |
| 5(a) | E = 1.8 × 10⁴ V m⁻¹; v = E/B = 2.25 × 10⁷ m s⁻¹ | 2.25 × 10⁷ | Evet |
| 5(b) | Sayfanın içine (aşağıda türetildi) | into the page | Evet |
| 5(c) | Kuvvet her an hıza dik, iş yapmaz, sürat sabit; sabit büyüklükte merkezcil kuvvet | Aynı | Evet |
| 5(d) | e/m = v/(Br) = 1.76 × 10¹¹ C kg⁻¹ (2.3 × 10⁷ ile 1.80 × 10¹¹) | 1.8 × 10¹¹ (aralık 1.7–1.8) | Evet |
| 5(e) | Sapmaz: v = E/B yük ve kütleden bağımsız; iki kuvvet de yön değiştirir | Aynı | Evet |
| 6(a) | Tele kuvvet etkir; Newton 3 ile mıknatıslara eşit-zıt kuvvet; terazi okuması değişir | Aynı | Evet |
| 6(b) | 0.04/0.41 = %9.8 ≈ %10 | %10 (9.8 kabul) | Evet |
| 6(c) | B = 0.41 × 10⁻³ × 9.8/0.050 = 0.0804 T; kesirli 0.0488 + 0.0200 = 0.0688; ΔB = 0.0055 → (0.080 ± 0.006) T | (0.080 ± 0.006) T | Evet |
| 6(d) | 0.0748–0.0859 T; 0.085 T aralıkta → tutarlı, ama sınıra çok yakın | tutarlı (0.074–0.086) | Evet (bkz. bulgu 2) |
| 6(e) | Beklenen "ders kitabı" cevabı: F = BIL sin θ küçülür → B küçük bulunur. **Ancak** anlatılan düzenekte etki olmamalı (bkz. bulgu 1) | B küçük bulunur | **Hayır / tartışmalı** |
| 6(f) | Daha büyük akım / daha uzun mıknatıs / daha duyarlı terazi / L'yi daha hassas ölçmek | Aynı liste | Evet |

Çeldiriciler yeniden hesaplandı (Soru 2: 5.0 × 10⁻⁸, 2.0 × 10⁵, 4.0 × 10⁵) ve eşleşti. Soru 6 verisi: en küçük kareler eğimi 0.409,
ilk/son nokta çubuk uçlarından en büyük / en küçük eğim 0.430 / 0.390 g A⁻¹ — verilen değerlerle uyumlu.

## Yön kontrolleri

Eksenler: x sağa, y sayfanın üstüne, z sayfadan dışarı.

- **Soru 3.** F = IL × B, I = +x̂, B = −ẑ: x̂ × (−ẑ) = −(x̂ × ẑ) = −(−ŷ) = +ŷ. Üste. Anahtar doğru; kök tek başına geometriyi belirliyor.
- **Soru 5(b).** E = −ŷ (üst levha artı). Elektron (q = −e): elektrik kuvveti +ŷ. Gerekli manyetik kuvvet −ŷ: (−e)(x̂ × B) = −ŷ →
  x̂ × B = +ŷ → B = −ẑ (x̂ × (−ẑ) = +ŷ). Sayfanın içine. Artı yük için de aynı sonuç çıkar (hız seçici yükün işaretinden bağımsız),
  bu da 5(e) ile tutarlı. Kök "left to right" ve "upper plate is positive" dediği için geometri şekilsiz de tek anlamlı.

## Bulgular

### KRİTİK

1. **KRİTİK — Soru 6(e), markscheme: "force / Δm / gradient is smaller … calculated B is smaller than the true value".**
   Anlatılan düzenekte bu sonuç fiziksel olarak doğru değil. Tel düz ve alan bölgesini (uzunluğu L olan mıknatısların arası) baştan
   sona geçiyor. Tel alana dik değil de dikle φ açısı yapıyorsa, alan içinde kalan tel uzunluğu L değil L/cos φ olur; kuvvet
   F = BI(L/cos φ) sin θ, θ = 90° − φ olduğundan F = BI(L/cos φ) cos φ = **BIL**. Genel olarak F = I(ℓ × B) yalnızca telin alana dik
   izdüşümüne bağlıdır ve bu izdüşüm, tel bölgeyi uçtan uca geçtiği sürece L'dir. Yani terazi okuması ve eğim değişmez, B düşük
   çıkmaz. Anahtarın sonucu ancak "alan içindeki tel uzunluğu yine L kalır" varsayımıyla geçerlidir; bu varsayım düzenekle çelişir
   ve soruda yazmıyor. Sonuç: fiziği doğru düşünen öğrenci ("etki yok, çünkü alan içindeki uzunluk 1/sin θ ile artar") sıfır alır.
   *Güven:* türetme kesin; ancak sınav geleneğinde beklenen cevap anahtardaki cevaptır, bu yüzden uzman kararı gerekir.
   *Öneri (birini seçin):* (i) parçayı başka bir sistematik etkiyle değiştirmek, ör. "The magnetic field extends beyond the ends of
   the magnets. Explain the effect of this on the value of *B* obtained." → kuvvet BIL'den büyük, eğim büyük, L = 5.0 cm ile
   hesaplanan B gerçek değerden **büyük** çıkar; (ii) düzeneği, alan içindeki uzunluğu sabit olan bir iletkene çevirmek (ör. alanın
   tamamen içinde kalan L uzunluğunda kısa bir iletken çubuk) ve sonra aynı soruyu sormak; (iii) en azından markscheme'e
   "no effect, as the length of wire in the field increases by the factor 1/sin θ" cevabını tam puanlı alternatif olarak eklemek.

### ORTA

2. **ORTA — Soru 6(d) ile 6(c) notundaki "Allow ± 0.005 T" birlikte.** Sonuçlar (yeniden hesaplandı):

   | Öğrencinin (c) sonucu | Aralık / T | 0.085 T | Sonuç |
   |---|---|---|---|
   | 0.080 ± 0.006 (anahtar) | 0.074–0.086 | içinde | tutarlı |
   | 0.0804 ± 0.0055 (yuvarlamadan) | 0.0748–0.0859 | içinde (0.0009 farkla) | tutarlı |
   | 0.080 ± 0.005 (anahtarın izin verdiği) | 0.075–0.085 | **tam sınırda** | belirsiz |
   | uç eğimler ve uç L ile (0.43/4.9 cm, 0.39/5.1 cm) | 0.0749–0.0860 | içinde | tutarlı |
   | yalnızca eğim belirsizliği (L unutulur, MP2 kaybı) ± 0.004 | 0.076–0.084 | dışında | tutarsız (ECF) |

   Yani anahtarın kabul ettiği ± 0.005 T ile (d)'nin cevabı sınırda kalıyor ve "Allow ECF" hangi sonucun puan alacağını söylemiyor.
   Yazarın işaretlediği sınır durumu gerçek. *Öneri:* üretici değerini aralığın açıkça içine çekmek (ör. **0.083 T**: yukarıdaki ilk dört
   satırın hepsinde tutarlı) **ya da** açıkça dışına çıkarmak (ör. 0.090 T: hepsinde tutarsız); ayrıca (d) notuna "conclusion must
   follow from the candidate's own range" yazmak. "Allow ± 0.005 T" notu kaldırılabilir (0.0055 tek basamağa 0.006 olarak yuvarlanır).

### DÜŞÜK

3. **DÜŞÜK — Soru 5(a), "about 2.3 × 10⁷ m s⁻¹".** Tam değer 2.25 × 10⁷; iki basamağa yuvarlamada tam sınırda (2.2 / 2.3). Sonraki
   parça iki değerle de kabul aralığında (1.76 ve 1.80 × 10¹¹ C kg⁻¹), işlevsel sorun yok. *Öneri:* levha aralığını ya da gerilimi
   sınırdan uzaklaşacak biçimde değiştirmek (ör. V = 460 V → 2.30 × 10⁷; r ve e/m yeniden hesaplanmalı) ya da bırakmak.
4. **DÜŞÜK — Soru 5(e), MP1'in ikinci alternatifi.** "both forces have the same magnitude as before" tek başına dengeyi göstermez
   (yönler de gerekir); MP2 bunu tamamlıyor ama MP1 alternatifi yön değişimini hiç anmadan puan veriyor. *Öneri:* alternatifi
   "both forces have the same magnitude as before **and** are still in opposite directions" yapmak.
5. **DÜŞÜK — Soru 5 toplam 9 puan, SL etiketli.** Biçim profilinde SL kısa sorular 4–6 puan (yazar da not etmiş). İçerik SL sınırında;
   yalnızca kâğıt biçimi konusu.
6. **DÜŞÜK — Soru 6(d) komut sözcüğü "Comment".** Profildeki 1B listesinde yok (yazar da not etmiş); uzman teyidi.

## Kontrol edilenler (sorun bulunmadı)

- Düzey: tüm sorular SL; W = qΔV ile hızlandırma (ek HL) kullanılmamış; hız dik alanlar koşulundan bulunuyor.
- Puanlar: Soru 5: 2 + 1 + 2 + 2 + 2 = 9; Soru 6: 2 + 1 + 3 + 1 + 2 + 1 = 10; ✓ sayıları parça puanlarına eşit; alt parça ≤ 3.
- Soru 1: yanılgı çeldiricileri (T/2, 2T, 4T) belirtilen hatalardan çıkıyor. Soru 4: tek doğru seçenek (parabol + sürat artar).
- Soru 5 iç tutarlılık: gerçek e/m ile r = m_e v/(eB) = 0.160 m. v ≈ 0.075c; göreli düzeltme %0.3 dolayında, önemsiz.
- Soru 6: birim dönüşümü (g → kg), yüzde belirsizlik, kesirli belirsizliklerin toplanması doğru; veri B ≈ 0.080 T, I ≤ 5 A,
  kuvvet ≈ 0.02 N için gerçekçi.
- Türev / integral yok; "nitel" sınırı olan içerik yok.

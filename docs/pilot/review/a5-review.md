# Bağımsız inceleme: A.5 Galileo ve özel görelilik

> Tarih: 2026-10-11. İncelenen dosya: [a5-relativity-pilot-questions.md](../a5-relativity-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; c = 3.00 × 10⁸ m s⁻¹), sonra anahtar
> ve markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (A.5 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | Şamandıra çerçevesinde 5.0 s; γ = 1.25; sonda saati öz zaman: 4.0 s → **B** | B | Evet |
| 2 (1A) | u = (0.60 + 0.70)c / (1 + 0.42) = 0.915c → **C** | C | Evet |
| 3 (1A) | (cΔt′)² = 5.0² − 3.0² = 16 m²; cΔt′ = 4.0 m → **D** | D | Evet |
| 4 (1A) | tan θ = 0.50; θ = 26.6° → **A** | A | Evet |
| 5 (a) | Cismin durgun olduğu referans çerçevesinde ölçülen uzunluk | Aynı | Evet |
| 5 (b) | γ = 1/√(1 − 0.64) = 1.667 | 1.67 | Evet |
| 5 (c) | Δt = 480 / (0.80 × 3.00 × 10⁸) = 2.0 × 10⁻⁶ s | 2.0 × 10⁻⁶ s | Evet |
| 5 (d) | Öz zaman: 2.0 × 10⁻⁶ / 1.667 = 1.2 × 10⁻⁶ s (γ = 1.7 ile 1.18 × 10⁻⁶) | 1.2 × 10⁻⁶ s | Evet |
| 5 (e) | Ön lamba önce; aralık γvL₀/c² = 2.13 × 10⁻⁶ s (γ = 1.7 ile 2.18 × 10⁻⁶) | Ön lamba önce; 2.1 × 10⁻⁶ s (aralık 2.1–2.2) | Evet |

### Soru 5 (e) için bağımsız türetim (özellikle istenen denetim)

Platform çerçevesi S: arka uç x = 0, ön uç x = +480 m. Mekik arkadan öne geçtiği için S′ (mekik) S'ye göre +x yönünde v = +0.80c
ile hareket eder. Dönüşüm: t′ = γ(t − vx/c²). İki flaş S'de t = 0 anında:

- arka lamba (x = 0): t′ = 0
- ön lamba (x = 480 m): t′ = −(5/3) × 0.80 × 480 / (3.00 × 10⁸) = −2.13 × 10⁻⁶ s

Ön lambanın t′ değeri daha küçük, yani mekik çerçevesinde **ön lamba 2.1 × 10⁻⁶ s önce** yanar. İkinci bir yoldan sağlama: mekik
çerçevesinde platform −x yönünde hareket eder; hareket yönünde önde giden uç arka uçtur ve "hareket yönünde öndeki saat geri kalır"
kuralına göre arka lamba geç yanar. İki yol aynı sonucu veriyor; anahtarın işareti ve yönü doğru.

Çeldiriciler yeniden hesaplandı: S1 A 3.0 s, C 5.0 s, D 6.25 s; S2 A 1.3c, D 0.172c; S3 A 8.0 m, B 5.83 m, C 5.0 m; S4 B 30.0°,
D 63.4°. Hepsi tabloda yazan yanılgıdan çıkıyor. S5 (d) notundaki 3.3 × 10⁻⁶ s (γ ile çarpma) ve uzay-zaman aralığı denetimi
(600² − 480² = 360² = 1.296 × 10⁵ m²) doğrulandı.

## Bulgular

**KRİTİK:** yok. **ORTA:** yok.

### DÜŞÜK

1. **Soru 5, "rear end" / "front end" adlandırması.** Durgun bir platformun kendiliğinden bir "ön"ü yoktur; hangi ucun ön olduğu
   yalnızca mekiğin geçiş sırasından (önce rear, sonra front) çıkarılıyor. (e)'nin cevabı tamamen bu adlandırmaya bağlı olduğu için
   dikkatsiz okuyan öğrenci yönü karıştırabilir. Soru çözülebilir; bulgu ifadeyle ilgili. *Öneri:* uçlar "end P" ve "end Q" diye
   adlandırılsın ("The shuttle passes end P (event 1) and later passes end Q (event 2)") ve öğrenci sürümüne şekil eklensin;
   (e) "which lamp (at P or at Q) flashes first" olsun.

2. **Soru 5 (e), markscheme notu "The third mark is independent".** Yön iki seçenekli; gerekçesiz "front" yazan öğrenci yarı
   olasılıkla 1 puan alır. Komut sözcüğü "Determine" olduğu için bu puanın bir gerekçeye ya da işaret tartışmasına bağlanması daha
   tutarlı olur (A.2 ve A.4 setlerindeki "sebepsiz ifadeye puan yok" notlarıyla da uyumlu). *Öneri:* "Award the third mark only if
   supported by the sign of Δ*t*′ or a simultaneity argument."

3. **Soru 2, seçenekler.** A (1.3c) ve B (c) fiziksel olarak hemen elenebilen değerler; ayırt edici tek çeldirici D. Yanılgılar
   gerçek (Galileo toplaması, "c'ye yuvarlama") olduğu için kural ihlali değil, yalnızca sorunun ayırt ediciliği düşük.
   *Öneri:* B yerine c'nin altında bir hata değeri, ör. yalnızca paydaki toplamın γ'ya bölünmesi gibi tanımlı bir yanılgı
   kullanılabilir; şart değil.

### Şüphe (doğrulanmış hata değil)

- **Terminoloji ve veri kitapçığı.** "Lorentz factor" teriminin ve Δt′ = γ(Δt − vΔx/c²) yazımının rehberdeki karşılığı yazar
  tarafından teyit edilmemiş; ben de kaynak açmadan teyit edemem. Uzman teyidi gerekir.
- **Soru 3, uzay-zaman aralığı işaret kuralı.** (cΔt)² − Δx² kullanılmış; rehber ters işaretle tanımlıyorsa bile bu sorunun cevabı
  değişmez (Δx′ = 0).

## Hata bulunmayan denetimler

- Tek doğru seçenek: dört 1A sorusunda da yalnızca bir seçenek savunulabilir. S3'te aralık zamansı (5.0 > 3.0), dolayısıyla
  olayların aynı konumda olduğu S′ çerçevesi vardır (v = 0.60c).
- Müfredat sınırı: türetim istenmiyor; zaman ekseni ct; dünya çizgisi sabit hızlı; yalnızca eylemsiz çerçeveler; S4'te açı ct
  ekseninden, tan θ = v/c. Düzey etiketi HL doğru.
- Seçenekler aynı birimde ve sıralı (S1, S4 artan; S2, S3 azalan); doğru cevap konumları B, C, D, A.
- Soru 5: alt parça puanları 1, 1, 2, 2, 3; markscheme ✓ sayıları 1, 1, 2 (her alternatifte 2), 2, 3; toplam 9. "Show that" değeri
  (γ ≈ 1.7) ile tam değer (1.667) (d)'de aynı 2 anlamlı basamaklı sonucu (1.2 × 10⁻⁶ s) veriyor; (e)'de 2.1 ve 2.2 çıkıyor ve
  kabul aralığı ikisini de kapsıyor.
- Hangi çerçevenin öz zamanı/öz uzunluğu ölçtüğü: S1 ve S5 (d)'de iki olay da sondanın/mekiğin bulunduğu yerde, öz zaman orada;
  S5'te öz uzunluk platform çerçevesinde. Doğru.
- Şekil gerektiren soru yok; S4 diyagramı sözle yeterince tanımlıyor (eksenler, eşit ölçek).

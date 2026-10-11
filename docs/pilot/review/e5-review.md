# Bağımsız inceleme: E.5 Füzyon ve yıldızlar

> Tarih: 2026-10-11. İncelenen dosya: [e5-fusion-stars-pilot-questions.md](../e5-fusion-stars-pilot-questions.md).
> Yöntem: önce cevapları çıkarılmış öğrenci görünümü üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtarla karşılaştırma,
> sonra yazım standardı, müfredat analizi (E.5 satırı) ve biçim profiline göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.
> Kullanılan sabitler: σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴, L☉ = 3.83 × 10²⁶ W, 1 pc = 3.26 ly, 1 ly = 9.46 × 10¹⁵ m.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | D (25 pc = 81.5 ly) | D | Evet |
| 2 | C (R² ∝ L/T⁴ = 64 → 8) | C | Evet |
| 3 | A (beyaz cüce); başka savunulabilir seçenek yok | A | Evet |
| 4 | B | B | Evet |
| 5 | A; ancak C'yi seçen öğrencinin gerekçesini müfredat çekirdeğiyle çürütmek zor (bkz. bulgu 1) | A | Evet (çekinceyle) |
| 6 (a) | d = 8.0 pc = 2.467 × 10¹⁷ m | 2.47 × 10¹⁷ m | Evet |
| 6 (b) | L = 1.53 × 10²⁷ W (d = 2.5 × 10¹⁷ m ile 1.57 × 10²⁷ W) | 1.5 × 10²⁷ W (1.6 kabul) | Evet |
| 6 (c) | R = 9.73 × 10⁸ m (d = 2.5 × 10¹⁷ m ile 9.86 × 10⁸ m) | 9.7 × 10⁸ m (9.7–9.9 kabul) | Evet — aralık için bkz. bulgu 2 |
| 6 (d) | Kırmızı dev → dış katmanları atar (gezegenimsi bulutsu) → çekirdek beyaz cüce | Aynı | Evet |

## Özel olarak istenen denetimler

**Soru 3 (sıcaklık ve ışınım gücünden yıldız türü) — anahtardaki cevap tek savunulabilir cevap.** T = 20 000 K ve L = 0.01 L☉ için
R/R☉ = √0.01 / (20 000 / 5772)² ≈ 0.008, yani Dünya boyutunda bir cisim: beyaz cüce. Bu sıcaklıktaki ana kol yıldızı L☉'nin binlerce
katıdır; kırmızı dev ve süperdevler L☉'den parlaktır. Gereken bilgi ("HR diyagramının bölgeleri") müfredat çekirdeğinde açıkça var;
eksenler sınır maddesine uygun (düşey ışınım gücü, yatay sıcaklık). Şekil tarifinde bölgeler etiketsiz ama yerleri yazılı; soru
şekilsiz de çözülüyor.

**Soru 6 (d) (yıldız evrimi) — anahtardaki yol doğru ve tek.** 1.5 M☉ kütleli yıldız kırmızı dev → gezegenimsi bulutsu → beyaz cüce
yolunu izler (güven: yüksek). Gereken bilgi "kütlenin yıldız evrimine etkisi" kazanımının içinde. Tek çekince bulgu 3'te.

## Bulgular

KRİTİK bulgu yok.

### 1. ORTA — Soru 5: doğru cevabı C'den ayıran bilgi müfredat çekirdeğinde açıkça yok; "immediately afterwards" belirsiz

- **Yer:** Soru 5 kökü ("What happens to the core immediately afterwards?") ve seçenek A / C.
- **Açıklama:** Anahtar (A: büzülür ve ısınır) fiziksel olarak doğrudur. Ancak A ile C arasındaki tek fark sıcaklığın yönüdür ve bunu
  belirlemek, büzülen çekirdeğin kütle çekim potansiyel enerjisinin iç enerjiye dönüşmesiyle ısındığını (yıldızın "negatif ısı
  sığası") bilmeyi gerektirir. Müfredat analizinin E.5 satırı yalnızca "yıldız dengesi (ışınım basıncı ve kütle çekimi)" diyor; yazar
  da başlık notunda bunun kapsamda olduğunun teyit edilmediğini yazmış. Ayrıca "immediately afterwards" ifadesi şu zinciri kuran
  öğrenciye C'yi savunma zemini verir: daha az füzyon → çekirdekte daha az enerji üretimi → önce sıcaklık ve basınç düşer → sonra
  büzülme. Bu zincir yanlış sonuca varır ama öğrencinin elindeki çekirdek bilgiyle çürütülemez. Kesin hata değil; kapsam şüphesi +
  ifade belirsizliği.
- **Öneri (ikisinden biri):** (a) Soruyu yalnızca denge kazanımına indir: seçenekleri büzülme / genleşme / değişmeme ekseninde kur
  (ör. "It contracts because the outward pressure is less than the inward gravitational pull." tek doğru), sıcaklığı sorma.
  (b) Sıcaklık kalacaksa köke bilgiyi ver ("When the core of a star contracts, gravitational potential energy is transferred to
  internal energy.") ve "immediately afterwards" yerine "as a result" yaz. Her iki durumda uzman kapsam teyidi gerekir.

### 2. ORTA — Soru 6 (c): kabul aralığı, (b)'nin doğru yuvarlanmış cevabını kullanan öğrenciyi dışarıda bırakıyor

- **Yer:** Soru 6 (c) markscheme, Notes ("Accept answers in the range 9.7–9.9 × 10⁸ m").
- **Açıklama:** (b)'nin markscheme cevabı 1.5 × 10²⁷ W, kabul edilen alternatifi 1.6 × 10²⁷ W. Bu iki değeri (c)'de kullanan öğrenci
  sırasıyla R = 9.64 × 10⁸ m ve R = 9.95 × 10⁸ m bulur (yeniden hesapladım); ikisi de 9.7–9.9 aralığının dışında. "Allow ECF from (b)"
  notu bunu kurtarabilir, ama ECF yanlış ara sonuç içindir; burada ara sonuç doğru ve aralık onu dışlıyor — puanlayıcılar arasında
  tutarsızlık doğurur.
- **Öneri:** Aralığı "9.6–10.0 × 10⁸ m" yap (yuvarlanmış L değerlerini de kapsar).

### 3. ORTA (şüphe) — Soru 6 (d): 1.5 M☉ seçimi ve kütle eşiği

- **Yer:** Soru 6 (d) kökü ("The mass of star K is 1.5 times the mass of the Sun").
- **Açıklama:** Cevap doğru. Ancak öğrencinin 1.5 M☉'nin "düşük kütle" olduğuna karar vermesi için bir sayısal eşik (yaklaşık 8 M☉)
  bilmesi gerekir; müfredat analizinde sayısal eşik yazmıyor. Buna ek olarak 1.5 M☉, ders kitaplarında sık geçen Chandrasekhar
  sınırının (1.4 M☉, **kalıntı çekirdek** için) hemen üstünde; sınırı yıldızın toplam kütlesine uygulayan öğrenci "nötron yıldızı"
  yazar ve markscheme bunu reddeder. Bu, sorunun ölçmek istediği kazanım dışında bir tuzak. Doğrulanmış hata değil; uzman görüşü
  gerektiren bir şüphe.
- **Öneri:** Kütleyi tuzaktan uzak seç (ör. "about the same mass as the Sun") ya da köke "This mass is too small for the star to
  become a supernova." benzeri bir yönlendirme ekle; sayısal eşiklerin kapsamda olup olmadığı uzmana sorulsun.

### 4. DÜŞÜK — Soru 6: σ soruda verilmemiş, diğer sabitler verilmiş

- **Yer:** Soru 6, veri tablosunun altındaki sabit satırı.
- **Açıklama:** 1 pc ve 1 ly soruda verilirken (c) için gereken σ verilmemiş (veri kitapçığında var). Çözülebilir; yalnızca tutarsız.
- **Öneri:** Ya σ'yı da ekle ya da hiçbirini verme ve veri kitapçığına bırak.

### 5. DÜŞÜK — Soru 6 (b): b = L / 4πd² başka düğümün (B.1) içeriği (yazarın bildirdiği)

- **Yer:** Soru 6 (b); başlık notu.
- **Açıklama:** Kazanım etiketi E.5 ama (b) B.1 ilişkisine dayanıyor. Soru kapsam içinde; yalnızca tek-düğüm etiketlemesi
  ("her soru tek bir düğümün kazanımını ölçer") tam karşılanmıyor. Yazar bunu not etmiş.
- **Öneri:** Kapsam tablosunda ikincil düğüm olarak B.1 yazılsın.

### 6. DÜŞÜK — Biçim: SL kısa sorusu 9 puan; veri tablosu başlığı; Soru 5 seçenek D (yazarın kısmen bildirdiği)

- **Yer:** Soru 6 başlığı ve veri tablosu; Soru 5 seçenek D.
- **Açıklama:** (i) Biçim profili SL kısa sorularını 4–6 puan gözlemiş; Soru 6 dokuz puan. (ii) Veri tablosu "Quantity / Value"
  başlıklı, birimler hücrede. İkisini de yazar işaretlemiş; doğruluyorum. (iii) Soru 5'te A–C "değişim + sıcaklık" çifti, D ise gerekçe
  içeren farklı yapıda bir cümle; seçenekler aynı türde değil.
- **Öneri:** (iii) için D: "It stays the same size and its temperature stays the same."

## Sorun bulunmayan denetimler

- **Müfredat sınırı ve düzey:** tüm sorular SL; Sefe değişenleri yok; uzaklık yalnızca ıraklıkla. Türev/integral yok.
- **Çeldiriciler:** Soru 1 (0.13; 7.7; 25 ly), Soru 2 (0.5; 4; 64) yeniden üretildi; yazılan yanılgılar o değerleri veriyor.
- **Tek doğru cevap, Soru 4:** A (iyonlaşma) yüksek sıcaklığın sonucu ama füzyon için gereken neden değil; D füzyonun sonucunu
  koşuluyla karıştırıyor; yalnızca B.
- **Gerçekçilik:** yıldız K (L ≈ 4.0 L☉, T = 6900 K, R ≈ 1.4 R☉, 1.5 M☉) ana kol için tutarlı (L ∝ M^3.5 ≈ 4.1 L☉; güven: yüksek).
- **Puanlar:** Soru 6: 2 + 2 + 3 + 2 = 9; her satırdaki ✓ sayısı parça puanına eşit; parça puanları 1–3. Formül zinciri hesaplarımla aynı.
- **Biçim:** sayısal seçenekler artan sırada; doğru cevap konumları D, C, A, B, A.

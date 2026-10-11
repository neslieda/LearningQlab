# Bağımsız inceleme: C.5 Doppler etkisi

> Tarih: 2026-10-11. İncelenen dosya: [c5-doppler-effect-pilot-questions.md](../c5-doppler-effect-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtar ve markscheme ile
> karşılaştırma, sonra yazım standardı, müfredat analizi (C.5 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | Δλ/λ = 6.0 × 10⁶ / 3.00 × 10⁸ = 0.020 → Δλ = 13 nm; uzaklaşma → 663 nm → **C** | C | Evet |
| 2 (1A) | Sabit hızla doğrudan yaklaşan kaynak: frekans f'den büyük ve sabit → **B** | B | Evet |
| 3 (1A) | Hareketli kaynak, yaklaşma: 600 × 340/300 = 680 Hz → **D** | D | Evet |
| 4 (1A) | Hareketli gözlemci, uzaklaşma: 800 × 306/340 = 720 Hz → **A** | A | Evet |
| 5 (a) | Kaynak ardışık dalga cepheleri arasında dedektöre yaklaşır → cepheler sıklaşır, λ kısalır; ses hızı aynı → f artar | Aynı | Evet |
| 5 (b) | u = 340 × (1 − 40.0/41.2) = 9.90 m s⁻¹ | 9.9 m s⁻¹ | Evet |
| 5 (c) | 40.0 × 340/(340 + 9.90) = 38.87 kHz ≈ 38.9 kHz (u = 10 ile 38.86) | 38.9 kHz | Evet |
| 5 (d) | Hareketli gözlemci: 40.0 × 350/340 = 41.18 kHz. Bu da **3 anlamlı basamakta 41.2 kHz**; yani öneri verilerin duyarlığında doğru, kesin olarak değil. Formüller farklı; u ≪ v olduğu için fark küçük | "not exactly correct, but the difference is small" | Kısmen (Bulgu 2) |

Çeldiriciler yeniden hesaplandı: S1 637; 650; 676 nm. S3 529.4; 536.8; 670.6 Hz. S4 727.3; 880; 888.9 Hz. Hepsi yazılan hesaptan
çıkıyor; her 1A sorusunda tek doğru seçenek var.

Özel olarak istenen denetim: hiçbir soruda kaynak ve gözlemci **aynı anda** hareket etmiyor (Soru 1–4 tek hareketli; Soru 5 (a)–(c)
yalnızca kaynak, (d) yalnızca gözlemci hareketli; yankı bağlamı yok).

Kural denetimi: Soru 1–2 SL (ışık için Δλ/λ ≈ v/c; ses için nitel), Soru 3–5 HL (ses için hareketli kaynak / gözlemci formülleri) —
etiketler doğru. SL sorularında ses için hesap yok. Türev/integral yok. Sayısal seçenekler aynı birimde ve artan sırada. Soru 5
puanları 2+2+2+3 = 9; markscheme ✓ sayıları parça puanlarıyla eşleşiyor. Gerçekçilik: gökada 6.0 × 10⁶ m s⁻¹ (z = 0.02), 40 kHz
yarasa sesi ve 10 m s⁻¹ uçuş hızı makul; Soru 4'teki bisikletli hariç (Bulgu 3).

## Bulgular

KRİTİK bulgu yok. Üç ORTA bulgunun ikisi (1 ve 2) aynı veri değişikliğiyle birlikte giderilebilir.

### 1. ORTA — Soru 5 (b): "about 10 m s⁻¹" hedefi yanlış formülü de doğruluyor

- **Yer:** Soru 5 (b) ve markscheme notu ("moving-observer equation (giving 10.2 m s⁻¹) scores [0]").
- **Açıklama:** Senaryo formülü belirsiz bırakmıyor: yarasa (kaynak) hareketli, dedektör "stationary". Öğrenci doğru formülü
  **metinden** seçebilir; bu açıdan soru çözülebilir. Sorun "Show that" hedefinde: doğru formül 9.90, yanlış (hareketli gözlemci)
  formül 10.2 m s⁻¹ veriyor ve ikisi de "about 10" koşulunu sağlıyor. Yanlış formülü kullanan öğrenci hedefe ulaştığını görür,
  hatasını fark edemez ve puanlayıcı [0] verir. "Show that" kalıbının öz denetim işlevi burada çalışmıyor; 2 puanın tamamı tek bir
  formül seçimine bağlı ve öğrenci geri bildirim almıyor.
- **Öneri (yeni sayılar):** dedektörün kaydettiği frekansı **42.0 kHz** yap ve hedefi "about 16 m s⁻¹" olarak değiştir.
  - Doğru (hareketli kaynak): u = 340 × (1 − 40.0/42.0) = **16.19 m s⁻¹** → "about 16".
  - Yanlış (hareketli gözlemci): u = 340 × (42.0/40.0 − 1) = **17.0 m s⁻¹** → 2 anlamlı basamakta 17; hedefi tutmaz, öğrenci hatayı görür.
  - (c): 40.0 × 340/(340 + 16) = **38.2 kHz** (u = 16.19 ile 38.18 → yine 38.2).
  - (d): öğrenci önerisi "42.0 kHz, dedektör 16 m s⁻¹ ile yaklaşırsa" olur; 40.0 × (340 + 16)/340 = **41.9 kHz** ≠ 42.0 kHz
    (16.19 ile 41.90). Hareketli kaynak, 16 m s⁻¹: 41.98 ≈ 42.0 kHz.
  - (a)'daki "higher than 40.0 kHz" değişmez.
  - Gerçekçilik: 16 m s⁻¹ hızlı uçan yarasa türleri için makul görünüyor ama bir kaynaktan teyit etmedim; uzman onayı gerekir.
- **Alternatif (sayılar kalırsa):** hedefi 3 anlamlı basamakla ver: "Show that the speed of the bat is about 9.9 m s⁻¹." Bu durumda
  10.2 hedefi tutmaz; ancak (d)'deki sorun (Bulgu 2) çözülmez.

### 2. ORTA — Soru 5 (d): öğrencinin önerisi verilerin duyarlığında doğru; markscheme "doğru değil" sonucuna 4 basamakla varıyor

- **Yer:** Soru 5 (d) ve markscheme'in üç maddesi.
- **Açıklama:** Hareketli gözlemci formülü 10 m s⁻¹ için 41.18 kHz verir; bu, sorudaki duyarlıkta (3 anlamlı basamak) **41.2 kHz**'dir.
  (b)'nin gerçek sonucu olan 9.90 m s⁻¹ ile de 41.17 → 41.2 kHz çıkar. Yani "the detector would also record 41.2 kHz" cümlesi, verilen
  anlamlı basamakta doğrudur. Markscheme 41.18 ile 41.21'i karşılaştırıp "not exactly correct" diyor; bu karşılaştırma 2 anlamlı
  basamaklı "10 m s⁻¹" verisinden 4 basamaklı sonuç üretmeye dayanıyor. "Öneri 3 anlamlı basamakta doğrudur, çünkü u ≪ v" diye
  bitiren öğrenci fizik olarak haklıdır; markscheme'in üçüncü maddesi bu sonucu açıkça kabul etmiyor ("not exactly correct"), "Accept
  comparison with 41.2 kHz" notu ise karşılaştırınca fark çıkmadığı için işlemiyor. Tartışmanın özü (iki formül farklı; fark u/v
  küçükken küçülür) doğru, ama sayılar bu farkı göstermiyor.
- **Öneri:** Bulgu 1'deki yeni sayılarla (42.0 kHz, 16 m s⁻¹) fark 3 anlamlı basamakta görünür: 41.9 kHz ile 42.0 kHz. Markscheme:
  "moving observer: f = 40.0 × (340 + 16)/340 = 41.9 «kHz» ✓ · this is less than 42.0 kHz / the two situations are described by
  different equations «because the motion is relative to the air» ✓ · the suggestion is incorrect, although the difference is small
  because the speed is much less than the speed of sound ✓".
  Sayılar değiştirilmeyecekse markscheme'in üçüncü maddesine şu not eklenmeli: "Accept the conclusion that the suggestion is correct
  to 3 s.f. if the two equations are distinguished."

### 3. ORTA — Soru 4: "cyclist … at 34 m s⁻¹" gerçekçi değil

- **Yer:** Soru 4 kökü; yazar da dosyada not etmiş.
- **Açıklama:** 34 m s⁻¹ ≈ 122 km h⁻¹; bisikletli için gerçek dışı. Yazım standardı gerçekçi veri istiyor.
- **Öneri:** "cyclist" yerine "motorcyclist" (ya da "a passenger in a car") yaz; sayılar ve seçenekler aynen kalır (720, 727, 880,
  889 Hz). Hızı düşürmek önerilmez: 17 m s⁻¹ ile anahtar 760 Hz, hareketli kaynak çeldiricisi 762 Hz olur ve fark %0.25'e iner.

### 4. DÜŞÜK — Soru 3 ve 4: anahtara yakın çeldiriciler ve anlamlı basamak

- **Yer:** Soru 3 (680 / 671 Hz), Soru 4 (720 / 727 Hz).
- **Açıklama:** Değerlendirme: sorular bu haliyle **adil**. Farklar %1.4 ve %1.0; seçenekler 3 anlamlı basamakta ayrık, hesap makinesi
  olan öğrenci için yuvarlama kaynaklı karışıklık yok ve ölçülen beceri tam olarak iki formülü ayırt etmek. Tek tutarsızlık: hızlar
  2 anlamlı basamakla verilmiş (40 ve 34 m s⁻¹), seçenekler 3 anlamlı basamakta. 2 anlamlı basamakta Soru 4'te 720 ile 730 hâlâ ayrık
  ama fark son basamakta kalıyor.
- **Öneri:** Hızları "40.0 m s⁻¹" ve "34.0 m s⁻¹" yaz (frekanslar ve 340 m s⁻¹ zaten 3 basamaklı okunuyor). İstenirse Soru 4'te fark
  büyütülebilir: gözlemci hızı 68 m s⁻¹ (ör. alçak uçan küçük uçak) → anahtar 640 Hz, hareketli kaynak çeldiricisi 667 Hz, ters yön
  960 Hz ve 1000 Hz. Bu zorunlu değil.

### 5. DÜŞÜK — Soru 5 (c): markscheme 10 m s⁻¹ kullanıyor, kök "at the same speed" diyor

- **Yer:** Soru 5 (c) kökü, markscheme ve "Biçim uyumu" satırı ("(c) ve (d) verilen 10 m s⁻¹ değerini kullanır").
- **Açıklama:** Kökte "Use 10 m s⁻¹" yönergesi yok; öğrenci 9.90 kullanabilir. Sonuç her iki değerle 38.9 kHz, markscheme de 9.9'u
  kabul ediyor; yani puanlama sorunu yok, yalnızca biçim uyumu satırındaki ifade kökle örtüşmüyor.
- **Öneri:** (c)'den önce "Use a speed of 10 m s⁻¹ for the bat." cümlesini ekle (yeni sayılarla "16 m s⁻¹").

### Şüphe (hata değil)

- Soru 1'in D çeldiricisi (kaymanın iki katı, "gidiş–dönüş") yansıma içeren radar bağlamına ait bir düşünce; gökada bağlamında zayıf
  ama sayı tutarlı.
- Soru 3'te sesi ışık yaklaşımıyla (Δf/f ≈ v/c) çözen öğrenci 600 × 40/340 = 70.6 → 671 Hz (C) bulur; bu, C çeldiricisini ayrıca
  destekleyen ikinci bir yanılgı yoludur ve çeldirici tablosuna eklenebilir.

# Bağımsız inceleme: C.2 Dalga modeli

> Tarih: 2026-10-11. İncelenen dosya: [c2-wave-model-pilot-questions.md](../c2-wave-model-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtar ve markscheme ile
> karşılaştırma, sonra yazım standardı, müfredat analizi (C.2 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | λ = 1500 / 1.5 × 10⁵ = 1.0 × 10⁻² m → **A** | A | Evet |
| 2 (1A) | Dalga sağa gidiyor; soldaki tepe P'ye yaklaşıyor → P yukarı hareket ediyor → **D** | D | Evet |
| 3 (1A) | Ardışık sıfır geçişleri T/2 → T = 4.0 ms; λ = 1.36 m; sıkışma–seyrelme λ/2 = 0.68 m → **B** | B | Evet |
| 4 (1A) | λ = 3.00 × 10⁸ / 2.5 × 10⁹ = 0.12 m → **C** | C | Evet |
| 5 (a) | Ortam parçacıklarının salınımı enerji aktarım (ilerleme) yönüne dik | Aynı | Evet |
| 5 (b) | f = 12/30 = 0.40 Hz; v = 0.40 × 3.5 = 1.4 m s⁻¹ | 1.4 m s⁻¹ | Evet |
| 5 (c) | 5.25 / 3.5 = 1.5 λ → zıt faz → −4.0 cm (çukurda) | −4.0 cm | Evet |
| 5 (d) | 12 × 4 × 4.0 cm = 192 cm = 1.92 m | 1.9 m | Evet |
| 5 (e) | Dalga enerji taşır, madde taşımaz; şamandıra sabit bir konum çevresinde salınır (21/15 = 1.4 m s⁻¹ dalganın hızıdır) | Aynı | Evet |

Çeldiriciler yeniden hesaplandı: S1 1500/150 = 10; 150 000/1500 = 100; 3.00 × 10⁸/1.5 × 10⁵ = 2.0 × 10³. S3 0.34; 1.36 ≈ 1.4;
2.72 ≈ 2.7. S4 340/2.5 × 10⁹ = 1.36 × 10⁻⁷ ≈ 1.4 × 10⁻⁷; 1.2 × 10⁻⁴; 8.33. Hepsi yazılan hesaptan çıkıyor; her soruda tek doğru
seçenek var. Soru 2'de verilen uzaklıklar kendi içinde tutarlı (tepe–çukur 0.20 m = λ/2, P tam ortada sıfır yer değiştirmede).

Kural denetimi: tüm sorular SL (C.2 yalnızca SL) — etiket doğru. Spektrum mertebesi ezberi istenmiyor. Türev/integral yok. Sayısal
seçenekler artan sırada ve aynı birimde. Soru 5 puanları 1+2+2+2+2 = 9; markscheme ✓ sayıları parça puanlarıyla eşleşiyor.
Gerçekçilik: yunus 150 kHz, deniz suyunda 1500 m s⁻¹, mikrodalga fırın 2.5 GHz gerçek değerlere uygun. Soru 5'teki su dalgası
(λ = 3.5 m, T = 2.5 s, v = 1.4 m s⁻¹) derin su bağıntısıyla uyuşmaz (derin suda λ = 3.5 m için v ≈ 2.3 m s⁻¹) ama sığ su için
v = √(gh) → h ≈ 0.20 m ile tutarlı; kıyıya yakın bir göl için kabul edilebilir.

## Bulgular

KRİTİK ve ORTA bulgu yok. Doğrulanmış hata yok.

### 1. DÜŞÜK — Soru 5: SL etiketli kısa soru 9 puan

- **Yer:** Soru 5 başlığı; yazar "Biçim uyumu" tablosunda zaten not etmiş.
- **Açıklama:** Biçim profilinde SL kısa soruları 4–6 puan. C.2 yalnızca SL olduğundan bu soru SL kâğıdında bu haliyle uzun kalır.
- **Öneri:** SL sürümü için (d) çıkarılırsa 7, (d) ve (a) çıkarılırsa 6 puan kalır; ya da soru iki ayrı kısa soruya bölünür
  ((a)(b)(c) = 5 puan; (d)(e) = 4 puan).

### 2. DÜŞÜK — Soru 1: seçeneklerin yazımı karışık

- **Yer:** Soru 1 seçenekleri (A 1.0 × 10⁻² m, B 10 m, C 1.0 × 10² m, D 2.0 × 10³ m).
- **Açıklama:** Üç seçenek bilimsel gösterimde, B düz yazılmış. Biçim profili "dört seçenek aynı biçimde" diyor.
- **Öneri:** B'yi "1.0 × 10¹ m" yaz ya da hepsini düz yaz (0.010 m, 10 m, 100 m, 2000 m).

### 3. DÜŞÜK — Soru 3: D çeldiricisinin dayanağı zayıf

- **Yer:** Soru 3, çeldirici tablosu, D satırı ("iki dalga boyu alınır").
- **Açıklama:** 2.7 m değeri hesapla doğru (2 × 1.36 = 2.72) ama "sıkışma–seyrelme arası iki dalga boyu" bilinen bir yanılgı değil.
- **Öneri:** Dayanak şöyle yazılabilir: "2.0 ms çeyrek periyot sanılır (T = 8.0 ms → λ = 2.72 m) ve sıkışma–seyrelme arası tam dalga
  boyu alınır: 2.7 m". Sayı değişmez.

### Şüphe (hata değil)

- Soru 5'te su yüzeyi dalgasının enine dalga olarak modellenmesi yazarın da belirttiği bir basitleştirme; kökte "can be modelled as a
  transverse wave" yazdığı için öğrenci açısından belirsizlik yok.
- Soru 5 (c)'de ikinci şamandıranın birincinin önünde mi arkasında mı olduğu verilmemiş; yol farkı 1.5 λ olduğundan sonuç her iki
  durumda −4.0 cm, yani eksik bilgi sorun yaratmıyor.

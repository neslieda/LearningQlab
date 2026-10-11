# Bağımsız inceleme: E.4 Fisyon

> Tarih: 2026-10-11. İncelenen dosya: [e4-fission-pilot-questions.md](../e4-fission-pilot-questions.md).
> Yöntem: önce cevapları çıkarılmış öğrenci görünümü üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtarla karşılaştırma,
> sonra yazım standardı, müfredat analizi (E.4 satırı) ve biçim profiline göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.
> Kullanılan sabitler: 1 u = 1.661 × 10⁻²⁷ kg = 931.5 MeV c⁻², e = 1.60 × 10⁻¹⁹ C.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | B (240 × (8.5 − 7.6) = 216 MeV) | B | Evet |
| 2 | D | D | Evet |
| 3 | C (sabit güç → fisyon başına ortalama 1 nötron) | C | Evet |
| 4 | A | A | Evet |
| 5 (a) | Çekirdek bir nötron soğurur ve iki küçük çekirdeğe (ve nötronlara) bölünür | Aynı | Evet |
| 5 (b) | Δm = 0.198255 u → 184.7 MeV | 0.19826 u; 184.7 MeV | Evet |
| 5 (c) | 2.07 × 10¹⁴ J/gün; 7.01 × 10²⁴ fisyon; 2.73 kg | 2.7 kg | Evet |
| 5 (d) | U-235'te fisyon olasılığı yavaş (ısıl) nötronlar için çok daha büyük; hızlı nötronlar kaçar ya da fisyon yapmadan soğurulur, zincir sürmez | Aynı | Evet |

## Bulgular

KRİTİK ya da ORTA bulgu yok.

### 1. DÜŞÜK — Soru 5: kütle tablosunda kütlelerin türü (atom / çekirdek) yazmıyor

- **Yer:** Soru 5 veri tablosu, başlık "Particle | Mass / u".
- **Açıklama:** Verilen değerler **atom** kütleleridir (U-235 235.04393 u, Xe-140 139.92165 u, Sr-94 93.91536 u). Tepkimede elektron
  sayısı dengeli (92 = 54 + 38) olduğu için atom kütleleriyle hesap doğru sonucu verir; karışıklıktan doğan bir sayısal hata **yok**.
  Yine de "Particle" başlığı altında çekirdek kütlesi sanılabilir; E.3 Soru 3 çekirdek kütlesi kullandığı için setler arası tutarlılık
  açısından belirtilmesi iyi olur.
- **Öneri:** Başlığı "Atomic mass / u" yap ya da tablonun üstüne "The masses of the atoms and of the neutron are given." ekle.

### 2. DÜŞÜK — Soru 5: SL kısa sorusu için 9 puan (yazarın bildirdiği)

- **Yer:** Soru 5 başlığı; Biçim uyumu tablosu.
- **Açıklama:** Yazım standardı 4–9 puana izin veriyor, ama biçim profili SL kısa sorularını 4–6 puan olarak gözlemiş. Yazar bunu
  not etmiş; doğruluyorum.
- **Öneri:** SL havuzu için (a)+(b) [4] ve (c)+(d) [5] olarak iki soruya bölme seçeneği uzman kararına bırakılsın.

### 3. DÜŞÜK — Soru 4: seçenek yapısı

- **Yer:** Soru 4 seçenek A–D.
- **Açıklama:** Kök "purposes" (çoğul) diyor; yalnızca A iki amaç içeriyor, B–D "X so that Y" biçiminde tek amaç. Biçim farkı doğru
  cevabı ele verebilir. Tek doğru cevap değişmiyor.
- **Öneri:** Kökü "What is the main purpose …" yapıp A'yı tek amaca indir ya da B–D'yi de iki ögeli yaz.

## Özel olarak istenen denetimler

- **Çekirdek denklemi (Soru 5):** ¹₀n + ²³⁵₉₂U → ¹⁴⁰₅₄Xe + ⁹⁴₃₈Sr + 2 ¹₀n; nükleon 1 + 235 = 140 + 94 + 2 = 236, yük 92 = 54 + 38 — doğru.
- **Alıntılanan veriler (bellekle karşılaştırma):**

| Veri | Dosyada | Benim bildiğim | Güven |
|---|---|---|---|
| U-235 atom kütlesi | 235.04393 u | 235.04393 u | Yüksek |
| Xe-140 atom kütlesi | 139.92165 u | ≈ 139.92165 u | Orta–yüksek |
| Sr-94 atom kütlesi | 93.91536 u | ≈ 93.91536 u | Orta–yüksek |
| Nötron kütlesi | 1.008665 u | 1.008665 u | Yüksek |
| Bu kanalın enerjisi | 184.7 MeV | ≈ 185 MeV | Yüksek |
| Z: U, Xe, Sr | 92, 54, 38 | aynı | Yüksek |
| Fisyon başına ortalama nötron (U-235, ısıl) | 2.5 | ≈ 2.4 | Yüksek (yuvarlak değer kabul edilebilir) |
| Nükleon başına bağlanma enerjisi A ≈ 240 / A ≈ 120 | 7.6 / 8.5 MeV | ≈ 7.6 / ≈ 8.5 MeV | Yüksek |

  Xe-140 ve Sr-94 kütlelerinin son basamakları bellekten; kaynakla teyit yazarın notundaki gibi hâlâ gerekli.
- **Gerçekçilik:** 2.4 GW ısıl güç için günde 2.7 kg U-235, bilinen büyüklük mertebesiyle (GW-gün başına yaklaşık 1 kg) uyumlu.
- **Müfredat sınırı ve düzey:** tüm sorular SL; E.4 için açık sınır yok. Kritik kütle, zenginleştirme sorulmuyor. Türev/integral yok.
- **Çeldiriciler:** Soru 1 (2040; 108; 0.90 MeV) yeniden üretildi; Soru 2'de A kontrol çubuğu, B ısı değiştirici, C zırhlama — her
  biri tek bir bileşenle karışıklığa dayanıyor ve yalnızca D doğru. Soru 3'te yalnızca 1 sabit güçle uyumlu.
- **Puanlar:** Soru 5: 1 + 3 + 3 + 2 = 9; her satırdaki ✓ sayısı parça puanına eşit; parça puanları 1–3. (b) "Show that" 3 a.b. istiyor
  (184.7), (c) verilen 185 MeV'i kullanıyor.
- **Biçim:** sayısal seçenekler azalan sırada ve aynı birimde; doğru cevap konumları B, D, C, A; formül zinciri hesaplarımla aynı.

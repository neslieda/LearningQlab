# Bağımsız inceleme: C.1 Basit harmonik hareket

> Tarih: 2026-10-11. İncelenen dosya: [c1-simple-harmonic-motion-pilot-questions.md](../c1-simple-harmonic-motion-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtar ve markscheme ile
> karşılaştırma, sonra yazım standardı, müfredat analizi (C.1 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | T ∝ √m; kütle 4 kat → T 2 kat = 1.2 s → **C** | C | Evet |
| 2 (1A) | ω = 2π × 0.50 = π; a = π² × 0.20 = 1.97 ≈ 2.0 m s⁻² → **B** | B | Evet |
| 3 (1A) | KE en büyük dengede, EPE en büyük uçta; arası T/4 → **A** | A | Evet |
| 4 (1A) | v = 2.0 × √(1 − 0.60²) = 1.6 m s⁻¹ → **D** | D | Evet |
| 5 (1A) | sin φ = 0.5 ve cos φ > 0 → φ = π/6 → **A** | A | Evet |
| 6 (a) | İvme (geri çağırıcı kuvvet) denge konumundan yer değiştirmeyle orantılı; denge konumuna yönelik | Aynı iki madde | Evet (ifade belirsizliği için Bulgu 1) |
| 6 (b) | T = 4.9 s; L = 9.8 × 4.9² / 4π² = 5.96 m | 5.96 m | Evet |
| 6 (c) | ω = 1.28 rad s⁻¹; a = ω²x₀ = 0.493 ≈ 0.49 m s⁻² | 0.49 m s⁻² | Evet |
| 6 (d) | GPE → KE (en alt noktaya kadar) → GPE; toplam enerji sabit | Aynı | Evet |
| 6 (e) | 3.0 m genlik ≈ 30°; küçük açı yaklaşımı geçersiz, geri çağırıcı kuvvet yer değiştirmeyle orantılı değil | Aynı | Evet |
| 7 (a) | T'deki kesirli (tepki süresi) belirsizliği küçülür | Aynı | Evet |
| 7 (b)(i) | 0.2 / 10 = 0.02 s | 0.02 s | Evet |
| 7 (b)(ii) | 2 × 0.2 / 4.9 = %8.2 ≈ %8 | %8 (8.2 kabul) | Evet |
| 7 (c) | k = 4π² / 1.56 = 25.3; Δk: aralık yöntemi 23.2–27.8 → ±2.3; k = 25 ± 2 N m⁻¹ | (25 ± 2) N m⁻¹ | Evet |
| 7 (d)(i) | Askının (ve yayın) kütlesi m'ye dahil değil; sabit ek kütle | Aynı | Evet |
| 7 (d)(ii) | T² = 4π²(m + m₀)/k; eğim 4π²/k değişmez, yalnızca kesim noktası oluşur; k etkilenmez | Aynı | Evet |

Yeniden hesaplananlar (Soru 7, tablodan): T² = 0.2401, 0.3969, 0.5476, 0.7056, 0.8649 s²; en küçük kareler eğimi **1.558 s² kg⁻¹**,
kesim noktası **0.0835 s²** (dosyada 1.558 ve 0.084; soruda 1.56 ve 0.08 — tutarlı). T² belirsizlikleri 2TΔT = 0.0196 … 0.0372 s².
Uç noktaların belirsizlik çubuklarından geçen doğrular: en büyük eğim (0.9021 − 0.2205)/0.400 = **1.704**, en küçük eğim
(0.8277 − 0.2597)/0.400 = **1.420** (soruda 1.70 ve 1.42 — tutarlı). k = 4π²/1.56 = 25.31; 4π²/1.42 = 27.80; 4π²/1.70 = 23.22;
Δk = 25.3 × 0.14/1.56 = 2.3 → **k = 25 ± 2 N m⁻¹**. Kesim/eğim = 0.0835/1.558 = 0.054 kg (soruda verilen yuvarlanmış değerlerle
0.08/1.56 = 0.051 kg); gizli 0.050 kg'lık askı ile tutarlı. Veri denetimi: T = 2π√(0.150/25) = 0.487 s → t = 4.9 s ✓.

Askı kütlesinin etkisi: sabit ek kütle doğruyu m ekseni boyunca kaydırır; **kesim noktasını değiştirir, eğimi değiştirmez** — dosyadaki
ifade doğru. Yayın kendi kütlesi de aynı türden (etkin kütle ≈ m_yay/3) katkı yapar; markscheme bunu da kabul ediyor.

Çeldiriciler yeniden hesaplandı: S1 0.30 / 0.60 / 2.4; S2 0.628, 3.95, 31.6; S4 0.80, 1.2, 1.26; S5 sin(π/3) = sin(2π/3) = 0.87,
sin(5π/6) = 0.50 ve cos < 0. Hepsi yazılan yanılgıdan çıkıyor; her soruda tek doğru seçenek var. Soru 6 denetimi: asin(0.30/5.96) = 2.9°,
asin(3.0/5.96) = 30.2°; 9.8 × 0.30 / 6 = 0.49 ✓.

Kural denetimi: Soru 4 ve 5 HL (v = ±ω√(x₀² − x²), faz açısı) — etiket doğru; Soru 1–3, 6, 7 SL içeriği (a = −ω²x, periyot bağıntıları,
nitel enerji). SL'de nicel enerji sorulmuyor (Soru 3 ve 6(d) nitel). Türev/integral yok; faz açısı radyan. Seçenekler aynı birimde ve
artan sırada. Puanlar: Soru 6 2+2+2+2+1 = 9; Soru 7 1+1+2+3+1+2 = 10; markscheme ✓ sayıları parça puanlarıyla eşleşiyor. Veriler
gerçekçi (k ≈ 22–25 N m⁻¹ yay; 6 m'lik sarkaç; 0.50 Hz şamandıra).

## Bulgular

KRİTİK bulgu yok. Doğrulanmış hata yok; aşağıdakiler ifade ve biçim konularıdır.

### 1. ORTA — Soru 6 (a): "the two conditions" ifadesi iki farklı cevaba açık

- **Yer:** Soru 6 (a) kökü: "State the **two** conditions for the motion of the lamp to be simple harmonic."
- **Açıklama:** Markscheme BHH'nin tanım koşullarını bekliyor (ivme ∝ yer değiştirme; denge konumuna yönelik). Ancak soru "lambanın
  hareketi" için koşul sorduğundan, öğrenci fiziksel koşulları yazabilir: "salınım açısı küçük olmalı" ve "sürtünme/hava direnci ihmal
  edilebilir olmalı" (ya da "kablo hafif ve uzamaz"). Bu cevap fizik olarak savunulabilir ama markscheme'de puan almıyor. Üstelik (e)
  parçası küçük açı koşulunu ayrıca soruyor; bu da (a)'da o cevabı vermeye yönlendirebilir. Kör çözümde bu ikilemi fark ettim.
- **Öneri:** Kökü tanıma bağla: "State, in terms of the acceleration of the lamp, the **two** conditions for its motion to be simple
  harmonic." Alternatif: "State the two defining conditions of simple harmonic motion." Markscheme değişmez.

### 2. DÜŞÜK — Soru 6: SL etiketli kısa soru 9 puan

- **Yer:** Kapsam tablosu satır 6 ve "Biçim uyumu" tablosu ("Soru 6 uygun").
- **Açıklama:** Biçim profiline göre SL Paper 2 kısa soruları 4–6 puan, HL 4–9 puan. C.2 ve C.4 dosyaları bu farkı not etmiş; C.1'de
  not yok.
- **Öneri:** Biçim uyumu satırına aynı notu ekle ya da SL kâğıdı için (d) ya da (e) parçasını ayrılabilir olarak işaretle.

### 3. DÜŞÜK — Soru 7 (c): markscheme'in üçüncü puanı aralık yöntemiyle çelişmesin

- **Yer:** Soru 7 (c) markscheme, Notes sütunu.
- **Açıklama:** Aralık yöntemi asimetrik sonuç verir (25.3 − 23.2 = 2.1; 27.8 − 25.3 = 2.5). Not "± 2.3" diyor; bu yarı aralıktır
  ((27.8 − 23.2)/2 = 2.3), doğru ama nasıl bulunduğu yazılmamış. Hata değil, açıklık sorunu.
- **Öneri:** Nota "(27.8 − 23.2)/2 = 2.3" ifadesini ekle.

### Şüphe (hata değil)

- Soru 3'ün D çeldiricisi (2T) zayıf; enerji periyodunun 2T sanılması pek yaygın bir yanılgı değil. Uzman isterse 3T/4 gibi bir
  değerle değiştirilebilir (o zaman sıra T/4, T/2, 3T/4, T olur).
- Soru 7'de grafiğin olmaması (eğimlerin metinde verilmesi) yazarın kendi "Biçim uyumu" tablosunda zaten belirtilmiş.

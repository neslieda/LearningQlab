# Bağımsız inceleme: B.5 Akım ve devreler

> Tarih: 2026-10-11. İncelenen dosya: [b5-current-circuits-pilot-questions.md](../b5-current-circuits-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile; devreler yalnızca sözlü tariften
> çözüldü), sonra anahtar ve markscheme ile karşılaştırma, sonra yazım standardı, müfredat analizi (B.5 satırı) ve biçim profiline
> göre kural denetimi. Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | R ∝ L / d²; 2 / 4 = 1⁄2 → R⁄2 → **A** | A | Evet |
| 2 (1A) | I = 6.0 / (2.5 + 0.50) = 2.0 A; P = 2.0² × 2.5 = 10 W → **B** | B | Evet |
| 3 (1A) | V = 9.0 × 10 / (10 + 2.0) = 7.5 V → **D** | D | Evet |
| 4 (1A) | Paralel 3.0 Ω; toplam 9.0 Ω; I = 2.0 A; paralel gerilim 6.0 V; 6.0 / 4.0 = 1.5 A → **C** | C | Evet |
| 5 (a) | A = π (0.10 × 10⁻³)² = 3.14 × 10⁻⁸ m²; L = RA / ρ = 0.137 m | 0.137 m | Evet |
| 5 (b) | I = 6.0 / 6.0 = 1.0 A; P = 4.8 W | 4.8 W | Evet |
| 5 (c) | Bataryadan akım geçer; iç dirençte gerilim düşer (Ir = 1.2 V); uç gerilimi = emk − Ir = 4.8 V | Aynı iki madde | Evet |
| 5 (d) | Paralel 2.4 Ω; I = 6.0 / 3.6 = 1.67 A; P = 6.67 W < 2 × 4.8 = 9.6 W → öngörü yanlış (uç gerilimi 4.0 V'a düşer; oran 1.39) | 6.7 W < 9.6 W, öngörü yanlış | Evet |

Devrelerin sözlü tariften çözülebilirliği:

- **Soru 2:** tek pil + tek direnç; iç direnç seri. Belirsizlik yok.
- **Soru 3:** batarya, LDR ve 10 kΩ tek gözde seri; voltmetre sabit direncin uçlarında, ideal. Kök metni tek başına topolojiyi
  belirliyor; şekil tarifi aynı şeyi söylüyor.
- **Soru 4:** 6.0 Ω, (12 Ω ∥ 4.0 Ω) ile seri; bataryanın iç direnci ihmal. Tek topoloji.
- **Soru 5 (d):** iki eş tel birbirine paralel, birlikte bataryanın (iç direnciyle) uçlarına bağlı. Tek topoloji.

Çeldiriciler yeniden hesaplandı: S1 B, C, D cebirsel; S2 A 2.0, C 12, D 14.4 W; S3 A 1.5, B 1.8, C 4.5 V; S4 A 0.50 (aynı zamanda
12 Ω'daki akım), B 1.0, D 2.0 A. Markscheme notları: çap yarıçap alınırsa 0.548 m (0.55 m); iç direnç yok sayılırsa 7.5 W;
ALTERNATIVE yolunda tel başına 4.0² / 4.8 = 3.33 W. Hepsi doğru. Her 1A sorusunda tek doğru seçenek var.

Veri gerçekçiliği: nikrom özdirenci 1.1 × 10⁻⁶ Ω m bilinen aralıkta (≈ 1.0–1.5 × 10⁻⁶ Ω m); 0.20 mm çaplı 0.14 m telin 4.8 Ω
olması bununla tutarlı; parlak ışıkta 2.0 kΩ LDR direnci makul; 6.0 V bataryada 1.2 Ω iç direnç makul.

Kural denetimi: SL etiketi doğru; alternatif akım yok; voltmetre ideal ve açıkça yazılı; tek değişken direnç LDR (izinli);
türev/integral yok; seçenekler aynı birimde ve artan sırada; Soru 5 puanları 2 + 2 + 2 + 3 = 9 ve markscheme madde sayıları
eşleşiyor.

## Bulgular

**KRİTİK:** yok. **ORTA:** yok.

### DÜŞÜK

1. **Soru 2, "A cell of emf 6.0 V".** Tek bir kimyasal pil için 6.0 V alışılmadık (tek pil tipik olarak 1.2–3.7 V). Cevap
   etkilenmiyor. *Öneri:* "A battery of emf 6.0 V and internal resistance 0.50 Ω".

2. **Soru 5 (d), bağlam.** Öğrenci "daha hızlı kesmek" için ikinci teli ekliyor; hesap toplam gücün 6.7 W'a çıktığını ama tel
   başına gücün 4.8 W'tan 3.3 W'a düştüğünü gösteriyor (yani her tel daha soğuk). Soru yalnızca toplam güç öngörüsünü
   değerlendirtiyor, markscheme doğru. İstenirse üçüncü puanın gerekçesine "power in each wire falls to 3.3 W" kabul edilen
   ifade olarak eklenebilir (ALTERNATIVE zaten bu değeri içeriyor).

3. **Soru 5, puan toplamı.** SL etiketli soru 9 puan; biçim profili SL kısa sorularını 4–6 puan olarak gözlemlemiş. Yazım
   standardı 4–9'a izin veriyor; uzman teyidi için kayıt.

4. **Şekiller.** Soru 3, 4 ve 5 (d)'de devre şeması çizilmemiş, yalnızca sözle tarif edilmiş; dosya bunu kendisi not ediyor. Kör
   çözümde eksik bilgi ya da belirsizlik çıkmadı.

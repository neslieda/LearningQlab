# Bağımsız inceleme: D.2 Elektrik ve manyetik alanlar

> Tarih: 2026-10-11. İncelenen dosya: [d2-electric-magnetic-fields-pilot-questions.md](../d2-electric-magnetic-fields-pilot-questions.md).
> Yöntem: önce cevapsız öğrenci kopyası üzerinden kör çözüm (python3; k = 8.99 × 10⁹, e = 1.60 × 10⁻¹⁹ C, m_p = 1.67 × 10⁻²⁷ kg),
> sonra anahtar ile karşılaştırma, sonra kural kontrolü. Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 | qV/d = mg, V ∝ 1/q; 600 × 3/5 = 360 V → B | B | Evet |
| 2 | E = 3000/0.015 = 2.0 × 10⁵ V m⁻¹; F = 2eE = 6.4 × 10⁻¹⁴ N → D | D | Evet |
| 3 | Eksenler x sağa, y üste, z dışarı. X: (−z) × (+x) = −y; Y: (+z) × (−x) = −y. Bileşke sayfanın altına → C | C | Evet |
| 4 | V = k(6.0 − 2.0) × 10⁻⁹ / 0.15 = 239.7 V → A | A | Evet |
| 5(a) | V = kQ/r = 1.498 × 10⁵ V | 1.498 × 10⁵ V | Evet |
| 5(b) | E = kQ/r² = 9.99 × 10⁵ ≈ 1.0 × 10⁶ N C⁻¹ | 1.0 × 10⁶ N C⁻¹ | Evet |
| 5(c) | ΔV = 9.99 × 10⁴ V; v = 4.37 × 10⁶ m s⁻¹ (ΔV = 1.0 × 10⁵ ile 4.38 × 10⁶) | 4.4 × 10⁶ m s⁻¹ | Evet |
| 5(d) | ΔV = 0 → W = qΔV = 0; ya da kuvvet yer değiştirmeye dik | Aynı | Evet |

Çeldirici değerleri yeniden hesaplandı (200, 1000 V; 1.44 × 10⁻¹⁷, 6.4 × 10⁻¹⁷, 3.2 × 10⁻¹⁴ N; 479, 1598, 3196; 5(c) çeldirici yol
5.36 × 10⁶ m s⁻¹) ve eşleşti.

## Yön kontrolü (Soru 3)

B ∝ I × r̂ (r̂ telden noktaya). X solda, akım −z, r̂ = +x: (−z) × (+x) = −y. Y sağda, akım +z, r̂ = −x: (+z) × (−x) = −y. Kavrama
kuralıyla da: içeri akım → saat yönünde çemberler → telin sağında aşağı; dışarı akım → saat yönünün tersine → telin solunda aşağı.
Anahtar ve yazarın vektörel kontrolü doğru. Şekil tarifi geometriyi tek anlamlı belirliyor (X solda, Y sağda, P ortada).

## Bulgular

KRİTİK: yok. ORTA: yok.

1. **DÜŞÜK — Soru 3, İngilizce kök ile "Biçim uyumu" tablosundaki "soru metni şekil olmadan da çözülebilir" ifadesi.** Bu ifade doğru
   değil: İngilizce kökte X'in Y'nin solunda olduğu yazmıyor; bu bilgi yalnızca (Türkçe) şekil tarifinde. X sağda olsaydı cevap B olurdu.
   Şekil tarifiyle soru tek anlamlı, bu yüzden hata değil; ama şekil üretilmeden / çevrilmeden gösterilirse B ile C ayırt edilemez.
   *Öneri:* köke "Wire X is to the left of wire Y." cümlesini eklemek ve tablodaki ifadeyi buna göre düzeltmek.
2. **DÜŞÜK — Soru 4, çeldirici kümesi.** "İşaret yok sayılır **ve** uzaklık olarak 0.30 m alınır" çifte hatası 8.99 × 10⁹ × 8.0 × 10⁻⁹ / 0.30
   = 240 V verir, yani doğru seçeneğe yanlış yoldan ulaşılır. Tek doğru cevap bozulmuyor; yalnızca sorunun ayırt ediciliğini biraz
   düşürür. *Öneri:* yükleri +6.0 nC ve −3.0 nC yapmak (doğru 180 V; çifte hata 270 V) ve çeldiricileri yeniden hesaplamak.
3. **DÜŞÜK — Soru 3 seçenek biçimi.** A tam cümle, B–D kısa ifade (yazar da işaretlemiş). *Öneri:* A'yı "zero" / "there is no resultant
   field" gibi kısa bir ifadeye indirmek ya da uzman görüşüne bırakmak.

## Kontrol edilenler (sorun bulunmadı)

- Müfredat sınırı: manyetik desen yalnızca düz tel; potansiyel sorusunda iki nokta yük (sınır dört); türev / integral yok.
- Düzey: Soru 1 (Millikan), 2 (E = V/d, F = qE), 3 (düz telin alanı) SL; Soru 4 (potansiyel) ve Soru 5 (potansiyel, W = qΔV,
  eşpotansiyel) HL — doğru etiketli.
- Puanlar: 5(a) 2, (b) 2, (c) 3, (d) 2 = 9; ✓ sayıları parça puanlarına eşit; alt parça ≤ 3.
- "Show that": 1.498 × 10⁵ ≈ 1.5 × 10⁵ V; (b) (E = V/r yolu dahil) ve (c) hem tam hem verilen değerle aynı 2 a.b. sonuca gidiyor.
- 5(c): 4.4 × 10⁶ m s⁻¹ ≈ 0.015c, göreli düzeltme gereksiz. 5(b): 1.0 × 10⁶ N C⁻¹ fiziksel olarak makul.
- Seçenekler: sayısal sorularda aynı birim, artan sıra; her soruda tek doğru seçenek.

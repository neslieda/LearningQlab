# Bağımsız inceleme: B.1 Isıl enerji aktarımı

> Tarih: 2026-10-11. İncelenen dosya: [b1-thermal-energy-transfers-pilot-questions.md](../b1-thermal-energy-transfers-pilot-questions.md).
> Yöntem: önce cevapları silinmiş öğrenci kopyası üzerinden kör çözüm (aritmetik `python3` ile), sonra anahtar ve markscheme ile
> karşılaştırma, sonra yazım standardı, müfredat analizi (B.1 satırı) ve biçim profiline göre kural denetimi.
> Bu inceleme uzman onayının yerine geçmez.

## Karşılaştırma tablosu

| Soru | Kör çözüm sonucum | Anahtar | Uyuşuyor mu |
|---|---|---|---|
| 1 (1A) | 180 (90 − T) = 1260 (T − 20) → T = 28.75 °C → **A** | A | Evet |
| 2 (1A) | 2.2 × 1.0 × 8.0 / 0.050 = 352 W → **C** | C | Evet |
| 3 (1A) | T_X = 2T_Y; L ∝ R²T⁴ = 9 × 16 = 144 → **D** | D | Evet |
| 4 (1A) | P = 400m; L = 400 × 300 = 1.2 × 10⁵ J kg⁻¹ → **B** | B | Evet |
| 5 (a) | Q = 0.80 × 4200 × 75 = 2.52 × 10⁵ J; t = 168 s | 168 s | Evet |
| 5 (b) | 1500 × 120 / 2.26 × 10⁶ = 0.0796 kg ≈ 0.080 kg | 0.080 kg | Evet |
| 5 (c) | Verilen enerji moleküller arası potansiyel enerjiyi artırır (bağları koparır); ortalama kinetik enerji, dolayısıyla sıcaklık değişmez | Aynı iki madde | Evet |
| 5 (d) | (1500 × 190 − 2.52 × 10⁵) / 190 = 174 W; (a)'daki 170 s kullanılırsa 1500 × 20 / 190 = 158 W | 170 W; kabul aralığı 160–180 W | Evet |

Çeldiriciler yeniden hesaplandı: S1 B 48.0, C 55, D 72.97; S2 A 0.88, B 3.52, D 1.166 × 10⁴; S3 A 9/16, B 36, C 48;
S4 A 400, C 2.4 × 10⁵, D 4.8 × 10⁵. Hepsi tabloda yazan yanılgıdan çıkıyor. Her soruda tek doğru seçenek var.

Veri gerçekçiliği: alüminyum 900, su 4200 J kg⁻¹ K⁻¹; suyun buharlaşma gizli ısısı 2.26 × 10⁶ J kg⁻¹; buzun ısıl iletkenliği
2.2 W m⁻¹ K⁻¹ — hepsi bilinen değerlerle uyumlu. S4'teki kurgusal malzeme (c = 800 J kg⁻¹ K⁻¹, L = 1.2 × 10⁵ J kg⁻¹) makul.

Kural denetimi: SL etiketi doğru; konveksiyon hesaplanmıyor; türev/integral yok; iletim nicel (izinli); seçenekler aynı birimde ve
artan sırada; Soru 5 parça puanları 2 + 2 + 2 + 2 = 8, markscheme madde sayıları parça puanlarıyla eşleşiyor.

## Bulgular

**KRİTİK:** yok.

### ORTA

1. **Soru 5, kök ile (d) arasında çelişki ("insulated vessel" ↔ çevreye enerji kaybı).** Kökte kap "insulated" deniyor ve (a), (b)
   bu varsayımla çözülüyor; (d) ise aynı düzenekte suyun çevreye enerji aktardığını varsayıyor. Öğrenci için hangi koşulun
   değiştiği belli değil. *Öneri:* (d)'den önceki cümle "In a test, the insulation is removed from the vessel. The time measured
   for the water to reach 100 °C is now 190 s." olsun.

2. **Soru 5 (d), kabul aralığının genişletilmesi (yazarın işaretlediği nokta).** Aralık doğru hesaplanmış: tam değerle 174 W,
   (a)'daki yuvarlanmış 170 s ile 158 W → 160 W. Ancak sonuç, iki yakın büyük sayının farkı olduğu için (a)'daki 168 → 170
   yuvarlaması cevabı yaklaşık %9 değiştiriyor; "Show that" kalıbının amacı (sonraki parçanın verilen değeri güvenle kullanması)
   burada zayıflıyor ve 2 anlamlı basamaklı cevap iki yoldan farklı çıkıyor (170 W ↔ 160 W). Bu bir hata değil, tasarım zayıflığı.
   *Öneri (yeniden hesaplandı):* ısıtıcı gücü 1.4 kW, test süresi 200 s. O zaman (a) t = 2.52 × 10⁵ / 1400 = 180 s (tam;
   "about 180 s"), (b) m = 1400 × 120 / 2.26 × 10⁶ = 0.0743 kg ≈ 0.074 kg, (d) 1400 − 2.52 × 10⁵ / 200 = 140 W ve verilen
   180 s ile 1400 × 20 / 200 = 140 W; iki yol aynı sonucu verir, kabul aralığına gerek kalmaz.

### DÜŞÜK

1. **Soru 5, puan toplamı.** SL etiketli soru 8 puan; biçim profili SL kısa sorularını 4–6 puan olarak gözlemlemiş (HL 4–9).
   Yazım standardı 4–9'a izin veriyor; uzman teyidi için kayıt.

2. **Soru 5 (b), açık varsayım.** Verilen enerjinin tamamının buharlaşmaya gittiği varsayımı kökteki "insulated" ifadesine
   dayanıyor; ORTA-1 düzeltmesi yapılırken (b)'nin yalıtımlı durumda kaldığı korunmalı.

3. **Soru 1 ve 2, yuvarlama.** 28.75 → 29 °C ve 352 → 350 W; dosya bunu "Biçim uyumu"nda kendisi not ediyor. Seçenekler birbirinden
   yeterince uzak, tek doğru cevap etkilenmiyor.

# Blueprint biçim referansı: IB Diploma Physics (ilk sınav 2025)

> **Durum: TASLAK — uzman doğrulaması bekliyor.** Tarih: 2026-10-11.
> **Kaynak:** proje sahibinin sağladığı tek bir örnek (specimen) kâğıt seti ve markscheme'leri (HL ve SL; Paper 1A, 1B, 2).
> Belge **yalnızca yapı için** incelendi. Bu dosya hiçbir soru metni, sorudan alınmış ifade, sayısal veri, senaryo ya da şekil tarifi
> ve tek bir soruya karşılık gelen satır içermez; yalnızca toplamlar (sayım, yüzde, aralık) ve bizim tanımladığımız soyut kategori
> adları vardır. Soru bazındaki çalışma notları geçici dizinde tutuldu ve iş bitiminde silindi.
> ⚖️ Kaynak belge sınav kurumunun telif işaretini taşıyor; yapısal analizin kapsamı hukuki teyide tabidir ([DECISIONS.md](../DECISIONS.md) R-01).
>
> **Yöntem:** Paper 1A'da her soru, Paper 1B ve Paper 2'de her en küçük alt parça elle sınıflandırıldı (tek okuyucu, tek geçiş);
> sayımlar betikle toplandı. Komut sözcüğü → AO eşlemesi [müfredat analizinden](../syllabus/dp-physics-2025-analysis.md) alındı.
> Çoktan seçmelide AO, adım sayısı, çeldirici temeli gibi boyutlar **yargıdır** (bkz. §9). Yüzdeler küçük örneklemlere dayanır;
> eğilim olarak okunmalı, kural olarak değil.

## 1. Örneklem

| Bölüm | HL | SL | HL–SL ilişkisi |
|---|---|---|---|
| Paper 1A | 40 soru, 40 puan | 25 soru, 25 puan | SL sorularının 24'ü HL kâğıdında da var; 1 soru yalnızca SL'de, 16 soru yalnızca HL'de |
| Paper 1B | 2 soru, 12 alt parça, 20 puan | aynı | İki düzeyde birebir aynı |
| Paper 2 | 10 soru, 45 alt parça, 90 puan | 7 soru, 25 alt parça, 50 puan | SL'nin 25 alt parçasının tamamı HL kâğıdında da var |

**Sonuç 1 — düzey bir soru özelliği değil, bir kullanım kümesidir.** Aynı soru (ya da aynı sorunun kısaltılmış hâli) iki düzeyde
kullanılıyor. HL kâğıdındaki bir soru, SL sürümünde ek HL içeriği ölçen parçaları çıkarılarak yer alabiliyor (gözlem: HL'de olup
SL'de olmayan 20 Paper 2 parçasının 13'ü ek HL içeriği, 7'si SL içeriği). Blueprint'te tek `level` alanı bunu taşıyamaz.

## 2. Paper 1A — dağılımlar

Tüm sorular 1 puan, komut sözcüğü yok. Yüzdeler soru sayısı üzerinden.

| Boyut | Değer | HL (n=40) | SL (n=25) |
|---|---|---|---|
| İçerik düzeyi | `sl_core` / `ahl` | %60 / %40 | %100 / — |
| AO (yargı) | AO1 / AO2 / AO3 | %15 / %60 / %25 | %16 / %60 / %24 |
| Seçenek türü | `numeric_with_unit` | %22 | %28 |
| | `algebraic_expression` (sembolik ifade, kat, kesir) | %28 | %20 |
| | `ratio` (birimsiz sayı) | %10 | %20 |
| | `statement` (cümle / cümle tamamlama) | %20 | %12 |
| | `word_phrase` (terim, sıra, yön adı) | %10 | %12 |
| | `figure_choice` (grafik ya da diyagram seçenekleri) | %10 | %8 |
| Akıl yürütme adımı | 1 / 2 / 3+ | %32 / %60 / %8 | %44 / %48 / %8 |
| Verilen büyüklük sayısı | 0 / 1–2 / 3+ | %32 / %48 / %20 | %20 / %64 / %16 |
| Veri kitapçığı ilişkisi | 0 / 1 / 2 | %30 / %60 / %10 | %32 / %56 / %12 |
| Uyaran | yok | %55 | %56 |
| | `schematic` | %22 | %20 |
| | `graph` | %12 | %12 |
| | `circuit` | %5 | %8 |
| | `field_diagram` / `energy_level_diagram` | %2 / %2 | — / %4 |
| Bağlam | `bare_abstract` | %60 | %64 |
| | `astronomy_space` | %18 | %16 |
| | `everyday_object` | %10 | %12 |
| | `laboratory` | %10 | %4 |
| | `technology_engineering` | %2 | %4 |
| | `natural_phenomenon` | 0 | 0 |
| Çeldirici temeli (baskın) | `conceptual` | %32 | %32 |
| | `factor_slip` (kat, üs, karekök, 2π hatası) | %30 | %28 |
| | `wrong_formula` | %15 | %20 |
| | `sign_direction` (işaret, yön, eğilim yönü) | %15 | %16 |
| | `inverse_swap` (ters oran, rol değişimi) | %5 | 0 |
| | `unit_conversion` | %2 | %4 |
| Kök biçimi | soru cümlesi / tamamlanacak cümle | %85 / %15 | %92 / %8 |
| Seçenek düzeni | `single_value` | %80 | %80 |
| | `figure_options` | %10 | %8 |
| | `two_column_table` | %8 | %8 |
| | `roman_statements` (I–II–III birleşimleri) | %2 | %4 |
| Tema payı | A / B / C / D / E | %22 / %20 / %15 / %22 / %20 | %24 / %24 / %16 / %16 / %20 |

Ek gözlemler (toplam olarak):

- **Düğüm kapsamı:** HL'de 24 düğümün 21'i, SL'de erişilebilir 19 düğümün 16'sı en az bir soruyla ölçülüyor; düğüm başına en çok 4 soru.
  İki düğüme yayılan soru: HL 4, SL 3.
- **AO × adım (HL):** AO1 sorularının tamamı tek adım; AO2: 7 / 16 / 1 (1 / 2 / 3+ adım); AO3: 0 / 8 / 2.
- **Seçenek türü × çeldirici temeli:** `statement` ve `word_phrase` → neredeyse hep `conceptual`; `numeric_with_unit` → `wrong_formula`,
  `factor_slip`, `sign_direction`; `algebraic_expression` ve `ratio` → ağırlıkla `factor_slip`; `figure_choice` → `sign_direction` (eğilimin yönü).
- **Sembolik sorular yaygın:** HL'de soruların yaklaşık %38'inde cevap sembolik bir ifade ya da oran; çözüm orantı akıl yürütmesine dayanıyor.
- **2×2 birleşim tasarımı:** HL'de yaklaşık 6–7 soruda dört seçenek, iki ikili özelliğin (ör. iki ayrı yön ya da iki ayrı değer) dört
  birleşimidir. İki sütunlu tablo biçimindeki seçenekler bunun bir alt türüdür.
- **Fazlalık veri** (çözüm için gerekmeyen büyüklük) 41 farklı sorudan 1'inde var; olumsuz kök gözlenmedi.
- Biçim profilinin "tablo biçiminde seçenek doğrulanamadı" maddesi bu okumayla **doğrulandı**: iki sütunlu tablo seçenekleri var.

## 3. Paper 1B — dağılımlar (HL = SL; 12 alt parça, 20 puan)

| Boyut | Dağılım (parça sayısı) |
|---|---|
| Komut sözcüğü | calculate 3 · state 2 · outline 2 · suggest 2 · describe 1 · determine 1 · discuss 1 |
| Puan | 1 puan: 5 · 2 puan: 6 · 3 puan: 1 |
| AO (puan payı) | AO1 %10 · AO2 %50 · AO3 %40 |
| Cevap türü | `explanation` 5 · `numeric_unitless` (kesirli/yüzde belirsizlik, üs) 3 · `numeric_with_unit` 1 · `value_from_graph` 1 · `unit` 1 · `word_phrase` 1 |
| Adım | 1: 5 · 2: 6 · 3+: 1 |
| Veri kitapçığı ilişkisi | 0: 9 · 1: 3 |
| Parçanın doğrudan kullandığı uyaran | yok 6 · `graph` 3 · `data_table` 2 · `schematic` 1 |
| Öğrencinin uyaran üzerine çizdiği parça | 1 (en uygun doğru) |
| Parçalar arası bağımlılık | hepsi bağımsız |
| Rol | `calculate` 4 · `evaluate` 4 · `recall` 2 · `explain` 2 |
| Markscheme bölünmesi | `method_answer` 4 · `single_point` 4 · `alternatives` 2 · `linked_statements` 1 · `independent_statements` 1 |
| Bağlam | tamamı `laboratory` |

- Soru büyüklüğü 8–12 puan; alt parça sayısı 5–7; üst düzey harf sayısı 2–4.
- Her soruda düzenek şeması var; veri tablosu ve/veya ölçekli grafik (belirsizlik çubuklu) eşlik ediyor.
- **Ölçülen şey müfredat düğümü değil, deney becerisidir.** Bağlamın fiziği bir soruda müfredat düğümlerine yaslanıyor, diğerinde
  müfredat içeriğinin dışından seçilmiş ve gereken kuramsal ilişki soruda verilmiş. Yani Paper 1B Blueprint'i için `syllabus_nodes`
  boş olabilmeli; zorunlu olan beceri listesidir.
- Gözlenen beceri türleri (bizim adlandırmamızla): `uncertainty_combination`, `uncertainty_propagation`, `measurement_technique`,
  `instrument_choice`, `linearity_judgement`, `linearised_best_fit_gradient`, `unit_of_constant`, `unit_consistency_exponents`,
  `significant_figures_outliers`, `systematic_error_source`, `model_assumption_validity`.

## 4. Paper 2 — dağılımlar

### 4.1 Alt parça düzeyi

| Boyut | Değer | HL (45 parça, 90 puan) | SL (25 parça, 50 puan) |
|---|---|---|---|
| İçerik düzeyi (puan payı) | `sl_core` / `ahl` | %73 / %27 | %100 / — |
| Puan (parça sayısı) | 1 / 2 / 3 | 13 / 19 / 13 | 7 / 11 / 7 |
| AO (puan payı) | AO1 / AO2 / AO3 | %17 / %32 / %51 | %18 / %32 / %50 |
| Komut sözcüğü (parça) | show | 6 | 5 |
| | calculate | 6 | 3 |
| | outline | 6 | 3 |
| | state | 5 | 2 |
| | determine | 4 | 3 |
| | explain | 4 | 1 |
| | draw | 3 | 3 |
| | discuss / deduce / estimate / sketch | 2 / 2 / 2 / 2 | 0 / 1 / 1 / 1 |
| | suggest / complete / identify | 1 / 1 / 1 | 1 / 1 / 0 |
| Cevap türü (puan payı) | `numeric_with_unit` | %24 | %38 |
| | `explanation` | %20 | %16 |
| | `judgement_justified` (gerekçeli karar / çıkarım) | %10 | %4 |
| | `derivation_algebraic` (verilen ifadeye ulaşma) | %9 | %6 |
| | `derivation_numeric` (verilen yaklaşık değere ulaşma) | %8 | %14 |
| | `drawing_on_diagram` | %8 | %14 |
| | `word_phrase` | %6 | %4 |
| | `numeric_unitless` | %4 | 0 |
| | `symbolic_equation` (ör. çekirdek denklemi) | %4 | %4 |
| | `extended_evaluation` | %3 | 0 |
| | `graph_sketch` / `algebraic_expression` | %2 / %1 | 0 / 0 |
| Adım (parça) | 1 / 2 / 3+ | 15 / 16 / 14 | 9 / 8 / 8 |
| Verilen büyüklük (parça) | 0 / 1–2 / 3+ | 26 / 13 / 6 | 13 / 7 / 5 |
| Veri kitapçığı ilişkisi (parça) | 0 / 1 / 2 | 23 / 17 / 5 | 13 / 8 / 4 |
| Parçanın doğrudan kullandığı uyaran | yok | 30 | 17 |
| | `schematic` / `graph` / `field_diagram` | 6 / 5 / 2 | 3 / 2 / 2 |
| | `picture` (ölçekli, üzerinden ölçüm alınan) / `data_table` | 1 / 1 | 1 / 0 |
| Öğrencinin uyaran üzerine çizdiği parça | | 5 | 4 |
| Bağımlılık (parça) | `independent` | 35 | 20 |
| | `uses_previous_answer` | 5 | 2 |
| | `uses_show_that_result` | 4 | 3 |
| | `uses_earlier_parts_data` (sentez) | 1 | 0 |
| Rol (puan payı) | `calculate` | %29 | %38 |
| | `explain` | %19 | %12 |
| | `show_that` | %17 | %20 |
| | `evaluate` | %14 | %8 |
| | `recall` | %11 | %8 |
| | `draw` | %10 | %14 |
| Bağlam (parça; soru bağlamından) | `laboratory` / `technology_engineering` / `astronomy_space` | 13 / 13 / 11 | 12 / 3 / 6 |
| | `bare_abstract` / `everyday_object` / `natural_phenomenon` | 6 / 2 / 0 | 2 / 2 / 0 |
| Tema payı (puan, birincil düğüme göre) | A / B / C / D / E | %28 / %10 / %9 / %30 / %23 | %22 / %12 / %10 / %34 / %22 |
| İki düğüme yayılan parça | | 12 | 9 |

Soru düzeyinde: HL'de 10 sorunun 9'unda, SL'de 7 sorunun 6'sında en az bir uyaran var; parça düzeyinde uyaran gerektirenler yaklaşık üçte bir.

### 4.2 Markscheme bölünmesi (parça sayısı)

| Kalıp | Anlamı | HL P2 | SL P2 |
|---|---|---|---|
| `method_answer` | yöntem/yerine koyma puan(lar)ı + sonuç puanı | 13 | 10 |
| `independent_statements` | birbirinden bağımsız ifadeler ya da özellikler | 8 | 5 |
| `single_point` | tek madde (yalnızca cevap) | 7 | 4 |
| `linked_statements` | sıralı akıl yürütme; sonraki madde öncekine bağlı | 6 | 2 |
| `single_point_and` | tek puan için iki öğe birlikte gerekli | 3 | 3 |
| `alternatives` | OR ile ayrılmış eşdeğer cevaplar | 3 | 0 |
| `method_steps` | yalnızca adım puanları (sonuç soruda verilmiş) | 3 | 1 |
| `alternative_routes` | iki bağımsız tam çözüm yolu | 1 | 0 |
| `level_bands` | madde değil, düzey tanımlayıcıları (3/2/1/0) | 1 | 0 |

- `numeric_with_unit` parçalarının HL'de 9'undan 8'i `method_answer`; 1 puanlık hesaplar `single_point`.
- Açıklama parçalarında en yaygın kalıp `linked_statements`; "kabul edilen herhangi bir uygun örnek" türü açık uçlu maddeler de var.
- Notlarda görülen ek kurallar (HL P2 + 1B toplamı): ECF izni 3, kabul aralığı/tolerans 3, belirli anlamlı basamak şartı 2,
  toplam puandan fazla madde ("max") 1.

### 4.3 Kısa soruların tipik bileşimi (HL 8 soru, 4–9 puan; SL 6 soru, 4–6 puan)

- **Parça sayısı** 2–4 (HL ortanca 3–4, SL 2–3); üst düzey harf sayısı 2–4; alt bölme (i, ii) en çok bir harfin altında.
- **Açılış parçası** çoğunlukla 1 puan (HL 8'de 5): bir olguyu söyleme, şekle bir ok çizme, tek adımlı hesap ya da tek satırlık
  "show that". Azınlıkta soru doğrudan 2–3 puanlık açıklama ya da hesapla açılır.
- **Çekirdek** hemen her soruda bir adet 3 puanlık parçadır (HL 8'de 7): çok adımlı hesap ya da gerekçeli çıkarım.
- **Kapanış** üç biçimde: çekirdek hesabın kendisi (3), nitel açıklama (2), değerlendirme/çıkarım (2), çizim (1) — HL sayıları.
- **AO3 payı neredeyse sabit:** HL'de her kısa soruda komut sözcüğüne göre 2–3 puan AO3; SL'de bir soru hiç AO3 parçası taşımıyor.
- **Düğüm sayısı:** kısa soruların yarısı tek düğüm, yarısı iki düğüm; ikinci düğüm çoğunlukla yardımcı bir ilişki sağlar ve
  3 soruda farklı temadandır.
- **Zincir:** 8 kısa sorunun 3'ünde parçalar arası bağımlılık var; "show that" değeri ya da önceki sayısal sonuç sonraki parçada kullanılır.
- Genelleştirilmiş kalıp: `kısa açılış (1–2 puan: recall / draw / show_that / explain)` → `çekirdek (3 puan: calculate ya da gerekçeli çıkarım)`
  → isteğe bağlı `kapanış (1–3 puan: explain / evaluate / draw)`. Azınlık kalıp: çekirdek hesapla açılıp değerlendirme parçalarıyla kapanma.

### 4.4 20 puanlık soruların tipik bileşimi (HL 2, SL 1)

- **9–10 alt parça**, 4–5 üst düzey harf; her harfin altında en çok dört alt bölme.
- **Puan deseni:** 1 puanlık 1–2 parça, 2 puanlık 5–6 parça, 3 puanlık 2–3 parça. 3 puanı geçen parça yok.
- **AO3 payı:** 20 puanın 11–12'si.
- **"Show that" yoğun:** soru başına 2–3 türetme parçası (ifadeye ya da yaklaşık değere ulaşma); 1–2 çizim parçası.
- **Yayılım iki ayrı biçimde gözlendi:** (i) tek bir deney bağlamı üzerinde derinleşen soru: 2 düğüm, 2 tema;
  (ii) şemsiye bir tema altında alt bağlam değiştiren sentez sorusu: 5–6 düğüm, 4 tema. İkinci biçim yalnızca HL'de var.
- **Soru ortasında yeni bilgi:** her iki biçimde de bağlam metni parçaların arasına serpiştirilir (yeni veri, yeni şekil, yeni alt bağlam).
- **Kapanış:** gerekçeli çıkarım (2 puan) ya da soru boyunca verilen verilere dayanan karşılaştırmalı tartışma (3 puan, düzey tanımlayıcılı puanlama).
- **Zincir:** soru başına 2 bağımlı parça; diğerleri bağımsız çözülebilir.

## 5. Çapraz tablolar (Paper 1B + HL Paper 2 birlikte; 57 alt parça)

### 5.1 Komut sözcüğü × puan

| Komut sözcüğü | 1 puan | 2 puan | 3 puan | Toplam |
|---|---|---|---|---|
| calculate | 2 | 5 | 2 | 9 |
| outline | 4 | 3 | 1 | 8 |
| state | 6 | 1 | 0 | 7 |
| show | 2 | 1 | 3 | 6 |
| determine | 0 | 2 | 3 | 5 |
| explain | 2 | 2 | 0 | 4 |
| draw | 1 | 2 | 0 | 3 |
| discuss | 0 | 1 | 2 | 3 |
| suggest | 1 | 2 | 0 | 3 |
| deduce | 0 | 1 | 1 | 2 |
| estimate | 0 | 0 | 2 | 2 |
| sketch | 0 | 2 | 0 | 2 |
| describe / complete / identify | 0 | 1 / 1 / 1 | 0 | 3 |

### 5.2 Komut sözcüğü × cevap türü

| Komut sözcüğü | Gözlenen cevap türleri (parça sayısı) |
|---|---|
| calculate | `numeric_with_unit` 5 · `numeric_unitless` 4 |
| determine | `numeric_with_unit` 3 · `judgement_justified` 1 · `value_from_graph` 1 |
| estimate | `numeric_with_unit` 1 · `numeric_unitless` 1 |
| show | `derivation_algebraic` 3 · `derivation_numeric` 3 |
| state | `word_phrase` 3 · `algebraic_expression` 1 · `symbolic_equation` 1 · `numeric_with_unit` 1 · `unit` 1 |
| outline | `explanation` 8 |
| explain | `explanation` 2 · `derivation_algebraic` 1 · `judgement_justified` 1 |
| describe | `explanation` 1 |
| suggest | `explanation` 2 · `word_phrase` 1 |
| discuss | `explanation` 2 · `extended_evaluation` 1 |
| deduce | `judgement_justified` 2 |
| draw | `drawing_on_diagram` 3 |
| sketch | `drawing_on_diagram` 1 · `graph_sketch` 1 |
| complete | `symbolic_equation` 1 |
| identify | `word_phrase` 1 |

### 5.3 Puan × adım sayısı

| Puan | 1 adım | 2 adım | 3+ adım |
|---|---|---|---|
| 1 | 15 | 3 | 0 |
| 2 | 5 | 19 | 1 |
| 3 | 0 | 0 | 14 |

Puan ile adım sayısı neredeyse aynı şeyi ölçüyor (adım sayısı markscheme maddelerine bakılarak yargılandığı için kısmen döngüsel; bkz. §9).

### 5.4 Bölümlere göre AO payı ve uyaran payı

| Bölüm | AO1 | AO2 | AO3 | Uyaran gerektiren birim |
|---|---|---|---|---|
| Paper 1A HL / SL (soru) | %15 / %16 | %60 / %60 | %25 / %24 | %45 / %44 |
| Paper 1B (puan) | %10 | %50 | %40 | parçaların %50'si doğrudan; soruların tamamı |
| Paper 1 toplam HL (60 puan) | %13 | %57 | %30 | — |
| Paper 2 HL / SL (puan) | %17 / %18 | %32 / %32 | %51 / %50 | parçaların %33 / %32'si; soruların 9/10 ve 6/7'si |

Paper 2'de AO3 payı ders rehberindeki "yaklaşık yarı" hedefiyle örtüşüyor. Paper 1'de bizim yargımızla AO3 %30 çıkıyor; fark
büyük olasılıkla çoktan seçmelide AO sınırını nereye çektiğimizden kaynaklanıyor (bkz. §9).

### 5.5 Tema başına puan payı

| Tema | 1A HL | 1A SL | P2 HL | P2 SL | Öğretim saati payı (HL / SL) |
|---|---|---|---|---|---|
| A | %22 | %24 | %28 | %22 | %23 / %25 |
| B | %20 | %24 | %10 | %12 | %18 / %22 |
| C | %15 | %16 | %9 | %10 | %16 / %15 |
| D | %22 | %16 | %30 | %34 | %21 / %17 |
| E | %20 | %20 | %23 | %22 | %22 / %21 |

Paper 1A öğretim saatiyle orantılı; Paper 2'de soru sayısı az olduğu için dağılım kaba (B ve C düşük, D yüksek). Paper 1B'de tema payı tanımsız.

## 6. Önerilen Blueprint biçimi

Tüm alanlar kapalı liste ya da kısa yapılandırılmış değerdir; serbest metin yoktur (üretim girdisinin denetlenebilir kalması için).
Alan adlarında sınav kurumu adı yoktur; programa özgü değerler veridir.

### 6.1 Soru düzeyi alanlar

| Alan | Tür | İzinli değerler | 1A | 1B | P2 |
|---|---|---|---|---|---|
| `schema_version` | string | `"2.0"` | Z | Z | Z |
| `program`, `subject` | enum | program kaydından | Z | Z | Z |
| `exam_section` | enum | `paper_1a` · `paper_1b` · `paper_2` | Z | Z | Z |
| `question_class` | enum | `mcq` · `data_based` · `short_structured` · `long_structured` | Z | Z | Z |
| `levels` | enum[] | `SL` · `HL` (kullanılabileceği kâğıtlar) | Z | Z | Z |
| `level_content` | enum | `sl_core` · `ahl` (parçalardan türetilir; en yükseği) | Z | Z | Z |
| `total_marks` | int | parçaların toplamı | Z (=1) | Z | Z |
| `syllabus_nodes` | string[] | düğüm kodları; ilki birincil | Z (1–2) | S (0–2) | Z (1–6) |
| `experimental_skills` | enum[] | §3'teki liste + `gradient_uncertainty`, `variable_identification`, `improvement_suggestion` | — | Z | S |
| `context.type` | enum | `bare_abstract` · `laboratory` · `everyday_object` · `technology_engineering` · `astronomy_space` · `natural_phenomenon` | Z | Z (=`laboratory`) | Z |
| `context.familiarity` | enum | `syllabus_context` · `unfamiliar_theory_given` | — | Z | S |
| `context.constraints` | enum[] | düğümün "kapsam dışı" maddelerinden | Z | S | Z |
| `stimuli[]` | nesne[] | aşağıda | S | Z (≥2) | S |
| `parts[]` | nesne[] | aşağıda | Z (1 öğe) | Z | Z |
| `mcq` | nesne | aşağıda | Z | — | — |
| `difficulty` | int 1–5 | uzman atar; bu analizden türetilemedi | Z | Z | Z |
| `format_profile_version` | string | biçim profili sürümü | Z | Z | Z |

Z = zorunlu, S = seçimlik, — = kullanılmaz.

**`stimuli[]` öğesi:** `id` · `type` (`schematic` · `graph_scaled` · `graph_sketch_axes` · `data_table` · `data_list` · `scaled_picture` ·
`circuit` · `field_diagram` · `ray_wavefront_diagram` · `energy_level_diagram` · `spacetime_diagram` · `classification_diagram`) ·
`template` (şablon kimliği) · `use` (`read_only` · `read_values` · `student_annotates`) · `has_uncertainty_bars` (bool, yalnızca grafik).

### 6.2 Parça düzeyi alanlar (`parts[]`)

| Alan | Tür | İzinli değerler | 1A | 1B | P2 |
|---|---|---|---|---|---|
| `label` | string | `a`, `b.i` …; 1A'da `""` | Z | Z | Z |
| `command_term` | enum | `state` · `draw` · `annotate` · `calculate` · `describe` · `estimate` · `outline` · `analyse` · `determine` · `discuss` · `explain` · `predict` · `show` · `sketch` · `suggest` · `deduce` · `identify` · `complete` | — | Z | Z |
| `assessment_objective` | enum | `AO1` · `AO2` · `AO3` (komut sözcüğünden türetilir; 1A'da elle) | Z | Z | Z |
| `marks` | int | 1–3 (1A'da 1) | Z | Z | Z |
| `answer_type` | enum | §6.4 | Z | Z | Z |
| `role` | enum | `recall` · `explain` · `calculate` · `show_that` · `draw` · `evaluate` | — | Z | Z |
| `reasoning_steps` | int | 1 · 2 · 3 (3 = "3 ve üzeri") | Z | Z | Z |
| `syllabus_node` | string | sorunun `syllabus_nodes` listesinden biri | — | S | Z |
| `secondary_node` | string | isteğe bağlı ikinci düğüm | S | S | S |
| `level_content` | enum | `sl_core` · `ahl` | Z | Z | Z |
| `skills` | enum[] | düğüme bağlı beceri sözlüğünden (ayrıca tanımlanmalı) | Z | S | Z |
| `givens.count` | int | 0–8 | Z | Z | Z |
| `givens.form` | enum | `none` · `numeric` · `symbolic` · `from_stimulus` · `data_list` | Z | Z | Z |
| `booklet_relations` | string[] | veri kitapçığı ilişki kimlikleri (0–2) | Z | Z | Z |
| `stimulus_refs` | string[] | `stimuli[].id` | S | S | S |
| `depends_on` | nesne | `{ "part": label, "kind": uses_show_that_result · uses_previous_answer · uses_earlier_parts_data }` | — | S | S |
| `show_that_target` | enum | `approximate_value` · `expression` · `inequality` | — | S | S |
| `new_information` | bool | parça öncesinde yeni bağlam/veri veriliyor mu | — | S | S |
| `marking_pattern` | enum | §4.2'deki dokuz değer | — | Z | Z |
| `verification` | enum | `formula_chain` · `not_code_verifiable` | Z | Z | Z |

### 6.3 Çoktan seçmeli bloğu (`mcq`)

| Alan | İzinli değerler |
|---|---|
| `stem_form` | `question` · `incomplete_sentence` |
| `option_layout` | `single_value` · `two_column_table` · `roman_statements` · `figure_options` |
| `data_form` | `numeric` · `symbolic` · `none` |
| `distractor_plan` | tam 3 öğe; her biri `conceptual` · `factor_slip` · `wrong_formula` · `sign_direction` · `inverse_swap` · `unit_conversion` |
| `combination_design` | bool — dört seçenek iki ikili özelliğin birleşimi mi |
| `extraneous_data` | bool (varsayılan `false`) |

### 6.4 `answer_type` değerleri

Çoktan seçmeli (seçenek türü): `numeric_with_unit` · `ratio` · `algebraic_expression` · `word_phrase` · `statement` · `figure_choice`.

Yapılandırılmış: `numeric_with_unit` · `numeric_unitless` · `value_from_graph` · `unit` · `algebraic_expression` · `symbolic_equation` ·
`word_phrase` · `explanation` · `judgement_justified` · `extended_evaluation` · `derivation_algebraic` · `derivation_numeric` ·
`drawing_on_diagram` · `graph_sketch`.

### 6.5 Doğrulama kuralları

Sütun "gözlenen" bu örnek setten; "önerilen" kural, müfredat analizindeki komut sözcüğü tanımlarıyla genişletilmiş hâlidir ve uzman onayı ister.

| Komut sözcüğü | Gözlenen puan | Önerilen puan | İzinli cevap türleri | İzinli markscheme kalıpları |
|---|---|---|---|---|
| state | 1–2 | 1–2 | `word_phrase`, `unit`, `numeric_with_unit`, `algebraic_expression`, `symbolic_equation` | `single_point`, `single_point_and`, `alternatives`, `independent_statements` |
| identify, complete | 2 | 1–2 | `word_phrase`, `symbolic_equation` | `single_point`, `independent_statements` |
| draw, annotate | 1–2 | 1–2 | `drawing_on_diagram` | `single_point`, `independent_statements` |
| sketch | 2 | 2–3 | `graph_sketch`, `drawing_on_diagram` | `independent_statements`, `method_answer` |
| calculate | 1–3 | 1–3 | `numeric_with_unit`, `numeric_unitless` | 1 puan: `single_point`; 2–3 puan: `method_answer` |
| estimate | 3 | 2–3 | `numeric_with_unit`, `numeric_unitless` | `method_answer`, `alternative_routes` |
| determine | 2–3 | 2–3 | `numeric_with_unit`, `numeric_unitless`, `value_from_graph`, `judgement_justified` | `method_answer`, `linked_statements` |
| show | 1–3 | 1–3 | `derivation_algebraic`, `derivation_numeric` | `method_steps`, `method_answer`, `single_point_and` |
| outline, describe | 1–3 | 1–3 | `explanation` | `single_point`, `alternatives`, `independent_statements`, `linked_statements` |
| explain | 1–2 | 1–3 | `explanation`, `judgement_justified`, `derivation_algebraic` | aynı + `method_answer` |
| suggest, predict | 1–2 | 1–2 | `explanation`, `word_phrase` | `single_point`, `alternatives`, `independent_statements` |
| deduce | 2–3 | 2–3 | `judgement_justified` | `linked_statements`, `method_answer` |
| discuss, analyse | 2–3 | 2–3 | `explanation`, `extended_evaluation` | `independent_statements`, `linked_statements`, `level_bands` |

Genel kurallar:

1. `marks` ∈ {1, 2, 3}; Paper 1A'da tam 1.
2. `total_marks`: `short_structured` 4–9 (SL kullanımında 4–6 gözlendi), `long_structured` tam 20, `data_based` 8–12 ve iki soru toplamı 20.
3. Parça sayısı: `short_structured` 2–4, `long_structured` 8–11, `data_based` 4–8.
4. `reasoning_steps` ≥ `marks` − 1 ve `marks` = 3 ise `reasoning_steps` = 3; `marks` = 1 ise `reasoning_steps` ≤ 2.
5. `long_structured` puan deseni: 1 puanlık en çok 3, 3 puanlık en çok 4 parça; en az bir `show_that` ve en az bir `evaluate` rolü.
6. `short_structured`: bir adet 3 puanlık parça ve en az 2 puan AO3 beklenir; eksikse hata değil, uyarı üretilir.
7. AO3 payı: `long_structured` için puanın %45–65'i; Paper 2 havuzu genelinde yaklaşık yarı.
8. `depends_on.kind` = `uses_show_that_result` ise hedef parçanın `command_term` = `show` ve `show_that_target` dolu olmalı.
9. `answer_type` ∈ {`drawing_on_diagram`, `graph_sketch`, `value_from_graph`} ise `stimulus_refs` boş olamaz; çizim türlerinde ilgili
   uyaranın `use` değeri `student_annotates` olmalı.
10. `levels` `SL` içeriyorsa hiçbir parçanın `level_content` değeri `ahl` olamaz. (HL sorusunun SL türevi, `ahl` parçaları çıkarılmış ayrı
    bir Blueprint'tir; türev ilişkisi kayıtta tutulur.)
11. `exam_section` = `paper_1b` ise `experimental_skills` en az 3 farklı beceri; en az bir `graph_scaled` ya da `data_table` uyaranı;
    `syllabus_nodes` boşsa `context.familiarity` = `unfamiliar_theory_given` olmalı.
12. Paper 1A: `reasoning_steps` ≤ 3 (3 adım uyarı verir), `booklet_relations` ≤ 2, `distractor_plan` tam 3 öğe;
    `option_layout` = `figure_options` ise `answer_type` = `figure_choice`; `answer_type` ∈ {`statement`, `word_phrase`} ise çeldiriciler
    `conceptual` ya da `sign_direction`.
13. `verification` = `formula_chain` zorunlu: `numeric_with_unit`, `numeric_unitless`, `ratio`, `derivation_numeric`, `value_from_graph`
    (sayısal cevap LLM çıktısından alınmaz). Diğer türler `not_code_verifiable` olabilir ve inceleme kuralı sıkılaşır.
14. `marking_pattern` = `level_bands` yalnızca `discuss`/`analyse` ve 3 puanlık parçada.

## 7. Mevcut taslakla karşılaştırma ([DATA_ARCHITECTURE.md](../DATA_ARCHITECTURE.md) §5)

| Mevcut alan | Durum | Öneri ve gerekçe |
|---|---|---|
| `level: "HL"` | Değişmeli | `levels[]` + `level_content`. Sorular iki düzeyde ortak kullanılıyor; içerik düzeyi parça bazında değişiyor (§1) |
| `exam_section` | Kalır | `question_class` eklenir: kısa / uzun / veri temelli / çoktan seçmeli ayrımı doğrulama kurallarını belirliyor |
| `syllabus_nodes` | Kalır, genişler | Parça düzeyinde `syllabus_node` gerekir (uzun soru 6 düğüme yayılabiliyor); Paper 1B'de boş olabilmeli |
| `skills` | Kalır, eksik | Serbest dizgi gibi duruyor; kapalı beceri sözlüğü tanımlanmalı. Paper 1B için ayrı `experimental_skills` gerekli |
| `structure[]` → `parts[]` | Genişlemeli | Eksikler: `assessment_objective`, `role`, parça bazlı `reasoning_steps`, `depends_on`, `show_that_target`, `marking_pattern`, `givens`, `booklet_relations`, `stimulus_refs`, `new_information`, `level_content`, `verification` |
| `answer_type` (4 değer) | Değişmeli | `numeric` / `short_text` / `extended` / `drawing` ayrımı fazla kaba: türetme, gerekçeli karar, birim, sembolik denklem, grafikten değer ve çoktan seçmeli seçenek türleri ayırt edilemiyor (§6.4). `extended` adı yanıltıcı; hiçbir parça 3 puanı geçmiyor |
| `difficulty` | Kalır, tanımsız | Örnek kâğıttan gözlenemez; ölçeğin anlamı (ve adım sayısı/AO ile ilişkisi) uzmanla tanımlanmalı |
| `reasoning_steps` (soru düzeyi) | Gereksiz | Parça düzeyine taşınır; soru düzeyinde toplam türetilebilir |
| `context_constraints` | Kalır | `context` nesnesine girer; `context.type` ve `context.familiarity` eklenir |
| `needs_figure`, `figure_template` | Değişmeli | Tek boole ve tek şablon yetmiyor: bir soruda birden çok uyaran, farklı türler ve "öğrenci üzerine çizer" kullanımı var → `stimuli[]` |
| `format_profile_version` | Kalır | Not: taslaktaki örnek değer biçim profilinin kendi sürüm adıyla aynı biçimde değil; adlandırma tek biçime bağlanmalı (belge tutarsızlığı, karar gerekir) |
| — (yok) | Eksik | `mcq` bloğu: kök biçimi, seçenek düzeni, veri biçimi, çeldirici planı. Mevcut taslak çoktan seçmeli soruyu tarif edemiyor |
| — (yok) | Eksik | `total_marks`; HL sorusundan türetilen SL sürümü için türev ilişkisi |

Biçim profiline yansıyanlar: iki sütunlu tablo seçenekleri doğrulandı; rehber sözlüğünde olmayan komut sözcükleri `deduce`, `identify`
ve `complete` olarak gözlendi (profilde `complete` yoktu); 3 puanlık bir tartışma parçası düzey tanımlayıcılarıyla puanlanıyor
(`MarkPoint` modelinde karşılığı yok).

Bu öneriler mimari karar değişikliğidir; uygulanmadan önce [DECISIONS.md](../DECISIONS.md) için onay gerekir.

## 8. Örnek Blueprint'ler (kurgusal)

Aşağıdakiler yalnızca biçimi göstermek için müfredat düğümlerinden **bizim kurguladığımız** örneklerdir; örnek kâğıtlardaki hiçbir
soruya dayanmaz. Beceri, şablon ve ilişki kimlikleri yer tutucudur.

### 8.1 Paper 1A

```json
{
  "schema_version": "2.0",
  "program": "ib_dp", "subject": "physics",
  "exam_section": "paper_1a", "question_class": "mcq",
  "levels": ["SL", "HL"], "level_content": "sl_core", "total_marks": 1,
  "syllabus_nodes": ["C.5"],
  "context": { "type": "astronomy_space", "constraints": ["light_only_approximation", "source_or_observer_moving_not_both"] },
  "stimuli": [],
  "parts": [
    {
      "label": "", "assessment_objective": "AO2", "marks": 1,
      "answer_type": "numeric_with_unit", "reasoning_steps": 2, "level_content": "sl_core",
      "skills": ["apply_doppler_shift_light", "use_scientific_notation"],
      "givens": { "count": 2, "form": "numeric" },
      "booklet_relations": ["doppler_light_fractional_shift"],
      "verification": "formula_chain"
    }
  ],
  "mcq": {
    "stem_form": "question", "option_layout": "single_value", "data_form": "numeric",
    "distractor_plan": ["inverse_swap", "factor_slip", "wrong_formula"],
    "combination_design": false, "extraneous_data": false
  },
  "difficulty": 2,
  "format_profile_version": "dp-physics-2025@0.1"
}
```

### 8.2 Paper 2 — kısa soru (7 puan)

```json
{
  "schema_version": "2.0",
  "program": "ib_dp", "subject": "physics",
  "exam_section": "paper_2", "question_class": "short_structured",
  "levels": ["SL", "HL"], "level_content": "sl_core", "total_marks": 7,
  "syllabus_nodes": ["B.3"],
  "context": { "type": "technology_engineering", "familiarity": "syllabus_context",
               "constraints": ["ideal_gas_only", "constant_volume_process"] },
  "stimuli": [ { "id": "s1", "type": "schematic", "template": "sealed_cylinder", "use": "read_only" } ],
  "parts": [
    { "label": "a", "command_term": "state", "assessment_objective": "AO1", "marks": 1,
      "answer_type": "word_phrase", "role": "recall", "reasoning_steps": 1,
      "syllabus_node": "B.3", "level_content": "sl_core", "skills": ["ideal_gas_model_assumptions"],
      "givens": { "count": 0, "form": "none" }, "booklet_relations": [],
      "marking_pattern": "single_point", "verification": "not_code_verifiable" },
    { "label": "b", "command_term": "show", "assessment_objective": "AO3", "marks": 2,
      "answer_type": "derivation_numeric", "role": "show_that", "reasoning_steps": 2,
      "syllabus_node": "B.3", "level_content": "sl_core", "skills": ["apply_ideal_gas_law", "convert_temperature_scale"],
      "givens": { "count": 3, "form": "numeric" }, "booklet_relations": ["ideal_gas_law_molar"],
      "stimulus_refs": ["s1"], "show_that_target": "approximate_value",
      "marking_pattern": "method_answer", "verification": "formula_chain" },
    { "label": "c", "command_term": "calculate", "assessment_objective": "AO2", "marks": 2,
      "answer_type": "numeric_with_unit", "role": "calculate", "reasoning_steps": 2,
      "syllabus_node": "B.3", "level_content": "sl_core", "skills": ["apply_pressure_temperature_proportionality"],
      "givens": { "count": 1, "form": "numeric" }, "booklet_relations": ["ideal_gas_law_molar"],
      "new_information": true,
      "marking_pattern": "method_answer", "verification": "formula_chain" },
    { "label": "d", "command_term": "explain", "assessment_objective": "AO3", "marks": 2,
      "answer_type": "explanation", "role": "explain", "reasoning_steps": 2,
      "syllabus_node": "B.3", "level_content": "sl_core", "skills": ["kinetic_theory_pressure_explanation"],
      "givens": { "count": 0, "form": "none" }, "booklet_relations": [],
      "marking_pattern": "linked_statements", "verification": "not_code_verifiable" }
  ],
  "difficulty": 3,
  "format_profile_version": "dp-physics-2025@0.1"
}
```

### 8.3 Paper 1B — veri temelli soru (12 puan)

```json
{
  "schema_version": "2.0",
  "program": "ib_dp", "subject": "physics",
  "exam_section": "paper_1b", "question_class": "data_based",
  "levels": ["SL", "HL"], "level_content": "sl_core", "total_marks": 12,
  "syllabus_nodes": ["C.4"],
  "experimental_skills": ["measurement_technique", "uncertainty_propagation", "significant_figures_outliers",
                          "linearised_best_fit_gradient", "gradient_uncertainty", "model_assumption_validity"],
  "context": { "type": "laboratory", "familiarity": "syllabus_context",
               "constraints": ["no_end_correction", "displacement_nodes_only"] },
  "stimuli": [
    { "id": "s1", "type": "schematic", "template": "resonance_air_column", "use": "read_only" },
    { "id": "s2", "type": "data_table", "template": "two_column_with_uncertainty", "use": "read_values" },
    { "id": "s3", "type": "graph_scaled", "template": "linearised_scatter", "use": "student_annotates", "has_uncertainty_bars": true }
  ],
  "parts": [
    { "label": "a", "command_term": "describe", "assessment_objective": "AO2", "marks": 2,
      "answer_type": "explanation", "role": "explain", "reasoning_steps": 2, "level_content": "sl_core",
      "givens": { "count": 0, "form": "none" }, "booklet_relations": [], "stimulus_refs": ["s1"],
      "marking_pattern": "linked_statements", "verification": "not_code_verifiable" },
    { "label": "b.i", "command_term": "calculate", "assessment_objective": "AO2", "marks": 2,
      "answer_type": "numeric_unitless", "role": "calculate", "reasoning_steps": 2, "level_content": "sl_core",
      "givens": { "count": 2, "form": "from_stimulus" }, "booklet_relations": ["uncertainty_product_quotient"],
      "stimulus_refs": ["s2"], "marking_pattern": "method_answer", "verification": "formula_chain" },
    { "label": "b.ii", "command_term": "state", "assessment_objective": "AO1", "marks": 1,
      "answer_type": "numeric_with_unit", "role": "recall", "reasoning_steps": 1, "level_content": "sl_core",
      "givens": { "count": 1, "form": "from_stimulus" }, "booklet_relations": [],
      "depends_on": { "part": "b.i", "kind": "uses_previous_answer" },
      "marking_pattern": "single_point", "verification": "formula_chain" },
    { "label": "c.i", "command_term": "determine", "assessment_objective": "AO3", "marks": 3,
      "answer_type": "value_from_graph", "role": "calculate", "reasoning_steps": 3, "level_content": "sl_core",
      "givens": { "count": 0, "form": "from_stimulus" }, "booklet_relations": ["wave_speed_relation"],
      "stimulus_refs": ["s3"], "new_information": true,
      "marking_pattern": "method_answer", "verification": "formula_chain" },
    { "label": "c.ii", "command_term": "determine", "assessment_objective": "AO3", "marks": 2,
      "answer_type": "numeric_with_unit", "role": "calculate", "reasoning_steps": 2, "level_content": "sl_core",
      "givens": { "count": 0, "form": "from_stimulus" }, "booklet_relations": [],
      "stimulus_refs": ["s3"], "depends_on": { "part": "c.i", "kind": "uses_previous_answer" },
      "marking_pattern": "method_answer", "verification": "formula_chain" },
    { "label": "d", "command_term": "discuss", "assessment_objective": "AO3", "marks": 2,
      "answer_type": "explanation", "role": "evaluate", "reasoning_steps": 2, "level_content": "sl_core",
      "givens": { "count": 0, "form": "none" }, "booklet_relations": [], "stimulus_refs": ["s3"],
      "marking_pattern": "independent_statements", "verification": "not_code_verifiable" }
  ],
  "difficulty": 3,
  "format_profile_version": "dp-physics-2025@0.1"
}
```

## 9. Sınırlar ve belirsizlikler

1. **Tek örnek set.** 41 farklı çoktan seçmeli soru, 12 veri temelli parça ve 45 Paper 2 parçası. HL ile SL büyük ölçüde aynı
   soruları paylaştığı için iki düzey bağımsız örneklem değildir. Gerçek sınav oturumlarında dağılımlar farklı olabilir; örnek kâğıt
   yeni müfredatı tanıtmak için kapsamı bilinçli biçimde geniş tutmuş olabilir.
2. **Küçük hücreler.** Çapraz tablolardaki çoğu hücre 1–3 gözlem. §6.5'teki "önerilen puan" aralıkları gözlemi aşar ve yargıdır
   (ör. `estimate` yalnızca 3 puanla, `sketch` yalnızca 2 puanla görüldü). `predict`, `analyse`, `annotate` hiç gözlenmedi.
3. **Çoktan seçmelide AO yargıdır.** Komut sözcüğü yok; yalnızca hatırlama → AO1, tek ilişkinin uygulanması → AO2, birden çok
   ilişkiyi birleştirme ya da grafik/diyagram yorumlama → AO3 saydık. Sınır kaydırılırsa AO3 payı %25'ten %40 dolayına çıkabilir.
   Paper 1 toplamında AO3'ün rehberdeki "yaklaşık yarı" hedefinin altında çıkması bu yüzden kesin bulgu değildir.
4. **Rehber sözlüğünde olmayan komut sözcükleri** için AO ataması bizim: `deduce` → AO3, `identify` ve `complete` → AO1.
5. **Adım sayısı** markscheme maddelerine bakılarak yargılandı; bu yüzden puan × adım ilişkisi kısmen döngüseldir. Çoktan seçmelide
   adım sayısı (özellikle 1 ile 2 arası) okuyucuya göre değişir.
6. **Veri kitapçığı ilişkisi sayısı** veri kitapçığı açılmadan, genel bilgiyle tahmin edildi. Doğrulanmamıştır.
7. **Çeldirici temeli** seçeneklerden geriye doğru çıkarıldı; her soruda yalnızca baskın tema kaydedildi, oysa çoğu soruda üç
   çeldirici farklı hatalara dayanır. Soru başına üç ayrı kayıt daha doğru olurdu.
8. **Bağlam türü** sınırları bulanık: `everyday_object` ↔ `technology_engineering` ve `bare_abstract` ↔ `laboratory` ayrımları keyfî
   kalabiliyor. `natural_phenomenon` hiç gözlenmedi; listede müfredat analizine dayanarak duruyor.
9. **Rol ve konum** tek etiketle kaydedildi; bazı parçalar hem hesap hem değerlendirme içeriyor (`judgement_justified` bunu yakalamak
   için eklendi). "Açıklama biçiminde sorulmuş türetme" gibi sınır durumları komut sözcüğüne göre değil, beklenen cevaba göre etiketlendi.
10. **Markscheme kalıbı** `independent_statements` ile `linked_statements` ayrımı markscheme notlarından ve içerikten yargılandı.
11. **Paper 2 tema payı** birincil düğüme göre hesaplandı; parçaların dörtte biri iki düğüme yayıldığı için paylar ±5 puan oynayabilir.
12. **Paper 1B'de müfredat düğümü atanmadı.** Bir sorunun bağlamı müfredat içeriğinin dışında görünüyor; bunun kasıtlı bir biçim
    özelliği mi yoksa bu sete özgü mü olduğu uzman teyidi ister.
13. **Zorluk** bu analizden çıkarılamadı; `difficulty` alanının ölçeği tanımsız kalıyor.
14. **Tek okuyucu.** Sınıflandırma ikinci bir okuyucuyla çapraz kontrol edilmedi; fizik uzmanının en azından AO, adım ve çeldirici
    boyutlarında örneklem üzerinde doğrulama yapması gerekir.
15. SL Paper 2 toplam puanı örnekte 50; ders rehberiyle uyuşmazlık biçim profilinde zaten kayıtlı ve bu çalışmada çözülmedi.

# Pilot soruların şemaya çevrilme kuralları

> **Durum: TASLAK** (proje sahibinin onayı dilim 4 birleştirmesiyle). Tarih: 2026-10-13. M1-G dilim 4'ün sözleşmesi. Kaynak: `docs/pilot/*-pilot-questions.md` (24 dosya, 130 soru;
> biçim: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md)). Hedef: şema v1 ([DATA_ARCHITECTURE.md](../DATA_ARCHITECTURE.md) §3.5).
> Karar (proje sahibi, 2026-10-13): çeviri **kurallı bir betikle** yapılır; metin metin olarak kalır, italik değişkenler matematik
> düğümü olur, sayılar ve birimler yapılandırılmaz, formül zinciri veri olarak aktarılır.

## 1. İlkeler

1. **Belirlenimci.** Aynı Markdown her zaman aynı JSON'u üretir. Betik tahmin yürütmez: kuralların karşılamadığı bir yerde dosya adı,
   soru numarası ve satırla **durur**. Çözüm ya bir kural eklemek ya da Markdown'ı düzeltmektir; ikisi de bu belgeye ve depoya yansır.
2. **Metin kaybı yok.** Sorunun öğrenciye ve incelemeciye görünen her karakteri belgede bulunur (§6). Bunu, dönüştürücüden bağımsız
   yazılmış bir test doğrular.
3. **Çıkarım açıkça işaretlidir.** Kaynakta yazmayan ama şemanın zorunlu tuttuğu alanlar (§5) sabit kurallarla doldurulur ve çeviri
   raporunda sayılır; bunlar eğitmen incelemesinde düzeltilecek varsayımlardır, kaynak bilgisi değildir.

## 2. Çıktı

- Her kaynak dosya için `content/pilot/<kök>.json` (kök: dosya adından `-pilot-questions.md` atılır). Biçim:
  `qlab.content.pilot.model.PilotFile`.
- Her sorunun kalıcı anahtarı: `source_ref = "pilot/<kök>#<soru numarası>"`.
- `content/pilot/CONVERSION_REPORT.md`: dosya başına soru sayıları, §5 varsayımlarının dağılımı, atlanan çözüm modelleri ve
  nedenleri, italik belirteçlerin sınıflandırma tablosu (§4.2).
- JSON dosyaları depoya girer. `python -m qlab.content.pilot convert --check` depodaki JSON'un kaynaktan yeniden üretilenle aynı
  olduğunu doğrular (CI'da çalışır).

## 3. Dosya ve soru yapısı

| Kaynak | Hedef |
|---|---|
| Dosya adının ilk parçası (`a1`, `c3`) | `primary_syllabus_node` (`A.1`, `C.3`); her parçanın `syllabus_node` değeri de budur |
| `## Kapsam tablosu` satırı (`#` sütunu soru numarası) | Bölüm, düzey, kazanım, hedef, zorluk (aşağıda) |
| `## Soru N — Paper 1A` | `question_class = mcq`, `exam_section = paper_1a`, `total_marks = 1` |
| `## Soru N — Paper 1B (… puan)` | `data_based`, `paper_1b` |
| `## Soru N — Paper 2 (… puan)` | `short_structured` (toplam 20 ise `long_structured`), `paper_2` |
| Başlıktaki puan | Parça puanlarının toplamıyla aynı olmalı; değilse hata |
| Düzey `SL` | `levels = ["sl", "hl"]`, içerik düzeyi `sl_core` |
| Düzey `HL` (tabloda ya da başlıkta) | `levels = ["hl"]`, içerik düzeyi `ahl` (çoktan seçmelide `mcq.level_content`, yapılandırılmışta her parça) |
| Kazanım sütunu | `outcome` (olduğu gibi, Türkçe) |
| Zorluk: Kolay / Kolay–orta / Orta / Orta–zor / Zor | `easy` / `medium` / `medium` / `hard` / `hard` |
| Hedef tek değerse (`AO2`) | Çoktan seçmelide `mcq.assessment_objective`; aralıksa (`AO1–AO3`) boş bırakılır |
| `language` | `en`; `calculator` = `true` |

Soru bloğu bir sonraki `## ` başlığında ya da `---` çizgisinde biter; `---` ile sonraki `## ` başlığı arasında boş olmayan bir satır varsa hata (soru içinde çizgi kullanılamaz). `## Biçim uyumu`, `## Bu denemeden çıkan gözlemler` ve dosya
başındaki durum notu aktarılmaz.

### 3.1 Çoktan seçmeli

| Kaynak | Hedef |
|---|---|
| İlk seçenekten (`A. `) önceki paragraflar | `stem` (her paragraf bir `paragraph`) |
| `> **Şekil:** …` alıntı bloğu | Uyaran (§3.3) ve bulunduğu yerde `figure` düğümü |
| `A. ` … `D. ` satırları | `mcq.options[].cells` (tek hücre); `option_layout = single_value` |
| `**Cevap: X**` | `mcq.correct_key` |
| `**Çözüm.** …` (tabloya kadar olan paragraflar) | `mcq.explanation` ("Çözüm." etiketi atılır) |
| `| Seçenek | Dayandığı yanılgı |` tablosu | İlgili seçeneğin `rationale` alanı |

Dört seçenek, bir cevap ve doğru olmayan üç seçeneğin her biri için bir yanılgı satırı zorunludur; eksikse hata.

### 3.2 Yapılandırılmış ve veri temelli

| Kaynak | Hedef |
|---|---|
| İlk parçadan önceki içerik | `stem`; veri tablosu `table` düğümü olur (ilk satır `table_header`) |
| `**(a)** metin [n]` | Parça: `label = a`, `id = a`, `marks = n`; `[n]` gövdeye alınmaz |
| `**(d)** (i) metin [n]` ve izleyen ` (ii) metin [n]` | Parçalar `d.i`, `d.ii` (`id` = etiket) |
| İki parça arasındaki paragraf, tablo ya da şekil | Sonraki parçanın `lead_in` alanı |
| Parça metni birden çok satıra bölünmüşse | Tek paragraf (satır sonu boşluk olur) |
| Markscheme tablosu satırı (`| N. | a | ii | Answers | Notes | Total |`) | İlgili parçanın maddeleri ve notları; `Total` parça puanına eşit olmalı |
| `Answers` hücresi, `<br>` ile ayrılmış ve `✓` ile biten her satır | Bir `MarkPoint` (`✓` atılır); `id = <parça id>-m<sıra>` |
| `**ALTERNATIVE 1**`, `**ALTERNATIVE 2**` satırları | Ardından gelen maddelere `route = alt1`, `alt2`; satırın kendisi madde olmaz |
| Madde içindeki `**OR**` ve `**AND**` | Madde **bölünmez**; sözcük koyu metin olarak kalır (alternatif grubu kurulmaz) |
| `« … »` | İçindeki metin `optional` işaretli; tırnak karakterleri metinde kalmaz |
| Altı çizili gereklilik | Kaynakta yok; `essential` kullanılmaz |
| Madde sayısı (yollar bir kez sayılarak) parça puanından fazlaysa | `marks_capped = true`; azsa hata |
| `Notes` hücresi, `<br>` ile ayrılmış her satır | Bir `Note` (çevreleyen italik işareti atılır) |
| Not `OWTTE` | `kind = owtte` |
| Not `Allow ECF from (b)…` ile başlıyorsa | `kind = ecf`; parçanın `ecf_from` alanına anılan parçalar (yalnızca önceki ve var olan parçalar; `(c)(i)` → `c.i`) |
| Not `Accept …` / `Do not accept …` / `Award [n] max …` | `accept` / `do_not_accept` / `cap` |
| Diğer notlar | `general` |
| `### Şekil notu` bölümü | Uyaran (§3.3), `kind = graph`, `use = read_values`; belgeye `figure` düğümü eklenmez. **Notun metni aktarılmaz** (yazarın çalışma notudur ve cevabı içerebilir); `description` sabit metindir: `Veriden üretilecek grafik; ayrıntı kaynak dosyadaki Şekil notunda.` |
| `### Formül zinciri (çözüm modeli)` | `solution_model` (§3.4) |
| Markscheme'den sonraki serbest açıklama paragrafları ("Denetim …") | Aktarılmaz (raporda sayılır) |

### 3.3 Uyaranlar

Her `> **Şekil:**` bloğu ve her `### Şekil notu` bir uyarandır: `id = fig1, fig2, …` (belgedeki sırayla), `asset_id` yok.
`> **Şekil:**` bloğu için `description` = blok metni ("Şekil:" etiketi olmadan, satırlar birleştirilmiş, işaretleme sadeleştirilmiş
düz metin), `use = read_only`. Şekil notu için §3.2'deki sabit açıklama. Açıklama personel içindir; öğrenciye gösterilmez.

`kind` (yalnızca `> **Şekil:**` blokları için; Şekil notu her zaman `graph`), açıklamada **en önce geçen** anahtar sözcükten. Eşleşme
büyük/küçük harfe duyarsızdır ve **sözcük başında** aranır (`ışın`, "dışında" sözcüğünün içinde eşleşmez):
`devre`, `direnç`, `batarya`, `voltmetre`, `ampermetre` → `circuit_diagram`; `grafik`, `eksen`, `P–V` → `graph`; `alan çizgi` →
`field_diagram`; `ışın`, `dalga cephe` → `ray_wavefront_diagram`; `enerji düzey` → `energy_level_diagram`; `uzay-zaman` →
`spacetime_diagram`; `tablo` → `data_table`; hiçbiri → `schematic_diagram`. Uyaranı olan soru yayınlanamaz (D-49).

### 3.4 Çözüm modeli

Formül zinciri tablosu şemaya yalnızca **tamamı** kurallara uyuyorsa aktarılır; uymuyorsa o sorunun `solution_model` alanı boş
bırakılır ve neden rapora yazılır (soru yine aktarılır).

- `Parametreler` satırı: ters tırnak içindeki her `ad = değer birim` bir parametredir. `sabit` / `sabitler` sözcüğünden sonra gelenler
  de parametre olarak aktarılır (sabit tablosuna bağ kurulmaz; rapora yazılır). Birim yoksa boştur.
- Diğer satırlar adımdır: ilk sütundaki ters tırnaklı ad `name`, ikinci sütundaki ters tırnaklı ifade `expr`, `id = s1, s2, …`.
  `Sonuç` sütunu sayı + birimden ibaretse birim `unit` olur (üst simge karakterleri ASCII'ye çevrilir: `m s⁻¹` → `m s^-1`).
- Uymama örnekleri: ters tırnaksız parametre, adı tanımlayıcı olmayan satır, yinelenen ad, sayı biçimine uymayan değer, birim
  biçimine uymayan birim, ifade sütunu boş ya da birden çok ifade içeren satır.
- Cevap bağı (`answers`), `stated_value` ve `solution_step` kurulmaz.

## 4. Satır içi metin

### 4.1 İşaretleme

| Kaynak | Hedef |
|---|---|
| Düz metin (Unicode dahil: `⁻¹`, `√`, `½`, `×`, `°`, `Δ`) | `text` düğümü, olduğu gibi |
| `**metin**` | `bold` işaretli `text` |
| `*metin*`, değişken değilse (§4.2) | `italic` işaretli `text` |
| `*x*`, değişkense | `math_inline` |
| `*x*<sub>y</sub>` (değişkenin hemen ardından) | Tek `math_inline`: `x_{y}`; `<sup>` için `x^{y}` |
| Değişkene bağlı olmayan `<sub>…</sub>`, `<sup>…</sup>` | `sub` / `sup` işaretli `text` |
| `<br>` (madde ve not ayırıcı olmadığı yerde) | `hard_break` |
| Ters tırnak (yalnızca formül zincirinde beklenir) | Başka yerde hata |

Ardışık, işaretleri aynı metin parçaları tek `text` düğümünde birleşir. Baştaki ve sondaki boşluk atılır; paragraf içi boşluk tekilleşir.

### 4.2 İtalik belirtecin sınıflandırılması

Bir `*…*` içeriği şu sırayla sınıflanır; hiçbirine uymuyorsa **hata** (sessiz tahmin yok):

1. Tek harf (Latin ya da Yunan) → değişken.
2. Yalnızca harflerden oluşan, en az bir büyük harf ya da Yunan harfi içeren, en çok 4 karakterlik dizi (`MR`, `Mv`, `GMm`, `Iω`) → değişken.
3. Küçük harfli çok harfli diziler için **kapalı değişken listesi** (ör. `mv`, `mg`, `ct`, `hf`, `gt`, `vx`, `vt`, `mr`) → değişken.
4. **Kapalı sözcük listesi** (ör. `not`, `one`, `two`, `twice`, `into`, `on`, `out of`, `parallel`, `one eighth`) ve boşluk ya da
   noktalama içeren tümceler → italik metin.

İki liste dönüştürücüde durur, bu belgeyle birlikte güncellenir ve her belirtecin hangi kuralla sınıflandığı raporda listelenir.

### 4.3 Değişkenden LaTeX'e

Matematik kaynağı yalnızca ASCII'dir ([DATA_ARCHITECTURE.md](../DATA_ARCHITECTURE.md) §3.4). Latin harfler olduğu gibi yazılır;
Yunan harfleri komuta çevrilir (`γ` → `\gamma`, `Δ` → `\Delta`, `ω` → `\omega`; komuttan sonra harf geliyorsa araya boşluk:
`Iω` → `I\omega`, `ωt` → `\omega t`). Alt ve üst simge içeriği aynı kuralla çevrilir ve süslü parantez içine alınır.

## 5. Kaynakta olmayan, kuralla doldurulan alanlar

| Alan | Kural |
|---|---|
| `mcq.option_kind` | Dört seçeneğin tamamı `sayı + birim` ise `numeric_with_unit`; tamamı yalnız sayı ya da oran ise `ratio`; herhangi biri değişken (`math_inline`) içeriyorsa `algebraic_expression`; tamamı en çok 4 sözcükse `word_phrase`; değilse `statement` |
| `part.command_term` | Parça metninin ilk sözcüğü küçük harfle, sözlükteyse; `Show that` → `show` ve `show_that = true`; sözlükte yoksa (ör. bağlam cümlesiyle başlayan parça) boş |
| `part.answer_type` | Komut sözcüğünden: `calculate`, `determine`, `estimate` → `numeric_with_unit`; `state`, `identify` → `word_phrase`; `show` → `derivation_numeric`; `explain`, `outline`, `describe`, `suggest`, `predict`, `deduce` → `explanation`; `discuss`, `analyse` → `extended_evaluation`; `draw`, `annotate`, `complete` → `drawing_on_diagram`; `sketch` → `graph_sketch`; komut sözcüğü boşsa `explanation` |
| `part.assessment_objective`, `depends_on`, `stimulus_refs` | Boş |
| `MarkPoint.kind` | `statement` |
| Uyaran `kind` | §3.3'teki anahtar sözcük kuralı |

Bu alanlar varsayımdır; rapor her değerin kaç kez üretildiğini verir ve eğitmen incelemesinde düzeltilir.

## 6. Kaynakla karşılaştırma (kabul testi)

Her soru için belgenin "görünen metni" kaynağın görünen metnine eşit olmalıdır. Test dönüştürücüyü kullanmaz; iki tarafı kendi
yöntemiyle düz metne indirger.

- **Belge tarafı**, sırayla: `stem`; çoktan seçmelide seçenek hücreleri (A–D), açıklama, yanılgılar (seçenek sırasıyla);
  yapılandırılmışta her parça için `lead_in`, gövde, maddeler, notlar; ardından uyaran açıklamaları. `text` düğümü metniyle;
  `math_inline` LaTeX'i §4.3'ün tersiyle (komut → Yunan harfi; `_`, `^`, `{`, `}` ve komut ayıran boşluk atılır); `hard_break` boşlukla;
  tablo hücreleri sırayla.
- **Kaynak tarafı**: aynı bölgeler; `*`, `**`, `<sub>`, `</sub>`, `<sup>`, `</sup>`, `«`, `»`, `✓`, tablo çizgileri, `[n]` puanları,
  parça etiketleri (`**(a)**`, `(ii)`), seçenek harfleri (`A. `), `**Cevap: X**`, `**Çözüm.**`, `> **Şekil:**` etiketleri,
  `**ALTERNATIVE n**` satırları ve markscheme'in `Question` / `Total` sütunları atılır; `<br>` boşluk olur. Not hücrelerindeki `✓` atılmaz (§8); yalnızca madde satırlarının sonundaki `✓` atılır.
- İki tarafta da tüm boşluklar atıldıktan sonra karşılaştırılır. Fark varsa test, ilk farkın çevresini gösterir.

Ayrıca: 24 dosya, toplam 130 soru; her `source_ref` tekil; her belge şemadan, müfredat sözlüğünden ve matematik kontrolünden geçer;
çoktan seçmeli sayısı 101, Paper 2 sayısı 24, Paper 1B sayısı 5.

## 7. İçe aktarma

`python -m qlab.content.pilot load --operator <hesap kimliği>` JSON dosyalarını `content` servisi üzerinden yükler. Tek transaction:
ya hepsi ya hiçbiri.

- **Kaynak doğrulaması.** Her JSON dosyasının `source_sha256` değeri, aynı depo kökündeki Markdown dosyasının özetiyle
  karşılaştırılır; uyuşmuyorsa (JSON eski ya da elle yazılmış) içe aktarma reddedilir.
- **Rights kaydı (D-52, D-58).** Platformun kendi içerik kaydı lisans referansı `platform:own-content` olan kayıttır: herkese gösterim,
  AI işleme ve ticari kullanım açık. İçe aktarma kaydı **kendiliğinden açmaz**:
  - Hiç kayıt yoksa durur; kayıt `--create-rights` ile açıkça açılır (sahip `--holder`). Açılış audit'e yazılır (sahip, izinler,
    geçerlilik başlangıcı ve işlemi yapan).
  - Kayıt varsa sahibi ve izinleri beklenenle **birebir** aynı olmalıdır; değilse durur.
  - Bu referansla iptal edilmiş, süresi dolmuş ya da birden çok kayıt varsa durur. İptal bir geri çekme kararıdır; içe aktarma onu
    yeni bir kayıtla aşmaz.
- **Kayıtlar** `authored` kökenli ve **taslak** olarak açılır; incelemeye gönderilmez, sürüm açılmaz, durum değiştirilmez.
- **Yeniden çalıştırma.** Soru `source_ref` ile tanınır:
  - İçerik aynıysa: atlanır (`unchanged`).
  - İçerik farklı, sürüm `draft` ve veritabanındaki içerik **içe aktarmanın son yazdığı içerikle aynıysa** (yani kimse elle
    değiştirmemişse): güncellenir (`updated`).
  - İçerik farklı ve sürüm elle değiştirilmişse (`edited`), ya da `draft` dışında bir durumdaysa (durumun adıyla): dokunulmaz,
    `skipped` altında raporlanır. Elle yapılan düzeltme hiçbir seçenekle ezilmez.
  - Anahtar var ama sorunun rights kaydı gösterime izin vermiyorsa: dokunulmaz, `blocked` altında raporlanır.
- **İz.** Sürüm kayıtlarını yapan `system:pilot_import`'tur. Her çalıştırma ayrıca bir `pilot_import.completed` audit kaydı yazar:
  işlemi yapan (`--operator`, opak hesap kimliği), dosyaların özetleri ve sayılar.
- `--dry-run` her şeyi yapar ve geri alır.

## 8. Uygulamada netleşen okumalar (2026-10-13)

Dönüştürücü ve bağımsız test 24 dosyaya karşı yazılırken yukarıdaki kuralların açık bıraktığı yerler şöyle bağlandı. Bunlar
dönüştürücünün davranışıdır; çeviri raporundaki "Kural ekleri" ve "Yorumlar" başlıkları hangi soruda gerektiğini listeler.

| Konu | Okuma |
|---|---|
| Başlık biçimi `Paper 2 (HL, 9 puan)` | Geçerli; düzey başlıktan ve tablodan okunur, başlık HL deyip tablo SL diyorsa hata |
| Markscheme `Total` hücresinde `2 max` | Sayı parça puanına eşit olmalı; "max" ek bilgi taşımaz (kapalı parça madde sayısından anlaşılır) |
| `Answers` hücresinde `✓` ile bitmeyen ve `ALTERNATIVE` olmayan satır | Hata. (`b3-gas-laws` soru 6 (g)'deki tek başına `**OR**` satırı kaynakta `ALTERNATIVE 1 / 2` olarak yeniden etiketlendi) |
| Çoktan seçmelide yanılgı tablosundan sonraki serbest paragraf ("Not: …") | Aktarılmaz; raporda sayılır (yapılandırılmış sorulardaki serbest açıklamalar gibi) |
| Komut sözcüğünden sonra noktalama (`Explain,`) | Noktalama atılır, sözcük sözlükte aranır |
| `Allow ECF …` ile başlayan her not (`Allow ECF for the volume from (a).`) | `kind = ecf`; `ecf_from` nottaki `(x)` / `(x)(y)` göndermelerinden. Alt parçası olan bir harfe `(c)` diye gönderme: hata (kaynakta yok) |
| `Award [n] max …`, `Award [n max] …` | `cap`. `Do not award …` ve diğer `Award …` notları `general` |
| Not içindeki italik | Hiçbir metin düğümü `italic` işareti taşımaz (notlar kaynakta kısmen italik). Notun italik olmayan kısmında italik yazılmış bir değişken (`*U*`) yine matematik düğümüdür; bütünüyle italik bir notun içindeki harfler ise düz metin kalır |
| Not içindeki `✓` ve koyu `**ALTERNATIVE:**` | `✓` **metinde kalır** (Notlar sütununa yazılmış alternatif yolun puan sınırlarını gösterir); `ALTERNATIVE` burada yol işareti değil, koyu metindir (not `general` kalır) |
| `option_kind`: birimsiz tek seçenek (`0`) ya da düz metin Yunan harfi (`π/6 rad`) içeren sayısal dörtlü | Kural harfiyen uygulanır: `word_phrase` ya da `statement` olur. Eğitmen incelemesinde düzeltilecek varsayım |
| `option_kind`: değişken içeren kısa sözel seçenekler ("less than *g*") | Kural sırası gereği `algebraic_expression` |
| Uyaran türünde "ilk eşleşen anahtar sözcük" | Açıklama metninde en önce geçen |
| Yunan harfi için iki komut varsa | Harfin Unicode adındaki: `ε` → `\epsilon`, `φ` → `\phi`, `θ` → `\theta` |
| `outcome` içindeki işaretleme (`*γ*`) | Hücre olduğu gibi alınır; işaretleme çevrilmez (6 soruda yıldız karakteri kalır). Alan gösterilen içerik değil, üst veridir |
| `secondary_syllabus_nodes`, `Note.mark_point_id` | Boş |
| Küçük harfli çok harfli değişkenler (kapalı liste) | `ct`, `gh`, `gr`, `gt`, `hc`, `hf`, `kx`, `mc`, `mg`, `mgv`, `mv`, `mx` ve dönüştürücüdeki diğerleri |
| İtalik sözcükler (kapalı liste) | `not`, `one`, `two`, `twice`, `into`, `on`, `out of`, `parallel`, `Accept`, `Allow`, `and`, `OWTTE` ve dönüştürücüdeki diğerleri |

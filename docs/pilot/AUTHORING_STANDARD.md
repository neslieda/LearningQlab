# Pilot soru yazım standardı

> **Durum: TASLAK.** Tarih: 2026-10-11. Pilot setlerin tüm konularda aynı ölçütlerle yazılmasını sağlar. Örnek uygulama:
> [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).

## 1. Kaynak kuralı

- Girdi yalnızca şunlardır: [müfredat analizi](../syllabus/dp-physics-2025-analysis.md), [biçim profili](../formats/dp-physics-2025-format-profile.md)
  ve genel fizik bilgisi.
- Hiçbir sınav kâğıdı, markscheme, ders kitabı sorusu ya da internetteki soru girdi olarak kullanılmaz; PDF açılmaz, soru aramak için
  web kullanılmaz.
- Bilinen bir soruyu hatırlayıp sayılarını değiştirmek yasaktır. Bağlam (senaryo) yazarın kendi kurgusudur.

## 2. Her konu dosyasının içeriği

Dosya adı: `<düğüm>-<kısa-ad>-pilot-questions.md` (ör. `b3-gas-laws-pilot-questions.md`). Bölümler, A.1 dosyasındaki sırayla:

1. Başlık ve durum notu ("İNCELENMEMİŞ TASLAK", tarih, kaynak, sayısal doğrulama, doğrulanmayanlar).
2. Kapsam tablosu: # · bölüm · düzey (SL / HL) · kazanım · hedef (AO) · komut sözcüğü · puan · zorluk. Altında kapsanmayan kazanımlar.
3. Sorular: `## Soru N — Paper …` başlığı; soru metni İngilizce; ardından `**Cevap: X**` (çoktan seçmeli) ya da `### Markscheme`.
4. Biçim uyumu tablosu.

Konu başına en az: **3 Paper 1A** sorusu + **1 Paper 2 kısa sorusu** (SL kâğıdında kullanılacaksa 4–6 puan; yalnızca HL için 4–9 puan;
kaynak: müfredat analizi §2.1). Tema başına ayrıca **1 Paper 1B** sorusu (8–12 puan).

## 3. Müfredat uyumu

- Her soru tek bir düğümün belirli bir kazanımını ölçer ve kapsam tablosunda yazılır.
- Düğümün "kapsam dışı / sınır" maddeleri tek tek kontrol edilir; soru bunların dışına çıkamaz.
- Düzey doğru etiketlenir: yalnızca HL düğümleri ve ek HL içeriği "HL"; diğerleri "SL".
- "Nitel" denen içerikte hesap sorulmaz. Müfredat dışı matematik (türev, integral, eşzamanlı denklemli çarpışma) kullanılmaz.
- Konu başına sorular AO1+AO2 ve AO3 arasında dengelenir; yalnızca formüle sayı koyma sorusu AO3 sayılmaz.

## 4. Bilimsel doğruluk

- Her sayısal cevap ve her sayısal çeldirici ayrı bir hesapla (`python3`) yeniden üretilir; dosyada bunun yapıldığı belirtilir.
- Sabitler [dp-physics-2025-constants.md](../syllabus/dp-physics-2025-constants.md) tablosundan, oradaki değer ve anlamlı basamakla alınır.
  Veri kitapçığında bulunan sabit soru metninde ayrıca verilmez; kitapçıkta **bulunmayan** her değer (sesin hızı, malzeme özellikleri,
  nüklit kütleleri, gök cismi verileri, belirli şekillerin eylemsizlik momenti) soruda verilir.
- Veriler fiziksel olarak gerçekçidir (gerçek malzeme özellikleri, makul büyüklükler).
- Tek doğru cevap vardır. Gerekli varsayımlar soruda yazılır (ör. "air resistance is negligible").
- Birimler ve anlamlı basamak tutarlıdır; cevap, verilerin anlamlı basamağıyla verilir.

## 5. Çoktan seçmeli sorular

- Yapı: bağlam → (varsa şekil tarifi) → ayrı satırda tek soru cümlesi → A–D.
- Dört seçenek aynı türde ve aynı birimde; sayısalsa büyüklük sırasında.
- Her yanlış seçenek belirli bir kavram yanılgısına ya da tipik hataya dayanır; tabloda yanılgı ve onu veren hesap yazılır.
- Bir konu dosyasındaki doğru cevapların konumu dengelenir (hepsi aynı harf olmaz).
- Şekil gerekiyorsa metinle tarif edilir: `> **Şekil:** …`. Şekil olmadan çözülemeyen soru yazılmaz.

## 6. Yapılandırılmış sorular (Paper 2 ve 1B)

- Alt parça puanı 1, 2 ya da 3; daha fazlası olmaz. Puan satır sonunda `[n]`.
- Komut sözcükleri müfredat analizindeki listeden; cevabın türü sözcüğe uyar.
- En az bir parça AO3 düzeyindedir (Explain, Determine, Show that, Suggest, Discuss…).
- Uygun yerde "Show that" kalıbı: yaklaşık değer verilir, sonraki parça o değeri kullanır.
- Markscheme dört sütunlu tablo: `Question | | | Answers | Notes | Total`; her madde `✓` ile biter; `« »`, `OR`, `AND`, `OWTTE`,
  `Allow ECF from (…)` gösterimleri biçim profilindeki anlamlarıyla kullanılır.
- Sayısal parçaların ardından "Formül zinciri" tablosu: parametreler, adım adı, ifade, sonuç.
- Paper 1B: deney bağlamı, "büyüklük / birim ± belirsizlik" başlıklı veri tablosu; belirsizlik, grafik ve değerlendirme becerileri.
  Grafik gerekiyorsa veriden üretilecek grafik tarif edilir ve bu eksik "Biçim uyumu" tablosunda yazılır.

## 7. Bağımsız doğrulama

Her dosya, yazarından farklı bir çözücü tarafından kontrol edilir:

1. Çözücü soruları cevapları görmeden çözer.
2. Sonuçlarını cevap anahtarı ve markscheme ile karşılaştırır.
3. Ayrıca şunlara bakar: tek doğru cevap, eksik bilgi, belirsiz ifade, müfredat sınırı, düzey etiketi, biçim kuralları.
4. Bulgular `review/<düğüm>-review.md` dosyasına yazılır; uyuşmazlık varsa soru düzeltilir ya da çıkarılır.

Bu, uzman incelemesinin yerine geçmez. Tüm dosyalar fizik uzmanı onayına kadar "incelenmemiş taslak"tır.

## 7. Sisteme aktarım için yazım kuralları (2026-10-13)

Sorular kurallı bir betikle şemaya çevrilir ([IMPORT_RULES.md](IMPORT_RULES.md)). Betik tahmin yürütmez; aşağıdakilere uyulmazsa ya
durur ya da bilgi kaybolur.

- Değişkenler italik yazılır (`*v*`); alt ve üst simge değişkenin hemen ardından `<sub>…</sub>` / `<sup>…</sup>` ile verilir
  (`*v*<sub>y</sub>`). Unicode alt simge (`θ₀`) ve işaret (`t′`) matematiğin dışında kalır; kullanılmamalıdır.
- İtalik içinde yalnızca değişken ya da vurgulanan sözcük bulunur; bir formülün tamamı tek italik içine alınmaz.
- Markscheme'de her puan satırı `✓` ile biter. Birbirini dışlayan tam çözüm yolları `**ALTERNATIVE 1**` / `**ALTERNATIVE 2**`
  satırlarıyla ayrılır; iki yol arasına tek başına `**OR**` satırı konmaz. Alternatif yol Notlar sütununa yazılmaz.
- Notlar: `OWTTE`, `Allow ECF from (b).`, `Accept …`, `Do not accept …`, `Award [n] max …` kalıplarıyla başlar.
- Formül zinciri tablosunda yalnızca parametre ve adım satırları bulunur; denetim ve karşılaştırma satırları tablonun altına düz
  metin olarak yazılır (tabloda kalırlarsa çözüm modeli aktarılmaz). Her parametre ters tırnak içinde `ad = değer birim` biçimindedir.
- "Şekil notu" yazarın çalışma notudur ve sisteme alınmaz; öğrencinin görmesi gereken her şey soru metninde olmalıdır.
- Soru bloğunun içinde `---` çizgisi kullanılmaz.
- Komut sözcüğü parçanın ilk sözcüğüdür ve müfredat analizindeki listeden seçilir.

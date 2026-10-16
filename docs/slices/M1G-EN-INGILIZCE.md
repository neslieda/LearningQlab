# M1-G dilim EN — sistem içeriğinin tamamen İngilizceye geçmesi

> **Durum: TASLAK** (2026-10-15, mimar oturumu). Sahibinin kararı (2026-10-15): "Sorular, cevaplar, hocaların yazacağı her şey,
> kontroller, cevap anahtarı, cevapların değerlendirilmesi, puanlama — hepsi İngilizce olacak." D-59 (4)'ün "çeviri zamanlaması
> sahibinin kararını bekliyor" kısmını kapatır: çeviri şimdi yapılır. Dilim 7a'nın (PR #4) üstüne kurulur. Dilim birleşirken içeriği
> kalıcı belgelere işlenir ve bu dosya kaldırılır.

## 1. Amaç ve kapsam

Amaç: sisteme giren ve sistemin ürettiği her içerik metni İngilizce olsun; bundan sonra Türkçe içerik kaydedilemesin.

Kapsam:

1. **Pilot kaynak dosyaları** (`docs/pilot/*-pilot-questions.md`, 24 dosya) baştan sona İngilizceye çevrilir: çözüm açıklamaları,
   çeldirici gerekçeleri, kazanım cümleleri, şekil tarifleri, şekil notları, serbest notlar, dosya başlığı ve durum notu, kapsam
   tablosu, biçim uyumu ve bağımsız kontrol bölümleri, yapı işaretleri (§3).
2. **Dönüştürücü** (`qlab.content.pilot`) İngilizce işaretleri okur; Türkçe işaretler artık tanınmaz (tek kaynak, iki dil yok).
3. `content/pilot/*.json` ve çeviri raporu yeniden üretilir.
4. **Kayıt koruması** (§4): Türkçeye özgü harf taşıyan soru belgesi kaydedilemez.
5. Belgeler: `AUTHORING_STANDARD.md`, `IMPORT_RULES.md`, `SINIRLAR.md`, `M1G-5-YETKILER.md` §3.1, `DECISIONS.md` (D-60).

Kapsam dışı:

- **Açıklamaların öğrenciye açılması.** D-59 §3.1 "çeviri bitince açıklamalar cevapla birlikte açılır" der; bu öğrenci yanıt tipini
  ve OpenAPI'yi değiştirir. Dilim 8'e (öğrenci önizlemesi) bırakılır.
- Proje belgeleri (`docs/*.md`, inceleme notları `docs/pilot/review/`, çeviri raporu): sahibe yazılır, Türkçe kalır. Sisteme girmezler.
- Kullanıcı arayüzü ve API hata iletileri: zaten İngilizce (denetlendi, 2026-10-15).

Kritik alan: kısmen. Şema kuralı (§4) yayın kapısını etkilemez ama her yazma yolunu etkiler; insan onayı ister. Migration yok.

## 2. Çevirinin kuralları (alt ajanlar için)

- **Yalnızca Türkçe metin değişir.** Soru metni, seçenekler, markscheme, notlar, sayılar, birimler, matematik, `*italik*`,
  `<sub>`, `« »`, tablo yapısı, satır ve sütun sayısı, boş satırlar, bağlantılar bayt bayt korunur. Satır sırası değişmez.
- Fizik İngilizcesi IB biçimindedir: birim yazımı `m s⁻¹`, komut sözcükleri (Calculate, Determine, …) olduğu gibi.
- Kazanım hücresi kısa bir öğrenme hedefi cümlesidir (ör. "Distance vs displacement; average velocity").
- Çeldirici gerekçesi, yanılgıyı anlatan tek cümledir (ör. "Uses total distance instead of displacement: 1400 / 200 (average speed)").
- Hiçbir sınav kurumu sorusundan metin alınmaz (CLAUDE.md kural 14); çeviri yalnızca bu dosyadaki kendi metnimizdendir.
- Türkçe kalan tek karakter bile hatadır: çeviriden sonra dosyada `ç ğ ı ş İ Ğ Ş Ç` bulunmaz (`ö ü` yalnızca özel adlarda, ör.
  Schrödinger).

## 3. Yapı işaretleri (dondurulmuş)

| Eski (Türkçe) | Yeni (İngilizce) |
|---|---|
| `# Pilot soru seti: A.1 Kinematik` | `# Pilot question set: A.1 Kinematics` |
| `## Kapsam tablosu` | `## Scope table` |
| `## Biçim uyumu` | `## Format conformance` |
| `## Bağımsız kontrol` | `## Independent check` |
| `## Bu denemeden çıkan gözlemler` | `## Observations from this trial` |
| Kapsam başlığı `# \| Bölüm \| Düzey \| Kazanım \| Hedef \| Komut sözcüğü \| Puan \| Zorluk` | `# \| Section \| Level \| Outcome \| Objective \| Command terms \| Marks \| Difficulty` |
| Zorluk `Kolay`, `Kolay–orta`, `Orta`, `Orta–zor`, `Zor` | `Easy`, `Easy–medium`, `Medium`, `Medium–hard`, `Hard` (eşleme aynı: easy, medium, medium, hard, hard) |
| `## Soru 4 — Paper 2 (HL, 9 puan)` | `## Question 4 — Paper 2 (HL, 9 marks)` |
| `**Cevap: A**` | `**Answer: A**` |
| `**Çözüm.**` | `**Solution.**` |
| `\| Seçenek \| Dayandığı yanılgı \|` | `\| Option \| Misconception \|` |
| `> **Şekil:**` | `> **Figure:**` |
| `### Şekil notu` | `### Figure note` |
| `### Formül zinciri (çözüm modeli)` | `### Formula chain (solution model)` |
| `\| Adım \| İfade \| Sonuç \|` | `\| Step \| Expression \| Result \|` |
| Parametrede `sabit` / `sabitler` | `constant` / `constants` |
| Serbest paragraf `Not:` | `Note:` |
| Durum notu etiketleri `Durum`, `Kaynak`, `Sayısal doğrulama`, `Bağımsız kontrol`, `Doğrulanmayan` | `Status`, `Source`, `Numerical check`, `Independent check`, `Not verified` |
| Biçim uyumu tablosu `\| Kural \| Durum \|` | `\| Rule \| Status \|` |

Şekil tarifinden uyaran türü çıkaran anahtar sözcükler (en önce geçen kazanır; tam sözcük olarak, isteğe bağlı çoğul `s`/`es` ekiyle — "graphs" eşleşir, "graphite" eşleşmez; büyük/küçük harfe duyarsız):

| Tür | Sözcükler |
|---|---|
| `circuit_diagram` | `circuit`, `resistor`, `battery`, `cell`, `voltmeter`, `ammeter` |
| `graph` | `graph`, `axis`, `axes`, `p–v` |
| `field_diagram` | `field line` |
| `ray_wavefront_diagram` | `ray`, `wavefront` |
| `energy_level_diagram` | `energy level` |
| `spacetime_diagram` | `spacetime`, `space-time` |
| `data_table` | `table` |

Şekil notundan açılan uyaranın sabit açıklaması: `Graph to be generated from data; details in the Figure note of the source file.`

## 4. Kayıt koruması

- `qlab.content.schema` bir saf fonksiyon sunar: soru belgesinin bütün metinlerini (metin düğümleri, `outcome`, uyaran açıklaması,
  not, gerekçe, açıklama, çözüm modeli adları dahil her `str`) gezer; Türkçeye özgü harf (`ğ Ğ ı İ ş Ş`) bulunan alanların yollarını
  döndürür. `ç ö ü` bilerek dışarıda: İngilizce fizik metninde özel adlarda geçer (Schrödinger).
- İçerik servisinin her yazma yolu (taslak oluşturma, taslak güncelleme, revizyon açma ve içe aktarma) bu fonksiyonu çağırır; bulgu
  varsa belge şemaya aykırı bir belge gibi reddedilir (var olan hata tipi ve kodu; yeni API hata kodu yok, OpenAPI değişmez). İleti:
  `Content must be written in English; found non-English letters at <yol>`.
- Okuma yolları denetlemez: veritabanındaki eski Türkçe taslaklar okunabilir kalır (yerel ortam; yeniden içe aktarma onları günceller).
- Dönüştürücü de aynı fonksiyonu çağırır: Türkçe kalan bir kaynak dosya dönüştürülemez.

## 5. Kabul testleri

1. 24 kaynak dosyada `ç ğ ı ş İ Ğ Ş Ç` yok.
2. Dönüştürme hatasız; `convert --check` temiz; kaynak karşılaştırma testi (görünen metin) geçer.
3. **Yapı değişmez:** yeni JSON ile eski JSON karşılaştırıldığında yalnızca şu alanlar farklıdır: `outcome`, `mcq.explanation`,
   `mcq.options[].rationale`, `stimuli[].description`. Soru sayısı, kimlikler, kaynak anahtarları, sınıf, bölüm, düzey, zorluk, puanlar,
   seçenek türleri, cevap türleri, **uyaran türleri**, markscheme, notlar, çözüm modelleri bayt bayt aynıdır.
4. Kayıt koruması: Türkçe harfli belge her yazma yolunda reddedilir; `Schrödinger` geçen belge kabul edilir; okuma yolu eski Türkçe
   belgeyi okur.
5. Bütün API ve web testleri geçer.

## 6. Mimar kararları (sahibin onayına)

1. Kaynak dosyalar yapı işaretleri dahil İngilizceye çevrilir; dönüştürücü yalnızca İngilizce işaretleri tanır.
2. Türkçe içerik kayıtta reddedilir (yalnızca belirgin Türkçe harfler; sözcük listesi kullanılmaz, yanlış ret riski yüzünden).
3. Proje belgeleri, inceleme notları ve çeviri raporu Türkçe kalır; bunlar sistem içeriği değildir.
4. Açıklamaların öğrenciye açılması dilim 8'e kalır.
5. Çeviri Sonnet alt ajanlarıyla yapılır; fizik doğruluğu yapısal karşılaştırma (§5.3) ve örneklem incelemesiyle denetlenir. Eğitmen
   incelemesi yerine geçmez: pilot sorular zaten "incelenmemiş taslak"tır (kural 13).

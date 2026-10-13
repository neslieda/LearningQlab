# Sınırlar

> **Durum: TASLAK.** Tarih: 2026-10-13. Kapsam: M1-G dilim 4'ün sonu (şema, veritabanı, content servisi, KaTeX kontrolü, pilot soruların içe aktarılması).
> Okur: eğitmenler ve incelemeciler. Bu belge sistemin **bugün** ne yapamadığını ve neye izin vermediğini düz bir dille anlatır.
> Her dilim birleştiğinde güncellenir. Eğitmenlerden beklenenler ayrı belgededir: [EGITMEN_BILGI_NOTU.md](EGITMEN_BILGI_NOTU.md).
> Teknik ayrıntı için köşeli parantez içindeki belgelere bakılır; bu belgeyle çelişirlerse onlar geçerlidir.

## 1. Bugün olmayanlar

| Ne | Durum |
|---|---|
| Web arayüzü (soru görüntüleme, inceleme, düzenleme) | Yok. Dilim 6–8'de gelir |
| Giriş, hesaplar ve roller | Yok. Dilim 5'te gelir; o zamana kadar kimin neyi yapabileceği denetlenmez |
| Öğrenci görünümü | Yok. Dilim 8'de gelir |
| Soruların sisteme yüklenmiş hali | 130 pilot soru şemaya çevrildi ve **taslak** olarak içe aktarılabiliyor (§7.1); görüntüleyecek arayüz henüz yok |
| Şekil, grafik ve diyagram | Üretilemiyor ve yüklenemiyor |
| Sayısal cevapların kodla doğrulanması | Yok (formül yorumlayıcısı M3'te) |
| Deneme sınavı, otomatik puanlama, AI geri bildirimi, analitik, ödeme | Yok |
| İnternetten erişim | Yok. Sistem yalnızca geliştirme bilgisayarında çalışıyor |

## 2. Yayınlanamayan sorular

- **Şekli, grafiği ya da veri görseli olan hiçbir soru yayınlanamaz.** İncelenebilir ve onaylanabilir, ama öğrenciye açılamaz.
  Görsel üretimi gelene kadar böyle kalır (D-49).
- Onaylanmamış soru yayınlanamaz.
- Otomatik kontrollerden (belge yapısı, müfredat sözlüğü, matematik gösterimi) biri eksikse ya da kalmışsa soru incelemeye bile
  giremez.
- Bunları yalnızca arayüz değil, sistemin kendisi ve veritabanı zorlar; "elle" atlatılamaz.

## 3. Doğruluk güvencesinin sınırı

- Sistem bugün bir sorunun **fizik olarak doğru** olup olmadığını denetlemez. Denetlediği şeyler biçimseldir: puanların toplamı,
  markscheme yapısı, verilen değer ile çözüm modelindeki parametrenin birebir aynı yazılması, matematiğin ekranda çizilebilmesi.
- Çözüm modeli (formül zinciri) veri olarak saklanır ama **hesaplanmaz**. Sayısal cevabın doğruluğu şimdilik yalnızca eğitmen
  incelemesine dayanır.
- Bir soruyu yazan, onaylayan ve yayınlayan şu an aynı kişi olabilir; tek onay yeterlidir (D-53, geçici). Web'e açılmadan önce
  yeniden değerlendirilecek.

## 4. Soru yapısının sınırları

[DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) §3.5

- Çoktan seçmeli: tam dört seçenek (A–D), tek doğru cevap, 1 puan. Her yanlış seçenek için dayandığı yanılgı yazılmak zorundadır.
- Yapılandırılmış soru: her alt parça 1, 2 ya da 3 puan; daha fazlası olamaz. Etiketler `a`, `b.ii` biçimindedir (alt parça en çok viii).
- Markscheme'de her madde 1 puandır. "Ya da" (OR) alternatifleri ve birbirini dışlayan çözüm yolları (ALTERNATIVE 1 / 2) desteklenir;
  düzey tanımlayıcılı (3/2/1/0 bantlı) puanlama **desteklenmez**.
- Düzey yalnızca SL ve HL'dir. SL kâğıdında kullanılabilen soru ek HL içeriği taşıyamaz.
- Tablolar: en çok 12 sütun birleştirme, iç içe tablo yok. Listeler: iç içe liste yok.
- Sınav bölümü, komut sözcüğü ve müfredat düğümü yalnızca sistemde tanımlı listeden seçilebilir (şu an: 3 bölüm, 18 komut sözcüğü,
  24 konu düğümü). Listede olmayan bir değerle soru kaydedilemez.
- Soru tek bir programa (IB DP Physics, ilk sınav 2025) göre kurulu; başka ders ya da program henüz yok.

## 5. Matematik yazımının sınırları

[DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) §3.4

- Matematik LaTeX ile yazılır ve **yalnızca klavyedeki standart (ASCII) karakterlerle**. Özel karakter doğrudan yazılamaz:
  `×` yerine `\times`, `µ` yerine `\mu`, `Ω` yerine `\Omega`, `°` yerine `\degree` ya da `^\circ`, `≤` yerine `\le`.
- Yalnızca izinli listedeki komutlar kullanılabilir (183 komut, 6 ortam: `aligned`, `cases`, `array`, `matrix`, `pmatrix`, `bmatrix`).
  Liste fizik için derlendi ama pilot sorularla henüz sınanmadı; eksik çıkabilir. Eksik komut bir kod değişikliğiyle eklenir.
- **Kullanılamayanlar:** renk, bağlantı, görsel, makro tanımı, yorum satırı (`%`), kimya gösterimi (`\ce`), denklem numarası (`\tag`),
  çerçeve (`\boxed`), satır arası boşluk ayarı (`\\[2em]`).
- Boyut: formül başına en çok 2 000 karakter; çok geniş matris ya da çok uzun tek formül (ör. yüzden fazla kesir) reddedilir.
- Hatalı ya da izinsiz matematik içeren soru **hiç kaydedilmez**; hata hangi formülde olduğunu söyler ama sorunun neresinde olduğunu
  henüz söylemez.
- Birimli büyüklükler (ör. 20 m/s) matematik olarak değil ayrı bir "büyüklük" öğesi olarak yazılır; ekranda nasıl dizileceği gösterim
  bileşeniyle (dilim 6) belirlenecek.

## 6. Düzenleme ve sürümlerin sınırları

[DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) §2.2 · [DOMAIN_MODEL.md](DOMAIN_MODEL.md) §4

- Soru yalnızca **taslak** ve **düzeltme bekliyor** durumunda düzenlenebilir. İncelemedeki, onaylanmış ya da yayınlanmış soru
  düzenlenemez; önce geri gönderilmesi gerekir.
- Yayınlanmış soru hiç değişmez. Düzeltmek için yeni sürüm açılır; yeni sürüm yayınlanınca eskisi kendiliğinden geri çekilir.
- Bir sorunun aynı anda yalnızca bir "üzerinde çalışılan" sürümü olabilir.
- İncelemede bulunan bir hata sisteme "kontrol sonucu" olarak yazılamaz; soru gerekçeyle geri gönderilir.
- Hiçbir soru ya da sürüm silinemez; reddedilen sürüm kayıtta kalır.
- Geri gönderme, ret, geri çekme ve yeniden yayınlama **gerekçe ister** (en çok 500 karakter). Gerekçeler silinemeyen bir kayda yazılır.
- Onay ve yayın, onaylayanın gördüğü içeriğe bağlıdır: soru o arada değiştiyse işlem reddedilir ve yeniden bakmak gerekir.
- Eski metin saklanmaz: düzeltilen taslağın önceki hali geri getirilemez (yalnızca yayınlanmış sürümler kalıcıdır).

## 7. İçeriğin bugünkü durumu

- 130 pilot soru **incelenmemiş taslaktır**; hiçbiri eğitmen onayından geçmedi. Yapay zekâ yardımıyla, müfredat analizinden yazıldı.
- Müfredat düğüm listesi, komut sözcükleri, sabitler tablosu ve biçim profili taslaktır ve uzman teyidi bekliyor
  ([EGITMEN_BILGI_NOTU.md](EGITMEN_BILGI_NOTU.md) §1).
- Bilinen uyumsuzluk: pilot Paper 2 sorularının çoğu 9 puan ve SL etiketli; örnek kâğıtlarda SL kısa sorular 4–6 puan. Sorular
  etiketlendikleri gibi aktarıldı.

### 7.1 İçe aktarılan soruların sınırları

Sorular Markdown'dan kurallı bir betikle çevrildi ([pilot/IMPORT_RULES.md](pilot/IMPORT_RULES.md)). Otomatik test, her sorunun
**görünen metninin** kaynağıyla aynı olduğunu doğrular; aşağıdakileri **doğrulamaz**. Ayrıntılı sayılar ve soru bazında liste:
`content/pilot/CONVERSION_REPORT.md`.

- **Kuralla doldurulmuş, güvenilmemesi gereken alanlar.** Kaynakta yazmadığı halde şema zorunlu tuttuğu için sabit kurallarla
  dolduruldu; bağımsız incelemenin kaba hata tahmini parantez içinde:
  - çoktan seçmelide seçenek türü (101 sorunun yaklaşık 7'si kesin yanlış, 6'sı tartışmalı; ör. içinde `0` ya da `π` geçen sayısal
    seçenekler "sözcük" sayıldı);
  - parçanın komut sözcüğü (17 parçada boş: parça bir bağlam cümlesiyle başlıyor ya da sözcük "Comment" ve sözlükte yok);
  - parçanın cevap türü (111 parçanın 6–9'u yanlış; komut sözcüğü boş olanlar "açıklama" sayıldı);
  - şekil türü (28 şekil; tarifteki anahtar sözcükle atanır, ör. tarifinde "ampermetre" geçen bir deney düzeneği "devre şeması" sayıldı);
  - puan maddesinin türü (hepsi "ifade"), ölçme hedefi (yapılandırılmış sorularda boş).
- **Markscheme alternatifleri yapılandırılmadı.** Madde içindeki `OR` ve `AND` koyu metin olarak durur; sistem bunları "tek puanın
  alternatifleri" olarak bilmez. `ALTERNATIVE 1 / 2` yolları yapılandırıldı. Beş soruda alternatif yol Notlar sütununa yazılmıştı;
  bunlar yol değil, içinde `✓` işaretleri duran düz nottur.
- **Notlardaki ve çözüm açıklamalarındaki değişkenler çoğunlukla düz metindir** (yaklaşık 20 not; çoktan seçmeli çözümlerinin çoğu).
  Aynı değişken puan maddesinde matematik, notta düz harf olarak görünebilir.
- **Unicode alt simge ve üs matematiğin dışında kalır** (38 yer): kaynakta `θ₀`, `t′`, `t²` olarak yazılan yerlerde harf matematik, simge
  düz metindir (`<sub>` ile yazılanlar tek matematik düğümüdür). Aynı büyüklüğün iki farklı gösterimi olabilir.
- **Sayılar ve birimler yapılandırılmadı**: "18 m s⁻¹" düz metindir; değer–parametre eşleşmesi denetlenmez.
- **Çözüm modeli** 29 yapılandırılmış sorunun 13'ünde var; 16'sında kaynak tablo kurallara uymadığı için boş. Var olanlarda
  sonuç değerleri aktarılmadı, 61 adımın 14'ünün birimi boş, sabitler sabit tablosuna bağlı değil ve hiçbiri hesaplanarak doğrulanmadı.
- **Aktarılmayanlar**: markscheme ve formül zincirinden sonraki serbest yazar notları (12 paragraf; bazıları incelemeci için
  yararlı gerekçeler içerir) ve beş veri temelli sorudaki "Şekil notu" metni (cevabı içerebildiği için). Bunlar yalnızca Markdown'dadır.
- **Türkçe içerik**: çözüm açıklamaları, çeldirici gerekçeleri, kazanım cümleleri ve şekil tarifleri Türkçedir; soru metni
  İngilizcedir. Ürün İngilizce olduğundan bunlar öğrenciye açılmadan önce çevrilmelidir.
- **24 soru yayınlanamaz**: şekil ya da grafik gerektiriyor ve yalnızca tarifi var (§2).
- Altı sorunun kazanım cümlesinde ham `*` işaretleri kaldı.

### 7.2 Yeniden içe aktarma

- İçe aktarma komutu yeniden çalıştırılabilir; var olan soruyu ikinci kez oluşturmaz.
- **Elle düzeltilmiş bir taslağı ezmez.** Kaynak Markdown sonradan değişirse yalnızca kimsenin dokunmadığı taslaklar güncellenir;
  düzeltilmiş, incelemeye girmiş ya da yayınlanmış sorular olduğu gibi kalır ve raporda "atlandı" olarak listelenir. Sonuç: bir soru
  sistemde düzeltildikten sonra Markdown'daki hali ile sistemdeki hali ayrışır; doğru olan sistemdekidir.
- Platformun kendi içerik hak kaydı iptal edilirse içe aktarma durur ve yeni kayıt açmaz; bu bir insan kararı gerektirir.

## 8. Hukuki belirsizlikler ⚖️

Bunlar teknik sınır değil, hukuk danışmanının yanıtını bekleyen sorulardır ([DECISIONS.md](DECISIONS.md) R-01, R-02):

- Sınav kurumunun adının, ders ve konu başlıklarının üründe kullanımı.
- Yapay zekâ yardımıyla yazılmış soruların telif durumu.
- Silinemeyen işlem kaydı ile kişisel verinin silinmesi hakkının ilişkisi.

Bu yüzden: sınav kâğıtlarından soru, sayı ya da senaryo sisteme **giremez**; orijinal sınav soruları öğrenciye gösterilmez.

# M1-G dilim 7c — yeni soru, parça düzenleme, hata yeri, müfredat bilgisi

> **Durum: TASLAK** (2026-10-15, mimar oturumu). Sahibinin kararı (2026-10-15): 7b'nin üç bilinen sınırı giderilir: komut sözcüğü
> listesinin sabit programdan gelmesi, bazı hataların alanın yanında görünmemesi, parça ekleme/silme ve yeni soru oluşturmanın olmaması.
> 7b'nin (PR #7) üstüne kurulur; PR doğrudan `main`'e açılır. Dilim birleşirken içeriği kalıcı belgelere işlenir ve bu dosya kaldırılır.

## 1. API sözleşmesi (donduruldu)

1. **Müfredat bilgisi.** `AdminVersion.syllabus = {program, subject, version}`: sorunun belgesinin doğrulandığı müfredat sürümünün
   kodları. Ekran komut sözcüğü, sınav bölümü ve düğüm listesini bunlarla `GET /v1/programs/{program}/subjects/{subject}/syllabus?version=`
   uç noktasından çeker.
2. **Hata yeri.** `content.InvalidDocument.errors` artık `DocumentProblem(message, location)` dizisidir. `location` belge içindeki
   noktalı yoldur (dizinler sayı: `parts.0.mark_points.1.content.content.0.content.2.attrs.latex`), belgenin bütünüyle ilgili sorunlarda
   (boyut, NUL) `null`. API bunu `ProblemItem.location = "document." + location` olarak verir. Sözlük, matematik ve İngilizce
   kurallarının her sorunu yerini taşır; bir kural birden çok yere değiyorsa her yer için ayrı sorun döner.
3. **Yeni soru.** `POST /v1/admin/questions` (personel; yetki tablosuna eklendi), gövde `{program, subject, version?, document}`;
   `version` yoksa dersin en yeni müfredat sürümü. Soru `authored` kökenli açılır, ilk sürümü `draft`, `source_ref` yok. Hak kaydı
   platformun kendi içerik kaydıdır (D-58; içe aktarmanın kullandığı kayıt ve aynı denetimler). Yanıt 201 `AdminVersion`.
   - Kayıt yoksa, birden çoksa, iptal edilmiş, süreli ya da gösterime izin vermiyorsa 409 `own_content_rights_unavailable`, hiçbir şey
     yazılmaz (fail-closed, kural 2).
   - Bilinmeyen program, ders ya da sürüm: 404 `not_found`.
   - Belge sorunları: 422 `invalid_document` (yerleriyle).
   - Audit: `question_version.created` (var olan).
4. **Katalog** (2026-10-15 eklendi; ekranın programı sabit yazmadan bulabilmesi için). `GET /v1/programs` (giriş yapmış her hesap,
   müfredat okumasıyla aynı yetki): `{items: [{program, program_name, subject, subject_name, versions: [{code, title}]}]}`. Yalnızca
   sınav biçimi olan müfredat sürümleri (soru yazılabilenler); sürümler en yeniden eskiye. Salt okunur.

## 2. Ekran

### 2.1 Yeni soru — `/admin/questions/new`

- Liste sayfasında personele "New question" düğmesi.
- Önce üst bilgi: soru sınıfı (multiple choice, short structured, long structured, data based), sınav bölümü (müfredatın sözlüğünden),
  düzeyler, ana müfredat düğümü (yaprak düğümler, kod + başlık; aranabilir liste), zorluk, hesap makinesi, `outcome`.
- Sonra 7b'deki form, sınıfa göre boş bir şablonla: çoktan seçmelide dört seçenek, doğru cevap, gerekçeler ve çözüm; yapılandırılmışta
  bir parça (a) ve bir puan maddesi. Seçenek türü ve düzeni yeni soruda seçilebilir (sonra salt okunur).
- "Create" `POST` gönderir; başarıda yeni sürümün düzenleme sayfasına gider ve "Created" duyurur. Hatalar 7b'deki gibi; 409
  `own_content_rights_unavailable` → "New questions cannot be created right now: the platform's content rights record is missing.
  Ask a platform admin."
- Program ve ders bu dilimde yalnızca sistemde var olan tek ders için önceden seçilidir, ama sabit yazılmaz: `GET` ile bulunur
  (birden fazla ders olduğunda seçim kutusu görünür).

### 2.2 Parça ekleme, silme, sıralama (yapılandırılmış sorular)

- "Add part" sona yeni bir harf parçası ekler (`a`, `b`, … sıradaki harf). Yeni parça: puan 1, bir puan maddesi, boş gövde (kayıttan
  önce doldurulmalı).
- "Remove part (b)" parçayı siler; en az bir parça kalır. "Move part (b) up/down" sıralar.
- Etiketler her değişiklikten sonra sırayla yeniden verilir (`a`, `b`, `c`; alt parçalı harfler birlikte taşınır, alt parça sırası
  korunur). Parça ve puan maddesi kimlikleri değişmez.
- Silme ya da taşıma sonucunda bir parçanın `depends_on` / `ecf_from` / notlardaki ECF başvurusu artık **önceki** bir parçaya gitmiyorsa
  bu başvuru kaldırılır ve görünür bir bildirim (`role="status"`) kaç başvurunun değiştiğini söyler.
- Toplam puan kendiliğinden hesaplanır. Alt parça ekleme bu dilimde yok.

### 2.3 Hata yeri ve müfredat

- 422 sorunlarının her biri `location`'dan alanına eşlenir (yolun en yakın düzenlenebilir alanına: ör. matematik düğümünün yolu
  içinde bulunduğu metin kutusuna) ve alanın yanında gösterilir; özet bağlantısı o alana odaklanır. Eşlenemeyen sorun yalnızca özette.
- Komut sözcüğü listesi `AdminVersion.syllabus`'tan çekilir; sabit program kodu kaldırılır.

## 3. Kabul testleri

1. `AdminVersion.syllabus` her yanıtta doğru kodları taşır.
2. Matematik, sözlük ve İngilizce kurallarının her sorunu doğru `location` ile döner; boyut/NUL sorunu `null`.
3. `POST /v1/admin/questions`: personel 201 alır ve sürüm `draft`; öğrenci/öğretmen 404 ya da 403 (yetki tablosundaki gibi); kendi içerik
   kaydı yoksa ya da iptal edilmişse 409 ve veritabanı değişmez; bilinmeyen ders 404; `origin` ve `source_ref` istemciden alınmaz.
4. Ekranda yeni soru: çoktan seçmeli ve yapılandırılmış bir soru oluşturulup düzenleme sayfası açılır.
5. Parça ekleme/silme/taşıma doğru etiketleri, kimlikleri, toplam puanı ve temizlenmiş başvuruları üretir; bildirim görünür.
6. 422'de hatalar alanların yanında; odak bağlantısı çalışır.
7. Komut sözcüğü listesi sürümün müfredatından gelir (sabit kod yok).

## 4. Mimar kararları (sahibin onayına)

1. Yeni sorular yalnızca platformun kendi içerik hak kaydıyla açılır; istemci hak kaydı seçmez. Kayıt yoksa oluşturulmaz (fail-closed).
2. Yeni uç nokta `STAFF` (incelemeci dahil): içerik yazarlığı incelemecinin işi sayıldı (D-59 (1) taslak düzenleme yetkisinin uzantısı).
3. Parça taşıma/silme, geçersiz kalan ECF/bağımlılık başvurularını kaldırır ve bildirir (engellemek yerine).
4. Alt parça ekleme, uyaran ekleme ve görsel yükleme kapsam dışı.

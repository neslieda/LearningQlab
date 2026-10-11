# SECURITY

> **Durum: ONAYLANDI** (2026-10-11, proje sahibi). Değişiklikler [DECISIONS.md](DECISIONS.md) üzerinden işlenir.
> **Bu belge hukuki görüş değildir.** ⚖️ işaretli maddeler hukuk danışmanının kararını gerektirir; teknik kesinlik gibi okunmamalıdır.

## 1. Korunan varlıklar ve başlıca tehditler

| Varlık | Tehdit | Ana önlem |
|---|---|---|
| Hak kısıtlı kaynak içerik | Yetkisiz erişim, toplu çekme, izinsiz AI işleme | Rights kapısı, tek erişim katmanı, hız sınırı, kill switch |
| Öğrenci kişisel verisi (reşit olmayanlar dahil) | Sızıntı, gereksiz saklama, rızasız işleme | Asgari veri, rıza kayıtları, imzalı erişim, silme akışı |
| Yayınlanan içeriğin doğruluğu | Hatalı sorunun yayınlanması | Kod kontrolleri, insan onayı, backend yayın bloğu |
| Hesaplar | Ele geçirme, yetki yükseltme | Managed kimlik, personelde 2FA, varsayılan ret |
| LLM bütçesi | Kötüye kullanım, kaçak maliyet | Kota, bütçe tavanı, uyarı |
| Sistem bütünlüğü | Talimat enjeksiyonu, yorumlayıcı istismarı, kötü niyetli yükleme | Veri/talimat ayrımı, beyaz liste yorumlayıcı, yükleme temizliği |

## 2. Kimlik doğrulama

- Managed identity provider (OIDC). Şifre uygulamada saklanmaz.
- API her istekte token imzasını, süresini ve hedefini doğrular.
- Personel rollerinde iki adımlı doğrulama zorunlu; sağlayıcıda zorlanır, API ayrıca token'daki doğrulama düzeyini kontrol eder.
- Oturum süreleri kısa, yenileme sağlayıcıda.

## 3. Yetkilendirme

- Tek politika katmanı; **varsayılan ret**. Uç nokta, gerekli rolü ve kapsamı beyan etmeden çalışmaz.
- Roller kurum kapsamındadır ([DOMAIN_MODEL.md](DOMAIN_MODEL.md) §3).
- İçerik erişimi üç koşulun kesişimidir: rol, entitlement, rights kaydı.

| Kaynak | student | teacher | org_admin | reviewer | content_admin | platform_admin |
|---|---|---|---|---|---|---|
| Yayınlanmış `generated` soru | entitlement | entitlement | entitlement | ✔ | ✔ | ✔ |
| `source_original` soru | yalnız rights'lı kurum üyesi | yalnız rights'lı kurum üyesi | yalnız rights'lı kurum üyesi | ✔ | ✔ | ✔ |
| Kendi cevapları ve puanları | ✔ | — | — | — | — | — |
| Kurum öğrencilerinin sonuçları | — | kendi kurumu | kendi kurumu | — | — | — |
| İtiraz edilen cevap | sahibi | — | — | ✔ | — | ✔ |
| İnceleme kuyruğu, karar | — | — | — | ✔ | ✔ | ✔ |
| Kaynak yükleme, pipeline | — | — | — | — | ✔ | ✔ |
| Yayın / geri çekme | — | — | — | — | ✔ | ✔ |
| Rights, kill switch, roller, kural tabloları | — | — | — | — | — | ✔ |

**Zorlama:** bu tablo bir test verisidir. Her uç nokta × her rol için otomatik test çalışır; tabloya girmemiş uç nokta CI'ı geçemez.

## 4. Haklar ve lisans ⚖️

### 4.1 Durum (R-01)

- ibo.org sayfalarının **arama özetine** göre: IB telifli materyalinin herhangi bir generative AI aracına sorgu ya da eğitim verisi olarak
  verilmesi yazılı izin olmadan yasak; resmi ilişkisi olmayan üçüncü tarafların ticari kullanımı yazılı lisans gerektiriyor; lisans
  politikası ücretli tutoring kullanımını ve son iki sınav dönemi materyalini kapsam dışı tutuyor.
- IB'nin IP sayfası doğrudan erişimde 403 döndü; **metin birebir okunamadı**. Bu özet bağlayıcı kaynak yerine geçmez.
- Kurumun IB ile ilişkisi belirsiz. Kullanıcı, kaynak soruların AI ile işlenmesini (içerik alma, Blueprint) bilerek açık tutmaya karar
  verdi; mimar itirazı [DECISIONS.md](DECISIONS.md) R-01'de kayıtlı.
- Diğer sınav kurumları (Cambridge, College Board, Pearson ve diğerleri) için aynı sorular ayrı ayrı sorulmalıdır; bir kurumdan alınan
  görüş diğerine taşınmaz.

### 4.2 Teknik kontroller

| Kontrol | Uygulama |
|---|---|
| Rights birinci sınıf veri | Her kaynak belge ve soru bir `RightsRecord`'a bağlı; izin bayrakları: gösterim (hangi kuruma), AI işleme, ticari kullanım, geçerlilik |
| Fail-closed | Kayıt yok, süresi dolmuş ya da bayrak kapalı → içerik işlenmez ve gösterilmez |
| Kill switch | Kaynak içerik işleyen adımlar ve `source_original` gösterimi tek ayardan kapatılır |
| Üretici izolasyonu | `generation` modülü soru tablolarını import edemez; yalnızca Blueprint alır |
| Sızıntı kontrolü | Blueprint kaynak metinden uzun ortak dizi taşıyamaz (kod) |
| Lineage | Üretilen her soru Blueprint üzerinden kaynak soruya bağlı; toplu geri çekme uç noktası |
| Sağlayıcı koşulu | Kaynak içerik gören adımlar yalnızca eğitimde kullanmayan ve saklamayan koşullardaki modellerle çalışır; `llm` modülü zorlar |
| Erişim kaydı | `source_original` içeriğe her erişim audit log'a yazılır |
| Marka | Arayüz ve pazarlama metinlerinde sınav kurumu adı ve "onaylanmamıştır" ibaresi ⚖️ |

### 4.3 Hukuk danışmanına sorular ⚖️

1. Kurumun statüsü ve kaynak soruları kendi öğrencilerine dijital olarak gösterme hakkı.
2. Kaynak soruların bir LLM'e verilmesi (içerik alma, sınıflandırma, Blueprint çıkarımı); "no-retention" koşulunun etkisi.
3. Kaynak soruların embedding'e çevrilip benzerlik karşılaştırmasında kullanılması.
4. Blueprint'ten üretilen sorunun türev eser sayılıp sayılmayacağı; "sınav tarzı" ifadesinin sınırı.
5. Sınav kurumu adının, ders ve müfredat başlıklarının ticari üründe kullanımı.
6. Lisans başvurusunun mümkün olup olmadığı ve kapsamı.
7. Bir geri çekme talebinde öğrenci geçmişindeki soru içeriğinin saklanıp saklanamayacağı.

Genel erişim (M6), bu soruların yazılı yanıtı olmadan açılmaz.

## 5. Gizlilik, yaş ve rıza ⚖️ (R-02)

### 5.1 Politika (kullanıcı kararı)

13 yaşından itibaren kontrollü üyelik. Hukuken mümkün olan yerde öğrenci bağımsız satın alır; mümkün olmayan yerde doğrulanabilir veli
izniyle. 13 yaş altı kayıt olamaz.

### 5.2 Tasarım

- Kayıtta doğum tarihi ve ülke. Yaş bandı türetilir; doğum tarihi yalnızca bu amaçla tutulur.
- `ConsentPolicy`: ülke bazlı, sürümlü kural tablosu — veri rızası yaşı, bağımsız satın alma yaşı, kabul edilen rıza yöntemi, saklama
  süreleri. **İçeriğini hukuk danışmanı sağlar.**
- Açılış, kuralları doğrulanmış sınırlı ülke listesiyle. Tabloda olmayan ülke: en sıkı kural (18 yaş altında hesap ve satın alma için veli
  izni); kayıt engellenmez.
- `Consent`: kim, kimin adına, ne için, yöntem, kural sürümü, zaman. Geri alınabilir; geri alma entitlement'ı ve veri işlemeyi durdurur.
- **Veli-öder:** öğrenci veliye ödeme bağlantısı gönderir; veli kendi ödeme aracıyla öder ve onay metnini kabul eder. Bunun
  "doğrulanabilir izin" sayılıp sayılmadığı ülkeye göre teyit edilir ⚖️.
- **Kontrollü üyelik (18 yaş altı):** asgari veri, herkese açık profil yok, pazarlama iletişimi ve davranışsal izleme kapalı.

### 5.3 Veri asgariliği

- LLM'e giden puanlama isteklerinde ad, e-posta, hesap kimliği yoktur.
- Fotoğraflar: yüklemede konum ve cihaz bilgisi silinir; kısa süreli imzalı bağlantıyla erişilir.
- **Açık nokta ⚖️:** cevap fotoğrafları, reşit olmayanlar dahil, hesap boyunca saklanır (kullanıcı kararı; mimar veri asgariliği itirazını
  kaydetti). Saklama süresi `ConsentPolicy`'de ülke ve yaş bandına göre ayarlanabilir alandır; danışman kısa süre isterse kod değişmez.
- Öğrenci cevaplarını işleyen LLM sağlayıcısının veri koşulları ve bunun gizlilik bildiriminde açıklanması ⚖️.

### 5.4 Kullanıcı hakları

Veriyi indirme, düzeltme, silme. Hesap silme kaskadı: cevaplar, fotoğraflar (object storage dahil), kişisel alanlar. Yedeklerdeki kopyalar
yedek penceresi dolunca düşer.

## 6. AI'a özgü riskler

| Risk | Önlem |
|---|---|
| PDF içindeki metnin modele talimat vermesi | Kaynak metin ayrı veri alanında; çıktı sabit şemada; model araç kullanamaz |
| Öğrenci cevabının puanlayıcıyı yönlendirmesi | Cevap veri alanında; çıktı yalnızca madde kararları; puan madde değerini aşamaz; toplamı kod hesaplar |
| Modelin uydurma cevabı | Cevap formül zincirinden; kör çözüm; insan onayı |
| Sessiz kalite düşüşü (model ya da prompt değişikliği) | Sürümleme; ölçüm eşiği geçilmeden etkinleşmez |
| Kaçak maliyet | Çalışma başı ve günlük bütçe tavanı; kullanıcı kotası; uyarı |
| Kaynak içeriğin loglara sızması | LLM çağrı gövdeleri rights kaydına bağlı saklama süresiyle; gözlem servislerine gövde gönderilmez |

Agent ve araç kullanan model olmaması etki alanını sınırlar: kandırılmış bir model en fazla hatalı JSON döndürür.

## 7. Formül yorumlayıcısı

- Girdi LLM üretimidir, dolayısıyla güvenilmezdir.
- Kendi ayrıştırıcısı; izinli öğe listesi dışında her şey reddedilir. Python `eval`/`exec` ve ham metne `sympify` kullanılmaz.
- Ayrı alt süreç; süre, bellek ve ifade boyutu sınırı; ağ ve dosya erişimi yok.
- Özellik tabanlı testler ve mutation testing kapsamındadır; değişikliği insan onayı gerektirir.

## 8. Yükleme güvenliği

- İzinli türler: PDF (personel), görsel (öğrenci). Boyut ve sayfa sınırı.
- Görseller yeniden kodlanır; meta veri silinir. PDF'ler yalnızca sayfa görüntüsüne çevrilerek işlenir.
- Yükleme imzalı adresle doğrudan depolamaya; içerik türü sunucuda yeniden doğrulanır.

## 9. Altyapı güvenliği

- Aktarımda TLS; depolamada şifreleme (managed servisler).
- Gizli anahtarlar PaaS deposunda; ortam başına ayrı; LLM anahtarları yalnızca worker'da. Depoda gizli anahtar taraması.
- Production veritabanına doğrudan erişim kısıtlı ve kayıtlı.
- Bağımlılık ve imaj taraması CI'da.
- Günlük yedek, zaman noktasına dönüş, yılda iki geri yükleme tatbikatı.

## 10. Denetim kaydı

Yalnızca eklenen, değiştirilemeyen `audit_log`. Kaydedilenler: içerik durum geçişleri ve yayınlar, inceleme kararları, rol ve üyelik
değişiklikleri, rights ve kill switch değişiklikleri, kural tablosu ve prompt sürümü değişiklikleri, `source_original` erişimleri, veri
indirme ve silme talepleri, rıza olayları.

## 11. İçerik koruma

Düzey: temel (kullanıcı kararı). Ücretli içerik yalnızca yetkili istekle döner; hesap başına hız sınırı; olağandışı çekme örüntüsü tespiti
ve uyarı. Kullanıcıya özel filigran MVP'de yok; kapalı dönemde sızıntı gözlenirse eklenir. Web'de gösterilen içeriğin kopyalanması
tamamen engellenemez.

## 12. Güvenlik testleri ve kapılar

| Ne | Ne zaman |
|---|---|
| Yetki tablosu testleri, import kuralları | Her değişiklikte (CI) |
| Bağımlılık, gizli anahtar ve statik kod taraması | Her değişiklikte (CI) |
| Güvenlik odaklı kod incelemesi (ajan) | Kritik alanlara dokunan her pull request |
| İnsan onayı | Yetki, rights, yorumlayıcı, migration, ödeme, prompt eşikleri |
| Bağımsız sızma testi + dış kod denetimi | M6; kritik bulgu kapanmadan genel erişim açılmaz |

## 13. Olay müdahalesi

- **Hak sahibi talebi:** kill switch → lineage ile etkilenen soruları bul → toplu geri çek → audit kaydını dışa aktar.
- **Veri sızıntısı:** erişimi kes, kapsamı audit log'dan belirle, bildirim yükümlülükleri ⚖️.
- **Hatalı içerik yayını:** soruyu geri çek; etkilenen öğrenci puanlarını işaretle; düzeltilmiş sürümü yayınla.
- Sorumlular ve iletişim listesi M6 öncesi yazılır.

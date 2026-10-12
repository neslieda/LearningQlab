# DECISIONS

> **Durum: ONAYLANDI** (2026-10-11, proje sahibi). Değişiklikler [DECISIONS.md](DECISIONS.md) üzerinden işlenir.
> Karar kaydı, ertelenen kararlar, risk kaydı ve dış bilgilerin doğrulama durumu. Yeni karar ya da değişiklik buraya eklenir; eski satır
> silinmez, "yerine geçen" notu düşülür.

## 1. Bağlam

Başlangıç referansı, başka bir araçla hazırlanmış "IB Soru Platformu İçin Önerilen Teknik Mimari" adlı ön araştırma belgesiydi (aşağıda
"ön belge"). Bağlayıcı değildi; öneriler tek tek değerlendirildi. Kararlar 2026-10-10 tarihli planlama oturumunda, proje sahibiyle
tartışılarak alındı.

**Ön belgeden korunan ilkeler:** LLM orkestratör değil; deterministic doğrulama ve insan onayı; sıralı blok dizisi; görseller object
storage'da; rights birinci sınıf veri ve fail-closed; eşiklerin kalibrasyon gerektirdiği kabulü.

**Ön belgeden reddedilenler:** Temporal, LangGraph, LiteLLM, Z3, self-hosted LLM ve embedding, üç motorlu OCR zinciri, KaTeX + MathJax
çift renderer, temperature ile çeşitlilik, tek JSONB soru dokümanı, 6–8 haftalık MVP tahmini.

**Ön belgede eksik olup eklenenler:** öğrenci ürününün tamamı, çok parçalı soru ve markscheme modeli, cevap değerlendirme, kurum ve rıza
modeli, gelir modeli, geliştirme yöntemi, genişleme stratejisi.

## 2. Karar kaydı

Sütunlar — **Kim:** S = proje sahibi kararı, Ö = mimar önerisi, sahibi onayladı. **İtiraz:** mimarın kayıtlı itirazı varsa.

### Ürün

| ID | Karar | Kim | Not |
|---|---|---|---|
| D-01 | MVP dersi yalnızca Physics (ilk program IB Diploma) | S | |
| D-02 | Tüm Physics soru tipleri kapsamda; sırayla: Paper 1A → Paper 2 sayısal/yapılandırılmış → Paper 1B → uzun açıklamalı | S / Ö | Sıra önerisi mimardan |
| D-03 | İki içerik kökeni: orijinal kaynak sorular (yalnızca kurumun öğrencilerine) ve AI üretimi özgün sorular (insan onaylı, genel erişim) | S | Orijinal soru gösterimi D-46 ile askıda |
| D-04 | Müfredat dışı sorular silinmez, ayrı durumda saklanır | S | |
| D-05 | Önce kapalı kullanım, sonra genel erişim; global, yalnızca İngilizce | S | |
| D-06 | Önce responsive web, sonra native mobil | Ö | |
| D-07 | Ekip: 2–4 geliştirici, 3+ fizik uzmanı incelemeci | S | |
| D-33 | Üç kademe: ücretsiz (seçili Ünite 1 testleri) / Abonelik 1 (sorular + cevaplar) / Abonelik 2 (+ AI geri bildirim, detaylı çözüm, konu özeti). Çözüm ve özetler önceden üretilip incelenir | S / Ö | Önceden üretim önerisi mimardan |
| D-40 | Yaş: 13+ kontrollü üyelik; mümkün olan yerde bağımsız satın alma, olmayan yerde doğrulanabilir veli izni. Sınırlı ülke listesiyle açılış; bilinmeyen ülkede en sıkı kural; veli izni = veli öder | S / Ö | R-02 |
| D-37 | Genişleme: diğer sınavlar ve dersler (Cambridge IGCSE/A-Level, AP, SAT/ACT, ESAT, TMUA…). Veri modeli genel, davranış Physics. İlk genişleme aynı programda yeni ders | S / Ö | R-03 |

### İçerik ve AI

| ID | Karar | Kim | Not |
|---|---|---|---|
| ~~D-08~~ | *(Yürürlükten kalktı → D-44, D-45)* Üretimin kaynağı mevcut sınav soruları; Blueprint'i AI çıkarır, baştan açık | S | **İtiraz:** R-01. Mimar önce clean-room (insan yazımı Blueprint), sonra "AI yolu izne bağlı" önerdi; sahibi baştan açık seçti |
| D-15 | İçerik alma: vision model + kod kontrolleri + örneklemeli insan incelemesi; doğrulanmamış soruda sayfa kırpımı; M0 ölçümüyle kesinleşir | Ö | Askıda (D-46) |
| D-17 | Cevap LLM'den değil hesaplanan çözüm modelinden gelir | Ö | |
| D-23 | Çözüm modeli = bildirimsel formül zinciri; serbest kod çalıştırılmaz. Sığmayan tipler için izole Python sonradan ve sınırlı | Ö | D-17'nin uygulaması |
| D-14 | Diyagramlar koddan ve parametreli şablonlardan; görsel üreten model yok | Ö | |
| D-18 | İnceleme riske göre: kodla doğrulanmış tiplerde 1, uzun açıklamalıda 2 incelemeci; rastgele ikinci inceleme | Ö | |
| D-28 | Üç aday sağlayıcı (Anthropic, OpenAI, Google); rol ataması ölçümle; üretici ve kör çözücü farklı sağlayıcıdan | Ö | |
| D-29 | İçerik hattı varsayılan toplu (batch) mod; etkileşimli işler anında | Ö | |
| D-30 | Üretim orta kademe modelle; zor tiplerde üst kademe | Ö | |
| D-31 | Kaynak içerik gören adımlarda eğitimde kullanmama ve saklamama koşulu zorunlu | Ö | Koşul başvuru gerektirebilir; M0'da teyit |
| D-36 | Prompt ve model değişikliği sürümlüdür; ölçüm eşiğini geçmeden etkinleşmez | Ö | |
| D-26 | AI puanlama: madde bazlı, "AI tahmini" + markscheme + itiraz; fotoğraf önce yazıya çevrilir ve öğrenci onaylar; Abonelik 2'de aylık tavan | S / Ö | AI puanlama kararı sahibinden; mimar MVP sonrası önermişti |
| D-27 | Cevap fotoğrafları hesap boyunca saklanır; reşit olmayanlar dahil | S | **İtiraz:** veri asgariliği. Süre kural tablosunda ayarlanabilir alan (R-02) |

### Veri modeli

| ID | Karar | Kim |
|---|---|---|
| D-19 | İlişkisel iskelet (Question → QuestionVersion → Part → MarkPoint) + JSONB içerik | Ö |
| D-20 | Yapılandırılmış `quantity` düğümü; gösterim bundan üretilir | Ö |
| D-21 | Şema ProseMirror-uyumlu; tek doğruluk kaynağı Pydantic | Ö |
| D-22 | Tek `Question` varlığı + `origin` + zorunlu `rights`; tek erişim katmanı; üretim modülü soru tablolarını okumaz | Ö |
| D-24 | Kapalı grup sistemdeki ilk Organization | Ö |
| D-13 | Matematik gösterimi yalnızca KaTeX; kayıt anında render kontrolü | Ö |

### Platform

| ID | Karar | Kim |
|---|---|---|
| D-09 | Backend Python + FastAPI + Pydantic; modüler monolith, API + worker | Ö |
| D-10 | PostgreSQL (ilişkisel + JSONB + pgvector); S3-uyumlu object storage | Ö |
| D-11 | İş akışı: veritabanında durum makinesi + Postgres tabanlı kuyruk | Ö |
| D-12 | Managed identity provider; roller uygulamada | Ö |
| D-16 | Container PaaS + managed Postgres, AB bölgesi | Ö |
| D-25 | İnceleme ve yönetim arayüzü aynı Next.js uygulamasında; API REST + OpenAPI | Ö |
| D-32 | Görsel matematik alanı; açık sayfalar = ücretsiz sorular + konu sayfaları; içerik koruma temel düzey; WCAG 2.2 AA | Ö |
| D-34 | Yerel + staging + production; gözlem managed servislerle | Ö |
| D-35 | Bağımsız sızma testi genel erişim kapısı | Ö |

### Süreç

| ID | Karar | Kim | Not |
|---|---|---|---|
| D-38 | M1 sonrası iki paralel hat; kapalı beta MCQ + sayısal ile açılır; hukuki danışmanlık şimdi; sabit tarih yok | S / Ö | |
| D-49 | Sıra değişikliği: "M1-G Görünür ürün" aşaması (şema, veritabanı, pilot soruların içe aktarılması, gösterim, admin inceleme/düzenleme, öğrenci önizlemesi) üretim hattından (M3) önce. İlk kapsam admin + öğrenci önizlemesi; önce yerelde, sonra web'e; şekli eksik sorular admin'de görünür, öğrenciden gizli ve yayınlanamaz | S / Ö | 2026-10-11. Gerekçe: 130 pilot soru hazır, gösterecek sistem yok |
| D-50 | Soru şeması v1, onaylı veri mimarisi taslağından şu noktalarda ayrılır: seçenekler blok düğümü değil `mcq` bloğunda; şekiller `stimuli[]` listesinde; düzey tek etiket yerine kâğıt kümesi + içerik düzeyi; her markscheme maddesi 1 puan, alternatif grubu ve yol kavramlarıyla; notlar parça düzeyinde; çözüm modeli yalnızca veri. **Doğruluk kaynağı JSON belgedir, ilişkisel satırlar ondan türetilir.** Sınav yapısına ait sabitler (dört seçenek, parça başına en çok 3 puan, SL/HL) v1'de şemada sabit; ikinci programda sınav biçimi kaydına taşınır | Ö | 2026-10-11. Ayrıntı: DATA_ARCHITECTURE §3.5. Kaynak: Blueprint biçimi analizi ve bağımsız şema incelemesi. **Sahibi onayladı (2026-10-11).** |
| D-51 | M1-G dilim 2 iki pull request'e bölündü: **2a temel** (yerel veritabanı, Alembic, `audit`, asgari `rights`, asgari `syllabus` tabloları ve müfredat sözlüğü) ve **2b content** (soru tabloları, tetikleyiciler, servis). Gerekçe: migration'lar insan onayı ister; okunabilir boyutta kalmalı | S / Ö | 2026-10-12 |
| D-52 | 130 pilot sorunun kökeni `authored`; rights kaydının sahibi platformun kendisidir. `content` servisi M1-G'de yalnızca `authored` kabul eder: `generated` Blueprint gelene kadar (DOMAIN_MODEL §6.2), `source_original` D-47 gereği kapalıdır | S / Ö | 2026-10-12. ⚖️ Geliştirme oturumunda AI yardımıyla yazılmış metnin telif durumu hukuki sorudur; rights kaydı bunu çözmez, yalnızca platformun beyanını kaydeder |
| D-53 | **Geçici kural (M1-G):** `approved` durumuna geçiş için tüm soru sınıflarında tek yetkili onayı yeter; onaylayan audit log'a yazılır. D-18'in 1 / 2 incelemeci kuralı `review` modülüyle (M3) uygulanır | S / Ö | 2026-10-12. D-18'den bilinçli, geçici sapma: yerelde tek kişi çalışıyor, yayın yalnızca öğrenci önizlemesine çıkıyor. **Web'e açılıştan (dilim 9) önce yeniden değerlendirilir** |
| D-54 | Veritabanı katmanı seçimleri: senkron SQLAlchemy 2 + psycopg 3; Python ≥ 3.14 (standart kütüphanedeki UUIDv7 için); kimlikler veritabanında UUIDv7, ön ek yalnızca API sınırında; migration'lar elle yazılır ve modellerle uyumu testle karşılaştırılır; `audit_log` üzerinde UPDATE / DELETE / TRUNCATE'i reddeden tetikleyici; yerelde ve CI'da `pgvector/pgvector:pg17` imajı | Ö | 2026-10-12. Sahibinin onayı 2a birleştirmesiyle. Açık: kuyruk kütüphanesi (M0 ertelenen karar) async bağlantı isterse senkron seçim yeniden değerlendirilir; production PostgreSQL ana sürümü barındırma seçimiyle kesinleşir |
| D-39 | Kod büyük ölçüde Claude ile; tek depo; kritik alanlarda insan onayı zorunlu, diğerlerinde ajan incelemesi + CI | S / Ö | Ek kapılar: mutation testing, aşama sonu uygunluk incelemesi, dış denetim |
| D-41 | Mimari belgeler onaylandı; M0 başladı (2026-10-11) | S | |
| ~~D-42~~ | *(Yürürlükten kalktı → D-44)* Kaynak sınav PDF'leri geliştirme oturumunda (Claude Code) şema tasarımı ve M0 ölçümleri için okunur | S | **İtiraz:** bu kanalın veri saklama koşulu teyit edilmedi; D-31'in gerekçesiyle çelişir. Mimar sentetik örnekle başlamayı önerdi; sahibi riski üstlendi (R-01). PDF'ler ve onlardan kopyalanan sorular depoya ve test verisine girmez |
| D-43 | Yerel git + özel GitHub deposu; kaynak materyal klasörü `.gitignore`'da | S / Ö | Uzak depo henüz açılmadı (sahibinin kararı) |
| D-44 | Sınav kurumlarının belgeleri **yalnızca biçim öğrenmek için** kullanılır: bir sorunun nasıl göründüğü, yapısı ve bilimsel olarak hangi öğeleri taşıması gerektiği. Soru üretimine girdi olmazlar. Soru metni, sayıları ve senaryosu depoya, veritabanına, prompt'a, Blueprint'e ve test verisine girmez. Çıktı, kendi cümlelerimizle yazılmış **biçim profilidir** | S | D-08 ve D-42'nin yerine geçer. Sahibi kalan sorumluluğu üstlendi. **Mimar notu:** belgelerin bir AI oturumunda okunması, sınav kurumunun koşullarıyla hâlâ çelişebilir (R-01) |
| D-45 | Blueprint bir sınav sorusundan türetilmez. Kaynağı müfredat düğümü + biçim profilidir; uzman yazar ya da AI müfredattan önerir ve uzman onaylar. Kaynak soruya lineage yoktur | S / Ö | **Onaylandı (2026-10-11).** Sahibi sınav sorularından bire bir Blueprint çıkarımını tercih ediyordu; mimar bunu yapmayı reddetti (türetilen her sorunun belirli bir telifli soruya bağlanması), sahibi müfredat yolunu kabul etti |
| ~~D-46~~ | *(Yerine geçti → D-47)* Orijinal sınav sorularının sisteme alınması ve gösterimi askıda | Ö | |
| D-47 | **Sahibin kişisel kitaplığı.** Proje sahibi elindeki sınav belgelerini sistemde yalnızca kendisi görmek için saklayabilir. Koşullar: yalnızca sahibin hesabı erişir (kurum, öğrenci ya da açık uç nokta yok); belgeler olduğu gibi (sayfa görüntüsü) gösterilir, metne çevrilmez; hiçbir AI adımına, embedding'e ya da üretime girdi olmaz; depoya girmez | S | Sahibinin değerlendirmesi: kişisel kullanım yasal sorun taşımaz. **Mimar notu:** bu, konuşulan kullanımların en düşük risklisidir, ama hukuki değerlendirme mimara ait değildir (⚖️ R-01). Ürün ticari olarak açıldığında kitaplık teknik olarak ayrık kalmalıdır |
| D-48 | Sınav belgeleri **Blueprint biçimini tasarlamak için referans** olarak kullanılabilir: hangi alanların gerektiği ve değerlerin dağılımı, toplu (aggregate) olarak. Soru başına Blueprint kaydı tutulmaz; soru metni, sayı ya da senaryo alınmaz. Referans seti: örnek (specimen) kâğıtlar | S / Ö | D-44'ün uzantısı; sahibinin önerisi |

## 3. Ertelenen kararlar

| Konu | Ne zaman | Karar ölçütü |
|---|---|---|
| Identity provider | M0 | 13–17 yaş son kullanıcı koşulu, AB veri konumu, SSO maliyeti |
| PaaS, object storage, CDN | M0 | AB bölgesi, worker, managed Postgres + pgvector, fiyat |
| Kuyruk kütüphanesi | M0 | Aynı transaction'da iş ekleme, async, bakım durumu |
| Matematik alanı kütüphanesi | M0 | Lisans, mobil davranış, erişilebilirlik |
| İçerik alma yöntemi | M0 | 50 sayfalık ölçüm |
| Rol başına model | M0 | Ölçüm setleri, no-retention teyidi |
| Embedding modeli | M0–M3 | Benzerlik setinde ayrım gücü |
| Gözlem ve mutation testing araçları | M0 | |
| Şema şablon aracı | M5 | |
| Ödeme sağlayıcısı | M6 | Vergi modeli, veli-öder, reşit olmayan koşulları |
| Native mobil teknolojisi | M7 | Mobil tarayıcı kullanım verisi |
| İkinci ders ve ikinci sınav kurumu | Physics yayındayken | Doğrulanabilirlik, hukuki durum, talep |
| Kullanıcıya özel filigran | Sızıntı gözlenirse | |
| Gerçek zamanlı kanal | Bekleme süresi ölçülünce | |

## 4. Risk kaydı

### R-01 — Sınav kurumu içeriğinin kullanımı · **Yüksek** (D-44 ile azaldı) · ⚖️

- **Birinci elden bulgu (2026-10-11):** incelenen Kasım 2025 sınav dosyalarının kapağında, üçüncü tarafların (özel öğretmenler, tutoring
  ve çalışma hizmetleri, dijital platform işletenler, uygulama geliştiriciler dahil) kullanımını ücretli olsun olmasın yasaklayan ve bunu
  suç olarak niteleyen bir bildirim var; seçilmiş dosya ya da alıntıların kullanımı da yasaklanıyor. O dosyalar klasörden kaldırıldı.
- **Bilinen (arama özeti):** IB materyalinin generative AI aracına sorgu olarak verilmesi yazılı izinsiz yasak; üçüncü taraf ticari
  kullanımı lisans gerektiriyor; ücretli tutoring ve son iki dönem materyali lisans kapsamı dışı.
- **Bilinmeyen:** kurumun statüsü; bildirimin şirketin kurulu olduğu ülkedeki hukuki karşılığı; diğer sınav kurumlarının koşulları.
- **Karar geçmişi:** sahibi önce sınav sorularından üretimi (D-08) ve PDF'lerin geliştirme oturumunda okunmasını (D-42) üstlendi; mimar
  itiraz etti. Bildirim görüldükten sonra strateji değişti: **D-44** (yalnızca biçim öğrenme), **D-45** (Blueprint müfredattan),
  **D-47** (orijinal belgeler yalnızca sahibin kişisel kitaplığında), **D-48** (Blueprint biçimi için referans kullanımı).
- **Kalan risk:**
  1. Biçim öğrenmek için belgelerin bir AI oturumunda okunması, sınav kurumunun koşullarıyla çelişebilir. Sahibi üstlendi.
  2. Üretici model, eğitim verisinden bildiği gerçek bir sınav sorusunu yeniden üretebilir; elimizde karşılaştıracak kaynak havuzu yok.
  3. Sınav kurumu adının ve müfredat başlıklarının ticari üründe kullanımı.
- **Azaltıcılar:** soru metni hiçbir kalıcı yere yazılmaz; biçim profili kendi cümlelerimizle ve yalnızca korunmayan öğelerle (yapı,
  gösterim kuralları, puanlama düzeni) yazılır; Blueprint'te kaynak soru bağı yok; incelemeciler "bilinen bir sınav sorusuna benziyor mu"
  sorusunu açıkça yanıtlar; orijinal içerik yolları rights kapısı ve kill switch arkasında kapalı; hukuki danışmanlık.
- **Sahibi:** proje sahibi + hukuk danışmanı.

### R-02 — Yaş, rıza ve reşit olmayan verisi · **Yüksek** · ⚖️

- **Ne:** veri rızası yaşı ve satın alma ehliyeti ülkeye göre değişir; kural tablosundaki yanlış satır ihlaldir. Reşit olmayanların cevap
  fotoğrafları hesap boyunca saklanıyor (D-27).
- **Azaltıcılar:** sınırlı ülke listesi; bilinmeyende en sıkı kural; sürümlü rıza kaydı; veli-öder; saklama süresi ayarlanabilir alan.
- **Açık:** veli ödemesinin doğrulanabilir izin sayılması; identity ve ödeme sağlayıcılarının reşit olmayan koşulları; LLM sağlayıcısına
  giden öğrenci verisi.

### R-03 — Doğrulama gücü derse göre değişir · **Orta**

- **Ne:** Physics ve Mathematics'te kod güçlü güvence verir; sözel derslerde güvence insan incelemesine kayar ve soru başı maliyet artar.
- **Azaltıcı:** her yeni ders için "doğruluğu neyle garanti ediyoruz" kabul kriteri; inceleme kuralı tipe göre.

### R-04 — Kodun büyük ölçüde ajanla yazılması · **Yüksek**

- **Ne:** testleri geçen ama yanlış şeyi test eden kod; mimari kuralların sessizce aşınması.
- **Azaltıcılar:** kurallar CI'da; testi yazan ile kodu yazan ayrı; mutation testing; kritik alanlarda zorunlu insan onayı; aşama sonu
  uygunluk incelemesi; M6'da dış kod denetimi.

### R-05 — İnceleme darboğazı · **Orta**

- **Ne:** üretimin gerçek maliyeti insan süresi (tahmin: soru başı ~5 dakika; 20 bin soru ~1.700 saat).
- **Azaltıcılar:** hat incelemeciye yalnızca kontrolleri geçen adayları gönderir; onay oranı izlenir; üretim hızı inceleme kapasitesine
  göre ayarlanır.

### R-06 — AI puanlama: maliyet ve hata · **Orta**

- **Ne:** kullanıcı başına sürekli maliyet (tahmin: yazılı cevap ~$0.015, fotoğraf ~$0.02–0.03, orta kademe modelle); yanlış puan güveni zedeler.
- **Azaltıcılar:** madde bazlı karar; sayısal parçalar kodla; "tahmin" sunumu ve itiraz; kota; öğretmenle uyum eşiği; küçük modelin
  yeterliliğinin ölçülmesi.

### R-07 — Formül zincirinin ifade gücü · **Orta**

- **Ne:** bazı soru tipleri (veri analizi, iterasyon) zincire sığmayabilir.
- **Azaltıcı:** M3'te sığma oranı ölçülür; sığmayanlar "kodla doğrulanamaz" tipine girer (iki incelemeci) ya da sınırlı izole Python yolu eklenir.

### R-08 — Şablon kütüphanesinin kapsamı · **Orta**

- **Ne:** şekil gerektiren konular şablon hazır olana kadar üretilemez.
- **Azaltıcı:** şablonlar konu önceliğine göre; şekilsiz sorular önce.

### R-09 — Ortak hata (iki modelin aynı yanılgısı) · **Orta**

- **Ne:** kör çözücünün anlaşması kanıt değil işarettir; zincirin kendisi yanlış fizik içerebilir.
- **Azaltıcı:** farklı sağlayıcı; eleştirmen; insan incelemesi kaldırılmaz; hata ekilmiş setle sürekli ölçüm.

### R-10 — Sağlayıcı bağımlılığı ve koşul değişikliği · **Düşük–orta**

- **Ne:** fiyat, model emekliliği, veri koşulu değişimi; tanıtım fiyatlarının bitmesi.
- **Azaltıcı:** ince adapter; üç aday; ölçüm kapısı model değişimini güvenli kılar; taşınabilir altyapı.

### R-11 — Tek örnekten erken soyutlama · **Düşük–orta**

- **Ne:** çoklu sınav hedefi için bugünden yanlış genelleme.
- **Azaltıcı:** yalnızca veri modelindeki adlar ve anahtarlar genel; davranış Physics; soyutlama ikinci dersle.

## 5. Dış bilgilerin doğrulama durumu

| Bilgi | Durum | Kaynak |
|---|---|---|
| IB IP kuralları (AI yasağı, ticari kullanım, lisans istisnaları) | 🔶 Resmi sayfaların arama özeti; IP sayfası 403, birebir okunamadı | [Rules for use of IB IP](https://ibo.org/terms-and-conditions/intellectual-property/) · [Licensing policies](https://www.ibo.org/become-an-ib-school/ib-publishing/licensing/licensing-policies/) |
| IB DP Physics müfredat yapısı | 🔶 Üçüncü taraf kaynaklar; resmi rehberden teyit edilecek | [Save My Exams — syllabus update](https://www.savemyexams.co.uk/guides/syllabus-updates/ib-physics-syllabus-update/) |
| Anthropic model fiyatları | ✅ Referans tarihi 2026-10-06 | Claude API referansı |
| OpenAI model fiyatları | 🔶 Arama özeti; sayfalar arası ad tutarsızlığı | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) |
| Google model fiyatları | 🔶 Arama özeti; tanıtım fiyatı 2026 sonunda bitiyor | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| Veri saklama ve sıfır saklama koşulları | 🔶 Karışık kaynaklar; sözleşme düzeyinde teyit şart | [Claude API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) |
| Identity provider fiyat ve koşulları | 🔶 Çoğu satıcı blogu; reşit olmayan koşulları büyük ölçüde bulunamadı | [TECH_STACK.md](TECH_STACK.md) §8 |
| PaaS özellikleri | 🔶 İkincil karşılaştırmalar; çelişkili | [TECH_STACK.md](TECH_STACK.md) §9 |
| Procrastinate: aynı transaction'da iş ekleme | 🔶 Belgelerin arama özeti | [Procrastinate docs](https://procrastinate.readthedocs.io) |
| MathLive: MIT, mobil klavye, LaTeX çıktısı | 🔶 Paket dizini kayıtları | [mathlive (npm)](https://npmjs.com/package/mathlive) |
| Maliyet tahminleri (üretim, puanlama, inceleme süresi) | ❓ Mimarın token ve süre varsayımları; ölçülmedi | — |

## 6. Proje sahibinden beklenenler

1. Hukuki danışmanlığın başlatılması ([SECURITY.md](SECURITY.md) §4.3 ve §5 soruları).
2. Kurumun sınav kurumuyla ilişkisinin netleştirilmesi.
3. IB IP ve lisans sayfalarının birebir metni (belgeler özete değil asıl metne dayansın).
4. M0 için: 50 sayfalık örnek set ve her soru tipinden uzman seçimi örnekler.
5. İncelemeci ekibinin haftalık kapasitesi.
6. Bu belgelerin incelenmesi ve onayı.

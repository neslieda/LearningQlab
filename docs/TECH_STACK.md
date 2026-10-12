# TECH_STACK

> **Durum: ONAYLANDI** (2026-10-11, proje sahibi). Değişiklikler [DECISIONS.md](DECISIONS.md) üzerinden işlenir.
> Her karar için: ihtiyaç, alternatifler, seçim ve gerekçe, maliyet, ölçek/güvenlik etkisi, başka çözümün daha iyi olacağı koşul.
>
> **Doğrulama etiketleri:** ✅ resmi kaynaktan teyitli · 🔶 resmi sayfanın arama özeti ya da ikincil kaynak; sözleşme öncesi teyit edilmeli ·
> ❓ doğrulanmadı.

## Özet

| Katman | Seçim | Durum |
|---|---|---|
| Backend | Python + FastAPI + Pydantic, modüler monolith | Onaylı |
| ORM / migration | SQLAlchemy 2 + Alembic | Varsayılan |
| Veritabanı | PostgreSQL (ilişkisel + JSONB + pgvector) | Onaylı |
| Object storage | S3-uyumlu + CDN | Onaylı |
| İş akışı | DB durum makinesi + Postgres tabanlı kuyruk | Onaylı; kütüphane adayı Procrastinate |
| API | REST + OpenAPI | Onaylı |
| Web | Next.js + TypeScript | Onaylı |
| Mobil | Ertelendi (Expo ya da Capacitor) | M7 |
| Kimlik | Managed identity provider | Onaylı; sağlayıcı M0'da |
| Barındırma | Container PaaS + managed Postgres, AB | Onaylı; sağlayıcı M0'da |
| Matematik gösterimi | KaTeX (tek) | Onaylı |
| Matematik girişi | Görsel matematik alanı; aday MathLive | Onaylı; teyit M0 |
| Editör | Tiptap (ProseMirror) | Onaylı |
| Diyagram | Koddan SVG + şablon kütüphanesi | Onaylı |
| İçerik alma | Vision LLM; Docling ile ölçüm | Onaylı; M0 ölçümü |
| LLM | Anthropic / OpenAI / Google adayları, ince iç adapter | Onaylı; roller M0'da |
| Doğrulama | Kendi formül yorumlayıcısı + SymPy + Pint | Onaylı |
| Gözlem | Managed servisler, OpenTelemetry | Onaylı; sağlayıcı M0'da |
| Ödeme | Ertelendi | M6 |

**Bilinçli olarak yok:** Temporal, LangGraph ve agent çerçeveleri, LiteLLM, Z3, self-hosted LLM ve embedding, ayrı vector DB, Redis,
microservice, GraphQL, MathJax.

---

## 1. Backend dili ve çerçevesi

- **İhtiyaç:** API, içerik hattı ve doğrulama için tek kod tabanı; 2–4 kişilik ekip.
- **Alternatifler:**

| Seçenek | Artı | Eksi |
|---|---|---|
| **Python + FastAPI** | Doğrulama kütüphaneleri (SymPy, Pint) ve doküman işleme aynı dilde; Pydantic şeması API, DB doğrulaması ve LLM çıktısında ortak; OpenAPI otomatik | Admin ve auth parçaları hazır gelmez |
| Python + Django | Hazır admin, auth, ORM, migration | Async ve akış (streaming) daha zahmetli; şema paylaşımı için ek katman |
| TypeScript (NestJS) + Python worker | Frontend ile ortak tipler | İki backend servisi, aralarında sözleşme; küçük ekipte yük |

- **Seçim:** FastAPI. Belirleyici olan, soru şemasının tek Pydantic modeli olarak üç yerde kullanılması.
- **Maliyet:** yönetim ekranları elle yazılır (zaten özel ekranlar gerekiyor).
- **Ölçek / güvenlik:** API durumsuz ve yatay ölçeklenir; giriş doğrulaması şemadan gelir.
- **Başka çözüm ne zaman:** ekip Django'da belirgin biçimde daha deneyimliyse; ya da ürün ağırlıklı olarak sıradan CRUD yönetim ekranlarına dönerse.

## 2. Veritabanı

- **İhtiyaç:** ilişkisel bütünlük (cevap → parça → madde), esnek zengin içerik, benzerlik araması, transaction içinde iş kuyruğu.
- **Alternatifler:** PostgreSQL · PostgreSQL + ayrı vector DB · doküman DB (MongoDB) · MySQL.
- **Seçim:** tek PostgreSQL; JSONB içerik blokları, pgvector benzerlik.
- **Gerekçe:** hedef ölçek (on binlerce soru, binlerce kullanıcı, yılda milyonlarca cevap satırı) tek örnek için küçük. Dört ihtiyacı
  tek sistem karşılıyor; kuyruğun veritabanında olması "durum değişti ama iş kayboldu" hatasını ortadan kaldırıyor.
- **Maliyet:** tek managed servis.
- **Ölçek:** önce dikey; okuma yükü artınca kopya; `response` tablosu aya göre bölümlenebilir.
- **Başka çözüm ne zaman:** milyonlarca vektör ve yüksek sorgu hızı gerekirse ayrı vector DB; analitik sorgular işlemsel yükü etkilerse ayrı
  analitik depo.

## 3. Object storage ve CDN

- **Seçim:** S3 API uyumlu depolama + CDN. Sağlayıcı PaaS seçimiyle birlikte belirlenir ❓.
- **Gerekçe:** görseller veritabanında tutulmaz; standart API taşınabilirliği korur.
- **Güvenlik:** hak kısıtlı ve kullanıcı yüklemesi nesneler özel kovada, kısa süreli imzalı bağlantıyla.

## 4. İş akışı ve kuyruk

- **İhtiyaç:** çok adımlı, yeniden denenebilir, insan onayı bekleyen içerik hattı; öğrenci cevabı puanlama kuyruğu.
- **Alternatifler:**

| Seçenek | Artı | Eksi |
|---|---|---|
| **DB durum makinesi + Postgres kuyruğu** | Ek altyapı yok; durum sorgulanabilir; iş, durum değişikliğiyle aynı transaction'da | Yeniden deneme ve idempotency'yi biz tasarlarız |
| Temporal | Güçlü durable execution, olgun | Ayrı küme ya da ücretli bulut, ayrı programlama modeli; bu ölçekte fazla |
| Managed durable workflow (Inngest, Hatchet) | Temporal'dan hafif | Üçüncü taraf bağımlılığı; içerik bir servise daha gider |
| Redis + Celery / Dramatiq | Yaygın | Ek altyapı; transaction dışı kuyruğa ekleme |

- **Seçim:** birincisi. "İnsan onayı bekleme" bir durum alanıdır, durable workflow gerektirmez.
- **Kütüphane adayı:** Procrastinate — Postgres tabanlı, async, yeniden deneme ve periyodik iş desteği; kendi veritabanı bağlantınız
  üzerinden, uygulama verisiyle aynı transaction'da iş ekleme belgelenmiş 🔶. PGQueuer daha hafif bir alternatif; aynı transaction desteği
  teyit edilmedi ❓. Kesin seçim M0'da küçük bir denemeyle.
- **Başka çözüm ne zaman:** adımlar arası karmaşık telafi mantığı, çok uzun süren ve iç içe iş akışları ya da günde on binlerce uzun iş.

## 5. API biçimi

- **Seçim:** REST + OpenAPI; TypeScript istemcisi şemadan üretilir.
- **Alternatif:** GraphQL — iç içe veri için rahat; yetkilendirme, önbellek ve sorgu maliyeti kontrolü zor.
- **Gerekçe:** iki istemci (web, sonra mobil); yayınlanmış soru sürümü tek hazır doküman olarak döner ve CDN'de önbelleklenir.

## 6. Web

- **İhtiyaç:** girişli uygulama alanı, inceleme/editör alanı, arama motorlarına açık sayfalar.
- **Alternatifler:** Next.js · Vite + React SPA · Remix/React Router · SvelteKit.
- **Seçim:** Next.js + TypeScript. Açık sayfalar sunucuda üretilir; uygulama alanı tarayıcıda çalışır.
- **Yanında:** TanStack Query (sunucu verisi), üretilmiş tipli istemci, Tailwind + Radix tabanlı erişilebilir bileşenler. Global durum
  kütüphanesi yok.
- **Başka çözüm ne zaman:** açık sayfa ihtiyacı kalkarsa düz SPA daha basit olur.

## 7. Mobil (ertelendi, M7)

| Seçenek | Artı | Eksi |
|---|---|---|
| Capacitor (web'i sarar) | Gösterim web ile birebir aynı; tek kod tabanı; kamera erişimi | Native his sınırlı |
| Expo (React Native) | Daha iyi native deneyim | Matematik gösterimi ayrı çözüm ister (WebView ya da yeniden yazım); iki arayüz kodu |
| Flutter | Tutarlı performans | Web ile kod paylaşımı yok |

Şimdiki tek şart: API-first ve tek gösterim bileşeni. Karar M7'de, web'in mobil tarayıcıdaki kullanım verisiyle.

## 8. Kimlik doğrulama

- **İhtiyaç:** e-posta ve sosyal giriş, personelde 2FA, ileride okul SSO'su, 13+ kullanıcılar.
- **Alternatifler:** managed provider · uygulama içi auth · hepsi-bir-arada platform (Supabase).
- **Seçim:** managed provider; roller ve izinler uygulama veritabanında.
- **Adaylar (ikincil kaynaklardan; hepsi teyit edilmeli):**

| Aday | Fiyat modeli 🔶 | SSO 🔶 | Reşit olmayan kullanıcı koşulu |
|---|---|---|---|
| Clerk | Aylık geri dönen kullanıcı; geniş ücretsiz kademe, Pro ~$25/ay | Bağlantı başına | ❓ bulunamadı |
| Auth0 | Aylık aktif kullanıcı; B2C ve B2B ayrı basamaklar | Bağlantı başına ek ücret | 🔶 üçüncü taraf kaynak, hesap açan için 18+ şartı bildiriyor; son kullanıcılar için anlamı teyit edilmeli |
| WorkOS AuthKit | 1M aylık kullanıcıya kadar ücretsiz | Bağlantı başına ~$125/ay | ❓ bulunamadı |

- **Seçim ölçütü:** 13–17 yaş son kullanıcılara izin veren koşullar (belirleyici), AB veri konumu, SSO maliyeti, standart OIDC ile çıkış kolaylığı.
- **Başka çözüm ne zaman:** hiçbir aday reşit olmayan kullanıcı koşulunu karşılamazsa uygulama içi auth (açık kaynak kütüphaneyle).

## 9. Barındırma

- **Seçim:** container tabanlı PaaS + managed PostgreSQL, AB bölgesi; yerel + staging + production.
- **Gerekçe:** hedef ölçek veritabanı açısından küçük; küçük ekipte ağ ve IAM kurulumu ürün geliştirmeden zaman çalar.
- **Adaylar (ikincil karşılaştırmalardan 🔶):** Render — AB (Frankfurt), worker servis türü, managed Postgres (PITR, kopya), pgvector;
  Fly.io — çok bölge, worker ayrı süreç grubu, managed Postgres durumu kaynaklarda çelişkili; Railway — kullanım bazlı ucuz, AB ve managed
  Postgres olgunluğu en zayıf. İlk bakışta Render en uygun görünüyor; M0'da resmi sayfalardan teyit edilir.
- **Taşınabilirlik:** container imajı, standart Postgres, S3 API. PaaS'e özgü servis kullanılmaz.
- **Başka çözüm ne zaman:** kurumsal müşteri belirli bulut ya da bölge şartı koşarsa; PaaS faturası eşdeğer bulut maliyetini belirgin aşarsa;
  GPU ihtiyacı doğarsa.

## 10. Matematik gösterimi ve girişi

- **Gösterim:** yalnızca KaTeX. Kayıt anında render kontrolü; MathML çıktısı erişilebilirlik için. MathJax fallback yok (iki renderer
  tutarsızlık üretir). Kayıt kontrolü resmi `katex` npm paketini (sabit sürüm) bir Node alt sürecinde çalıştırır (D-57): API ve worker
  imajında **Node ≥ 24** ile `apps/api/katex` (`npm ci` çıktısı) bulunur; paket kaynak ağacının dışına kurulursa `QLAB_KATEX_DIR`
  ayarlanır. Kimya gösterimi eklentisi (`mhchem`) yüklü değildir.
  - **Başka çözüm ne zaman:** bir ders KaTeX'in desteklemediği gösterimi zorunlu kılarsa. Kimya için KaTeX eklentisi o derste ölçülür.
- **Giriş:** görsel matematik alanı. Aday MathLive: web bileşeni, mobil sanal klavye, LaTeX çıktısı, MIT lisansı 🔶 (resmi depodaki lisans
  dosyası ve güncel sürüm teyit edilmeli). M0'da mobil tarayıcıda denenir.
- **Editör:** Tiptap (ProseMirror tabanlı); soru şeması ProseMirror düğüm yapısıyla uyumlu.

## 11. Diyagramlar

- **Seçim:** grafikler veriden, şemalar parametreli şablonlardan SVG olarak üretilir. Görsel üreten model kullanılmaz.
- **Gerekçe:** görseldeki sayılar formül zinciriyle aynı kaynaktan gelir; alt metin otomatik yazılır.
- **Maliyet:** şablon kütüphanesi zamanla büyür; her yeni konu bir şablon işi.
- **Araç:** grafikler için matplotlib (SVG çıktı) varsayılan; şema şablonları için yaklaşım M5'te seçilir ❓.

## 12. İçerik alma

- **Seçim:** vision LLM + kod kontrolleri + örneklemeli insan incelemesi.
- **Alternatif:** Docling + PaddleOCR + Pix2Text zinciri — içerik dışarı çıkmaz; ağır bağımlılıklar ve araçları uzlaştıran ara kod gerekir.
- **Karar yöntemi:** M0'da 50 sayfalık sette ölçüm: formül birebir doğruluk, yapı doğruluğu, sayfa başı maliyet. Çıkarma bir arayüzün
  arkasındadır.

## 13. LLM sağlayıcıları

- **Seçim:** üç aday, rol başına ölçümle atama; üretici ve kör çözücü farklı sağlayıcıdan. İnce iç adapter (`llm` modülü).
- **Liste fiyatları (1M token, girdi / çıktı):**

| Kademe | Anthropic ✅ (referans 2026-10-06) | OpenAI 🔶 | Google 🔶 |
|---|---|---|---|
| Üst | Claude Opus 5.5: $4 / $20 | GPT-6 Astra: $10 / $50 | Gemini 3.1 Pro Preview: $2 / $12 |
| Orta | Claude Sonnet 5.5: $2 / $10 | GPT-6.1 Sol: $2 / $10 | Gemini 3.8 Flash: $0.75 / $3.75 (2027-01-01'den itibaren $1.50 / $7.50) |
| Küçük | Claude Haiku 5.5: $0.10 / $0.50 | GPT-6 Luna: $0.10 / $0.50 | ❓ |

  Toplu (batch) işlem üç sağlayıcıda yaklaşık yarı fiyat 🔶. OpenAI sayfalarında model adı tutarsızlığı görüldü; birebir teyit gerekir.
- **Veri saklama 🔶:** Anthropic ve OpenAI'da varsayılan 30 gün saklama; sıfır saklama başvuru ve onayla, uç nokta bazında. Anthropic'te
  Claude Fable sınıfı modeller sıfır saklama kapsamı dışında. Google'da ücretli kademede veriler ürün geliştirmede kullanılmıyor; sıfır
  saklama modu teyit edilmedi. **Sonuç:** kaynak içerik gören adımlar için sözleşme düzeyinde teyit M0'ın çıktısıdır.
- **Embedding:** sağlayıcı API'si. Anthropic embedding modeli sunmuyor; OpenAI ya da Google'dan seçilir ❓.
- **Neden LiteLLM yok:** iki-üç sağlayıcı için ince bir arayüz yeter; ek bağımlılık ve hata yüzeyi getirmez.
- **Neden self-host yok:** GPU ve işletme yükü; kalite genelde daha düşük; lisans sorununu çözmez.

## 14. Doğrulama kütüphaneleri

- **Kendi formül yorumlayıcımız:** izinli işlem listesi; ifadeyi kendi ayrıştırıcısıyla ağaca çevirir, SymPy ile hesaplar.
- **SymPy:** sembolik ve sayısal hesap. **Pint:** birim ve boyut.
- **Z3 yok:** Physics sayısal sorularında tek çözümlülük formül zinciriyle sağlanıyor. Mantık ya da kombinatorik ağırlıklı derste yeniden
  değerlendirilir.
- **Güvenlik:** ayrı alt süreç, süre ve bellek sınırı.

## 15. Gözlem

- **Seçim:** managed hata takibi ve log/metrik servisi; OpenTelemetry ile bağlanır (sağlayıcı değişebilir). Sağlayıcı M0'da ❓.
- **LLM gözlemi:** kendi `llm_call` tablomuz; ayrı ürün gerekmez.
- **Uyarılar:** hata oranı, kuyruk birikmesi, günlük LLM harcaması.

## 16. Test araçları

pytest + Hypothesis (özellik tabanlı) · gerçek PostgreSQL ile entegrasyon (container) · Playwright (uçtan uca ve görsel karşılaştırma) ·
import-linter (modül sınırları) · mutation testing (kritik modüller; araç M0'da ❓). Ayrıntı: [TESTING_STRATEGY.md](TESTING_STRATEGY.md).

## 17. Ödeme (ertelendi, M6)

- **Ölçütler:** global satışta vergi yükünü üstlenen "merchant of record" modeli mi, doğrudan ödeme işlemcisi mi; veli-öder akışı
  (üçüncü kişinin ödemesi); reşit olmayan kullanıcı koşulları; abonelik ve kota yönetimi.
- **Durum:** aday karşılaştırması yapılmadı ❓.

## Kaynaklar

- [OpenAI API Pricing](https://developers.openai.com/api/docs/pricing)
- [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Claude API — API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- [Procrastinate documentation](https://procrastinate.readthedocs.io) · [Procrastinate — external connection](https://procrastinate.readthedocs.io/en/stable/howto/production/external_connection.html) · [PgQueuer](https://github.com/janbjorge/PgQueuer/wiki/)
- [MathLive (npm)](https://npmjs.com/package/mathlive)
- [WorkOS — WorkOS vs Auth0 vs Clerk](https://workos.com/blog/workos-vs-auth0-vs-clerk) · [Clerk vs Auth0](https://clerk.com/articles/clerk-vs-auth0-which-authentication-platform-fits-your-team-3) (satıcı blogları; taraflı olabilir)
- [Render — Railway alternatives](https://render.com/articles/best-railway-alternatives) (satıcı blogu; taraflı olabilir)

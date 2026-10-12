# TESTING_STRATEGY

> **Durum: ONAYLANDI** (2026-10-11, proje sahibi). Değişiklikler [DECISIONS.md](DECISIONS.md) üzerinden işlenir.

## 1. Neden bu kadar ağırlık

Kodun büyük kısmını Claude yazacak ve her değişikliğe insan bakmayacak (D-39). Bu durumda testler iki iş görür: davranışı doğrular ve
mimari kuralları zorlar. "Testler geçti" ifadesinin anlam taşıması için testlerin kendisi de denetlenir (§6).

## 2. Katmanlar

| Katman | Kapsam | Araç | Ne zaman |
|---|---|---|---|
| Birim | Saf mantık: yorumlayıcı, kontroller, puanlama kuralları, politika | pytest | Her değişiklik |
| Özellik tabanlı | Yorumlayıcı, birim dönüşümü, tolerans karşılaştırması, şema gidiş-dönüş | Hypothesis | Her değişiklik |
| Entegrasyon | Gerçek PostgreSQL: durum geçişleri, kuyruk, yeniden deneme, idempotency, değişmezlik | pytest + container | Her değişiklik |
| Sözleşme | OpenAPI ↔ üretilen istemci; geriye uyumsuz değişiklik tespiti | Şema karşılaştırma | Her değişiklik |
| Mimari | Modül import kuralları; uç nokta × rol tablosu | import-linter, tablo güdümlü test | Her değişiklik |
| Bileşen | Soru gösterim bileşeni, matematik alanı, editör düğümleri | Bileşen testleri | Her değişiklik |
| Görsel regresyon | Örnek soru setinin ekran görüntüleri (masaüstü ve mobil genişlik) | Playwright | Gösterim ya da KaTeX değişince |
| Uçtan uca | Kritik akışlar | Playwright | Birleştirme öncesi ve staging'de |
| Erişilebilirlik | Otomatik WCAG taraması + elle klavye ve ekran okuyucu kontrolü | axe + elle | Her aşama sonunda |
| AI ölçümü | Çıkarma, sınıflandırma, hata ekilmiş set, üretim, benzerlik, puanlama | Ölçüm takımı | Prompt/model değişince ve dönemsel |
| Mutation | Kritik modüllerde testlerin yeterliliği | Mutation aracı | Kritik modül değişince ve her aşama sonunda |
| Güvenlik | Tarama, yetki testleri, sızma testi | CI + dış ekip | Sürekli + M6 |

## 3. Kritik birim ve özellik testleri

**Formül yorumlayıcısı**
- İzinli olmayan her öğe reddedilir (rastgele üretilmiş ifadelerle).
- Rastgele geçerli ifadelerde sonuç, bağımsız referans hesapla eşleşir.
- Süre ve bellek sınırı aşımı temiz hata verir.
- Birimler: boyutça tutarsız adım reddedilir; dönüşümler gidiş-dönüşte korunur.

**Kod kontrolleri** ([AI_PIPELINE.md](AI_PIPELINE.md) §6)
- Her kontrol için en az bir geçen ve bir kalan örnek; kalan örnek doğru hata kodunu üretir.
- `quantity` ↔ parametre eşleşmesi: tek karakterlik fark yakalanır (`"20"` ile `"20.0"`).

**Puanlama**
- Tolerans sınır değerleri; anlamlı basamak; birim eşdeğerliği (`m/s` ile `km/h`).
- Hata taşıma: yanlış ara değerle doğru yöntem, politika izin veriyorsa yöntem puanını alır.
- Verilen puan hiçbir girdiyle madde puanını aşamaz.

**Şema**
- Pydantic ↔ JSON ↔ editör gidiş-dönüşü içeriği değiştirmez.
- Şema sürümü yükseltme fonksiyonları eski örnekleri geçerli yeni örneğe çevirir.

## 4. Değişmez kural testleri

[DOMAIN_MODEL.md](DOMAIN_MODEL.md) §6'daki her kural bir testtir. Öne çıkanlar:

| Kural | Test |
|---|---|
| `generation` soru tablolarını okumaz | Import denetimi; ihlal CI'ı kırar |
| Rights fail-closed | Rights'ı olmayan, süresi dolmuş ya da bayrağı kapalı içerik işlenmez ve dönmez |
| Kurum dışı hesap `source_original` göremez | Her okuma uç noktası için |
| Kritik kontrol varken yayın olmaz | Arayüzü atlayıp doğrudan API ile denenir |
| Sürüm değişmezliği | İncelemeye girmiş sürümün içeriğini değiştirme denemesi reddedilir |
| Her matematik düğümü render olur | Kayıt yolunda ve yayın öncesi toplu tarama |
| Kill switch | Açıkken kaynak içerik adımları çalışmaz, kuyruktakiler iptal olur |
| Reşit olmayan satın alması | Kural gerektiriyorsa `Consent` olmadan entitlement verilmez |

## 5. Uçtan uca akışlar

1. Kayıt (yaş bandı ve ülke dahil) → ücretsiz soru çözme.
2. MCQ ve sayısal cevap → anında sonuç → markscheme.
3. Süreli deneme: süre sunucuda; sayfa yenileme ve geç teslim.
4. Yazılı açık uçlu cevap → puanlama → itiraz.
5. Fotoğraflı cevap → çeviri → düzeltme → puanlama.
6. Kaynak yükleme → içerik alma → inceleme → yapılandırılmış gösterime geçiş.
7. Üretim → kontroller → inceleme → yayın → öğrencide görünme.
8. Kritik kontrolü kalan adayın yayınlanamaması.
9. Geri çekme: öğrenci listesinden kalkma, geçmiş kayıtların korunması.
10. Kota dolumu ve plan yükseltme; veli-öder akışı (M6).

## 6. Testlerin denetimi

- **Mutation testing:** yorumlayıcı, kod kontrolleri, puanlama kuralları, yetki politikası ve rights modülünde. Hayatta kalan mutasyonlar
  ya testle öldürülür ya da gerekçesiyle kayda geçer.
- **Testi yazan, kodu yazandan farklı:** test yazarı ajan yalnızca spesifikasyonu görür.
- **Kabul testi önce:** her dilimin kabul testi uygulama başlamadan yazılır ve başarısız olduğu görülür.
- **Kapsam oranı hedef değildir:** kritik modüllerde dal kapsamı izlenir ama geçiş ölçütü mutation sonucudur.

## 7. LLM içeren kodun testi

- CI'da gerçek model çağrısı yapılmaz. Çağrılar kayıttan oynatılır; kayıtlar depoda, kaynak içerik içermeyen sentetik örneklerle.
- `llm` adapter'ı için sağlayıcı başına sözleşme testi: şema zorlaması, hata eşlemesi, ret (refusal) ve kesilme durumları.
- Hat mantığı (yeniden deneme, bütçe, önbellek, durum geçişleri) sahte sağlayıcıyla test edilir.

## 8. AI ölçüm takımı

Setler ve ölçüler: [AI_PIPELINE.md](AI_PIPELINE.md) §13.

- Gerçek modellerle, ürünün API anahtarlarıyla çalışır; maliyeti kayda geçer.
- **Yayın kapısı:** prompt ya da model değişikliği, ilgili sette yürürlükteki sürümden kötü değilse etkinleşir.
- Setler sürümlüdür ve eğitim/ayar için kullanılan örneklerle karışmaz: prompt geliştirme bir alt kümede, karar ayrı tutulan kümede.
- Ölçüm setindeki kaynak içerik de rights kurallarına tabidir.
- İtirazlar ve incelemeci düzeltmeleri setlere akar; setler zamanla zorlaşır.
- Etiketleme insandadır (fizik uzmanları). Ajan etiket üretmez.

## 9. Gösterim tutarlılığı

- Sabit örnek set: her blok tipi, uzun formül, geniş tablo, çok parçalı soru, şekilli soru, MCQ.
- Ekran görüntüleri masaüstü ve 375 px genişlikte karşılaştırılır.
- KaTeX sürüm yükseltmesi yalnızca bu test geçerse yapılır.
- Native mobil (M7) aynı setle doğrulanır.

## 10. Ortamlar ve veri

- Yerel: container ile PostgreSQL (`infra/local/compose.yaml`; [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) §13); sentetik veri üreten tohum betiği.
- Veritabanı testleri migration'ları boş bir veritabanına uygulayarak başlar; her test kendi transaction'ında çalışır ve geri alınır.
- Staging: production ile aynı yapı; gerçek öğrenci verisi kopyalanmaz.
- Test verisinde gerçek kaynak soru bulunmaz; sentetik sorular kullanılır.

## 11. Aşama geçiş ölçütleri

Her aşamanın kabul kriteri [ROADMAP.md](ROADMAP.md)'dedir. Ortak ölçütler: CI yeşil; kritik modüllerde mutation sonucu kabul edilmiş;
mimari uygunluk incelemesi yapılmış ve sapmalar kapatılmış ya da [DECISIONS.md](DECISIONS.md)'e yazılmış.

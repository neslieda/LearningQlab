# M1-G dilim 5 — yetki tanımı (API, yetki katmanı, yerel kimlik)

> **Durum: TASLAK — kısmen onaylı.** Tarih: 2026-10-13. Proje sahibi §2'deki dört kararın üçünü onayladı; §3'teki iki nokta açık.
> Bu belge dilim 5'in sözleşmesinin yetki kısmıdır ve dilim ayrı bir oturumda uygulanacağı için yazıldı. Dilim birleşirken içeriği
> [SECURITY.md](../SECURITY.md) §3, [API_DESIGN.md](../API_DESIGN.md) §3 ve [DECISIONS.md](../DECISIONS.md)'e işlenir ve bu dosya kaldırılır.
> Yetki politikası kritik alandır: uygulama güvenlik incelemesi ve insan onayı ister (CLAUDE.md).

## 1. Uç nokta × rol tablosu (öneri)

✔ izinli · — yok (**404** döner; kaynağın varlığı sızdırılmaz) · kimliksiz ya da geçersiz token **401**.
Roller: [DOMAIN_MODEL.md](../DOMAIN_MODEL.md) §3. M1-G'de kurum ve entitlement olmadığı için `student`, `teacher` ve `org_admin` aynı sütundadır.

| # | Uç nokta | student / teacher / org_admin | reviewer | content_admin | platform_admin |
|---|---|---|---|---|---|
| 1 | `GET /healthz` (kimliksiz; içerik yok) | ✔ | ✔ | ✔ | ✔ |
| 2 | `GET /v1/me` | ✔ | ✔ | ✔ | ✔ |
| 3 | `GET /v1/programs/{program}/subjects/{subject}/syllabus` | ✔ | ✔ | ✔ | ✔ |
| 4 | `GET /v1/questions` — yalnızca yayınlanmış; öğrenci görünümü | ✔ | ✔ | ✔ | ✔ |
| 5 | `GET /v1/questions/{id}` — yayınlanmış sürüm; öğrenci görünümü | ✔ | ✔ | ✔ | ✔ |
| 6 | `POST /v1/questions/{id}/check` — cevabı işaretle, doğru cevabı gör (**§3.1 açık**) | ✔ | ✔ | ✔ | ✔ |
| 7 | `GET /v1/admin/questions` — tüm durumlar, filtreli liste | — | ✔ | ✔ | ✔ |
| 8 | `GET /v1/admin/questions/{id}` — soru ve sürümleri | — | ✔ | ✔ | ✔ |
| 9 | `GET /v1/admin/question-versions/{id}` — tam belge, kontroller | — | ✔ | ✔ | ✔ |
| 10 | `GET /v1/admin/question-versions/{id}/history` — işlem kaydı | — | ✔ | ✔ | ✔ |
| 11 | `PUT /v1/admin/question-versions/{id}` — taslağı düzenle | — | ✔ | ✔ | ✔ |
| 12 | `POST /v1/admin/question-versions/{id}/submit` | — | ✔ | ✔ | ✔ |
| 13 | `POST /v1/admin/question-versions/{id}/approve` | — | ✔ | ✔ | ✔ |
| 14 | `POST /v1/admin/question-versions/{id}/request-changes` | — | ✔ | ✔ | ✔ |
| 15 | `POST /v1/admin/question-versions/{id}/reject` | — | ✔ | ✔ | ✔ |
| 16 | `POST /v1/admin/questions/{id}/revisions` — yayınlanmışı düzeltmek için yeni sürüm | — | ✔ | ✔ | ✔ |
| 17 | `POST /v1/admin/question-versions/{id}/publish` | — | — | ✔ | ✔ |
| 18 | `POST /v1/admin/question-versions/{id}/withdraw` | — | — | ✔ | ✔ |
| 19 | `POST /v1/admin/question-versions/{id}/republish` | — | — | ✔ | ✔ |

**Bilerek olmayanlar**

- Yeni soru oluşturma uç noktası: M1-G var olan soruların incelenmesini ve düzeltilmesini kapsar; sorular içe aktarmayla gelir.
- Rights, rol atama, kural tabloları için uç nokta: `platform_admin` işleridir ve M1-G'de komut satırından yapılır.
- Kimliksiz açık uç nokta (sağlık denetimi dışında): açık sayfalar M6'da.
- Entitlement: M1-G'de plan yok; giriş yapmış her hesap yayınlanmış her soruyu görür. Sistem yalnızca yerelde çalışır.

## 2. Proje sahibinin onayladığı kararlar (2026-10-13)

1. **İncelemeci düzenler.** `reviewer` rolü taslağı düzenler (11), incelemeye gönderir (12) ve yayınlanmış soru için yeni sürüm
   açar (16). Yayınlama, geri çekme ve yeniden yayınlama `content_admin` ve `platform_admin`'de kalır. SECURITY §3 tablosuna
   "taslak düzenleme, gönderme, revizyon" satırı eklenir.
2. **Görev ayrımı hazır ama kapalı.** Aynı hesap bir soruyu düzenleyip onaylayabilir (D-53'ün devamı). "Son düzenleyen onaylayamaz"
   kuralı kodda yazılır ve test edilir, bir ayarla kapalı gelir; her onayın audit kaydında onaylayanın aynı zamanda son düzenleyen
   olup olmadığı işaretlenir. **Kuralın açılması web'e açılışın (dilim 9) koşuludur.**
3. **Öğrenci, cevabını işaretledikten sonra doğru cevabı görür; öğrenciye görünen her şey İngilizcedir.** (Sahibinin ifadesi;
   uygulanışı §3'te açık.)
4. **Yerel kimlik: yerelde imzalanmış token.** API, gerçek sağlayıcıda olduğu gibi imzalı token doğrular (imza, süre, hedef, veren);
   yerelde token'ı bu makinede üretilen bir anahtarla küçük bir komut üretir (rol başına bir geliştirme hesabı). Geliştirme anahtarı
   depoya girmez; uygulama yerel ortam dışında bu anahtarla açılmayı reddeder. Dilim 9'da yalnızca anahtar kaynağı değişir.

## 3. Açık noktalar (uygulamadan önce sahibinin kararı gerekir)

### 3.1 Cevap nasıl açılır

M1-G'de öğrenci cevaplarını saklayan yapı yoktur (deneme ve cevap kayıtları M2'de; ROADMAP "Bilinen sınırlar").

| Seçenek | Ne olur | Bedel |
|---|---|---|
| **A (öneri): cevap sunucuya gider, saklanmaz** | Öğrenci seçeneğini `POST …/check` ile gönderir; sunucu doğru/yanlış bilgisini ve doğru seçeneği döndürür, cevabı kaydetmez. Doğru cevap, cevap gönderilmeden hiçbir yanıtta yer almaz (sunucu zorlar). Yazılı parçada öğrenci parçayı "cevapladım" diye işaretleyince o parçanın markscheme'i döner | Cevap geçmişi, deneme ve analitik yok (M2) |
| B: cevaplar şimdiden saklanır | Dilime `attempt` ve `response` tabloları eklenir | M2'nin bir parçası öne alınır; yeni tablolar ve migration; öğrenci verisi (R-02 ⚖️ açık); ROADMAP sınırı değişir |
| C: yalnızca çoktan seçmeli | A gibi, ama yazılı parçaların markscheme'i öğrenci rolüne hiç dönmez | Paper 2 ve 1B sorularında önizleme cevapsız kalır |

### 3.2 Türkçe açıklamalar

Çözüm açıklamaları, çeldirici gerekçeleri, kazanım cümleleri ve şekil tarifleri Türkçedir; soru metni, markscheme maddeleri ve notlar
İngilizcedir ([SINIRLAR.md](../SINIRLAR.md) §7.1).

| Seçenek | Ne olur | Bedel |
|---|---|---|
| **A (öneri): öğrenciye kapalı, çeviri ayrı iş** | Öğrenciye yalnızca doğru seçenek ve İngilizce markscheme döner; açıklama ve gerekçeler öğrenci görünümüne girmez. Çeviri (ve eğitmen incelemesi) ayrı bir içerik işi olarak planlanır | Önizlemede "neden" açıklaması olmaz |
| B: dilim 5'ten önce çevrilir | Açıklamalar kaynak Markdown'da İngilizceye çevrilir, JSON yeniden üretilir; cevapla birlikte açılır | Araya bir içerik dilimi girer; incelenmemiş çeviri öğrenci rolüne açılır (yalnızca yerelde) |

## 4. Öğrenci görünümü

Öğrenci rolüne dönen belge ayrı bir tiptir; `content.get_published_version` çıktısı olduğu gibi verilmez
([DATA_ARCHITECTURE.md](../DATA_ARCHITECTURE.md) §2.2, devreden 5).

- **Girer:** soru metni, seçenekler (çoktan seçmelide), parçaların etiket, gövde, puan ve komut sözcüğü, tablolar, şekil yer tutucusu
  (şekli olan soru zaten yayınlanamaz), sınav bölümü, düzey, toplam puan.
- **Hiç girmez:** personel hesap kimlikleri, şekil tarifleri, çözüm modeli, kontrol sonuçları, kaynak anahtarı, kazanım cümlesi,
  kuralla doldurulan üst veri (seçenek türü, cevap türü, ölçme hedefi), Türkçe metinler (§3.2).
- **Yalnızca cevap işaretlendikten sonra:** doğru seçenek; yazılı parçada o parçanın puan maddeleri ve notları (§3.1).
- Sunucu zorlar: görünüm sunucuda kurulur; istemcinin süzmesine bırakılmaz. Her uç nokta × rol testi, öğrenci rolüne dönen yanıtta
  cevap alanlarının bulunmadığını da doğrular.

## 5. Teknik çerçeve

- **Tek politika katmanı, varsayılan ret.** Her uç nokta gerekli rolü beyan eder; beyan etmeyen uç nokta uygulama açılırken hata
  verir. §1'deki tablo test verisidir: her uç nokta × her rol için otomatik test çalışır; tabloya girmemiş uç nokta CI'ı geçemez
  (CLAUDE.md kural 9).
- **Roller veritabanında** (D-12): hesap tablosu ve rol ataması tablosu (`identity`, `organizations` modülleri). Rol atamaları
  audit'e yazılır. Personel rolleri için iki adımlı doğrulama denetimi gerçek sağlayıcıyla (dilim 9) gelir.
- **İşlemi yapan** audit kaydına hesabın opak kimliğiyle geçer; ad ya da e-posta yazılmaz.
- **Hatalar** `application/problem+json`; kararlı `code` alanı. İçerik değişmişken onay ya da yayın (içerik özeti uyuşmuyor) **409**.
- **Onay, yayın, yeniden yayın** istekleri çağıranın gördüğü içeriğin özetini taşır (D-56).
- **Geri çekme, ret, düzeltme isteme** yanıtları içerik döndürmez.
- **Kimlikler** API sınırında ön eklidir (`q_…`, `qv_…`).
- **Renderer denetimi** uygulama açılışında yapılır (`math.ensure_renderer`, D-57).
- **OpenAPI** depoda tutulur; TypeScript istemcisi ondan üretilir ve elle düzenlenmez.

## 6. Dilim 5'in kabul ölçütleri (yetki kısmı)

- §1 tablosundaki her hücre bir testtir (19 uç nokta × 6 rol + kimliksiz).
- Öğrenci rolü admin uç noktalarının hiçbirinden veri alamaz ve kaynağın var olup olmadığını öğrenemez.
- Öğrenci rolüne dönen hiçbir yanıt, cevap gönderilmeden doğru cevabı ya da markscheme'i içermez.
- Onaylanmamış, kontrolü eksik ya da görseli olan soru API doğrudan çağrılsa da yayınlanamaz.
- Yerel geliştirme anahtarıyla imzalanmış token, yerel ortam dışında kabul edilmez; süresi dolmuş, başka hedefe kesilmiş ya da imzası
  bozuk token 401 alır.
- "Son düzenleyen onaylayamaz" kuralı ayar açıkken reddeder, kapalıyken izin verir ve audit kaydına işaret düşer.

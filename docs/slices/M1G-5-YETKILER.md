# M1-G dilim 5 — yetki tanımı (API, yetki katmanı, yerel kimlik)

> **Durum: ONAYLANDI** (2026-10-13, proje sahibi; kararlar §2 ve D-59). Uygulama ayrıca güvenlik incelemesi ve birleştirme onayı ister.
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
| 6 | `POST /v1/questions/{id}/check` — cevabı gönder, doğru cevabı gör (§3) | ✔ | ✔ | ✔ | ✔ |
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
3. **Öğrenci, cevabını gönderdikten sonra doğru cevabı görür; cevap saklanmaz** (§3).
4. **Yerel kimlik: yerelde imzalanmış token.** API, gerçek sağlayıcıda olduğu gibi imzalı token doğrular (imza, süre, hedef, veren);
   yerelde token'ı bu makinede üretilen bir anahtarla küçük bir komut üretir (rol başına bir geliştirme hesabı). Geliştirme anahtarı
   depoya girmez; uygulama yerel ortam dışında bu anahtarla açılmayı reddeder. Dilim 9'da yalnızca anahtar kaynağı değişir.

5. **Sistemde kayıtlı her içerik İngilizcedir; öğrencinin cevabı da İngilizce beklenir.** Öğrenci Türkçe yazarsa sistem İngilizce
   yazması için uyarı döndürür (§3).

## 3. Cevap gönderme ve dil (`POST /v1/questions/{id}/check`)

- **Cevap sunucuya gider, saklanmaz.** M1-G'de deneme ve cevap kaydı yoktur (M2). İstek ve yanıt hiçbir tabloya yazılmaz; audit
  kaydına da öğrencinin cevabı girmez.
- **Çoktan seçmeli:** istek seçilen seçeneği taşır; yanıt doğru/yanlış bilgisini ve doğru seçeneği döndürür.
- **Yazılı parça:** istek parça kimliğini ve öğrencinin yazdığı metni taşır; yanıt o parçanın puan maddelerini ve notlarını döndürür.
  Cevap **puanlanmaz** (AI puanlama M4'te); öğrenci kendi cevabını markscheme ile karşılaştırır.
- **Sunucu zorlar:** doğru seçenek ve markscheme, bir cevap gönderilmeden hiçbir yanıtta yer almaz. Boş cevap kabul edilmez.
- **Dil uyarısı:** yazılı cevap İngilizce görünmüyorsa yanıt bir uyarı alanı taşır ("cevabınızı İngilizce yazın"); markscheme yine
  döner. Tespit belirlenimci ve yereldir (Türkçeye özgü harfler ve sık sözcükler gibi basit bir kural); LLM kullanılmaz, cevap
  hiçbir dış servise gitmez. Kural kaba bir sezgidir: kısa ya da yalnızca sayı ve formülden oluşan cevaplarda uyarı vermez; yanlış
  uyarı verebilir. Bu bir yardım iletisidir, engel değildir.
- **Sınır:** metin uzunluğu sınırlıdır; hız sınırı web'e açılışla (dilim 9) gelir.

### 3.1 Türkçe içerik (kapandı, D-60)

Pilot soruların Türkçe alanları (çözüm açıklamaları, çeldirici gerekçeleri, kazanım cümleleri, şekil tarifleri) 2026-10-15'te
İngilizceye çevrildi; Türkçe harfli içerik artık kaydedilmez ([M1G-EN-INGILIZCE.md](M1G-EN-INGILIZCE.md)). Açıklamaların cevapla
birlikte öğrenciye açılması öğrenci yanıt tipini değiştirdiği için dilim 8'dedir; o zamana kadar öğrenci görünümü aşağıdaki gibi kalır.

## 4. Öğrenci görünümü

Öğrenci rolüne dönen belge ayrı bir tiptir; `content.get_published_version` çıktısı olduğu gibi verilmez
([DATA_ARCHITECTURE.md](../DATA_ARCHITECTURE.md) §2.2, devreden 5).

- **Girer:** soru metni, seçenekler (çoktan seçmelide), parçaların etiket, gövde, puan ve komut sözcüğü, tablolar, şekil yer tutucusu
  (şekli olan soru zaten yayınlanamaz), sınav bölümü, düzey, toplam puan.
- **Hiç girmez:** personel hesap kimlikleri, şekil tarifleri, çözüm modeli, kontrol sonuçları, kaynak anahtarı, kazanım cümlesi,
  kuralla doldurulan üst veri (seçenek türü, cevap türü, ölçme hedefi), çözüm açıklaması ve çeldirici gerekçeleri (§3.1).
- **Yalnızca cevap gönderildikten sonra:** doğru seçenek; yazılı parçada o parçanın puan maddeleri ve notları (§3).
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
- Öğrenci rolüne dönen hiçbir yanıt, cevap gönderilmeden doğru cevabı ya da markscheme'i içermez; gönderilen cevap hiçbir tabloya
  yazılmaz.
- Türkçe yazılmış bir cevap dil uyarısı alır; İngilizce bir cevap, yalnızca sayı ve formülden oluşan bir cevap almaz.
- Öğrenci rolüne dönen hiçbir yanıtta açıklama, gerekçe, kazanım ya da şekil tarifi alanı bulunmaz (dilim 8'e kadar).
- Onaylanmamış, kontrolü eksik ya da görseli olan soru API doğrudan çağrılsa da yayınlanamaz.
- Yerel geliştirme anahtarıyla imzalanmış token, yerel ortam dışında kabul edilmez; süresi dolmuş, başka hedefe kesilmiş ya da imzası
  bozuk token 401 alır.
- "Son düzenleyen onaylayamaz" kuralı ayar açıkken reddeder, kapalıyken izin verir ve audit kaydına işaret düşer.

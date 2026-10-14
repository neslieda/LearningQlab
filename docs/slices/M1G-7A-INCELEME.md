# M1-G dilim 7a — admin inceleme ekranları

> **Durum: TASLAK** (2026-10-14, mimar oturumu). Dilim 7 ikiye bölündü: **7a** inceleme ve karar ekranları (bu belge), **7b** yerinde
> düzenleme (Tiptap editörü). Dilim 6'nın (PR #3) üstüne kurulur. Dilim birleşirken içeriği kalıcı belgelere işlenir ve bu dosya kaldırılır.

## 1. Amaç ve kapsam

Amaç: incelemeci ve içerik yöneticisinin soruları tarayıp her sürümü sınav düzeninde, kontrolleri ve geçmişiyle görmesi ve kararlarını
(gönderme, onay, düzeltme isteme, ret, yayın, geri çekme, yeniden yayın, revizyon açma) arayüzden vermesi.

Kapsam dışı: içerik düzenleme (7b), yeni soru oluşturma, rol yönetimi, öğrenci ekranı (dilim 8).

Kritik alan: hayır. API değişmez; yetkiyi API zorlar, arayüzdeki rol denetimi yalnızca kolaylıktır.

## 2. Sayfalar (`apps/web/src/app/admin/…`)

Hepsi istemci bileşeni; veri `useApi()` + TanStack Query ile. Personel rolü (`reviewer`, `content_admin`, `platform_admin`) yoksa sayfa
"This area is for staff" der ve hiçbir admin isteği göndermez. Giriş yoksa `/dev/sign-in`'e bağlantı verir.

### 2.1 `/admin/questions` — liste

- Süzgeçler (URL sorgu parametresinde durur, geri tuşu çalışır): durum, sınav bölümü, soru sınıfı, düzey, "görseli bekleyen".
- Tablo: kaynak anahtarı (yoksa kısa kimlik), sınıf, bölüm, düzeyler, puan, son sürümün numarası ve durumu (rozet; renk tek ipucu
  değil, metin de var), "yayında" işareti, "üzerinde çalışılan sürüm" işareti. Satır, soru sayfasına bağlantıdır.
- "Load more" düğmesi `next_cursor` ile sonraki sayfayı ekler; sayfa boyutu 50.
- Boş sonuç ve hata durumları görünür.

### 2.2 `/admin/questions/[id]` — soru

- Üst bilgi: kaynak anahtarı, köken, oluşturan (opak kimlik), oluşturulma zamanı.
- Sürümler tablosu (eskiden yeniye): numara, durum, içerik özetinin ilk 8 karakteri, güncellenme zamanı, "görsel bekliyor"; her satır
  sürüm sayfasına bağlantı.
- "Open revision" düğmesi: üzerinde çalışılan sürüm yoksa görünür; başarıda yeni sürümün sayfasına gider.

### 2.3 `/admin/versions/[id]` — sürüm

- Başlık: soru bağlantısı, sürüm numarası, durum rozeti, içerik özetinin ilk 12 karakteri.
- İçerik: `QuestionDocumentView` (gösterim bileşeninden; başka yolla içerik çizilmez). "Show answers" anahtarı, varsayılan açık.
- Kontroller: her kontrol için kod, önem (critical / warning), sonuç (passed / failed / not applicable); `detail` katlanabilir JSON
  olarak (metin; HTML olarak değil). Kontrol yoksa "No checks recorded for this content".
- "Görsel bekliyor" işaretliyse açık bir not: "Has figures without verified images: can be approved, cannot be published (D-49)".
- Geçmiş: `history` kayıtları eskiden yeniye; zaman (yerel saat), eylem, işlemi yapan (opak kimlik; kendi hesabıysa "you"), varsa
  önceki durum → durum, gerekçe, başarısız kontroller, `approver_is_last_editor`.
- **Karar paneli:** §3.

## 3. Karar paneli

`availableActions(status, roles, hasWorkingVersion)` saf bir işlevdir (`apps/web/src/lib/decisions.ts`) ve paneli o çizer:

| Durum | Eylem | Roller | İstek |
|---|---|---|---|
| `draft` | Submit for review | personel | `POST …/submit` |
| `in_review` | Approve | personel | `POST …/approve` + `expected_content_sha256` (sayfada gösterilen içeriğin özeti) |
| `in_review`, `approved` | Request changes | personel | `POST …/request-changes` + gerekçe |
| `in_review` | Reject | personel | `POST …/reject` + gerekçe; onay penceresi ("cannot be undone") |
| `approved` | Publish | `content_admin`, `platform_admin` | `POST …/publish` + özet |
| `published` | Withdraw | `content_admin`, `platform_admin` | `POST …/withdraw` + gerekçe |
| `withdrawn` | Republish | `content_admin`, `platform_admin` | `POST …/republish` + özet + gerekçe |
| `published`, `withdrawn`, `rejected` (çalışılan sürüm yoksa) | Open revision | personel | `POST …/questions/{id}/revisions` |

- `auto_checking` ve `needs_fix` durumunda karar yoktur (`needs_fix` düzeltme 7b'de; panel "Waiting for changes" der).
- **Gerekçe alanı:** 1–500 karakter, kırpılmış; alanın yanında sabit uyarı: "Describe the content, not a person. Do not paste
  question text. Reasons are kept permanently." (DATA_ARCHITECTURE §2.2 devreden 8, ⚖️).
- Onay ve yayın, kullanıcının **gördüğü** sürümün özetini gönderir; sürüm arada değiştiyse API 409 `stale_content` döner ve panel
  "This version changed since you opened it. Reload to see the current content." der, yeniden yükleme düğmesi verir.
- Her karardan sonra sürüm, soru, liste ve geçmiş sorguları geçersiz kılınır; panel yeni durumu gösterir. Düğme istek sürerken kilitli
  (çift gönderim yok).
- Hata eşlemesi (problem `code` → metin): `not_publishable` → nedenlerin listesi (`critical_checks_failed` → "A required check has
  not passed", `unverified_visuals` → "Figures are not verified yet", `rights_denied` → "Rights do not permit display");
  `self_approval_forbidden` → "You edited this version last, so someone else must approve it"; `invalid_transition` → "This action is
  not possible in the current state" + yeniden yükleme; `working_version_exists` → "A version is already being worked on" + ona
  bağlantı yok (bilinmiyor; soru sayfasına bağlantı); `not_found` → "Not found or not visible to you"; 401 → oturum bitti, giriş
  bağlantısı; diğerleri → "Something went wrong" + `code`.

## 4. Testler

- **Birim (Vitest, `apps/web`):** `availableActions` tablonun her hücresi (8 durum × rol kümeleri × çalışılan sürüm var/yok);
  hata eşlemesi işlevi her `code` için.
- **Uçtan uca (Playwright, Docker'daki aynı imaj, API taklit edilir):** `page.route` ile `/api/v1/**` yanıtları sabit verilerle taklit
  edilir (gerçek API ve veritabanı gerekmez). Akışlar: personel olmayan rol admin sayfasında istek göndermez; liste süzgeci URL'ye
  yazılır ve istek parametresine geçer; "Load more"; sürüm sayfası içerik + kontroller + geçmiş; onay isteği doğru özeti taşır; 409
  `stale_content` mesajı; yayın 409 `not_publishable` nedenleri; gerekçe uyarısı görünür ve boş gerekçe gönderilemez; incelemeci
  "Publish" görmez; 375 px'de sayfa yatay kaymaz.
- `apps/web` için Vitest bu dilimde eklenir (gösterim paketindeki kurulumun aynısı).

## 5. Mimar kararları — sahibinin onayını bekliyor

1. Dilim 7'nin 7a / 7b diye bölünmesi.
2. Uçtan uca testler gerçek API yerine taklit yanıtlarla; gerçek API'yle bir duman testi dilim 8'de (öğrenci akışıyla birlikte).
3. Personel görünümünde "Show answers" varsayılan açık.

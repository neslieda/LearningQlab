# M1-G dilim 5 — dilim tanımı ve donmuş sözleşme

> **Durum: TASLAK** (2026-10-14, mimar oturumu). Yetki kısmı [M1G-5-YETKILER.md](M1G-5-YETKILER.md) ve D-59 ile onaylıdır; bu belge onun
> üstüne dilimin geri kalanını tanımlar. §8'deki mimar kararları **sahibinin onayını bekliyor**. Dilim birleşirken içeriği kalıcı
> belgelere işlenir ve bu dosya kaldırılır.

## 1. Amaç ve kapsam

Amaç: içe aktarılmış soruların incelenmesi, düzeltilmesi, yayınlanması ve yayınlananların öğrenci görünümünde okunması için HTTP API;
tek yetki katmanı; yerel geliştirme kimliği; OpenAPI ve ondan üretilen TypeScript istemcisi.

Kapsam dışı: web arayüzü (dilim 6–8), gerçek kimlik sağlayıcısı ve dağıtım (dilim 9), yeni soru oluşturma uç noktası, rights / rol
yönetimi uç noktaları, entitlement, deneme ve cevap kaydı, hız sınırı, `Idempotency-Key` (§8.6).

Kritik alan: **evet** (yetki politikası, migration). CI + bağımsız inceleme + güvenlik incelemesi + insan onayı.

## 2. Donmuş sözleşme (değiştirilmez; yanlış görünüyorsa dur ve bildir)

| Dosya | İçerik |
|---|---|
| `apps/api/openapi.json` | Kesin API sözleşmesi (üretilir: `python -m qlab.api.openapi`) |
| `apps/api/src/qlab/api/schemas.py` | İstek ve yanıt tipleri |
| `apps/api/src/qlab/api/policy.py` | Uç nokta × rol tablosu (`ENDPOINT_POLICY`), `PolicyRoute`, `Principal` |
| `apps/api/src/qlab/api/errors.py` | `problem+json`, kararlı `code` değerleri, servis hatası → yanıt eşlemesi |
| `apps/api/src/qlab/api/{app,deps,ids,settings,openapi}.py`, `routers/common.py` | Uygulama, transaction yardımcıları, kimlik kodlaması, ayarlar |
| `apps/api/src/qlab/api/routers/{system,learner,admin}.py` | Uç nokta imzaları ve belge dizgileri (gövdeler uygulanacak) |
| `apps/api/src/qlab/identity/**`, `organizations/**` | Hesap, token doğrulama, geliştirme anahtarı, rol ataması |
| `apps/api/migrations/versions/0005_identity_roles.py` | `account`, `role_assignment` |
| `content.service`: `approve(..., forbid_self_approval)`, `SelfApprovalForbidden`, `VersionSummary`, `QuestionListItem`, `ListFilter`, `summarize`, `list_questions`, `list_published`, `get_history` imzaları | Görev ayrımı kuralı (uygulandı); liste ve geçmiş (uygulanacak) |
| `syllabus.service`: `TreeNode`, `SyllabusTree`, `get_tree` imzası | Müfredat ağacı (uygulanacak) |
| `apps/api/tests/api/support.py`, `conftest.py` | API testlerinin ortak düzeneği (`api` fixture) |

## 3. Davranış kuralları

### 3.1 Kimlik ve yetki (uygulandı; test edilecek)

- `Authorization: Bearer <token>`; token EdDSA (Ed25519) imzalı JWT; zorunlu alanlar `iss`, `sub`, `aud`, `exp`, `iat`. Süre toleransı
  yok; ömür en çok 24 saat; uzunluk en çok 4096 karakter. Roller token'da **değildir**, her istekte veritabanından okunur (D-12).
- Sıra: (1) uç nokta politika tablosunda yoksa 404; (2) `/healthz` dışında token yoksa ya da geçersizse **401** `unauthenticated`
  (`WWW-Authenticate: Bearer`); (3) token geçerli ama `iss`+`sub` için hesap yoksa ya da hesap kapatılmışsa **401**; (4) hesabın
  uç noktanın izin verdiği rollerden hiçbiri yoksa **404** `not_found` — var olmayan bir yolun yanıtıyla bayt bayt aynı.
- Yetki kararı gövde okunmadan ve parametreler doğrulanmadan önce verilir: yetkisiz çağıran bozuk gövde de gönderse 404 (ya da 401)
  alır, 422 almaz.
- Hiç rolü olmayan hesap `/healthz` dışında her yerden 404 alır. Rol geri alınınca bir sonraki istekte etkisini gösterir.
- Yanıtlar nedenini söylemez (süresi dolmuş / imza bozuk / hesap yok ayrımı yapılmaz).
- Başlangıç denetimleri (`create_app`): politika tablosu ile yollar bire bir eşleşmezse `PolicyError`; `local` dışında geliştirme
  anahtarı ya da geliştirme vereni (`qlab-local-dev`) `StartupError`; `local` dışında görev ayrımı kapalıysa `StartupError`;
  `local` dışında kimlik sağlayıcısı yoksa `StartupError`; KaTeX çalışmıyorsa `RendererUnavailable`.

### 3.2 Kimlikler ve sayfalama

- `q_…`, `qv_…`, `acc_…`: ön ek + alt çizgi + 26 karakter küçük harf Crockford base32 (`qlab.api.ids`). Yoldaki kimlik bozuksa 404.
- Audit kaydındaki `actor`, çağıranın `acc_…` kimliğidir (`Principal.actor`).
- Listeler soru kimliğine göre artan sıradadır. `next_cursor`, sayfadaki son sorunun `q_…` kimliğidir; daha fazla kayıt yoksa `null`
  (bunu bilmek için servisten `limit + 1` kayıt istenir). İstemci imleci opak sayar. Çözülemeyen imleç: **422** `invalid_cursor`.

### 3.3 Öğrenci görünümü (`qlab/api/learner_view.py`, uygulanacak)

`content.QuestionVersionView` → `LearnerQuestion` dönüşümü **izin listesiyle** yapılır: hedef tipteki her alan belgeden tek tek
okunur; belge `model_dump` edilip alan silinerek kurulmaz. Giren ve girmeyen alanlar [M1G-5-YETKILER.md](M1G-5-YETKILER.md) §4.

| Hedef | Kaynak |
|---|---|
| `id`, `version_id` | soru ve sürüm kimlikleri (ön ekli) |
| `question_class`, `exam_section`, `levels`, `total_marks`, `stem` | belgeden aynen |
| `stimuli[]` | yalnızca `id`, `kind` |
| `mcq` | `option_layout`, `column_headers`, `statements`, `options[]` (yalnızca `key`, `cells`) |
| `parts[]` | `id`, `label`, `lead_in`, `body`, `marks`, `command_term`, `stimulus_refs` |

`POST /v1/questions/{id}/check` (yayınlanmış sürüm üzerinde, salt okunur transaction):

- `mcq` cevabı + çoktan seçmeli soru → `McqCheckResult(correct = selected_key == correct_key, correct_key)`.
- `written` cevabı + yapılandırılmış soru + var olan `part_id` → o parçanın `marks`, `marks_capped`, `mark_points[]`
  (`id`, `content`, `kind`, `alternative_group`, `route`, `accept_range`), `notes[]` (`kind`, `content`, `mark_point_id`) ve dil uyarısı.
  Başka parçanın maddeleri dönmez. `solution_step`, açıklama, gerekçe dönmez.
- Uyuşmayan tür ya da bilinmeyen `part_id`: **422** `answer_does_not_fit`. Boş ya da yalnızca boşluk cevap: 422 `validation_failed`.
- Hiçbir şey yazılmaz: tablo satır sayıları ve audit kaydı değişmez; cevap metni log'a da yazılmaz.

### 3.4 Dil sezgisi (`qlab/api/language.py`, uygulanacak)

`looks_non_english(text: str) -> bool`; saf, belirlenimci, dış çağrı yok.

1. Sözcükler: ardışık harf dizileri (Unicode), küçük harfe çevrilir; tek harfli sözcükler sayılmaz.
2. Üçten az sözcük varsa → `False` (kısa cevap, sayı, formül).
3. Türkçeye özgü güçlü harflerden (`ğ`, `ı`, `ş`, `İ`, `Ğ`, `Ş`) birini içeren en az bir sözcük varsa → `True`.
   (`ç`, `ö`, `ü` tek başına sayılmaz: özel adlarda geçer.)
4. Aksi halde: küçük, sabit bir Türkçe sık sözcük kümesinden en az iki **farklı** sözcük geçiyorsa ve bu sayı, sabit İngilizce sık sözcük
   kümesinden geçen farklı sözcük sayısından büyükse → `True`. İki küme kesişmez ve modülde `frozenset` olarak durur.
5. Aksi halde `False`.

Uyarı: `LanguageWarning(code="answer_not_english", message="Please write your answer in English.")`.

### 3.5 Personel uç noktaları (`routers/admin.py`, uygulanacak)

Her uç nokta ilgili `content.service` işlevini çağırır; hata eşlemesi `errors.from_service_error` içindedir (uç nokta `try/except`
yazmaz). Yazan uç noktalar `deps.writing`, okuyanlar `deps.reading` kullanır.

| Uç nokta | Servis | Not |
|---|---|---|
| `GET /v1/admin/questions` | `list_questions` | Süzgeçler son sürüme uygulanır |
| `GET /v1/admin/questions/{id}` | `get_question` + `list_versions` | Sürümler `summarize` ile; içerik dönmez |
| `POST …/questions/{id}/revisions` | `start_revision` | 201; `AdminVersion` |
| `GET …/question-versions/{id}` | `get_version` + `get_checks` | |
| `GET …/{id}/history` | `get_history` | `action` ön eksiz; `data.failed` → `failed_checks`; `based_on`, `superseded_by` → `qv_…` |
| `PUT …/{id}` | `update_draft` | Yanıt `AdminVersion` |
| `POST …/submit`, `request-changes`, `reject`, `publish`, `withdraw`, `republish` | aynı adlı işlev | Yanıt `VersionStateOut`; içerik dönmez |
| `POST …/approve` | `approve(..., forbid_self_approval=settings.forbid_self_approval)` | 403 `self_approval_forbidden` |

`AdminVersion.created_by` ve `HistoryEntry.actor` opak kimliklerdir; olduğu gibi döner.

### 3.6 Müfredat (`GET /v1/programs/{program}/subjects/{subject}/syllabus`)

`syllabus.get_tree`; `None` → 404.

### 3.7 Yerel geliştirme komutu (`python -m qlab.api.dev`, uygulanacak)

Yalnızca `QLAB_ENV=local` iken çalışır (`Settings.from_env`); başka ortamda hiçbir şey yapmadan hata verir.

| Komut | Davranış |
|---|---|
| `init` | Anahtar yoksa üretir (`devkey.generate`, `settings.dev_key_file`); altı rol için `dev-<rol>` hesaplarını (`issuer = qlab-local-dev`) ve rol atamalarını açar. Yeniden çalıştırılabilir. Rol → `acc_…` tablosunu basar |
| `token <rol> [--hours N]` | O rolün geliştirme hesabı için token basar (varsayılan 8, en çok 24 saat). Yalnızca token'ı standart çıktıya yazar |
| `accounts` | Geliştirme hesaplarını ve rollerini listeler |
| `grant <subject> <rol>` / `revoke <subject> <rol>` | Geliştirme vereninin bir hesabına rol verir / alır |

Her rol verme ve alma **audit kaydı** yazar: `action = role_assignment.granted | role_assignment.revoked`, `entity_type = account`,
`entity_id = acc_…`, `data = {"role": …}`, `actor = system:dev-cli`. Zaten var olan atama yeni kayıt yazmaz. Anahtar dosyasının
içeriği hiçbir çıktıya yazılmaz.

## 4. Kabul ölçütleri

[M1G-5-YETKILER.md](M1G-5-YETKILER.md) §6'nın tamamı, ve:

- Politika tablosu, YETKILER §1 tablosuyla hücre hücre aynıdır (test tabloyu belgedeki haliyle yeniden yazar ve karşılaştırır).
- Yetkisiz çağıran, bozuk gövdeyle de 404/401 alır (yetki doğrulamadan önce gelir).
- Öğrenci görünümü testi belgenin her cevap, açıklama, gerekçe, kazanım ve şekil tarifi alanına tanınabilir bir işaret dizgisi koyar
  ve hiçbir öğrenci yanıtının gövdesinde bu dizgilerin ve yasaklı alan adlarının geçmediğini doğrular.
- Geri çekilmiş, taslak ya da rights'ı iptal edilmiş soru öğrenci uç noktalarından 404 döner ve listede görünmez.
- Bir soru API üzerinden uçtan uca ilerler: taslak düzenleme → gönderme → onay → yayın → öğrenci görünümünde okunma → cevap denetimi →
  revizyon → yeni sürümün yayını → eski sürümün `withdrawn` olması; her adımın audit kaydında çağıranın `acc_…` kimliği vardır.
- `apps/api/openapi.json` üretilenle aynıdır (test); üretilen TypeScript istemcisi şemayla aynıdır (denetim komutu).
- Rol verme ve alma yollarının her biri audit kaydı yazar (test).

## 5. Test düzeneği

- `tests/api/support.py`: `api` fixture → `ApiHarness`. `api.client` (Starlette `TestClient`), `api.headers(Role.X)`,
  `api.account(*roller)`, `api.actor(*roller)`, `api.token(subject, issuer=…, audience=…, lifetime=…, now=…, key=…)`.
  Görev ayrımı açık bir uygulama için `make_harness(connection, session, settings=Settings(Environment.LOCAL, True))`.
- İçerik kurmak için `tests/content/support.py` ve `tests/content/samples.py` kullanılır (`make_env`, `create`, `bring_to`, …).
  Test verisi sentetiktir; gerçek sınav sorusu kullanılmaz (CLAUDE.md kural 14).
- Veritabanı testleri `pytest.mark.db`, KaTeX gerektirenler `pytest.mark.node` işaretlidir.

## 6. İş bölümü

| İş | Kim | Dosyalar |
|---|---|---|
| Sözleşme, yetki katmanı, migration, görev ayrımı kuralı | Ana oturum | §2 |
| A — içerik liste/geçmiş servisleri ve personel uç noktaları | `backend-implementer` | `content/service.py` (yalnızca üç yeni işlev), `api/routers/admin.py`, `api/admin_view.py` |
| B — müfredat ağacı, öğrenci görünümü, dil sezgisi, öğrenci uç noktaları | `backend-implementer` | `syllabus/service.py` (yalnızca `get_tree`), `api/learner_view.py`, `api/language.py`, `api/routers/learner.py` |
| C — yerel geliştirme komutu | `backend-implementer` | `api/dev.py` |
| T1 — kimlik, yetki tablosu, başlangıç denetimleri | `test-writer` | `tests/api/test_authorization*.py`, `tests/identity/`, `tests/organizations/` |
| T2 — öğrenci görünümü, cevap denetimi, dil | `test-writer` | `tests/api/test_learner*.py`, `tests/api/test_language.py`, `tests/syllabus/test_syllabus_tree.py` |
| T3 — personel akışları, geçmiş, OpenAPI, geliştirme komutu | `test-writer` | `tests/api/test_admin*.py`, `tests/api/test_openapi.py`, `tests/api/test_dev_cli.py`, `tests/content/test_content_listing.py` |
| İstemci üretimi | `frontend-implementer` | `packages/api-client/` |
| İnceleme, güvenlik incelemesi | `reviewer`, `security-reviewer` | salt okuma |

## 7. Yeni bağımlılıklar

`fastapi`, `uvicorn`, `pyjwt[crypto]` (çalışma zamanı); `httpx2` (test; Starlette'in test istemcisi bunu ister). Sürümler
`apps/api/uv.lock` içindedir. FastAPI ve Pydantic onaylı stack'tedir; **`pyjwt` ve `cryptography` yeni seçimdir** (§8.1).

## 8. Mimar kararları — sahibinin onayını bekliyor

1. **Token kütüphanesi ve algoritma.** PyJWT + cryptography; yerelde Ed25519 (EdDSA). Gerçek sağlayıcı başka algoritma kullanırsa
   (çoğu RS256) dilim 9'da doğrulayıcıya eklenir.
2. **Hesap kendiliğinden açılmaz.** Geçerli token'ı olan ama `account` satırı olmayan çağıran 401 alır. Kayıt akışı gerçek sağlayıcıyla
   (dilim 9 / M2) gelir; yerelde hesapları `python -m qlab.api.dev init` açar.
3. **Rolsüz hesap hiçbir şey göremez** (varsayılan ret). YETKILER §1'deki "giriş yapmış her hesap yayınlanmış her soruyu görür"
   cümlesi "altı rolden birini taşıyan her hesap" olarak uygulandı.
4. **Rol ataması kurum kapsamı taşımıyor.** M1-G'de kurum tablosu yok; `role_assignment` platform genelindedir. Kurum kapsamı M2'de
   kurum tablosuyla birlikte eklenir (migration gerekir).
5. **Rol atamaları silinmez, geri alınır** (tetikleyici); `granted_by` / `revoked_by` saklanır.
6. **`Idempotency-Key` bu dilimde yok.** API_DESIGN §1 yayın için öngörüyor. Durum geçişleri durum ve içerik özeti denetimi sayesinde
   yinelenen istekte zaten 409 döner (çift yayın olmaz); anahtar tablosu cevap kaydıyla (M2) birlikte yazılır.
7. **Öğrenci görünümünde müfredat düğümü kodu yok.** YETKILER §4'ün "girer" listesinde olmadığı için eklenmedi; konuya göre süzme
   `syllabus_node` sorgu parametresiyle yapılır.
8. **Geliştirme anahtarı depo dışında durur:** `~/.qlab/dev-signing-key.pem` (0600) ya da `QLAB_DEV_KEY_FILE`.
9. **`self_approval_forbidden` 403 döner** (404 değil): çağıran kaynağı zaten görebilen personeldir; saklanacak bir şey yoktur.
10. **Etkileşimli API belgesi (`/docs`) kapalı.** Her yol politika katmanından geçer; sözleşme depodaki `openapi.json`'dır.
11. **`tests/test_package_layout.py`** modül listesine `api` eklendi (HTTP katmanı, `pipeline` gibi modüllerin üstünde durur) ve
    import-linter'a üç sözleşme eklendi (hiçbir modül `qlab.api`'yi import edemez; `identity` ve `organizations` bağımlılıkları).

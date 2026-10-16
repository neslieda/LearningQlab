# M1-G dilim 9 — web'e açılış (ücretsiz deneme ortamı)

> **Durum: TASLAK** (2026-10-16, mimar oturumu). Sahibinin kararları: D-61 (Neon Free + Render Free), D-62 (Zitadel Cloud AB),
> D-63 (hesap yalnızca davetle), D-64 (personel + öğrenci; sıra 9 → 8). Dilim birleşirken içeriği kalıcı belgelere işlenir ve bu
> dosya kaldırılır.

## 1. Amaç ve kapsam

Amaç: site internette çalışsın; sahibi ve öğretmenler gerçek bir giriş ekranından girip soruları görsün, yüklesin, düzenlesin.
Öğrenci davetleri çalışsın (öğrenci ekranı dilim 8'de gelir).

Kapsam: Zitadel ile giriş (tarayıcıda PKCE), API'de JWKS doğrulaması, personel için iki adımlı doğrulama denetimi, davet sistemi,
ilk yöneticinin atanması, uygulamanın süper kullanıcı olmayan veritabanı rolüyle çalışması, Docker imajları, Render kurulum dosyası,
gecelik yedek, güvenlik başlıkları, sahibin adım adım kurulum rehberi (`docs/KURULUM_DENEME.md`).

Kapsam dışı: öğrenci ekranı (8), kurum kapsamı (M2), e-posta gönderimi bizden (Zitadel gönderir), özel alan adı (isteğe bağlı, rehberde).

Kritik alan: evet (yetki, migration, CI, kimlik). Sahibinin onayı gerekir.

## 2. Zitadel düzeni (D-62)

- Bir proje, bir "User Agent" uygulaması (PKCE, erişim token'ı JWT). İki organizasyon:
  - **Staff**: kayıt kapalı, iki adımlı doğrulama zorunlu (Force MFA). Hesapları sahibi açar.
  - **Learners**: kayıt açık, iki adımlı doğrulama isteğe bağlı. Öğretmenler (rol `teacher`) ve öğrenciler buradadır.
- Kapsamlar: `openid profile email offline_access urn:zitadel:iam:org:project:id:<projectId>:aud
  urn:zitadel:iam:user:resourceowner` ve girişin hangi organizasyona yapılacağı `urn:zitadel:iam:org:id:<orgId>`.
- ❓ Doğrulanacak (rehberin ilk adımı, bir deneme token'ıyla): erişim token'ında kullanıcının organizasyon kimliğini taşıyan alan
  (`urn:zitadel:iam:user:resourceowner:id`). Yoksa personel rolleri hiç tanınmaz (fail-closed) ve tasarım yeniden ele alınır.

## 3. API sözleşmesi

### 3.1 Token doğrulama

- Ayarlar (yerel dışında zorunlu): `QLAB_OIDC_ISSUER` (keşif belgesindeki `issuer`, bire bir), `QLAB_OIDC_AUDIENCE` (proje kimliği),
  `QLAB_OIDC_CLIENT_ID` (`azp` ile karşılaştırılır), `QLAB_OIDC_STAFF_ORG_ID`.
- Anahtarlar `<issuer>/.well-known/openid-configuration` → `jwks_uri`'den alınır, bellekte saklanır; bilinmeyen `kid` görülünce en çok
  dakikada bir yeniden çekilir. İzinli algoritmalar: RS256, ES256, EdDSA (`none` ve HS* asla). Doğrulanan: imza, `iss`, `aud` içinde
  proje kimliği, `azp` = istemci kimliği, `exp`, `iat`, ömür ≤ 24 saat, `sub` biçimi (dilim 5 kuralları).
- Yerel geliştirme anahtarı ve vereni yerel dışında reddedilir (değişmez).

### 3.2 İki adımlı doğrulama (SECURITY §2)

- `STAFF` rolleri (`reviewer`, `content_admin`, `platform_admin`) yalnızca token'ın organizasyon alanı `QLAB_OIDC_STAFF_ORG_ID` ise
  geçerlidir. Değilse bu roller o istek için yok sayılır. Çağıranın rolleri uç noktaya yetiyor ama kalan (personel dışı) rolleri
  yetmiyorsa 403 `mfa_required` döner ("Staff access needs a staff sign-in with two-step verification"); herkese açık uç noktalar
  (`/v1/me` dahil) bunun dışında değildir: yalnızca personel rolü olan biri Staff girişi yapmadan hiçbir uç noktayı kullanamaz.
  Rolleri zaten yetmeyen çağıran eskisi gibi 404 alır.
- Yerelde bu denetim yoktur (geliştirme token'ı).

### 3.3 Davetler (D-63)

Yeni erişim türü **`SIGNED_IN`**: geçerli token yeter, hesap henüz olmayabilir. Yalnızca davet kullanma uç noktasında.

| Uç nokta | Erişim | Gövde / yanıt |
|---|---|---|
| `POST /v1/invites/redeem` | `SIGNED_IN` | `{code}` → 200 `{roles}`. Hesap yoksa açılır, rol verilir (zaten varsa değişmez), kullanım sayılır. Bilinmeyen, süresi dolmuş, geri alınmış ya da kullanımı bitmiş kod: 404 `invite_not_found` (hepsi aynı). Devre dışı hesap: 401 |
| `POST /v1/admin/invites` | `teacher`, `platform_admin` | `{role, expires_in_days: 1–30 (7), max_uses: 1–200 (1)}` → 201 `{id, code, role, expires_at, max_uses, uses, created_at}`. **Kod yalnızca burada döner.** `teacher` yalnızca `student` daveti üretebilir, değilse 403 `invite_role_forbidden` |
| `GET /v1/admin/invites` | `teacher`, `platform_admin` | Davetler (kodsuz), en yeni önce; `teacher` yalnızca kendi davetlerini görür. Sayfalama 7a listesi gibi |
| `POST /v1/admin/invites/{invite_id}/revoke` | `teacher`, `platform_admin` | 200; `teacher` yalnızca kendisininkini. Başkasının: 404 |

- Bu daveti daha önce kullanmış aynı kişi tekrar kullanırsa (davet dolmuş, süresi geçmiş ya da geri alınmış olsa bile) 200 ve güncel
  rolleri döner; sayılmaz, audit yazılmaz. Biçimi bozuk kod 422.
- Personel rolü veren davet, Staff organizasyonu dışından girişle de kullanılabilir (`SIGNED_IN` MFA denetlemez); rol verilir ama
  Staff girişi yapılana kadar kullanılamaz (§3.2).
- Kod: 32 bayt rastgele, base64url; veritabanında yalnızca SHA-256 özeti. Kaba kuvvete karşı ayrıca sınır gerekmez (2^256).
- Tablolar (migration 0006): `invite` (`id`, `code_sha256` tekil, `role`, `created_by`, `created_at`, `expires_at`, `max_uses`,
  `uses`, `revoked_at`, `revoked_by`) ve `invite_redemption` (`invite_id`, `account_id`, `redeemed_at`; ikisi birlikte tekil: aynı
  kişi aynı daveti iki kez saymaz). Kullanım sayımı satır kilidiyle (eşzamanlı iki kullanım `max_uses`'u aşamaz).
- Audit: `invite.created`, `invite.revoked`, `invite.redeemed` (davet kimliği, rol, hesap kimliği; kod asla).
- **İlk yönetici:** `python -m qlab.api.admin invite --role platform_admin --base-url <web adresi>` sahibin bilgisayarından,
  `QLAB_DATABASE_URL` ile çalışır; tek kullanımlık, 1 günlük davet bağlantısı yazar. Audit actor `cli:owner`.

### 3.4 Veritabanı rolleri (D-54)

- Migration'lar sahibi rolüyle (`QLAB_MIGRATION_DATABASE_URL`), uygulama `qlab_app` rolüyle (`QLAB_DATABASE_URL`) çalışır.
  `qlab_app` tablo sahibi ve süper kullanıcı değildir; yalnızca `SELECT, INSERT, UPDATE, DELETE` ve dizi kullanımı. Kurulum betiği
  `infra/sql/app-role.sql` (varsayılan yetkiler dahil, sonraki migration'ların tabloları da kapsanır).

## 4. Web

- `/sign-in`: "Sign in" (Learners organizasyonu) ve "Staff sign-in" (Staff organizasyonu). `oidc-client-ts` (sabit sürüm), tarayıcıda
  PKCE, token'lar `sessionStorage`'da, yenileme token'ıyla sessiz yenileme. `/auth/callback`, "Sign out".
- `/invite/[code]`: giriş yoksa önce giriş (kod korunur), sonra `redeem`; sonuç: "You now have the <role> role" + uygun sayfaya
  bağlantı. 404 → "This invite link is not valid. Ask for a new one."
- `/admin/invites`: rol, süre, kullanım sayısı seçilip davet üretilir; bağlantı bir kez gösterilir, "Copy link"; liste ve "Revoke".
- 403 `mfa_required` → "Staff access needs two-step verification. Sign out and use Staff sign-in."
- Yerel geliştirme girişi (`/dev/sign-in`) yalnızca yerelde görünür ve çalışır.
- Güvenlik başlıkları: CSP (`connect-src` yalnızca kendi kökeni ve Zitadel), `frame-ancestors 'none'`, HSTS, `Referrer-Policy:
  no-referrer` (davet kodu adres çubuğunda), `X-Content-Type-Options`.

## 5. Dağıtım (D-61)

- `infra/docker/api.Dockerfile`: Python 3.14 + Node 24 + `apps/api/katex` (`npm ci`); başlangıçta `alembic upgrade head`
  (migration URL'siyle), sonra uvicorn `$PORT`.
- `infra/docker/web.Dockerfile`: Next.js standalone çıktısı.
- `render.yaml`: Frankfurt, ücretsiz iki web servisi; gizli değerler `sync: false` (sahibi panelden girer).
- Gecelik yedek: GitHub Actions zamanlanmış iş, salt okunur rolle `pg_dump`, şifreli yapıt, 14 gün saklama (CI kritik alan).
- `QLAB_FORBID_SELF_APPROVAL` yerel dışında zorunlu açık (D-59); deneme ortamında da açık kalır (§7.3).

## 6. Kabul testleri

1. JWKS doğrulayıcı: geçerli token; yanlış `iss`/`aud`/`azp`; süresi dolmuş; `alg: none`, HS256; bilinmeyen `kid` → bir kez yeniden
   çekme; anahtar dönüşü; keşif belgesine ulaşılamazsa uygulama açılmaz.
2. MFA: staff rolüyle, staff organizasyonu olmayan token → 403 `mfa_required`; aynı hesapla `teacher` uç noktaları çalışır.
3. Davet: üretme (rol kuralları), kullanma (hesap açılır, rol verilir), aynı kişi ikinci kez (sayılmaz), süresi dolmuş / geri alınmış /
   bitmiş → 404 aynı gövde, eşzamanlı kullanım `max_uses`'u aşmaz, kod veritabanında yok (yalnız özet), audit.
4. Yetki tablosu: yeni uç noktalar ve `SIGNED_IN` erişimi; rolsüz hesap yalnızca `redeem`'i çağırabilir.
5. İlk yönetici komutu bir davet yazar ve audit'e `cli:owner` düşer.
6. Uygulama `qlab_app` rolüyle çalışır; DDL denemesi reddedilir.
7. Web: giriş, çıkış, davet akışı, davet ekranı, `mfa_required` mesajı (API taklit edilerek); CSP başlıkları.
8. Docker imajları yerelde derlenir ve açılır; `render.yaml` doğrulanır.

## 7. Mimar kararları (sahibin onayına)

1. Personel MFA'sı organizasyon ayrımıyla zorlanır; API organizasyon alanını denetler (fail-closed).
2. `teacher` yalnızca öğrenci daveti üretir; diğer davetleri yalnızca `platform_admin` üretir.
3. Görev ayrımı kuralı (D-59) deneme ortamında da açık (sahibinin kararı, 2026-10-16: ekipte birden çok düzenleyici var). Soru düzenleyen eğitmenler `reviewer` rolü alır (Staff organizasyonu, iki adımlı doğrulama).
4. Gecelik yedek GitHub Actions yapıtı olarak (ABD'de saklanır ⚖️; içerik soru metinleri ve opak hesap kimlikleri, ad/e-posta yok).

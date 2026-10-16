# Deneme ortamı kurulum rehberi (sahibi için)

> Bu rehber yazılımcı olmayan biri için yazıldı. Her adım sırayla yapılır. Sağlayıcıların ekranları zamanla değişir; ekran
> tarifleri bu yüzden kelimelerle verildi. Doğrulayamadığım ekran ayrıntıları **❓** ile işaretlidir: orada ekranda biraz
> farklı bir ad görürseniz şaşırmayın, anlamı aynıdır. Kararlar: D-61 (Neon + Render ücretsiz), D-62 (Zitadel Cloud, AB),
> D-63 (hesap yalnızca davetle), D-64 (personel + öğrenci).
>
> **Gizli bilgi kuralı:** parolalar ve bağlantı adresleri yalnızca sağlayıcı panellerine ve GitHub "Secrets" ekranına yazılır.
> Dosyalara, sohbete, e-postaya yazılmaz. Bir parola yanlışlıkla bir yere yapışırsa o parolayı hemen değiştirin.

Toplam süre: ilk kez yapana yaklaşık 2 saat. Önerilen sıra: 1 Neon, 2 Zitadel, 3 Render, 4 ilk yönetici, 5 içerik, 6 davetler, 7 yedek.

## 0. Başlamadan önce

- Bir e-posta adresi (tüm hesaplar için aynısı olabilir) ve bir telefon (iki adımlı doğrulama uygulaması için).
- GitHub'da `neslieda/LearningQlab` deposuna erişim (zaten var).
- Bilgisayarınızda proje klasörü ve komutlar için **Terminal** (rehberdeki gri kutulardaki komutlar oraya yapıştırılır).
- Bir not defteri (kağıt ya da parola yöneticisi). Aşağıda üretilecek değerleri buraya yazacaksınız:
  Neon sahibi adresi, Neon uygulama adresi, Neon yedek adresi, Zitadel issuer, proje kimliği, istemci kimliği, iki organizasyon
  kimliği, Render adresleri.

## 1. Neon (veritabanı)

Resmi belgeler: <https://neon.com/docs> ; roller: <https://neon.com/docs/manage/roles>

1. <https://neon.com> adresine gidin, **Sign up** ile hesap açın (GitHub ya da e-posta).
2. Proje oluşturma ekranında: proje adı `qlab`, **Postgres version: 17**, bölge (**Region**) olarak **Europe (Frankfurt)**
   (`aws-eu-central-1`; ❓ listede AWS Frankfurt olarak görünür). **Create project**.
3. Proje açılınca **Connect** (bağlan) düğmesine basın. Açılan pencerede **Role** olarak otomatik oluşturulan sahip rolünü
   (adı genellikle `neondb_owner` ❓), **Database** olarak `neondb` seçili olsun. Pencerede "Connection string" yazan kutuda
   `postgresql://...` ile başlayan uzun bir adres görürsünüz. **"Show password"** ile parolalı halini kopyalayıp
   not defterine **Neon sahibi adresi** diye yazın. ❓ "Pooled connection" kutusunu **kapatın** (doğrudan bağlantı kullanılır).
4. vector eklentisini açın: sol menüde **SQL Editor**'ı açın, kutuya şunu yazıp **Run**'a basın:
   `CREATE EXTENSION IF NOT EXISTS vector;`  "Success" benzeri bir yeşil ileti görmelisiniz.
5. Uygulama ve yedek rolleri. Bu roller **konsoldan değil, SQL ile** oluşturulur (konsolda oluşturulan roller fazla yetkilidir;
   kaynak: Neon "Manage roles" sayfası). Terminalde proje klasöründe, iki yeni uzun parola uydurarak:

   ```
   psql "NEON_SAHIBI_ADRESI" -v app_password='UYGULAMA_PAROLASI' -v backup_password='YEDEK_PAROLASI' -f infra/sql/app-role.sql
   ```

   `psql` kurulu değilse Mac'te: `brew install libpq` sonra `brew link --force libpq`. Parolalar en az 12 karakter, karışık
   harf/rakam olsun; adres içinde özel karakter (`@`, `/`, `:`) kullanmayın, adrese yapıştırmak sorun çıkarır.
   Sonunda birkaç `CREATE ROLE`/`GRANT`/`ALTER DEFAULT PRIVILEGES` satırı ve hata olmaması gerekir.
6. İki yeni adres elde edin: 3. adımdaki adreste kullanıcı adını ve parolayı değiştirin:
   - **Uygulama adresi:** `postgresql+psycopg://qlab_app:UYGULAMA_PAROLASI@<aynı sunucu adı>/<veritabanı>?sslmode=require`
   - **Yedek adresi:** `postgresql://qlab_backup:YEDEK_PAROLASI@<aynı sunucu adı>/<veritabanı>?sslmode=require`
   - **Sahip adresi (Render için):** 3. adımdaki adresin başını `postgresql+psycopg://` yapın (yalnız baştaki kısım).
   Uygulama (SQLAlchemy) için adres `postgresql+psycopg://` ile başlamalı; `pg_dump` için düz `postgresql://`.
7. Neon ücretsiz planı 1 GB depolama verir; 5 dakika kullanılmayınca veritabanı uyur ve ilk istekte birkaç saniyede uyanır
   (D-61).

## 2. Zitadel Cloud (giriş)

Resmi belgeler: <https://zitadel.com/docs> (uygulama kaydı: "Applications" bölümü; token'lar: "Claims" bölümü)

1. <https://zitadel.com> → **Get started / Sign up**. Oluşturulan **instance** için bölge olarak **EU** seçin ❓
   (ücretsiz kademe: günde 100 aktif kullanıcı, D-62). Instance adresiniz `https://<ad>.zitadel.cloud` gibi olur. Bu adres
   **issuer**'dır; ancak tam değeri bir sonraki "doğrulama" kutusundaki yöntemle de kontrol edin (sonunda `/` olup olmaması önemli).
2. **Organizasyonlar.** Üst menüde **Organizations** → **New**. İki tane oluşturun:
   - `Staff` (personel). Sonra bu organizasyonun **Settings** ❓ bölümünde:
     - **Login Behavior and Security** ❓ → **Force MFA** (iki adımlı doğrulamayı zorunlu kıl) açık.
     - **Register allowed / User registration** ❓ kapalı (kimse kendi kendine kayıt olamasın).
   - `Learners` (öğretmen ve öğrenciler). Kayıt **açık** (Register allowed). İki adımlı doğrulama isteğe bağlı kalır.
   Her organizasyonun sayfasında **Organization ID** (uzun bir sayı) vardır; ikisini de not edin.
3. **Proje.** Soldaki menüden **Projects** → **Create New Project**, adı `qlab`. Projeyi hangi organizasyonda
   oluşturduğunuz önemli değil (varsayılan organizasyon olabilir), ama ❓ projenin ayarlarında
   **"Assert Roles on Authentication"**/**"Check roles on authentication"** gibi kutular varsa dokunmayın. Proje sayfasında
   **Resource ID** (proje kimliği) vardır; not edin.
   Başka organizasyonların kullanıcılarının bu projeye girebilmesi için projede ❓ **"Private labeling" / "Project settings"**
   altında projeye erişim kısıtı varsa **kapalı** olsun (yani "Check authorization on Authentication" kapalı).
4. **Uygulama.** Proje içinde **New** (Applications) → ad `qlab-web` → tür: **User Agent** → kimlik doğrulama yöntemi:
   **PKCE** (client secret yok) → **Continue**.
   - **Redirect URIs** (girişten sonra dönülecek adresler), her satır ayrı:
     - `https://<render-web-adresi>/auth/callback` (Render adresini 3. bölümde öğrenirsiniz; şimdilik boş geçip sonra
       dönüp ekleyebilirsiniz)
     - `http://localhost:3000/auth/callback` (kendi bilgisayarınızdaki deneme uygulaması için)
   - **Post Logout URIs**: aynı iki adres, ancak `/auth/callback` yerine `/`.
   - Oluşturduktan sonra uygulamanın **Token Settings** ❓ bölümünde **Auth Token Type = JWT** seçin ve **Save**.
     (Varsayılan "Bearer" ise API token'ı okuyamaz.) Ayrıca ❓ **"Add user roles to the access token"** ve
     **"User roles inside ID Token"** kutularını işaretlemeniz gerekmez; roller uygulamanın içindedir (D-12).
   - Uygulama sayfasındaki **Client ID** değerini not edin.
   - Dev Mode ❓ (Development Mode) açık olursa `http://localhost` adreslerine izin verilir; localhost için gerekebilir.
5. **Giriş sayfasında e-posta gönderimi (SMTP) notu.** Zitadel'in kendi e-posta göndericisi doğrulama ve parola sıfırlama
   postaları için yeterlidir ama günlük sınırı olabilir ❓. Çok sayıda öğrenci eklemeden önce **Settings → SMTP** ❓ altında
   kendi gönderici bilginizi (okulunuzun e-posta sunucusu ya da bir posta hizmeti) girmeniz önerilir. Teslim sorunu olursa
   postalar spam klasörüne düşmüş olabilir.
6. **Personel hesabınızı açın.** `Staff` organizasyonunda **Users → New** → kişi tipi **Human**, kendi e-postanız, bir parola.
   (Kayıt kapalı olduğu için personeli yalnızca siz eklersiniz.) İlk girişte Zitadel sizden iki adımlı doğrulama (telefon
   uygulaması ❓ OTP) kurmanızı isteyecek.
7. **Değerleri toplayın (not defterine):**
   - **issuer:** tarayıcıda `https://<instance-adresiniz>/.well-known/openid-configuration` adresini açın; sayfadaki
     `"issuer": "https://..."` değeri aynen (sonunda `/` yoksa yok) kullanılır.
   - **Proje kimliği** (`QLAB_OIDC_AUDIENCE`), **Client ID**, **Staff organizasyon kimliği**, **Learners organizasyon kimliği**.

### 2.1 Doğrulama adımı (önemli, atlamayın)

Personel iki adımlı doğrulaması şuna dayanır: giriş yapan kişinin erişim token'ının içinde, kişinin hangi organizasyona ait
olduğunu söyleyen `urn:zitadel:iam:user:resourceowner:id` alanı bulunmalı. Bu alan yoksa personel rolleri hiç tanınmaz
(güvenli taraf) ve tasarım yeniden ele alınır. Şimdi kontrol edelim:

1. Render'da uygulama ayağa kalktıktan sonra (bölüm 3) `https://<web-adresi>/sign-in` sayfasına gidin, **Staff sign-in**'e basın,
   Staff hesabınızla girin. Tarayıcıda sağ tık → **İncele/Inspect** → **Application** (Safari'de **Storage**) sekmesi →
   **Session Storage** → sitenizin adresi. Uzun bir değerin içinde `access_token` alanı bulunur ❓ (anahtar adı `oidc.user:...`
   ile başlar). `eyJ...` ile başlayan, iki nokta içeren o uzun metni kopyalayın (yalnızca bu denemede, kimseye göndermeyin).
2. <https://jwt.io> kullanmak yerine (token'ı bir siteye yapıştırmamak için) kendi bilgisayarınızda çözün. Terminalde:

   ```
   pbpaste | python3 -c "import sys,json,base64; p=sys.stdin.read().strip().split('.')[1]; print(json.dumps(json.loads(base64.urlsafe_b64decode(p+'='*(-len(p)%4))),indent=2))"
   ```

   (Önce token'ı kopyalayın; `pbpaste` panodaki metni verir. Komut base64 dolgusunu kendisi tamamlar.) Çıktıda şunu arayın:
   `"urn:zitadel:iam:user:resourceowner:id": "<Staff organizasyon kimliği>"`. Aynı kimliğin 2. adımda not ettiğiniz Staff
   organizasyon kimliğiyle **aynı** olduğunu kontrol edin. Ayrıca `"aud"` içinde proje kimliği, `"azp"` yerinde Client ID
   görünmelidir.
3. **Alan yoksa:** `/sign-in` sayfasının istediği kapsamlar (`scope`) arasında
   `urn:zitadel:iam:user:resourceowner` yer almalıdır (web uygulamasında zaten tanımlı olmalı). Zitadel'de uygulamanın
   Token ayarlarının JWT olduğunu (adım 2.4) yeniden kontrol edin. Yine yoksa durun, bu bilgiyi (token'ı değil, hangi alanların
   olduğunu) geliştirme oturumuna bildirin; personel girişi bu noktada tasarım değişikliği ister.

## 3. Render (web ve API)

Resmi belgeler: <https://render.com/docs/blueprint-spec> , <https://render.com/docs/docker>

1. <https://render.com> → **Get Started**, **GitHub ile** kayıt olun. İstenirse `neslieda/LearningQlab` deposuna erişim verin
   (Render'ın GitHub uygulaması; yalnızca bu depoyu seçin).
2. Panelde **New +** → **Blueprint** → depoyu seçin, dal `main` (bu dilim birleşene kadar `slice/m1g-9-launch` dalını
   seçmeniz gerekebilir). Render depodaki `render.yaml` dosyasını okur ve iki servis gösterir: `qlab-api` ve `qlab-web`
   (ikisi de **Free**, **Frankfurt**).
3. Render, `sync: false` olarak işaretlenmiş değerleri sizden ister. Doldurun:

   | Servis | Değişken | Değer |
   |---|---|---|
   | qlab-api | `QLAB_DATABASE_URL` | **MUTLAKA** Neon **uygulama adresi** (qlab_app). Sahip adresi yazarsanız API bilerek başlamaz: sahip rolü ya da `public` şemasında CREATE yetkisi olan rol reddedilir. |
   | qlab-api | `QLAB_MIGRATION_DATABASE_URL` | Neon **sahip adresi** (`postgresql+psycopg://` ile başlayan); yalnızca açılışta migration için kullanılır |
   | qlab-api | `QLAB_OIDC_ISSUER` | issuer |
   | qlab-api | `QLAB_OIDC_AUDIENCE` | proje kimliği |
   | qlab-api | `QLAB_OIDC_CLIENT_ID` | Client ID |
   | qlab-api | `QLAB_OIDC_STAFF_ORG_ID` | Staff organizasyon kimliği |
   | qlab-web | `QLAB_API_URL` | qlab-api'nin herkese açık adresi, ör. `https://qlab-api-xxxx.onrender.com` (sonda `/` yok) |
   | qlab-web | `NEXT_PUBLIC_OIDC_ISSUER`, `..._CLIENT_ID`, `..._PROJECT_ID`, `..._STAFF_ORG_ID`, `..._LEARNER_ORG_ID` | aynı değerler |

   `QLAB_API_URL` için api'nin adresini henüz bilmiyorsanız: Blueprint'i önce herhangi bir geçici değerle (`https://example.com`)
   oluşturun, qlab-api açılınca adresini panelde servisin adının altında görürsünüz; sonra qlab-web → **Environment**'ta düzeltip
   **Manual Deploy** yapın. (Bu değer web derlenirken kullanıldığı için değişince yeniden derleme gerekir.)
   `QLAB_ENV=staging` ve `QLAB_FORBID_SELF_APPROVAL=true` dosyada hazırdır; dokunmayın. Not: `true` olduğu sürece bir soruyu
   son düzenleyen kişi onaylayamaz; onay için ikinci bir personel hesabı gerekir (D-59). Sahibin kararı (2026-10-16): kural deneme
   ortamında da açık, çünkü ekipte birden çok kişi (eğitmenler ve yazılımcılar) soru düzenleyip birbirinin işini onaylar.
4. **Apply / Deploy**'a basın. İlk derleme 5-10 dakika sürer. Her servisin sayfasında **Logs** sekmesi vardır; qlab-api
   günlüğünde "Running upgrade ... 0006" benzeri satırlar (veritabanı hazırlanıyor) ve ardından "Uvicorn running" görmelisiniz.
5. Adresleri bulun: her servisin sayfasının sol üstünde `https://....onrender.com` adresi yazar. Önce `https://<api-adresi>/healthz`
   adresini tarayıcıda açın: kısa bir "ok" benzeri yanıt gelmelidir.
6. Zitadel'e dönün (bölüm 2.4) ve Redirect URI listesine `https://<web-adresi>/auth/callback`, Post Logout listesine
   `https://<web-adresi>/` ekleyin.
7. Ücretsiz plan: 15 dakika kullanılmayınca servis uyur, ilk istekte yaklaşık 1 dakikada uyanır (D-61).

## 4. İlk yönetici

Hesap yalnızca davetle açılır (D-63). İlk daveti kendi bilgisayarınızdan üretirsiniz.

1. Terminalde proje klasöründe:

   ```
   cd apps/api
   export QLAB_DATABASE_URL='NEON_UYGULAMA_ADRESI'
   export QLAB_ENV=local
   uv run python -m qlab.api.admin invite --role platform_admin --base-url https://<web-adresi>
   ```

   Burada yalnızca **uygulama adresi** (qlab_app) kullanın. Komut `https://<web-adresi>/invite#<kod>` biçiminde (kod `#`'den
   sonra gelir; sunucuya gönderilmez), varsayılan olarak 1 gün geçerli bir bağlantı yazar. Staff rolleri için bir davet en
   fazla 5 kez kullanılabilir. ❓ `QLAB_ENV` gerekmiyorsa komut bunu söyler; hata verirse mesajı okuyun.
2. Bağlantıyı tarayıcıda açın. Giriş yapmanız istenir: **Staff sign-in** ile Staff hesabınızla girin (iki adımlı doğrulama
   kodunu girin). Giriş sonrası bağlantı kendiliğinden kullanılır ve "You now have the platform_admin role" yazar.
3. Hesap kimliğinizi öğrenin (yükleme komutunda lazım): girişliyken `https://<web-adresi>/account` sayfasını açın;
   **"Your account ID"** satırındaki `acc_...` değeri hesap kimliğinizdir.

## 5. Müfredat, haklar ve pilot soruları yükleme

Komutlar `docs/DEVELOPMENT_WORKFLOW.md` §13'tendir; yalnızca veritabanı adresi Neon'unkidir. Yüklemeyi **uygulama** adresiyle
(qlab_app) yapabilirsiniz (yalnız veri yazar). Terminalde:

```
cd apps/api
(cd katex && npm ci --ignore-scripts)         # bir kez; Node 24 gerekir
export QLAB_DATABASE_URL='NEON_UYGULAMA_ADRESI'
uv run python -m qlab.syllabus ../../content/reference/dp-physics-2025-syllabus.json
uv run python -m qlab.content.pilot load --operator <HESAP_KIMLIGINIZ> --create-rights
```

`--create-rights` yalnızca ilk seferde gerekir. Önce denemek isterseniz komutun sonuna `--dry-run` ekleyin (hiçbir şey yazmaz).
Yaklaşık 130 pilot soru **taslak** olarak yüklenir. Ardından web uygulamasında yönetim ekranlarından bunları görürsünüz.

## 6. Davetler ve roller

Davet bağlantısı `https://<web-adresi>/invite#<kod>` biçimindedir. Staff rolleri için bir davet en fazla 5 kez kullanılabilir.

**Zitadel kontrol listesi (davet vermeden önce işaretleyin):**
- [ ] Staff organizasyonunda kendi kendine kayıt **kapalı**, **Force MFA açık**.
- [ ] Learners organizasyonunun kullanıcıları Staff organizasyonuna üyelik/yetki veremez (Staff'a yalnızca siz kullanıcı eklersiniz;
  Learners'taki hiçbir kullanıcıya Staff organizasyonunda yönetici (Org Owner vb.) rolü vermeyin).

Yönetim ekranından (`/admin/invites`) davet bağlantısı üretilir: rolü, geçerlilik süresini (1-30 gün) ve kaç kişi kullanabileceğini
seçersiniz. Bağlantı yalnızca üretildiği anda gösterilir; kopyalayıp kişiye gönderin. Yanlış kişiye gittiyse listeden **Revoke**.

| Kişi | Rol | Nereden girer | Not |
|---|---|---|---|
| Öğrenci | `student` | **Sign in** (Learners) | Öğretmen de bu daveti üretebilir. Öğrenci ekranı sonraki dilimde gelir. |
| Öğretmen | `teacher` | **Sign in** (Learners) | Yalnızca `platform_admin` öğretmen daveti üretebilir. Öğretmen yalnız öğrenci daveti üretir. |
| Soru editörü / gözden geçirici | `reviewer` (ve gerekirse `content_admin`) | **Staff sign-in** (Staff) | Önce Zitadel'de Staff organizasyonunda kişinin hesabını **siz** açarsınız (kayıt kapalı). |

**Fark:** Öğretmenler Learners organizasyonundadır; kayıt açıktır, iki adımlı doğrulama zorunlu değildir. Soru düzenleme gibi
personel yetkileri ise yalnızca Staff organizasyonundaki, iki adımlı doğrulamalı girişte geçerlidir. Bir kişiye hem öğretmen
hem editör yetkisi verecekseniz iki ayrı hesabı (biri Learners'ta, biri Staff'ta) olur ve her biri için ayrı davet kullanılır.
Staff dışında bir girişle editör ekranı açılırsa "Staff access needs two-step verification. Sign out and use Staff sign-in."
iletisi görünür.

## 7. Yedekleme

Her gece 02:30'da (UTC) GitHub, veritabanının şifreli bir kopyasını alır ve 14 gün saklar (`.github/workflows/backup.yml`).
Kopya GitHub'ın ABD'deki sunucularında durur ⚖️; içinde soru metinleri ve opak hesap kimlikleri vardır, ad ve e-posta yoktur.

1. Önce şifreleme anahtar çiftini **kendi bilgisayarınızda** üretin (`brew install age`):

   ```
   age-keygen -o qlab-yedek-anahtar.txt
   ```

   Ekrana `Public key: age1...` yazar. Bu `age1...` değeri **herkese açıktır** (GitHub'a girer). `qlab-yedek-anahtar.txt` dosyasındaki
   `AGE-SECRET-KEY-...` satırı **özel anahtardır**: GitHub'a, sohbete, e-postaya asla koymayın; çevrimdışı (parola yöneticisi
   ve USB bellek gibi) en az iki yerde saklayın. Kaybederseniz yedekler açılamaz.
2. GitHub'da depo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. İki tane:
   - `NEON_BACKUP_URL` = Neon **yedek adresi** (`postgresql://qlab_backup:...`)
   - `BACKUP_AGE_RECIPIENT` = yukarıdaki **açık** anahtar (`age1...`). (İsterseniz "Variables" sekmesine de koyabilirsiniz.)
3. Deneme: depo → **Actions** → **backup** → **Run workflow**. Yeşil biterse çalışmıştır. Çalıştırmanın sayfasının altında
   **Artifacts** bölümünde `qlab-<tarih>` dosyası görünür.
4. **Geri yükleme:** artifact'i indirin ve açın (`qlab-....dump.age`). Boş bir Neon veritabanı (ya da yeni bir Neon projesi)
   hazırlayın, bölüm 1.4'teki `CREATE EXTENSION vector` ve 1.5'teki rol komutunu orada çalıştırın, sonra:

   ```
   age --decrypt -i qlab-yedek-anahtar.txt -o geri.dump qlab-XXXX.dump.age   # özel anahtar dosyanız gerekir
   pg_restore --no-owner --no-privileges --dbname "NEON_SAHIBI_ADRESI" geri.dump
   ```

   (`pg_restore` sürüm 17 olsun.) Ardından `infra/sql/app-role.sql` komutunu yeniden çalıştırın ki roller yeni tablolara da
   yetki alsın. Geri yüklemeyi ciddi bir ihtiyaç doğmadan **bir kez deneme** olarak yapmanız önerilir.

## 8. Maliyet

Hepsi ücretsiz kademede (D-61, D-62; fiyatlar ve sınırlar 2026-10-16'da resmi sayfalardan okundu, değişebilir):

- Neon Free: 1 GB, 5 dakika sonra uyku, 6 saat geri dönüş penceresi.
- Render Free (iki servis): 15 dakika sonra uyku, ilk açılış yaklaşık 1 dakika. ❓ Aylık ücretsiz saat sınırı olabilir; Render
  panelinde kullanımı kontrol edin.
- Zitadel Cloud ücretsiz: günde 100 aktif kullanıcı.
- GitHub Actions yedek işi: özel depoda ücretsiz dakika kotası içinde, günlük birkaç dakika. ❓
- Alan adı (isteğe bağlı) ücretlidir; deneme için gerekmez.

## 9. Sorun giderme

| Belirti | Neden / yapılacak |
|---|---|
| Site ilk açılışta bir dakika yükleniyor | Render ücretsiz plan uyumuştur. Bekleyin, sayfayı yenileyin. İki servis de uyuyabilir. |
| İlk istek hata veriyor, ikincisi çalışıyor | Neon veritabanı uyanıyordur (birkaç saniye). Yenileyin. |
| "Staff access needs two-step verification. Sign out and use Staff sign-in." (`mfa_required`) | Staff yetkili bir işlem Learners girişiyle yapıldı. Çıkış yapın, **Staff sign-in** ile girin. Staff hesabında 2FA kurulu olmalı. |
| "This invite link is not valid. Ask for a new one." | Bağlantı süresi dolmuş, geri alınmış, kullanım hakkı bitmiş ya da yanlış kopyalanmış. Yeni davet üretin. (Hepsi aynı mesajı verir, bilerek.) |
| Girişte "redirect_uri mismatch" benzeri Zitadel hatası | Zitadel uygulamasındaki Redirect URI listesinde web adresiniz yok ya da yazım farkı var (`https`, sonda `/`). |
| Giriş yapılıyor ama API 401 veriyor | Token türü JWT değil (2.4), ya da issuer/proje kimliği/Client ID Render'da yanlış. `QLAB_OIDC_ISSUER` keşif belgesindeki `issuer` ile **birebir** olmalı. |
| qlab-api başlamıyor, günlükte "missing settings" | Render'da bir `QLAB_OIDC_*` değeri boş. **Environment**'tan doldurup yeniden dağıtın. |
| qlab-api günlükte "password authentication failed" | Adresteki parola ya da rol adı yanlış; Neon'da `app-role.sql`'in çalıştığını ve parolada özel karakter olmadığını kontrol edin. |
| Web açılıyor ama veri gelmiyor | `QLAB_API_URL` yanlış ya da sonunda `/` var; düzeltip qlab-web'i yeniden derleyin (derleme sırasında okunur). |
| Soru kaydı "renderer unavailable" diyor | Yalnızca kendi bilgisayarınızdaki yüklemede: `apps/api/katex` içinde `npm ci` yapılmamış. |
| Yedek işi kırmızı | Actions günlüğünü açın; çoğunlukla `NEON_BACKUP_URL` hatalıdır (rol parolası). Adres düz `postgresql://` ile başlamalı. |

## 10. Ortam değişkenleri başvurusu (.env.example biçiminde, gizli değer yok)

Değerler yalnızca Render paneline ve GitHub Secrets'a yazılır; hiçbir dosyaya yazılmaz.
Render, Docker servislerinde panelde tanımlı ortam değişkenlerini hem çalışma anında hem derleme argümanı olarak verir
(<https://render.com/docs/docker>), bu yüzden `qlab-web` değişkenlerinin hepsi derlemede de görünür. Web değerleri derleme
sırasında pakete gömülür: bunlardan biri değişirse **Manual Deploy** ile yeniden derlemek gerekir.

```
# --- qlab-api (Render) ---
QLAB_ENV=staging                       # render.yaml'da hazır
QLAB_FORBID_SELF_APPROVAL=true         # render.yaml'da hazır; staging/production'da true olmak zorunda
QLAB_DATABASE_URL=                     # MUTLAKA qlab_app adresi: postgresql+psycopg://qlab_app:...@HOST/DB?sslmode=require
                                       # (sahip rolü ya da public'te CREATE yetkisi olan rol ise API açılışı reddeder)
QLAB_MIGRATION_DATABASE_URL=           # postgresql+psycopg://<sahip>:...@HOST/DB?sslmode=require (yalnız açılışta migration)
QLAB_OIDC_ISSUER=                      # Zitadel keşif belgesindeki issuer, birebir
QLAB_OIDC_AUDIENCE=                    # Zitadel proje kimliği
QLAB_OIDC_CLIENT_ID=                   # qlab-web uygulamasının Client ID'si
QLAB_OIDC_STAFF_ORG_ID=                # Staff organizasyon kimliği
# PORT'u Render verir; QLAB_DEV_KEY_FILE staging'de tanımlanmamalıdır (reddedilir).

# --- qlab-web (Render; derlemede gömülür) ---
NEXT_PUBLIC_QLAB_ENV=staging           # render.yaml'da hazır
QLAB_API_URL=                          # https://qlab-api-xxxx.onrender.com (sonda / yok)
NEXT_PUBLIC_OIDC_ISSUER=
NEXT_PUBLIC_OIDC_CLIENT_ID=
NEXT_PUBLIC_OIDC_PROJECT_ID=
NEXT_PUBLIC_OIDC_STAFF_ORG_ID=
NEXT_PUBLIC_OIDC_LEARNER_ORG_ID=

# --- GitHub Actions secrets (backup) ---
NEON_BACKUP_URL=                       # postgresql://qlab_backup:...@HOST/DB?sslmode=require
BACKUP_AGE_RECIPIENT=                  # age1... AÇIK anahtar; özel anahtar yalnızca sizde, çevrimdışı

# --- Yalnızca kendi bilgisayarınızda (yükleme komutları) ---
QLAB_DATABASE_URL=                     # Neon uygulama adresi
```

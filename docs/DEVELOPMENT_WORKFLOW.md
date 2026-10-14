# DEVELOPMENT_WORKFLOW

> **Durum: ONAYLANDI** (2026-10-11, proje sahibi). Değişiklikler [DECISIONS.md](DECISIONS.md) üzerinden işlenir.
> Claude Code ile geliştirme yöntemi. Ajan tanımları taslaktır; dosyaların kendisi M0'da oluşturulur ve alan adları güncel Claude Code
> belgelerinden teyit edilir.

## 1. İlkeler

1. **Hafıza belgelerde.** Her oturum sıfırdan başlar. Süreklilik `docs/`, `CLAUDE.md`, testler ve git geçmişindedir.
2. **Her işi ajana çevirme.** Alt ajan yalnızca ona yazılanı bilir; ana oturum yalnızca özetini görür. Devirlerde ayrıntı kaybolur.
3. **Önce sözleşme, sonra paralellik.** Şema, API sözleşmesi ve migration ana oturumda yazılır ve dondurulur.
4. **Yazan ile sınayan ayrı.** Test yazarı uygulamayı görmez; inceleyen, yazarın gerekçesini görmez.
5. **Kurallar kodla zorlanır.** Yazılı talimat unutulabilir; CI unutmaz.
6. **Küçük dilim, tek pull request.** Bir oturum bir dikey dilim yapar.

## 2. Depo düzeni (öneri)

```
/
├─ CLAUDE.md
├─ docs/                    mimari belgeler
├─ apps/
│  ├─ api/                  FastAPI: modül başına paket (identity, content, generation, …)
│  └─ web/                  Next.js
├─ packages/
│  ├─ question-renderer/    tek soru gösterim bileşeni
│  └─ api-client/           OpenAPI'den üretilen istemci (elle düzenlenmez)
├─ prompts/                 sürümlü prompt dosyaları
├─ evals/                   ölçüm takımı ve set tanımları (set verisi rights kurallarına tabi)
├─ infra/                   dağıtım tanımları
└─ .claude/
   ├─ agents/               alt ajan tanımları
   └─ settings.json         izinler ve hook'lar
```

## 3. Dilim döngüsü

```mermaid
flowchart TD
  A[Roadmap'ten dilim seç] --> B[Plan: kapsam, sözleşme, kabul testi]
  B --> C[Sözleşmeyi yaz ve dondur: şema, OpenAPI, migration]
  C --> D[Kabul testini yaz; başarısız olduğunu gör]
  D --> E{Paralel iş var mı?}
  E -->|hayır| F[Ana oturum uygular]
  E -->|evet| G[Uygulayıcılar ayrı worktree'lerde]
  C --> T[Test yazarı: yalnız spesifikasyonla]
  F --> H[Birleştir, tüm testleri çalıştır]
  G --> H
  T --> H
  H --> I[Bağımsız inceleme; kritik alanda güvenlik incelemesi]
  I --> J{Kritik alan mı?}
  J -->|evet| K[İnsan onayı]
  J -->|hayır| L[CI yeşil + inceleme temiz]
  K --> M[Merge]
  L --> M
  M --> N[Belgeleri güncelle]
```

**Dilim tanımı** (her dilim için yazılır): amaç; kapsam dışı; dokunulan modüller; sözleşme değişikliği; kabul testleri; kritik alan mı;
ilgili belge bölümleri.

## 4. Roller ve model dağılımı

| Rol | Model | Araç izni | Görev |
|---|---|---|---|
| **Tech lead** (ana oturum) | Opus 5.5 | Tam | Plan, sözleşme, kritik modüller, birleştirme, belgeler |
| `backend-implementer` | Sonnet 5.5 | Okuma, yazma, test çalıştırma; kendi worktree'si | Donmuş sözleşmeye karşı backend dilimi |
| `frontend-implementer` | Sonnet 5.5 | Aynı | Donmuş sözleşmeye karşı arayüz dilimi |
| `test-writer` | Sonnet 5.5 | Okuma (yalnız spesifikasyon ve sözleşme), test dosyası yazma | Spesifikasyondan test |
| `explorer` | Haiku 5.5 | Salt okuma, web | Kütüphane ve kod keşfi; özet döner |
| `reviewer` | Opus 5.5 | Salt okuma | Doğruluk ve mimari uygunluk incelemesi |
| `security-reviewer` | Opus 5.5 | Salt okuma | Yetki, rights, girdi doğrulama, gizli anahtar, enjeksiyon |

Kadro bilinçli olarak küçük. Yeni rol ancak tekrar eden bir ihtiyaç kanıtlanınca eklenir.

### Alt ajan kullanılır

- Sözleşmesi donmuş, birbirinden bağımsız dilimler (ör. bir uç nokta grubu ve onun ekranı).
- Birbirine benzeyen çok sayıda parça (diyagram şablonları, kod kontrolleri, blok tipi bileşenleri).
- Okuma ağırlıklı keşif.
- Test yazımı ve inceleme.

### Alt ajan kullanılmaz (ana oturum yapar)

- Soru şeması, veri modeli, migration tasarımı.
- Yetki politikası katmanı ve rights modülü.
- Formül yorumlayıcısı.
- Pipeline durum makinesi.
- Birbirine sıkı bağlı, sözleşmesi henüz oturmamış değişiklikler.

### Ajana verilen talimatın içeriği

Amaç ve bitmiş sayılma ölçütü; okunacak belge bölümleri ve dosyalar (yeniden yazılmaz, işaret edilir); donmuş sözleşme; kapsam ve
dokunulmayacak yerler; bilinen tuzaklar; beklenen çıktı biçimi. Açık yazılamıyorsa iş henüz devredilmeye hazır değildir.

## 5. Ajan tanım taslakları

`.claude/agents/` altında, her biri ayrı dosya. Aşağıdakiler içerik taslağıdır.

```markdown
---
name: test-writer
description: Bir dilimin spesifikasyonundan ve donmuş sözleşmesinden test yazar. Uygulama kodunu okumaz.
model: sonnet
tools: Read, Glob, Grep, Write, Edit, Bash
---
Yalnızca sana verilen spesifikasyonu, sözleşmeyi (şema, OpenAPI) ve docs/ bölümlerini oku.
Uygulama dosyalarını açma. Davranışı sına, iç yapıyı değil. Sınır değerleri ve hata yollarını ekle.
docs/TESTING_STRATEGY.md'deki katman kurallarına uy. Testlerin şu an başarısız olduğunu çalıştırarak göster.
```

```markdown
---
name: reviewer
description: Bir değişikliği doğruluk ve mimari uygunluk açısından inceler. Salt okuma.
model: opus
tools: Read, Glob, Grep, Bash
---
Sana diff ve dilim tanımı verilir; yazarın açıklaması verilmez. Şunlara bak:
kabul ölçütü karşılanmış mı; docs/ ile çelişki; CLAUDE.md'deki değişmez kurallar;
testler davranışı gerçekten sınıyor mu; hata yolları; gereksiz karmaşıklık.
Her bulgu için dosya, satır, somut başarısızlık senaryosu ver. Emin olmadığını ayrıca belirt.
```

```markdown
---
name: security-reviewer
description: Kritik alanlara dokunan değişiklikleri güvenlik açısından inceler. Salt okuma.
model: opus
tools: Read, Glob, Grep, Bash
---
docs/SECURITY.md'yi oku. Odak: yetki (varsayılan ret, uç nokta-rol tablosu), rights fail-closed,
source_original sızıntısı, generation → content import yasağı, formül yorumlayıcısı beyaz listesi,
LLM girdilerinde veri/talimat ayrımı, gizli anahtar, yükleme doğrulaması, kişisel veri.
```

`backend-implementer`, `frontend-implementer` ve `explorer` aynı kalıpla yazılır: okunacak belgeler, kapsam sınırı, bitmiş sayılma ölçütü.

## 6. Merge kapıları

| Alan | Kapı |
|---|---|
| **Kritik:** yetki politikası, `rights`, formül yorumlayıcısı, migration'lar, ödeme, `ConsentPolicy` mantığı, prompt dosyaları ve ölçüm eşikleri, CI ve `.claude/` ayarları | CI + bağımsız inceleme + güvenlik incelemesi + **insan onayı** (CODEOWNERS ve dal koruması ile zorunlu) |
| Diğer | CI + bağımsız inceleme (ajan) |

CI içeriği: lint, tip kontrolü, testler, import kuralları, yetki tablosu, OpenAPI ↔ istemci uyumu, bağımlılık ve gizli anahtar taraması;
kritik modüller değiştiyse mutation testing.

## 7. Hook ve izin önerileri

| Ne | Amaç |
|---|---|
| Düzenleme sonrası format ve tip kontrolü | Hızlı geri bildirim |
| Üretilen istemcinin ve uygulanmış migration dosyalarının elle düzenlenmesini engelleme | Sözleşme bütünlüğü |
| `.env`, gizli anahtar dosyaları ve production kimlik bilgilerine erişim yok | Sızıntı önleme |
| Production'a dağıtım komutları ajan izninde yok | İnsan kararı |
| Test ve lint komutları önceden izinli | Gereksiz onay istemi olmasın |

## 8. Paralel hatlar

Ürün hattı ve içerik/AI hattı ayrı worktree'lerde, ayrı oturumlarda yürür. Ortak dokunulan yerler (şema, `content` modülü, gösterim
bileşeni) için değişiklik önce sözleşme olarak tek bir pull request'te birleşir, sonra iki hat ona göre ilerler.

## 9. Çok ajanlı iş akışları

Aynı kalıbın çok sayıda parçaya uygulandığı işler (ör. on diyagram şablonu, her kod kontrolü için test, çok boyutlu inceleme)
deterministic bir iş akışıyla dağıtılabilir. Bu, token tüketimini hızla artırır; yalnızca proje sahibi açıkça istediğinde kullanılır.

## 10. İnsanda kalanlar

- Kritik alanlarda merge onayı.
- Fizik doğruluğu: içerik incelemesi ve ölçüm setlerinin etiketlenmesi.
- Production'a dağıtım, gizli anahtarlar, sağlayıcı sözleşmeleri.
- Hukuki kararlar ve kural tablosunun içeriği.
- Mimari kararların değiştirilmesi ([DECISIONS.md](DECISIONS.md)).

## 11. Aşama sonu rutini

1. **Mimari uygunluk incelemesi:** ayrı bir oturum kodu `docs/` ile karşılaştırır; sapmaları listeler.
2. Kritik modüllerde mutation testing sonucu gözden geçirilir.
3. Belgeler güncellenir; karar değiştiyse `DECISIONS.md`'ye yazılır.
4. Risk kaydı güncellenir.

## 12. Geliştirme ve üretim ayrımı

Kod yazımı geliştirme aboneliğiyle yapılır. Ürünün LLM çağrıları ve ölçüm çalıştırmaları ürünün kendi API anahtarları ve bütçesiyle
yapılır; ikisi karıştırılmaz. Paralel alt ajanlar abonelik kotasını hızlı tüketir; paralellik yalnızca gerçekten bağımsız işlerde kullanılır.

## 13. Yerel ortam

```
docker compose -f infra/local/compose.yaml up -d      # PostgreSQL, 127.0.0.1:54340
(cd apps/api/katex && npm ci --ignore-scripts)            # sabitlenmiş KaTeX; Node >= 24 gerekir
cd apps/api
export QLAB_DATABASE_URL=postgresql+psycopg://qlab:qlab-local-only@127.0.0.1:54340/qlab
uv run alembic upgrade head
uv run python -m qlab.syllabus ../../content/reference/dp-physics-2025-syllabus.json
uv run python -m qlab.content.pilot convert --check       # depodaki JSON, Markdown'ın çevirisi mi (Node ister)
uv run python -m qlab.content.pilot load --operator <hesap kimliği> --create-rights   # 130 pilot soru, taslak olarak
uv run pytest                                          # veritabanı testleri qlab_test veritabanını silip yeniden kurar

# API (dilim 5): yerel hesaplar, token ve sunucu
export QLAB_ENV=local
uv run python -m qlab.api.dev init                     # geliştirme anahtarı (~/.qlab, depo dışı) + her rol için bir hesap
uv run python -m qlab.api.dev token content_admin      # 8 saatlik token; Authorization: Bearer <token>
uv run uvicorn --factory qlab.api.app:app_from_env --host 127.0.0.1 --port 8000
uv run python -m qlab.api.openapi                      # sözleşme değişince: apps/api/openapi.json
(cd ../../packages/api-client && npm ci --ignore-scripts && npm run generate)   # ve ondan üretilen istemci
```

- Veritabanı testleri (`db` işaretli) gerçek PostgreSQL ister; sunucuya ulaşılamazsa atlanmaz, **başarısız olur**. Yalnızca saf
  testler: `uv run pytest -m "not db"`. Başka bir sunucu için `QLAB_TEST_DATABASE_URL` (veritabanı adı `_test` ile bitmelidir).
- Matematik içeren kayıtlar Node ve `apps/api/katex/node_modules` ister; yoksa `RendererUnavailable` hatası alınır ve hiçbir şey
  kaydedilmez. Node'suz çalıştırılabilen testler: `uv run pytest -m "not db and not node"`. Başka konumlar için `QLAB_NODE_BIN` ve
  `QLAB_KATEX_DIR`.
- Pilot Markdown değişince `convert` yeniden çalıştırılır ve JSON ile rapor birlikte commit edilir; CI `convert --check` ile denetler.
  `load` yeniden çalıştırılabilir; `--create-rights` yalnızca ilk kez gerekir, `--dry-run` hiçbir şey yazmaz
  ([pilot/IMPORT_RULES.md](pilot/IMPORT_RULES.md) §7).
- **Sözleşme.** `apps/api/openapi.json` ve `packages/api-client/src/schema.d.ts` üretilir, elle düzenlenmez; ikisi de CI'da
  üretilenle karşılaştırılır. Uç nokta eklemek üç yerde değişiklik ister: yol, `qlab/api/policy.py` içindeki politika tablosu ve
  yetki tablosu testi; biri eksikse uygulama açılmaz ya da test kalır.
- Compose dosyasındaki parola yalnızca yerel içindir; loopback'e bağlıdır ve gizli anahtar değildir.
- Aynı klasörde birden çok oturum çalışıyorsa her oturum kendi worktree'sinde ve kendi test veritabanıyla çalışır (§8).
- **Oturum başında denetlenecekler.** (1) Docker Desktop yeniden başlatmadan sonra kapalı gelir; veritabanı testleri ve içe aktarma
  için önce Docker, sonra `docker compose -f infra/local/compose.yaml up -d --wait` çalıştırılır. (2) `git worktree list` ile `main`
  dalının hangi klasörde açık olduğuna bakılır; bir dal aynı anda yalnızca bir klasörde açık olabilir, bu yüzden dilim dalı `main`'in
  açık olduğu klasörde ya da ondan türetilen yeni bir worktree'de açılır. (3) Matematik içeren testler için `apps/api/katex` altında
  `npm ci` yapılmış olmalıdır.
- **Uzak depo ve CI.** Uzak depo henüz açılmadı (D-43, sahibinin kararı); `.github/workflows/ci.yml` bu yüzden **hiç çalışmadı**.
  Yerelde aynı denetimler elle çalıştırılır: `ruff format --check .`, `ruff check .`, `mypy`, `lint-imports`,
  `python -m qlab.content.pilot convert --check`, `pytest`. Uzak depo açıldığında ilk iş akışının sonucu ayrıca doğrulanır
  (PostgreSQL servisi, Node 24 kurulumu ve `npm ci` adımı denenmemiştir).

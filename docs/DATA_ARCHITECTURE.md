# DATA_ARCHITECTURE

> **Durum: ONAYLANDI** (2026-10-11, proje sahibi). Değişiklikler [DECISIONS.md](DECISIONS.md) üzerinden işlenir.
> Şemalar gösterim amaçlıdır; kesin alan adları M0'da Pydantic modelleriyle sabitlenir.

## 1. Depolama yerleşimi

| Veri | Yer | Not |
|---|---|---|
| İlişkisel veri, soru gövdeleri (JSONB), iş kuyruğu, embedding'ler | PostgreSQL | Tek veritabanı; pgvector eklentisi |
| Kaynak PDF'ler, sayfa görüntüleri, sayfa kırpımları, diyagramlar, cevap fotoğrafları | S3-uyumlu object storage | Veritabanında yalnızca anahtar ve meta veri |
| Yayınlanmış soru dokümanları, açık görseller | CDN | Sürüm değişmez olduğu için süresiz önbellek |
| Gizli anahtarlar | PaaS gizli anahtar deposu | Depoda ve veritabanında yok |

Ayrı vector DB, doküman DB ya da Redis MVP'de yok. Tetikleyici: [TECH_STACK.md](TECH_STACK.md).

## 2. İlişkisel iskelet + JSONB içerik (D-19)

**Doğruluk kaynağı JSON belgedir;** ilişkisel satırlar ondan türetilir (D-50). Yapı satırlarda, zengin içerik JSONB'de durur.
Gerekçe: cevap, puan ve analitik parçaya ve markscheme maddesine foreign key ile bağlanır. Uygulanan tablolar §2.2'dedir; ilk
taslaktaki `answer_spec`, madde başına `marks`, ayrı `solution_model` ve `asset` tabloları şema v1 ile kalktı ya da ertelendi.

### 2.1 Temel tablolar — uygulanan hali (dilim 2a, 2026-10-12)

Kod: `apps/api/src/qlab/{audit,rights,syllabus}/models.py`; migration `apps/api/migrations/versions/0001_foundation.py`.
Kimlikler UUIDv7'dir; ön ekli biçim (`q_…`) yalnızca API sınırında üretilir (D-54).

```
audit_log(id, occurred_at, actor, action, entity_type, entity_id, data jsonb)      -- yalnızca ekleme
rights_record(id, holder, license_ref, display_scope: none | organization | all,
              display_organization_id, allows_ai_processing, allows_commercial_use,
              valid_from, valid_until, revoked_at, note, created_at)
program(id, code, name)
subject(id, program_id, code, name)
syllabus_version(id, subject_id, code, title)
syllabus_node(id, syllabus_version_id, parent_id, code, title, position, attributes jsonb)
exam_format(id, syllabus_version_id, code, definition jsonb)
```

- `audit_log`: UPDATE, DELETE ve TRUNCATE veritabanı tetikleyicisiyle reddedilir; tetikleyiciler `ENABLE ALWAYS` durumundadır.
  `occurred_at` değerini yazan değil veritabanı koyar (ekleme anının saati); geriye tarihli kayıt yazılamaz ve kayıtlar oluş sırasıyla
  okunur. `actor` opak hesap kimliği ya da `system:<süreç>` biçimindedir (harf, rakam ve `_ . : | -`); ad ya da e-posta yazılamaz.
  `data` sınırlı boyutta bir JSON nesnesidir ve kişisel veri değil kimlik ve kod taşır. Bu kuralları hem servis hem tablo (CHECK) zorlar.
  Kayıt, anlattığı değişiklikle aynı transaction'da yazılır.
  **Sınır:** tetikleyiciler tablonun sahibi olan ya da superuser olan rolü durduramaz. Uygulama, tablo sahibi olmayan ve superuser
  olmayan ayrı bir rolle çalışmalıdır ([SECURITY.md](SECURITY.md) §10); yerelde ve CI'da şimdilik tek rol var.
- `rights_record`: her izin varsayılan olarak kapalıdır. Karar kuralı (`qlab.rights.service.evaluate`): kayıt yoksa, geçerlilik
  aralığının dışındaysa, iptal edilmişse ya da ilgili bayrak kapalıysa **ret**. Karar her seferinde veritabanından okunur.
  Saklanan kayıt değişmez: tek izinli değişiklik ilk iptaldir (tetikleyici); genişletme, iptali geri alma ve silme reddedilir. Farklı
  bir izin yeni bir kayıttır. `rights` modülü `audit`'e bağımlı olamadığı için kayıt açma ve iptalin audit kaydını **çağıran** yazar.
  Kill switch bu dilimde yok; `source_original` yolları `content` modülünde tümden kapalıdır (D-47, D-52).
- Müfredat ve sınav biçimi bir referans dosyasından yüklenir (`content/reference/*-syllabus.json`,
  `python -m qlab.syllabus <dosya>`). Yükleme idempotenttir ve hiçbir şey silmez: dosya var olan bir düğümü, sınav bölümünü ya da
  komut sözcüğünü düşürüyorsa ya da sınav biçiminin kodunu değiştiriyorsa reddedilir. Bir müfredat sürümünün tek sınav biçimi vardır;
  bir düğümün üst düğümü aynı sürümdendir. Dosyanın beyan ettiği inceleme durumu (`status`) sürümle birlikte saklanır. Başlıklar kısa
  etiketlerdir (en çok 120 karakter) ve düğüm öznitelikleri küçük bir kod → kod eşlemesidir; daha uzun metin dosyaya giremez.
  Programa özgü kavramlar (bölüm kodları, komut sözcükleri, düğüm düzeyi) sütun değil veridir (CLAUDE.md kural 12).
  `MarkingPolicy`, bölüm süreleri ve puanları, hesap makinesi izni henüz yok; uzman teyidinden sonra eklenir.

### 2.2 Soru tabloları — uygulanan hali (dilim 2b, 2026-10-12)

Kod: `apps/api/src/qlab/content/models.py`, `service.py`; migration `0002_content.py`.

```
question(id, origin, rights_record_id, syllabus_version_id, syllabus_status, created_by, created_at)
question_version(id, question_id, version_no, status, schema_version, document jsonb, content_sha256,
                 question_class, exam_section, levels[], total_marks,
                 has_unverified_visuals (veritabanı hesaplar), created_by, created_at, updated_at)
part(id, question_version_id, position, part_key, label, marks, answer_type)          -- belgeden türetilir
mark_point(id, part_id, position, point_key, kind, alternative_group, route)          -- belgeden türetilir
question_version_syllabus(question_version_id, syllabus_node_id, is_primary)          -- belgeden türetilir
question_version_check(id, question_version_id, check_code, severity, outcome, detail jsonb, created_at)
```

- **Belge ve özet.** `document` şema v1 belgesidir; `content_sha256` kanonik JSON'un özetidir ve her durum geçişinde audit kaydına
  yazılır. Okunan belge yazılanla aynı baytlara serileşir. Çoktan seçmeli soru tek `part` satırı taşır (`part_key = "mcq"`).
- **Yayınlanan sürüm** ayrı bir işaretçi sütunuyla değil durumla bulunur: bir sorunun en çok bir `published` ve en çok bir
  "üzerinde çalışılan" (`draft`, `auto_checking`, `needs_fix`, `in_review`, `approved`) sürümü olabilir (kısmi tekil indeks).
- **Değişmezlik (D-55).** İçerik yalnızca `draft` ve `needs_fix` durumunda değişir; `in_review`, `approved`, `published`,
  `withdrawn` ve `rejected` durumlarında veritabanı tetikleyicisi reddeder. Yayınlanmış sürümün düzeltmesi yeni sürümdür
  (`start_revision`). Türetilmiş satırlar da yalnızca bu iki durumda değiştirilebilir; hiçbir soru ya da sürüm silinemez.
- **Durum geçişleri** [DOMAIN_MODEL.md](DOMAIN_MODEL.md) §4'teki çizgeyle sınırlıdır; hem servis hem tetikleyici zorlar. Yeni sürüm
  yalnızca `draft` olarak eklenebilir.
- **Yayın koşulları** (CLAUDE.md kural 8; servis ve tetikleyici): durum `approved` (ya da yeniden yayın için `withdrawn` ve daha
  yeni sürüm yok); zorunlu kontrollerin hepsi geçmiş ve başarısız kritik kontrol yok; doğrulanmamış görsel yok; rights kaydı gösterime
  izin veriyor (bu sonuncusu yalnızca serviste). Asset tablosu gelene kadar uyaranı olan her belge "doğrulanmamış görsel" sayılır:
  incelenip onaylanabilir ama yayınlanamaz (D-49).
- **Kontroller.** `submit` kendi kontrollerini (`schema_valid`, `vocabulary_valid`) çalıştırır ve saklar; dış kontroller
  `record_check` ile yazılır (üretim hattı, M3). **Eksik kontrol geçmiş sayılmaz:** incelemeye ve yayına geçiş, zorunlu kontrollerin
  bu içerik üzerinde "geçti" olarak kayıtlı olmasını ister (servis `REQUIRED_CHECKS`, tetikleyici aynı listeyi taşır; yeni zorunlu
  kontrol ikisine birlikte eklenir). Sonuçlar yalnızca içerik gerçekten değişince silinir; aynı belgeyi yeniden kaydetmek başarısız
  bir sonucu temizlemez. Sonuçlar `in_review`'dan sonra değiştirilemez.
- **İçeriğe bağlı kararlar.** Onay, yayın ve yeniden yayın çağrıları, çağıranın gördüğü içeriğin özetini (`expected_content_sha256`)
  taşır; içerik o arada değiştiyse reddedilir. Durum değiştiren işlemler içerik döndürmez (yalnızca kimlik, durum, özet).
- **Bütünlük.** Her yazma işlemi bir savepoint içinde çalışır: hata olursa ne değişiklik ne audit kaydı kalır. Aynı sorunun
  sürümleri üzerindeki işlemler soru satırı kilitlenerek sıraya girer.
- **Sınırlar.** Belge en çok 512 kB (serviste; tabloda 1 MB), kontrol ayrıntısı en çok 8 kB, gerekçe en çok 500 karakter.
- **Tetikleyici güvenliği.** Koruma işlevleri `search_path` değerini sabitler (`pg_temp` sonda) ve tabloları şema adıyla anar; aynı
  adlı geçici tablo yaratılarak atlatılamaz.
- **Sözlük.** Kayıtta sınav bölümü, komut sözcükleri ve müfredat düğümleri (yalnızca yaprak düğümler) sorunun müfredat sürümüne
  göre doğrulanır; uymayan belge kaydedilmez.
- **Köken ve rights.** Servis ve tetikleyici yalnızca `authored` kabul eder (D-52). Her işlem (kontrol kaydı dahil) rights kaydının
  şu an herkese gösterime izin vermesini ister; izin yoksa yazma reddedilir, okuma "bulunamadı" döner. Yalnızca kısıtlayan işlemler
  (geri çekme, ret, düzeltme isteme) rights iptal edilmiş olsa da çalışır ve içerik döndürmez.
- **Onay.** M1-G'de tek onay yeter (D-53). Rol denetimi bu katmanda değil, yetki katmanındadır (dilim 5); servis yalnızca `actor`
  kimliğini audit'e yazar.

**Sonraki dilimlere devredenler**

1. Rights kaydı açan ya da iptal eden her yol audit kaydı yazar; bunu bir test doğrular (içe aktarma komutu, dilim 4; yönetim uç noktaları).
2. Kill switch eklendiğinde her çağıranda değil `rights.is_permitted` içinde durur.
3. `source_original` açılırsa `content`, rights sonucundan bağımsız olarak kurum üyeliğini de ister (CLAUDE.md kural 3); şu an köken tümden kapalı.
4. Rol denetimi ve "onaylayan yazardan farklı olmalı mı" sorusu yetki katmanıyla birlikte ele alınır (dilim 5; D-53 web'e açılıştan önce yeniden değerlendirilir).
5. **Öğrenci görünümü (dilim 5 ve 8).** `get_published_version` belgenin tamamını döndürür (doğru cevap, açıklamalar, markscheme,
   yazarın hesap kimliği). Öğrenci uç noktası bunu olduğu gibi veremez; cevap malzemesini ve personel kimliklerini çıkaran ayrı bir
   görünüm tipi yazılır, entitlement ve `syllabus_status` orada denetlenir.
6. Veritabanı, `content_sha256` değerinin, kopya sütunların ve türetilmiş satırların belgeyle uyumunu denetlemez; `draft` ve
   `needs_fix` durumunda ham SQL ile ayrıştırılabilir. Uygulama rolüyle ham SQL yazabilen biri zaten uygulamanın kendisidir; yine de
   cevaplar `part`/`mark_point` satırlarına bağlanmadan önce (M2) okuma anında özet doğrulaması değerlendirilir.
7. Yayın anında rights kaydı kilitlenmez; yayınla aynı anda yapılan iptal yayını durdurmayabilir. Her okuma rights'ı yeniden
   denetlediği için içerik yine de dönmez. Kill switch ile birlikte ele alınır.
8. ⚖️ Geri çekme, ret ve düzeltme isteme gerekçeleri serbest metindir ve silinemeyen audit kaydına yazılır. Gerekçeye kişi adı ya da
   soru metni yazılmamalıdır; arayüz bunu belirtir (dilim 7). Silme hakkıyla ilişkisi [SECURITY.md](SECURITY.md) §10'daki açık sorudur.
9. İncelemede bulunan bir hata kontrol sonucu olarak kaydedilemez (sonuçlar `in_review`'da kilitlidir); `request_changes` ile geri gönderilir.

## 3. İçerik bloğu şeması

ProseMirror-uyumlu düğüm yapısı: `{type, attrs?, content?, text?, marks?}`. Tek doğruluk kaynağı backend'deki Pydantic modelidir;
editör şeması ve TypeScript tipleri ondan üretilir (D-21).

### 3.1 Düğüm tipleri (şema v1)

| Tip | Tür | Öznitelikler | Not |
|---|---|---|---|
| `doc` | kök | — | `stem`, `part.body`, `mark_point.body` alanlarının kökü |
| `paragraph` | blok | — | |
| `text` | satır içi | `marks`: bold, italic, sub, sup | |
| `math_inline` | satır içi | `latex` | KaTeX alt kümesi; kayıtta render kontrolü |
| `math_block` | blok | `latex` | |
| `quantity` | satır içi | `value`, `unit`, `param`, `sig_figs?`, `uncertainty?` | Gösterim bundan üretilir |
| `table` / `table_row` / `table_cell` | blok | `header`, `colspan`, `rowspan` | Hücre içeriği satır içi düğümler |
| `figure` | blok | `asset_id`, `role`, `caption?` | Alt metin `asset` kaydında |
| `list` / `list_item` | blok | `ordered` | |
| `option_list` / `option` | blok | `key` (A–D) | Yalnızca MCQ parçalarında |
| `answer_space` | blok | `lines` | Kâğıt düzenini korumak için; ekranda cevap alanına dönüşür |

### 3.2 Örnek: parça gövdesi

```json
{
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "A ball is projected with speed " },
        { "type": "quantity", "attrs": { "value": "20", "unit": "m/s", "param": "v0", "sig_figs": 2 } },
        { "type": "text", "text": " at " },
        { "type": "quantity", "attrs": { "value": "30", "unit": "deg", "param": "theta", "sig_figs": 2 } },
        { "type": "text", "text": " above the horizontal. Calculate the horizontal range " },
        { "type": "math_inline", "attrs": { "latex": "R" } },
        { "type": "text", "text": "." }
      ]
    },
    { "type": "figure", "attrs": { "asset_id": "ast_01H...", "role": "question_diagram" } }
  ]
}
```

### 3.3 `quantity` düğümü (D-20)

- `value` metin olarak saklanır; yazıldığı haliyle anlamlı basamak korunur (`"20"` ile `"20.0"` farklıdır).
- `unit` Pint'in ayrıştırabildiği bir ifade; gösterim programın birim yazım kuralına göre deterministic üretilir (IB: `m s⁻¹`).
- `param` çözüm modelindeki parametre adıdır. Doğrulama: düğümün değeri ve birimi parametreyle birebir eşleşmelidir.
- İçerik alma bir sayıyı `quantity`'ye çeviremezse düz `math_inline` kalır; bu durumda soru "sayısal bağ doğrulanamadı" işaretiyle incelemeye gider.

### 3.4 Matematik gösterimi

- Kanonik biçim: LaTeX, KaTeX'in desteklediği alt küme. İzinli komut listesi şemanın parçasıdır.
- Kayıtta her matematik düğümü sunucuda KaTeX ile render edilir; hata varsa kayıt reddedilir (D-13).
- MathML saklanmaz; KaTeX çıktısından türetilir. KaTeX sürümü sabittir; yükseltme görsel regresyon testinden geçer.
- Hesaplama biçimi LaTeX'ten türetilmez; ayrı olarak `solution_model` içinde durur.

### 3.5 Şema v1 — uygulanan hali (2026-10-11, bağımsız inceleme sonrası)

Kod: `apps/api/src/qlab/content/schema/`. Bu bölüm §2–§4'teki eski taslaklarla çelişirse **bu bölüm geçerlidir** (D-50). Bilinmeyen alan
her düzeyde reddedilir. Tüm modeller değişmezdir. JSON'da diziler sıralıdır ve aynı belge her zaman aynı baytlara serileşir (dizilerin
sırası, işaretlerin sırası dahil, yazıldığı gibi korunur; kanonik sıra yalnızca `levels` için zorunludur).

#### Düğümler (ProseMirror JSON biçimi)

`type` her düğümde zorunludur. İşaretler nesne dizisidir: `"marks": [{"type": "bold"}]`.

| Düğüm | Tür | İçerik / öznitelik |
|---|---|---|
| `doc` | kök | en az bir blok |
| `paragraph` | blok | satır içi düğümler (boş olabilir) |
| `math_block` | blok | `attrs.latex` (boş olamaz) |
| `table` → `table_row` → `table_header` / `table_cell` | blok | hücre: yalnızca `paragraph`, en az bir; `attrs.colspan` (1–12), `attrs.rowspan` (1–50). Satır birleştirme yoksa tüm satırların genişliği eşit olmalı |
| `figure` | blok | `attrs.stimulus_id` |
| `bullet_list`, `ordered_list` → `list_item` | blok | madde: yalnızca `paragraph`, en az bir (iç içe liste yok) |
| `text` | satır içi | `text` (boş olamaz), `marks` |
| `math_inline` | satır içi | `attrs.latex`, `marks` |
| `quantity` | satır içi | `attrs.value`, `attrs.unit`, `attrs.param`, `attrs.uncertainty`, `marks` |
| `hard_break` | satır içi | — |

- İşaret türleri: `bold`, `italic`, `sub`, `sup`, `optional` (markscheme'de « »: puan için gerekmeyen), `essential` (altı çizili: zorunlu).
  Aynı işaret iki kez olamaz; `sub` ile `sup` ve `optional` ile `essential` birlikte olamaz. İşaretler `text`, `math_inline` ve `quantity`
  üzerinde kullanılabilir (ör. `3.0 «s»`).
- Sayı metni (`value`, parametre değeri, kabul aralığı): ASCII rakamlar, isteğe bağlı baştaki `-`, isteğe bağlı ondalık kısım, isteğe
  bağlı `e`/`E` ve üs (üssün işareti isteğe bağlı). Geçerli: `20`, `20.0`, `-5`, `1.5e-3`, `1e+3`. Geçersiz: `+5`, `.5`, `5.`, Unicode eksi ya da rakam.
  `uncertainty` aynı biçimde ama işaretsiz. Değer metin olarak saklanır; `20` ile `20.0` farklıdır.
- Birim metni: boş ya da ASCII harf, `µ` (U+00B5), `Ω`, `°`, `%` ile başlar; devamında bunlara ek olarak rakam, boşluk ve `/ * ^ ( ) . -`
  olabilir; baş ve sonda boşluk olamaz. Kural tüm birim alanlarında aynıdır (büyüklük, parametre, adım, kabul aralığı). Bu yalnızca biçim denetimidir; birim dilbilgisi
  yorumlayıcıyla gelir. Karşılaştırmalar birebir metin eşitliğidir (`m/s` ile `m s^-1` eşit sayılmaz).

#### `QuestionDocument`

| Alan | Kural |
|---|---|
| `schema_version` | Zorunlu, `"1.0"` |
| `question_class` | `mcq`, `data_based`, `short_structured`, `long_structured` |
| `exam_section` | Küçük harfli kısa ad (ör. `paper_1a`); kayıtta sorunun müfredat sürümünün sözlüğüne göre doğrulanır (§2.2) |
| `levels` | Kullanılabildiği kâğıtlar; en az bir; tekrarsız ve kanonik sırada (`sl`, `hl`) |
| `language`, `calculator`, `difficulty` (`easy`/`medium`/`hard`), `outcome` | İsteğe bağlı üst veri; `outcome` yazarın kendi cümlesi |
| `primary_syllabus_node`, `secondary_syllabus_nodes` | Tekrarsız |
| `stem` | Boş olamaz |
| `stimuli[]` | `id` tekil; `kind`; `use` (`read_only`, `read_values`, `student_annotates`); `description` (boş olamaz); `asset_id`; `alt_text`. `asset_id` varsa `alt_text` zorunlu. Herhangi bir uyaranın `asset_id` değeri yoksa `visual_pending` doğrudur |
| `mcq` / `parts[]` | Sınıfa göre: `mcq` sınıfında `mcq` bloğu var, `parts` boş, `total_marks` = 1; diğerlerinde `mcq` yok, en az bir parça var, parça puanları toplamı `total_marks` |
| `solution_model` | İsteğe bağlı |

Belgedeki her `figure` düğümü ve her `stimulus_refs` girdisi var olan bir uyarana gitmelidir.

#### Çoktan seçmeli bloğu (`mcq`)

- `option_kind` (6 değer), `option_layout` (`single_value`, `two_column_table`, `figure_options`, `roman_statements`).
- `options`: tam olarak A, B, C, D sırasıyla. Her seçenek `cells` (birer `doc`) taşır: iki sütunlu tabloda 2 hücre ve `column_headers`
  2 başlık; diğer düzenlerde 1 hücre ve başlık yok. `roman_statements` düzeninde en az 2 `statements`, diğerlerinde hiç.
- Her yanlış seçenek boş olmayan bir `rationale` (`doc`) taşır. İki seçenek aynı olamaz.
- `correct_key`, `explanation` (çözüm, `doc`), `assessment_objective`, `level_content`, `solution_step` (cevabın çözüm modelindeki adımı).

#### Parça

`id` (soru içinde tekil), `label` (`a`, `b.ii`; harf a–z, alt parça i–viii), `lead_in` (parçadan önce gösterilen, üst harfe ait ya da yeni
bağlam veren metin), `body` (boş olamaz), `marks` (1–3), `marks_capped`, `show_that`, `command_term`, `answer_type` (14 değer),
`assessment_objective`, `level_content`, `syllabus_node` (sorunun düğümlerinden biri), `stimulus_refs`, `depends_on`, `ecf_from`,
`mark_points[]`, `notes[]`.

- Etiketler tekil ve sıralıdır; bir harf hem alt parçasız hem alt parçalı kullanılamaz (`a` ile `a.i` birlikte olmaz).
- `depends_on` ve `ecf_from` yalnızca **önceki** parçalara gider; bunlar ve `stimulus_refs` tekrar içermez. Etiketlerde boşluk
  bırakılabilir (`a`, `c`); yalnızca sıra ve tekillik zorunludur.
- `sl` içeren soruda `ahl` içerikli parça ya da `ahl` içerikli çoktan seçmeli olamaz.

#### Markscheme

- Her `MarkPoint` bir puandır: `id` (soru genelinde tekil), `content` (`doc`), `kind` (`method`, `answer`, `statement`),
  `alternative_group`, `route`, `accept_range` (`minimum` ≤ `maximum`, sayı metni; `unit`), `solution_step`.
- **Alternatifler (OR):** aynı `alternative_group` içindeki maddeler tek bir puanın alternatifidir.
- **Yollar (ALTERNATIVE 1 / 2):** aynı `route` değerini taşıyan maddeler parçanın puanlarını kazanmanın eksiksiz bir yoludur; yollar
  birbirini dışlar. Tek yol tanımlanamaz (en az iki).
- **Ödüllendirilebilir puan** = yolu olmayan maddeler (her alternatif grubu bir kez) + en iyi yolun maddeleri (aynı sayımla).
- `marks_capped` yanlışsa ödüllendirilebilir puan parça puanına **eşit** olmalıdır; doğruysa parça puanından **büyük** olmalıdır ("max").
- **Birlikte gereken (AND):** tek puan için iki ifade gerekiyorsa ikisi aynı maddenin içeriğinde yazılır; ayrı bir yapı yoktur.
- `notes[]`: parça düzeyinde not; `kind` (`general`, `owtte`, `accept`, `do_not_accept`, `cap`, `ecf`), `content` (`doc`), isteğe bağlı
  `mark_point_id` (o parçanın bir maddesi olmalı).

#### Çözüm modeli

`parameters[]` (ad, değer, birim), `constants[]` (ad, `ref`), `steps[]` (`id`, `name`, `expr`, `unit`, `stated_value`), `answers[]`
(`part_id`, `step`). Veri olarak saklanır, **hesaplanmaz**; doğrulama durumu belgede değil, sistemin durumunda tutulur.

- Parametre, sabit ve adım adları birlikte tekildir; adım `id` değerleri tekildir.
- Bir parçanın en çok bir cevap bağı vardır; bağlar var olan parça ve adıma gider.
- Madde ve çoktan seçmeli `solution_step` değerleri var olan bir adıma gider.
- `param` taşıyan her `quantity`, aynı adlı parametreyle değer ve birim metni olarak birebir aynıdır. **Çözüm modeli yoksa `param` ve
  `solution_step` taşımak hatadır.**
- `stated_value` (sayı metni): "show that" parçasında soruda verilen değer; sonraki adımlar hesaplanan yerine bunu kullanır.

#### Bilerek olmayanlar

Düzey tanımlayıcılı (3/2/1/0) puanlama · "birlikte gereken" için ayrı yapı · veri tablosu sütununa bağlı belirsizlik alanı (başlık
metninde yazılır) · `answer_space` düğümü · Blueprint şeması · doğrulama durumu.

#### Henüz kodla zorlanmayanlar

Boş bırakılabilen metinler (`lead_in`, madde ve not içeriği, seçenek hücresi, açıklama) · yolların eşit puanlı olması · işaretlerin
kanonik sırası · kullanılmayan uyaran ·

KaTeX render kontrolü (dilim 3) ·
sayısal cevaplı her parçanın bir cevap bağı taşıması (yorumlayıcıyla) · birim dilbilgisi · adım ifadelerindeki adların tanımlı olması ·
dört seçeneğin aynı türde ve sıralı olması · komut sözcüğü ↔ puan ↔ cevap türü kuralları · soru sınıfına göre toplam puan sınırları.

#### v1 sınırı: sınav yapısına ait sabitler

Dört seçenek (A–D), çoktan seçmelinin 1 puan olması, alt parçanın en çok 3 puan olması ve `sl`/`hl` ile `sl_core`/`ahl` ayrımı şemada
sabittir. CLAUDE.md kural 12'ye göre bunlar programın verisi olmalıdır; ikinci program eklendiğinde sınav biçimi kaydına taşınacaktır (D-50).

## 4. Çözüm modeli: bildirimsel formül zinciri (D-23)

> Aşağıdaki örnek ilk tasarımdır. Uygulanan alan adları §3.5 "Çözüm modeli" başlığındadır: cevap bağı `part_id` ile yapılır;
> `sig_figs`, `ranges` ve ayrı `schema_version` v1'de yoktur.

```json
{
  "schema_version": "1.0",
  "parameters": [
    { "name": "v0", "value": "20", "unit": "m/s" },
    { "name": "theta", "value": "30", "unit": "deg" }
  ],
  "constants": [
    { "name": "g", "ref": "ib_dp_physics.data_booklet.g" }
  ],
  "steps": [
    { "id": "s1", "name": "R", "expr": "v0**2 * sin(2*theta) / g", "unit": "m" }
  ],
  "answers": [
    { "part_label": "a", "step": "s1", "sig_figs": 2 }
  ],
  "ranges": [
    { "param": "v0", "min": "1", "max": "100", "unit": "m/s" },
    { "param": "theta", "min": "5", "max": "85", "unit": "deg" }
  ]
}
```

- `expr` yalnızca izinli öğeleri içerir: sayılar, tanımlı adlar, `+ - * / **`, parantez ve beyaz listedeki fonksiyonlar
  (`sin cos tan asin acos atan sqrt exp ln log10 abs pi`). Yorumlayıcı ifadeyi kendi ayrıştırıcısıyla ağaca çevirir; Python `eval` ya da
  SymPy `sympify` ham metne uygulanmaz.
- Sabitler programın sabit tablosundan gelir (ör. veri kitapçığı değerleri); soruya gömülmez.
- `ranges` varyant üretiminde parametrelerin fiziksel olarak makul kalacağı aralığı tanımlar.
- Zincirle ifade edilemeyen soru `solution_model` taşımaz ve "kodla doğrulanamaz" tipinde sayılır; inceleme kuralı buna göre sıkılaşır.

## 5. Blueprint

Üretimin tek girdisi. Müfredat düğümünden ve biçim profilinden yazılır; bir sınav sorusundan türetilmez (D-45). Alanlar kapalı listeler ve kısa yapılandırılmış değerlerdir.

```json
{
  "schema_version": "1.0",
  "program": "ib_dp", "subject": "physics", "level": "HL", "exam_section": "paper_2",
  "syllabus_nodes": ["A.1"],
  "skills": ["apply_kinematics_2d", "resolve_components"],
  "structure": [
    { "label": "a", "command_term": "calculate", "marks": 2, "answer_type": "numeric" },
    { "label": "b", "command_term": "explain", "marks": 2, "answer_type": "short_text" }
  ],
  "difficulty": 3,
  "reasoning_steps": 3,
  "context_constraints": ["no_air_resistance", "single_object"],
  "needs_figure": true, "figure_template": "projectile_trajectory",
  "format_profile_version": "ib_dp_physics.paper_2@1"
}
```

Blueprint kaydı ayrıca `format_profile_version`, yazım yöntemi ve onaylayan uzmanı taşır. Ayrıntı: [AI_PIPELINE.md](AI_PIPELINE.md) §4.

## 6. Asset yönetimi

```
asset(id, storage_key, mime, bytes, width, height, sha256, alt_text,
      source: uploaded | page_crop | template_generated,
      template_id, template_params jsonb, rights_record_id, created_at)
```

- Görseller JSONB'ye gömülmez. Anahtar düzeni: `{env}/{kind}/{yyyy}/{id}.{ext}`.
- Şablondan üretilen diyagram, şablon kimliği ve parametreleriyle yeniden üretilebilir; alt metin aynı parametrelerden yazılır.
- Erişim: açık içerik CDN'den; hak kısıtlı içerik ve kullanıcı yüklemeleri kısa süreli imzalı bağlantıyla.
- Yüklemede: tür ve boyut kontrolü, görselin yeniden kodlanması, konum ve cihaz bilgisinin silinmesi.

## 7. Sürümleme ve kaynak takibi

| Ne | Nasıl |
|---|---|
| Soru içeriği | Değişmez `question_version`; `version_no` artar |
| Şema | Her JSONB alanında `schema_version`; şema değişikliği için ileri taşıma fonksiyonu ve test |
| Müfredat | `syllabus_version`; soru etiketleri belirli sürüme bağlı |
| Kaynak izi | `source_document` (sha256) → sayfa → bölge (bbox) → `question` |
| Üretim izi | `question` → `blueprint` → kaynak `question`; her adımın `step_run` ve `llm_call` kaydı |
| Prompt ve model | `prompt_version` tablosu; `llm_call` hangi sürümle çalıştığını taşır |
| Karar izi | `review`, `audit_log` (değiştirilemez, yalnızca ekleme) |

## 8. Benzerlik verisi

- `question_embedding(question_version_id, model, vector)`; pgvector indeksli.
- Yeni aday kendi soru havuzumuza karşı aranır. Sınav kurumu soruları gömülmez ve saklanmaz (D-44).
- Embedding modeli değişirse tüm vektörler yeniden üretilir; `model` sütunu karışmayı önler.

## 9. Öğrenci verisi

```
attempt(id, user_id, exam_id?, mode, started_at, due_at, submitted_at, status)
response(id, attempt_id, part_id, question_version_id, kind, payload jsonb,
         photo_asset_id?, transcript jsonb?, transcript_confirmed_at?, created_at)
marking_result(id, response_id, method, model?, prompt_version?, total, status, created_at)
mark_point_decision(marking_result_id, mark_point_id, awarded, evidence, reason)
appeal(id, marking_result_id, user_id, reason, reviewer_id?, outcome?, resolved_at?)
```

Büyüme: yılda milyonlarca `response` satırı beklenir. `(user_id, created_at)` ve `(part_id)` indeksleri; hacim artarsa aya göre bölümleme.

## 10. Veri yaşam döngüsü ve saklama

| Veri | Saklama | Silme tetikleyicisi |
|---|---|---|
| Yayınlanmış soru sürümleri | Süresiz | Hak sahibi talebi → geri çekme; öğrenci kaydı için içerik saklanır mı hukuki soru |
| Kaynak PDF ve sayfa görüntüleri | Rights kaydı geçerli olduğu sürece | Rights iptali |
| LLM çağrı kayıtları (girdi/çıktı gövdesi) | Kaynak içerik içerenler rights kaydıyla aynı; diğerleri 12 ay (öneri) | Süre dolumu |
| Öğrenci cevapları (metin) | Hesap boyunca | Hesap silme, silme talebi |
| Cevap fotoğrafları | Hesap boyunca (D-27); süre `ConsentPolicy`'de ülke ve yaş bandına göre ayarlanabilir | Hesap silme, silme talebi, kural değişikliği |
| Rıza kayıtları | Yasal süre boyunca (hukuki teyit) | — |
| Audit log | Süresiz (öneri) | — |
| Yedekler | Günlük + zaman noktasına dönüş penceresi | Pencere dolumu |

Hesap silme kaskadı: kullanıcı satırları, cevaplar, fotoğraflar (object storage dahil), rıza dışı kişisel veriler. Analitik için anonim
toplamlar kalabilir (hukuki teyit).

## 11. Yedekleme

Günlük tam yedek ve zaman noktasına geri dönüş. Geri yükleme yılda en az iki kez staging'e gerçekten yapılır. Object storage'da
sürümleme açık.

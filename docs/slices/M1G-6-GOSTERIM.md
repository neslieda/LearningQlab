# M1-G dilim 6 — web iskeleti ve soru gösterim bileşeni

> **Durum: TASLAK** (2026-10-14, mimar oturumu). §7'deki kararlar sahibinin onayını bekliyor. Dilim 5'in (PR #2) üstüne kurulur;
> dilim birleşirken içeriği kalıcı belgelere işlenir ve bu dosya kaldırılır.

## 1. Amaç ve kapsam

Amaç: soruların tek bir gösterim bileşeniyle, sınav düzeninde, masaüstünde ve 375 px genişlikte doğru görünmesi; üzerine dilim 7
(admin) ve dilim 8'in (öğrenci önizlemesi) kurulacağı web iskeleti.

Kapsam: npm çalışma alanı; `packages/question-renderer` (React bileşenleri); `apps/web` (Next.js iskeleti, yerel giriş, API vekili,
gösterim galerisi); bileşen testleri; görsel regresyon (Playwright).

Kapsam dışı: admin inceleme ve düzenleme ekranları (dilim 7), öğrenci soru listesi ve cevap ekranı (dilim 8), editör (Tiptap),
şekil üretimi, gerçek kimlik sağlayıcısı.

Kritik alan: **hayır** (CI dosyasına dokunulursa o kısım kritik). Kapı: CI + bağımsız inceleme.

## 2. Depo düzeni

```
package.json                      npm çalışma alanı: apps/web, packages/*  (özel, yayınlanmaz)
packages/api-client/              dilim 5'ten; üretilir
packages/question-renderer/       gösterim bileşeni
apps/web/                         Next.js (App Router), TypeScript strict
```

Sürümler tam sabitlenir (`^` yok), tek `package-lock.json` kökte. Kurulum `npm ci --ignore-scripts`.

## 3. Gösterim bileşeninin sözleşmesi (`@qlab/question-renderer`)

Tipler `@qlab/api-client`'tan gelir; bileşen kendi içerik tipini tanımlamaz.

| Dışa açılan | Props | Ne çizer |
|---|---|---|
| `DocView` | `doc: Doc` | Bir zengin metin belgesi (§3.1) |
| `LearnerQuestionView` | `question: LearnerQuestion`, `renderPartFooter?: (part) => ReactNode`, `renderMcqFooter?: () => ReactNode` | Öğrencinin gördüğü soru, sınav düzeninde (§3.2). Footer'lar dilim 8'in cevap alanları içindir |
| `MarkSchemeView` | `markPoints: MarkPointOut[]`, `notes: NoteOut[]`, `marks: number`, `marksCapped: boolean` | Bir parçanın puan maddeleri ve notları (§3.3) |
| `McqResultView` | `result: McqCheckResult`, `question: LearnerQuestion` | Doğru seçeneğin işaretlenmesi |
| `QuestionDocumentView` | `document: QuestionDocument`, `showAnswers: boolean` | Personel görünümü (dilim 7'nin temeli): tüm belge; `showAnswers` ile doğru seçenek, puan maddeleri, notlar, açıklama ve gerekçeler |
| `Math` | `latex: string`, `display: boolean` | Tek matematik düğümü |

### 3.1 Düğümler

- **Metin güvenliği.** `text` düğümü metin olarak çizilir; HTML olarak yorumlanmaz (`dangerouslySetInnerHTML` yalnızca KaTeX
  çıktısı için ve yalnızca `Math` içinde). Metinde matematik taraması yapılmaz (`$…$` düz metindir).
- İşaretler: `bold` → `<strong>`, `italic` → `<em>`, `sub` / `sup` → `<sub>` / `<sup>`, `optional` → « » içinde (puan için gerekmeyen sözcükler;
  DATA_ARCHITECTURE §3.5). Ardışık satır içi düğümlerin hepsi `optional` taşıyorsa (ör. içinde kalın bir sözcük, matematik ya da
  `quantity` olan bir ifade) **tek** bir « » çifti bütün diziyi sarar. `essential` → altı çizili (puan için zorunlu sözcükler) ve ekran
  okuyucuya "essential" diye bildirilir. İşaretler iç içe geçebilir; sıra çıktıyı değiştirmez.
- `math_inline` / `math_block` → `Math`. KaTeX **0.19.0** (sunucuyla aynı sürüm), sunucuyla aynı ayarlar: `throwOnError: true`,
  `strict: "error"`, `trust: false`, `maxExpand: 1000`, `maxSize: 20`, `output: "htmlAndMathml"`, paylaşılan makro yok. Render hatası
  (kayıt kontrolünden geçmiş içerikte beklenmez) sayfayı düşürmez: kaynak LaTeX düz metin olarak, `role="alert"` olmadan, görünür bir
  "math could not be displayed" işaretiyle gösterilir. KaTeX CSS'i ve fontları pakette paketlenir; CDN yok.
- `math_block` ve `table`, taşmayı kendi kaydırma kapsayıcısında keser (`overflow-x: auto`, odaklanabilir, `tabindex="0"`, erişilebilir
  ad). Sayfa 375 px'de hiçbir zaman yatay kaymaz.
- `quantity` → değer + ince boşluk (U+2009) + birim, yazıldığı gibi; `uncertainty` varsa `value ± uncertainty unit`. Birim dönüştürülmez
  ve yeniden yazılmaz (`m/s` olduğu gibi kalır; §7.3). Değer anlamlı basamağıyla, metin olarak yazılır.
- `hard_break` → `<br>`. `paragraph` → `<p>`. `bullet_list` / `ordered_list` / `list_item` → `<ul>` / `<ol>` / `<li>`.
- `table` → `<table>`. Yalnızca `table_header` hücrelerinden oluşan her satır bir **başlık satırıdır**: hücreleri `<th scope="col">`
  (birden çok sütunu kapsıyorsa `scope="colgroup"`). Başka hücrelerle aynı satırdaki `table_header` → `<th scope="row">`.
  `colspan` / `rowspan` aynen. Listeler (`<ul>`, `<ol>`) madde işaretini ve numarasını her ortamda gösterir (sayfanın CSS
  sıfırlamasına karşı).
- `figure` → şekil yer tutucusu: kesikli çerçeve, "Figure" ve uyaran türü (`kind`, okunur biçimde: `graph` → "Graph"). Öğrenci
  görünümünde tarif yoktur; personel görünümünde (`QuestionDocumentView`) tarif yer tutucunun içinde, "Description (staff only)"
  başlığıyla gösterilir. Yer tutucuya `role="img"` ve `aria-label` verilir.

### 3.2 Sınav düzeni (`LearnerQuestionView`)

- Üst satır: sınav bölümü kodu, düzey(ler) (`SL`, `HL`), toplam puan ("[n marks]"; 1 ise "[1 mark]"). Erişilebilir adda bu parçalar
  boşlukla ayrılır ("paper_2 SL HL 9 marks" gibi okunur, bitişik değil).
- Kök metin (`stem`), ardından uyaranlar (yer tutucu).
- **Çoktan seçmeli:**
  - `single_value`: dört satır, "A" … "D" etiketi + hücre.
  - `two_column_table`: başlık satırı (`column_headers`) ve A–D satırları olan bir tablo.
  - `roman_statements`: önce ifadeler "I.", "II.", "III." …; sonra seçenekler (hücreler ifade kombinasyonlarıdır).
  - `figure_options`: her seçenek bir şekil yer tutucusu.
  - Seçenekler bir liste olarak işaretlenir (`<ol>` `list-style: none`); seçim davranışı yoktur (dilim 8).
- **Yapılandırılmış:** parçalar sırayla. Etiket `a` → "(a)"; `a.i` → "(i)", harfli üst parçanın altına girintili. Aynı harfin ilk alt
  parçasından önce harf etiketi bir kez yazılır. `lead_in` gövdeden önce, aynı girintide. Puan sağa yaslı "[2]". `command_term`
  ayrıca gösterilmez (gövdenin içindedir).
- Anlamsal yapı: soru `<article>`, parçalar `<section>` + başlık seviyesi düzgün; puan metni ekran okuyucuda "2 marks" okunur.

### 3.3 Markscheme (`MarkSchemeView`)

- Maddeler sırayla, her biri `✓` ile başlayan bir satır (görsel; ekran okuyucuya "mark point"). Aynı `alternative_group`'taki maddeler
  "OR" ile birleşik tek satır grubudur. `route` taşıyan maddeler rota başına gruplanır ("Method 1", "Method 2"…).
  `accept_range` varsa "Accept min–max unit".
- Notlar maddelerden sonra; `kind` önek olarak: `owtte` → "OWTTE", `accept` → "Accept", `do_not_accept` → "Do not accept",
  `cap` → "Max", `ecf` → "ECF", `general` önek yok. `mark_point_id` taşıyan not, ilgili maddenin hemen altında girintili.
- `marksCapped` ise başlıkta "[max n]", değilse "[n]".

## 4. Web iskeleti (`apps/web`)

- Next.js App Router, TypeScript strict, Tailwind (TECH_STACK §6). Radix bu dilimde gerekmez.
- **API vekili:** tarayıcı API'ye doğrudan gitmez; Next `rewrites` ile `/api/*` → `QLAB_API_URL` (varsayılan
  `http://127.0.0.1:8000`). Böylece CORS gerekmez. Vekil yalnızca `/api/v1/*` ve `/api/healthz`'i geçirir.
- **Yerel giriş (yalnızca geliştirme):** `/dev/sign-in` sayfası, `python -m qlab.api.dev token <rol>` çıktısını yapıştırmak için bir
  alan. Token `sessionStorage`'da durur (sekme kapanınca gider), `GET /v1/me` ile doğrulanır ve hesap ile roller gösterilir. Çıkış
  düğmesi token'ı siler. Sayfa ve token saklama, `NODE_ENV=production` derlemesinde bulunmaz. Gerçek giriş dilim 9'da.
- İstemci: `@qlab/api-client` (`createApiClient({ baseUrl: "/api", getToken })`); sunucu verisi için TanStack Query.
- **Gösterim galerisi** `/dev/gallery`: sabit, sentetik örnek setini (§5) API'siz çizer; görsel regresyonun hedefidir. Her örnek
  `data-testid` taşır.
- Ana sayfa: hangi rolle girildiğini ve dilim 7–8'de gelecek alanları gösteren basit bir iskelet.
- Arayüz metinleri İngilizcedir (içerik İngilizce, D-59).
- Güvenlik başlıkları (CSP dahil) bu dilimde yazılmaz; dilim 9 (SOZLESME 5 §9.5). KaTeX inline style kullandığı için CSP o zaman
  buna göre yazılır.
- `QLAB_API_URL` **derleme anında** okunur (Next `rewrites` derlemeye girer); başka bir API adresi yeni derleme ister. Dilim 9'da
  çalışma anı ayarına çevrilir. `next dev` yalnızca `127.0.0.1`'i dinler.

## 5. Örnek set (görsel regresyon)

`packages/question-renderer/fixtures/`: sentetik, gerçek sınav sorusu değil (CLAUDE.md kural 14), `@qlab/api-client` tipleriyle
yazılmış. TESTING_STRATEGY §9: her blok tipi, uzun formül, geniş tablo, çok parçalı soru, şekilli soru, MCQ. En az:

1. Çoktan seçmeli `single_value` (satır içi matematik ve `quantity` içeren seçenekler)
2. Çoktan seçmeli `two_column_table`
3. Çoktan seçmeli `roman_statements`
4. Çoktan seçmeli `figure_options`
5. Yapılandırılmış soru: `a`, `b.i`, `b.ii`, `c`, `lead_in`, liste, `hard_break`, tüm işaretler
6. Veri temelli soru: geniş tablo (375 px'de kendi içinde kayar), `colspan` / `rowspan`, belirsizlikli `quantity`
7. Uzun `math_block` (375 px'de kendi içinde kayar), matris / `aligned`
8. Markscheme: alternatif grup, iki rota, `accept_range`, her not türü, maddeye bağlı not, `marksCapped`
9. Personel görünümü: aynı yapılandırılmış soru, `showAnswers` açık ve kapalı; şekil tarifi görünür

KaTeX sürümü ve ayarları sunucununkiyle (`apps/api/katex/package.json`, `render.mjs`) bir testle eşit tutulur; KaTeX yükseltmesi
artık dört yeri birlikte değiştirir: `KATEX_VERSION`, `apps/api/katex` paketi ve kilidi, `packages/question-renderer` paketi ve kök kilit.

Örneklerdeki her LaTeX sunucunun kapalı komut listesinden geçer (2026-10-14'te `qlab.content.math.disallowed` ile elle
denetlendi: 27 kaynak, hepsi geçti). **Bilinen sınır:** bu denetim otomatik değil; fikstürler TypeScript, liste Python'da. Örnek set
değişirse elle yinelenir; otomatik hale getirmek dilim 7'nin işi (editör aynı listeyi istemcide de isteyecek).

## 6. Testler

- **Bileşen testleri** (Vitest + Testing Library, jsdom): §3'ün her kuralı; metin düğümünde HTML enjeksiyonu (`<img onerror>`) metin
  kalır; KaTeX ayarları (ör. `\href` reddedilir ve hata işareti gösterilir); öğrenci görünümünde tarif yoktur; erişilebilirlik
  özellikleri (kapsayıcıların `tabindex` ve adları, yer tutucuların `role="img"`). Test yazarı uygulamayı görmeden §3'ten yazar.
- **Görsel regresyon** (Playwright, Chromium): galeri, 1280 px ve 375 px genişlikte, örnek başına ekran görüntüsü. 375 px'de
  `document.documentElement.scrollWidth <= 375`. Ekran görüntüleri işletim sistemine bağlıdır: temel görüntüler ve karşılaştırma,
  Playwright'ın resmi Linux Docker imajında, aynı sürümle alınır (`npm run test:visual`; yerelde Docker ile, CI'da aynı imajla).
- **Bilinen sınır:** Playwright imajındaki varsayılan yazı tipinin kalın biçimi yok; temel görüntülerde kalın metin normal görünür, yani
  görsel regresyon kalınlık hatasını yakalayamaz (bileşen testleri `<strong>` çıktısını denetler). Uygulamanın kendi yazı tipi
  paketlendiğinde (dilim 7–8) düzelir.
- **Tip ve lint:** `tsc --noEmit` (strict), ESLint (Next varsayılanı), `next build`.
- **CI** (kritik alan, sahibinin onayıyla): `web` işi — `npm ci`, istemci denetimi, tip, lint, bileşen testleri, `next build`,
  görsel regresyon.

## 7. Mimar kararları — sahibinin onayını bekliyor

1. **Kökte npm çalışma alanı** (pnpm/yarn değil): Node ile gelir, ek araç yok.
2. **Sürümler:** Next.js 16.4, React 19.3, Tailwind 4.3, Vitest 5, Playwright 1.64 (2026-10-14'te npm'deki son kararlı sürümler;
   kurulumda kilit dosyasıyla sabitlenir).
3. **Birim yazımı dönüştürülmez.** DATA_ARCHITECTURE §3.3 "programın birim yazım kuralı" (IB: `m s⁻¹`) diyor; bunun için birim
   ayrıştırıcısı gerekir ve o formül yorumlayıcısıyla (M3) gelir. O zamana kadar birim yazıldığı gibi gösterilir.
4. **API vekili Next rewrites ile;** API'ye CORS eklenmez.
5. **Yerel giriş token yapıştırarak,** `sessionStorage`'da; production derlemesinde yok.
6. **Görsel regresyon Docker'daki Linux imajında** (`mcr.microsoft.com/playwright:v1.64.0-noble`, `linux/amd64`, CI çalıştırıcısıyla
   aynı); macOS'ta alınan görüntüler kullanılmaz. Apple Silicon'da emülasyonla çalışır, yavaştır (bir koşu ~1 dk).
7. **ESLint 9.39.5** (10 değil): `eslint-config-next` 16.4 eklentileri 9'a bağlı; npm 9'u "desteklenmiyor" olarak işaretliyor.
   Next'in yapılandırması 10'u desteklediğinde yükseltilir.
8. **Gösterim bileşeni istemci bileşenidir** (`"use client"`): KaTeX ve React bağlamı tarayıcıda çalışır. Sunucuda üretilen açık
   sayfalar (M6) için yeniden değerlendirilir.

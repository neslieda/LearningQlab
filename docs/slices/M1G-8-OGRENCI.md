# M1-G dilim 8 — öğrenci ekranı ve cevapların saklanması

> **Durum: TASLAK** (2026-10-16, mimar oturumu). Sahibinin kararları (2026-10-16): (1) açıklamalar cevap gönderildikten sonra görünür,
> (2) **öğrenci cevapları saklanır** (D-66), (3) kapsam: soru listesi, çözme ekranı, cevap sonrası doğru cevap ve açıklama; puanlama
> ve geri bildirim yok. Dilim 9'un (web'e açılış) üstüne kurulur. Dilim birleşirken içeriği kalıcı belgelere işlenir ve bu dosya
> kaldırılır.

## 1. Amaç ve kapsam

Amaç: giriş yapmış bir öğrenci yayınlanmış soruları listeleyip çözsün, cevabını göndersin ve doğru cevabı ile açıklamayı görsün;
cevapları kendisi için saklansın, görebilsin ve silebilsin.

Kapsam:
- Öğrenci ekranları (§4): soru listesi, çözme ekranı, cevap geçmişi, "cevaplarımı sil".
- API: `POST /v1/questions/{id}/answers` (eski `…/check`; artık saklar ve açıklamaları döndürür), `GET /v1/me/responses`,
  `DELETE /v1/me/responses`.
- Migration 0007: `response` tablosu.
- Gizlilik bildirimi (İngilizce kısa metin; sahibin incelemesine ⚖️).

Kapsam dışı: puanlama ve AI geri bildirimi (M4), öğretmenin öğrenci cevaplarını görmesi (M2, kurum kapsamı), deneme sınavı oturumu
(`attempt`, süre, M2), cevap fotoğrafı, çözüm modeli gösterimi, analitik.

Kritik alan: **evet** (öğrenci kişisel verisi, migration, yetki, API sözleşmesi). Sahibin onayı gerekir.

## 2. Veri ve gizlilik (D-66, ⚖️ R-02)

- Saklanan: hesap kimliği (opak), soru sürümü, parça (yazılıda), cevap (seçilen seçenek ya da metin), çoktan seçmelide doğru mu,
  zaman. **Saklanmayan:** ad, e-posta, IP, tarayıcı bilgisi, süre ölçümü. Veritabanımız zaten ad ve e-posta tutmaz; kimlik yalnızca
  giriş sağlayıcısındadır.
- Cevap bir **sürüme** bağlanır (kural 7); yayınlanmış sürüm değişmez, böylece "bu cevap hangi soruya verildi" her zaman bellidir.
- **Hiçbir AI adımına girmez** (kural 10 ve 11); bu dilimde puanlama yok.
- Saklama: hesap boyunca (DATA_ARCHITECTURE §10). Öğrenci `DELETE /v1/me/responses` ile hepsini siler (SECURITY §5.4 hakkının kendi
  kendine kullanımı). Hesap silinince satırlar kaskadla gider. Silme audit'e yalnızca sayıyla yazılır (kişi ve içerik yok).
- Yedeklerdeki kopyalar yedek penceresi dolunca düşer (gecelik yedek 14 gün). ⚖️ Yedekler GitHub'da (ABD) durur; içinde cevaplar ve
  opak hesap kimlikleri vardır, ad ve e-posta yoktur.
- **Öğretmen ve personel, öğrenci cevabını arayüzden göremez** (kurum kapsamı M2'de gelir). Platform sahibi veritabanına doğrudan
  erişebilir; bu, sahibin sorumluluğundadır.
- Ücretsiz deneme altyapısında (D-61) veri işleme sözleşmesi (DPA) kapsamı doğrulanmadı ⚖️; sahibi riski üstlendi (D-66).

## 3. API sözleşmesi (donduruldu)

Hepsi `EVERYONE` (giriş yapmış, rolü olan her hesap); yalnızca kendi verisi.

| Uç nokta | İstek / yanıt |
|---|---|
| `POST /v1/questions/{question_id}/answers` | Gövde: `{kind: "mcq", selected_key}` ya da `{kind: "written", part_id, text}` (dilim 5'teki gibi). Yanıt 201: `McqResult` (`response_id`, `version_id`, `correct`, `correct_key`, `explanation: Doc \| null`, `rationales: [{key, content: Doc}]` — her yanlış seçenek) ya da `WrittenResult` (`response_id`, `version_id`, `part_id`, `marks`, `marks_capped`, `mark_points`, `notes`, `language_warning`). Cevap **saklanır**. Eski `…/check` yolu kalkar |
| `GET /v1/me/responses` | Sorgu: `question_id?`, `cursor?`, `limit` (1–100, 20). Yanıt: `{items: [{id, question_id, version_id, kind, part_id, selected_key \| text, correct \| null, created_at}], next_cursor}`, en yeni önce |
| `DELETE /v1/me/responses` | 200 `{deleted: n}`; çağıranın tüm cevaplarını siler. Audit: `learner.responses_deleted` (hesap, sayı) |

- Eşleşmeyen cevap (mcq cevabı yapılandırılmış soruya, bilinmeyen `part_id`): 422 `answer_does_not_fit` (değişmez).
- Cevap boyutu `MAX_ANSWER_LENGTH`; gövde sınırı 64 KiB (var olan).
- Her gönderim yeni bir satırdır (öğrenci aynı soruyu tekrar çözebilir); bir hesabın bir soruya en çok 200 cevabı olur, fazlası 429
  `too_many_answers` (kötüye kullanım ve depolama sınırı).
- Açıklama (`explanation`) ve gerekçeler (`rationales`) yalnızca cevap gönderildikten sonra, bu yanıtta gelir (dilim 5'in "cevaptan
  önce hiçbir şey" kuralı sürer). Kazanım cümlesi, şekil tarifi ve çözüm modeli **hâlâ** öğrenciye gitmez.
- Tablo `response` (migration 0007): `id` (UUIDv7), `account_id` (FK, ON DELETE CASCADE), `question_version_id` (FK), `part_id` (null:
  çoktan seçmeli), `kind` (`mcq`/`written`), `payload` (JSONB; `{"selected_key"}` ya da `{"text"}`), `correct` (yalnız çoktan seçmelide),
  `created_at`. Kısıtlar: kind ↔ part_id ↔ correct tutarlılığı, payload boyutu. İndeks: `(account_id, created_at DESC, id)`,
  `(account_id, question_version_id)`. Silme koruma tetikleyicisi yok (silme hakkı).
- Modül: `qlab.attempts` (var olan boş modül; `content`'e yalnızca okuma yoluyla bağımlı olabilir, import-linter kontratına bakılır).

## 4. Ekranlar (`apps/web/src/app/learn/…`)

- **`/learn`**: yayınlanmış sorular. Süzgeçler: sınav bölümü, soru sınıfı, düzey (URL'de). Satır: konu, sınıf, bölüm, puan, "Answered"
  rozeti (kendi cevabı varsa). "Load more". Boş ve hata durumları.
- **`/learn/[id]`**: soru sınav düzeninde (`LearnerQuestionView`). Çoktan seçmeli: seçenek seçilir, "Submit answer". Yapılandırılmış:
  her parçada bir metin kutusu ve "Submit answer for (a)". Gönderince: doğru seçenek vurgulanır, açıklama ve yanlış seçeneklerin
  gerekçeleri açılır; yazılıda markscheme maddeleri ve notlar açılır, dil uyarısı varsa gösterilir. Gönderilen cevap kutuda kilitli kalır,
  "Try again" yeni bir deneme açar. Altta bu soruya önceki cevaplarım listesi.
- **`/learn/history`**: tüm cevaplarım (en yeni önce, soruya bağlantı), sayfalama.
- **`/account`**: mevcut sayfaya "My answers" bölümü: sayı, `/learn/history` bağlantısı, **"Delete all my answers"** (onay penceresi,
  geri alınamaz uyarısı).
- **Gizlilik bildirimi** (İngilizce; `/learn` ve `/account` altında kısa bölüm, ayrıntı `/privacy`): ne saklanıyor, kim göremez,
  nasıl silinir. Metin sahibin incelemesine bırakılır ⚖️.
- Ana sayfa ve başlık: giriş yapmış herkes için "Practice" bağlantısı. Rol önemli değil; personel de çözebilir (cevapları saklanır).
- Erişilebilirlik: seçenekler `radiogroup`, odak yönetimi, sonuç `aria-live`, klavye ile tam kullanım; 375 px'te yatay kaydırma yok.
- Hata eşlemesi: `answer_does_not_fit` → "This answer does not fit the question"; `too_many_answers` → "You have reached the limit of
  200 answers for this question"; 401 → giriş bağlantısı; diğerleri 7a'daki gibi.

## 5. Kabul testleri

1. Öğrenci cevabı gönderince cevap tek satır olarak saklanır; satırda ad, e-posta, IP yoktur; cevap sürüme bağlıdır; yayınlanmış
   sürümün sonraki düzeltmesi eski cevabın sürümünü değiştirmez.
2. Cevaptan önce hiçbir yanıtta açıklama, gerekçe, doğru cevap yoktur (dilim 5 testleri sürer); `answers` yanıtı açıklamayı ve gerekçeleri içerir;
   kazanım, şekil tarifi, çözüm modeli içermez.
3. Öğrenci yalnızca kendi cevaplarını görür ve siler; başkasının cevabını göremez (iki hesapla test); personel rolleri de başkasının
   cevabına ulaşamaz.
4. `DELETE /v1/me/responses` yalnızca çağıranın satırlarını siler, sayıyı döndürür, audit yazar (içerik yok); hesap silinince cevaplar
   kaskadla gider.
5. 200 cevap sınırı: 201. cevap 429; sayaç hesap ve soruya özgü.
6. Yetki tablosu: yeni uç noktalar (`EVERYONE`), eski `…/check` yolu 404.
7. Web: liste süzgeçleri, çoktan seçmeli çözüm, yapılandırılmış çözüm, sonuç gösterimi (açıklama, gerekçeler, markscheme), tekrar dene,
   geçmiş, silme onayı, hata mesajları (API taklit edilerek); görsel regresyon etkilenmez.
8. Açıklama ve gerekçeler pilot sorularda doğru görünür (130 sorunun hepsi için gösterim hatasız; galeri örnekleri).

## 6. Mimar kararları (sahibin onayına)

1. `…/check` yolu `…/answers` olur: artık "kontrol" değil, saklayan bir gönderimdir; ad davranışı yansıtsın.
2. `attempt` (oturum) tablosu bu dilimde yok; deneme sınavı oturumu M2'de, `response`'a `attempt_id` eklenerek gelir.
3. Bir soru için 200 cevap sınırı (depolama ve kötüye kullanım).
4. Öğretmenin öğrenci cevaplarını görmesi bu dilimde yok; kurum kapsamıyla (M2) birlikte tasarlanır.
5. Cevaplar saklandığı için gizlilik bildirimi ve silme düğmesi bu dilimin parçasıdır (R-02'yi kapatmaz).

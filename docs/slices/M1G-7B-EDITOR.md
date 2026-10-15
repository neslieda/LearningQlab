# M1-G dilim 7b — yerinde düzenleme (editör)

> **Durum: TASLAK** (2026-10-15, mimar oturumu). Sahibinin kararları (2026-10-15): form + metin kutuları, eşzamanlı düzenlemede
> kaydı reddetme, kapsam "metin + puan maddeleri", editör şeması Pydantic'ten üretilir. 7a'nın ve İngilizce dilimin üstüne kurulur
> (PR #6 birleşince tabanı `main`). Dilim birleşirken içeriği kalıcı belgelere işlenir ve bu dosya kaldırılır.

## 1. Amaç ve kapsam

Amaç: personel (`reviewer`, `content_admin`, `platform_admin`) `draft` ya da `needs_fix` durumundaki bir sürümü tarayıcıda düzeltip
kaydedebilsin (D-55). Yayınlanmış soru düzeltilecekse önce 7a'daki "Open revision" ile yeni sürüm açılır, o düzenlenir.

Kapsam:

- Bütün metin alanları: kök, uyaran açıklaması, parça `lead_in` ve gövdesi, puan maddeleri, notlar, seçenek hücreleri ve ifadeleri,
  çeldirici gerekçeleri, çözüm açıklaması, `outcome`.
- Üst veri: zorluk, hesap makinesi, düzeyler, doğru seçenek, parça puanı (1–3), `marks_capped`, `show_that`, komut sözcüğü (sözlükten),
  cevap türü, ölçme hedefi, madde türü, alternatif grubu ve yolu, not türü ve `ecf_from`.
- Puan maddesi ve not ekleme, silme, sıralama. Toplam puan parça puanlarından hesaplanır (elle girilmez).

Kapsam dışı: parça ekleme/silme, yeni soru oluşturma, uyaran ekleme/silme ve görsel yükleme, çözüm modeli düzenleme (yorumlayıcı M3;
salt okunur gösterilir), `option_kind` / `option_layout` değiştirme (salt okunur), müfredat düğümü değiştirme.

Kritik alan: kısmen. API sözleşmesi değişir (§2); yetki değişmez (`PUT` politikası aynı).

## 2. API sözleşmesi (donduruldu)

- `PUT /v1/admin/question-versions/{version_id}` gövdesi: `{document, expected_content_sha256}`. İkincisi zorunludur: düzenleyicinin
  **başladığı** içeriğin özeti. Saklanan içerik artık o değilse 409 `stale_content`, hiçbir şey değişmez. Durum denetimi önce gelir
  (yayınlanmış sürüme kayıt yine 409 `invalid_transition`).
- Servis düzeyinde (`content.update_draft`) alan isteğe bağlıdır; içe aktarma son sürümün özetini gönderir.
- Diğer hatalar aynı: 422 `invalid_document` (sözlük, matematik, İngilizce kuralı; `detail` içinde yol listesi), 409 `invalid_transition`.

## 3. Editör şeması (D-21)

- `uv run python -m qlab.content.schema.manifest` Pydantic düğüm modellerinden `packages/question-editor/src/manifest.json` üretir;
  `--check` depodaki dosyanın üretilenle aynı olduğunu doğrular. Bir API testi de aynı karşılaştırmayı yapar (CI değişmeden yakalanır).
- Manifest içeriği: düğümler (`name`, `group`: block/inline, `content` ifadesi ProseMirror sözdiziminde, `attrs` ve her birinin türü,
  zorunluluğu, varsayılanı; `atom`; işaret alıp almadığı), işaretler (Pydantic'teki sıra = kanonik sıra) ve birlikte olamayan işaret
  çiftleri. El yazısı tek şey: alan adlarının ekrandaki etiketi.
- Editör (`packages/question-editor`, Tiptap) düğüm ve işaret tanımlarını manifestten kurar; manifestte olmayan düğüm yapıştırılamaz.
- **Gidiş-dönüş kuralı:** bir `doc` editöre yüklenip hiç değiştirilmeden dışa alındığında bayt bayt aynı JSON çıkar. Kabul testi:
  130 pilot sorunun her `doc` alanı.

## 4. Ekran

`/admin/versions/[id]/edit` (istemci bileşeni). Sürüm sayfasında `draft` ve `needs_fix` durumunda personele "Edit" düğmesi görünür;
`needs_fix` panelindeki "Waiting for changes" yerine "Edit to fix" bağlantısı gelir.

- Düzen sınav düzenini izler: üst veri → kök → uyaranlar → (çoktan seçmeli) seçenekler, doğru cevap, gerekçeler, çözüm → (yapılandırılmış)
  parça parça gövde, puan, komut sözcüğü, markscheme maddeleri, notlar → çözüm modeli (salt okunur).
- Metin kutusu araç çubuğu: kalın, italik, alt/üst simge, « » (optional), altı çizili (essential; yalnızca markscheme alanlarında),
  satır içi matematik, blok matematik, tablo (yalnızca izin verilen alanlarda), liste. Matematik düğümü tıklanınca LaTeX alanı ve
  canlı KaTeX önizlemesi açılır (gösterimdeki KaTeX sürümüyle aynı). Büyüklük (`quantity`) düğümü değer/birim/parametre açılır
  penceresiyle düzenlenir. `figure` düğümü taşınabilir ama editörde yeni eklenemez.
- "Preview" sekmesi o anki belgeyi 7a'daki gösterim bileşeniyle sınav düzeninde çizer.
- Kaydet: açık düğme, otomatik kayıt yok. Kaydedilmemiş değişiklik varken sayfadan çıkışta uyarı. İstek sürerken düğme kilitli.
- Kayıttan önce istemci denetimi: Türkçeye özgü harf (`ğ Ğ ı İ ş Ş`) varsa kayıt gönderilmez ve alan gösterilir ("Content must be
  written in English"). Sunucu yine de zorlar.
- Hata eşlemesi: `stale_content` → "Someone else saved this version while you were editing. Your changes are still here; copy what
  you need, then reload." + "Reload (discards your changes)" düğmesi; `invalid_document` → sunucunun döndürdüğü her sorun, yolu
  okunur alan adına çevrilerek, ilgili alanın yanında ve üstte özet listede; `invalid_transition` → "This version can no longer be
  edited" + sürüme bağlantı; 401 → giriş bağlantısı; diğerleri 7a'daki gibi.
- Başarılı kayıttan sonra sorgular geçersiz kılınır, yeni özet sabitlenir, "Saved" duyurulur (`aria-live`). Gönderme (submit) 7a'daki
  panelden yapılır.
- Erişilebilirlik: her alanın görünür etiketi; araç çubuğu düğmelerinin erişilebilir adları; klavyeyle tam kullanım; hata özeti
  odak alır.

## 5. Kabul testleri

1. Manifest üretilenle aynı; manifestteki düğüm ve işaret kümesi Pydantic modelleriyle aynı.
2. Gidiş-dönüş: 130 pilot sorunun bütün `doc` alanları editörden değişmeden çıkar.
3. Bir metni değiştirip kaydetmek, başlanan özetle `PUT` gönderir; yanıt sonrası sayfa yeni özeti sabitler.
4. 409 `stale_content`: kullanıcının değişiklikleri ekranda kalır, uyarı ve yeniden yükleme düğmesi görünür.
5. 422: sorunlar alanlarının yanında ve özette görünür; hiçbir şey kaybolmaz.
6. Türkçe harf içeren metin istek gönderilmeden engellenir.
7. Puan maddesi ekleme/silme/sıralama ve parça puanı değişikliği doğru belgeyi üretir; toplam puan kendiliğinden güncellenir.
8. `published` sürümde "Edit" yoktur; doğrudan `/edit` adresine gidilirse "This version can no longer be edited".
9. Öğrenci rolü düzenleme sayfasını göremez (7a'daki personel kapısı).

## 6. Mimar kararları (sahibin onayına)

1. Servis düzeyinde `expected_content_sha256` isteğe bağlı, API'de zorunlu (içe aktarma ve iç çağrılar için).
2. Manifest bir API testiyle de denetlenir; CI dosyası değişmez.
3. Yeni bağımlılıklar: Tiptap paketleri (en az iki haftalık, sabit sürüm; TECH_STACK'te onaylı).
4. Çözüm modeli, seçenek türü/düzeni ve müfredat düğümü bu dilimde salt okunur.

# CLAUDE.md

> Mimari belgeler 2026-10-11 tarihinde onaylandı. Aktif aşama: **M0** (`docs/ROADMAP.md`).

## Proje

Uluslararası sınavlar için soru bankası, deneme ve AI destekli geri bildirim platformu. İlk kapsam: IB Diploma Physics.
Proje sahibiyle Türkçe konuş; teknik terimler İngilizce kalabilir. Kod, tanımlayıcılar ve commit mesajları İngilizce.

## Önce oku

- Mimari ve kararlar: `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`
- Çalışma yöntemi: `docs/DEVELOPMENT_WORKFLOW.md`
- Dokunduğun alana göre: `DOMAIN_MODEL`, `DATA_ARCHITECTURE`, `AI_PIPELINE`, `API_DESIGN`, `SECURITY`, `TESTING_STRATEGY`, `ROADMAP`

Belge ile kod çelişiyorsa durup bildir; sessizce birini diğerine uydurma.

## Stack

Python + FastAPI + Pydantic (modüler monolith: API + worker) · SQLAlchemy 2 + Alembic · PostgreSQL (JSONB, pgvector, kuyruk) ·
S3-uyumlu storage · Next.js + TypeScript · KaTeX · Tiptap · REST + OpenAPI (istemci üretilir).

## Değişmez kurallar

1. `generation` modülü soru tablolarını ve `content` modülünü import etmez; yalnızca Blueprint alır.
2. Rights fail-closed: geçerli `RightsRecord` yoksa içerik işlenmez ve gösterilmez.
3. `source_original` içerik yalnızca rights kaydı olan kurumun üyelerine döner; açık uç noktalardan asla.
4. Sayısal cevap LLM çıktısından alınmaz; formül zincirinden hesaplanır.
5. Formül yorumlayıcısında `eval`, `exec` ya da ham metne `sympify` yok; yalnızca izinli öğeler.
6. Her matematik düğümü kayıt anında KaTeX ile render edilir; edilemeyen kaydedilmez. MathJax ekleme.
7. Yayınlanmış soru sürümü değişmez; düzeltme yeni sürümdür. Cevaplar sürüme bağlanır.
8. Kritik kontrolü kalan sürüm yayınlanamaz; bunu backend zorlar.
9. Yetki varsayılan rettir; yeni uç nokta rol tablosuna girmeden eklenmez.
10. LLM girdilerinde dış metin (PDF, öğrenci cevabı) veri alanındadır; çıktı şemayla doğrulanır. Agent ve araç kullanan model ekleme.
11. Kaynak içerik gören LLM adımları yalnızca no-retention koşulundaki modellerle çalışır.
12. Tablo, modül ve alan adlarında belirli bir sınav kurumunun adı geçmez; programa özgü kavramlar veridir.
13. Öğrenciye canlı üretilmiş, incelenmemiş içerik gösterilmez (kendi cevabına verilen puanlama geri bildirimi hariç).
14. Sınav kurumlarının belgeleri yalnızca biçim öğrenmek için kullanılır (D-44). Soru metni, sayıları, senaryosu ya da şekli depoya,
    veritabanına, prompt'a, Blueprint'e, test verisine ya da belgelere girmez. Biçim profilleri kendi cümlelerimizle yazılır.
15. Blueprint bir sınav sorusundan türetilmez; müfredat düğümü ve biçim profilinden yazılır (D-45). Orijinal sınav sorusu alma ve
    gösterme yolları kapalıdır (D-46).

## Çalışma biçimi

- Bir oturum, bir dikey dilim, bir pull request. Kabul testi uygulamadan önce yazılır.
- Şema, OpenAPI ve migration'ı ana oturum yazar ve dondurur; alt ajanlar ondan sonra çalışır.
- Kritik alanlar (yetki, rights, yorumlayıcı, migration, ödeme, rıza mantığı, promptlar ve eşikler, CI ve `.claude/`) insan onayı ister.
- Mimari kararı değiştirme; öner ve `docs/DECISIONS.md` için onay iste.
- Temporal, LangGraph, LiteLLM, Z3, Redis, ayrı vector DB, GraphQL, self-hosted model ekleme; gerekçe gördüysen önce sor.
- Doğrulanmamış fiyat, model adı ya da kütüphane özelliğini kesin bilgi gibi yazma; kaynağını ve doğrulama durumunu belirt.
- Hukuki konuları teknik kesinlik gibi sunma; ⚖️ ile işaretle.
- Gizli anahtarlara ve production'a erişme. Test verisinde gerçek kaynak soru kullanma.

## Açık riskler

R-01 (sınav kurumu içeriğinin kullanımı; D-44–D-46 ile daraltıldı) ve R-02 (yaş, rıza, reşit olmayan verisi) hukuki teyit bekliyor.
Ayrıntı: `docs/DECISIONS.md` §4.

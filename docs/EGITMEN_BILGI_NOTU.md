# Eğitmen bilgi notu

> **Durum: TASLAK.** Tarih: 2026-10-13. Kapsam: M1-G dilim 4'ün sonu.
> Okur: fizik eğitmenleri ve incelemeciler. Sistemin neye izin vermediği ayrı belgededir: [SINIRLAR.md](SINIRLAR.md).
> Bu not üç şeyi anlatır: sizden hangi doğrulamalar bekleniyor, bir soru hangi adımlardan geçiyor, soru yazarken ve incelerken
> nelere dikkat edilmeli. Arayüz henüz yok (dilim 6–8); §1'deki doğrulamalar belgeler üzerinden şimdi yapılabilir.

## 1. Sizden beklenen doğrulamalar

Aşağıdakilerin hepsi taslaktır ve sistem bunlara dayanarak çalışıyor. Yanlışsa üzerine kurulan her şey yanlış olur.

| # | Ne doğrulanacak | Nerede | Neden önemli |
|---|---|---|---|
| 1 | Konu düğümleri (A.1–E.5), her düğümün SL / ek HL / yalnız HL ayrımı, "ölçülen çekirdek" ve "kapsam dışı" sütunları | [müfredat analizi](syllabus/dp-physics-2025-analysis.md) §6, §8 | Her soru bir düğüme bağlanır; düzey etiketi buradan gelir |
| 2 | Sabitler tablosu: değerler ve anlamlı basamak, veri kitapçığının güncel sürümüyle aynı mı | [sabitler](syllabus/dp-physics-2025-constants.md) | Sorularda ve çözümlerde bu değerler kullanılır |
| 3 | Komut sözcüğü listesi (18 sözcük) ve her sözcüğün beklediği cevap türü | [müfredat analizi](syllabus/dp-physics-2025-analysis.md) §2–§3 | Listede olmayan sözcükle soru kaydedilemez |
| 4 | Biçim profili: soru yapısı, puan dağılımı, markscheme gösterimleri | [biçim profili](formats/dp-physics-2025-format-profile.md) §7 | Soruların "sınav gibi" görünmesinin ölçütü |
| 5 | SL Paper 2 toplam puanı: örnek kâğıtta 50, ders rehberinde 55. Hangisi geçerli? | biçim profili §7 | Deneme sınavı yapısı buna bağlı |
| 6 | Paper 1A'da iki sütunlu tablo biçiminde seçenek kullanılıyor mu? Paper 1B, SL ve HL'de aynı mı? | biçim profili §7 | Soru türlerinin kapsamı |
| 7 | 130 pilot soru: fizik doğruluğu, tek doğru cevap, müfredat sınırı, düzey | [pilot sorular](pilot/) ve [inceleme raporları](pilot/review/) | Hiçbiri henüz insan onayından geçmedi |
| 8 | Pilot Paper 2 sorularının çoğu 9 puan ve SL etiketli; SL kısa soru aralığı 4–6. Bölünsün mü, yalnız HL mi sayılsın? | müfredat analizi §2.1 | İçe aktarmadan önce karar gerekir |
| 9 | Matematik komut listesi: fizik sorularında gereken ama listede olmayan gösterim var mı? | [SINIRLAR.md](SINIRLAR.md) §5 | Listede olmayan komutla soru kaydedilemez |

| 10 | "Comment" komut sözcüğü pilot sorularda kullanılıyor (üç parça) ama komut sözcüğü listesinde yok. Listeye eklensin mi, yoksa bu parçalar başka sözcükle mi yazılsın? | müfredat analizi §2; `a1` soru 5 (d), `b3` soru 6 (f), `d3` soru 6 (d) | Listede olmayan sözcük sisteme "boş" olarak girdi |

Yanıtlarınızı düğüm ya da soru numarasıyla, kısa notlar halinde iletmeniz yeterli.

## 2. Bir sorunun yolu

| Durum | Anlamı | Kim ne yapar |
|---|---|---|
| Taslak | Yazılıyor ya da düzeltiliyor | Yazar düzenler, hazır olunca incelemeye gönderir |
| Otomatik kontrol | Sistem yapıyı, müfredat sözlüğünü ve matematik gösterimini denetler | Kendiliğinden; saniyeler sürer |
| Düzeltme bekliyor | Otomatik kontrol kaldı ya da incelemeci geri gönderdi | Yazar düzeltir; soru yeniden taslak olur |
| İncelemede | Eğitmen incelemesini bekliyor; düzenlenemez | İncelemeci onaylar, geri gönderir ya da reddeder |
| Onaylandı | Yayına hazır; düzenlenemez | Yayınlanır ya da (hata bulunursa) geri gönderilir |
| Yayında | Öğrenciye açık; hiç değişmez | Gerekirse geri çekilir; düzeltme yeni sürümdür |
| Geri çekildi | Öğrenciye kapalı; kayıtta durur | Yeni sürüm açılır ya da gerekçeyle yeniden yayınlanır |
| Reddedildi | Kullanılmayacak; kayıtta durur | — |

Şekilli sorular "Onaylandı" durumuna kadar gelebilir ama yayınlanamaz ([SINIRLAR.md](SINIRLAR.md) §2).

## 3. İncelerken bakılacaklar

Sistem bugün fizik doğruluğunu denetlemiyor; **bu sizin incelemenize dayanıyor** ([SINIRLAR.md](SINIRLAR.md) §3).

1. **Doğruluk.** Cevap ve markscheme fizik olarak doğru mu? Sayısal cevabı kendiniz yeniden hesaplayın; çözüm modelindeki adımlar
   cevaba gerçekten götürüyor mu?
2. **Tek doğru cevap.** Çoktan seçmelide ikinci bir savunulabilir seçenek var mı? Gerekli varsayımlar soruda yazıyor mu?
3. **Çeldiriciler.** Her yanlış seçenek gerçek bir kavram yanılgısına ya da tipik hataya dayanıyor mu?
4. **Müfredat.** Soru bağlandığı düğümün içinde mi; "kapsam dışı" maddelerinden birine giriyor mu? "Nitel" denen yerde hesap soruyor mu?
5. **Düzey.** SL etiketli soru ek HL içeriği gerektiriyor mu?
6. **Komut sözcüğü ve puan.** Sözcük istenen cevaba uyuyor mu; puan, beklenen adım sayısıyla orantılı mı?
7. **Birim ve anlamlı basamak.** Veriler tutarlı mı; cevap verilerin anlamlı basamağıyla mı?
8. **Özgünlük.** Soru bildiğiniz bir sınav sorusuna, ders kitabı sorusuna ya da yaygın bir internet sorusuna benziyor mu? Benziyorsa
   reddedin ve gerekçede "bilinen bir soruya benziyor" yazın (sorunun kendisini yazmayın).
9. **Dil.** Kısa, yalın, tek anlamlı mı; bağlam önce, istenen en sonda mı?

Ayrıntılı ölçütler: [pilot soru yazım standardı](pilot/AUTHORING_STANDARD.md).

## 4. Yazarken ve düzeltirken

- **Kaynak kuralı.** Girdi yalnızca müfredat analizi, biçim profili ve genel fizik bilgisidir. Sınav kâğıdından, markscheme'den, ders
  kitabından ya da internetten soru, sayı ya da senaryo alınmaz; bilinen bir sorunun sayılarını değiştirmek de yasaktır (D-44).
  ⚖️ Bu, hukuki riskin başlıca önlemidir.
- **Matematik** LaTeX ile ve yalnızca standart klavye karakterleriyle yazılır: `\times`, `\mu`, `\Omega`, `\degree`, `\le`
  ([SINIRLAR.md](SINIRLAR.md) §5). Hatalı LaTeX içeren soru kaydedilmez.
- **Birimli değerler** ayrı "büyüklük" öğesi olarak girilir (değer + birim). Değer yazıldığı gibi saklanır: `20` ile `20.0` farklıdır,
  anlamlı basamak buradan okunur.
- **Sabitler** soruya gömülmez; sabitler tablosundaki değerler kullanılır. Tabloda olmayan bir sabit gerekiyorsa soruda verilir.
- **Şekil gereken soru** yazılabilir: şekil metinle tarif edilir. Soru incelenir ama görsel hazır olana kadar yayınlanmaz.
- **Çoktan seçmelide** her yanlış seçeneğin dayandığı yanılgı yazılmak zorundadır; yazılmazsa soru kaydedilmez.

## 4.1 İçe aktarılan pilot sorularda önce bakılacaklar

130 pilot soru sisteme otomatik bir betikle çevrildi. Metin kaynağıyla aynıdır, ama aşağıdaki alanlar **tahminle dolduruldu** ve
incelemede ilk düzeltilecek yerlerdir ([SINIRLAR.md](SINIRLAR.md) §7.1; soru bazında liste: `content/pilot/CONVERSION_REPORT.md`):

1. **Seçenek türü** (çoktan seçmeli), **komut sözcüğü** ve **cevap türü** (her parça), **şekil türü**. Yanlışsa düzeltin; boş komut
   sözcüğünü doldurun.
2. **Alternatifler.** Markscheme'de `OR` ile ayrılmış alternatifler sistemde düz metindir. Alternatiflerin ayrı ayrı işaretlenmesi
   gerekiyorsa maddeyi bölüp alternatif grubu verin.
3. **Notlar sütunundaki alternatif yollar** (beş soru: `b1`, `b3`, `b5`, `d2`, `d4` setlerinin 5. soruları) düz not olarak geldi;
   gerçek bir çözüm yoluysa markscheme'e yol olarak taşıyın.
4. **Değişkenler.** Notlarda ve çözüm açıklamalarında değişkenler düz harf olarak görünebilir; `θ₀`, `t′` gibi yazımlarda alt simge
   matematiğin dışındadır. Gösterim önemliyse matematik olarak yeniden yazın.
5. **Çözüm modeli** sorunun yarısından azında var ve hiçbiri hesaplanarak doğrulanmadı; sayısal cevabı kendiniz hesaplayın.
6. **Yazar notları sistemde yok.** Bazı sorularda markscheme'in ardından yazılmış gerekçeler (ör. yön gerekçesi, bilerek verilmiş
   fazladan veri, çeldirici yolların neden anahtara düşmediği) yalnızca Markdown dosyasındadır: `a5` soru 5, `c1` soru 6, `c3` soru 6,
   `d2` soru 4, `d4` soru 5. İncelerken kaynak dosyaya da bakın.
7. **Şekil tarifleri personel içindir.** Veri temelli sorulardaki "Şekil notu" cevabı içerebildiği için sisteme alınmadı.
8. **Türkçe açıklamalar.** Çözüm ve çeldirici gerekçeleri Türkçedir; öğrenciye açılmadan önce İngilizceye çevrilmeleri gerekir.

Bir soruyu sistemde düzelttikten sonra doğru olan sistemdeki halidir; kaynak Markdown güncellenmez ve yeniden içe aktarma
düzeltmenizi ezmez.

## 5. Gerekçe yazarken

Geri gönderme, ret, geri çekme ve yeniden yayınlama gerekçeleri **silinemeyen** bir kayda yazılır.

- İçeriği anlatın: "b.ii'de birim hatalı", "çeldirici C de doğru sayılabilir".
- Kişi adı, öğrenci bilgisi ya da başka kişisel veri **yazmayın**.
- Soru metnini ya da bir sınav sorusunu gerekçeye **kopyalamayın**.
- En çok 500 karakter.

## 6. Bilmeniz gereken diğer noktalar

- **Onay içeriğe bağlıdır.** Siz bakarken soru değiştiyse onayınız reddedilir; yeniden bakmanız istenir. Bu bir hata değil, korumadır.
- **Şimdilik tek onay yeterli** ve yazan kişi kendi sorusunu onaylayabiliyor (D-53, geçici). Uzun açıklamalı sorularda iki inceleme
  kuralı ileride gelecek; o zamana kadar bu soruları ikinci bir eğitmenin de görmesi önerilir.
- **Yapılan her işlem kayda geçer** (kim, ne zaman, hangi içerikle). Kayıtta adınız değil hesap kimliğiniz durur.
- **Sorular yapay zekâ yardımıyla yazıldı.** Akıcı ve ikna edici görünmeleri doğru oldukları anlamına gelmez; özellikle sayısal
  cevapları ve çeldiricilerin gerekçelerini kendiniz sınayın.

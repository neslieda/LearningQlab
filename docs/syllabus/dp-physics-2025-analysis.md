# Müfredat analizi: IB Diploma Physics (ilk sınav 2025)

> **Durum: TASLAK — fizik uzmanlarının doğrulamasını bekliyor.** Tarih: 2026-10-11.
> Kaynak: proje sahibinin sağladığı resmi ders rehberi (Şubat 2023 baskısı). Bu belge rehberin kopyası değildir; soru üretimini
> yönlendirmek için kendi cümlelerimizle yazılmış bir kapsam haritasıdır. Rehber metni depoya alınmaz.
> ⚖️ Rehberin künyesi, üçüncü tarafların ticari kullanımının yazılı lisans gerektirdiğini belirtiyor ([DECISIONS.md](../DECISIONS.md) R-01).

## 1. Bu belge ne için

Üretilen her soru şu dört soruya cevap verebilmelidir; cevaplar bu belgeden gelir:

1. Hangi konu düğümünü ölçüyor (ör. `A.1`) ve o düğüm SL mi, yalnızca HL mi?
2. Hangi ölçme hedefini (AO1–AO3) ve hangi komut sözcüğünü kullanıyor?
3. Konunun açıkça belirtilen sınırlarının içinde mi (§6'daki "kapsam dışı" sütunu)?
4. Gereken matematik, §4'teki listede mi?

## 2. Ölçme hedefleri ve sınav yapısı

| Hedef | Öz | Komut sözcükleri |
|---|---|---|
| AO1 | Bilgiyi gösterme | Draw, State |
| AO2 | Anlama ve uygulama | Annotate, Calculate, Describe, Estimate, Outline |
| AO3 | Analiz, değerlendirme, sentez (deney yöntemi, veri, eğilim ve öngörü) | Analyse, Determine, Discuss, Explain, Predict, Show, Sketch, Suggest |
| AO4 | Araştırma becerileri | Yalnızca iç değerlendirme; yazılı sınavda yok |

Paper 1 ve Paper 2'nin her birinde ağırlık yaklaşık yarı yarıya: AO1+AO2 ile AO3. Yani soru havuzunun yaklaşık yarısı analiz
düzeyinde olmalı; yalnızca hesap sorusu üretmek kapsamı karşılamaz.

| Bölüm | SL | HL | İçerik |
|---|---|---|---|
| Paper 1A | 25 puan | 40 puan | Çoktan seçmeli; yanlış cevap puan düşürmez |
| Paper 1B | 20 puan | 20 puan | Veri temelli sorular |
| Paper 1 toplam | 45 puan, 1 sa 30 dk | 60 puan, 2 sa | 1A ve 1B aralıksız birlikte |
| Paper 2 | 55 puan, 1 sa 30 dk | 90 puan, 2 sa 30 dk | Kısa cevaplı ve uzun cevaplı |

- SL kâğıtları yalnızca SL içeriğini; HL kâğıtları SL + ek HL içeriğini ölçer.
- Tüm kâğıtlarda hesap makinesi ve veri kitapçığı kullanılır. Sonuç: formül ezberi ölçülmez; formülü seçme, yorumlama ve uygulama ölçülür.
- Bilimin doğası temaları soruya bağlam olabilir; tanım ezberi sorulmaz.

## 3. Komut sözcüğü → beklenen cevap türü

| Sözcük | Beklenen | Şemadaki cevap türü |
|---|---|---|
| State | Açıklamasız kısa cevap | `short_text` / `numeric` |
| Calculate | Adımları gösterilen sayısal sonuç | `numeric` |
| Determine | Tek olası sonuç; genelde birden çok adım | `numeric` |
| Show | Verilen sonuca giden adımlar | `extended` (yöntem puanları) |
| Estimate | Yaklaşık değer | `numeric`, geniş tolerans |
| Outline / Describe | Kısa ya da ayrıntılı anlatım | `short_text` |
| Explain | Nedenleriyle anlatım | `short_text` / `extended` |
| Discuss | Dengeli, kanıta dayalı değerlendirme | `extended` |
| Predict / Suggest | Beklenen sonuç ya da olası açıklama | `short_text` |
| Draw / Sketch / Annotate | Çizim ya da grafik | `drawing` |
| Analyse | Öğelerine ayırma | `extended` |

## 4. Matematik ve veri becerileri (her temada geçerli)

**Kullanılabilir:** temel cebir ve aritmetik; kesir, yüzde, oran, üs; trigonometrik oranlar; logaritma ve üstel fonksiyonlar; değişim
oranı; bilimsel gösterim; denklem seçme ve düzenleme; cebirsel türetme; yaklaşıklık ve büyüklük mertebesi; doğru ve ters orantı;
yüzde değişim, yüzde hata.

**Vektörler:** skaler/vektör ayrımı; aynı düzlemde en çok üç vektörün toplanması; iki dik bileşene ayırma; serbest cisim diyagramı.

**Birimler:** SI ve önekler; türetilmiş birimi temel birimlerle ifade; eV, ışık yılı, parsek gibi birimler; birim tutarlılığı kontrolü
(biçimsel boyut analizi sorulmaz); uygun anlamlı basamak.

**Belirsizlik:** ± ile gösterim; mutlak, kesirli ve yüzde belirsizlik; toplama, çıkarma, çarpma, bölme ve üs almada yayılım.

**Grafik:** eksenleri ölçeksiz taslak grafik; ölçekli grafik çizme; logaritmik ölçek; en uygun doğru ya da eğri; belirsizlik çubukları;
en büyük ve en küçük eğimli doğrular; eğim ve kesim noktasının belirsizliği; doğrusallaştırma; eğim, kesim noktası, grafik altındaki alan,
uç değerlerin yorumu; iç ve dış değerleme.

**Deney tasarımı ve değerlendirme (Paper 1B'nin özü):** bağımlı, bağımsız ve kontrol değişkenleri; ölçüm aralığı ve sayısının
gerekçesi; rastgele ve sistematik hata kaynakları ve etkileri; doğruluk, kesinlik, güvenilirlik, geçerlilik; aykırı değerin dahil
edilmesi ya da çıkarılması (matematiksel işlem gerekmez); belirsizliğin sonuca etkisi; gerçekçi iyileştirme önerisi.

**Kapsam dışı matematik:** türev ve integral hesabı, karmaşık sayılar, eşzamanlı denklem gerektiren çarpışma çözümleri.

## 5. İçerik haritası

Saatler önerilen öğretim süresidir ve soru havuzundaki ağırlık için kaba ölçüdür.

| Tema | SL saat | HL saat |
|---|---|---|
| A. Uzay, zaman ve hareket | 27 | 42 |
| B. Maddenin tanecikli yapısı | 24 | 32 |
| C. Dalga davranışı | 17 | 29 |
| D. Alanlar | 19 | 38 |
| E. Nükleer ve kuantum fiziği | 23 | 39 |

## 6. Konu düğümleri

Sütunlar — **Düzey:** SL = SL ve HL ortak; +HL = ortak içerik + ek HL; HL = yalnızca HL. **Kapsam dışı / sınır:** rehberin açıkça
koyduğu sınırlar; soru bunların dışına çıkamaz.

### A. Uzay, zaman ve hareket

| Düğüm | Düzey (saat) | Ölçülen çekirdek | Kapsam dışı / sınır |
|---|---|---|---|
| A.1 Kinematik | SL (9) | Konum, yer değiştirme, hız, ivme; yol–yer değiştirme farkı; anlık ve ortalama değerler; sabit ivmeli hareket denklemleri; değişken ivmeli hareketin grafikle yorumu; eğik atışın bileşenlerle çözümü; akışkan direncinin nitel etkisi (uçuş süresi, yörünge, hız, ivme, menzil, limit hız) | Dirençli eğik atışta hesap yok; yörünge denklemi istenmez; yalnızca yüzeye yakın sabit g; yatay, yukarı açılı ve aşağı açılı fırlatma bilinmeli |
| A.2 Kuvvet ve momentum | SL (10) | Newton yasaları; serbest cisim diyagramı ve bileşke; normal kuvvet, statik ve kinetik sürtünme, gerilme, Hooke yasası, Stokes sürüklemesi, kaldırma kuvveti; momentum, itme, F = Δp/Δt; esnek ve esnek olmayan çarpışma, patlama ve enerji; düzgün ve düzgün olmayan çembersel hareket, merkezcil ivme ve kuvvet, açısal hız | Diyagram ve bileşke yalnızca 1 ve 2 boyutta; çarpışmada momentum ve enerjinin eşzamanlı denklemleri istenmez; nicel çarpışma SL'de 1 boyut, HL'de 2 boyut; düşey çemberde yalnızca en üst ve en alt nokta; eğimli viraj hesabı yok |
| A.3 İş, enerji, güç | SL (8) | Enerjinin korunumu; iş = Fs cos θ; iş–enerji ilişkisi; kinetik, yerçekimi ve esneklik potansiyel enerjisi; mekanik enerjinin korunumu ve korunumsuz kuvvetin işi; güç = Fv; verim; Sankey diyagramı; yakıtların enerji yoğunluğu | Yerçekimi potansiyeli burada yalnızca yüzeye yakın (mgΔh) |
| A.4 Katı cisim mekaniği | HL (7) | Tork; dönme dengesi; açısal yer değiştirme, hız, ivme ve sabit açısal ivme denklemleri; eylemsizlik momenti (nokta kütleler için Σmr²); τ = Iα; açısal momentum ve korunumu; açısal itme; dönme kinetik enerjisi | Vektörel işlem yok, yalnızca dönme yönü; kütle merkezi hesabı yok; belirli şekillerin I formülü soruda verilir; dönme + öteleme yalnızca kaymadan yuvarlanma |
| A.5 Galileo ve özel görelilik | HL (8) | Referans çerçeveleri; Galileo dönüşümü ve hız toplama; iki postüla; Lorentz dönüşümleri, γ; göreli hız toplama; uzay-zaman aralığının değişmezliği; öz zaman ve öz uzunluk; zaman genişlemesi, boy kısalması; eşzamanlılığın göreliliği; uzay-zaman diyagramları (tan θ = v/c); müon kanıtı | Dönüşüm ve formül türetimleri yok; zaman ekseni ct; dünya çizgileri yalnızca sabit hız |

### B. Maddenin tanecikli yapısı

| Düğüm | Düzey (saat) | Ölçülen çekirdek | Kapsam dışı / sınır |
|---|---|---|---|
| B.1 Isıl enerji aktarımı | SL (6) | Molekül modeli; yoğunluk; Kelvin ve Celsius; sıcaklık ve ortalama kinetik enerji; iç enerji; hâl değişimi; Q = mcΔT, Q = mL; iletim (nicel), konveksiyon (nitel), ışınım; Stefan-Boltzmann, ışınım gücü, görünür parlaklık; Wien yasası | Konveksiyon yalnızca nitel |
| B.2 Sera etkisi | SL (6) | Yayıcılık; albedo; güneş sabiti ve S/4 ortalaması; başlıca sera gazları ve kaynakları; kızılötesi soğurma ve yeniden yayma (molekül enerji düzeyleri, rezonans modeli); artmış sera etkisi; denge sıcaklığı için enerji dengesi | Enerji dengesi problemleri yüzey–atmosfer alışverişini içerebilir |
| B.3 Gaz yasaları | SL (6) | Basınç; mol ve Avogadro sabiti; ideal gaz modeli ve kinetik kuram; PV = nRT = NkT; P = ⅓ρv²; tek atomlu ideal gazın iç enerjisi; ideal gaz yaklaşımının geçerlilik koşulları; P–V diyagramı | Yalnızca sabit hacim, sabit sıcaklık, sabit basınç ve ideal gaz yasası |
| B.4 Termodinamik | HL (8) | Birinci yasa (Q = ΔU + W); W = PΔV; entropi (ΔS = ΔQ/T ve S = k ln Ω); ikinci yasa (Clausius, Kelvin ve entropi biçimleri); tersinmezlik; izokorik, izobarik, izotermal, adyabatik süreçler; PV^(5/3) = sabit; ısı makinesi çevrimleri ve verim; Carnot sınırı | İşaret kuralı: Q sisteme verilen, W sistemin yaptığı iş; nicel problemler yalnızca tek atomlu ideal gaz; mikrodurumlar basit sayma modeliyle |
| B.5 Akım ve devreler | SL (6) | Emk kaynağı olarak kimyasal ve güneş pilleri; devre şemaları; akım, potansiyel farkı; direnç, özdirenç; Ohm yasası, ohmik ve ohmik olmayan davranış; güç; seri ve paralel bağlama; iç direnç; değişken dirençler | Alternatif akım devreleri yok; aksi belirtilmedikçe ölçü aletleri ideal; değişken direnç yalnızca termistör, LDR, potansiyometre |

### C. Dalga davranışı

| Düğüm | Düzey (saat) | Ölçülen çekirdek | Kapsam dışı / sınır |
|---|---|---|---|
| C.1 Basit harmonik hareket | +HL (3+4) | BHH koşulları, a = −ω²x; periyot, frekans, açısal frekans, genlik; kütle–yay ve basit sarkaç periyodu; enerji değişiminin nitel anlatımı. **HL:** faz açısı; x, v denklemleri; v = ±ω√(x₀²−x²); toplam ve potansiyel enerji | Enerjinin nicel işlenmesi yalnızca HL; faz açısı radyan |
| C.2 Dalga modeli | SL (3) | Enine ve boyuna ilerleyen dalgalar; v = fλ; ses ve elektromanyetik dalgaların doğası; mekanik–elektromanyetik farkı; ortam parçacıklarının hareketi (konuma ve zamana göre yer değiştirme) | Elektromanyetik spektrumun mertebeleri veri kitapçığından |
| C.3 Dalga olayları | +HL (5+6) | Dalga cephesi ve ışın; yansıma, kırılma, iletim; kırınım; Snell yasası, kritik açı, tam yansıma; üst üste binme; eşfazlı kaynaklar; yapıcı ve yıkıcı girişim koşulları; çift yarık (s = λD/d). **HL:** tek yarık kırınımı (θ = λ/b) ve şiddet deseni; tek yarığın çift yarık desenini biçimlendirmesi; çoklu yarık ve kırınım ağı | Yalnızca dik geliş; tek yarık yalnızca tek renkli ışık ve dikdörtgen yarık; yarık genişliğinin şiddete etkisi nitel |
| C.4 Duran dalgalar ve rezonans | SL (4) | Duran dalganın oluşumu; düğüm ve karın noktaları, genlik ve faz; tel ve borularda desenler; n. harmoniğin dalga boyu ve frekansı; rezonans, doğal frekans; sönümün genliğe ve rezonans frekansına etkisi; hafif, kritik, ağır sönüm | İkiden fazla dalganın üst üste binmesi yok; açık boruda uç düzeltmesi yok; havada basınç düğümleri yok (yalnızca yer değiştirme); "temel ton / üst ton" terimleri kullanılmaz, "birinci harmonik" denir; sönümün frekans tepkisine etkisi nitel |
| C.5 Doppler etkisi | +HL (2+2) | Ses ve elektromanyetik dalgalarda Doppler; dalga cephesi diyagramları; ışık için Δf/f = Δλ/λ ≈ v/c; tayf çizgisi kaymaları. **HL:** ses için hareketli kaynak ve hareketli gözlemci formülleri | Kaynak ve gözlemcinin ikisi birden hareket etmez |

### D. Alanlar

| Düğüm | Düzey (saat) | Ölçülen çekirdek | Kapsam dışı / sınır |
|---|---|---|---|
| D.1 Kütle çekim alanları | +HL (5+7) | Kepler yasaları; evrensel çekim yasası; nokta kütle yaklaşımı; alan şiddeti; alan çizgileri. **HL:** potansiyel enerji ve potansiyel (sonsuzda sıfır); alan şiddeti = potansiyel gradyanı; W = mΔV; eşpotansiyel yüzeyler; kaçış ve yörünge hızı; atmosfer sürüklemesinin yörüngeye nitel etkisi | Yörüngeler çembersel; bileşke alan yalnızca iki cismi birleştiren doğru üzerinde |
| D.2 Elektrik ve manyetik alanlar | +HL (8+6) | Yük türleri ve kuvvet yönü; Coulomb yasası; yükün korunumu; Millikan deneyi; sürtünme, etkiyle ve dokunmayla yüklenme, topraklama; alan şiddeti; alan çizgileri ve yoğunluk; paralel levhalar (E = V/d); manyetik alan çizgileri. **HL:** elektrik potansiyel enerjisi ve potansiyeli; E = −ΔV/Δr; W = qΔV; eşpotansiyel yüzeyler | Manyetik alan desenleri: çubuk mıknatıs, düz tel, çembersel halka, hava çekirdekli solenoid; eşpotansiyeller en çok dört nokta yük için |
| D.3 Elektromanyetik alanlarda hareket | SL (6) | Yüklü parçacığın düzgün elektrik alanda, düzgün manyetik alanda ve birbirine dik alanlarda hareketi; F = qvB sin θ; F = BIL sin θ; paralel teller arası kuvvet; yük/kütle oranının belirlenmesi | — |
| D.4 İndüksiyon | HL (6) | Manyetik akı; Faraday yasası; hareketli iletkende ε = BvL; Lenz yasası ve enerji korunumu; dönen bobinde sinüzoidal emk; dönme frekansının etkisi | Nicel işlem: alana dik hareket eden düz iletken ve alana girip çıkan ya da dönen dikdörtgen bobin; öz indüksiyon nitel; indüktans ve RL devreleri yok |

### E. Nükleer ve kuantum fiziği

| Düğüm | Düzey (saat) | Ölçülen çekirdek | Kapsam dışı / sınır |
|---|---|---|---|
| E.1 Atomun yapısı | +HL (6+3) | Geiger–Marsden–Rutherford deneyi; çekirdek gösterimi; yayma ve soğurma tayfları, kesikli enerji düzeyleri; E = hf; tayftan bileşim. **HL:** R = R₀A^(1/3) ve çekirdek yoğunluğu; yüksek enerjide Rutherford saçılmasından sapma; en yakın yaklaşma uzaklığı; Bohr modeli (E = −13,6/n² eV, açısal momentum kuantumlanması) | Kimyasal semboller ezberlenmez; SL'de deney yalnızca nitel; saçılmada yalnızca elektriksel itme |
| E.2 Kuantum fiziği | HL (8) | Fotoelektrik olay, eşik frekansı, iş fonksiyonu; parçacık kırınımı; dalga–parçacık ikiliği; de Broglie dalga boyu; Compton saçılması ve dalga boyu kayması | Compton formülünün türetimi yok |
| E.3 Radyoaktif bozunma | +HL (7+5) | İzotoplar; bağlanma enerjisi ve kütle açığı; nükleon başına bağlanma enerjisi eğrisi; E = mc²; güçlü çekirdek kuvveti; bozunmanın rastgele ve kendiliğinden doğası; α, β⁻, β⁺, γ denklemleri; nötrino; giricilik ve iyonlaştırma; aktiflik, sayım hızı, yarı ömür; arka plan ışınımı. **HL:** nötron/proton oranı ve kararlılık; kesikli çekirdek enerji düzeyleri; sürekli β tayfı; N = N₀e^(−λt); A = λN; T½ = ln 2/λ | SL'de yalnızca tam sayı yarı ömür; keyfi zaman aralıkları yalnızca HL; zayıf çekirdek kuvveti kapsamda değil |
| E.4 Fisyon | SL (4) | Kendiliğinden ve nötronla uyarılmış fisyon; zincirleme tepkime; kontrol çubukları, yavaşlatıcı, ısı değiştirici, zırhlama; fisyon ürünleri ve yönetimi; açığa çıkan enerjinin hesabı | — |
| E.5 Füzyon ve yıldızlar | SL (6) | Yıldız dengesi (ışınım basıncı ve kütle çekimi); füzyon koşulları; kütlenin yıldız evrimine etkisi; HR diyagramının bölgeleri; ıraklık açısıyla uzaklık; yıldız yarıçapının belirlenmesi; AU, ışık yılı, parsek dönüşümleri | Sefe değişenleri yok; HR diyagramında düşey eksen ışınım gücü, yatay eksen sıcaklık |

## 7. Soru üretimine yansıyan kurallar

1. **Düzey etiketi zorunlu.** Yalnızca HL düğümlerinden (A.4, A.5, B.4, D.4, E.2) ya da "+HL" düğümlerinin ek kısmından gelen soru SL
   havuzuna girmez.
2. **Kapsam sınırı bir kontroldür.** Her düğümün "kapsam dışı" maddeleri Blueprint'te `context_constraints` olarak taşınır; eleştirmen
   adımı bunları tek tek denetler.
3. **Formül ezberi ölçülmez.** Veri kitapçığında olan bir ilişkiyi yalnızca yerine koymaktan ibaret soru AO1/AO2'de kalır; AO3 için
   seçme, birleştirme, yorumlama ya da değerlendirme gerekir.
4. **Nitel–nicel ayrımına uyulur.** Rehberin "nitel" dediği yerde (dirençli hareket, konveksiyon, sönüm, öz indüksiyon) hesap sorulmaz.
5. **Terminoloji.** "Birinci harmonik", "akışkan direnci", "öz zaman" gibi rehberin kullandığı terimler kullanılır; kaçınılması
   istenenler kullanılmaz.
6. **Veri temelli sorular** §4'teki belirsizlik ve grafik becerilerini ölçer; fizik içeriği herhangi bir düğümden gelebilir.
7. **Havuz dengesi.** Düğüm başına soru sayısı kabaca öğretim saatiyle orantılı; her düğümde AO1+AO2 ve AO3 yaklaşık eşit.

## 8. Uzmanların doğrulaması gerekenler

- Bu belge rehberin tek bir okumasına dayanıyor; her düğümün "ölçülen çekirdek" ve "kapsam dışı" sütunları fizik uzmanınca gözden
  geçirilmeli.
- Veri kitapçığındaki sabit değerleri (ör. g) bu belgeye alınmadı; soru üretiminde kullanılacak sabit tablosu kitapçıktan girilmeli.
- Paper 1B ve Paper 2'de soru başına tipik puan aralıkları rehberde yok; uzman bilgisinden gelmeli.

# Sabitler ve veri kitapçığı: IB Diploma Physics (ilk sınav 2025)

> **Durum: TASLAK — fizik uzmanlarının doğrulamasını bekliyor.** Tarih: 2026-10-11.
> Kaynak: proje sahibinin sağladığı veri kitapçığı (sürüm 1.0, Şubat 2023). Bu belge kitapçığın kopyası değildir: sabitlerin değerlerini
> (olgusal veri) ve kitapçığın soru yazımına etkisini kendi cümlelerimizle özetler. Kitapçık metni ve formül sayfaları depoya alınmaz.
> ⚖️ Kitapçığın künyesi, üçüncü tarafların ticari kullanımının yazılı lisans gerektirdiğini belirtiyor ([DECISIONS.md](../DECISIONS.md) R-01).
> Makinece okunur sürüm: [`content/reference/dp-physics-2025-constants.json`](../../content/reference/dp-physics-2025-constants.json).

## 1. Öğrencinin elinde ne var

Kitapçık her sınavda öğrencinin önündedir ve iki bölümden oluşur:

- **Genel bölüm:** temel geometri ve trigonometri bağıntıları, vektör bileşenleri, belirsizlik yayılım kuralları (toplama/çıkarma, çarpma/bölme,
  üs alma), temel sabitler, SI önekleri (femto–peta), birim dönüşümleri, devre sembolleri, elektromanyetik spektrumun dalga boyu ölçeği.
- **Tema bölümleri (A–E):** müfredatta "… olarak verilen" her bağıntı, SL ve ek HL ayrı başlıklar altında. Bağıntılar yalnızca büyüklükler
  içindir; vektör gösterimi kullanılmaz.

**Soru yazımına etkisi:** kitapçıkta bulunan bir bağıntıyı hatırlamak ölçülmez; seçmek, birleştirmek ve yorumlamak ölçülür. Kitapçıkta
**olmayan** bir sabit ya da bağıntı gerekiyorsa soruda verilmelidir.

## 2. Temel sabitler (kitapçıktaki değerler)

Sorularda ve çözüm modellerinde **bu değerler ve bu anlamlı basamak** kullanılır.

| Sabit | Sembol | Değer | Referans adı |
|---|---|---|---|
| Serbest düşme ivmesi (Dünya yüzeyi) | g | 9.8 m s⁻² | `g` |
| Kütle çekim sabiti | G | 6.67 × 10⁻¹¹ N m² kg⁻² | `G` |
| Avogadro sabiti | N_A | 6.02 × 10²³ mol⁻¹ | `N_A` |
| Gaz sabiti | R | 8.31 J K⁻¹ mol⁻¹ | `R` |
| Boltzmann sabiti | k_B | 1.38 × 10⁻²³ J K⁻¹ | `k_B` |
| Stefan–Boltzmann sabiti | σ | 5.67 × 10⁻⁸ W m⁻² K⁻⁴ | `sigma` |
| Coulomb sabiti | k | 8.99 × 10⁹ N m² C⁻² | `k` |
| Boşluğun elektriksel geçirgenliği | ε₀ | 8.85 × 10⁻¹² C² N⁻¹ m⁻² | `epsilon_0` |
| Boşluğun manyetik geçirgenliği | μ₀ | 4π × 10⁻⁷ T m A⁻¹ | `mu_0` |
| Işığın boşluktaki hızı | c | 3.00 × 10⁸ m s⁻¹ | `c` |
| Planck sabiti | h | 6.63 × 10⁻³⁴ J s | `h` |
| Temel yük | e | 1.60 × 10⁻¹⁹ C | `e` |
| Elektronun durgun kütlesi | m_e | 9.110 × 10⁻³¹ kg = 0.000549 u = 0.511 MeV c⁻² | `m_e` |
| Protonun durgun kütlesi | m_p | 1.673 × 10⁻²⁷ kg = 1.007276 u = 938 MeV c⁻² | `m_p` |
| Nötronun durgun kütlesi | m_n | 1.675 × 10⁻²⁷ kg = 1.008665 u = 940 MeV c⁻² | `m_n` |
| Atomik kütle birimi | u | 1.661 × 10⁻²⁷ kg = 931.5 MeV c⁻² | `u` |
| Güneş sabiti | S | 1.36 × 10³ W m⁻² | `S` |
| Fermi yarıçapı | R₀ | 1.20 × 10⁻¹⁵ m | `R_0` |

Birim dönüşümleri: 1 rad ≡ 180°/π · T(K) = T(°C) + 273 · 1 ly = 9.46 × 10¹⁵ m · 1 pc = 3.26 ly · 1 AU = 1.50 × 10¹¹ m ·
1 kWh = 3.60 × 10⁶ J · hc = 1.99 × 10⁻²⁵ J m = 1.24 × 10⁻⁶ eV m.

Tema bölümlerinde bağıntının içinde verilen sayısal değerler de vardır (ör. Wien yasasındaki 2.9 × 10⁻³ m K ve hidrojen enerji
düzeylerindeki 13.6 eV); bunlar bağıntıyla birlikte öğrencinin elindedir.

## 3. Kitapçıkta olmayanlar (soruda verilmelidir)

Pilot sorularda kullanılan ve kitapçıkta **bulunmayan** değerler:

| Değer | Durum |
|---|---|
| Sesin havadaki hızı | Kitapçıkta yok; soruda verilmeli (pilot sorularda 340 m s⁻¹ olarak veriliyor) |
| Güneş'in ışınım gücü L☉ | Kitapçıkta yok; kullanılıyorsa soruda verilmeli |
| Güneş'in yarıçapı ve kütlesi, gezegen ve uydu verileri | Kitapçıkta yok; soruda verilmeli |
| Malzeme özellikleri (özgül ısı, gizli ısı, ısıl iletkenlik, özdirenç, yoğunluk, viskozite, kırılma indisi, iş fonksiyonu) | Kitapçıkta yok; soruda verilmeli |
| Nüklit kütleleri, yarı ömürler, bağlanma enerjileri | Kitapçıkta yok; soruda verilmeli (yalnızca proton, nötron, elektron ve u var) |
| Belirli şekillerin eylemsizlik momenti formülleri | Kitapçıkta yok; müfredat da "gerektiğinde verilir" diyor |
| Compton dalga boyu (h / m_e c) sayısal değeri | Bağıntı var, sayısal değer yok; öğrenci hesaplar ya da soruda verilir |

## 4. Pilot soruların bu tabloyla karşılaştırması (2026-10-11)

130 pilot soruda geçen sabit değerleri metin taramasıyla kitapçıkla karşılaştırıldı.

**Uyumlu (aynı değer, aynı anlamlı basamak):** g, G, R, k_B, N_A, σ, k, c, h, e, u (kg ve MeV c⁻²), R₀, 1 pc ve 1 ly dönüşümleri,
nötron kütlesi (u cinsinden).

**Düzeltilmesi gerekenler:**

| Dosya | Bulgu | Öneri |
|---|---|---|
| `d2-electric-magnetic-fields` (Soru 5) | Proton kütlesi 1.67 × 10⁻²⁷ kg olarak verilmiş; kitapçık 1.673 × 10⁻²⁷ kg veriyor | Kitapçık değerine çekilmeli; soruda ayrıca verilmesine gerek yok. Sonuç 2 anlamlı basamakta değişmez, ama markscheme satırı yeniden hesaplanmalı |
| `d3-motion-in-em-fields`, `e2-quantum-physics` | Elektron kütlesi 9.11 × 10⁻³¹ kg yazılmış; kitapçık 9.110 × 10⁻³¹ kg veriyor | Değer aynı; yazım kitapçıktaki gibi olmalı |
| `e3-radioactive-decay` | Proton ve nötron kütleleri 1.00728 u ve 1.00866 u olarak yuvarlanmış; kitapçık 1.007276 u ve 1.008665 u veriyor | Kitapçık değerleri kullanılmalı; kütle açığı yeniden hesaplanmalı |
| `e5-fusion-stars` | Güneş'in ışınım gücü 3.83 × 10²⁶ W dosya notunda geçiyor | Kitapçıkta olmadığı için, kullanıldığı her soruda açıkça verildiği doğrulanmalı |
| Tüm dosyalar | Kitapçıkta bulunan sabitler bazı sorularda ayrıca soru metninde veriliyor (ör. *k* = 8.99 × 10⁹) | Gerçek sınav düzeninde kitapçıktaki sabitler soruda tekrar verilmez; uzman kararıyla kaldırılabilir |

Bu tarama yalnızca sayı biçimine bakar; her sorunun hesabını yeniden yapmaz. Düzeltmeler uygulandığında etkilenen sorular yeniden
hesaplanmalı ve bağımsız çözücüden geçmelidir.

## 5. Uzmanların doğrulaması gerekenler

1. Bu tablo kitapçığın 1.0 sürümünden alındı; sınavda kullanılan güncel sürümle aynı olduğu teyit edilmeli.
2. §3'teki "soruda verilmeli" listesi pilot sorularda geçenlerle sınırlı; eksiksiz değil.
3. Kitapçıktaki sabitlerin soru metninde tekrar verilip verilmeyeceği (§4 son satır).

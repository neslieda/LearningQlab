# Pilot soruları çeviri raporu

> Otomatik üretilir: `python -m qlab.content.pilot convert`. Elle düzenlenmez; `convert --check` bu dosyanın yeniden üretilenle aynı olduğunu doğrular.
> Kurallar: [IMPORT_RULES.md](../../docs/pilot/IMPORT_RULES.md).

## 1. Dosya başına sorular

| Dosya | Soru | mcq | data_based | short_structured | long_structured |
|---|---|---|---|---|---|
| `a1-kinematics` | 5 | 3 | 1 | 1 | 0 |
| `a2-forces-momentum` | 5 | 4 | 0 | 1 | 0 |
| `a3-work-energy-power` | 5 | 4 | 0 | 1 | 0 |
| `a4-rigid-body-mechanics` | 5 | 4 | 0 | 1 | 0 |
| `a5-relativity` | 5 | 4 | 0 | 1 | 0 |
| `b1-thermal-energy-transfers` | 5 | 4 | 0 | 1 | 0 |
| `b2-greenhouse-effect` | 5 | 4 | 0 | 1 | 0 |
| `b3-gas-laws` | 6 | 4 | 1 | 1 | 0 |
| `b4-thermodynamics` | 6 | 5 | 0 | 1 | 0 |
| `b5-current-circuits` | 5 | 4 | 0 | 1 | 0 |
| `c1-simple-harmonic-motion` | 7 | 5 | 1 | 1 | 0 |
| `c2-wave-model` | 5 | 4 | 0 | 1 | 0 |
| `c3-wave-phenomena` | 6 | 5 | 0 | 1 | 0 |
| `c4-standing-waves-resonance` | 5 | 4 | 0 | 1 | 0 |
| `c5-doppler-effect` | 5 | 4 | 0 | 1 | 0 |
| `d1-gravitational-fields` | 5 | 4 | 0 | 1 | 0 |
| `d2-electric-magnetic-fields` | 5 | 4 | 0 | 1 | 0 |
| `d3-motion-in-em-fields` | 6 | 4 | 1 | 1 | 0 |
| `d4-induction` | 5 | 4 | 0 | 1 | 0 |
| `e1-structure-of-atom` | 6 | 5 | 0 | 1 | 0 |
| `e2-quantum-physics` | 6 | 4 | 1 | 1 | 0 |
| `e3-radioactive-decay` | 6 | 5 | 0 | 1 | 0 |
| `e4-fission` | 5 | 4 | 0 | 1 | 0 |
| `e5-fusion-stars` | 6 | 5 | 0 | 1 | 0 |
| **Toplam** | 130 | 101 | 5 | 24 | 0 |

## 2. Kuralla doldurulan alanlar (§5)

Bunlar kaynak bilgisi değil, varsayımdır; eğitmen incelemesinde düzeltilir.

**`mcq.option_kind` (çoktan seçmeli; 101 soru)**

| Değer | Adet |
|---|---|
| numeric_with_unit | 55 |
| statement | 17 |
| ratio | 13 |
| algebraic_expression | 10 |
| word_phrase | 6 |

**`part.command_term` (boş: ilk sözcük sözlükte yok)**

| Değer | Adet |
|---|---|
| determine | 25 |
| calculate | 24 |
| show | 23 |
| explain | 19 |
| (boş) | 17 |
| state | 13 |
| outline | 6 |
| suggest | 4 |
| describe | 1 |
| discuss | 1 |
| predict | 1 |

**`part.answer_type`**

| Değer | Adet |
|---|---|
| numeric_with_unit | 49 |
| explanation | 48 |
| derivation_numeric | 23 |
| word_phrase | 13 |
| extended_evaluation | 1 |

**`MarkPoint.kind`**

| Değer | Adet |
|---|---|
| statement | 271 |

**Uyaran `kind` (Şekil bloğu ve Şekil notu)**

| Değer | Adet |
|---|---|
| schematic_diagram | 14 |
| graph | 6 |
| ray_wavefront_diagram | 4 |
| circuit_diagram | 2 |
| energy_level_diagram | 1 |
| field_diagram | 1 |

**`Note.kind` (§3.2 kuralı; kaynakta yazmaz)**

| Değer | Adet |
|---|---|
| general | 71 |
| accept | 37 |
| owtte | 36 |
| ecf | 27 |
| cap | 16 |
| do_not_accept | 7 |

**`marks_capped = true` olan parçalar**

| Değer | Adet |
|---|---|
| true | 2 |

Sabit değerler: `part.assessment_objective`, `depends_on`, `stimulus_refs` boş; `Note.mark_point_id` ve `MarkPoint.alternative_group` kurulmaz; Uyaran `asset_id` yok (`visual_pending`).

## 3. Çözüm modelleri (§3.4)

Aktarılan: **13**. Atlanan: **16** (soru yine aktarılır, `solution_model` boştur).

**Atlama nedenleri (gruplu)**

| Neden | Adet |
|---|---|
| satır adı tanımlayıcı değil | 10 |
| ters tırnaksız parametre metni | 4 |
| bölüm yok | 1 |
| ifade sütunu tek ifade değil | 1 |

**Atlanan modeller**

| Soru | Neden | Ayrıntı |
|---|---|---|
| `pilot/a1-kinematics#5` | bölüm yok |  |
| `pilot/a4-rigid-body-mechanics#5` | ters tırnaksız parametre metni | `'( )'` |
| `pilot/b3-gas-laws#6` | ters tırnaksız parametre metni | `'veri tablosu'` |
| `pilot/b4-thermodynamics#6` | satır adı tanımlayıcı değil | `line 208: 'Tutarlılık kontrolü (öğrenciden istenmez)'` |
| `pilot/b5-current-circuits#5` | satır adı tanımlayıcı değil | `line 180: 'Karşılaştırma'` |
| `pilot/c1-simple-harmonic-motion#6` | satır adı tanımlayıcı değil | `line 189: 'Denetim (soruda istenmez)'` |
| `pilot/c1-simple-harmonic-motion#7` | ters tırnaksız parametre metni | `'(s² kg⁻¹)'` |
| `pilot/c2-wave-model#5` | satır adı tanımlayıcı değil | `line 171: 'Denetim (e)'` |
| `pilot/c3-wave-phenomena#6` | ifade sütunu tek ifade değil | `line 203` |
| `pilot/c4-standing-waves-resonance#5` | satır adı tanımlayıcı değil | `line 180: 'Denetim'` |
| `pilot/c5-doppler-effect#5` | satır adı tanımlayıcı değil | `line 178: 'Denetim (yanlış formül)'` |
| `pilot/d2-electric-magnetic-fields#5` | satır adı tanımlayıcı değil | `line 192: 'Çeldirici yol (c)'` |
| `pilot/d3-motion-in-em-fields#5` | satır adı tanımlayıcı değil | `line 194: 'Tutarlılık kontrolü'` |
| `pilot/d3-motion-in-em-fields#6` | satır adı tanımlayıcı değil | `line 263: 'Aralık'` |
| `pilot/e4-fission#5` | ters tırnaksız parametre metni | `'(u)'` |
| `pilot/e5-fusion-stars#6` | satır adı tanımlayıcı değil | `line 203: 'Kontrol'` |

**`sabit` sözcüğünden sonra gelip parametre olarak aktarılan değerler (24).** Sabit tablosuna bağ kurulmaz:

`pilot/a1-kinematics#4` `g`, `pilot/a2-forces-momentum#5` `g`, `pilot/a3-work-energy-power#5` `g`, `pilot/a5-relativity#5` `c`, `pilot/b1-thermal-energy-transfers#5` `L`, `pilot/b1-thermal-energy-transfers#5` `c`, `pilot/b2-greenhouse-effect#5` `sigma`, `pilot/b3-gas-laws#5` `R`, `pilot/b5-current-circuits#5` `rho`, `pilot/c1-simple-harmonic-motion#6` `g`, `pilot/d1-gravitational-fields#5` `G`, `pilot/d2-electric-magnetic-fields#5` `k`, `pilot/d3-motion-in-em-fields#6` `g`, `pilot/e1-structure-of-atom#6` `R0`, `pilot/e1-structure-of-atom#6` `e`, `pilot/e1-structure-of-atom#6` `k`, `pilot/e2-quantum-physics#5` `c`, `pilot/e2-quantum-physics#5` `e`, `pilot/e2-quantum-physics#5` `h`, `pilot/e2-quantum-physics#5` `m_e`, `pilot/e2-quantum-physics#6` `e`, `pilot/e5-fusion-stars#6` `ly_m`, `pilot/e5-fusion-stars#6` `pc_ly`, `pilot/e5-fusion-stars#6` `sigma`

## 4. Aktarılmayan serbest paragraflar

Markscheme ve formül zincirinden sonra (çoktan seçmelide yanılgı tablosundan sonra) gelen açıklama paragrafları aktarılmaz. Toplam: **12** paragraf, **11** soruda.

| Soru | Paragraf |
|---|---|
| `pilot/a2-forces-momentum#5` | 1 |
| `pilot/a3-work-energy-power#5` | 1 |
| `pilot/a4-rigid-body-mechanics#5` | 1 |
| `pilot/a5-relativity#5` | 2 |
| `pilot/c1-simple-harmonic-motion#6` | 1 |
| `pilot/c3-wave-phenomena#6` | 1 |
| `pilot/c4-standing-waves-resonance#4` | 1 |
| `pilot/c5-doppler-effect#4` | 1 |
| `pilot/d2-electric-magnetic-fields#4` | 1 |
| `pilot/d3-motion-in-em-fields#5` | 1 |
| `pilot/d4-induction#5` | 1 |

## 5. İtalik belirteçler (§4.2)

Toplam 979 italik belirteç, 236 farklı belirteç.

**Kural 1 (tek harf → değişken)** — 46 farklı belirteç:

`A` (6), `B` (11), `E` (30), `F` (4), `I` (20), `L` (17), `M` (1), `N` (7), `P` (35), `Q` (10), `R` (31), `S` (9), `T` (69), `U` (12), `V` (24), `W` (14), `a` (1), `b` (2), `c` (35), `d` (15), `e` (18), `f` (22), `g` (16), `h` (16), `k` (25), `m` (33), `n` (7), `p` (3), `q` (2), `r` (23), `s` (1), `t` (37), `u` (3), `v` (41), `x` (20), `y` (1), `Φ` (5), `α` (4), `γ` (6), `ε` (3), `θ` (23), `λ` (8), `σ` (2), `τ` (3), `φ` (2), `ω` (9)

**Kural 2 (büyük/Yunan harfli ≤ 4 harf → değişken)** — 34 farklı belirteç:

`AT` (1), `BIL` (2), `Br` (1), `BvL` (1), `FR` (1), `Fs` (1), `Fv` (2), `GM` (2), `GMm` (4), `Ir` (1), `Iω` (2), `MR` (7), `MRv` (1), `Mgh` (2), `Mv` (5), `NkT` (1), `PV` (8), `RA` (1), `TV` (1), `eE` (1), `eV` (3), `evB` (2), `kA` (1), `kQ` (2), `kT` (1), `mL` (1), `nR` (4), `αt` (1), `εI` (1), `ηr` (1), `λt` (1), `σT` (1), `ωR` (1), `ωt` (1)

**Kural 3 (kapalı değişken listesi → değişken)**

| Belirteç | Adet | Liste | İlk kullanım |
|---|---|---|---|
| `ct` | 4 | şartname örneği | `pilot/a5-relativity#4` |
| `gh` | 1 | **ek** | `pilot/a4-rigid-body-mechanics#5` |
| `gr` | 1 | **ek** | `pilot/a2-forces-momentum#3` |
| `gt` | 1 | şartname örneği | `pilot/a1-kinematics#5` |
| `hc` | 1 | **ek** | `pilot/e2-quantum-physics#5` |
| `hf` | 3 | şartname örneği | `pilot/e2-quantum-physics#6` |
| `kx` | 1 | **ek** | `pilot/a3-work-energy-power#4` |
| `mc` | 1 | **ek** | `pilot/b1-thermal-energy-transfers#4` |
| `mg` | 3 | şartname örneği | `pilot/a2-forces-momentum#3` |
| `mgv` | 1 | **ek** | `pilot/a3-work-energy-power#2` |
| `mr` | 0 | şartname örneği | — |
| `mv` | 8 | şartname örneği | `pilot/a2-forces-momentum#3` |
| `mx` | 1 | **ek** | `pilot/e2-quantum-physics#6` |
| `vt` | 0 | şartname örneği | — |
| `vx` | 0 | şartname örneği | — |

**Kural 4 (kapalı sözcük listesi → italik metin)**

| Belirteç | Adet | Liste | İlk kullanım |
|---|---|---|---|
| `Accept` | 3 | **ek** | `pilot/b4-thermodynamics#6` |
| `Allow` | 1 | **ek** | `pilot/c1-simple-harmonic-motion#6` |
| `OWTTE` | 36 | **ek** | `pilot/a1-kinematics#4` |
| `and` | 1 | **ek** | `pilot/c1-simple-harmonic-motion#7` |
| `into` | 0 | şartname örneği | — |
| `not` | 0 | şartname örneği | — |
| `on` | 0 | şartname örneği | — |
| `one` | 0 | şartname örneği | — |
| `one eighth` | 0 | şartname örneği | — |
| `out of` | 0 | şartname örneği | — |
| `parallel` | 0 | şartname örneği | — |
| `twice` | 0 | şartname örneği | — |
| `two` | 0 | şartname örneği | — |

**Kural 4 (boşluk ya da noktalama içeren tümce → italik metin)** — 140 farklı tümce, 160 kullanım (çoğu markscheme notudur).

## 6. Kural ekleri

IMPORT_RULES.md'nin açıkça karşılamadığı ve dönüştürücünün dar biçimde genişlettiği yerler. Her biri belgeye de işlenmelidir.

- **note-italic** — Notlarda tüm metin düğümlerinden `italic` işareti atılır (not satırının tamamı italik yazılır; satır `*Accept* Δ*U* = … *for the second mark.*` gibi bölünmüşse de).
  - Gerektiği yerler (29): `pilot/a1-kinematics#4`, `pilot/a1-kinematics#5`, `pilot/a2-forces-momentum#5`, `pilot/a3-work-energy-power#5`, `pilot/a4-rigid-body-mechanics#5`, `pilot/a5-relativity#5`, `pilot/b1-thermal-energy-transfers#5`, `pilot/b2-greenhouse-effect#5`, `pilot/b3-gas-laws#5`, `pilot/b3-gas-laws#6`, `pilot/b4-thermodynamics#6`, `pilot/b5-current-circuits#5`, `pilot/c1-simple-harmonic-motion#6`, `pilot/c1-simple-harmonic-motion#7`, `pilot/c2-wave-model#5`, `pilot/c3-wave-phenomena#6`, `pilot/c4-standing-waves-resonance#5`, `pilot/c5-doppler-effect#5`, `pilot/d1-gravitational-fields#5`, `pilot/d2-electric-magnetic-fields#5`, `pilot/d3-motion-in-em-fields#5`, `pilot/d3-motion-in-em-fields#6`, `pilot/d4-induction#5`, `pilot/e1-structure-of-atom#6`, `pilot/e2-quantum-physics#5`, `pilot/e2-quantum-physics#6`, `pilot/e3-radioactive-decay#6`, `pilot/e4-fission#5`, `pilot/e5-fusion-stars#6`
- **note-tick** — Not hücresindeki `✓` karakterleri atılır (alternatif yol notun içine yazılmış: `**OR** *… ✓ … ✓*`, `**ALTERNATIVE:** … ✓`); kaynak karşılaştırması da `✓` atar.
  - Gerektiği yerler (5): `pilot/b1-thermal-energy-transfers#5`, `pilot/b3-gas-laws#5`, `pilot/b5-current-circuits#5`, `pilot/d2-electric-magnetic-fields#5`, `pilot/d4-induction#5`
- **ecf-prefix** — `Allow ECF` ile başlayan her not `ecf` olur (`Allow ECF from (b)…` kalıbının dışındaki `Allow ECF for the volume from (a).`, `Allow ECF from an incorrect T in (b).`); `ecf_from` notun içindeki `(x)` / `(x)(y)` başvurularından kurulur.
  - Gerektiği yerler (2): `pilot/a2-forces-momentum#5`, `pilot/c1-simple-harmonic-motion#6`
- **total-max** — Markscheme `Total` hücresi `n` ya da `n max` olabilir (`2 max`); sayı parça puanına eşit olmalıdır.
  - Gerektiği yerler (2): `pilot/b2-greenhouse-effect#5`, `pilot/b3-gas-laws#5`
- **mcq-trailing-note** — Çoktan seçmelide yanılgı tablosundan sonra gelen serbest paragraflar (`Not: …`) aktarılmaz, raporda sayılır.
  - Gerektiği yerler (3): `pilot/c4-standing-waves-resonance#4`, `pilot/c5-doppler-effect#4`, `pilot/d2-electric-magnetic-fields#4`
- **italic-word** — Kapalı italik sözcük listesine eklenen belirteçler (aşağıda).
  - Gerektiği yerler (4): `Accept` (3; ilk: `pilot/b4-thermodynamics#6`), `Allow` (1; ilk: `pilot/c1-simple-harmonic-motion#6`), `OWTTE` (36; ilk: `pilot/a1-kinematics#4`), `and` (1; ilk: `pilot/c1-simple-harmonic-motion#7`)
- **variable-word** — Kapalı değişken listesine eklenen belirteçler (aşağıda).
  - Gerektiği yerler (7): `gh` (1; ilk: `pilot/a4-rigid-body-mechanics#5`), `gr` (1; ilk: `pilot/a2-forces-momentum#3`), `hc` (1; ilk: `pilot/e2-quantum-physics#5`), `kx` (1; ilk: `pilot/a3-work-energy-power#4`), `mc` (1; ilk: `pilot/b1-thermal-energy-transfers#4`), `mgv` (1; ilk: `pilot/a3-work-energy-power#2`), `mx` (1; ilk: `pilot/e2-quantum-physics#6`)

## 7. Yorumlar

Kuralın birden çok okunabildiği yerlerde seçilen okuma:

- **Uyaran türü** (§3.3): "açıklamadaki ilk eşleşen anahtar sözcük" açıklama metninde en önce geçen anahtar sözcük olarak okundu (listedeki sıra değil); büyük/küçük harf Türkçe kurallarıyla yok sayılır, eşleşme alt dizgidir (`devre` → `devresi`).
- **Yunan harfi komutu** (§4.3): komut adı Unicode harf adından alınır (`ε` → `\epsilon`, `φ` → `\phi`, `λ` → `\lambda`, `µ` → `\mu`, `Ω` → `\Omega`); `\varepsilon` ve `\varphi` kullanılmaz.
- **option_kind** (§5): "sayı + birim" = sayı (isteğe bağlı `× 10ⁿ`) ve en çok dört sözcüklük düz metin birim; seçeneklerden biri bile bu kalıba uymazsa (ör. birimsiz `0`) sıradaki kurala geçilir, bu yüzden `−2.0 J K⁻¹ | 0 | +0.50 J K⁻¹ | +2.0 J K⁻¹` `word_phrase` olur. İtalik harf içeren seçenek (`1.3*c*`) değişken sayılır → `algebraic_expression`.
- **Kazanım** (`outcome`): tablo hücresi olduğu gibi alınır; hücredeki `*γ*` gibi işaretler çevrilmez.
- **Düzey** (§3): başlık `HL` diyor da tablo `SL` diyorsa dönüştürücü durur; tablo `HL` iken başlıkta HL yazmaması hata değildir.
- **Parametre birimi**: ters tırnak içinde değerden sonra gelen metin birimdir; ters tırnağın dışındaki açıklama (`(s² kg⁻¹)`) "ters tırnaksız parametre" sayılır ve modeli düşürür.
- **Adım adı**: ilk sütundaki ilk ters tırnaklı tanımlayıcıdır; ardından gelen ters tırnaksız metin (`(denetim)`) yok sayılır, ikinci bir ters tırnaklı ad modeli düşürür.
- **Sonuç sütunu birimi**: sayıdan sonra kalan metin yalnızca birim sözcüklerinden oluşuyorsa `unit` olur; açıklama içeren sonuçlar (`180 s (tam)`) birimsiz bırakılır.

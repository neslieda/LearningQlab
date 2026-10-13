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
| schematic_diagram | 13 |
| graph | 7 |
| circuit_diagram | 5 |
| energy_level_diagram | 1 |
| field_diagram | 1 |
| ray_wavefront_diagram | 1 |

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

### Soru soru kuralla doldurulan değerler

| Soru | Tür | Değer |
|---|---|---|
| `pilot/a1-kinematics#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a1-kinematics#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a1-kinematics#3` | mcq | `option_kind = algebraic_expression` |
| `pilot/a1-kinematics#4` | yapılandırılmış | a: state → word_phrase; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d.i: explain → explanation; d.ii: state → word_phrase |
| `pilot/a1-kinematics#5` | yapılandırılmış | a: outline → explanation; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: — → explanation; e: — → explanation |
| `pilot/a2-forces-momentum#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a2-forces-momentum#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a2-forces-momentum#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a2-forces-momentum#4` | mcq | `option_kind = ratio` |
| `pilot/a2-forces-momentum#5` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: explain → explanation |
| `pilot/a3-work-energy-power#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a3-work-energy-power#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a3-work-energy-power#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a3-work-energy-power#4` | mcq | `option_kind = algebraic_expression` |
| `pilot/a3-work-energy-power#5` | yapılandırılmış | a: show → derivation_numeric; b: determine → numeric_with_unit; c: — → explanation; d: explain → explanation |
| `pilot/a4-rigid-body-mechanics#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a4-rigid-body-mechanics#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a4-rigid-body-mechanics#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a4-rigid-body-mechanics#4` | mcq | `option_kind = ratio` |
| `pilot/a4-rigid-body-mechanics#5` | yapılandırılmış | a: state → word_phrase; b: show → derivation_numeric; c: calculate → numeric_with_unit; d: explain → explanation |
| `pilot/a5-relativity#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a5-relativity#2` | mcq | `option_kind = algebraic_expression` |
| `pilot/a5-relativity#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a5-relativity#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/a5-relativity#5` | yapılandırılmış | a: state → word_phrase; b: show → derivation_numeric; c: calculate → numeric_with_unit; d: determine → numeric_with_unit; e: determine → numeric_with_unit |
| `pilot/b1-thermal-energy-transfers#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b1-thermal-energy-transfers#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b1-thermal-energy-transfers#3` | mcq | `option_kind = ratio` |
| `pilot/b1-thermal-energy-transfers#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b1-thermal-energy-transfers#5` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: explain → explanation; d: determine → numeric_with_unit |
| `pilot/b2-greenhouse-effect#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b2-greenhouse-effect#2` | mcq | `option_kind = algebraic_expression` |
| `pilot/b2-greenhouse-effect#3` | mcq | `option_kind = statement` |
| `pilot/b2-greenhouse-effect#4` | mcq | `option_kind = ratio` |
| `pilot/b2-greenhouse-effect#5` | yapılandırılmış | a: explain → explanation; b: show → derivation_numeric; c: explain → explanation; d: determine → numeric_with_unit |
| `pilot/b3-gas-laws#1` | mcq | `option_kind = ratio` |
| `pilot/b3-gas-laws#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b3-gas-laws#3` | mcq | `option_kind = statement` |
| `pilot/b3-gas-laws#4` | mcq | `option_kind = ratio` |
| `pilot/b3-gas-laws#5` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: explain → explanation; d: calculate → numeric_with_unit; e: suggest → explanation |
| `pilot/b3-gas-laws#6` | yapılandırılmış | a: state → word_phrase; b: outline → explanation; c: — → explanation; d: — → explanation; e: determine → numeric_with_unit; f: — → explanation; g: suggest → explanation |
| `pilot/b4-thermodynamics#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b4-thermodynamics#2` | mcq | `option_kind = algebraic_expression` |
| `pilot/b4-thermodynamics#3` | mcq | `option_kind = algebraic_expression` |
| `pilot/b4-thermodynamics#4` | mcq | `option_kind = ratio` |
| `pilot/b4-thermodynamics#5` | mcq | `option_kind = word_phrase` |
| `pilot/b4-thermodynamics#6` | yapılandırılmış | a: show → derivation_numeric; b: determine → numeric_with_unit; c: determine → numeric_with_unit; d: discuss → extended_evaluation |
| `pilot/b5-current-circuits#1` | mcq | `option_kind = algebraic_expression` |
| `pilot/b5-current-circuits#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b5-current-circuits#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b5-current-circuits#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/b5-current-circuits#5` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: explain → explanation; d: determine → numeric_with_unit |
| `pilot/c1-simple-harmonic-motion#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c1-simple-harmonic-motion#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c1-simple-harmonic-motion#3` | mcq | `option_kind = algebraic_expression` |
| `pilot/c1-simple-harmonic-motion#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c1-simple-harmonic-motion#5` | mcq | `option_kind = word_phrase` |
| `pilot/c1-simple-harmonic-motion#6` | yapılandırılmış | a: state → word_phrase; b: show → derivation_numeric; c: calculate → numeric_with_unit; d: describe → explanation; e: — → explanation |
| `pilot/c1-simple-harmonic-motion#7` | yapılandırılmış | a: state → word_phrase; b.i: state → word_phrase; b.ii: calculate → numeric_with_unit; c: determine → numeric_with_unit; d.i: suggest → explanation; d.ii: explain → explanation |
| `pilot/c2-wave-model#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c2-wave-model#2` | mcq | `option_kind = word_phrase` |
| `pilot/c2-wave-model#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c2-wave-model#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c2-wave-model#5` | yapılandırılmış | a: state → word_phrase; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: show → derivation_numeric; e: — → explanation |
| `pilot/c3-wave-phenomena#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c3-wave-phenomena#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c3-wave-phenomena#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c3-wave-phenomena#4` | mcq | `option_kind = ratio` |
| `pilot/c3-wave-phenomena#5` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c3-wave-phenomena#6` | yapılandırılmış | a: explain → explanation; b: show → derivation_numeric; c.i: calculate → numeric_with_unit; c.ii: determine → numeric_with_unit; d: state → word_phrase |
| `pilot/c4-standing-waves-resonance#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c4-standing-waves-resonance#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c4-standing-waves-resonance#3` | mcq | `option_kind = word_phrase` |
| `pilot/c4-standing-waves-resonance#4` | mcq | `option_kind = statement` |
| `pilot/c4-standing-waves-resonance#5` | yapılandırılmış | a: outline → explanation; b: show → derivation_numeric; c.i: state → word_phrase; c.ii: calculate → numeric_with_unit; d: explain → explanation; e: — → explanation |
| `pilot/c5-doppler-effect#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c5-doppler-effect#2` | mcq | `option_kind = algebraic_expression` |
| `pilot/c5-doppler-effect#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c5-doppler-effect#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/c5-doppler-effect#5` | yapılandırılmış | a: explain → explanation; b: show → derivation_numeric; c: calculate → numeric_with_unit; d: — → explanation |
| `pilot/d1-gravitational-fields#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d1-gravitational-fields#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d1-gravitational-fields#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d1-gravitational-fields#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d1-gravitational-fields#5` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: explain → explanation |
| `pilot/d2-electric-magnetic-fields#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d2-electric-magnetic-fields#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d2-electric-magnetic-fields#3` | mcq | `option_kind = statement` |
| `pilot/d2-electric-magnetic-fields#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d2-electric-magnetic-fields#5` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: explain → explanation |
| `pilot/d3-motion-in-em-fields#1` | mcq | `option_kind = algebraic_expression` |
| `pilot/d3-motion-in-em-fields#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d3-motion-in-em-fields#3` | mcq | `option_kind = statement` |
| `pilot/d3-motion-in-em-fields#4` | mcq | `option_kind = statement` |
| `pilot/d3-motion-in-em-fields#5` | yapılandırılmış | a: show → derivation_numeric; b: state → word_phrase; c: explain → explanation; d: determine → numeric_with_unit; e: explain → explanation |
| `pilot/d3-motion-in-em-fields#6` | yapılandırılmış | a: outline → explanation; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: — → explanation; e: — → explanation; f: suggest → explanation |
| `pilot/d4-induction#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/d4-induction#2` | mcq | `option_kind = statement` |
| `pilot/d4-induction#3` | mcq | `option_kind = statement` |
| `pilot/d4-induction#4` | mcq | `option_kind = statement` |
| `pilot/d4-induction#5` | yapılandırılmış | a: calculate → numeric_with_unit; b: determine → numeric_with_unit; c: show → derivation_numeric; d: explain → explanation |
| `pilot/e1-structure-of-atom#1` | mcq | `option_kind = statement` |
| `pilot/e1-structure-of-atom#2` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e1-structure-of-atom#3` | mcq | `option_kind = statement` |
| `pilot/e1-structure-of-atom#4` | mcq | `option_kind = ratio` |
| `pilot/e1-structure-of-atom#5` | mcq | `option_kind = ratio` |
| `pilot/e1-structure-of-atom#6` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c.i: explain → explanation; c.ii: — → explanation |
| `pilot/e2-quantum-physics#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e2-quantum-physics#2` | mcq | `option_kind = ratio` |
| `pilot/e2-quantum-physics#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e2-quantum-physics#4` | mcq | `option_kind = statement` |
| `pilot/e2-quantum-physics#5` | yapılandırılmış | a: show → derivation_numeric; b: outline → explanation; c: predict → explanation; d: calculate → numeric_with_unit |
| `pilot/e2-quantum-physics#6` | yapılandırılmış | a: outline → explanation; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: determine → numeric_with_unit; e: — → explanation |
| `pilot/e3-radioactive-decay#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e3-radioactive-decay#2` | mcq | `option_kind = word_phrase` |
| `pilot/e3-radioactive-decay#3` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e3-radioactive-decay#4` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e3-radioactive-decay#5` | mcq | `option_kind = statement` |
| `pilot/e3-radioactive-decay#6` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: — → explanation |
| `pilot/e4-fission#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e4-fission#2` | mcq | `option_kind = statement` |
| `pilot/e4-fission#3` | mcq | `option_kind = ratio` |
| `pilot/e4-fission#4` | mcq | `option_kind = statement` |
| `pilot/e4-fission#5` | yapılandırılmış | a: state → word_phrase; b: show → derivation_numeric; c: determine → numeric_with_unit; d: — → explanation |
| `pilot/e5-fusion-stars#1` | mcq | `option_kind = numeric_with_unit` |
| `pilot/e5-fusion-stars#2` | mcq | `option_kind = ratio` |
| `pilot/e5-fusion-stars#3` | mcq | `option_kind = word_phrase` |
| `pilot/e5-fusion-stars#4` | mcq | `option_kind = statement` |
| `pilot/e5-fusion-stars#5` | mcq | `option_kind = statement` |
| `pilot/e5-fusion-stars#6` | yapılandırılmış | a: show → derivation_numeric; b: calculate → numeric_with_unit; c: determine → numeric_with_unit; d: — → explanation |

**Komut sözcüğü boş olan parçalar (17):** `pilot/a1-kinematics#5` (d), `pilot/a1-kinematics#5` (e), `pilot/a3-work-energy-power#5` (c), `pilot/b3-gas-laws#6` (c), `pilot/b3-gas-laws#6` (d), `pilot/b3-gas-laws#6` (f), `pilot/c1-simple-harmonic-motion#6` (e), `pilot/c2-wave-model#5` (e), `pilot/c4-standing-waves-resonance#5` (e), `pilot/c5-doppler-effect#5` (d), `pilot/d3-motion-in-em-fields#6` (d), `pilot/d3-motion-in-em-fields#6` (e), `pilot/e1-structure-of-atom#6` (c.ii), `pilot/e2-quantum-physics#6` (e), `pilot/e3-radioactive-decay#6` (d), `pilot/e4-fission#5` (d), `pilot/e5-fusion-stars#6` (d).

### Uyaranlar

| Soru | Uyaran | Tür | Kaynak |
|---|---|---|---|
| `pilot/a1-kinematics#5` | fig1 | graph | Şekil notu |
| `pilot/a4-rigid-body-mechanics#1` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/a5-relativity#5` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/b3-gas-laws#6` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/b3-gas-laws#6` | fig2 | graph | Şekil notu |
| `pilot/b4-thermodynamics#6` | fig1 | graph | Şekil bloğu |
| `pilot/b5-current-circuits#3` | fig1 | circuit_diagram | Şekil bloğu |
| `pilot/b5-current-circuits#4` | fig1 | circuit_diagram | Şekil bloğu |
| `pilot/b5-current-circuits#5` | fig1 | circuit_diagram | Şekil bloğu |
| `pilot/c1-simple-harmonic-motion#7` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/c1-simple-harmonic-motion#7` | fig2 | graph | Şekil notu |
| `pilot/c2-wave-model#2` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/c3-wave-phenomena#6` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/c4-standing-waves-resonance#5` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/c5-doppler-effect#5` | fig1 | ray_wavefront_diagram | Şekil bloğu |
| `pilot/d2-electric-magnetic-fields#3` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/d3-motion-in-em-fields#3` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/d3-motion-in-em-fields#5` | fig1 | field_diagram | Şekil bloğu |
| `pilot/d3-motion-in-em-fields#6` | fig1 | circuit_diagram | Şekil bloğu |
| `pilot/d3-motion-in-em-fields#6` | fig2 | graph | Şekil notu |
| `pilot/d4-induction#1` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/d4-induction#2` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/d4-induction#5` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/e1-structure-of-atom#2` | fig1 | energy_level_diagram | Şekil bloğu |
| `pilot/e2-quantum-physics#5` | fig1 | schematic_diagram | Şekil bloğu |
| `pilot/e2-quantum-physics#6` | fig1 | circuit_diagram | Şekil bloğu |
| `pilot/e2-quantum-physics#6` | fig2 | graph | Şekil notu |
| `pilot/e5-fusion-stars#3` | fig1 | graph | Şekil bloğu |

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

**Adım birimleri.** Aktarılan modellerde 61 adım var; bunlardan **14** tanesinin `unit` alanı boş, çünkü `Sonuç` hücresi "sayı + birim" değil (sayı, açıklama ya da birimsiz ifade). Soru başına (yalnızca boş birimi olanlar):

| Soru | Birimsiz adım | Adım |
|---|---|---|
| `pilot/a5-relativity#5` | 3 | 5 |
| `pilot/b1-thermal-energy-transfers#5` | 2 | 5 |
| `pilot/b2-greenhouse-effect#5` | 1 | 5 |
| `pilot/b3-gas-laws#5` | 1 | 3 |
| `pilot/d1-gravitational-fields#5` | 2 | 5 |
| `pilot/d4-induction#5` | 1 | 5 |
| `pilot/e2-quantum-physics#5` | 1 | 4 |
| `pilot/e2-quantum-physics#6` | 1 | 5 |
| `pilot/e3-radioactive-decay#6` | 2 | 5 |

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

**Aktarılmayan Şekil notu metni:** 5 soruda `### Şekil notu` bölümü vardır; metni aktarılmaz (§3.2), uyaranın açıklaması sabit metindir: `pilot/a1-kinematics#5`, `pilot/b3-gas-laws#6`, `pilot/c1-simple-harmonic-motion#7`, `pilot/d3-motion-in-em-fields#6`, `pilot/e2-quantum-physics#6`.

## 5. İtalik belirteçler (§4.2)

Toplam 962 italik belirteç, 236 farklı belirteç.

**Kural 1 (tek harf → değişken)** — 46 farklı belirteç:

`A` (6), `B` (11), `E` (30), `F` (4), `I` (19), `L` (17), `M` (1), `N` (7), `P` (34), `Q` (10), `R` (31), `S` (9), `T` (64), `U` (12), `V` (23), `W` (14), `a` (1), `b` (2), `c` (35), `d` (15), `e` (18), `f` (20), `g` (16), `h` (15), `k` (24), `m` (31), `n` (7), `p` (3), `q` (2), `r` (23), `s` (1), `t` (36), `u` (3), `v` (41), `x` (20), `y` (1), `Φ` (5), `α` (4), `γ` (6), `ε` (3), `θ` (21), `λ` (8), `σ` (2), `τ` (3), `φ` (2), `ω` (9)

**Kural 2 (büyük/Yunan harfli ≤ 4 harf → değişken)** — 34 farklı belirteç; yeni biri incelemede görünsün diye tek tek listelenir:

| Belirteç | Adet | İlk kullanım |
|---|---|---|
| `AT` | 1 | `pilot/b1-thermal-energy-transfers#3` |
| `BIL` | 2 | `pilot/d3-motion-in-em-fields#6` |
| `Br` | 1 | `pilot/d3-motion-in-em-fields#5` |
| `BvL` | 1 | `pilot/d4-induction#5` |
| `FR` | 1 | `pilot/a4-rigid-body-mechanics#2` |
| `Fs` | 1 | `pilot/a3-work-energy-power#1` |
| `Fv` | 2 | `pilot/a3-work-energy-power#2` |
| `GM` | 2 | `pilot/d1-gravitational-fields#5` |
| `GMm` | 4 | `pilot/d1-gravitational-fields#5` |
| `Ir` | 1 | `pilot/b5-current-circuits#5` |
| `Iω` | 2 | `pilot/a4-rigid-body-mechanics#5` |
| `MR` | 7 | `pilot/a4-rigid-body-mechanics#2` |
| `MRv` | 1 | `pilot/a4-rigid-body-mechanics#5` |
| `Mgh` | 2 | `pilot/a4-rigid-body-mechanics#5` |
| `Mv` | 5 | `pilot/a4-rigid-body-mechanics#4` |
| `NkT` | 1 | `pilot/b3-gas-laws#2` |
| `PV` | 8 | `pilot/b3-gas-laws#1` |
| `RA` | 1 | `pilot/b5-current-circuits#5` |
| `TV` | 1 | `pilot/b4-thermodynamics#2` |
| `eE` | 1 | `pilot/d3-motion-in-em-fields#5` |
| `eV` | 3 | `pilot/e2-quantum-physics#5` |
| `evB` | 2 | `pilot/d3-motion-in-em-fields#5` |
| `kA` | 1 | `pilot/b1-thermal-energy-transfers#2` |
| `kQ` | 2 | `pilot/d2-electric-magnetic-fields#5` |
| `kT` | 1 | `pilot/b3-gas-laws#1` |
| `mL` | 1 | `pilot/b1-thermal-energy-transfers#4` |
| `nR` | 4 | `pilot/b3-gas-laws#5` |
| `αt` | 1 | `pilot/a4-rigid-body-mechanics#2` |
| `εI` | 1 | `pilot/d4-induction#5` |
| `ηr` | 1 | `pilot/a2-forces-momentum#5` |
| `λt` | 1 | `pilot/e3-radioactive-decay#6` |
| `σT` | 1 | `pilot/e5-fusion-stars#6` |
| `ωR` | 1 | `pilot/a4-rigid-body-mechanics#5` |
| `ωt` | 1 | `pilot/c1-simple-harmonic-motion#5` |

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

- **Uyaran türü** (§3.3): "en önce geçen anahtar sözcük" açıklama metninde en küçük konumlu eşleşme olarak okundu (listedeki sıra değil). Eşleşme büyük/küçük harfe duyarsızdır (Türkçe `I/ı`, `İ/i` çiftleriyle: `Işın` → `ışın`) ve sözcük başında aranır; sözcüğün sonu serbesttir (`devre` → `devresi`). `P–V` yalnızca uzun çizgiyle yazıldığında eşleşir.
- **Not içindeki `✓`** (§8): metinde kalır; kaynak karşılaştırması da `✓` atar. Bu notlar Notlar sütununa yazılmış alternatif yollardır.
- **Şekil notu** (§3.2): metni aktarılmaz; uyaran sabit açıklama ve `graph` türüyle açılır.
- **Yunan harfi komutu** (§4.3): komut adı Unicode harf adından alınır (`ε` → `\epsilon`, `φ` → `\phi`, `λ` → `\lambda`, `µ` → `\mu`, `Ω` → `\Omega`); `\varepsilon` ve `\varphi` kullanılmaz.
- **option_kind** (§5): "sayı + birim" = sayı (isteğe bağlı `× 10ⁿ`) ve en çok dört sözcüklük düz metin birim; seçeneklerden biri bile bu kalıba uymazsa (ör. birimsiz `0`) sıradaki kurala geçilir, bu yüzden `−2.0 J K⁻¹ | 0 | +0.50 J K⁻¹ | +2.0 J K⁻¹` `word_phrase` olur. İtalik harf içeren seçenek (`1.3*c*`) değişken sayılır → `algebraic_expression`.
- **Kazanım** (`outcome`): tablo hücresi olduğu gibi alınır; hücredeki `*γ*` gibi işaretler çevrilmez.
- **Düzey** (§3): başlık `HL` diyor da tablo `SL` diyorsa dönüştürücü durur; tablo `HL` iken başlıkta HL yazmaması hata değildir.
- **Parametre birimi**: ters tırnak içinde değerden sonra gelen metin birimdir; ters tırnağın dışındaki açıklama (`(s² kg⁻¹)`) "ters tırnaksız parametre" sayılır ve modeli düşürür.
- **Adım adı**: ilk sütundaki ilk ters tırnaklı tanımlayıcıdır; ardından gelen ters tırnaksız metin (`(denetim)`) yok sayılır, ikinci bir ters tırnaklı ad modeli düşürür.
- **Sonuç sütunu birimi**: sayıdan sonra kalan metin yalnızca birim sözcüklerinden oluşuyorsa `unit` olur; açıklama içeren sonuçlar (`180 s (tam)`) birimsiz bırakılır.

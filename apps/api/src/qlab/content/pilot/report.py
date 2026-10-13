"""The conversion report (content/pilot/CONVERSION_REPORT.md), generated from a `Tally`.

Contents follow docs/pilot/IMPORT_RULES.md section 2. Nothing here depends on time, paths or the
order of dictionary insertion: the same tally always renders the same text.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence

from qlab.content.pilot.markdown import (
    ADDITIONS,
    ITALIC_WORDS,
    SPEC_ITALIC_WORDS,
    SPEC_VARIABLE_WORDS,
    VARIABLE_WORDS,
    ItalicUse,
    Tally,
)

_CLASS_ORDER = ("mcq", "data_based", "short_structured", "long_structured")
_CATEGORY_TITLES = (
    ("option_kind", "`mcq.option_kind` (çoktan seçmeli; 101 soru)"),
    ("command_term", "`part.command_term` (boş: ilk sözcük sözlükte yok)"),
    ("answer_type", "`part.answer_type`"),
    ("mark_point_kind", "`MarkPoint.kind`"),
    ("stimulus_kind", "Uyaran `kind` (Şekil bloğu ve Şekil notu)"),
    ("note_kind", "`Note.kind` (§3.2 kuralı; kaynakta yazmaz)"),
    ("marks_capped", "`marks_capped = true` olan parçalar"),
)
_INTERPRETATIONS = (
    '**Uyaran türü** (§3.3): "en önce geçen anahtar sözcük" açıklama metninde en küçük konumlu '
    "eşleşme olarak okundu (listedeki sıra değil). Eşleşme büyük/küçük harfe duyarsızdır "
    "(Türkçe `I/ı`, `İ/i` çiftleriyle: `Işın` → `ışın`) ve sözcük başında aranır; sözcüğün "
    "sonu serbesttir (`devre` → `devresi`). `P–V` yalnızca uzun çizgiyle yazıldığında eşleşir.",
    "**Not içindeki `✓`** (§8): metinde kalır; kaynak karşılaştırması da `✓` atar. Bu notlar "
    "Notlar sütununa yazılmış alternatif yollardır.",
    "**Şekil notu** (§3.2): metni aktarılmaz; uyaran sabit açıklama ve `graph` türüyle açılır.",
    "**Yunan harfi komutu** (§4.3): komut adı Unicode harf adından alınır (`ε` → `\\epsilon`, "
    "`φ` → `\\phi`, `λ` → `\\lambda`, `µ` → `\\mu`, `Ω` → `\\Omega`); `\\varepsilon` ve `\\varphi` "
    "kullanılmaz.",
    '**option_kind** (§5): "sayı + birim" = sayı (isteğe bağlı `× 10ⁿ`) ve en çok dört sözcüklük '
    "düz metin birim; seçeneklerden biri bile bu kalıba uymazsa (ör. birimsiz `0`) sıradaki kurala "
    "geçilir, bu yüzden `−2.0 J K⁻¹ | 0 | +0.50 J K⁻¹ | +2.0 J K⁻¹` `word_phrase` olur. "
    "İtalik harf içeren seçenek (`1.3*c*`) değişken sayılır → `algebraic_expression`.",
    "**Kazanım** (`outcome`): tablo hücresi olduğu gibi alınır; hücredeki `*γ*` gibi işaretler "
    "çevrilmez.",
    "**Düzey** (§3): başlık `HL` diyor da tablo `SL` diyorsa dönüştürücü durur; tablo `HL` iken "
    "başlıkta HL yazmaması hata değildir.",
    "**Parametre birimi**: ters tırnak içinde değerden sonra gelen metin birimdir; ters tırnağın "
    'dışındaki açıklama (`(s² kg⁻¹)`) "ters tırnaksız parametre" sayılır ve modeli düşürür.',
    "**Adım adı**: ilk sütundaki ilk ters tırnaklı tanımlayıcıdır; ardından gelen ters tırnaksız "
    "metin (`(denetim)`) yok sayılır, ikinci bir ters tırnaklı ad modeli düşürür.",
    "**Sonuç sütunu birimi**: sayıdan sonra kalan metin yalnızca birim sözcüklerinden "
    "oluşuyorsa `unit` olur; açıklama içeren sonuçlar (`180 s (tam)`) birimsiz bırakılır.",
)


def _table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return lines


def _ranked(counter: Counter[str]) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def _inline(tokens: Iterable[tuple[str, ItalicUse]]) -> str:
    return ", ".join(f"`{token}` ({use.count})" for token, use in sorted(tokens))


def _field_sections(tally: Tally) -> list[str]:
    """Rule-filled values to double-check, per question (section 5 of the rules)."""
    rows = sorted(tally.question_fields)
    out: list[str] = ["### Soru soru kuralla doldurulan değerler", ""]
    table: list[tuple[object, ...]] = []
    for ref, kind, option, parts in rows:
        if kind == "mcq":
            table.append((f"`{ref}`", "mcq", f"`option_kind = {option}`"))
        else:
            summary = "; ".join(f"{lab}: {term or '—'} → {atype}" for lab, term, atype in parts)
            table.append((f"`{ref}`", "yapılandırılmış", summary))
    out += _table(("Soru", "Tür", "Değer"), table)
    empty = [
        (ref, lab) for ref, kind, _, parts in rows if kind != "mcq" for lab, t, _ in parts if not t
    ]
    out += [
        "",
        f"**Komut sözcüğü boş olan parçalar ({len(empty)}):** "
        + ", ".join(f"`{ref}` ({lab})" for ref, lab in empty)
        + ".",
        "",
        "### Uyaranlar",
        "",
    ]
    out += _table(
        ("Soru", "Uyaran", "Tür", "Kaynak"),
        ((f"`{ref}`", sid, kind, src) for ref, sid, kind, src in sorted(tally.stimuli)),
    )
    out += [""]
    return out


def render_report(tally: Tally, stems: Sequence[str]) -> str:
    out: list[str] = [
        "# Pilot soruları çeviri raporu",
        "",
        "> Otomatik üretilir: `python -m qlab.content.pilot convert`. Elle düzenlenmez; "
        "`convert --check` bu dosyanın yeniden üretilenle aynı olduğunu doğrular.",
        "> Kurallar: [IMPORT_RULES.md](../../docs/pilot/IMPORT_RULES.md).",
        "",
    ]

    totals: Counter[str] = Counter()
    for stem in stems:
        totals.update(tally.file_counts.get(stem, Counter()))
    out += ["## 1. Dosya başına sorular", ""]
    rows: list[tuple[object, ...]] = []
    for stem in stems:
        counts = tally.file_counts.get(stem, Counter())
        rows.append((f"`{stem}`", sum(counts.values()), *(counts[c] for c in _CLASS_ORDER)))
    rows.append(("**Toplam**", sum(totals.values()), *(totals[c] for c in _CLASS_ORDER)))
    out += _table(
        ("Dosya", "Soru", "mcq", "data_based", "short_structured", "long_structured"), rows
    )
    out += [""]

    out += [
        "## 2. Kuralla doldurulan alanlar (§5)",
        "",
        "Bunlar kaynak bilgisi değil, varsayımdır; eğitmen incelemesinde düzeltilir.",
        "",
    ]
    for key, title in _CATEGORY_TITLES:
        counter = tally.counters.get(key)
        if not counter:
            continue
        out += [f"**{title}**", ""]
        out += _table(("Değer", "Adet"), _ranked(counter))
        out += [""]
    out += [
        "Sabit değerler: `part.assessment_objective`, `depends_on`, `stimulus_refs` boş; "
        "`Note.mark_point_id` ve `MarkPoint.alternative_group` kurulmaz; Uyaran `asset_id` yok "
        "(`visual_pending`).",
        "",
    ]
    out += _field_sections(tally)

    imported = sorted(tally.models_imported)
    omitted = sorted(tally.models_omitted)
    out += [
        "## 3. Çözüm modelleri (§3.4)",
        "",
        f"Aktarılan: **{len(imported)}**. Atlanan: **{len(omitted)}** "
        "(soru yine aktarılır, `solution_model` boştur).",
        "",
    ]
    groups: Counter[str] = Counter(code for _, code, _ in omitted)
    if groups:
        out += ["**Atlama nedenleri (gruplu)**", ""]
        out += _table(("Neden", "Adet"), _ranked(groups))
        out += ["", "**Atlanan modeller**", ""]
        out += _table(
            ("Soru", "Neden", "Ayrıntı"),
            ((f"`{ref}`", code, f"`{detail}`" if detail else "") for ref, code, detail in omitted),
        )
        out += [""]
    steps_total = sum(n for _, _, n in tally.step_units)
    steps_empty = sum(e for _, e, _ in tally.step_units)
    out += [
        f"**Adım birimleri.** Aktarılan modellerde {steps_total} adım var; bunlardan "
        f'**{steps_empty}** tanesinin `unit` alanı boş, çünkü `Sonuç` hücresi "sayı + birim" '
        "değil (sayı, açıklama ya da birimsiz ifade). Soru başına (yalnızca boş birimi olanlar):",
        "",
    ]
    out += _table(
        ("Soru", "Birimsiz adım", "Adım"),
        ((f"`{ref}`", e, n) for ref, e, n in sorted(tally.step_units) if e),
    )
    out += [""]
    constants = sorted(tally.constants)
    out += [
        "**`sabit` sözcüğünden sonra gelip parametre olarak aktarılan değerler "
        f"({len(constants)}).** Sabit tablosuna bağ kurulmaz:",
        "",
        ", ".join(f"`{ref}` `{name}`" for ref, name in constants) or "yok",
        "",
    ]

    free = sorted(tally.free_paragraphs)
    out += [
        "## 4. Aktarılmayan serbest paragraflar",
        "",
        "Markscheme ve formül zincirinden sonra (çoktan seçmelide yanılgı tablosundan sonra) gelen "
        f"açıklama paragrafları aktarılmaz. Toplam: **{sum(n for _, n in free)}** paragraf, "
        f"**{len(free)}** soruda.",
        "",
    ]
    out += _table(("Soru", "Paragraf"), ((f"`{ref}`", n) for ref, n in free))
    notes = sorted(tally.figure_notes_skipped)
    out += [
        "",
        f"**Aktarılmayan Şekil notu metni:** {len(notes)} soruda `### Şekil notu` bölümü "
        "vardır; metni aktarılmaz (§3.2), uyaranın açıklaması sabit metindir: "
        + ", ".join(f"`{ref}`" for ref in notes)
        + ".",
        "",
    ]

    out += ["## 5. İtalik belirteçler (§4.2)", ""]
    by_rule: dict[str, list[tuple[str, ItalicUse]]] = {}
    for token, use in tally.italics.items():
        by_rule.setdefault(use.rule, []).append((token, use))
    total_uses = sum(use.count for use in tally.italics.values())
    out += [
        f"Toplam {total_uses} italik belirteç, {len(tally.italics)} farklı belirteç.",
        "",
        f"**Kural 1 (tek harf → değişken)** — {len(by_rule.get('1', []))} farklı belirteç:",
        "",
        _inline(by_rule.get("1", [])),
        "",
        f"**Kural 2 (büyük/Yunan harfli ≤ 4 harf → değişken)** — "
        f"{len(by_rule.get('2', []))} farklı belirteç; yeni biri incelemede görünsün diye tek tek "
        "listelenir:",
        "",
        *_table(
            ("Belirteç", "Adet", "İlk kullanım"),
            ((f"`{t}`", u.count, f"`{u.first}`") for t, u in sorted(by_rule.get("2", []))),
        ),
        "",
        "**Kural 3 (kapalı değişken listesi → değişken)**",
        "",
    ]
    out += _table(
        ("Belirteç", "Adet", "Liste", "İlk kullanım"),
        (
            (
                f"`{token}`",
                tally.italics[token].count if token in tally.italics else 0,
                "şartname örneği" if token in SPEC_VARIABLE_WORDS else "**ek**",
                f"`{tally.italics[token].first}`" if token in tally.italics else "—",
            )
            for token in sorted(VARIABLE_WORDS)
        ),
    )
    out += ["", "**Kural 4 (kapalı sözcük listesi → italik metin)**", ""]
    out += _table(
        ("Belirteç", "Adet", "Liste", "İlk kullanım"),
        (
            (
                f"`{token}`",
                tally.italics[token].count if token in tally.italics else 0,
                "şartname örneği" if token in SPEC_ITALIC_WORDS else "**ek**",
                f"`{tally.italics[token].first}`" if token in tally.italics else "—",
            )
            for token in sorted(ITALIC_WORDS)
        ),
    )
    phrases = by_rule.get("4-phrase", [])
    out += [
        "",
        f"**Kural 4 (boşluk ya da noktalama içeren tümce → italik metin)** — "
        f"{len(phrases)} farklı tümce, {sum(use.count for _, use in phrases)} kullanım "
        "(çoğu markscheme notudur).",
        "",
    ]

    out += ["## 6. Kural ekleri", ""]
    out += [
        "IMPORT_RULES.md'nin açıkça karşılamadığı ve dönüştürücünün dar biçimde genişlettiği "
        "yerler. Her biri belgeye de işlenmelidir.",
        "",
    ]
    added_variables = [
        f"`{t}` ({tally.italics[t].count}; ilk: `{tally.italics[t].first}`)"
        for t in sorted(VARIABLE_WORDS - SPEC_VARIABLE_WORDS)
        if t in tally.italics
    ]
    added_words = [
        f"`{t}` ({tally.italics[t].count}; ilk: `{tally.italics[t].first}`)"
        for t in sorted(ITALIC_WORDS - SPEC_ITALIC_WORDS)
        if t in tally.italics
    ]
    for key, text in ADDITIONS.items():
        if key == "variable-word":
            places = added_variables
        elif key == "italic-word":
            places = added_words
        else:
            places = [f"`{place}`" for place in sorted(tally.additions.get(key, []))]
        if places:
            out += [
                f"- **{key}** — {text}",
                f"  - Gerektiği yerler ({len(places)}): " + ", ".join(places),
            ]
    out += [""]

    out += ["## 7. Yorumlar", ""]
    out += ["Kuralın birden çok okunabildiği yerlerde seçilen okuma:", ""]
    out += [f"- {text}" for text in _INTERPRETATIONS]
    out += [""]
    return "\n".join(out)

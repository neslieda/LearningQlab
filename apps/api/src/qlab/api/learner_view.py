"""The learner view of a published question, and the answer check (docs/slices/M1G-5-SOZLESME.md
section 3.3, docs/slices/M1G-5-YETKILER.md section 4).

Everything here is an allow-list: each field of a target type is read from the stored document
by name. The document is never dumped and then pruned, so a field added to the document later
stays out of the learner view until someone adds it here on purpose.
"""

from __future__ import annotations

from qlab.api import errors, ids
from qlab.api.language import looks_non_english
from qlab.api.schemas import (
    LanguageWarning,
    LearnerMcq,
    LearnerOption,
    LearnerPart,
    LearnerQuestion,
    LearnerQuestionSummary,
    LearnerStimulus,
    MarkPointOut,
    McqAnswer,
    McqCheckResult,
    NoteOut,
    WrittenAnswer,
    WrittenCheckResult,
)
from qlab.content import service as content
from qlab.content.schema import Mcq, Part

_NOT_ENGLISH = LanguageWarning(
    code="answer_not_english", message="Please write your answer in English."
)


def _does_not_fit() -> errors.ApiError:
    return errors.ApiError(422, "answer_does_not_fit", "The answer does not fit this question")


def to_learner_summary(summary: content.VersionSummary) -> LearnerQuestionSummary:
    return LearnerQuestionSummary(
        id=ids.encode(ids.QUESTION, summary.question_id),
        version_id=ids.encode(ids.QUESTION_VERSION, summary.id),
        question_class=summary.question_class,
        exam_section=summary.exam_section,
        levels=summary.levels,
        total_marks=summary.total_marks,
    )


def _mcq(mcq: Mcq) -> LearnerMcq:
    return LearnerMcq(
        option_layout=mcq.option_layout,
        column_headers=mcq.column_headers,
        statements=mcq.statements,
        options=tuple(LearnerOption(key=o.key, cells=o.cells) for o in mcq.options),
    )


def _part(part: Part) -> LearnerPart:
    return LearnerPart(
        id=part.id,
        label=part.label,
        lead_in=part.lead_in,
        body=part.body,
        marks=part.marks,
        command_term=part.command_term,
        stimulus_refs=part.stimulus_refs,
    )


def to_learner_question(view: content.QuestionVersionView) -> LearnerQuestion:
    document = view.document
    return LearnerQuestion(
        id=ids.encode(ids.QUESTION, view.question_id),
        version_id=ids.encode(ids.QUESTION_VERSION, view.id),
        question_class=document.question_class,
        exam_section=document.exam_section,
        levels=document.levels,
        total_marks=document.total_marks,
        stem=document.stem,
        stimuli=tuple(LearnerStimulus(id=s.id, kind=s.kind) for s in document.stimuli),
        mcq=_mcq(document.mcq) if document.mcq is not None else None,
        parts=tuple(_part(p) for p in document.parts),
    )


def check(
    view: content.QuestionVersionView, answer: McqAnswer | WrittenAnswer
) -> McqCheckResult | WrittenCheckResult:
    """Show the correct answer or the mark scheme of one part. Nothing is stored or marked."""
    document = view.document
    version_id = ids.encode(ids.QUESTION_VERSION, view.id)
    if isinstance(answer, McqAnswer):
        if document.mcq is None:
            raise _does_not_fit()
        return McqCheckResult(
            kind="mcq",
            version_id=version_id,
            correct=answer.selected_key == document.mcq.correct_key,
            correct_key=document.mcq.correct_key,
        )
    if document.mcq is not None:
        raise _does_not_fit()
    part = next((p for p in document.parts if p.id == answer.part_id), None)
    if part is None:
        raise _does_not_fit()
    return WrittenCheckResult(
        kind="written",
        version_id=version_id,
        part_id=part.id,
        marks=part.marks,
        marks_capped=part.marks_capped,
        mark_points=tuple(
            MarkPointOut(
                id=p.id,
                content=p.content,
                kind=p.kind,
                alternative_group=p.alternative_group,
                route=p.route,
                accept_range=p.accept_range,
            )
            for p in part.mark_points
        ),
        notes=tuple(
            NoteOut(kind=n.kind, content=n.content, mark_point_id=n.mark_point_id)
            for n in part.notes
        ),
        language_warning=_NOT_ENGLISH if looks_non_english(answer.text) else None,
    )

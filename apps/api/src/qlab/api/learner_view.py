"""The learner view of a published question, and the answer check (docs/slices/M1G-5-SOZLESME.md
section 3.3, docs/slices/M1G-5-YETKILER.md section 4).

Everything here is an allow-list: each field of a target type is read from the stored document
by name. The document is never dumped and then pruned, so a field added to the document later
stays out of the learner view until someone adds it here on purpose.
"""

from __future__ import annotations

from qlab.api import ids
from qlab.api.schemas import (
    LearnerMcq,
    LearnerOption,
    LearnerPart,
    LearnerQuestion,
    LearnerQuestionSummary,
    LearnerStimulus,
    TopicOut,
)
from qlab.content import service as content
from qlab.content.schema import Mcq, Part


def _topic(topic: tuple[str, str]) -> TopicOut:
    return TopicOut(code=topic[0], title=topic[1])


def to_learner_summary(
    summary: content.VersionSummary, *, topic: tuple[str, str], answered: bool
) -> LearnerQuestionSummary:
    return LearnerQuestionSummary(
        id=ids.encode(ids.QUESTION, summary.question_id),
        version_id=ids.encode(ids.QUESTION_VERSION, summary.id),
        question_class=summary.question_class,
        exam_section=summary.exam_section,
        levels=summary.levels,
        total_marks=summary.total_marks,
        topic=_topic(topic),
        answered=answered,
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


def to_learner_question(
    view: content.QuestionVersionView, *, topic: tuple[str, str], answered: bool
) -> LearnerQuestion:
    document = view.document
    return LearnerQuestion(
        id=ids.encode(ids.QUESTION, view.question_id),
        version_id=ids.encode(ids.QUESTION_VERSION, view.id),
        question_class=document.question_class,
        exam_section=document.exam_section,
        levels=document.levels,
        total_marks=document.total_marks,
        topic=_topic(topic),
        answered=answered,
        stem=document.stem,
        stimuli=tuple(LearnerStimulus(id=s.id, kind=s.kind) for s in document.stimuli),
        mcq=_mcq(document.mcq) if document.mcq is not None else None,
        parts=tuple(_part(p) for p in document.parts),
    )

"""Smoke tests written with the schema. The acceptance suite lives in test_question_schema.py."""

from typing import Any

import pytest

from qlab.content.schema import QuestionDocument
from tests.content.samples import data_based_document, mcq_document, structured_document

SAMPLES = [mcq_document, structured_document, data_based_document]


@pytest.mark.parametrize("sample", SAMPLES)
def test_samples_validate_and_round_trip(sample: Any) -> None:
    document = QuestionDocument.model_validate(sample())
    dumped = document.model_dump_json()
    assert QuestionDocument.model_validate_json(dumped).model_dump_json() == dumped

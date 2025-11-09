import os
from pathlib import Path

from src.generators.services.baseline_initializer import BaselineInitializer
from src.generators.services.verification_service import VerificationService


def test_baseline_initializer_creates_missing(tmp_path: Path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "\n".join([
            "number_of_companies: 3",
            "seed: 42",
            "company_onboarding_interval: PT30M",
            "drivers_per_company: 1",
            "event_rate_per_driver: 1"
        ]) + "\n"
    )
    companies = tmp_path / "companies.jsonl"
    events = tmp_path / "events"
    init = BaselineInitializer(str(cfg), str(companies), str(events))
    result = init.ensure_baseline()
    assert result.companies_created == 3
    assert result.driver_batches_created == 1
    assert companies.exists() and companies.stat().st_size > 0
    assert events.exists() and any(events.iterdir())


def test_verification_service_reports_missing(tmp_path: Path):
    companies = tmp_path / "companies.jsonl"  # not created
    events = tmp_path / "events"  # not created
    verifier = VerificationService(str(companies), str(events))
    report = verifier.verify()
    assert not report.companies_exists
    assert not report.events_exists
    assert str(companies) in report.missing
    assert str(events) in report.missing


def test_verification_service_reports_existing(tmp_path: Path):
    companies = tmp_path / "companies.jsonl"
    companies.write_text("{\n}")
    events = tmp_path / "events"
    events.mkdir()
    (events / "batch_meta.json").write_text("{}")
    verifier = VerificationService(str(companies), str(events))
    report = verifier.verify()
    assert report.companies_exists
    assert report.events_exists
    assert report.event_file_count >= 1
    assert not report.missing
"""Health read-only handler registration."""

from __future__ import annotations

from flask import jsonify

from src.generators.services.health_aggregator import HealthAggregator
from src.generators.services.verification_service import VerificationService


def register_health(bp, health_agg: HealthAggregator, verifier: VerificationService):
    @bp.get('/health')
    def health():  # type: ignore
        report = verifier.verify()
        snap = health_agg.aggregate(verification={
            'companies_exists': report.companies_exists,
            'events_exists': report.events_exists,
            'missing': report.missing,
            'event_file_count': report.event_file_count,
        })
        return jsonify(snap.__dict__)

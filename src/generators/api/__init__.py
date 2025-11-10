"""API blueprint factory composing individual handler registrations."""

from __future__ import annotations

from flask import Blueprint

from src.generators.lifecycle import GeneratorLifecycle
from src.generators.services.baseline_initializer import BaselineInitializer
from src.generators.services.verification_service import VerificationService
from src.generators.services.lifecycle_service import LifecycleCommandService
from src.generators.services.health_aggregator import HealthAggregator
from src.generators.services.log_reader import LogReaderService

from .health import register_health
from .lifecycle import register_lifecycle
from .data_reset import register_data_reset
from .logs import register_logs


def create_api_blueprint(
    lifecycle: GeneratorLifecycle,
    config_path: str,
    companies_file: str,
    events_dir: str,
    state_file: str,
    logs_root: str,
) -> Blueprint:
    bp = Blueprint("api", __name__)
    lifecycle_service = LifecycleCommandService(lifecycle)
    baseline = BaselineInitializer(config_path, companies_file, events_dir)
    verifier = VerificationService(companies_file, events_dir)
    health_agg = HealthAggregator(lifecycle, state_file, config_path)
    log_reader = LogReaderService(logs_root)

    register_health(bp, health_agg, verifier)
    register_lifecycle(bp, lifecycle_service, baseline, verifier)
    register_data_reset(bp, lifecycle)
    register_logs(bp, log_reader)
    return bp

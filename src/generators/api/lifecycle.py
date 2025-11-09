"""Lifecycle (pause/resume) handlers."""

from __future__ import annotations

from flask import jsonify

from src.generators.services.lifecycle_service import LifecycleCommandService
from src.generators.services.baseline_initializer import BaselineInitializer
from src.generators.services.verification_service import VerificationService


def register_lifecycle(bp, lifecycle_service: LifecycleCommandService, baseline: BaselineInitializer, verifier: VerificationService):
    @bp.post('/pause')
    def pause():  # type: ignore
        result = lifecycle_service.pause()
        return jsonify(result.__dict__)

    @bp.post('/resume')
    def resume():  # type: ignore
        result = lifecycle_service.resume()
        if result.status == 'running' and result.success:
            init = baseline.ensure_baseline()
            verify = verifier.verify()
            result.extra = {
                'baseline_actions': init.actions,
                'baseline_errors': init.errors,
                'verification_missing': verify.missing,
            }
        return jsonify(result.__dict__)

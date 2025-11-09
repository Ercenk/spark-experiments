"""Data reset handler."""

from __future__ import annotations

from pathlib import Path
import shutil
from flask import jsonify

from src.generators.lifecycle import GeneratorLifecycle


def register_data_reset(bp, lifecycle: GeneratorLifecycle):
    @bp.post('/clean')
    def clean():  # type: ignore
        if not lifecycle.paused:
            return jsonify({'success': False, 'error': 'pause_required'}), 400
        base_dir = Path('data')
        manifests = base_dir / 'manifests'
        raw_dir = base_dir / 'raw'
        targets = [
            raw_dir / 'companies.jsonl',
            raw_dir / 'events',
            manifests / 'seed_manifest.json',
            manifests / 'batch_manifest.json',
            manifests / 'generator_state.json',
        ]
        deleted = 0
        errors = []
        for p in targets:
            if not p.exists():
                continue
            try:
                if p.is_file():
                    p.unlink()
                else:
                    shutil.rmtree(p)
                deleted += 1
            except Exception as e:  # pragma: no cover
                errors.append(str(e))
        raw_dir.mkdir(parents=True, exist_ok=True)
        (base_dir / 'staged').mkdir(parents=True, exist_ok=True)
        (base_dir / 'processed').mkdir(parents=True, exist_ok=True)
        return jsonify({
            'success': len(errors) == 0,
            'deleted_count': deleted,
            'errors': errors,
        })

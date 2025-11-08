"""Coordination utilities for ensuring data consistency across generators."""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from src.generators.models import Company


def get_onboarded_companies_before(timestamp: datetime, companies_file: str) -> List[str]:
    """
    Get list of company IDs that were onboarded before the given timestamp.
    
    This ensures driver event batches only reference companies that existed
    before the interval started, maintaining referential integrity.
    
    Args:
        timestamp: Cutoff timestamp (typically interval_start for a batch)
        companies_file: Path to companies.jsonl file
        
    Returns:
        List of company_id strings that were created before timestamp
        
    Note:
        Returns empty list if companies_file does not exist (no companies yet).
    """
    companies_path = Path(companies_file)
    
    if not companies_path.exists():
        return []
    
    eligible_company_ids = []
    
    with open(companies_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                company_data = json.loads(line)
                company = Company(**company_data)
                
                # Check if company was created before cutoff
                if company.created_at < timestamp:
                    eligible_company_ids.append(company.company_id)
            except (json.JSONDecodeError, ValueError) as e:
                # Skip invalid lines (log warning in production)
                continue
    
    return eligible_company_ids

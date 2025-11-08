"""Base generator abstract class for common functionality."""

from abc import ABC, abstractmethod
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

from src.generators.config import Config
from src.logging.json_logger import JSONLogger
from src.util.seed import generate_or_load_seed


class BaseGenerator(ABC):
    """
    Abstract base class for data generators.
    
    Provides common functionality:
    - Configuration loading
    - Logging setup
    - Seed management
    - Manifest writing
    """
    
    def __init__(self):
        """Initialize base generator."""
        self.config: Optional[Config] = None
        self.logger: Optional[JSONLogger] = None
        self.seed: Optional[int] = None
        self.run_id: str = str(uuid.uuid4())
    
    def load_config(self, config_path: str) -> Config:
        """
        Load and validate configuration from YAML or JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Validated Config instance
            
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config validation fails
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Load based on extension
        with open(config_file, 'r') as f:
            if config_file.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif config_file.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {config_file.suffix}")
        
        self.config = Config(**data)
        return self.config
    
    def setup_logging(self, component: str, log_file: Optional[str] = None) -> JSONLogger:
        """
        Setup structured JSON logging.
        
        Args:
            component: Component name for log entries
            log_file: Optional log file path
            
        Returns:
            JSONLogger instance
        """
        self.logger = JSONLogger(component=component, run_id=self.run_id, log_file=log_file)
        return self.logger
    
    def get_seed(self, manifest_path: str, provided_seed: Optional[int] = None) -> int:
        """
        Get or generate seed for reproducibility.
        
        Args:
            manifest_path: Path to seed manifest file
            provided_seed: Optional explicit seed
            
        Returns:
            Seed value to use
        """
        self.seed = generate_or_load_seed(manifest_path, provided_seed)
        return self.seed
    
    def write_manifest(self, manifest_path: str, batch_meta: Dict[str, Any]) -> None:
        """
        Write batch metadata to manifest file.
        
        Args:
            manifest_path: Path to manifest file
            batch_meta: Metadata dictionary to write
        """
        manifest_file = Path(manifest_path)
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_file, 'w') as f:
            json.dump(batch_meta, f, indent=2, default=str)
    
    @abstractmethod
    def generate(self, *args, **kwargs):
        """
        Abstract method for generation logic.
        
        Subclasses must implement this method.
        """
        pass

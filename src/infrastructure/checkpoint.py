"""Checkpoint management for resilient extraction."""
import json
from pathlib import Path
from typing import Optional, Set
from datetime import datetime
from loguru import logger


class CheckpointManager:
    """Manages extraction checkpoints for recovery and deduplication."""
    
    def __init__(self, checkpoint_dir: str = "./checkpoints") -> None:
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)
    
    def _get_checkpoint_file(self, uf: str) -> Path:
        """Get checkpoint file path for a state."""
        return self.checkpoint_dir / f"{uf.upper()}_checkpoint.json"
    
    def load_checkpoint(self, uf: str) -> Set[str]:
        """
        Load processed municipalities for a state.
        
        Returns a set of municipality names that have been successfully processed.
        """
        checkpoint_file = self._get_checkpoint_file(uf)
        
        if not checkpoint_file.exists():
            logger.info(f"No checkpoint found for {uf}, starting fresh")
            return set()
        
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                processed = set(data.get("processed_municipios", []))
                logger.info(
                    f"Loaded checkpoint for {uf}",
                    processed_count=len(processed),
                    last_update=data.get("last_update"),
                )
                return processed
        except Exception as e:
            logger.error(f"Failed to load checkpoint for {uf}: {e}")
            return set()
    
    def save_checkpoint(
        self, 
        uf: str, 
        processed_municipios: Set[str],
        total_municipios: Optional[int] = None,
    ) -> None:
        """
        Save checkpoint for a state.
        
        Args:
            uf: State abbreviation
            processed_municipios: Set of successfully processed municipalities
            total_municipios: Total number of municipalities (optional)
        """
        checkpoint_file = self._get_checkpoint_file(uf)
        
        data = {
            "uf": uf.upper(),
            "processed_municipios": sorted(list(processed_municipios)),
            "total_municipios": total_municipios,
            "processed_count": len(processed_municipios),
            "last_update": datetime.utcnow().isoformat(),
        }
        
        try:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(
                f"Checkpoint saved for {uf}",
                processed_count=len(processed_municipios),
                total=total_municipios,
            )
        except Exception as e:
            logger.error(f"Failed to save checkpoint for {uf}: {e}")
    
    def add_processed_municipio(self, uf: str, municipio: str) -> None:
        """
        Add a municipality to the processed list.
        
        This is atomic - loads current checkpoint, adds municipality, saves back.
        """
        processed = self.load_checkpoint(uf)
        processed.add(municipio)
        self.save_checkpoint(uf, processed)
    
    def is_processed(self, uf: str, municipio: str) -> bool:
        """Check if a municipality has been processed."""
        processed = self.load_checkpoint(uf)
        return municipio in processed
    
    def clear_checkpoint(self, uf: str) -> None:
        """Clear checkpoint for a state (for reprocessing)."""
        checkpoint_file = self._get_checkpoint_file(uf)
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.info(f"Checkpoint cleared for {uf}")
    
    def get_progress(self, uf: str) -> dict:
        """Get progress statistics for a state."""
        checkpoint_file = self._get_checkpoint_file(uf)
        
        if not checkpoint_file.exists():
            return {
                "uf": uf.upper(),
                "processed_count": 0,
                "total_municipios": None,
                "progress_pct": 0.0,
            }
        
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        processed = data.get("processed_count", 0)
        total = data.get("total_municipios")
        
        return {
            "uf": uf.upper(),
            "processed_count": processed,
            "total_municipios": total,
            "progress_pct": (processed / total * 100) if total else 0.0,
            "last_update": data.get("last_update"),
        }

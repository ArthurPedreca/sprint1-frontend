"""
Modelo de domínio do Equipamento.

Camada de modelo desacoplada de qualquer framework de UI ou de persistência.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Equipamento:
    """Representa um ativo industrial monitorado."""

    # Identificação
    tag: str
    modelo: str
    fabricante: str
    tipo: str

    # Características elétricas/mecânicas (placa do motor)
    potencia_kw: float
    tensao_v: float
    corrente_nominal_a: float
    rotacao_nominal_rpm: int
    frequencia_hz: float

    # Informações complementares
    numero_serie: str = ""
    localizacao: str = ""
    data_instalacao: str = ""   # ISO date string (YYYY-MM-DD)
    status: str = "Ativo"
    observacoes: str = ""

    # Metadados (gerados automaticamente)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    criado_em: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    atualizado_em: Optional[str] = None

    # ----------------------------------------------------------------------- #
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Equipamento":
        # Aceita dicionários que possam conter chaves extras sem quebrar
        valid_keys = {f for f in cls.__dataclass_fields__.keys()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

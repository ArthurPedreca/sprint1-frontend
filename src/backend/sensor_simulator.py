"""
Simulador de sensores.

No Sprint 1 ainda não temos hardware real entregando dados, então este
módulo gera leituras "brutas" (valores ADC 12-bit, 0-4095) que mimetizam
o que viria de um CLP / microcontrolador via Modbus, MQTT, OPC-UA etc.

Em sprints futuros, este módulo será substituído por um adaptador que
consome dados reais sem mudar a interface (`gerar_amostras`).
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List

from src.backend.models import Equipamento
from src.config.settings import ADC_RESOLUTION


class SensorSimulator:
    """Gera leituras brutas simuladas de sensores."""

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

    # ----------------------------------------------------------------------- #
    def gerar_amostras(
        self,
        equipamento: Equipamento,
        n_amostras: int = 60,
        intervalo_segundos: int = 1,
    ) -> List[Dict]:
        """
        Retorna uma lista de leituras brutas no formato:

            { "timestamp": iso_str,
              "tensao_raw": int (0-4095),
              "corrente_raw": int (0-4095),
              "rpm_raw": int (0-4095),
              "temperatura_raw": int (0-4095),
              "vibracao_raw": int (0-4095) }
        """
        amostras: List[Dict] = []
        agora = datetime.now()

        # Pequena variação determinística (ciclo lento) + ruído gaussiano
        for i in range(n_amostras):
            ts = agora - timedelta(seconds=intervalo_segundos * (n_amostras - i))

            ruido = random.gauss(0, 0.015)
            ciclo = math.sin(i * 0.18) * 0.04

            # Tensão -> raw representa percentual da nominal (0.95-1.05 da nominal)
            tensao_pct = 1.0 + ruido + ciclo
            tensao_raw = self._mapear_pct(tensao_pct, fator=0.5)

            # Corrente -> motor operando ~70% da carga nominal com flutuações
            corrente_pct = 0.7 + ruido + ciclo
            corrente_raw = self._mapear_pct(corrente_pct, fator=0.5)

            # RPM -> próximo da nominal
            rpm_pct = 1.0 + ruido * 0.4
            rpm_raw = self._mapear_pct(rpm_pct, fator=0.5)

            # Temperatura -> ~65 °C com leve oscilação (faixa 0-150 °C)
            temp_c = 65 + ruido * 6 + ciclo * 12
            temp_raw = int((max(0, temp_c) / 150.0) * ADC_RESOLUTION)

            # Vibração -> ~2.5 mm/s, faixa 0-10 mm/s
            vib_mms = 2.5 + abs(ruido) * 2.5 + abs(ciclo)
            vib_raw = int((min(10, vib_mms) / 10.0) * ADC_RESOLUTION)

            amostras.append(
                {
                    "timestamp": ts.isoformat(timespec="seconds"),
                    "tensao_raw": tensao_raw,
                    "corrente_raw": corrente_raw,
                    "rpm_raw": rpm_raw,
                    "temperatura_raw": temp_raw,
                    "vibracao_raw": vib_raw,
                }
            )

        return amostras

    # ----------------------------------------------------------------------- #
    @staticmethod
    def _mapear_pct(pct: float, fator: float = 0.5) -> int:
        """
        Mapeia um percentual (esperado próximo de 1.0) em um valor ADC.
        `fator=0.5` faz com que pct=1.0 corresponda à metade do range (~2047),
        deixando margem para subir e descer sem saturar.
        """
        valor = int(pct * fator * ADC_RESOLUTION)
        return max(0, min(ADC_RESOLUTION, valor))

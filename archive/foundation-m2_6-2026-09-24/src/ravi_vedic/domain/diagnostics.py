from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import TypeAlias

from ravi_vedic.domain.identity import RuntimeIdentity

DiagnosticDetailValue: TypeAlias = str | int | float | bool | None

CANONICAL_SOURCE_PROFILE = "canonical-strict-swiss-files"
DEVELOPMENT_SOURCE_PROFILE = "development-allow-moshier"


class DiagnosticSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DiagnosticLayer(StrEnum):
    INPUT = "input"
    TIME = "time"
    RUNTIME = "runtime"
    ASTRONOMY = "astronomy"
    POLICY = "policy"
    PROJECTION = "projection"


class CanonicalityImpact(StrEnum):
    NONE = "none"
    DEVELOPMENT = "development"
    DEGRADED = "degraded"


class CalculationStatus(StrEnum):
    CANONICAL = "canonical"
    DEVELOPMENT = "development"
    DEGRADED = "degraded"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    severity: DiagnosticSeverity
    layer: DiagnosticLayer
    affected_fields: tuple[str, ...]
    canonicality_impact: CanonicalityImpact
    details: Mapping[str, DiagnosticDetailValue]

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code or self.code.strip() != self.code:
            raise ValueError("diagnostic code must be a non-empty canonical string")

        object.__setattr__(self, "severity", DiagnosticSeverity(self.severity))
        object.__setattr__(self, "layer", DiagnosticLayer(self.layer))
        object.__setattr__(
            self,
            "canonicality_impact",
            CanonicalityImpact(self.canonicality_impact),
        )

        fields = tuple(self.affected_fields)
        if any(
            not isinstance(field, str) or not field or field.strip() != field
            for field in fields
        ):
            raise ValueError("diagnostic affected_fields must contain canonical strings")
        if len(set(fields)) != len(fields):
            raise ValueError("diagnostic affected_fields must not contain duplicates")
        object.__setattr__(self, "affected_fields", fields)

        if not isinstance(self.details, Mapping):
            raise TypeError("diagnostic details must be a mapping")
        detached: dict[str, DiagnosticDetailValue] = {}
        for key, value in self.details.items():
            if not isinstance(key, str) or not key or key.strip() != key:
                raise ValueError("diagnostic detail keys must be canonical strings")
            if value is not None and not isinstance(value, (str, int, float, bool)):
                raise TypeError("diagnostic detail values must be JSON scalars or null")
            if isinstance(value, float) and not isfinite(value):
                raise ValueError("diagnostic float details must be finite")
            detached[key] = value
        object.__setattr__(self, "details", MappingProxyType(detached))


def derive_calculation_status(
    runtime_identity: RuntimeIdentity,
    diagnostics: tuple[Diagnostic, ...],
) -> CalculationStatus:
    if any(
        diagnostic.severity == DiagnosticSeverity.ERROR
        or diagnostic.canonicality_impact == CanonicalityImpact.DEGRADED
        for diagnostic in diagnostics
    ):
        return CalculationStatus.DEGRADED

    if runtime_identity.source_profile == DEVELOPMENT_SOURCE_PROFILE:
        return CalculationStatus.DEVELOPMENT

    if runtime_identity.source_profile != CANONICAL_SOURCE_PROFILE:
        return CalculationStatus.DEGRADED

    if any(
        diagnostic.canonicality_impact == CanonicalityImpact.DEVELOPMENT
        for diagnostic in diagnostics
    ):
        return CalculationStatus.DEVELOPMENT

    return CalculationStatus.CANONICAL


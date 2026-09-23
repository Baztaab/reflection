from dataclasses import FrozenInstanceError

import pytest

from ravi_vedic.domain.diagnostics import (
    CalculationStatus,
    CanonicalityImpact,
    Diagnostic,
    DiagnosticLayer,
    DiagnosticSeverity,
    derive_calculation_status,
    legacy_warning_string,
)
from ravi_vedic.domain.identity import (
    AstronomyRuntimeIdentity,
    PythonRuntimeIdentity,
    RaviBuildIdentity,
    RuntimeIdentity,
    TimezoneRuntimeIdentity,
)


def _runtime(source_profile: str) -> RuntimeIdentity:
    return RuntimeIdentity(
        ravi=RaviBuildIdentity(
            distribution_name="ravi-vedic",
            package_version="test",
            source_sha256="0" * 64,
        ),
        python=PythonRuntimeIdentity(
            implementation="test-python",
            version="test",
            system="test-system",
            machine="test-machine",
        ),
        astronomy=AstronomyRuntimeIdentity(
            implementation="fake",
            binding_version="test",
            library_version="test",
            ephemeris_manifest_sha256=None,
            ephemeris_file_count=0,
        ),
        timezone=TimezoneRuntimeIdentity(provider="fake", version="test"),
        source_profile=source_profile,
    )


def _diagnostic(
    *,
    impact: CanonicalityImpact = CanonicalityImpact.NONE,
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING,
) -> Diagnostic:
    return Diagnostic(
        code="TEST_DIAGNOSTIC",
        severity=severity,
        layer=DiagnosticLayer.ASTRONOMY,
        affected_fields=("astronomy.bodies.sun",),
        canonicality_impact=impact,
        details={"reason": "test"},
    )


def test_diagnostic_detaches_mutable_inputs_and_is_frozen():
    fields = ["astronomy.bodies.sun"]
    details = {"source": "moshier"}
    diagnostic = Diagnostic(
        code="EPHEMERIS_SOURCE_FALLBACK",
        severity="warning",
        layer="astronomy",
        affected_fields=fields,
        canonicality_impact="development",
        details=details,
    )

    fields.append("mutated")
    details["source"] = "mutated"

    assert diagnostic.affected_fields == ("astronomy.bodies.sun",)
    assert diagnostic.details["source"] == "moshier"
    assert diagnostic.severity == DiagnosticSeverity.WARNING
    assert diagnostic.layer == DiagnosticLayer.ASTRONOMY
    assert diagnostic.canonicality_impact == CanonicalityImpact.DEVELOPMENT
    with pytest.raises(TypeError):
        diagnostic.details["source"] = "changed"
    with pytest.raises(FrozenInstanceError):
        diagnostic.code = "CHANGED"


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_diagnostic_rejects_nonfinite_float_details(bad):
    with pytest.raises(ValueError, match="finite"):
        Diagnostic(
            code="BAD_FLOAT",
            severity=DiagnosticSeverity.WARNING,
            layer=DiagnosticLayer.RUNTIME,
            affected_fields=("runtime",),
            canonicality_impact=CanonicalityImpact.NONE,
            details={"value": bad},
        )


def test_status_is_canonical_only_for_strict_profile_without_degradation():
    assert (
        derive_calculation_status(_runtime("canonical-strict-swiss-files"), ())
        == CalculationStatus.CANONICAL
    )


def test_development_profile_is_explicit_even_without_diagnostics():
    assert (
        derive_calculation_status(_runtime("development-allow-moshier"), ())
        == CalculationStatus.DEVELOPMENT
    )


def test_degraded_impact_overrides_profile():
    diagnostic = _diagnostic(impact=CanonicalityImpact.DEGRADED)
    assert (
        derive_calculation_status(
            _runtime("canonical-strict-swiss-files"),
            (diagnostic,),
        )
        == CalculationStatus.DEGRADED
    )


def test_error_severity_is_always_degraded():
    diagnostic = _diagnostic(
        impact=CanonicalityImpact.NONE,
        severity=DiagnosticSeverity.ERROR,
    )
    assert (
        derive_calculation_status(
            _runtime("canonical-strict-swiss-files"),
            (diagnostic,),
        )
        == CalculationStatus.DEGRADED
    )


def test_unknown_source_profile_cannot_be_mistaken_for_canonical():
    assert derive_calculation_status(_runtime("test-only"), ()) == CalculationStatus.DEGRADED


def test_legacy_warning_encoding_is_projection_compatibility_only():
    diagnostic = Diagnostic(
        code="EPHEMERIS_SOURCE_FALLBACK",
        severity=DiagnosticSeverity.WARNING,
        layer=DiagnosticLayer.ASTRONOMY,
        affected_fields=("astronomy.bodies",),
        canonicality_impact=CanonicalityImpact.DEVELOPMENT,
        details={"source": "moshier"},
    )
    assert legacy_warning_string(diagnostic) == "EPHEMERIS_SOURCE_FALLBACK:moshier"

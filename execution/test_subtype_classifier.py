"""
Test Subtype Classifier & Enhanced Risk Scorer
Classifies tests into subtypes for more precise risk scoring.
Examples:
  - BVA-PaymentBoundaries (90% risk)
  - BVA-StringBoundaries (60% risk)
  - ECP-CrossField (75% risk)
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class TestSubtype:
    """Classification of a test by its subtype"""
    test_type: str  # BVA, ECP, etc.
    subtype: str  # payment_boundaries, cross_field, etc.
    confidence: float  # 0.0-1.0: how confident we are about this classification
    base_risk: float  # Base risk for this subtype
    indicators: List[str]  # Why we classified it this way


class TestSubtypeClassifier:
    """
    Detects which subtype a test belongs to based on:
    - Test data values (boundaries, special chars, etc.)
    - Form fields (field types, names)
    - Expected results
    - Patterns in test case structure
    """
    
    # Test subtype -> base failure risk
    SUBTYPE_RISK = {
        # BVA Subtypes
        "bva_payment_boundaries": 0.90,
        "bva_file_boundaries": 0.85,
        "bva_numeric_boundaries": 0.70,
        "bva_string_boundaries": 0.60,
        "bva_date_boundaries": 0.55,
        
        # ECP Subtypes
        "ecp_cross_field": 0.75,
        "ecp_invalid_partition": 0.65,
        "ecp_boundary_partition": 0.60,
        "ecp_statistical_partition": 0.45,
        "ecp_valid_partition": 0.30,
        
        # StateTransition Subtypes
        "state_invalid_transition": 0.80,
        "state_concurrent_changes": 0.75,
        "state_error_recovery": 0.70,
        "state_conditional": 0.60,
        "state_sequential": 0.40,
        
        # DecisionTable Subtypes
        "dt_edge_combination": 0.85,
        "dt_all_combination": 0.70,
        "dt_three_way": 0.65,
        "dt_orthogonal": 0.55,
        "dt_pairwise": 0.45,
        
        # UseCase Subtypes
        "uc_exception_path": 0.70,
        "uc_complex_flow": 0.65,
        "uc_alternative_path": 0.45,
        "uc_accessibility": 0.50,
        "uc_happy_path": 0.25,
    }
    
    # Keywords that indicate specific subtypes
    PAYMENT_KEYWORDS = {"credit_card", "cvv", "card", "payment", "amount", "price", "checkout"}
    FILE_KEYWORDS = {"file", "upload", "document", "attachment", "image", "csv"}
    DATE_KEYWORDS = {"date", "time", "birthday", "scheduled", "deadline", "timestamp"}
    PASSWORD_KEYWORDS = {"password", "pwd", "secret", "passphrase", "pin"}
    EMAIL_KEYWORDS = {"email", "mail", "address", "contact"}
    PHONE_KEYWORDS = {"phone", "tel", "number", "mobile", "cell"}
    
    BOUNDARY_VALUES = {"", None, 0, -1, 1, 999999, 2147483647, -2147483648, float("inf")}
    INVALID_CHARS = {"<", ">", "'", '"', "\\", ";", "--", "/*", "*/", "${", "#{"}
    
    def classify(self, test_case: Dict) -> TestSubtype:
        """
        Classify a test case into its subtype.
        
        Args:
            test_case: Dict with keys: type, test_data, form, expected_result, etc.
        
        Returns:
            TestSubtype with classification details
        """
        test_type = test_case.get("type", "UseCase").upper()
        test_data = test_case.get("test_data", {})
        form = test_case.get("form", {})
        expected = test_case.get("expected_result", "").lower()
        
        indicators = []
        
        # Route to appropriate classifier
        if test_type == "BVA":
            subtype, conf, inds = self._classify_bva(test_data, form, expected)
        elif test_type == "ECP":
            subtype, conf, inds = self._classify_ecp(test_data, form, expected)
        elif test_type == "STATETRANSITION":
            subtype, conf, inds = self._classify_state_transition(test_data, form, expected)
        elif test_type == "DECISIONTABLE":
            subtype, conf, inds = self._classify_decision_table(test_data, form, expected)
        elif test_type == "USECASE":
            subtype, conf, inds = self._classify_usecase(test_data, form, expected)
        else:
            subtype = "unknown"
            conf = 0.5
            inds = ["Unknown test type"]
        
        # Construct full subtype name
        full_subtype = f"{test_type.lower()}_{subtype}" if subtype != "unknown" else "unknown"
        base_risk = self.SUBTYPE_RISK.get(full_subtype, 0.5)
        
        return TestSubtype(
            test_type=test_type,
            subtype=subtype,
            confidence=conf,
            base_risk=base_risk,
            indicators=inds,
        )
    
    def _classify_bva(self, test_data: Dict, form: Dict, expected: str) -> Tuple[str, float, List[str]]:
        """Classify BVA tests into subtypes"""
        indicators = []
        
        # Check for payment-related fields
        if self._contains_keywords(test_data, form, self.PAYMENT_KEYWORDS):
            indicators.append("Payment field detected (credit card, cvv, amount)")
            return "payment_boundaries", 0.95, indicators
        
        # Check for file uploads
        if self._has_file_field(form):
            indicators.append("File upload field detected")
            return "file_boundaries", 0.90, indicators
        
        # Check for date fields
        if self._contains_keywords(test_data, form, self.DATE_KEYWORDS):
            indicators.append("Date field detected")
            boundary_vals = self._has_boundary_values(test_data)
            if boundary_vals:
                indicators.extend(boundary_vals)
            return "date_boundaries", 0.80, indicators
        
        # Check for string boundaries (empty, very long, special chars)
        string_indicators = self._is_string_boundary(test_data, form)
        if string_indicators:
            indicators.extend(string_indicators)
            return "string_boundaries", 0.85, indicators
        
        # Check for numeric boundaries
        numeric_indicators = self._is_numeric_boundary(test_data, form)
        if numeric_indicators:
            indicators.extend(numeric_indicators)
            return "numeric_boundaries", 0.85, indicators
        
        # Default to numeric if unclear
        return "numeric_boundaries", 0.50, ["Generic BVA test"]
    
    def _classify_ecp(self, test_data: Dict, form: Dict, expected: str) -> Tuple[str, float, List[str]]:
        """Classify ECP tests into subtypes"""
        indicators = []
        
        # Check for error conditions (invalid partition)
        if "error" in expected or "invalid" in expected or "fail" in expected:
            indicators.append(f"Expected result indicates error: {expected}")
            return "invalid_partition", 0.90, indicators
        
        # Check for cross-field dependencies
        form_fields = form.get("fields", [])
        if self._has_cross_field_dependencies(form_fields):
            indicators.append("Form has cross-field dependencies (password confirmation, etc.)")
            return "cross_field", 0.85, indicators
        
        # Check if at boundaries
        if self._at_boundary(test_data):
            indicators.append("Values at partition boundaries")
            return "boundary_partition", 0.80, indicators
        
        # Check for statistical distribution
        if self._is_statistical_extreme(test_data):
            indicators.append("Statistical extreme values (very rare/common)")
            return "statistical_partition", 0.70, indicators
        
        # Check for valid partition
        if self._all_valid_values(test_data, form):
            indicators.append("All values in valid partition")
            return "valid_partition", 0.80, indicators
        
        return "valid_partition", 0.50, ["Generic ECP test"]
    
    def _classify_state_transition(self, test_data: Dict, form: Dict, expected: str) -> Tuple[str, float, List[str]]:
        """Classify StateTransition tests into subtypes"""
        indicators = []
        
        # Check for invalid transitions (skip steps, go back, etc.)
        if "skip" in str(test_data).lower() or "back" in str(test_data).lower():
            indicators.append("Test involves skipping or revisiting steps")
            return "invalid_transition", 0.90, indicators
        
        # Check for error recovery
        if "error" in expected or "recover" in expected or "retry" in expected:
            indicators.append("Test involves error recovery")
            return "error_recovery", 0.85, indicators
        
        # Check for conditional logic
        if form.get("has_conditional_fields") or "if" in str(test_data).lower():
            indicators.append("Form has conditional state transitions")
            return "conditional", 0.75, indicators
        
        # Check for concurrent changes
        if len(test_data) > 5:  # Many fields changing at once
            indicators.append("Multiple simultaneous field changes")
            return "concurrent_changes", 0.80, indicators
        
        # Sequential (normal flow)
        indicators.append("Sequential step progression")
        return "sequential", 0.60, indicators
    
    def _classify_decision_table(self, test_data: Dict, form: Dict, expected: str) -> Tuple[str, float, List[str]]:
        """Classify DecisionTable tests into subtypes"""
        indicators = []
        num_fields = len(form.get("fields", []))
        num_values = len(test_data)
        
        # Edge combinations (multiple boundaries)
        edge_count = sum(1 for v in test_data.values() if v in self.BOUNDARY_VALUES or self._is_edge_value(v))
        if edge_count >= 2:
            indicators.append(f"Multiple edge case values ({edge_count} fields)")
            return "edge_combination", 0.90, indicators
        
        # All combinations (very high coverage)
        if num_fields > 5 and num_values > 20:
            indicators.append(f"High coverage test ({num_fields} fields, {num_values} values)")
            return "all_combination", 0.80, indicators
        
        # 3-way interactions
        if num_fields == 3 or num_values == 3:
            indicators.append(f"Three-way interaction test")
            return "three_way", 0.75, indicators
        
        # Pairwise
        if num_fields <= 2:
            indicators.append("Pairwise interaction test")
            return "pairwise", 0.60, indicators
        
        # Default to orthogonal
        indicators.append("Orthogonal array test")
        return "orthogonal", 0.65, indicators
    
    def _classify_usecase(self, test_data: Dict, form: Dict, expected: str) -> Tuple[str, float, List[str]]:
        """Classify UseCase tests into subtypes"""
        indicators = []
        
        # Exception path (error handling)
        if "error" in expected or "invalid" in expected or "should not" in expected:
            indicators.append(f"Expected error/exception: {expected}")
            return "exception_path", 0.90, indicators
        
        # Complex flow (multi-step, async, etc.)
        if form.get("is_wizard") or form.get("steps", 1) > 1:
            indicators.append("Multi-step wizard or complex flow")
            return "complex_flow", 0.80, indicators
        
        # Alternative path (different but valid flow)
        if "alternative" in str(test_data).lower() or "option" in str(test_data).lower():
            indicators.append("Alternative user path/option")
            return "alternative_path", 0.70, indicators
        
        # Accessibility path
        if "keyboard" in str(test_data).lower() or "screen reader" in str(test_data).lower():
            indicators.append("Accessibility test (keyboard, screen reader, etc.)")
            return "accessibility", 0.75, indicators
        
        # Happy path (normal, all valid)
        if self._all_valid_values(test_data, form):
            indicators.append("Happy path - all valid inputs, normal flow")
            return "happy_path", 0.40, indicators
        
        return "happy_path", 0.50, ["Generic UseCase test"]
    
    # ── Helper Methods ──────────────────────────────────────────────────
    
    def _contains_keywords(self, test_data: Dict, form: Dict, keywords: set) -> bool:
        """Check if test contains any keywords"""
        field_names = {f.get("name", "").lower() for f in form.get("fields", [])}
        test_keys = {str(k).lower() for k in test_data.keys()}
        
        return bool((field_names | test_keys) & keywords)
    
    def _has_file_field(self, form: Dict) -> bool:
        """Check if form has file upload field"""
        return any(f.get("type") == "file" for f in form.get("fields", []))
    
    def _has_boundary_values(self, test_data: Dict) -> List[str]:
        """Check for boundary values and return indicators"""
        indicators = []
        for key, value in test_data.items():
            if value in ("", None, 0, -1, 999999):
                indicators.append(f"Boundary value: {key}={value}")
        return indicators
    
    def _is_string_boundary(self, test_data: Dict, form: Dict) -> List[str]:
        """Check for string boundary tests"""
        indicators = []
        
        for key, value in test_data.items():
            if isinstance(value, str):
                if value == "":
                    indicators.append("Empty string test")
                elif len(value) == 1:
                    indicators.append("Single character test")
                elif len(value) > 1000:
                    indicators.append("Very long string test")
                elif any(c in value for c in self.INVALID_CHARS):
                    indicators.append("Special/invalid characters test")
        
        return indicators
    
    def _is_numeric_boundary(self, test_data: Dict, form: Dict) -> List[str]:
        """Check for numeric boundary tests"""
        indicators = []
        
        for key, value in test_data.items():
            try:
                num = float(value)
                if num == 0:
                    indicators.append("Zero/null numeric test")
                elif num < 0:
                    indicators.append("Negative number test")
                elif num > 1000000:
                    indicators.append("Very large number test")
            except (ValueError, TypeError):
                pass
        
        return indicators
    
    def _at_boundary(self, test_data: Dict) -> bool:
        """Check if values are at logical boundaries"""
        return any(v in self.BOUNDARY_VALUES for v in test_data.values())
    
    def _is_boundary_value(self, value) -> bool:
        """Check if single value is a boundary"""
        try:
            num = float(value)
            return num in (0, -1, 1, 999999, 2147483647)
        except (ValueError, TypeError):
            return value in ("", None) or len(str(value)) == 1 or len(str(value)) > 1000
    
    def _is_edge_value(self, value) -> bool:
        """Check if value is an edge case"""
        return self._is_boundary_value(value) or any(
            c in str(value) for c in self.INVALID_CHARS
        )
    
    def _is_statistical_extreme(self, test_data: Dict) -> bool:
        """Check for statistically extreme values"""
        # Very rare values, very common values
        rare_keywords = {"rare", "unique", "1%", "exceptional"}
        return any(k.lower() in str(test_data).lower() for k in rare_keywords)
    
    def _all_valid_values(self, test_data: Dict, form: Dict) -> bool:
        """Check if all values are valid (no boundaries, no errors)"""
        for value in test_data.values():
            if value in self.BOUNDARY_VALUES or self._is_edge_value(value):
                return False
        return True
    
    def _has_cross_field_dependencies(self, fields: List[Dict]) -> bool:
        """Check if form has dependent fields"""
        field_names = {f.get("name", "").lower() for f in fields}
        
        # Look for confirm/match/verify pairs
        patterns = [
            ("password", "confirm"),
            ("email", "confirm"),
            ("password", "verify"),
        ]
        
        for field1, field2 in patterns:
            if any(field1 in n for n in field_names) and any(field2 in n for n in field_names):
                return True
        
        return False
    
    def get_report(self, test_cases: List[Dict]) -> str:
        """Generate report of test classifications"""
        classifications = {}
        
        for test in test_cases:
            subtype_info = self.classify(test)
            key = f"{subtype_info.test_type}/{subtype_info.subtype}"
            
            if key not in classifications:
                classifications[key] = {"count": 0, "risk": subtype_info.base_risk}
            classifications[key]["count"] += 1
        
        report = "\n" + "="*80 + "\n"
        report += "TEST CLASSIFICATION REPORT\n"
        report += "="*80 + "\n\n"
        
        # Sort by risk
        sorted_class = sorted(
            classifications.items(),
            key=lambda x: x[1]["risk"],
            reverse=True
        )
        
        report += "Classification | Count | Risk\n"
        report += "-"*50 + "\n"
        
        for classification, data in sorted_class:
            risk_str = f"{data['risk']:.0%}"
            report += f"{classification:<30} | {data['count']:>5} | {risk_str:>8}\n"
        
        report += "\n" + "="*80 + "\n"
        return report

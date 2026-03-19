"""
Test Failure Probability Scorer
Analyzes test case characteristics to predict which tests are most likely to fail.
Uses multiple heuristics to rank tests for optimized execution order.
"""

import json
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution.test_subtype_classifier import TestSubtypeClassifier
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class TestScore:
    """Score and metadata for a test case"""
    test_id: str
    test_type: str
    failure_probability: float  # 0.0 (safe) to 1.0 (risky)
    risk_factors: List[str]  # Reasons for the score
    priority: int  # 1 (run first) to N (run last)


class TestFailureScorer:
    """
    Analyzes test cases and assigns failure probability scores.
    
    Risk Factors Considered:
    1. Input complexity (special chars, boundary values, regex patterns)
    2. Field type (passwords, dates, emails = higher risk)
    3. Test type (BVA > ECP > StateTransition > DecisionTable > UseCase)
    4. Form complexity (multi-step, wizard, file uploads)
    5. Validation rules (min/max length, patterns, required fields)
    6. Historical failure rates (if available)
    """
    
    # Test type base risk (how prone they are to uncovering bugs)
    TEST_TYPE_RISK = {
        "BVA": 0.8,                      # Boundary Value Analysis - high risk
        "ECP": 0.7,                      # Equivalence Class Partitioning
        "StateTransition": 0.5,          # State transitions - moderate
        "DecisionTable": 0.4,            # Decision tables - lower
        "UseCase": 0.3,                  # Use cases - lower
    }
    
    # Field type risk scores
    FIELD_TYPE_RISK = {
        "password": 0.7,                 # Password fields often have validation
        "email": 0.6,                    # Email validation is common
        "phone": 0.5,                    # Phone formatting issues
        "date": 0.6,                     # Date format mismatches
        "range": 0.7,                    # Min/max boundary issues
        "file": 0.8,                     # File uploads often break
        "textarea": 0.4,                 # Textareas usually flexible
        "checkbox": 0.3,                 # Checkboxes simple
        "radio": 0.3,                    # Radio buttons simple
        "select": 0.3,                   # Dropdowns usually validated
    }
    
    # Keywords indicating likely validation/complexity
    RISKY_KEYWORDS = {
        "password": 0.3,
        "credit_card": 0.8,              # High risk
        "ssn": 0.8,                      # Social security number
        "pin": 0.7,
        "age": 0.6,
        "phone": 0.5,
        "zip": 0.4,
        "postal": 0.4,
        "country": 0.2,
        "state": 0.2,
        "city": 0.2,
    }
    
    def __init__(self):
        """Initialize scorer"""
        self.test_scores: Dict[str, TestScore] = {}
        self.subtype_classifier = TestSubtypeClassifier()  # ← Add subtype detection
    
    def score_tests(self, test_cases: List[Dict]) -> List[TestScore]:
        """
        Score all test cases and return sorted by failure probability.
        
        Args:
            test_cases: List of test case dicts from test_storage
        
        Returns:
            List of TestScore objects sorted by priority (risky first)
        """
        scores = []
        
        for test_case in test_cases:
            score = self._score_single_test(test_case)
            scores.append(score)
            self.test_scores[test_case.get("id", "")] = score
        
        # Sort by priority (1 = run first, i.e., highest risk)
        scores.sort(key=lambda x: x.priority)
        
        return scores
    
    def _score_single_test(self, test_case: Dict) -> TestScore:
        """Calculate failure probability for a single test"""
        test_id = test_case.get("id", "unknown")
        test_type = test_case.get("type", "UseCase")
        
        risk_factors = []
        total_risk = 0.0
        factor_count = 0
        
        # ═══ NEW: Classify test subtype for more precise scoring ═══
        subtype_info = self.subtype_classifier.classify(test_case)
        subtype_risk = subtype_info.base_risk
        total_risk += subtype_risk
        factor_count += 1
        
        risk_factors.append(
            f"Subtype: {test_type}/{subtype_info.subtype} "
            f"(base risk: {subtype_risk:.2f}, confidence: {subtype_info.confidence:.0%})"
        )
        risk_factors.extend(subtype_info.indicators)
        
        # 2. Input complexity
        test_data = test_case.get("test_data", {})
        input_risk = self._assess_input_complexity(test_data)
        if input_risk > 0:
            total_risk += input_risk
            factor_count += 1
            risk_factors.append(f"Complex inputs detected (risk: {input_risk:.2f})")
        
        # 3. Field types
        form_data = test_case.get("form", {})
        field_risk = self._assess_field_types(form_data, test_data)
        if field_risk > 0:
            total_risk += field_risk
            factor_count += 1
            risk_factors.append(f"High-risk field types (risk: {field_risk:.2f})")
        
        # 4. Form complexity
        form_complexity_risk = self._assess_form_complexity(form_data)
        if form_complexity_risk > 0:
            total_risk += form_complexity_risk
            factor_count += 1
            risk_factors.append(f"Complex form structure (risk: {form_complexity_risk:.2f})")
        
        # 5. Validation rules
        validation_risk = self._assess_validation_rules(form_data)
        if validation_risk > 0:
            total_risk += validation_risk
            factor_count += 1
            risk_factors.append(f"Complex validation rules (risk: {validation_risk:.2f})")
        
        # 6. Boundary values
        boundary_risk = self._assess_boundary_values(test_case)
        if boundary_risk > 0:
            total_risk += boundary_risk
            factor_count += 1
            risk_factors.append(f"Boundary value test (risk: {boundary_risk:.2f})")
        
        # Calculate average probability
        if factor_count > 0:
            failure_probability = min(1.0, total_risk / factor_count)
        else:
            failure_probability = 0.5
        
        # Convert probability to 1-based priority (1 = highest priority)
        # Priority 1 = highest risk (will run first)
        priority = max(1, int((1.0 - failure_probability) * 100))  # Invert & scale
        
        if not risk_factors:
            risk_factors.append("Standard test")
        
        return TestScore(
            test_id=test_id,
            test_type=test_type,
            failure_probability=round(failure_probability, 2),
            risk_factors=risk_factors,
            priority=priority,
        )
    
    def _assess_input_complexity(self, test_data: Dict) -> float:
        """
        Assess complexity of input values.
        Special characters, unusual encodings, edge cases.
        """
        if not test_data:
            return 0.0
        
        risk = 0.0
        value_count = 0
        
        for field_name, field_value in test_data.items():
            if isinstance(field_value, str):
                value_count += 1
                
                # Check for special characters
                if re.search(r'[<>"\';\\]', field_value):
                    risk += 0.2  # XSS/injection concerns
                
                # Check for empty/null-like values
                if field_value.lower() in ('', 'null', 'none', 'undefined'):
                    risk += 0.15  # Null/empty handling
                
                # Check for very long strings
                if len(field_value) > 1000:
                    risk += 0.1
                
                # Check for numeric boundary values
                try:
                    num = float(field_value)
                    if num < 0 or num == 0 or abs(num) < 0.01:
                        risk += 0.1
                except ValueError:
                    pass
        
        return min(0.5, risk / max(1, value_count))
    
    def _assess_field_types(self, form_data: Dict, test_data: Dict) -> float:
        """
        Assess risk based on field types.
        Some fields are more prone to validation issues.
        """
        if not form_data or not form_data.get("fields"):
            return 0.0
        
        risk = 0.0
        field_count = 0
        
        for field in form_data.get("fields", []):
            field_count += 1
            field_type = field.get("type", "text").lower()
            field_name = field.get("name", "").lower()
            
            # Get base risk for this field type
            type_risk = self.FIELD_TYPE_RISK.get(field_type, 0.3)
            risk += type_risk
            
            # Add keyword-based risk
            for keyword, keyword_risk in self.RISKY_KEYWORDS.items():
                if keyword in field_name:
                    risk += keyword_risk * 0.5  # Moderate additional risk
        
        return min(0.8, risk / max(1, field_count))
    
    def _assess_form_complexity(self, form_data: Dict) -> float:
        """
        Assess form complexity (multi-step, file uploads, dynamic fields).
        """
        risk = 0.0
        
        # Multi-step form / wizard
        if form_data.get("is_wizard") or form_data.get("steps", 1) > 1:
            risk += 0.2
        
        # File upload
        if any(f.get("type") == "file" for f in form_data.get("fields", [])):
            risk += 0.3
        
        # Many fields
        field_count = len(form_data.get("fields", []))
        if field_count > 10:
            risk += 0.2
        elif field_count > 20:
            risk += 0.3
        
        # Dynamic fields (conditional rendering)
        if form_data.get("has_conditional_fields"):
            risk += 0.15
        
        # Dependent fields
        if form_data.get("has_dependent_fields"):
            risk += 0.1
        
        return min(0.7, risk)
    
    def _assess_validation_rules(self, form_data: Dict) -> float:
        """
        Assess complexity of validation rules on fields.
        """
        risk = 0.0
        
        for field in form_data.get("fields", []):
            has_rules = False
            
            # Check for various validation types
            if field.get("required"):
                risk += 0.1
                has_rules = True
            
            if field.get("min_length") or field.get("max_length"):
                risk += 0.1
                has_rules = True
            
            if field.get("pattern") or field.get("regex"):
                risk += 0.15  # Regex often has edge cases
                has_rules = True
            
            if field.get("match_field"):
                risk += 0.1  # Cross-field validation
                has_rules = True
            
            if field.get("custom_validator"):
                risk += 0.1
                has_rules = True
        
        return min(0.5, risk / max(1, len(form_data.get("fields", []))))
    
    def _assess_boundary_values(self, test_case: Dict) -> float:
        """
        Check if this is specifically a boundary value test.
        BVA tests are designed to find edge case bugs.
        """
        test_type = test_case.get("type", "")
        
        if test_type != "BVA":
            return 0.0
        
        # Check test data for boundary indicators
        test_data = test_case.get("test_data", {})
        test_value = str(test_case.get("test_value", ""))
        
        risk = 0.2  # Base risk for BVA
        
        # Check for specific boundary patterns
        if test_value in ("", "-1", "0", "max", "999999"):
            risk += 0.2
        
        # Check for boundary-like values in test data
        for value in test_data.values():
            str_value = str(value).lower()
            if any(b in str_value for b in ["boundary", "edge", "limit", "max", "min"]):
                risk += 0.1
        
        return min(0.8, risk)
    
    def get_test_by_priority(self, test_id: str) -> TestScore:
        """Retrieve calculated score for a test"""
        return self.test_scores.get(test_id, None)
    
    def report_scores(self, scores: List[TestScore], limit: int = 10) -> str:
        """
        Generate human-readable report of test scores.
        
        Args:
            scores: List of TestScore objects
            limit: Show top N tests
        
        Returns:
            Formatted report string
        """
        report = f"\n=== Test Failure Probability Report (Top {limit}) ===\n"
        report += f"{'Priority':<10} {'Test ID':<20} {'Type':<15} {'Risk':<8} {'Risk Factors':<60}\n"
        report += "-" * 120 + "\n"
        
        for i, score in enumerate(scores[:limit]):
            risk_str = f"{score.failure_probability:.2%}"
            factors = "; ".join(score.risk_factors[:2])  # Show top 2 factors
            
            report += (
                f"{score.priority:<10} "
                f"{score.test_id[:19]:<20} "
                f"{score.test_type:<15} "
                f"{risk_str:<8} "
                f"{factors:<60}\n"
            )
        
        report += "-" * 120 + "\n"
        avg_risk = sum(s.failure_probability for s in scores) / len(scores) if scores else 0
        report += f"Average failure probability: {avg_risk:.2%}\n"
        
        return report

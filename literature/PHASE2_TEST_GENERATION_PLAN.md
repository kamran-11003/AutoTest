# 🧪 Phase 2: Test Case Generation - Implementation Plan

**Project:** AutoTestAI - Intelligent Web Testing Framework  
**Phase:** 2 - Automated Test Generation & Refinement  
**Date:** November 28, 2025  
**Status:** Planning Complete → Ready for Implementation

---

## 📋 Overview

Phase 2 focuses on **generating comprehensive test cases** from the UI graph and form data collected in Phase 1. We'll use multiple test generation strategies, write tests in industry-standard libraries (Playwright/Selenium), and refine them using Gemini AI.

---

## 🎯 Test Case Types We'll Generate

### 📊 **Complete Test Type Matrix**

#### **1️⃣ Functional Test Cases**

| **Type** | **Description** | **Example** | **Feasibility** |
|----------|----------------|-------------|----------------|
| **Boundary Value Analysis (BVA)** | Test min, max, just-inside, just-outside boundaries | Age field: -1, 0, 1, 17, 18, 100, 101 | ✅ **High** |
| **Equivalence Class Partitioning (ECP)** | Test representative values from each valid/invalid class | Valid emails, invalid formats, empty | ✅ **High** |
| **Decision Table Testing** | Test combinations of inputs/conditions | Shipping (domestic/intl) × Payment (card/paypal) | ✅ **Medium** |
| **State Transition Testing** | Test state changes (e.g., cart states) | Empty → Item Added → Checkout → Paid | ✅ **High** |
| **Use Case Testing** | End-to-end user scenarios | "Add product, apply coupon, checkout" | ✅ **High** |
| **Error Guessing** | Test common error scenarios | XSS, SQL injection, buffer overflow | ⚠️ **Medium** |

---

#### **2️⃣ UI/UX Test Cases**

| **Type** | **Description** | **Example** | **Feasibility** |
|----------|----------------|-------------|----------------|
| **Element Visibility** | Verify elements render correctly | Button visible, form accessible | ✅ **High** |
| **Responsive Testing** | Test different screen sizes | Mobile (375px), Tablet (768px), Desktop | ✅ **High** |
| **Accessibility (a11y)** | WCAG compliance | ARIA labels, keyboard navigation | ✅ **High** |
| **Cross-Browser** | Test on Chrome, Firefox, Safari | CSS compatibility, JS behavior | ✅ **High** |
| **Performance** | Load time, render time | Page loads < 3s, LCP < 2.5s | ✅ **Medium** |

---

#### **3️⃣ Integration Test Cases**

| **Type** | **Description** | **Example** | **Feasibility** |
|----------|----------------|-------------|----------------|
| **API Integration** | Test form submissions → backend | POST /cart/add returns 200 | ✅ **High** |
| **Third-Party Services** | Payment gateways, analytics | Stripe checkout flow | ⚠️ **Low** (requires mocking) |
| **Database Validation** | Verify data persistence | User registration → DB entry created | ❌ **Low** (no DB access) |

---

#### **4️⃣ Security Test Cases**

| **Type** | **Description** | **Example** | **Feasibility** |
|----------|----------------|-------------|----------------|
| **Input Validation** | XSS, SQL injection attempts | `<script>alert(1)</script>` in form | ✅ **High** |
| **Authentication** | Login/logout flows | Session management, token validation | ⚠️ **Medium** |
| **Authorization** | Access control | Regular user cannot access admin panel | ⚠️ **Low** (requires auth) |
| **HTTPS Enforcement** | SSL/TLS validation | HTTP redirects to HTTPS | ✅ **High** |

---

#### **5️⃣ Negative Test Cases**

| **Type** | **Description** | **Example** | **Feasibility** |
|----------|----------------|-------------|----------------|
| **Missing Required Fields** | Submit form with empty required fields | Email field empty → error message | ✅ **High** |
| **Invalid Data Types** | Enter text in numeric fields | Age = "twenty" → validation error | ✅ **High** |
| **Exceeding Limits** | Enter values beyond allowed range | 1000-character name | ✅ **High** |
| **Special Characters** | Unicode, emojis, SQL chars | Name = "O'Brien 🚀" | ✅ **High** |

---

### ✅ **High Priority (Phase 2 Focus)**

#### **1. Boundary Value Analysis (BVA)**

**Inputs Detected by Crawler:**
```json
{
  "type": "number",
  "name": "age",
  "min": 18,
  "max": 100,
  "required": true
}
```

**Generated Test Cases:**
```python
test_cases = [
    {"age": 17,  "expected": "validation_error"},  # Below min
    {"age": 18,  "expected": "success"},           # Min boundary
    {"age": 19,  "expected": "success"},           # Just above min
    {"age": 99,  "expected": "success"},           # Just below max
    {"age": 100, "expected": "success"},           # Max boundary
    {"age": 101, "expected": "validation_error"},  # Above max
]
```

**Coverage Target:** 100% of all numeric/date/length-constrained inputs

---

#### **2. Equivalence Class Partitioning (ECP)**

**Input Detected:**
```json
{
  "type": "email",
  "name": "email",
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
}
```

**Generated Test Cases:**
```python
test_cases = [
    # Valid class
    {"email": "user@example.com", "expected": "success"},
    {"email": "test.user+tag@domain.co.uk", "expected": "success"},
    
    # Invalid - missing @
    {"email": "userexample.com", "expected": "validation_error"},
    
    # Invalid - missing domain
    {"email": "user@", "expected": "validation_error"},
    
    # Invalid - special chars
    {"email": "user#@example.com", "expected": "validation_error"},
    
    # Edge - empty
    {"email": "", "expected": "validation_error"},
]
```

**Coverage Target:** 90%+ of all input types

---

#### **3. State Transition Testing**

**From Crawler Graph:**
```
Empty Cart → Product Page → Add to Cart → Cart Page → Checkout → Payment
```

**Generated Test Cases:**
```python
test_cases = [
    {
        "name": "Happy path - complete purchase",
        "steps": [
            {"action": "navigate", "url": "/products/shoes"},
            {"action": "click", "selector": ".add-to-cart"},
            {"action": "verify", "condition": "cart_count == 1"},
            {"action": "navigate", "url": "/cart"},
            {"action": "click", "selector": ".checkout-btn"},
            {"action": "verify", "condition": "url.includes('/checkout')"}
        ]
    },
    {
        "name": "Remove item from cart",
        "steps": [
            {"action": "navigate", "url": "/cart"},
            {"action": "click", "selector": ".remove-item"},
            {"action": "verify", "condition": "cart_count == 0"}
        ]
    }
]
```

**Coverage Target:** 15+ major user flows

---

#### **4. UI Validation Tests**

**From Crawler Data:**
```json
{
  "buttons": [
    {"text": "Add to Cart", "selector": ".add-to-cart", "visible": true}
  ],
  "forms": [
    {"id": "checkout-form", "action": "/checkout", "method": "POST"}
  ]
}
```

**Generated Test Cases:**
```python
test_cases = [
    {
        "name": "Verify Add to Cart button exists",
        "test": "expect(page.locator('.add-to-cart')).toBeVisible()"
    },
    {
        "name": "Verify checkout form submits to correct endpoint",
        "test": "expect(form.getAttribute('action')).toBe('/checkout')"
    }
]
```

**Coverage Target:** 100% of critical UI elements

---

#### **5. Accessibility (a11y) Tests**

**Generated from DOM Analysis:**
```python
test_cases = [
    {
        "name": "All images have alt text",
        "test": "expect(page.locator('img:not([alt])')).toHaveCount(0)"
    },
    {
        "name": "Form inputs have labels",
        "test": "expect(page.locator('input:not([aria-label]):not([aria-labelledby])')).toHaveCount(0)"
    },
    {
        "name": "Buttons are keyboard accessible",
        "test": "await button.press('Enter'); expect(button).toBeFocused()"
    }
]
```

**Coverage Target:** WCAG 2.1 Level AA compliance

---

### ⚠️ **Medium Priority (Phase 2.5)**

#### **6. Decision Table Testing**

**Example: Shipping Calculator**

| **Domestic?** | **Express?** | **Weight > 5kg?** | **Shipping Cost** |
|---------------|--------------|-------------------|-------------------|
| Yes | Yes | Yes | $25 |
| Yes | Yes | No  | $15 |
| Yes | No  | Yes | $10 |
| Yes | No  | No  | $5  |
| No  | Yes | Yes | $50 |
| No  | Yes | No  | $30 |
| No  | No  | Yes | $20 |
| No  | No  | No  | $10 |

**Generated Test Cases:**
```python
test_cases = [
    {"domestic": True,  "express": True,  "weight": 6,  "expected_cost": 25},
    {"domestic": True,  "express": False, "weight": 3,  "expected_cost": 5},
    {"domestic": False, "express": True,  "weight": 10, "expected_cost": 50},
    # ... 5 more combinations
]
```

---

#### **7. Error Guessing (Security)**

**Generated XSS Test Cases:**
```python
test_cases = [
    {"input": "<script>alert('XSS')</script>", "expected": "escaped_or_blocked"},
    {"input": "javascript:alert(1)", "expected": "escaped_or_blocked"},
    {"input": "<img src=x onerror=alert(1)>", "expected": "escaped_or_blocked"},
    {"input": "'; DROP TABLE users; --", "expected": "escaped_or_blocked"},
]
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             PHASE 1: CRAWLER (Already Complete)              │
│  ├─ UI Graph (nodes, edges, states)                         │
│  ├─ Form Data (inputs, validation rules)                    │
│  ├─ Element Data (buttons, links, images)                   │
│  └─ State Transitions (cart flows, wizards)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            PHASE 2: TEST GENERATION (New)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  STEP 1: Test Case Generator Engine               │    │
│  │  ├─ BVA Generator (boundaries)                     │    │
│  │  ├─ ECP Generator (equivalence classes)            │    │
│  │  ├─ State Transition Generator (flows)             │    │
│  │  ├─ UI Validation Generator (element checks)       │    │
│  │  └─ Accessibility Generator (a11y checks)          │    │
│  │  Output: test_cases.json                           │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  STEP 2: Library-Based Test Writer                │    │
│  │  ├─ Playwright Writer (TypeScript/JavaScript)      │    │
│  │  ├─ Selenium Writer (Python)                       │    │
│  │  └─ Pytest Format (Python)                         │    │
│  │  Output: tests/*.spec.ts, tests/*.py               │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  STEP 3: Gemini AI Refinement                     │    │
│  │  ├─ Semantic Enhancement                           │    │
│  │  ├─ Edge Case Suggestions                          │    │
│  │  ├─ Test Description Generation                    │    │
│  │  ├─ Code Quality Improvement                       │    │
│  │  └─ Assertion Enhancement                          │    │
│  │  Output: tests_refined/*.spec.ts                   │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  STEP 4: Test Executor & Validator                │    │
│  │  ├─ Run Playwright tests                           │    │
│  │  ├─ Collect execution results                      │    │
│  │  ├─ Generate coverage report                       │    │
│  │  └─ Identify gaps for iteration                    │    │
│  │  Output: test_results.html, coverage_report.json   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
fyp crawler/
├── crawler/                  # Phase 1 (Complete)
│   ├── orchestrator.py
│   ├── form_wizard_detector.py
│   └── ...
│
├── test_generator/          # Phase 2 (New)
│   ├── __init__.py
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── bva_generator.py         # Boundary Value Analysis
│   │   ├── ecp_generator.py         # Equivalence Class Partitioning
│   │   ├── state_generator.py       # State Transition Tests
│   │   ├── ui_generator.py          # UI Validation Tests
│   │   └── a11y_generator.py        # Accessibility Tests
│   │
│   ├── writers/
│   │   ├── __init__.py
│   │   ├── playwright_writer.py     # Playwright test code writer
│   │   ├── selenium_writer.py       # Selenium test code writer
│   │   └── pytest_writer.py         # Pytest format writer
│   │
│   ├── refiner/
│   │   ├── __init__.py
│   │   ├── gemini_refiner.py        # AI-powered test enhancement
│   │   └── prompt_templates.py      # Gemini prompts
│   │
│   ├── executor/
│   │   ├── __init__.py
│   │   ├── test_runner.py           # Execute generated tests
│   │   └── coverage_analyzer.py     # Analyze test coverage
│   │
│   └── test_orchestrator.py         # Main test generation coordinator
│
├── generated_tests/         # Output directory
│   ├── playwright/
│   │   ├── bva/
│   │   ├── ecp/
│   │   ├── state/
│   │   └── ui/
│   ├── selenium/
│   └── test_results/
│
├── config/
│   └── test_config.yaml     # Test generation configuration
│
└── data/
    └── crawled_graphs/      # Input from Phase 1
```

---

## 🔧 Implementation Roadmap

### **Week 1: Core Test Generators (Dec 2-8, 2025)**

#### Day 1-2: BVA Generator
```python
# test_generator/generators/bva_generator.py

class BVAGenerator:
    """Generate Boundary Value Analysis test cases"""
    
    def generate(self, input_field: Dict) -> List[Dict]:
        """
        Input:
        {
            "name": "age",
            "type": "number",
            "min": 18,
            "max": 100,
            "required": True
        }
        
        Output:
        [
            {"value": 17, "expected": "error", "description": "Below minimum"},
            {"value": 18, "expected": "success", "description": "At minimum"},
            {"value": 19, "expected": "success", "description": "Above minimum"},
            {"value": 99, "expected": "success", "description": "Below maximum"},
            {"value": 100, "expected": "success", "description": "At maximum"},
            {"value": 101, "expected": "error", "description": "Above maximum"}
        ]
        """
```

**Deliverable:** BVA test cases for all numeric/date/length fields

---

#### Day 3-4: ECP Generator
```python
# test_generator/generators/ecp_generator.py

class ECPGenerator:
    """Generate Equivalence Class Partitioning test cases"""
    
    def generate(self, input_field: Dict) -> List[Dict]:
        """
        Input:
        {
            "name": "email",
            "type": "email",
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        }
        
        Output:
        [
            # Valid class
            {"value": "user@example.com", "class": "valid", "expected": "success"},
            {"value": "test+tag@domain.co.uk", "class": "valid", "expected": "success"},
            
            # Invalid - format errors
            {"value": "userexample.com", "class": "invalid_missing_at", "expected": "error"},
            {"value": "user@", "class": "invalid_missing_domain", "expected": "error"},
            {"value": "", "class": "invalid_empty", "expected": "error"}
        ]
        """
```

**Deliverable:** ECP test cases for all pattern-validated fields

---

#### Day 5: Playwright Test Writer
```typescript
// Example generated test
// generated_tests/playwright/bva/age-field.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Age Field - Boundary Value Analysis', () => {
    test('Rejects age below minimum (17)', async ({ page }) => {
        await page.goto('https://example.com/checkout');
        await page.fill('[name="age"]', '17');
        await page.click('.submit-btn');
        
        await expect(page.locator('.error-message')).toContainText('Age must be at least 18');
    });
    
    test('Accepts minimum valid age (18)', async ({ page }) => {
        await page.goto('https://example.com/checkout');
        await page.fill('[name="age"]', '18');
        await page.click('.submit-btn');
        
        await expect(page).toHaveURL(/order-confirmation/);
    });
});
```

**Deliverable:** 50-100 executable Playwright tests

---

### **Week 2: Advanced Generators (Dec 9-15, 2025)**

#### Day 1-2: State Transition Generator
```python
# test_generator/generators/state_generator.py

class StateTransitionGenerator:
    """Generate tests for state transitions from UI graph"""
    
    def generate(self, graph: Dict) -> List[Dict]:
        """
        Input: UI graph with state transitions
        
        Output:
        [
            {
                "name": "Complete purchase flow",
                "path": [
                    "/products/shoes",
                    "/cart",
                    "/checkout",
                    "/payment",
                    "/confirmation"
                ],
                "actions": [
                    {"type": "click", "selector": ".add-to-cart"},
                    {"type": "click", "selector": ".checkout-btn"},
                    {"type": "fill", "selector": "[name='card']", "value": "4111111111111111"},
                    {"type": "click", "selector": ".pay-btn"}
                ],
                "assertions": [
                    {"type": "url", "expected": "/confirmation"},
                    {"type": "element", "selector": ".success-message", "expected": "visible"}
                ]
            }
        ]
        """
```

**Deliverable:** 15+ user flow test cases

---

#### Day 3-4: UI & Accessibility Generators
```python
# test_generator/generators/ui_generator.py
# test_generator/generators/a11y_generator.py

class UIValidationGenerator:
    """Generate UI element validation tests"""
    
class AccessibilityGenerator:
    """Generate WCAG 2.1 compliance tests"""
```

**Deliverable:** 100+ UI/a11y test cases

---

### **Week 3: Gemini AI Refinement (Dec 16-22, 2025)**

#### Day 1-2: Gemini Integration
```python
# test_generator/refiner/gemini_refiner.py

class GeminiTestRefiner:
    """Enhance tests using Gemini AI"""
    
    async def refine_test(self, test_code: str) -> str:
        """
        Uses Gemini to:
        1. Add better error messages
        2. Suggest edge cases
        3. Improve test descriptions
        4. Enhance assertions
        5. Add comments
        """
        
        prompt = self._build_refinement_prompt(test_code)
        response = await self.gemini_client.generate_content(prompt)
        return response.text
```

**Deliverable:** Gemini-powered test enhancement system

---

#### Day 3-5: Prompt Engineering & Iteration
- Create effective prompts for different test types
- Handle Gemini response parsing
- Implement feedback loop for continuous improvement

**Deliverable:** 70%+ tests enhanced with AI suggestions

---

### **Week 4: Execution & Validation (Dec 23-29, 2025)**

#### Day 1-2: Test Executor
```python
# test_generator/executor/test_runner.py

class TestRunner:
    """Execute generated Playwright tests"""
    
    async def run_tests(self, test_dir: str) -> Dict:
        """
        Runs all tests and collects:
        - Pass/fail counts
        - Execution time
        - Screenshots on failure
        - Error messages
        """
```

**Deliverable:** Automated test execution pipeline

---

#### Day 3-4: Coverage Analysis & Reporting
```python
# test_generator/executor/coverage_analyzer.py

class CoverageAnalyzer:
    """Analyze test coverage and identify gaps"""
    
    def generate_report(self) -> Dict:
        """
        Returns:
        {
            "total_tests": 250,
            "passed": 212,
            "failed": 38,
            "coverage": {
                "bva": 95,
                "ecp": 88,
                "state": 100,
                "ui": 90,
                "a11y": 85
            },
            "gaps": ["Missing payment error tests", "No timeout tests"]
        }
        """
```

**Deliverable:** Comprehensive coverage report with HTML output

---

## 📊 Success Metrics

| **Metric** | **Target** | **Measurement** |
|-----------|-----------|-----------------|
| **Total Test Cases Generated** | 200+ | Count in generated_tests/ |
| **Code Coverage** | 80%+ | Playwright coverage report |
| **BVA Coverage** | 100% | All numeric/date inputs tested |
| **ECP Coverage** | 90%+ | Major input types covered |
| **State Transitions** | 15+ | User flows tested |
| **UI Element Tests** | 100+ | Button/form/link tests |
| **Accessibility Tests** | 50+ | WCAG checks |
| **Gemini Refinement Rate** | 70%+ | Tests enhanced by AI |
| **Test Execution Success** | 85%+ | Pass rate on first run |
| **Execution Time** | < 10 min | For full test suite |

---

## 🎯 Example: Complete Test Generation Flow

### **Input (From Phase 1 Crawler):**
```json
{
  "url": "https://www.allbirds.com/checkout",
  "forms": [
    {
      "id": "checkout-form",
      "action": "/order/submit",
      "method": "POST",
      "inputs": [
        {
          "name": "email",
          "type": "email",
          "required": true,
          "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        {
          "name": "age",
          "type": "number",
          "min": 18,
          "max": 100,
          "required": true
        },
        {
          "name": "zipcode",
          "type": "text",
          "pattern": "\\d{5}",
          "maxlength": 5,
          "required": true
        }
      ],
      "submit_button": {
        "selector": ".btn-submit",
        "text": "Place Order"
      }
    }
  ]
}
```

---

### **Step 1: Generate Test Cases**

**BVA Generator Output:**
```json
{
  "test_suite": "Checkout Form - BVA",
  "tests": [
    {
      "field": "age",
      "test_cases": [
        {"value": 17, "expected": "error", "description": "Below minimum"},
        {"value": 18, "expected": "success", "description": "At minimum"},
        {"value": 19, "expected": "success", "description": "Just above minimum"},
        {"value": 99, "expected": "success", "description": "Just below maximum"},
        {"value": 100, "expected": "success", "description": "At maximum"},
        {"value": 101, "expected": "error", "description": "Above maximum"}
      ]
    },
    {
      "field": "zipcode",
      "test_cases": [
        {"value": "1234", "expected": "error", "description": "Below length"},
        {"value": "12345", "expected": "success", "description": "Valid length"},
        {"value": "123456", "expected": "error", "description": "Above length"}
      ]
    }
  ]
}
```

**ECP Generator Output:**
```json
{
  "test_suite": "Checkout Form - ECP",
  "tests": [
    {
      "field": "email",
      "classes": [
        {
          "class": "valid_standard",
          "values": ["user@example.com", "test@domain.co.uk"],
          "expected": "success"
        },
        {
          "class": "valid_with_tags",
          "values": ["user+tag@example.com", "test.user@domain.com"],
          "expected": "success"
        },
        {
          "class": "invalid_missing_at",
          "values": ["userexample.com", "user.example.com"],
          "expected": "error"
        },
        {
          "class": "invalid_missing_domain",
          "values": ["user@", "user@.com"],
          "expected": "error"
        },
        {
          "class": "invalid_empty",
          "values": ["", " "],
          "expected": "error"
        }
      ]
    }
  ]
}
```

---

### **Step 2: Write Playwright Tests**

**Generated Test File:**
```typescript
// generated_tests/playwright/bva/checkout-age.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Checkout Form - Age Field BVA', () => {
    const BASE_INPUT = {
        email: 'test@example.com',
        zipcode: '12345'
    };

    test('Age validation - Below minimum (17)', async ({ page }) => {
        await page.goto('https://www.allbirds.com/checkout');
        
        await page.fill('[name="email"]', BASE_INPUT.email);
        await page.fill('[name="age"]', '17');
        await page.fill('[name="zipcode"]', BASE_INPUT.zipcode);
        await page.click('.btn-submit');
        
        await expect(page.locator('.error-message')).toContainText('Age must be at least 18');
        await expect(page).toHaveURL('https://www.allbirds.com/checkout'); // Form should not submit
    });

    test('Age validation - At minimum (18)', async ({ page }) => {
        await page.goto('https://www.allbirds.com/checkout');
        
        await page.fill('[name="email"]', BASE_INPUT.email);
        await page.fill('[name="age"]', '18');
        await page.fill('[name="zipcode"]', BASE_INPUT.zipcode);
        await page.click('.btn-submit');
        
        await expect(page).toHaveURL(/order-confirmation/);
    });

    test('Age validation - Above maximum (101)', async ({ page }) => {
        await page.goto('https://www.allbirds.com/checkout');
        
        await page.fill('[name="email"]', BASE_INPUT.email);
        await page.fill('[name="age"]', '101');
        await page.fill('[name="zipcode"]', BASE_INPUT.zipcode);
        await page.click('.btn-submit');
        
        await expect(page.locator('.error-message')).toContainText('Age cannot exceed 100');
    });
});
```

---

### **Step 3: Gemini AI Refinement**

**Prompt to Gemini:**
```
You are a test automation expert. Improve this Playwright test:

[paste generated test code]

Enhancements needed:
1. Add better error messages and comments
2. Include edge cases (e.g., decimal numbers, negative numbers)
3. Add proper setup/teardown
4. Improve test descriptions using Given-When-Then format
5. Add timeout handling
6. Consider accessibility (keyboard navigation)

Return improved test code.
```

**Gemini-Enhanced Output:**
```typescript
// generated_tests/playwright/bva/checkout-age-refined.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Checkout Form - Age Field Boundary Value Analysis', () => {
    const BASE_INPUT = {
        email: 'test@example.com',
        zipcode: '12345'
    };

    test.beforeEach(async ({ page }) => {
        // Navigate to checkout and wait for form to be ready
        await page.goto('https://www.allbirds.com/checkout');
        await page.waitForSelector('[name="email"]', { state: 'visible' });
    });

    test('Should reject age below minimum boundary (17)', async ({ page }) => {
        // GIVEN: User is on checkout page
        // WHEN: User enters age 17 (below minimum of 18)
        await page.fill('[name="email"]', BASE_INPUT.email);
        await page.fill('[name="age"]', '17');
        await page.fill('[name="zipcode"]', BASE_INPUT.zipcode);
        await page.click('.btn-submit');
        
        // THEN: Validation error should appear
        const errorMessage = page.locator('.error-message');
        await expect(errorMessage).toBeVisible({ timeout: 5000 });
        await expect(errorMessage).toContainText(/age must be at least 18/i);
        
        // AND: Form should not submit
        await expect(page).toHaveURL('https://www.allbirds.com/checkout');
    });

    test('Should accept minimum valid age boundary (18)', async ({ page }) => {
        // GIVEN: User is on checkout page
        // WHEN: User enters exactly age 18 (minimum valid)
        await page.fill('[name="email"]', BASE_INPUT.email);
        await page.fill('[name="age"]', '18');
        await page.fill('[name="zipcode"]', BASE_INPUT.zipcode);
        await page.click('.btn-submit');
        
        // THEN: Form should submit successfully
        await page.waitForURL(/order-confirmation/, { timeout: 10000 });
        await expect(page.locator('.success-message')).toBeVisible();
    });

    // 🤖 AI-ADDED: Edge case tests
    test('Should reject negative age values', async ({ page }) => {
        // Tests edge case: negative numbers
        await page.fill('[name="age"]', '-5');
        await page.click('.btn-submit');
        
        await expect(page.locator('.error-message')).toContainText(/age must be positive/i);
    });

    test('Should reject decimal age values', async ({ page }) => {
        // Tests edge case: decimal numbers
        await page.fill('[name="age"]', '18.5');
        await page.click('.btn-submit');
        
        await expect(page.locator('.error-message')).toContainText(/age must be a whole number/i);
    });

    test('Should reject non-numeric age input', async ({ page }) => {
        // Tests edge case: string input
        await page.fill('[name="age"]', 'twenty');
        await page.click('.btn-submit');
        
        await expect(page.locator('.error-message')).toContainText(/age must be a number/i);
    });

    // 🤖 AI-ADDED: Accessibility test
    test('Should support keyboard navigation for age input', async ({ page }) => {
        // GIVEN: User relies on keyboard
        // WHEN: User tabs to age field and enters value
        await page.keyboard.press('Tab'); // Focus email
        await page.keyboard.type(BASE_INPUT.email);
        await page.keyboard.press('Tab'); // Focus age
        await page.keyboard.type('18');
        await page.keyboard.press('Tab'); // Focus zipcode
        await page.keyboard.type(BASE_INPUT.zipcode);
        await page.keyboard.press('Enter'); // Submit form
        
        // THEN: Form should submit successfully
        await expect(page).toHaveURL(/order-confirmation/);
    });
});
```

---

### **Step 4: Execute & Report**

**Execution Results:**
```json
{
  "test_run": {
    "timestamp": "2025-12-15T10:30:00Z",
    "duration_ms": 45230,
    "total_tests": 6,
    "passed": 5,
    "failed": 1,
    "skipped": 0
  },
  "results": [
    {
      "name": "Should reject age below minimum boundary (17)",
      "status": "passed",
      "duration_ms": 3420
    },
    {
      "name": "Should accept minimum valid age boundary (18)",
      "status": "passed",
      "duration_ms": 5210
    },
    {
      "name": "Should reject negative age values",
      "status": "failed",
      "error": "Validation message not found (app doesn't handle negatives)",
      "screenshot": "screenshots/failed-negative-test.png"
    },
    {
      "name": "Should reject decimal age values",
      "status": "passed",
      "duration_ms": 3890
    },
    {
      "name": "Should reject non-numeric age input",
      "status": "passed",
      "duration_ms": 3240
    },
    {
      "name": "Should support keyboard navigation",
      "status": "passed",
      "duration_ms": 6180
    }
  ],
  "coverage": {
    "bva": 100,
    "edge_cases": 75
  }
}
```

---

## 🎯 **Phase 2 Implementation Plan**

### **Week 1: Core Test Generator (Dec 2-8, 2025)**
- ✅ BVA Generator (input boundaries)
- ✅ ECP Generator (equivalence classes)
- ✅ Basic Playwright writer

**Deliverable:** 50-100 basic test cases for Allbirds

---

### **Week 2: Advanced Generators (Dec 9-15, 2025)**
- ✅ State Transition Generator (cart flows)
- ✅ UI Validation Generator (element presence)
- ✅ Accessibility Generator (a11y checks)

**Deliverable:** 150-200 comprehensive test cases

---

### **Week 3: Gemini Integration (Dec 16-22, 2025)**
- ✅ Connect Gemini API
- ✅ Prompt engineering for test refinement
- ✅ Edge case suggestion system
- ✅ Test description enhancement

**Deliverable:** AI-refined test suite with 30% more coverage

---

### **Week 4: Execution & Validation (Dec 23-29, 2025)**
- ✅ Run generated tests
- ✅ Collect pass/fail metrics
- ✅ Generate coverage report
- ✅ Identify gaps and iterate

**Deliverable:** Execution report + demo video

---

## 📈 **Success Metrics for Phase 2**

| **Metric** | **Target** |
|-----------|-----------|
| Test cases generated | 200+ |
| Code coverage | 80%+ |
| BVA coverage | 100% (all numeric/date inputs) |
| ECP coverage | 90%+ (major input types) |
| State transitions tested | 15+ paths |
| Gemini refinement rate | 70%+ tests enhanced |
| Test execution success | 85%+ pass rate |

---

## 🚀 Quick Start Commands

### **Setup:**
```bash
# Install dependencies
npm install -D @playwright/test
npm install -D typescript

# Install Python dependencies
pip install google-generativeai pyyaml pytest playwright

# Initialize Playwright
npx playwright install
```

### **Run Test Generation:**
```bash
# Generate tests from crawl data
python test_generator/test_orchestrator.py \
  --input data/crawled_graphs/crawl_51.json \
  --output generated_tests/playwright \
  --types bva,ecp,state \
  --refine

# Execute generated tests
npx playwright test generated_tests/playwright/

# Generate coverage report
python test_generator/executor/coverage_analyzer.py \
  --results test-results/ \
  --output coverage_report.html
```

---

## 📈 Expected Outcomes

### **After Week 1:**
- ✅ 50-100 BVA + ECP test cases
- ✅ Executable Playwright tests
- ✅ Basic test runner

### **After Week 2:**
- ✅ 150-200 comprehensive test cases
- ✅ State transition tests for e-commerce flows
- ✅ UI + accessibility tests

### **After Week 3:**
- ✅ AI-refined test suite with 30%+ more coverage
- ✅ Improved test descriptions and assertions
- ✅ Edge cases identified and tested

### **After Week 4:**
- ✅ Fully automated test execution pipeline
- ✅ Coverage report with gap analysis
- ✅ Demo-ready system with impressive metrics

---

## 🎓 Research Contributions

### **Novel Aspects for FYP:**

1. **Hybrid Test Generation:**
   - Combines rule-based generators (BVA, ECP) with AI refinement
   - No existing tool does this combination

2. **Graph-to-Test Translation:**
   - First framework to generate state transition tests from UI graphs
   - Leverages Phase 1 crawler output directly

3. **AI-Powered Test Enhancement:**
   - Uses LLM to suggest edge cases and improve test quality
   - Demonstrates practical AI application in testing

4. **Cross-Library Support:**
   - Generates tests for multiple frameworks (Playwright, Selenium, Pytest)
   - Enables flexibility and wider adoption

---

## ❓ **Next Steps - Your Decision**

### **Which Test Generator Should We Implement First?**

| **Aspect** | **Option A: BVA + ECP** | **Option B: State Transition** | **Option C: UI + Accessibility** |
|-----------|------------------------|-------------------------------|--------------------------------|
| **Complexity** | ✅ Simple (3-4 days) | ⚠️ Complex (5-6 days) | ⚠️ Medium (4-5 days) |
| **Demo Impact** | ⚠️ Standard | ✅ Very Impressive | ✅ Unique & Practical |
| **Measurability** | ✅ Clear metrics | ✅ Flow coverage | ✅ WCAG compliance |
| **Foundation** | ✅ Builds base for others | ⚠️ Requires graph algorithms | ⚠️ Needs WCAG expertise |
| **Industry Relevance** | ✅ Standard practice | ✅ E-commerce critical | ✅ Growing demand |
| **Alignment** | ⚠️ Generic | ✅ Matches crawler strength | ⚠️ Moderate |
| **Learning Curve** | ✅ Easy | ⚠️ Moderate | ⚠️ Moderate |

---

### **Recommendation: Option A (BVA + ECP)**

**Why Start Here:**
1. ✅ **Fast Implementation:** Get working tests in 3-4 days
2. ✅ **Foundation:** Required for Options B & C anyway
3. ✅ **Clear Success Metrics:** Easy to measure and demonstrate
4. ✅ **Universal Applicability:** Works for all input types
5. ✅ **Incremental Progress:** Can add State/UI tests later

**What You'll Get:**
- 50-100 executable Playwright tests in Week 1
- BVA coverage for age, dates, text lengths
- ECP coverage for emails, phones, URLs
- Solid foundation for Gemini refinement

---

### **Implementation Order (Recommended):**

```
Week 1: BVA + ECP (Option A)
  └─► 50-100 basic tests

Week 2: State Transition (Option B)
  └─► Add e-commerce flows

Week 3: UI + Accessibility (Option C)
  └─► Add WCAG compliance tests

Week 4: Gemini Refinement + Execution
  └─► Polish everything with AI
```

---

**Ready to start with BVA + ECP? Let me know and I'll create the generators!** 🚀

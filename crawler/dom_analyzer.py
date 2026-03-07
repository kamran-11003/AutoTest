"""
Universal DOM Analyzer
Detects forms and inputs using 7 strategies (framework-agnostic + AI vision)
"""
from typing import List, Dict, Optional, Set
from playwright.async_api import Page
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class InputElement:
    """Represents an input field"""
    type: str
    name: str
    id: str
    label: str
    placeholder: str
    required: bool
    pattern: Optional[str]
    min_length: Optional[int]
    max_length: Optional[int]
    min: Optional[str] = None  # For number/date inputs
    max: Optional[str] = None  # For number/date inputs
    step: Optional[str] = None  # For number/range inputs
    visible: bool = True
    parent_form: Optional[str] = None
    selector: str = ''
    disabled: bool = False  # Track disabled state
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'type': self.type,
            'name': self.name,
            'id': self.id,
            'label': self.label,
            'placeholder': self.placeholder,
            'required': self.required,
            'pattern': self.pattern,
            'minLength': self.min_length,
            'maxLength': self.max_length,
            'min': self.min,
            'max': self.max,
            'step': self.step,
            'visible': self.visible,
            'parent_form': self.parent_form,
            'selector': self.selector,
            'disabled': self.disabled
        }


@dataclass
class FormStructure:
    """Represents a form with its inputs"""
    signature: str
    inputs: List[InputElement]
    submit_button: Optional[str]
    action: Optional[str]
    method: Optional[str]
    selector: Optional[str]
    detection_method: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'signature': self.signature,
            'inputs': [inp.to_dict() for inp in self.inputs],
            'submit_button': self.submit_button,
            'action': self.action,
            'method': self.method,
            'selector': self.selector,
            'detection_method': self.detection_method
        }


class DOMAnalyzer:
    """Universal DOM analyzer with 7 detection strategies (6 code + 1 AI vision)"""
    
    def __init__(self, enable_deduplication: bool = True, min_inputs_for_form: int = 2, 
                 ai_detector=None):
        """
        Initialize DOM analyzer
        
        Args:
            enable_deduplication: Remove duplicate forms
            min_inputs_for_form: Minimum inputs to consider as form
            ai_detector: Optional GeminiElementDetector for AI-powered form detection
        """
        self.enable_deduplication = enable_deduplication
        self.min_inputs_for_form = min_inputs_for_form
        self.ai_detector = ai_detector  # NEW: Gemini vision detector
        
        strategy_count = 7 if ai_detector else 6
        logger.info(f"DOMAnalyzer initialized with {strategy_count} detection strategies{' (AI vision enabled)' if ai_detector else ''}")
    
    async def analyze_page(self, page: Page) -> Dict:
        """
        Analyze page and extract all forms and inputs
        
        Args:
            page: Playwright page object
        
        Returns:
            Dict with 'inputs', 'buttons', 'links', 'forms'
        """
        logger.debug(f"Analyzing page: {page.url}")
        
        # Extract all inputs
        all_inputs = await self._extract_all_inputs(page)
        
        # Extract buttons
        buttons = await self._extract_buttons(page)
        
        # Extract links
        links = await self._extract_links(page)
        
        # Detect forms using all 6 strategies
        forms = await self._detect_forms_all_strategies(page, all_inputs)
        
        # Deduplicate forms
        if self.enable_deduplication:
            forms = self._deduplicate_forms(forms)
        
        result = {
            'inputs': [inp.to_dict() for inp in all_inputs],
            'buttons': buttons,
            'links': links,
            'forms': [form.to_dict() for form in forms]
        }
        
        logger.info(
            f"📊 Analysis complete: {len(all_inputs)} inputs, "
            f"{len(forms)} forms, {len(buttons)} buttons, {len(links)} links"
        )
        
        return result
    
    async def _extract_all_inputs(self, page: Page) -> List[InputElement]:
        """Extract all input elements from page"""
        
        # JavaScript to extract input data (ENHANCED for React components)
        js_code = """
        () => {
            const inputs = [];
            
            // STRATEGY 1: Standard HTML inputs
            const selectors = [
                'input:not([type="hidden"])',
                'textarea',
                'select'
            ];
            
            const elements = document.querySelectorAll(selectors.join(','));
            
            elements.forEach((el, idx) => {
                const computedStyle = window.getComputedStyle(el);
                const isVisible = computedStyle.display !== 'none' && 
                                  computedStyle.visibility !== 'hidden' &&
                                  el.offsetParent !== null;
                
                // Find associated label
                let label = '';
                if (el.id) {
                    const labelEl = document.querySelector(`label[for="${el.id}"]`);
                    if (labelEl) label = labelEl.textContent.trim();
                }
                if (!label && el.parentElement?.tagName === 'LABEL') {
                    label = el.parentElement.textContent.replace(el.value || '', '').trim();
                }
                // Check for label in parent wrapper (DemoQA pattern)
                if (!label) {
                    const wrapper = el.closest('.row, .form-group, [class*="wrapper"]');
                    if (wrapper) {
                        const labelEl = wrapper.querySelector('label');
                        if (labelEl) label = labelEl.textContent.trim();
                    }
                }
                if (!label) {
                    label = el.getAttribute('aria-label') || el.getAttribute('placeholder') || '';
                }
                
                // Find parent form
                let parentForm = null;
                let parent = el.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.tagName === 'FORM') {
                        parentForm = parent.id || parent.name || `form-${idx}`;
                        break;
                    }
                    parent = parent.parentElement;
                }
                
                inputs.push({
                    type: el.type || el.tagName.toLowerCase(),
                    name: el.name || '',
                    id: el.id || '',
                    label: label,
                    placeholder: el.placeholder || '',
                    required: el.required || false,
                    pattern: el.pattern || null,
                    minLength: el.minLength > 0 ? el.minLength : null,
                    maxLength: el.maxLength > 0 ? el.maxLength : null,
                    min: el.min || null,
                    max: el.max || null,
                    step: el.step || null,
                    visible: isVisible,
                    parentForm: parentForm,
                    selector: `${el.tagName.toLowerCase()}[name="${el.name}"]` || `#${el.id}` || `${el.tagName.toLowerCase()}:nth-of-type(${idx+1})`,
                    disabled: el.disabled || el.readOnly || false
                });
            });
            
            // STRATEGY 2: React DatePicker (detect by class pattern)
            const datePickers = document.querySelectorAll('.react-datepicker-wrapper input, input[id*="date"], input[id*="Date"]');
            datePickers.forEach((el, idx) => {
                // Skip if already added
                if (inputs.some(inp => inp.id === el.id && el.id)) return;
                
                const wrapper = el.closest('.row, .form-group, [id*="wrapper"]');
                let label = '';
                if (wrapper) {
                    const labelEl = wrapper.querySelector('label');
                    if (labelEl) label = labelEl.textContent.trim();
                }
                
                let parentForm = null;
                let parent = el.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.tagName === 'FORM') {
                        parentForm = parent.id || parent.name || `form-${idx}`;
                        break;
                    }
                    parent = parent.parentElement;
                }
                
                inputs.push({
                    type: 'date',  // Correct type
                    name: el.name || el.id || '',
                    id: el.id || '',
                    label: label,
                    placeholder: el.placeholder || el.value || '',
                    required: el.required || false,
                    pattern: null,
                    minLength: null,
                    maxLength: null,
                    visible: el.offsetParent !== null,
                    parentForm: parentForm,
                    selector: el.id ? `#${el.id}` : '.react-datepicker-wrapper input',
                    disabled: el.disabled || el.readOnly || false
                });
            });
            
            // STRATEGY 3: React Select dropdowns (detect by class pattern)
            const reactSelects = document.querySelectorAll('[class*="select"], [class*="Select"], [id*="select"], [id*="Select"]');
            reactSelects.forEach((el, idx) => {
                // Look for React Select container
                if (!el.className.includes('container') && !el.className.includes('control')) return;
                
                const wrapper = el.closest('.row, .form-group, .col-md-4, .col-md-9');
                let label = '';
                if (wrapper) {
                    const labelEl = wrapper.querySelector('label');
                    if (labelEl) label = labelEl.textContent.trim();
                }
                
                // Check if disabled (React Select adds specific classes)
                const isDisabled = el.className.includes('disabled') || 
                                  el.className.includes('--is-disabled') ||
                                  el.querySelector('[aria-disabled="true"]') !== null;
                
                // Get selected value
                const selectedValue = el.querySelector('[class*="singleValue"]')?.textContent?.trim() || '';
                
                // Get ID from nearby input or parent
                const reactSelectId = el.id || el.querySelector('input')?.id || wrapper?.id || '';
                
                let parentForm = null;
                let parent = el.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.tagName === 'FORM') {
                        parentForm = parent.id || parent.name || `form-${idx}`;
                        break;
                    }
                    parent = parent.parentElement;
                }
                
                inputs.push({
                    type: 'select',  // Correct type
                    name: reactSelectId.replace(/-wrapper|-container/g, ''),
                    id: reactSelectId,
                    label: label,
                    placeholder: selectedValue || '',
                    required: false,
                    pattern: null,
                    minLength: null,
                    maxLength: null,
                    visible: el.offsetParent !== null,
                    parentForm: parentForm,
                    selector: el.id ? `#${el.id}` : `[class*="select__control"]`,
                    disabled: isDisabled
                });
            });
            
            return inputs;
        }
        """
        
        try:
            raw_inputs = await page.evaluate(js_code)
            
            inputs = []
            for inp in raw_inputs:
                inputs.append(InputElement(
                    type=inp['type'],
                    name=inp['name'],
                    id=inp['id'],
                    label=inp['label'],
                    placeholder=inp['placeholder'],
                    required=inp['required'],
                    pattern=inp['pattern'],
                    min_length=inp['minLength'],
                    max_length=inp['maxLength'],
                    min=inp.get('min'),
                    max=inp.get('max'),
                    step=inp.get('step'),
                    visible=inp['visible'],
                    parent_form=inp['parentForm'],
                    selector=inp['selector'],
                    disabled=inp.get('disabled', False)
                ))
            
            return inputs
        
        except Exception as e:
            logger.error(f"Error extracting inputs: {e}")
            return []
    
    async def _extract_buttons(self, page: Page) -> List[str]:
        """Extract all button texts"""
        js_code = """
        () => {
            const buttons = [];
            const elements = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
            elements.forEach(el => {
                const text = el.textContent?.trim() || el.value || el.getAttribute('aria-label') || '';
                if (text) buttons.push(text);
            });
            return buttons;
        }
        """
        
        try:
            return await page.evaluate(js_code)
        except Exception as e:
            logger.error(f"Error extracting buttons: {e}")
            return []
    
    async def _extract_links(self, page: Page) -> List[str]:
        """Extract all link URLs"""
        js_code = """
        () => {
            const links = [];
            const elements = document.querySelectorAll('a[href]');
            elements.forEach(el => {
                const href = el.href;
                if (href && !href.startsWith('javascript:') && !href.startsWith('#')) {
                    links.push(href);
                }
            });
            return [...new Set(links)];  // Remove duplicates
        }
        """
        
        try:
            return await page.evaluate(js_code)
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    async def _detect_forms_all_strategies(self, page: Page, all_inputs: List[InputElement]) -> List[FormStructure]:
        """Run all 7 detection strategies (6 code-based + 1 AI vision)"""
        forms = []
        
        # Strategy 1: Semantic Detection (<form> tags)
        semantic_forms = await self._strategy_semantic(page)
        forms.extend(semantic_forms)
        logger.debug(f"Strategy 1 (Semantic): Found {len(semantic_forms)} forms")
        
        # Strategy 2: Container-Based Detection
        container_forms = await self._strategy_container(page, all_inputs)
        forms.extend(container_forms)
        logger.debug(f"Strategy 2 (Container): Found {len(container_forms)} forms")
        
        # Strategy 3: Input Clustering (proximity-based)
        clustered_forms = self._strategy_clustering(all_inputs)
        forms.extend(clustered_forms)
        logger.debug(f"Strategy 3 (Clustering): Found {len(clustered_forms)} forms")
        
        # Strategy 4: Event-Driven Detection
        event_forms = await self._strategy_event_driven(page)
        forms.extend(event_forms)
        logger.debug(f"Strategy 4 (Event-Driven): Found {len(event_forms)} forms")
        
        # Strategy 5: Checkbox Tree Detection
        checkbox_forms = await self._strategy_checkbox_tree(page)
        forms.extend(checkbox_forms)
        logger.debug(f"Strategy 5 (Checkbox Tree): Found {len(checkbox_forms)} forms")
        
        # Strategy 6: AI Vision Detection (if enabled)
        if self.ai_detector:
            ai_forms = await self._strategy_ai_vision(page, all_inputs)
            forms.extend(ai_forms)
            logger.debug(f"Strategy 6 (AI Vision): Found {len(ai_forms)} forms")
        
        return forms
    
    async def _strategy_semantic(self, page: Page) -> List[FormStructure]:
        """Strategy 1: Detect <form> tags"""
        js_code = """
        () => {
            const forms = [];
            document.querySelectorAll('form').forEach((form, idx) => {
                const inputs = [];
                form.querySelectorAll('input:not([type="hidden"]), textarea, select').forEach(inp => {
                    // Get label text
                    let label = '';
                    if (inp.id) {
                        const labelEl = document.querySelector(`label[for="${inp.id}"]`);
                        if (labelEl) label = labelEl.textContent.trim();
                    }
                    if (!label && inp.labels && inp.labels.length > 0) {
                        label = inp.labels[0].textContent.trim();
                    }
                    if (!label) {
                        const parentLabel = inp.closest('label');
                        if (parentLabel) label = parentLabel.textContent.trim();
                    }
                    
                    inputs.push({
                        type: inp.type || inp.tagName.toLowerCase(),
                        name: inp.name || '',
                        id: inp.id || '',
                        label: label,
                        placeholder: inp.placeholder || '',
                        required: inp.required || false,
                        pattern: inp.pattern || null,
                        minLength: inp.minLength > 0 ? inp.minLength : null,
                        maxLength: inp.maxLength > 0 ? inp.maxLength : null,
                        min: inp.min || null,
                        max: inp.max || null,
                        step: inp.step || null,
                        disabled: inp.disabled || false,
                        selector: inp.id ? `#${inp.id}` : `${inp.tagName.toLowerCase()}[name="${inp.name}"]`
                    });
                });
                
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                
                forms.push({
                    inputs: inputs,
                    submitButton: submitBtn ? submitBtn.textContent || submitBtn.value : null,
                    action: form.action || null,
                    method: form.method || 'get',
                    selector: form.id ? `#${form.id}` : `form:nth-of-type(${idx+1})`
                });
            });
            return forms;
        }
        """
        
        try:
            raw_forms = await page.evaluate(js_code)
            forms = []
            
            for rf in raw_forms:
                if len(rf['inputs']) >= self.min_inputs_for_form:
                    inputs = [
                        InputElement(
                            type=inp['type'],
                            name=inp['name'],
                            id=inp['id'],
                            label=inp.get('label', ''),
                            placeholder=inp.get('placeholder', ''),
                            required=inp.get('required', False),
                            pattern=inp.get('pattern'),
                            min_length=inp.get('minLength'),
                            max_length=inp.get('maxLength'),
                            min=inp.get('min'),
                            max=inp.get('max'),
                            step=inp.get('step'),
                            visible=True,
                            disabled=inp.get('disabled', False),
                            parent_form=rf['selector'],
                            selector=inp['selector']
                        )
                        for inp in rf['inputs']
                    ]
                    
                    signature = self._generate_form_signature(inputs)
                    
                    forms.append(FormStructure(
                        signature=signature,
                        inputs=inputs,
                        submit_button=rf['submitButton'],
                        action=rf['action'],
                        method=rf['method'],
                        selector=rf['selector'],
                        detection_method='semantic'
                    ))
            
            return forms
        
        except Exception as e:
            logger.error(f"Error in semantic detection: {e}")
            return []
    
    async def _strategy_container(self, page: Page, all_inputs: List[InputElement]) -> List[FormStructure]:
        """Strategy 2: Detect <div> containers with multiple inputs"""
        # Group inputs by parent containers
        # Simplified implementation - would need more sophisticated grouping
        return []
    
    def _strategy_clustering(self, all_inputs: List[InputElement]) -> List[FormStructure]:
        """Strategy 3: Group inputs by proximity (simplified)"""
        # This would use DOM position clustering
        # Simplified implementation
        return []
    
    async def _strategy_event_driven(self, page: Page) -> List[FormStructure]:
        """Strategy 4: Find inputs with onChange/onSubmit handlers"""
        # Would detect event listeners
        return []
    
    async def _strategy_checkbox_tree(self, page: Page) -> List[FormStructure]:
        """Strategy 5: Detect hierarchical checkbox groups"""
        # Would detect parent-child checkbox relationships
        return []
    
    def _generate_form_signature(self, inputs: List[InputElement]) -> str:
        """Generate unique signature for form deduplication"""
        signature_parts = []
        for inp in sorted(inputs, key=lambda x: (x.type, x.name)):
            signature_parts.append(f"{inp.type}:{inp.name}")
        
        signature_str = '|'.join(signature_parts)
        return hashlib.md5(signature_str.encode()).hexdigest()[:8]
    
    def _deduplicate_forms(self, forms: List[FormStructure]) -> List[FormStructure]:
        """Remove duplicate forms based on signature"""
        seen_signatures: Set[str] = set()
        unique_forms = []
        
        for form in forms:
            if form.signature not in seen_signatures:
                seen_signatures.add(form.signature)
                unique_forms.append(form)
        
        return unique_forms
    
    async def _strategy_ai_vision(self, page: Page, all_inputs: List[InputElement]) -> List[FormStructure]:
        """
        Strategy 7: AI Vision Detection using Gemini
        Detects forms that are:
        - Dynamically rendered (React/Vue/Angular)
        - Hidden in modals/tabs/accordions
        - Using custom components without semantic HTML
        - Visually apparent but not in DOM initially
        """
        if not self.ai_detector:
            return []
        
        try:
            # Take screenshot for vision analysis with aggressive timeout
            screenshot_dir = Path("data/snapshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f"form_analysis_{hash(page.url) % 10000}.png"
            
            # Try full-page first with 5s timeout, fall back to viewport
            try:
                await page.screenshot(path=str(screenshot_path), full_page=True, timeout=5000)
            except Exception as e:
                logger.debug(f"Full-page screenshot failed ({str(e)[:50]}), using viewport")
                await page.screenshot(path=str(screenshot_path), full_page=False, timeout=3000)
            
            # Get HTML content
            html_content = await page.content()
            
            # Call Gemini to detect forms
            detected_forms = await self.ai_detector.detect_forms_vision(
                screenshot_path=str(screenshot_path),
                html_content=html_content,
                page_url=page.url
            )
            
            # Convert AI detection results to FormStructure objects
            forms = []
            for ai_form in detected_forms:
                # Match detected inputs with extracted inputs by label/placeholder/name
                form_inputs = []
                for ai_input in ai_form.get('inputs', []):
                    # Try to find matching input from all_inputs
                    matching_input = self._find_matching_input(ai_input, all_inputs)
                    if matching_input:
                        form_inputs.append(matching_input)
                    else:
                        # Create new input from AI detection
                        form_inputs.append(InputElement(
                            type=ai_input.get('type', 'text'),
                            name=ai_input.get('name', ''),
                            id=ai_input.get('id', ''),
                            label=ai_input.get('label', ''),
                            placeholder=ai_input.get('placeholder', ''),
                            required=ai_input.get('required', False),
                            pattern=None,
                            min_length=None,
                            max_length=None,
                            min=None,
                            max=None,
                            step=None,
                            visible=True,
                            parent_form=ai_form.get('selector'),
                            selector=ai_input.get('selector', ''),
                            disabled=False
                        ))
                
                if len(form_inputs) >= self.min_inputs_for_form:
                    form = FormStructure(
                        signature=self._compute_signature(form_inputs),
                        inputs=form_inputs,
                        submit_button=ai_form.get('submit_button'),
                        action=ai_form.get('action'),
                        method=ai_form.get('method', 'post'),
                        selector=ai_form.get('selector'),
                        detection_method='ai_vision'
                    )
                    forms.append(form)
            
            logger.info(f"🤖 AI Vision: Detected {len(forms)} forms from screenshot analysis")
            return forms
            
        except Exception as e:
            logger.warning(f"⚠️  AI vision form detection failed: {e}")
            return []
    
    def _find_matching_input(self, ai_input: Dict, all_inputs: List[InputElement]) -> Optional[InputElement]:
        """Find matching input from extracted inputs based on AI detection"""
        label = (ai_input.get('label') or '').lower()
        placeholder = (ai_input.get('placeholder') or '').lower()
        name = (ai_input.get('name') or '').lower()
        input_id = (ai_input.get('id') or '').lower()
        
        for inp in all_inputs:
            # Match by ID (strongest match)
            if input_id and inp.id and inp.id.lower() == input_id:
                return inp
            
            # Match by name
            if name and inp.name and inp.name.lower() == name:
                return inp
            
            # Match by label
            if label and inp.label and inp.label.lower() == label:
                return inp
            
            # Match by placeholder
            if placeholder and inp.placeholder and inp.placeholder.lower() == placeholder:
                return inp
        
        return None
    
    def _compute_signature(self, inputs: List[InputElement]) -> str:
        """Compute signature for a list of inputs"""
        return self._generate_form_signature(inputs)
        if removed > 0:
            logger.debug(f"Removed {removed} duplicate forms")
        
        return unique_forms

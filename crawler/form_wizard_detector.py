"""
Multi-Step Form Wizard Detector
Detects and navigates through multi-step forms/wizards for testing
"""
from typing import List, Dict, Optional
import json as _json_mod
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

ACTION_TIMEOUT = 8_000  # ms

logger = setup_logger(__name__)


class FormWizardDetector:
    """Detects and navigates multi-step forms"""
    
    def __init__(self):
        self.wizard_indicators = [
            'next', 'continue', 'step', 'proceed', 'forward',
            'siguiente', 'continuar', 'weiter'  # Multi-language support
        ]
        self.step_indicators = [
            'step', 'etapa', 'schritt', 'phase', 'stage'
        ]
    
    async def detect_wizard(self, page: Page) -> bool:
        """Check if current page contains a multi-step form"""
        js_code = f"""
        () => {{
            // Strategy 1: Look for step indicators
            const stepIndicators = {self.step_indicators};
            const hasStepIndicator = Array.from(document.querySelectorAll('*'))
                .some(el => {{
                    const text = el.textContent.toLowerCase();
                    return stepIndicators.some(indicator => 
                        new RegExp(`${{indicator}}\\\\s*\\\\d|\\\\d\\\\s*of\\\\s*\\\\d`, 'i').test(text)
                    );
                }});
            
            // Strategy 2: Look for next/continue buttons
            const wizardButtons = {self.wizard_indicators};
            const hasWizardButton = Array.from(document.querySelectorAll('button, a, input[type="submit"], input[type="button"]'))
                .some(el => {{
                    const text = (el.textContent || el.value || '').toLowerCase();
                    return wizardButtons.some(indicator => text.includes(indicator));
                }});
            
            // Strategy 3: Look for progress bars
            const hasProgressBar = document.querySelector('[class*="progress"], [class*="stepper"], [role="progressbar"]') !== null;
            
            // Strategy 4: Look for fieldset with legend (common in wizards)
            const hasFieldsetStructure = document.querySelectorAll('fieldset').length > 1;
            
            return hasStepIndicator || (hasWizardButton && (hasProgressBar || hasFieldsetStructure));
        }}
        """
        
        try:
            is_wizard = await page.evaluate(js_code)
            if is_wizard:
                logger.info("🧙 Multi-step wizard detected")
            return is_wizard
        except Exception as e:
            logger.debug(f"Wizard detection error: {e}")
            return False
    
    async def navigate_wizard_steps(self, page: Page, max_steps: int = 5, ai_detector=None) -> List[Dict]:
        """
        Navigate through wizard steps and collect form data from each step
        
        Returns:
            List of form analyses for each step
        """
        steps_data = []
        current_step = 1
        
        from crawler.dom_analyzer import DOMAnalyzer
        dom_analyzer = DOMAnalyzer(ai_detector=ai_detector)
        
        while current_step <= max_steps:
            logger.info(f"📋 Analyzing wizard step {current_step}...")
            
            # Log which step container is currently visible
            try:
                visible_step_check = await page.evaluate("""
                    () => {
                        // Check which .form-step has the 'active' class
                        const activeFormStep = document.querySelector('.form-step.active');
                        if (activeFormStep) {
                            const stepNum = activeFormStep.getAttribute('data-step');
                            return {stepIndex: stepNum, stepId: activeFormStep.id || 'no-id', classes: activeFormStep.className};
                        }
                        
                        // Fallback: check progress indicator
                        const steps = document.querySelectorAll('.step.active');
                        if (steps.length > 0) {
                            const step = steps[0];
                            return {stepIndex: step.getAttribute('data-step'), stepId: step.id || 'progress-indicator', classes: step.className};
                        }
                        
                        return {stepIndex: 'unknown', stepId: 'none', classes: 'none'};
                    }
                """)
                logger.info(f"  👁️  Visible step container: Step {visible_step_check['stepIndex']} (ID: {visible_step_check['stepId']})")
                
                # CRITICAL: If visible step doesn't match current_step, DOM state is wrong
                if visible_step_check['stepIndex'] and visible_step_check['stepIndex'] != 'unknown':
                    expected_step = str(current_step)
                    actual_step = visible_step_check['stepIndex']
                    if actual_step != expected_step:
                        logger.error(f"  ❌ STEP MISMATCH: Expected step {expected_step}, but DOM shows step {actual_step}")
                        logger.error(f"  ❌ This means page reloaded or step state was lost!")
                        # Sync to actual step shown in DOM
                        current_step = int(actual_step)
                        logger.info(f"  🔄 Synced to actual DOM step: {current_step}")
            except Exception as e:
                logger.debug(f"  Could not check visible step: {e}")
            
            # Analyze current step
            try:
                # CRITICAL: Extended wait to ensure DOM fully updated
                # The wait_for_function confirms step changed, but DOM may still be re-rendering
                await page.wait_for_timeout(1500)  # Increased from 500ms
                
                # DOUBLE-CHECK: Verify the active step one more time before analyzing
                final_check = await page.evaluate("""
                    () => {
                        const activeStep = document.querySelector('.form-step.active');
                        return activeStep ? activeStep.getAttribute('data-step') : null;
                    }
                """)
                logger.info(f"  ✅ Final verification: Active step is {final_check}")
                
                # CRITICAL FIX: Disable AI vision for wizard steps!
                # full_page=True screenshot scrolls the page and might trigger JavaScript that resets wizard
                # Save original AI detector state
                original_ai_detector = dom_analyzer.ai_detector
                dom_analyzer.ai_detector = None  # Temporarily disable AI vision
                
                analysis = await dom_analyzer.analyze_page(page)
                
                # Restore AI detector
                dom_analyzer.ai_detector = original_ai_detector
                
                current_url = page.url
                title = await page.title()
                
                # DEBUG: Check what querySelector actually returns
                debug_info = await page.evaluate("""
                    () => {
                        // CRITICAL: Check ALL elements with .form-step.active class
                        const allActiveSteps = Array.from(document.querySelectorAll('.form-step.active'));
                        
                        if (allActiveSteps.length === 0) return {error: 'No active step found'};
                        
                        // Return info about ALL active steps (should only be 1!)
                        return {
                            totalActiveSteps: allActiveSteps.length,
                            activeSteps: allActiveSteps.map(step => ({
                                stepNum: step.getAttribute('data-step'),
                                stepId: step.id || 'no-id',
                                stepClass: step.className,
                                display: window.getComputedStyle(step).display,
                                visibility: window.getComputedStyle(step).visibility,
                                inputCount: step.querySelectorAll('input, select, textarea').length,
                                inputIds: Array.from(step.querySelectorAll('input, select, textarea')).map(i => i.id || i.name)
                            }))
                        };
                    }
                """)
                logger.info(f"  🔍 DEBUG querySelector result: {debug_info}")
                
                # CRITICAL FIX: Filter to only VISIBLE inputs FROM ACTIVE STEP CONTAINER
                visible_inputs = await self._get_visible_inputs(page)
                visible_buttons = await self._get_visible_buttons(page)
                
                # LOG: Show what inputs were detected for debugging
                logger.info(f"  📝 Detected input IDs: {[inp.get('id') or inp.get('name') for inp in visible_inputs]}")
                
                steps_data.append({
                    'step': current_step,
                    'url': current_url,
                    'title': f"{title} - Step {current_step}",
                    'forms': analysis.get('forms', []),
                    'inputs': visible_inputs,  # Only visible inputs
                    'buttons': visible_buttons,  # Only visible buttons
                    'file_inputs': analysis.get('file_inputs', []),
                    'all_inputs': analysis.get('inputs', []),  # Keep full list for reference
                })
                
                logger.info(f"  ✅ Step {current_step}: {len(visible_inputs)} visible inputs, {len(analysis.get('forms', []))} forms")
            except Exception as e:
                logger.error(f"Error analyzing step {current_step}: {e}")
                break
            
            # Find "Next" / "Continue" button
            next_button = await self._find_next_button(page)
            if not next_button:
                logger.info(f"  ℹ️  No 'Next' button found - end of wizard (step {current_step})")
                break
            
            # Fill ALL fields (not just required) to ensure validation passes
            try:
                logger.info(f"  🖊️  Attempting to fill {len(visible_inputs)} visible inputs...")
                filled_count = await self._fill_all_visible_fields(page, visible_inputs)
                logger.info(f"  ✅ Successfully filled {filled_count} fields")
            except Exception as e:
                logger.warning(f"⚠️  Error filling fields: {e}")
            
            # Click next button via Playwright API (supports :has-text() selectors)
            try:
                btn_el = await page.query_selector(next_button)
                if not btn_el:
                    logger.warning(f"  ⚠️  Next button selector '{next_button}' resolved to None - stopping")
                    break

                # Capture current visible input IDs BEFORE clicking — used as change signal
                pre_click_ids = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('input:not([type=hidden]),select,textarea'))
                             .filter(el => el.getBoundingClientRect().width > 0)
                             .map(el => el.id || el.name || el.type)
                """)

                await btn_el.scroll_into_view_if_needed()
                await page.wait_for_timeout(200)
                await btn_el.click(timeout=ACTION_TIMEOUT)

                # ── Wait for DOM change ─────────────────────────────────────────────
                # Strategy A: explicit .form-step[data-step] attribute (DemoQA style)
                advanced = False
                try:
                    await page.wait_for_function(
                        f"""
                        () => {{
                            // Strategy A: data-step attribute
                            const formSteps = document.querySelectorAll('.form-step');
                            for (const s of formSteps) {{
                                if (s.classList.contains('active') &&
                                    s.getAttribute('data-step') === '{current_step + 1}') {{
                                    return true;
                                }}
                            }}
                            // Strategy B: any step container change (aria, tab-pane, etc.)
                            const panels = document.querySelectorAll(
                                '[role="tabpanel"]:not([hidden]), .tab-pane.active.show,'
                                + '.wizard-step.active, [data-wizard-state="current"]'
                            );
                            return panels.length > 0;
                        }}
                        """,
                        timeout=4000,
                    )
                    advanced = True
                    logger.info(f"  ✅ DOM updated (attribute-based) - entering step {current_step + 1}")
                except Exception:
                    pass  # Try Strategy C

                if not advanced:
                    # Strategy C: wait for the set of visible inputs to change
                    try:
                        import json as _json
                        pre_ids_str = _json.dumps(sorted(pre_click_ids))
                        await page.wait_for_function(
                            f"""
                            () => {{
                                const pre = {pre_ids_str};
                                const cur = Array.from(
                                    document.querySelectorAll('input:not([type=hidden]),select,textarea')
                                ).filter(el => el.getBoundingClientRect().width > 0)
                                 .map(el => el.id || el.name || el.type);
                                cur.sort();
                                return JSON.stringify(cur) !== JSON.stringify(pre);
                            }}
                            """,
                            timeout=4000,
                        )
                        advanced = True
                        logger.info(f"  ✅ Visible inputs changed after Next click - step progressed")
                    except Exception as e:
                        logger.warning(f"  ⚠️  No DOM change detected after Next click: {e}")

                if not advanced:
                    logger.warning(f"  ⚠️  Wizard stuck at step {current_step} - validation may have failed")
                    break

                current_step += 1
                await page.wait_for_timeout(600)  # allow animations to finish

            except Exception as e:
                logger.warning(f"⚠️  Could not proceed to next step: {e}")
                break
        
        logger.info(f"🧙 Wizard complete: collected data from {len(steps_data)} steps")
        return steps_data
    
    async def _fill_required_fields(self, page: Page, visible_inputs: List[Dict]) -> int:
        """Fill required fields with test data, returns count of filled fields"""
        filled_count = 0
        
        for input_field in visible_inputs:
            if not input_field.get('required'):
                continue
            
            try:
                input_type = input_field.get('type', 'text')
                field_id = input_field.get('id')
                field_name = input_field.get('name')
                
                # Construct selector
                if field_id:
                    selector = f"#{field_id}"
                elif field_name:
                    selector = f"[name='{field_name}']"
                else:
                    continue
                
                # Fill based on type
                if input_type == 'radio':
                    # Click first radio in group
                    await page.click(selector, timeout=2000)
                    logger.info(f"  📝 Filled radio: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'checkbox':
                    await page.check(selector, timeout=2000)
                    logger.info(f"  📝 Checked: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'select-one':
                    # Select first non-empty option
                    await page.select_option(selector, index=1, timeout=2000)
                    logger.info(f"  📝 Selected: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'email':
                    await page.fill(selector, "test@example.com", timeout=2000)
                    logger.info(f"  📝 Filled email: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'tel':
                    await page.fill(selector, "1234567890", timeout=2000)
                    logger.info(f"  📝 Filled phone: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'date':
                    await page.fill(selector, "2000-01-01", timeout=2000)
                    logger.info(f"  📝 Filled date: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'password':
                    await page.fill(selector, "TestPassword123!", timeout=2000)
                    logger.info(f"  📝 Filled password: {field_name or field_id}")
                    filled_count += 1
                    
                elif input_type == 'textarea':
                    await page.fill(selector, "Test address content", timeout=2000)
                    logger.info(f"  📝 Filled textarea: {field_name or field_id}")
                    filled_count += 1
                    
                else:  # text and others
                    await page.fill(selector, f"Test_{field_name or field_id}", timeout=2000)
                    logger.info(f"  📝 Filled text: {field_name or field_id}")
                    filled_count += 1
                    
            except Exception as e:
                logger.debug(f"  ⚠️  Could not fill {input_field.get('name')}: {e}")
                continue
        
        return filled_count
    
    async def _fill_all_visible_fields(self, page: Page, visible_inputs: List[Dict]) -> int:
        """Fill ALL visible fields (required or not) to maximize form progression success"""
        filled_count = 0
        
        for input_field in visible_inputs:
            try:
                input_type = input_field.get('type', 'text')
                field_id = input_field.get('id')
                field_name = input_field.get('name')
                
                # Construct selector
                if field_id:
                    selector = f"#{field_id}"
                elif field_name:
                    selector = f"[name='{field_name}']"
                else:
                    continue
                
                # Fill based on type
                if input_type == 'radio':
                    # Check if NOT already checked
                    is_checked = await page.evaluate(f"""
                        () => {{
                            const radios = document.querySelectorAll('[name="{field_name}"]');
                            return Array.from(radios).some(r => r.checked);
                        }}
                    """)
                    
                    if not is_checked:
                        await page.click(selector, timeout=2000)
                        logger.info(f"  📝 Filled radio: {field_name or field_id}")
                        filled_count += 1
                    
                elif input_type == 'checkbox':
                    # Check if NOT already checked
                    is_checked = await page.is_checked(selector, timeout=1000)
                    if not is_checked:
                        await page.check(selector, timeout=2000)
                        logger.info(f"  📝 Checked: {field_name or field_id}")
                        filled_count += 1
                    
                elif input_type == 'select-one':
                    # Check if no option selected
                    current_value = await page.evaluate(f"""
                        () => document.querySelector('{selector}')?.value || ''
                    """)
                    if not current_value:
                        await page.select_option(selector, index=1, timeout=2000)
                        logger.info(f"  📝 Selected: {field_name or field_id}")
                        filled_count += 1
                    
                elif input_type in ['email', 'text', 'tel', 'date', 'password', 'textarea']:
                    # Check if empty
                    current_value = await page.input_value(selector, timeout=1000)
                    if not current_value:
                        # Fill with appropriate test data
                        if input_type == 'email':
                            await page.fill(selector, "test@example.com", timeout=2000)
                        elif input_type == 'tel':
                            await page.fill(selector, "1234567890", timeout=2000)
                        elif input_type == 'date':
                            await page.fill(selector, "2000-01-01", timeout=2000)
                        elif input_type == 'password':
                            await page.fill(selector, "TestPassword123!", timeout=2000)
                        elif input_type == 'textarea':
                            await page.fill(selector, "Test address content", timeout=2000)
                        else:  # text
                            await page.fill(selector, f"Test_{field_name or field_id}", timeout=2000)
                        
                        logger.info(f"  📝 Filled {input_type}: {field_name or field_id}")
                        filled_count += 1
                    
            except Exception as e:
                logger.debug(f"  ⚠️  Could not fill {input_field.get('name')}: {e}")
                continue
        
        return filled_count

    
    async def _get_visible_inputs(self, page: Page) -> List[Dict]:
        """Get only VISIBLE inputs from the ACTIVE form step container"""
        js_code = """
        () => {
            // CRITICAL: Only look for inputs within the ACTIVE form step
            const activeStep = document.querySelector('.form-step.active');
            if (!activeStep) {
                console.warn('No active form step found!');
                return [];
            }
            
            // DEBUG: Log which step is active
            const stepNum = activeStep.getAttribute('data-step');
            console.log(`Active step: ${stepNum}, ID: ${activeStep.id}, Class: ${activeStep.className}`);
            
            // Get inputs ONLY from active step container
            const inputs = Array.from(activeStep.querySelectorAll('input, select, textarea'));
            console.log(`Found ${inputs.length} inputs in active step ${stepNum}`);
            
            // CRITICAL DEBUG: Return diagnostic info
            const diagnostics = {
                activeStepNumber: stepNum,
                activeStepId: activeStep.id,
                activeStepClass: activeStep.className,
                totalInputsInActiveStep: inputs.length,
                inputDetails: inputs.map(inp => ({
                    id: inp.id,
                    name: inp.name,
                    type: inp.type,
                    parentStep: inp.closest('.form-step')?.getAttribute('data-step')
                }))
            };
            console.log('DIAGNOSTICS:', JSON.stringify(diagnostics, null, 2));
            
            const visibleInputs = [];
            
            function isElementVisible(element) {
                // Check the element itself
                const style = window.getComputedStyle(element);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                    return false;
                }
                
                // Check all parent elements up to active step container
                let parent = element.parentElement;
                while (parent && parent !== activeStep) {
                    const parentStyle = window.getComputedStyle(parent);
                    if (parentStyle.display === 'none' || 
                        parentStyle.visibility === 'hidden' || 
                        parentStyle.opacity === '0') {
                        return false;
                    }
                    parent = parent.parentElement;
                }
                
                // Final check: element must have layout (offsetParent)
                // Exception: fixed/absolute positioned elements may have null offsetParent
                if (element.offsetParent === null && style.position !== 'fixed') {
                    return false;
                }
                
                return true;
            }
            
            for (const input of inputs) {
                if (isElementVisible(input)) {
                    visibleInputs.push({
                        tag: input.tagName.toLowerCase(),
                        type: input.type || 'text',
                        name: input.name || '',
                        id: input.id || '',
                        placeholder: input.placeholder || '',
                        required: input.required || false,
                        value: input.value || '',
                        label: input.labels?.[0]?.textContent?.trim() || ''
                    });
                }
            }
            
            console.log(`Returning ${visibleInputs.length} visible inputs from step ${stepNum}`);
            return visibleInputs;
        }
        """
        
        try:
            visible_inputs = await page.evaluate(js_code)

            if visible_inputs:
                logger.debug(f"🔍 JavaScript returned {len(visible_inputs)} inputs from .form-step.active")
            else:
                logger.warning("⚠️  .form-step.active returned empty — trying generic visibility fallback")
                visible_inputs = await self._get_visible_inputs_generic(page)

            return visible_inputs
        except Exception as e:
            logger.error(f"Error getting visible inputs: {e}")
            # Fallback on exception too
            try:
                return await self._get_visible_inputs_generic(page)
            except Exception:
                return []

    async def _get_visible_inputs_generic(self, page: Page) -> List[Dict]:
        """Generic fallback: returns all visible inputs in the page, regardless
        of wizard CSS class structure.  Used when .form-step.active is absent."""
        js_code = """
        () => {
            const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            const skipTypes = new Set(['submit','button','hidden','reset','image','file']);

            function isVisible(el) {
                if (skipTypes.has((el.type || '').toLowerCase())) return false;
                let node = el;
                while (node && node !== document.body) {
                    const s = window.getComputedStyle(node);
                    if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) < 0.05)
                        return false;
                    node = node.parentElement;
                }
                return el.getBoundingClientRect().width > 0;
            }

            return inputs.filter(isVisible).map(inp => ({
                tag: inp.tagName.toLowerCase(),
                type: inp.type || 'text',
                name: inp.name || '',
                id: inp.id || '',
                placeholder: inp.placeholder || '',
                required: inp.required || false,
                value: inp.value || '',
                label: inp.labels && inp.labels[0] ? inp.labels[0].textContent.trim() : ''
            }));
        }
        """
        try:
            result = await page.evaluate(js_code)
            logger.info(f"Generic fallback returned {len(result)} visible inputs")
            return result
        except Exception as e:
            logger.error(f"Generic input fallback failed: {e}")
            return []
    
    async def _get_visible_buttons(self, page: Page) -> List[Dict]:
        """Get only VISIBLE buttons from the current step"""
        js_code = """
        () => {
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]'));
            const visibleButtons = [];
            
            function isElementVisible(element) {
                // Check the element itself
                const style = window.getComputedStyle(element);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                    return false;
                }
                
                // Check all parent elements up to body
                let parent = element.parentElement;
                while (parent && parent !== document.body) {
                    const parentStyle = window.getComputedStyle(parent);
                    if (parentStyle.display === 'none' || 
                        parentStyle.visibility === 'hidden' || 
                        parentStyle.opacity === '0') {
                        return false;
                    }
                    parent = parent.parentElement;
                }
                
                // Final check: element must have layout (offsetParent)
                if (element.offsetParent === null && style.position !== 'fixed') {
                    return false;
                }
                
                return true;
            }
            
            for (const btn of buttons) {
                if (isElementVisible(btn)) {
                    visibleButtons.push({
                        tag: btn.tagName.toLowerCase(),
                        type: btn.type || 'button',
                        text: btn.textContent?.trim() || btn.value || '',
                        id: btn.id || '',
                        class: btn.className || ''
                    });
                }
            }
            
            return visibleButtons;
        }
        """
        
        try:
            visible_buttons = await page.evaluate(js_code)
            return visible_buttons
        except Exception as e:
            logger.debug(f"Error getting visible buttons: {e}")
            return []
    
    async def _find_next_button(self, page: Page) -> Optional[str]:
        """Find the Next/Continue button and return a Playwright-compatible selector.

        Returns a selector that works with ``page.query_selector()`` (which
        supports Playwright's extended CSS, including ``:has-text()``) but
        expressly avoids the plain-CSS ``text="..."`` syntax that only works
        in older Playwright text-selector format and NOT in
        ``document.querySelector()`` inside page.evaluate().
        """
        js_code = f"""
        () => {{
            const wizardButtons = {self.wizard_indicators};

            // Find all potential buttons
            const buttons = Array.from(document.querySelectorAll(
                'button, a, input[type="submit"], input[type="button"], [role="button"]'
            ));

            for (const btn of buttons) {{
                const rawText = (btn.textContent || btn.value || btn.getAttribute('aria-label') || '');
                const text = rawText.toLowerCase().trim();
                const isVisible = btn.offsetParent !== null || 
                                  window.getComputedStyle(btn).position === 'fixed';
                const isNextButton = wizardButtons.some(ind => text.includes(ind));

                if (isNextButton && isVisible) {{
                    // Prefer stable attribute-based selectors (work everywhere)
                    if (btn.id) return '#' + btn.id;
                    if (btn.getAttribute('data-testid')) 
                        return '[data-testid="' + btn.getAttribute('data-testid') + '"]';
                    if (btn.getAttribute('name'))
                        return '[name="' + btn.getAttribute('name') + '"]';
                    // Class-based (CSS-safe)
                    if (btn.className && typeof btn.className === 'string') {{
                        const cls = btn.className.trim().split(/\\s+/).filter(c => c && !c.match(/^(btn|disabled|active|focus)$/i));
                        if (cls.length > 0)
                            return btn.tagName.toLowerCase() + '.' + cls[0];
                    }}
                    // Safe text fallback: encode as data attribute to avoid querySelector issues
                    // Return null here; caller will use :has-text() Playwright selector
                    return '__HASTEXT__' + rawText.trim().substring(0, 40);
                }}
            }}

            return null;
        }}
        """

        try:
            raw = await page.evaluate(js_code)
            if raw is None:
                return None
            if raw.startswith('__HASTEXT__'):
                # Convert to Playwright :has-text() selector — valid in page.query_selector()
                btn_text = raw[len('__HASTEXT__'):]
                return f"button:has-text('{btn_text}')"
            return raw
        except Exception as e:
            logger.debug(f"Error finding next button: {e}")
            return None

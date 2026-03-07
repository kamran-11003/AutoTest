"""
Crawler Orchestrator
Main crawl loop with BFS/DFS, queue management, and crash recovery
"""
import asyncio
from collections import deque
from typing import List, Dict, Optional, Set
from pathlib import Path
import yaml
from datetime import datetime

from crawler.page_loader import PageLoader, manual_login_flow
from crawler.dom_analyzer import DOMAnalyzer
from crawler.url_normalizer import URLNormalizer
from crawler.state_manager import StateManager
from crawler.link_extractor import LinkExtractor
from crawler.ai_enricher import AIEnricher
from crawler.interaction_sim import InteractionSimulator
from crawler.graph_builder import GraphBuilder
from crawler.form_wizard_detector import FormWizardDetector
from crawler.modal_handler import ModalHandler
from crawler.file_upload_detector import FileUploadDetector
from crawler.rate_limiter import RateLimiter
from crawler.shadow_dom_detector import ShadowDOMDetector
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class CrawlerOrchestrator:
    """Orchestrates the entire crawling process"""
    
    def __init__(self, config_path: str = "config/crawler_config.yaml"):
        """
        Initialize crawler orchestrator
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize AI Site Analyzer and Gemini detector (for smart URL normalization and form detection)
        self.ai_site_analyzer = None
        gemini_detector = None  # Define at class level
        
        if self.config['ai_enrichment']['enabled']:
            try:
                from crawler.ai_site_analyzer import AISiteAnalyzer
                from crawler.ai_detector import GeminiElementDetector
                from crawler.gemini_key_rotator import GeminiKeyRotator
                
                key_rotator = GeminiKeyRotator()
                if key_rotator.get_current_key():
                    self.ai_site_analyzer = AISiteAnalyzer(key_rotator=key_rotator)
                    gemini_detector = GeminiElementDetector(key_rotator=key_rotator)
                    logger.info("🧠 AI Site Analyzer enabled (smart URL normalization)")
                    logger.info("🤖 Gemini detector initialized for form/navigation detection")
            except Exception as e:
                logger.warning(f"⚠️  AI components initialization failed: {e}")
        
        # Initialize components
        self.page_loader: Optional[PageLoader] = None
        self.dom_analyzer = DOMAnalyzer(
            enable_deduplication=self.config['form_detection']['deduplication'],
            min_inputs_for_form=self.config['form_detection']['min_inputs_for_form']
        )
        self.url_normalizer = URLNormalizer(
            patterns=self.config['url_normalization']['patterns']
        )
        self.state_manager = StateManager(
            enable_normalization=self.config['url_normalization']['enabled']
        )
        self.link_extractor = LinkExtractor(
            same_origin_only=self.config['link_extraction']['same_origin_only'],
            exclude_patterns=self.config['link_extraction']['exclude_patterns'],
            action_verify_back_enabled=self.config['link_extraction']['action_verify_back']['enabled'],
            max_clickables_per_page=self.config['link_extraction']['action_verify_back']['max_clickables_per_page'],
            use_intelligent_filtering=self.config['link_extraction']['action_verify_back'].get('intelligent_filtering', True),
            save_snapshots=self.config['link_extraction']['action_verify_back'].get('save_snapshots', True),
            state_manager=self.state_manager
        )
        
        # Pass AI detector to link_extractor for enhanced navigation detection
        if gemini_detector:
            self.link_extractor.ai_detector = gemini_detector
            logger.info("🤖 AI-enhanced form detection enabled in DOMAnalyzer")
        
        # Update DOMAnalyzer with AI detector for form detection
        self.dom_analyzer = DOMAnalyzer(
            enable_deduplication=self.config['form_detection']['deduplication'],
            min_inputs_for_form=self.config['form_detection']['min_inputs_for_form'],
            ai_detector=gemini_detector  # Enable AI vision for form detection
        )
        self.ai_enricher = AIEnricher(
            enabled=self.config['ai_enrichment']['enabled'],
            max_dom_size=self.config['ai_enrichment']['max_dom_size'],
            rate_limit_delay=self.config['ai_enrichment']['rate_limit_delay']
        )
        self.interaction_sim = InteractionSimulator(
            click_links=self.config['interaction']['click_links'],
            submit_forms=self.config['interaction']['submit_forms'],
            expand_accordions=self.config['interaction']['expand_accordions'],
            open_modals=self.config['interaction']['open_modals'],
            hover_menus=self.config['interaction']['hover_menus'],
            state_manager=self.state_manager
        )
        self.graph_builder = GraphBuilder()
        
        # NEW: Initialize testing enhancement detectors
        self.wizard_detector = FormWizardDetector()
        self.modal_handler = ModalHandler()
        self.file_upload_detector = FileUploadDetector()
        self.shadow_dom_detector = ShadowDOMDetector()
        self.rate_limiter = RateLimiter(
            min_delay=self.config['crawler'].get('min_delay', 0.5),
            max_delay=self.config['crawler'].get('max_delay', 2.0)
        )
        
        # Store gemini_detector reference for wizard detector
        self.gemini_detector = gemini_detector
        
        logger.info("🧙 Form wizard detector initialized")
        logger.info("🚫 Modal handler initialized")
        logger.info("📎 File upload detector initialized")
        logger.info("🌑 Shadow DOM detector initialized")
        logger.info("⏱️  Rate limiter initialized")
        
        # Crawl state
        self.queue: deque = deque()
        self.visited: Set[str] = set()  # Track visited URLs (for deduplication)
        self.current_depth: Dict[str, int] = {}
        self.start_url: Optional[str] = None
        self.max_depth: int = self.config['crawler']['max_depth']
        self.max_pages: int = self.config['crawler']['max_pages']
        self.pages_crawled: int = 0
        
        logger.info("🚀 CrawlerOrchestrator initialized")
    
    async def start_crawl(
        self,
        start_url: str,
        manual_login: bool = True,
        session_file: str = "auth_session.json",
        max_depth: Optional[int] = None,
        max_pages: Optional[int] = None,
        seed_urls: Optional[List[str]] = None  # NEW: Additional URLs to crawl
    ) -> Dict:
        """
        Start the crawling process
        
        Args:
            start_url: Starting URL
            manual_login: Whether to prompt for manual login
            session_file: Path to session file
            max_depth: Override max depth
            max_pages: Override max pages
            seed_urls: Optional list of additional URLs to add to queue (e.g., ['/products', '/about'])
        
        Returns:
            Crawl results dictionary
        """
        self.start_url = start_url
        if max_depth:
            self.max_depth = max_depth
        if max_pages:
            self.max_pages = max_pages
        
        logger.info(f"🎯 Starting crawl: {start_url}")
        logger.info(f"📊 Config: max_depth={self.max_depth}, max_pages={self.max_pages}")
        if seed_urls:
            logger.info(f"🌱 Seed URLs: {len(seed_urls)} additional URLs provided")
        
        try:
            # Initialize browser
            if manual_login and not Path(session_file).exists():
                logger.info("🔐 Manual login required...")
                self.page_loader = await manual_login_flow(start_url, session_file)
            else:
                self.page_loader = PageLoader(
                    browser_type=self.config['crawler']['browser'],
                    headless=self.config['crawler']['headless'],
                    timeout=self.config['crawler']['timeout_per_page'] * 1000,
                    wait_for=self.config['crawler']['wait_for'],
                    additional_wait=self.config['crawler']['additional_wait']
                )
                
                storage_state = session_file if Path(session_file).exists() else None
                await self.page_loader.start(storage_state=storage_state)
                
                # Navigate to start URL
                await self.page_loader.load_page(start_url)
                
                # Auto-login if credentials provided and no saved session
                if not storage_state:
                    await self._attempt_auto_login()
            
            # CRITICAL: Dismiss immediate popups (newsletters, country selectors, etc.)
            page = await self.page_loader.get_current_page()
            logger.info("🚫 Checking for initial popups/modals...")
            dismissed = await self.modal_handler.dismiss_all_popups(page)
            if dismissed > 0:
                logger.info(f"✅ Cleared {dismissed} initial popup(s)")
            
            # Initialize queue with start URL
            self.queue.append(start_url)
            self.current_depth[start_url] = 0
            
            # Add seed URLs to queue (if provided)
            if seed_urls:
                from urllib.parse import urljoin
                for seed_url in seed_urls:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(start_url, seed_url)
                    if absolute_url not in self.visited and absolute_url not in self.queue:
                        self.queue.append(absolute_url)
                        self.current_depth[absolute_url] = 1  # Depth 1 (directly from seeds)
                        logger.info(f"🌱 Added seed URL: {absolute_url}")
            
            # ONE-TIME SITE ANALYSIS (if AI enabled)
            if self.ai_site_analyzer and self.pages_crawled == 0:
                logger.info("🧠 Performing ONE-TIME site structure analysis...")
                try:
                    # Get homepage HTML
                    page = await self.page_loader.get_current_page()
                    homepage_html = await page.content()
                    
                    # Collect 10 sample URLs for pattern detection (without AI to avoid duplication)
                    logger.info("📡 Collecting sample URLs for pattern detection...")
                    sample_links = await self.link_extractor.extract_all_links(page, start_url, use_ai=False)
                    sample_urls = [start_url] + sample_links[:15]  # Homepage + 15 samples
                    
                    # Analyze site structure
                    from urllib.parse import urlparse
                    domain = urlparse(start_url).netloc
                    site_analysis = await self.ai_site_analyzer.analyze_site_structure(
                        homepage_html,
                        sample_urls,
                        domain
                    )
                    
                    # Update URL normalizer with AI-detected patterns
                    ai_patterns = site_analysis.get('url_normalization', [])
                    if ai_patterns:
                        logger.info(f"🎯 Applying {len(ai_patterns)} AI-detected URL patterns")
                        for pattern_dict in ai_patterns:
                            logger.info(f"   • {pattern_dict['pattern']} → {pattern_dict['replacement']} (confidence: {pattern_dict['confidence']}%)")
                        
                        # Add AI patterns to normalizer
                        self.url_normalizer.patterns.extend([
                            {'pattern': p['pattern'], 'replacement': p['replacement']}
                            for p in ai_patterns if p['confidence'] >= 85
                        ])
                    
                    logger.info("✅ Site analysis complete - patterns cached for all pages")
                
                except Exception as e:
                    logger.warning(f"⚠️  Site analysis failed (continuing with defaults): {e}")
            
            # Run BFS crawl
            await self._breadth_first_crawl()
            
            # Get final stats
            results = self._generate_results()
            
            # Print snapshot report if available
            if self.link_extractor.snapshot_manager:
                self.link_extractor.snapshot_manager.print_report()
                self.link_extractor.snapshot_manager.save_summary()
            
            logger.info("✅ Crawl completed successfully")
            return results
        
        except Exception as e:
            logger.error(f"❌ Crawl failed: {e}")
            raise
        
        finally:
            if self.page_loader:
                await self.page_loader.close()
    
    async def _breadth_first_crawl(self):
        """Execute breadth-first crawl"""
        logger.info("🔄 Starting BFS crawl...")
        
        while self.queue and self.pages_crawled < self.max_pages:
            current_url = self.queue.popleft()
            current_depth = self.current_depth.get(current_url, 0)
            
            # Check depth limit
            if current_depth > self.max_depth:
                logger.debug(f"⏭️  Skipping {current_url} (depth {current_depth} > {self.max_depth})")
                continue
            
            # Check if already visited
            if self.state_manager.is_url_visited(current_url):
                logger.debug(f"⏭️  Skipping {current_url} (already visited)")
                continue
            
            # Crawl page
            try:
                await self._crawl_page(current_url, current_depth)
                self.pages_crawled += 1
                
                # Checkpoint every N pages
                if self.pages_crawled % self.config['state_management']['checkpoint_interval'] == 0:
                    self._save_checkpoint()
                
                logger.info(
                    f"📊 Progress: {self.pages_crawled}/{self.max_pages} pages | "
                    f"Queue: {len(self.queue)} | Depth: {current_depth}"
                )
            
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")
                continue
        
        logger.info(f"🏁 Crawl finished: {self.pages_crawled} pages crawled")
    
    async def _crawl_page(self, url: str, depth: int):
        """Crawl a single page"""
        logger.info(f"🌐 Crawling [{depth}]: {url}")
        
        # Navigate to page
        page = await self.page_loader.get_current_page()
        if page.url != url:
            await self.page_loader.load_page(url)
        
        # NEW: Dismiss any blocking modals/popups before analysis (aggressive mode for e-commerce)
        await self.modal_handler.dismiss_all_popups(page)
        
        # NEW: Check if page is a multi-step form/wizard
        is_wizard = await self.wizard_detector.detect_wizard(page)
        
        if is_wizard and self.config['crawler'].get('detect_wizards', True):
            logger.info(f"🧙 Multi-step wizard detected on {url}")
            
            # Navigate through wizard steps
            wizard_steps = await self.wizard_detector.navigate_wizard_steps(
                page, 
                max_steps=self.config['crawler'].get('max_wizard_steps', 5),
                ai_detector=self.gemini_detector
            )
            
            # Process each wizard step as a separate state
            step_hashes = {}  # Track hashes for edge creation
            
            for step_data in wizard_steps:
                step_num = step_data['step']
                
                # For wizard steps, use the URL directly with step suffix (NO hashing)
                # Each step gets its own unique identifier based on step number only
                step_hash = f"{url}#wizard-step-{step_num}"
                
                # Check if this step was already processed
                step_is_new = step_hash not in self.state_manager.states
                
                # Store hash for edge creation
                step_hashes[step_num] = step_hash
                
                step_url = step_hash  # URL and hash are the same for wizards
                
                if step_is_new:
                    # Add state manually (bypass hash-based deduplication)
                    # Create proper PageState object for compatibility with export
                    from crawler.state_manager import PageState
                    
                    step_title = f"{step_data['title']} (Step {step_num})"
                    state_obj = PageState(
                        hash=step_hash,
                        url=step_url,
                        normalized_url=url,
                        title=step_title,
                        timestamp=datetime.now().isoformat(),
                        input_count=len(step_data['inputs']),
                        button_count=len(step_data['buttons']),
                        link_count=0,
                        form_count=len(step_data['forms']),
                        inputs=step_data['inputs'],
                        buttons=step_data['buttons'],
                        links=[],
                        forms=step_data['forms']
                    )
                    
                    self.state_manager.states[step_hash] = state_obj
                    
                    # Add node for this step
                    self.graph_builder.add_node(
                        state_hash=step_hash,
                        url=step_url,
                        normalized_url=url,  # All steps share same base URL
                        title=step_title,
                        inputs=step_data['inputs'],
                        buttons=step_data['buttons'],
                        links=[],
                        forms=step_data['forms']
                    )
                    logger.info(f"✅ Wizard step {step_num}: {step_hash} | {len(step_data['inputs'])} inputs")
                    
                    # Increment pages crawled for each unique step
                    self.pages_crawled += 1
                    
                    # Create edge from previous step
                    if step_num > 1:
                        prev_hash = step_hashes.get(step_num - 1)
                        if prev_hash:
                            self.graph_builder.add_edge(
                                from_hash=prev_hash,  # Use actual hash, not URL
                                to_hash=step_hash,
                                action='click',
                                element='wizard_next',
                                label=f"Next Step",
                                allow_pending=False
                            )
                else:
                    logger.info(f"⏩ Wizard step {step_num}: {step_hash} (duplicate)")
            
            logger.info(f"🧙 Wizard complete: processed {len(wizard_steps)} steps")
            
            # Apply rate limiting
            await self.rate_limiter.wait()
            return  # Don't continue with normal processing for wizard pages
        
        # Continue with normal page processing...
        # Discover hidden elements first
        if self.config['interaction']['enabled']:
            await self.interaction_sim.discover_hidden_elements(page)
        
        # Analyze page
        analysis = await self.dom_analyzer.analyze_page(page)
        
        # AI enrichment (if enabled and not many elements found)
        if self.ai_enricher.enabled and len(analysis['inputs']) < 10:
            html_content = await page.content()
            ai_result = await self.ai_enricher.enrich_page(html_content, url)
            
            # Merge AI results (simplified - would need proper merging logic)
            if ai_result.get('forms'):
                logger.debug(f"🤖 AI found {len(ai_result['forms'])} additional forms")
        
        # Extract links
        links = await self.link_extractor.extract_all_links(page, self.start_url)
        analysis['links'] = links
        
        # NEW: Detect file upload inputs
        file_inputs = await self.file_upload_detector.detect_file_inputs(page)
        if file_inputs:
            analysis['file_inputs'] = file_inputs
            logger.info(f"📎 Found {len(file_inputs)} file upload fields")
        
        # Add state to state manager (must create parent state FIRST before component states)
        title = await page.title()
        state_hash, is_new = self.state_manager.add_state(
            url=url,
            title=title,
            inputs=analysis['inputs'],
            buttons=analysis['buttons'],
            links=links,
            forms=analysis['forms']
        )
        
        # Add node to graph (only if new state)
        if is_new:
            normalized_url = self.url_normalizer.normalize(url)
            self.graph_builder.add_node(
                state_hash=state_hash,
                url=url,
                normalized_url=normalized_url,
                title=title,
                inputs=analysis['inputs'],
                buttons=analysis['buttons'],
                links=links,
                forms=analysis['forms']
            )
            logger.info(f"✅ New state: {state_hash} | {normalized_url} | {len(analysis['inputs'])} inputs, {len(analysis['forms'])} forms")
        else:
            logger.info(f"⏭️  Duplicate state: {state_hash} | {url} | Queueing child links anyway")
        
        # Process component states (SPA views discovered during AVB)
        # HYBRID APPROACH: These are already analyzed to support SPAs
        # Must be AFTER parent state_hash is created
        component_states = self.link_extractor.get_component_states()
        if component_states:
            logger.info(f"📦 Processing {len(component_states)} component states")
            
            for comp_state in component_states:
                comp_url = comp_state['url']
                comp_title = comp_state['title']
                comp_analysis = comp_state['analysis']
                
                # OPTIMIZATION: Check if this component state already exists (by URL)
                # If it does, skip to avoid duplicate graph nodes
                if comp_url in self.visited:
                    logger.debug(f"⏭️  Skipping duplicate component: {comp_url}")
                    continue
                
                # Add component state to state manager
                comp_hash, comp_is_new = self.state_manager.add_state(
                    url=comp_url,
                    title=comp_title,
                    inputs=comp_analysis['inputs'],
                    buttons=comp_analysis['buttons'],
                    links=[],  # Component states don't have their own link discovery
                    forms=comp_analysis['forms']
                )
                
                if comp_is_new:
                    normalized_url = self.url_normalizer.normalize(comp_url)
                    self.graph_builder.add_node(
                        state_hash=comp_hash,
                        url=comp_url,
                        normalized_url=normalized_url,
                        title=comp_title,
                        inputs=comp_analysis['inputs'],
                        buttons=comp_analysis['buttons'],
                        links=[],
                        forms=comp_analysis['forms']
                    )
                    logger.info(f"✅ Component state added: {comp_hash} | {normalized_url} | {len(comp_analysis['inputs'])} inputs")
                    
                    # Mark as visited to prevent re-analysis
                    self.visited.add(comp_url)
                    
                    # Add edge from parent page to component
                    self.graph_builder.add_edge(
                        from_hash=state_hash,  # Parent page state
                        to_hash=comp_hash,
                        action='click',
                        element=comp_state['trigger_element'],
                        label=f"Show {comp_state['trigger_element']}",
                        allow_pending=False
                    )
                else:
                    logger.debug(f"⏭️  Component state already exists: {comp_hash}")
            
            # Clear processed component states
            self.link_extractor.clear_component_states()
        
        # NEW: Apply rate limiting before processing next page
        await self.rate_limiter.wait()
        
        # Queue child links (even for duplicate states to ensure complete graph)
        for link in links[:20]:  # Limit to first 20 links per page
            if link not in self.current_depth:
                self.queue.append(link)
                self.current_depth[link] = depth + 1
                
                # Add edge to graph (using link URL as temporary target)
                # This will be fixed by _fix_graph_edges() after crawl completes
                self.graph_builder.add_edge(
                    from_hash=state_hash,
                    to_hash=link,  # Use actual URL, will be mapped to hash in _fix_graph_edges
                    action='click',
                    element=f'a[href="{link}"]',
                    label=f'Link to {link}',
                    allow_pending=True  # Allow edges to not-yet-crawled pages
                )
    
    def _save_checkpoint(self):
        """Save crawl state checkpoint"""
        checkpoint_dir = Path("data/checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint_{self.pages_crawled}.json"
        self.state_manager.save_checkpoint(str(checkpoint_file))
    
    def _generate_results(self) -> Dict:
        """Generate final crawl results"""
        stats = self.state_manager.get_stats()
        graph_stats = self.graph_builder.get_stats()
        ai_stats = self.ai_enricher.get_stats()
        
        # Fix graph edges: replace temporary URL targets with actual state hashes
        self._fix_graph_edges()
        
        # Get graph data with nodes and edges
        graph_dict = self.graph_builder.to_dict()
        
        results = {
            'crawl_stats': {
                'pages_crawled': self.pages_crawled,
                'start_url': self.start_url,
                'max_depth_reached': max(self.current_depth.values()) if self.current_depth else 0,
                **stats
            },
            'graph_stats': graph_stats,
            'ai_stats': ai_stats,
            'states': [s.to_dict() for s in self.state_manager.get_all_states()],
            # Include graph structure for visualization
            'nodes': graph_dict.get('nodes', []),
            'edges': graph_dict.get('edges', [])
        }
        
        return results
    
    def _fix_graph_edges(self):
        """
        Fix graph edges to use actual state hashes instead of URLs
        
        After crawling, edges use actual URLs as targets (e.g., 'https://demoqa.com/widgets').
        We need to replace these with the actual state hashes that were created during crawling.
        """
        from urllib.parse import urlparse
        
        # Build URL to state_hash mapping with all variations
        url_to_hash = {}
        for state in self.state_manager.get_all_states():
            # Map full URL
            url_to_hash[state.url] = state.hash
            url_to_hash[state.url.rstrip('/')] = state.hash
            
            # Map normalized URL
            normalized = self.url_normalizer.normalize(state.url)
            url_to_hash[normalized] = state.hash
            
            # Map path variations
            parsed = urlparse(state.url)
            if parsed.path:
                url_to_hash[parsed.path] = state.hash
                url_to_hash[parsed.path.rstrip('/')] = state.hash
            
            # Map full variations with scheme
            for scheme in ['http:', 'https:']:
                full = f"{scheme}//{parsed.netloc}{parsed.path}"
                url_to_hash[full] = state.hash
                url_to_hash[full.rstrip('/')] = state.hash
        
        logger.debug(f"URL→hash mapping: {len(url_to_hash)} entries for {len(list(self.state_manager.get_all_states()))} states")
        
        # Get all edges and rebuild with correct target hashes
        edges_to_fix = list(self.graph_builder.graph.edges(data=True))
        fixed_count = 0
        removed_count = 0
        
        for source, target, data in edges_to_fix:
            # Check if target looks like a URL (not a hash)
            if target in url_to_hash:
                actual_target = url_to_hash[target]
                
                # Remove old edge with URL target
                self.graph_builder.graph.remove_edge(source, target)
                
                # Add corrected edge with hash target
                if actual_target in self.graph_builder.graph:
                    self.graph_builder.graph.add_edge(source, actual_target, **data)
                    fixed_count += 1
                    logger.debug(f"Fixed edge: {source[:8]} → {target[:50]} => {actual_target[:8]}")
                else:
                    logger.warning(f"Target node {actual_target} not in graph")
                    removed_count += 1
            elif target not in self.graph_builder.graph:
                # Target is neither a valid URL nor a valid hash - remove orphan edge
                logger.warning(f"Removing orphan edge: {source[:8]} → {target[:50]}")
                self.graph_builder.graph.remove_edge(source, target)
                removed_count += 1
        
        logger.info(f"✅ Fixed {fixed_count} graph edges, removed {removed_count} orphans")
        logger.info(f"📊 Final graph: {self.graph_builder.graph.number_of_nodes()} nodes, {self.graph_builder.graph.number_of_edges()} edges")
        
        # CLEANUP: Remove orphan nodes that were created as placeholders (nodes with URL as ID but no data)
        nodes_to_remove = []
        for node_id in list(self.graph_builder.graph.nodes()):
            node_data = self.graph_builder.graph.nodes[node_id]
            # If node has no 'url' attribute, it's a placeholder created by allow_pending=True
            if not node_data.get('url'):
                nodes_to_remove.append(node_id)
        
        if nodes_to_remove:
            for node_id in nodes_to_remove:
                self.graph_builder.graph.remove_node(node_id)
            logger.info(f"🧹 Removed {len(nodes_to_remove)} orphan placeholder nodes")
            logger.info(f"📊 Clean graph: {self.graph_builder.graph.number_of_nodes()} nodes, {self.graph_builder.graph.number_of_edges()} edges")
    
    def export_results(
        self,
        output_dir: str = "data/crawled_graphs",
        formats: List[str] = None
    ):
        """
        Export crawl results using a URL-based filename so files are
        human-readable (e.g. ``localhost_8080_20250305_143022``).

        Args:
            output_dir: Output directory
            formats: List of formats ('json', 'graphml', 'csv')
        """
        import re
        formats = formats or self.config['export']['formats']
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Build a human-readable slug from the start URL + wall-clock timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.start_url:
            from urllib.parse import urlparse
            parsed = urlparse(self.start_url)
            host = parsed.netloc.replace(":", "_").replace(".", "_")
            path_slug = re.sub(r"[^a-zA-Z0-9_\-]", "_", parsed.path.strip("/"))
            slug = f"{host}_{path_slug}_{timestamp}" if path_slug else f"{host}_{timestamp}"
        else:
            slug = f"crawl_{timestamp}"

        # JSON export
        if 'json' in formats:
            json_file = output_path / f"{slug}.json"
            self.graph_builder.to_json(str(json_file))

        # GraphML export
        if 'graphml' in formats:
            graphml_file = output_path / f"{slug}.graphml"
            self.graph_builder.to_graphml(str(graphml_file))

        # CSV export (simplified)
        if 'csv' in formats:
            import pandas as pd
            states = self.state_manager.get_all_states()

            df = pd.DataFrame([
                {
                    'url': s.url,
                    'normalized_url': s.normalized_url,
                    'title': s.title,
                    'input_count': s.input_count,
                    'form_count': s.form_count,
                    'link_count': s.link_count
                }
                for s in states
            ])

            csv_file = output_path / f"{slug}.csv"
            df.to_csv(csv_file, index=False)
            logger.info(f"💾 Exported CSV: {csv_file}")

        logger.info(f"✅ Results exported to {output_dir} as {slug}")
    
    async def _attempt_auto_login(self):
        """
        Attempt auto-login if credentials provided in .env
        Detects login forms and fills them automatically
        """
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        username = os.getenv('AUTH_USERNAME')
        password = os.getenv('AUTH_PASSWORD')
        
        # Skip if no credentials provided
        if not username or not password:
            logger.debug("ℹ️  No AUTH credentials in .env - skipping auto-login")
            return
        
        try:
            page = await self.page_loader.get_current_page()
            
            # Check if current page has a login form
            # Look for username/email and password inputs
            username_input = await page.query_selector('input[name*="user" i], input[id*="user" i], input[type="text"], input[type="email"]')
            password_input = await page.query_selector('input[type="password"]')
            
            if username_input and password_input:
                logger.info("🔐 Login form detected - attempting auto-login...")
                
                # Fill username
                await username_input.fill(username)
                logger.debug(f"   ✅ Filled username: {username}")
                
                # Fill password
                await password_input.fill(password)
                logger.debug(f"   ✅ Filled password: {'*' * len(password)}")
                
                # Find and click submit button
                submit_button = await page.query_selector(
                    'button[type="submit"], input[type="submit"], button:has-text("Log"), button:has-text("Sign")'
                )
                
                if submit_button:
                    await submit_button.click()
                    logger.info("   🖱️  Clicked login button")
                    
                    # Wait for navigation or error message
                    try:
                        await page.wait_for_load_state('networkidle', timeout=5000)
                        logger.info("   ✅ Login successful - page navigated")
                    except:
                        # Check if still on login page (login failed)
                        if await page.query_selector('input[type="password"]'):
                            logger.warning("   ⚠️  Still on login page - credentials may be incorrect")
                        else:
                            logger.info("   ✅ Login completed")
                else:
                    logger.warning("   ⚠️  Login form found but no submit button detected")
            else:
                logger.debug("ℹ️  No login form detected on start page")
        
        except Exception as e:
            logger.warning(f"⚠️  Auto-login failed: {e}")
            # Don't raise - continue crawling even if login fails

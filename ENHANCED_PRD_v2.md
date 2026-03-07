# 🧾 PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Module:** Black-Box Web Crawler and Graph Visualization System  
**Project:** AutoTestAI – AI-Powered Black-Box Testing Framework  
**Version:** 2.1 (Hybrid Semantic-AI Crawler)  
**Date:** October 2024  
**Author:** Kamran  
**Scope:** Input Fields + SPA Navigation Discovery + AI Enrichment

---

## 📋 Executive Summary

The **Black-Box Crawler Module** autonomously explores authenticated web applications to discover, map, and visualize all interactive elements and navigation flows. Unlike traditional crawlers, this system:

- **Starts post-authentication** (user logs in manually first)
- **Detects input fields universally** (works with any framework: React, Vue, Angular, plain HTML)
- **Handles SPAs intelligently** (detects DOM-based navigation without URL changes)
- **Normalizes dynamic URLs** (merges `/product/123` and `/product/456` as `/product/:id`)
- **AI-powered semantic enrichment** (Gemini API detects non-semantic interactive elements)
- **Builds interactive state graphs** (NetworkX + Streamlit visualization)
- **Exports structured data** for test generation

---

## 1. Problem Statement

### 1.1 Challenges in Black-Box Testing

| Challenge | Description | Our Solution |
|-----------|-------------|--------------|
| **Framework Diversity** | Web apps use React, Vue, Angular, or plain HTML/JS | Universal detection strategies (6+ methods) |
| **Dynamic Content** | SPAs change content without URL navigation | DOM hashing + MutationObserver |
| **Form Detection** | Forms without `<form>` tags, nested inputs | Semantic clustering + AI-powered detection |
| **Authentication Barriers** | Login required before exploration | Post-auth crawling (manual login first) |
| **Hidden Elements** | Modals, accordions, collapsed sections | Interactive element testing |
| **Duplicate State Detection** | Same content, different URL (or vice versa) | URL + DOM hybrid hashing |
| **Dynamic URL Explosion** | `/product/123`, `/product/456` treated as separate pages | URL normalization (`:id`, `:slug` placeholders) |
| **Non-Semantic HTML** | Clickable `<div>` or `<span>` elements without proper roles | AI enrichment via Gemini API |

### 1.2 Scope Definition

**In Scope:**
- ✅ Post-authentication crawling (user logs in manually before crawl starts)
- ✅ Universal input field detection (all frameworks)
- ✅ SPA navigation flow discovery
- ✅ **URL normalization** (merge dynamic routes like `/product/:id`)
- ✅ **AI-powered semantic enrichment** (Gemini API for non-semantic elements)
- ✅ Interactive graph visualization
- ✅ Form structure analysis
- ✅ Link extraction (visible + deep links from sitemaps)
- ✅ State graph generation (nodes = pages, edges = transitions)

**Out of Scope:**
- ❌ Authentication handling (login/logout automation)
- ❌ Multi-role crawling (admin, user, guest comparison)
- ❌ API interception and network monitoring
- ❌ Security vulnerability scanning
- ❌ Performance metrics collection
- ❌ Test case generation (future phase)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard UI                    │
│  (Start URL, Max Depth, Headless Toggle, Export Controls)   │
│  [✓] Use Gemini Enrichment  [✓] Enable URL Normalization    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Crawler Orchestrator                      │
│  • Manages crawl queue (BFS/DFS)                             │
│  • Coordinates all components                                │
│  • Handles state restoration on failure                      │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Page Loader │ │ DOM Analyzer │ │ Interaction  │
│  (Playwright)│ │ (Universal)  │ │  Simulator   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                ▼                │
       │         ┌──────────────┐        │
       │         │ AI Enricher  │        │
       │         │ (Gemini API) │        │
       │         └──────┬───────┘        │
       │                │                │
       └────────────────┼────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     State Manager                            │
│  • DOM Hasher (URL + Content)                                │
│  • URL Normalizer (/product/:id)                             │
│  • Duplicate Detection                                       │
│  • State Metadata Storage                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Graph Builder (NetworkX)                  │
│  • Nodes: Unique UI states                                   │
│  • Edges: User interactions (clicks, form submits)           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Visualization & Export Layer                   │
│  • PyVis/Plotly Interactive Graph                            │
│  • JSON Export (graph + metadata)                            │
│  • CSV Reports (discovered elements)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Functional Requirements

### 3.1 Core Components

#### 3.1.1 Page Loader (Playwright-based)

**Purpose:** Launch and navigate web pages with full JavaScript support.

**Key Features:**
- Browser automation (Chromium/Firefox/WebKit)
- Headless/headed mode toggle
- Wait for dynamic content (network idle, DOM stable)
- Handle page transitions (URL changes + SPA navigation)
- Maintain session cookies across navigations

**Technical Details:**
```python
# Pseudo-code
async def load_page(url, wait_for='networkidle'):
    page = await browser.new_page()
    await page.goto(url, wait_until=wait_for)
    await page.wait_for_timeout(2000)  # Let SPAs stabilize
    return page
```

---

#### 3.1.2 Universal DOM Analyzer

**Purpose:** Extract ALL input fields, forms, and interactive elements regardless of framework.

**Detection Strategies (6 Methods):**

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **1. Semantic Detection** | Find `<form>` tags with inputs | Traditional HTML forms |
| **2. Container-Based** | Detect `<div>` wrapping multiple inputs | React/Vue component forms |
| **3. Input Clustering** | Group nearby inputs by proximity | Inline forms, login boxes |
| **4. Event-Driven** | Find inputs with `onChange`/`onSubmit` handlers | Dynamic forms |
| **5. Checkbox Trees** | Detect hierarchical checkbox groups | Complex filters, category selectors |
| **6. AI-Powered** | Heuristic analysis when other methods fail | Custom components |

**Input Field Metadata Extracted:**
```json
{
  "type": "text | email | password | checkbox | radio | select | textarea | file | number | date",
  "name": "username",
  "id": "login-username",
  "label": "Username",
  "placeholder": "Enter your email",
  "required": true,
  "pattern": "[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$",
  "minLength": 3,
  "maxLength": 50,
  "visible": true,
  "parent_form": "form#login-form"
}
```

**Form Deduplication:**
- Uses **input signature** (type + name + count + order)
- Prevents duplicate detection (e.g., 7 identical forms on same page)

---

#### 3.1.3 Intelligent Normalization & AI Enrichment (Gemini-Driven)

**Purpose:** Enhance crawler coverage on sites with **non-semantic HTML**, **dynamic URLs**, and **hidden logical groupings** (e.g., forms built from `<div>` + JS, or `/product/123` → `/product/:id` routes).

**Features:**

| Function | Description |
|----------|-------------|
| **URL Normalization** | Detect and unify dynamic routes such as `/product/123`, `/blog/article-slug`, etc. |
| **Non-Semantic Element Detection** | Identify clickable or input-like elements rendered as `<div>`, `<span>`, or `<svg>` |
| **Gemini API Enrichment** | Send page DOM to Gemini API with structured prompt to extract logical sections, interactive areas, and inferred semantics |
| **Hybrid Merging** | Merge rule-based detections with Gemini's JSON output for a richer, cleaner crawl result |

**URL Normalization Algorithm:**

```python
def normalize_url(url):
    """
    Normalize dynamic URLs to prevent duplicate state detection.
    Examples:
      /product/123 → /product/:id
      /blog/my-article-title → /blog/:slug
      /user/john-doe → /user/:username
    """
    # Remove query parameters
    url = url.split('?')[0].rstrip('/')
    
    # Replace numeric IDs
    url = re.sub(r'/\d+', '/:id', url)
    
    # Replace long alphanumeric slugs (6+ chars)
    url = re.sub(r'/[a-zA-Z0-9-]{6,}', '/:slug', url)
    
    return url
```

**Gemini API Integration:**

**Prompt Template:**
```
You are a QA analyst analyzing a webpage's structure.
Identify all elements that behave like forms, buttons, or navigation areas.
Return JSON:
{
  "page_type": "login|dashboard|product|generic",
  "forms": [
    {
      "inputs": [{"type": "text", "label": "Username", "identifier": "div.login-field"}],
      "submit_button": "button.submit-btn"
    }
  ],
  "buttons": [{"text": "Add to Cart", "selector": "div.buy-btn"}],
  "links": [{"text": "Product Details", "url": "/product/123"}]
}
```

**API Call Logic:**
```python
async def enrich_with_gemini(page_html, url):
    """
    Send DOM snippet to Gemini API for semantic analysis.
    Returns: JSON with detected interactive elements
    """
    prompt = f"""
    Analyze this HTML and identify interactive elements:
    URL: {url}
    HTML: {page_html[:5000]}  # First 5KB only
    
    Return JSON with forms, buttons, and links.
    """
    
    response = await gemini_api.generate_content(prompt)
    return json.loads(response.text)
```

**Privacy & Security:**
- **Data Minimization**: Only DOM structure sent (no user input values)
- **Rate Limiting**: Max 1 API call per normalized URL
- **Optional Toggle**: Users can disable AI enrichment in Streamlit UI
- **Local Fallback**: If API fails, use rule-based detection only

**Hybrid Detection Flow:**
```
1. Run 6 universal detection strategies
2. IF page has <10 elements detected:
   → Send to Gemini API
   → Merge AI results with rule-based results
3. Deduplicate combined results
4. Store in graph with "detection_method" metadata
```

---

#### 3.1.4 Link Extraction (Deep + Visible)

**Purpose:** Discover all navigable URLs (visible links + hidden routes).

**Methods:**

| Method | Description | Implementation |
|--------|-------------|----------------|
| **Visible Links** | Extract all `<a href>` elements | `document.querySelectorAll('a[href]')` |
| **SPA Routes** | Detect React Router, Vue Router paths | Search for route definitions in JS |
| **Sitemap Parsing** | Fetch `/sitemap.xml` and extract URLs | Fetch + XML parse |
| **Hidden Menus** | Expand dropdowns, accordions | Click expand buttons |

**Link Filtering:**
- ✅ Same-origin only
- ✅ Remove anchors (`#section`)
- ✅ Remove duplicates
- ❌ Skip external domains
- ❌ Skip logout/delete actions

---

#### 3.1.5 State Manager (DOM Hasher)

**Purpose:** Uniquely identify each UI state to avoid infinite loops.

**Hash Generation Algorithm:**
```javascript
// Hybrid hashing: URL + Interactive Elements
hash = FNV1a(
  normalize_url(window.location.pathname) + 
  window.location.search + 
  "::" + 
  serialize(interactive_elements)
)

// Interactive elements = forms, inputs, buttons, links
// Serialization: tag:type:name (e.g., "input:text:username")
```

**URL Normalization in Hashing:**
Incorporates **normalized URLs** (parameter placeholders like `:id`, `:slug`) to ensure equivalent pages are treated as the same logical state — preventing node explosion in product or blog listings.

**Example:**
```python
# Without normalization:
/product/123 → hash_abc123
/product/456 → hash_def456
/product/789 → hash_ghi789
# Result: 3 separate nodes

# With normalization:
/product/123 → /product/:id → hash_unified
/product/456 → /product/:id → hash_unified
/product/789 → /product/:id → hash_unified
# Result: 1 node (40% reduction in graph complexity)
```

**Why Hybrid Hashing?**
- **URL-only hashing** fails for SPAs (same URL, different content)
- **Content-only hashing** fails when pages have identical forms (e.g., `/login` and `/register` both have email+password)
- **Hybrid approach** ensures unique hashes per page + content combination

**Lessons Learned from v1.0:**
- ❌ **Problem:** Pages with identical navigation bars generated same hash
- ✅ **Solution:** Include normalized URL path in hash to guarantee uniqueness

---

#### 3.1.6 Interaction Simulator

**Purpose:** Simulate user interactions to discover hidden content and navigation flows.

**Supported Interactions:**

| Action | Trigger | Detection Method |
|--------|---------|------------------|
| **Click Links** | Navigate to new pages | `element.click()` |
| **Submit Forms** | Fill inputs + click submit | Synthetic data + submit |
| **Expand Accordions** | Reveal hidden content | Click `[aria-expanded]` |
| **Open Modals** | Trigger overlays | Click buttons with modal triggers |
| **Hover Menus** | Reveal dropdowns | `element.hover()` |

**Synthetic Data Generation:**
```python
SYNTHETIC_DATA = {
    'text': 'TestUser123',
    'email': 'test@example.com',
    'password': 'Test@1234',
    'number': '12345',
    'tel': '+1234567890',
    'url': 'https://example.com',
    'date': '2024-01-01'
}
```

**Safety Mechanisms:**
- **Dry-run mode** (no actual form submissions)
- **Blacklist dangerous actions** (delete, logout, purchase)
- **Timeout limits** (30 seconds per interaction)

---

#### 3.1.7 SPA Navigation Detector

**Purpose:** Detect page transitions in Single Page Applications without URL changes.

**Detection Strategies:**

| Method | Description | Implementation |
|--------|-------------|----------------|
| **URL Change** | Monitor `window.location` | `page.url()` comparison |
| **DOM Mutation** | Detect major DOM changes | `MutationObserver` |
| **History API** | Intercept `pushState`/`replaceState` | Override `history` methods |
| **Content Hash** | Compare before/after DOM hash | Hash difference > threshold |

**Adaptive Waiting:**
- React apps: Wait 6 seconds after navigation
- Vue apps: Wait 5 seconds
- Angular apps: Wait 7 seconds
- Plain HTML: Wait 2 seconds

---

### 3.2 Graph Builder (NetworkX)

**Purpose:** Build a directed graph representing the UI state machine.

**Graph Structure:**

```python
# Nodes (UI States)
{
  "id": "hash_abc123",
  "url": "/dashboard",
  "title": "Dashboard - AutoTestAI",
  "inputs": [
    {"type": "text", "name": "search", "label": "Search"}
  ],
  "buttons": ["Submit", "Cancel"],
  "links": ["/profile", "/settings", "/logout"],
  "timestamp": "2024-10-24T10:30:00Z"
}

# Edges (Transitions)
{
  "from": "hash_abc123",
  "to": "hash_def456",
  "action": "click",
  "element": "a[href='/profile']",
  "label": "Profile Link"
}
```

**Graph Metrics:**
- **Node count**: Total unique pages discovered
- **Edge count**: Total interactions performed
- **Depth**: Maximum navigation depth from start URL
- **Isolated nodes**: Pages with no incoming/outgoing edges
- **Cyclic paths**: Detect navigation loops

---

### 3.3 Visualization Dashboard (Streamlit)

**Purpose:** Interactive UI for controlling crawls and viewing results.

**Dashboard Sections:**

#### 1. **Control Panel**
```
┌─────────────────────────────────────────┐
│  🎯 Crawl Configuration                 │
├─────────────────────────────────────────┤
│  Start URL: [https://app.example.com]   │
│  Max Depth: [5] ────────── (1-10)       │
│  Headless:  [✓] On  [ ] Off             │
│  Timeout:   [30] seconds per page       │
│                                          │
│  [✓] Use Gemini Enrichment              │
│  [✓] Enable URL Normalization           │
│                                          │
│  [▶ Start Crawl]  [⏸ Pause]  [⏹ Stop]   │
└─────────────────────────────────────────┘
```

#### 2. **Live Progress**
```
┌─────────────────────────────────────────┐
│  📊 Crawl Status                         │
├─────────────────────────────────────────┤
│  Current URL: /dashboard                │
│  Pages Crawled: 15 / 50                 │
│  Forms Found: 8                          │
│  Queue Size: 12                          │
│  Progress: ████████░░░░ 65%             │
└─────────────────────────────────────────┘
```

#### 3. **Graph Visualization (PyVis)**
- **Interactive node dragging**
- **Zoom in/out**
- **Click node → Show details**
- **Filter by depth/form count**
- **Export as PNG/SVG**

#### 4. **Element Explorer Table**
```
┌──────────┬────────────────────┬──────────┬─────────┐
│ Page URL │ Input Type         │ Name     │ Label   │
├──────────┼────────────────────┼──────────┼─────────┤
│ /login   │ email              │ email    │ Email   │
│ /login   │ password           │ pass     │ Password│
│ /profile │ text               │ username │ Username│
│ /profile │ file               │ avatar   │ Avatar  │
└──────────┴────────────────────┴──────────┴─────────┘
```

#### 5. **Export Options**
- **JSON** (full graph data)
- **CSV** (element list)
- **PNG** (graph image)
- **GraphML** (import into Gephi/Cytoscape)

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Page Load Time** | < 5 seconds | Playwright `networkidle` |
| **State Hash Generation** | < 50ms | Performance timer |
| **Crawl Speed** | 20-30 pages in 2-3 minutes | End-to-end timing |
| **Memory Usage** | < 1GB for 100 pages | Process monitor |
| **Graph Rendering** | < 2 seconds for 50 nodes | Streamlit profiler |

### 4.2 Reliability

| Requirement | Implementation |
|-------------|----------------|
| **Crash Recovery** | Save state every 5 pages; resume from checkpoint |
| **Timeout Handling** | 30-second timeout per page; skip and log failures |
| **Error Logging** | Structured JSON logs with timestamps |
| **Duplicate Prevention** | Track visited URLs + hashes in set |

### 4.3 Compatibility

| Category | Support |
|----------|---------|
| **Frameworks** | React, Vue, Angular, Svelte, Plain HTML |
| **Browsers** | Chromium, Firefox, WebKit (via Playwright) |
| **Operating Systems** | Windows, macOS, Linux |
| **Python Version** | 3.9+ |

### 4.4 Usability

| Feature | Description |
|---------|-------------|
| **Zero Configuration** | Works out-of-the-box for most web apps |
| **Progress Indicators** | Real-time console logs + Streamlit progress bar |
| **Error Messages** | Clear, actionable error messages (not stack traces) |
| **Documentation** | README with examples + architecture diagram |

### 4.5 Security & Ethics

| Principle | Implementation |
|-----------|----------------|
| **No Data Exfiltration** | All data stays local (no external API calls except Gemini) |
| **Data Privacy** | Gemini API receives **DOM snippets only**, excluding personal or sensitive data fields |
| **Local First** | AI calls are optional (toggle in Streamlit UI) |
| **Rate Limiting** | Max 1 Gemini API call per unique normalized page |
| **Respect Robots.txt** | Optional flag to honor crawl delays |
| **User Consent** | User manually logs in (no credential storage) |

---

## 5. Technical Specifications

### 5.1 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Crawler** | Playwright (Python) | Full browser automation, multi-browser support |
| **Graph Library** | NetworkX | Standard Python graph library, easy NetworkX integration |
| **Visualization** | PyVis (NetworkX + vis.js) | Interactive graphs with drag-and-drop |
| **UI Framework** | Streamlit | Rapid prototyping, built-in widgets |
| **AI Enrichment** | Gemini API | Semantic understanding of non-standard UI patterns |
| **Data Storage** | JSON files + SQLite (optional) | Simple, portable, no DB setup required |
| **Logging** | Python `logging` module | Structured logs with levels (DEBUG, INFO, ERROR) |

### 5.2 Project Structure

```
autotestai-crawler/
│
├── crawler/
│   ├── __init__.py
│   ├── orchestrator.py         # Main crawl loop (BFS/DFS)
│   ├── page_loader.py          # Playwright wrapper
│   ├── dom_analyzer.py         # Universal form detection (6 strategies)
│   ├── ai_enricher.py          # Gemini API integration
│   ├── url_normalizer.py       # Dynamic route normalization
│   ├── link_extractor.py       # Deep link discovery
│   ├── state_manager.py        # DOM hasher + visited tracker
│   ├── interaction_sim.py      # Click, submit, hover simulator
│   └── graph_builder.py        # NetworkX graph construction
│
├── app/
│   ├── streamlit_app.py        # Main Streamlit dashboard
│   ├── components/
│   │   ├── control_panel.py    # Crawl config UI
│   │   ├── graph_viz.py        # PyVis graph renderer
│   │   └── element_table.py    # Data table component
│   └── utils/
│       ├── exporter.py         # JSON/CSV/PNG export
│       └── logger_config.py    # Logging setup
│
├── data/
│   ├── crawled_graphs/         # Saved graph JSON files
│   ├── screenshots/            # Page screenshots
│   └── logs/                   # Crawl logs
│
├── tests/
│   ├── test_dom_analyzer.py
│   ├── test_state_manager.py
│   └── test_graph_builder.py
│
├── config/
│   └── crawler_config.yaml     # Default settings
│
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

### 5.3 Key Algorithms

#### 5.3.1 Breadth-First Crawl (BFS)

```python
def breadth_first_crawl(start_url, max_depth):
    queue = deque([(start_url, 0)])  # (url, depth)
    visited = set()
    graph = nx.DiGraph()
    
    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()
        
        if depth > max_depth or url in visited:
            continue
        
        # Load page
        page = await load_page(url)
        state_hash = generate_hash(page)
        
        if state_hash in visited:
            continue  # Duplicate content
        
        visited.add(state_hash)
        
        # Extract data
        forms = extract_forms(page)
        links = extract_links(page)
        
        # Add to graph
        graph.add_node(state_hash, url=url, forms=forms)
        
        # Queue child links
        for link in links:
            queue.append((link, depth + 1))
            graph.add_edge(state_hash, hash(link), action='click')
    
    return graph
```

#### 5.3.2 DOM Hash Generation (Hybrid with Normalization)

```python
def generate_hash(page):
    # Extract URL components
    url_path = normalize_url(page.url)  # Apply normalization
    
    # Extract interactive elements
    elements = page.query_selector_all('form, input, button, a')
    element_signature = '|'.join([
        f"{el.tag_name}:{el.get_attribute('type')}:{el.get_attribute('name')}"
        for el in elements
    ])
    
    # Combine and hash
    combined = f"{url_path}::{element_signature}"
    return hashlib.sha256(combined.encode()).hexdigest()[:8]

def normalize_url(url):
    """
    Normalize dynamic URLs to prevent duplicate state detection.
    """
    # Remove query parameters and trailing slashes
    url = url.split('?')[0].rstrip('/')
    
    # Replace numeric IDs: /product/123 → /product/:id
    url = re.sub(r'/\d+', '/:id', url)
    
    # Replace long alphanumeric slugs: /blog/my-article → /blog/:slug
    url = re.sub(r'/[a-zA-Z0-9-]{6,}', '/:slug', url)
    
    return url
```

#### 5.3.3 Form Deduplication

```python
def deduplicate_forms(forms):
    seen_signatures = set()
    unique_forms = []
    
    for form in forms:
        # Create signature from inputs
        signature = '|'.join(sorted([
            f"{inp['type']}:{inp['name']}"
            for inp in form['inputs']
        ]))
        
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_forms.append(form)
    
    return unique_forms
```

---

## 6. Success Criteria & Metrics

### 6.1 Functional Success

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Form Detection Accuracy** | ≥ 90% | Manual verification on 10 test sites |
| **SPA Navigation Detection** | ≥ 85% | Test on React/Vue/Angular apps |
| **Link Discovery Rate** | ≥ 95% | Compare against manual sitemap |
| **Duplicate State Rate** | ≤ 10% | `duplicate_count / total_pages` |
| **Crash Recovery Success** | 100% | Force-kill and resume 10 times |
| **URL Normalization Accuracy** | ≥ 90% | `/product/123` → `/product/:id` match count |
| **AI Element Detection Accuracy** | ≥ 85% | Gemini vs. manual audit on 10 sites |
| **Duplicate Reduction via Normalization** | ≥ 40% fewer nodes | Compare with non-normalized crawl |

### 6.2 Performance Benchmarks

| Test Case | Pages | Expected Time | Actual |
|-----------|-------|---------------|--------|
| Simple Blog (HTML) | 10 | < 30 seconds | TBD |
| E-commerce (React) | 30 | < 90 seconds | TBD |
| Dashboard (Vue) | 50 | < 150 seconds | TBD |

### 6.3 Usability Testing

- **Task 1:** Non-technical user starts a crawl → Success if < 2 minutes
- **Task 2:** User exports graph as PNG → Success if < 30 seconds
- **Task 3:** User identifies a specific form in UI → Success if < 1 minute

---

## 7. Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|----------|--------|------------|
| **Anti-bot detection** | Medium | High | User-agent spoofing, human-like delays |
| **Infinite loops** | High | High | Max depth limit, visited set, timeout |
| **Memory overflow** | Medium | Medium | Periodic garbage collection, page limit |
| **Framework incompatibility** | Low | High | Test on diverse apps, fallback strategies |
| **SPA not detected** | Medium | High | Multiple detection methods (URL + DOM + History API) |
| **Forms missed** | Medium | High | 6 detection strategies, manual verification |

---

## 8. Testing Strategy

### 8.1 Unit Tests

| Component | Test Cases |
|-----------|-----------|
| `dom_analyzer.py` | ✅ Detect `<form>` tags<br>✅ Detect inline forms<br>✅ Detect React forms<br>✅ Deduplicate identical forms |
| `state_manager.py` | ✅ Generate unique hashes<br>✅ Detect duplicate content<br>✅ Handle URL changes |
| `link_extractor.py` | ✅ Extract visible links<br>✅ Parse sitemap.xml<br>✅ Filter external links |

### 8.2 Integration Tests

| Scenario | Expected Outcome |
|----------|------------------|
| **Crawl 5-page blog** | All 5 pages discovered, 0 duplicates |
| **Crawl React SPA** | Client-side routes detected without URL changes |
| **Crawl with forms** | All input fields extracted with metadata |
| **Crash and resume** | Crawl continues from last checkpoint |

### 8.3 Test Sites

| Site Type | URL | Purpose |
|-----------|-----|---------|
| **HTML Blog** | [http://example.com/blog](http://example.com/blog) | Basic link crawling |
| **React SPA** | [https://demoqa.com](https://demoqa.com) | SPA navigation, form detection |
| **Vue Dashboard** | TBD | Vue Router detection |
| **Complex Forms** | [https://demoqa.com/automation-practice-form](https://demoqa.com/automation-practice-form) | Multi-input form detection |

---

## 9. Deliverables & Timeline

### Phase 1: Core Crawler (Weeks 1-2)
- ✅ Playwright page loader
- ✅ Universal DOM analyzer (6 strategies)
- ✅ State manager (hybrid hashing)
- ✅ Link extractor
- ✅ BFS crawl loop

### Phase 2: Graph Builder (Week 3)
- ✅ NetworkX graph construction
- ✅ Node/edge metadata storage
- ✅ JSON export

### Phase 3: Streamlit Dashboard (Week 4)
- ✅ Control panel UI
- ✅ PyVis graph visualization
- ✅ Element data table
- ✅ Export functionality

### Phase 4: Testing & Polish (Week 5)
- ✅ Unit tests
- ✅ Integration tests on real sites
- ✅ Performance optimization
- ✅ Documentation

---

## 10. Lessons Learned (from v1.0 Chrome Extension)

### 10.1 What Worked Well ✅

| Feature | Why It Worked |
|---------|---------------|
| **Universal Form Detection** | 6 strategies caught 95%+ of forms across frameworks |
| **Deep Link Extractor** | Sitemap parsing found pages regular link extraction missed |
| **DOM Hashing** | Fast, reliable state identification |
| **Deduplication Logic** | Input signature method eliminated 70% false positives |
| **Breadth-First Search** | Systematic, predictable crawl order |

### 10.2 What Didn't Work ❌

| Issue | Problem | Solution in v2.0 |
|-------|---------|------------------|
| **Content-only hashing** | Pages with identical navigation generated same hash | **Hybrid hashing** (URL + content) |
| **No SPA detection** | Missed React Router transitions | **MutationObserver + History API** interception |
| **Excessive logging** | 25+ logs per page cluttered console | **Reduced to 4-5 critical logs** |
| **No crash recovery** | Lost all progress on browser crash | **Checkpoint every 5 pages** |
| **Hidden elements missed** | Collapsed accordions not explored | **Interactive element testing** |

### 10.3 Key Insights 💡

1. **Framework-agnostic is essential**: Don't assume `<form>` tags exist
2. **URL ≠ Unique Page**: SPAs reuse URLs with different content
3. **Content ≠ Unique Page**: Same navigation bars appear everywhere
4. **Hybrid approach wins**: Combine URL + content for perfect uniqueness
5. **Deduplication saves time**: 30% fewer pages to process
6. **Interactive testing matters**: 15-20% of forms are hidden initially
7. **Adaptive timing is critical**: React needs 6s, plain HTML needs 2s

---

## 11. Future Enhancements (Out of Current Scope)

### 11.1 Phase 2 Features
- **Multi-role crawling**: Admin vs. user vs. guest comparison
- **API interception**: Capture network requests during crawl
- **Test case generation**: Auto-generate Selenium scripts from graph
- **AI-powered exploration**: RL agent decides which links to prioritize
- **LLM-assisted DOM labeling**: Gemini output reused in test case generation
- **Contextual action prediction**: AI suggests next click priorities

### 11.2 Phase 3 Features
- **Distributed crawling**: Multiple browser instances in parallel
- **Visual regression testing**: Screenshot comparison across crawls
- **A/B testing support**: Detect variant pages
- **Accessibility auditing**: WCAG compliance checking

---

## 12. Appendix

### 12.1 Glossary

| Term | Definition |
|------|------------|
| **SPA** | Single Page Application (React, Vue, Angular) |
| **DOM** | Document Object Model (browser's HTML structure) |
| **BFS** | Breadth-First Search (explores level-by-level) |
| **DFS** | Depth-First Search (explores one path fully) |
| **State Hash** | Unique identifier for a UI state (URL + content) |
| **URL Normalization** | Converting `/product/123` to `/product/:id` template |
| **Semantic Detection** | Using HTML structure to identify elements |
| **Non-Semantic HTML** | Interactive elements built with `<div>` + JS without proper ARIA roles |
| **Synthetic Data** | Fake test data (e.g., `test@example.com`) |
| **AI Enrichment** | Using Gemini API to detect interactive elements missed by rule-based methods |

### 12.2 References

- [Playwright Documentation](https://playwright.dev/python/)
- [NetworkX Documentation](https://networkx.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyVis Documentation](https://pyvis.readthedocs.io/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)

---

## 13. Approval & Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| **Product Owner** | Kamran | 2024-10-24 | _________ |
| **Technical Lead** | TBD | | |
| **QA Lead** | TBD | | |

---

**Document Version:** 2.1 (Hybrid Semantic-AI Crawler)  
**Last Updated:** October 24, 2024  
**Next Review:** Before Phase 2 kickoff  

---

*This PRD incorporates lessons learned from the SmartCrawler v1.0 Chrome extension project, focusing on universal detection, framework-agnostic design, robust state management, and AI-powered semantic enrichment via Gemini API.*

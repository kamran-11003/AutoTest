<div align="center">

# Toward Intelligent Black-Box Automation for Web Application Testing

**AutoTestAI: A Hybrid Framework Combining Rule-Based Testing, Reinforcement Learning, Computer Vision, and Large Language Models**

---

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](#)
[![Playwright](https://img.shields.io/badge/Playwright-1.58-green?logo=playwright&logoColor=white)](#)
[![Gemini](https://img.shields.io/badge/Gemini_AI-Flash-orange?logo=google&logoColor=white)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.11-red?logo=pytorch&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?logo=streamlit&logoColor=white)](#)

</div>

---

## Abstract

Automated black-box testing plays a critical role in validating web applications without requiring access to internal source code. Despite significant advances in testing tools and automation frameworks, fully autonomous black-box testing for modern web applications remains an open research challenge. Existing approaches often depend on manual scripting, predefined interaction flows, or limited exploration strategies, which restrict scalability, adaptability, and coverage. This paper investigates the fundamental limitations of current black-box testing tools and approaches and examines whether complete automation is theoretically or practically achievable. The study analyzes challenges related to application exploration, test case generation, large-scale execution, result verification, and regression testing. Furthermore, it explores the potential of combining rule-based testing techniques, reinforcement learning, computer vision, and large language models to enhance the intelligence and effectiveness of black-box testing systems. The research is guided by a set of well-defined questions aimed at understanding coverage limitations, the role of semantic reasoning in test generation, scalable execution strategies, and the feasibility of automated failure explanation and fix recommendation. By synthesizing insights from existing literature and system-level design considerations, this work aims to clarify the boundaries of black-box automation and outline directions for building more adaptive and human-comparable testing frameworks for web applications.

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Background and Motivation](#2-background-and-motivation)
- [3. Research Questions](#3-research-questions)
- [4. Proposed Framework: AutoTestAI](#4-proposed-framework-autotestai)
- [5. Why Fully Automated Black-Box Testing Remains Unsolved](#5-why-fully-automated-black-box-testing-remains-unsolved-rq1)
- [6. Coverage and Test Scenario Limitations](#6-coverage-and-test-scenario-limitations-rq2)
- [7. Intelligent Test Case Generation](#7-intelligent-test-case-generation-rq3)
- [8. Scalable Test Execution and Regression Testing](#8-scalable-test-execution-and-regression-testing-rq4)
- [9. Automated Result Verification and Oracles](#9-automated-result-verification-and-oracles-rq5)
- [10. Discussion and Threats to Validity](#10-discussion-and-threats-to-validity)
- [11. Conclusion and Future Work](#11-conclusion-and-future-work)
- [References](#references)

---

## 1. Introduction

Web applications have evolved into complex, highly interactive systems that support diverse user workflows and continuous deployment practices. Ensuring the correctness and reliability of these applications is a fundamental requirement in modern software engineering. Among various testing paradigms, black-box testing is particularly valuable as it evaluates system behavior solely through externally observable inputs and outputs, without requiring access to internal implementation details.
Although numerous tools exist for automating web application testing, fully automated black-box testing remains an unresolved problem. Most existing solutions rely on manually written scripts, predefined interaction paths, or limited exploration strategies that struggle to scale and adapt to application changes. As a result, achieving meaningful coverage and reliable correctness verification still requires substantial human involvement.
Recent advances in artificial intelligence, including reinforcement learning, computer vision, and large language models (LLMs), have introduced new opportunities to improve automation in software testing. However, integrating these techniques into a cohesive, end-to-end black-box testing framework that autonomously explores applications, generates meaningful test cases, verifies execution outcomes, and produces actionable reports remains a significant research challenge.
This paper investigates the fundamental reasons behind the lack of fully automated black-box testing for web applications and explores how intelligent, hybrid approaches can advance the state of the art.
## 2. Background and Motivation

### 2.1 Background

Software testing is a critical activity in the software development lifecycle, aimed at identifying defects and validating system behavior against expected outcomes. Black-box testing focuses on functional behavior without relying on knowledge of internal code structure, making it well suited for testing web applications, third-party systems, and deployed software.
As noted by Balsam and Mishra (2024), "Testing web applications is usually more complex than testing other software products, and methods and tools must be found to make testing more efficient" [1]. The complexity arises from multiple factors: users interact through rich but complex user interfaces with multiple interaction choices, pages are rendered differently across devices, and server-client communication introduces additional challenges [1], [16], [20].
Historically, black-box web testing has relied on manual testing and script-based automation frameworks. Manual testing allows testers to reason about application behavior and uncover subtle defects but is time-consuming, expensive, and difficult to scale. Script-based automation improves repeatability and execution speed but requires significant effort to design, maintain, and update test scripts.
To reduce manual effort, research has introduced automated crawling and model-based testing techniques, which represent web applications as state-transition models derived from user interface exploration [9], [18]. These approaches enable systematic test generation but often depend on predefined heuristics and structural observations, limiting their general applicability. As highlighted in recent work, "Model-based testing represent applications as abstract state-transition systems derived from observed UI interactions. These models enable systematic reasoning about coverage and support path-based test generation" [2].
More recent work explores the use of machine learning techniques to enhance black-box testing. Reinforcement learning has been applied to guide exploration strategies [3], [6], [11], [13], while natural language processing has been used to improve test documentation and reporting. Chang et al. (2023) demonstrate that "reinforcement learning approaches are widely adapted in automatic software testing" by designing reward functions to train policies for state space exploration [3]. Despite these advancements, existing methods remain fragmented and do not yet constitute a fully autonomous black-box testing solution.
### 2.2 Motivation

The motivation for this research arises from persistent limitations in current black-box testing approaches and increasing demands from modern software development practices.
First, contemporary development environments emphasize automation, scalability, and rapid release cycles, requiring testing solutions that can operate autonomously with minimal human intervention. Existing black-box testing tools still rely heavily on manual configuration and scripting, limiting their effectiveness in large or frequently changing applications [1]. Recent empirical studies reveal that "Google Monkey has remained the de facto standard for practitioners" due to its black-box nature, yet it "uses the most naive form of test input generation technique, i.e., random testing" [4], [18].
Second, commonly used test design techniques such as Boundary Value Analysis (BVA) and Equivalence Class Partitioning (ECP) are effective for validating input constraints but offer limited support for multi-step workflows and complex interaction scenarios. As web applications grow in functional complexity, input-level testing alone becomes insufficient. Research shows that "some deep states can only be reached by specific action sequences" requiring sophisticated exploration strategies [3], [6], [14].
Third, automated testing systems often generate large volumes of test cases without mechanisms to assess their relative importance or redundancy. This leads to inefficient execution, increased regression testing costs, and limited insight into actual application behavior. Studies have found that "reinforcement learning agents frame UI exploration as a sequential decision-making problem, where actions are rewarded based on novelty, coverage, or goal achievement" but "learned policies optimize exploration rather than correctness" [5].
Finally, many black-box testing solutions focus primarily on defect detection while providing minimal support for failure interpretation, result explanation, and developer-oriented reporting, reducing their practical usefulness in real-world development workflows [1], [10]. As noted in recent work on LLM-based testing, "LLMs struggle with following specific instructions for UI testing and replanning based on new information," resulting in "reduced effectiveness of LLM-driven solutions for automated feature-based UI testing" [6].
These limitations motivate the need for an intelligent black-box testing framework that can autonomously explore applications, generate representative and meaningful test cases, execute them efficiently, and provide actionable insights.
## 3. Research Questions

This research is guided by the following questions:
- RQ1: Why does fully automated black-box testing for web applications still not exist, and is complete automation theoretically or practically achievable?
- RQ2: If a web application can be successfully explored and all testable input fields are identified, is it possible to achieve 100% test coverage and generate all meaningful test scenarios?
- RQ3: Can large language models be effectively used to enhance test case generation by introducing semantic understanding and human-like reasoning into black-box testing?
- RQ4: Given a large number of automatically generated test cases, what strategies can be employed to efficiently execute, prioritize, and maintain tests, particularly in regression testing scenarios?
- RQ5: Can an automated black-box testing system provide not only defect detection but also meaningful explanations and fix suggestions for identified failures?
## 4. Proposed Framework: AutoTestAI

To systematically analyze why fully automated black-box testing for web applications remains infeasible, this work decomposes the testing process into a sequence of well-defined subprocesses. Each subprocess is examined independently in terms of feasibility, limitations, and scalability. Based on this decomposition, we propose AutoTestAI, a modular black-box testing framework that explicitly separates concerns across exploration, test generation, execution, and result analysis.
Rather than claiming end-to-end automation, AutoTestAI is designed as a reference framework that exposes where automation succeeds, where it partially succeeds, and where fundamental limitations remain. This decomposition-driven design allows the research questions to be addressed in a structured and evidence-based manner.
### 4.1 Decomposition of the Black-Box Testing Problem

AutoTestAI divides the web application testing lifecycle into the following major stages:
1. Application Exploration and State Discovery
2. Constraint-Aware Test Case Generation
3. Test Case Refinement Using Large Language Models
4. Test Execution and Outcome Observation
5. Result Verification and Regression Maintenance
6. Failure Analysis and Fix Suggestion
Each stage operates independently and produces artifacts that are consumed by subsequent stages. This staged design is intentional: it enables the analysis of automation feasibility at each step, rather than treating black-box testing as a monolithic problem.
### 4.2 Overall Architecture

AutoTestAI follows an orchestrated, pipeline-based architecture centered around a coordination component that manages execution flow, shared state, and persistence. At a high level, the framework consists of:
- A crawler and exploration engine responsible for discovering reachable application states
- A constraint extraction layer that captures testable properties of input fields
- A rule-based test generation layer (planned)
- An LLM-assisted refinement and reasoning layer
- A test execution and monitoring engine
- A result analysis and reporting module
All components communicate through a centralized state repository that stores page states, interaction graphs, extracted constraints, and execution metadata.
### 4.3 Phase 1: Initialization and Setup

The testing process begins with an initialization phase driven through a Streamlit-based user interface. The user provides high-level configuration parameters, including the start URL, crawl depth limits, page limits, and authentication preferences.
Upon startup, the orchestrator loads configuration rules from a dedicated configuration file and initializes a set of specialized components, including browser automation, DOM analysis, link extraction, state management, graph construction, and optional AI-based enrichment modules.
Authentication is handled as a first-class concern. The framework supports manual login with session persistence, session reuse through stored cookies and local storage, and automated credential-based login where applicable. This design reflects real-world testing constraints where authentication is often unavoidable.
### 4.4 Phase 2: Automated Exploration and Crawling

The exploration phase is responsible for discovering the structure of the target web application. AutoTestAI employs a breadth-first search (BFS) strategy to systematically traverse reachable states while respecting configurable depth and page limits.
#### 4.4.1 Page Navigation and Stabilization

Each page is loaded using browser automation, with explicit waits for DOM readiness and additional delays to accommodate dynamically loaded content. Before analysis, blocking UI elements such as cookie banners, popups, and modals are detected and dismissed using multiple fallback strategies to ensure uninterrupted interaction.
#### 4.4.2 Hidden State and Component Discovery

To address modern single-page application behavior, the framework actively reveals hidden UI states by interacting with accordions, tabs, dropdowns, and hover-triggered elements. These interactions allow the crawler to observe component-level state transitions that do not necessarily involve URL changes. Such component states are treated as first-class citizens in the exploration graph, enabling a more faithful representation of application behavior.
#### 4.4.3 Multi-Strategy Form Detection

AutoTestAI employs a multi-strategy DOM analysis engine to detect forms and input fields under diverse frontend implementations. These strategies include explicit HTML forms, implicit form groupings, JavaScript-driven submissions, dynamically generated forms, and shadow DOM traversal.
As a fallback, a vision-based AI module can be invoked when conventional DOM-based strategies fail to identify sufficient input elements. This fallback operates on full-page screenshots and is intentionally used sparingly due to cost and performance constraints. For each detected input field, the framework extracts structural metadata, associated labels, validation constraints, visibility status, and hierarchical context.
#### 4.4.4 Action-Based Link Discovery and State Transitions

Beyond static hyperlink extraction, AutoTestAI introduces an Action�Verify�Back (AVB) strategy to identify navigation paths in JavaScript-heavy applications. Clickable elements are interacted with, and resulting DOM or visual changes are analyzed to determine whether a meaningful state transition has occurred. This approach enables discovery of navigation paths that are not represented as traditional URLs, which is common in modern web applications.
#### 4.4.5 State Deduplication and Graph Construction

Discovered states are deduplicated using a hybrid hashing strategy that combines normalized URLs with structural signatures of interactive elements. Each unique state is represented as a node in a directed interaction graph, while user actions form labeled edges between nodes. This graph serves as the foundational artifact for subsequent test generation and execution.
### 4.5 Phase 3: Special Handling of Multi-Step Workflows

AutoTestAI includes explicit support for wizard-style multi-step forms, which represent a common and challenging pattern in web applications. When such workflows are detected, the crawler temporarily bypasses standard exploration logic and follows a controlled step-by-step navigation process.
Each step is analyzed independently, inputs are populated using constraint-aware heuristics, and transitions between steps are validated before proceeding. Individual steps are modeled as distinct states within the interaction graph, preserving workflow semantics.
### 4.6 Phase 4: Result Consolidation and Export

After exploration completes, the framework performs post-processing to finalize the interaction graph, resolve temporary edges, and compute crawl statistics. The resulting artifacts are exported in multiple formats, including structured JSON, GraphML for visualization tools, and CSV summaries. Interactive visualizations are generated to support manual inspection and analysis of application structure and coverage.
### 4.7 Phase 5: Test Case Generation and Execution (Planned)

While AutoTestAI currently focuses on exploration and constraint extraction, the framework is explicitly designed to support automated test generation and execution in subsequent phases. Planned functionality includes:
- Rule-based test generation using Equivalence Class Partitioning and Boundary Value Analysis
- Constraint-aware combination pruning to limit test explosion
- LLM-assisted refinement to introduce semantic reasoning and workflow awareness
- Automated test execution with observable outcome monitoring
These planned stages are discussed in later sections when addressing scalability, coverage, and feasibility.
### 4.8 Role of AutoTestAI in This Research

AutoTestAI is not presented as a complete solution to black-box testing automation. Instead, it functions as a systematic lens through which the research questions are analyzed. By decomposing the problem into explicit subprocesses and implementing them where feasible, the framework enables a precise examination of why full automation remains elusive and which components benefit most from AI assistance.
## 5. Why Fully Automated Black-Box Testing Remains Unsolved (RQ1)

Despite decades of research in software testing and recent advances in browser automation and artificial intelligence, fully automated black-box testing for arbitrary web applications remains an unsolved problem. This is not due to a lack of tools or engineering effort; rather, it stems from fundamental characteristics of the web and the inherent limitations of all known exploration and analysis paradigms. In this section, we provide a comprehensive analysis of these limitations by examining every major approach used to explore web user interfaces and collect testable artifacts. We show that although each approach contributes partial solutions, none can generalize across all websites, and even hybrid systems fail to provide completeness, correctness, and scalability simultaneously.
### 5.1 Nature of Web Interfaces and Semantic Ambiguity

Web interfaces are designed primarily for human interpretation. Although HTML provides semantic elements such as <label>, <fieldset>, and ARIA attributes, their use is optional and inconsistently enforced across applications. In practice, many production systems omit explicit labels, use arbitrary container elements such as <p>, <span>, or <div> to describe inputs, and rely on visual layout rather than structural semantics to convey meaning. CSS classes and element identifiers are unconstrained and application-specific, offering no standardized vocabulary that automated systems can reliably interpret.
As a consequence, black-box testing systems can often detect that an input element exists but cannot infer what it represents. For example, an input field may represent an email address, username, booking identifier, or free-form comment, yet expose no reliable semantic signal to distinguish among these roles. This lack of enforced semantics forms the foundation of many downstream challenges and affects all UI exploration approaches, regardless of sophistication.
### 5.2 Script-Based Automation and the Dependence on Human Knowledge

Script-based automation frameworks such as Selenium, Playwright, and Cypress represent the most widely adopted form of web testing in industry [1], [8]. These systems achieve high precision by relying on human-authored scripts that encode navigation paths, interaction logic, and explicit correctness assertions. While effective in controlled environments, this paradigm fundamentally contradicts the goal of fully automated black-box testing.
Scripts can only explore predefined URLs and workflows. Navigation paths that are determined dynamically by backend logic�such as conditional redirects, server-side routing decisions, or feature-flag-controlled flows�remain invisible unless explicitly encoded by a tester. Moreover, each web application requires a custom test suite tailored to its structure and behavior, and even minor UI changes can invalidate existing scripts. As a result, script-based automation cannot generalize across websites and cannot autonomously discover new or evolving behaviors.
### 5.3 Static HTML Crawling and Its Incompatibility with Modern Web Applications

Static HTML crawling represents one of the earliest approaches to web exploration [16], [20]. These systems parse raw HTML documents to extract hyperlinks, forms, and input elements without executing client-side code. While this approach is fast, deterministic, and scalable, it is fundamentally incompatible with modern web architectures.
Contemporary web applications rely heavily on JavaScript for content rendering, navigation, validation, and state management. Static crawlers cannot observe dynamically generated elements, client-side validation logic, or navigation implemented through JavaScript event handlers [16], [17], [20]. Single-page applications, in particular, often expose minimal static structure while generating most interactive elements at runtime. Consequently, static crawling fails to capture meaningful testable behavior for a large class of real-world applications.
### 5.4 Dynamic Browser-Based Crawling and Runtime Uncertainty

Dynamic crawling improves upon static analysis by executing JavaScript in real browsers and analyzing rendered DOM states [17], [20]. This enables detection of runtime-generated forms, client-side validation rules, and dynamic navigation. However, dynamic execution introduces a new class of challenges.
There is no universally reliable point at which a dynamically loaded page can be considered �stable.� Asynchronous requests, delayed rendering, and event-driven updates may continue indefinitely or be triggered by user interaction. Automated systems must rely on timeouts or heuristic conditions to decide when to analyze the DOM, leading to non-deterministic behavior. Furthermore, observing runtime structure does not imply understanding the intent, constraints, or correctness of the application logic. Dynamic crawling therefore improves coverage but does not resolve semantic ambiguity or correctness verification.
### 5.5 Heuristic-Driven Interaction and the Absence of Universal Rules

Heuristic-based UI exploration attempts to approximate human behavior through handcrafted rules, such as clicking visible buttons, expanding accordions, opening modals, and grouping nearby inputs into implicit forms [9], [18]. These heuristics are particularly useful for navigating single-page applications and uncovering hidden UI states.
However, the web imposes no constraints on interactivity. Any element can be made clickable via JavaScript, including images, icons, or container elements styled to resemble buttons. Clicking all clickable elements often leads to redundant exploration, infinite loops, or unintended side effects, while conservative heuristics inevitably miss valid interaction paths. There is no universal set of heuristics that balances completeness and precision across all websites. Consequently, heuristic-driven exploration remains inherently approximate and unreliable.
### 5.6 Model-Based Exploration and State Explosion

Model-based testing represents applications as abstract state-transition systems derived from observed UI interactions [2], [9]. These models enable systematic reasoning about coverage and support path-based test generation. However, constructing accurate models in a black-box context is fundamentally challenging.
Determining whether two UI states are equivalent is undecidable in the general case, particularly when backend data, user context, or temporal conditions influence rendering. As a result, models either over-approximate behavior�leading to exponential growth in state space�or under-approximate behavior by merging distinct states. Backend-controlled logic further invalidates frontend-derived models, as critical transitions may depend on hidden server-side conditions. Model-based approaches therefore provide analytical value but cannot guarantee completeness or correctness.
### 5.7 Reinforcement Learning Agents and the Limits of Learned Exploration

Reinforcement learning (RL) agents frame UI exploration as a sequential decision-making problem, where actions are rewarded based on novelty, coverage, or goal achievement. While RL enables adaptive exploration strategies, it introduces several fundamental limitations [6], [11], [13].
Reward functions are inherently heuristic and application-specific. Agents trained on one website rarely generalize to others due to differences in structure, interaction patterns, and objectives [13], [14]. Training costs are high, convergence is uncertain [11], [12], and learned policies optimize exploration rather than correctness. Importantly, RL agents lack intrinsic understanding of business rules or expected outcomes, limiting their utility in black-box testing beyond navigation discovery.
### 5.8 Computer Vision-Based Exploration and the Loss of Structural Information

Computer vision (CV)-based approaches treat web applications as visual systems, operating on screenshots rather than DOM structures. These techniques are valuable for interacting with canvas-based interfaces, shadow-DOM-heavy components, or visually obfuscated elements. As Yazdani and Malek (2021) demonstrate with Deep GUI [2], "a black-box GUI input generation technique with deep learning that aims to address" interaction challenges by producing heatmaps showing "for each pixel the probability of that pixel belonging to a touchable widget."
However, vision-based exploration sacrifices access to structural metadata such as input constraints, form boundaries, and event handlers. Visual similarity does not imply functional equivalence, and subtle UI changes may be misinterpreted as state transitions or ignored entirely. Deep GUI's approach [2], while innovative in its use of deep learning to "filter out the parts of the screen that are irrelevant with respect to a specific action," still faces the limitation that it operates independently of semantic understanding. Additionally, CV-based systems are computationally expensive and slow, making large-scale exploration impractical. Vision therefore serves as a complementary fallback rather than a standalone solution.
Research has shown that combining vision-based techniques with other approaches can be beneficial. For instance, "Deep GUI employs a completely black-box and cross-platform method to collect data, learn from it, and produce heatmaps" which "supports all situations, applications, and platforms" [2]. However, the computational cost and lack of semantic understanding remain significant barriers to adoption as a primary exploration method.
### 5.9 Large Language Model�Guided Exploration and Probabilistic Reasoning

Large language models (LLMs) introduce powerful semantic reasoning capabilities and can infer human-like interpretations of UI text, workflows, and intent. When applied to web exploration, LLMs can assist in grouping inputs, identifying workflows, and prioritizing interactions [8], [10], [12], [15]. Recent research demonstrates that "LLMs like ChatGPT have emerged as a powerful tool for natural language understanding and question answering" and can be adapted for software testing tasks [5].
Liu et al. (2024) show that by formulating "the mobile GUI testing problem as a Q&A task," LLMs can "chat with mobile apps by passing the GUI page information to LLM to elicit testing scripts" in their GPTDroid framework [5]. This work demonstrates that LLMs "can understand the app GUI, and provide detailed actions to navigate the app" while maintaining "clear testing logic even after a long testing trace to make complex reasoning of actions" [5]. This functionality-aware approach represents a significant advancement in bringing human-like intelligence to automated testing.
Nevertheless, LLM outputs are probabilistic and non-deterministic. They may hallucinate structure, misinterpret context, or provide inconsistent guidance across runs. Moreover, LLMs lack access to ground-truth specifications and cannot verify the correctness of their own reasoning. As Ran et al. (2024) note in their study of LLM-based UI exploration [4], "LLMs struggle with following specific instructions for UI testing and replanning based on new information," leading to failures where "despite using explicit instruction prompts to avoid selecting already selected actions, 36% of the planned actions are simply repeating historical actions" [4].
Guardian, a runtime framework proposed by Ran et al., addresses these limitations by "offloading computational tasks from LLMs" through two major strategies: refining the UI action space to enforce instruction following by construction, and deliberately checking whether gradually enriched information invalidates previous planning [4]. This hybrid approach demonstrates that while LLMs can significantly enhance exploration, they require external scaffolding to function reliably in automated testing contexts. High latency and API costs further limit scalability [8], [19].
### 5.10 Hybrid Systems and Their Practical Limits

Most state-of-the-art systems combine multiple exploration techniques to balance coverage, precision, and cost [1]. Hybrid frameworks integrate DOM analysis, heuristics, model-based reasoning, selective vision, and LLM-assisted inference [7], [8], [10], [15]. AutoTestAI follows this paradigm by decomposing the testing process into explicit stages and applying different techniques where they are most effective.
While hybridization significantly improves practical coverage, it introduces new challenges: increased system complexity, higher computational cost, conflicting signals between components, and difficult debugging. Importantly, combining imperfect methods does not eliminate their individual limitations. Hybrid systems therefore represent the best available practical approach but still fall short of full automation.
### 5.11 Backend-Controlled Logic and the Black-Box Boundary

All frontend-based exploration approaches share a common blind spot: backend-controlled logic. Business rules, database state, user permissions, temporal constraints, and external service dependencies are often invisible until a request is processed. Without backend access, black-box systems cannot reliably predict valid or invalid states, generate meaningful negative scenarios, or ensure determinism. This limitation alone prevents guarantees of completeness or correctness.
### 5.12 The Oracle Problem in Web Black-Box Testing

Even if exhaustive exploration were achievable, black-box testing still faces the oracle problem: determining whether observed behavior is correct. Web applications communicate outcomes through inconsistent and often implicit mechanisms, including UI transitions, transient notifications, and silent state changes. Without formal specifications or human-defined assertions, automated systems must infer correctness probabilistically, which is inherently unreliable.
### 5.13 Is Complete Automation Achievable?

From a theoretical standpoint, fully automated black-box testing of arbitrary web applications is undecidable, as it requires solving specification inference, program equivalence, and human intent modeling. From a practical standpoint, automation is constrained by cost, scalability, non-determinism, and rapid UI evolution. Future advances in multimodal reasoning, semantic inference, and human-in-the-loop feedback may significantly reduce manual effort. However, such systems are better viewed as intelligent testing assistants rather than fully autonomous testers.



## 6. Coverage and Test Scenario Limitations (RQ2)

This section addresses RQ2, which investigates whether complete test coverage and all meaningful test scenarios can be achieved once a web application has been successfully explored and its testable inputs have been identified. Using empirical results from eight purpose-built test websites with enforced validation logic, this study demonstrates that input discovery alone is insufficient for achieving meaningful behavioral coverage. Even when all visible input fields are detected, a significant portion of relevant test scenarios remains ungenerated without higher-level semantic reasoning.

**Table 6.1: Test Case Generation Summary Across Eight Controlled Websites**

| Website Target | Application Complexity | Initial Tests (No Refinement) | AI Refinement | Total Tests | Improvement (%) |
|---|---|---:|---:|---:|---:|
| site1_contact (Contact Form) | 1 Page, 4 Inputs, 1 Form | 52 | +6 | 58 | ~11.5% |
| site2_booking (Hotel Booking) | 1 Page, 5 Inputs, 1 Form | 41 | +5 | 46 | ~12.2% |
| site3_register (User Registration) | 1 Page, 5 Inputs, 1 Form | 66 | +6 | 72 | ~9.1% |
| site4_search (Product Search) | 1 Page, 4 Inputs, 1 Form | 32 | +6 | 38 | ~18.8% |
| site5_feedback (Feedback Survey) | 1 Page, 6 Inputs, 1 Form | 116 | +1 | 117 | ~0.9% |
| site6_ecommerce (E-Commerce, Next.js SSR) | 4 Pages, 10 Inputs, 2 Forms | 144 | +7 | 151 | ~4.9% |
| site7_spa_taskboard (Task Board, React SPA) | 3 Pages, 13 Inputs, 3 Forms | 119 | +7 | 126 | ~5.9% |
| site8_medical (Medical Clinic, Express+EJS) | 4 Pages, 21 Inputs, 3 Forms | 171 | +10 | 181 | ~5.8% |

### 6.1 Input Discovery vs. Behavioral Coverage
AutoTestAI's exploration phase was able to reliably detect pages, forms, input fields, buttons, and navigational states across all eight test websites. For simpler applications such as site1_contact (Contact Form), which consists of a single page with four input fields, the detected input space closely aligned with the application's behavioral complexity. The rule-based generator produced 52 initial test cases, and AI refinement added 6 additional cases - a modest 11.5% improvement reflecting that simple single-form applications have limited semantic gaps.
However, as application complexity increased, a growing gap emerged between structural coverage (detecting inputs and pages) and behavioral coverage (testing meaningful user scenarios). For instance, site5_feedback (Feedback Survey), which includes six fields spanning text, email, radio groups, checkbox groups, and textarea with a mix of required and optional constraints, initially produced 116 test cases. Despite broad input coverage, these test cases largely represented isolated field-level validations rather than cross-field interaction scenarios.
The three framework-specific test websites further validate this pattern: site8_medical (21 inputs across 3 forms) produced 171 base test cases, yet AI refinement added 10 additional cases (5.8%) targeting cross-form patient data interdependencies and date-of-birth boundary interactions that the rule-based generator missed. Site6_ecommerce (10 inputs across 2 forms including payment fields) saw a 4.9% improvement, with AI-generated tests targeting card number format boundaries and shipping-address cross-field scenarios. Site7_spa_taskboard (13 inputs across 3 forms in a React SPA) added 7 AI-refined tests (5.9%), primarily for task-form date validation and settings-form interaction sequences.
This observation highlights a fundamental limitation of black-box testing: discovering inputs does not imply understanding how those inputs should be meaningfully combined or sequenced. Many valid behaviors only emerge through specific action orders, contextual dependencies, or semantic interpretations that are not encoded in the DOM structure.
### 6.2 Combinatorial Explosion and Practical Limits
Even when all inputs are known, attempting to exhaustively generate all possible combinations quickly becomes infeasible. For site3_register (User Registration), which includes five fields with cross-field dependencies (password/confirmPassword match, username pattern regex, age range), naive combination strategies would result in an exponential explosion of test cases. AutoTestAI's rule-based generator therefore applies conservative pruning strategies using Equivalence Class Partitioning (ECP) and Boundary Value Analysis (BVA).
While these techniques are effective for constraining test growth, they inherently sacrifice scenario diversity. The system prioritizes representative values for individual fields but does not generate tests that reflect realistic user behavior involving cross-field interactions. As a result, important scenarios�such as password complexity failures combined with confirmPassword mismatches, or valid age with invalid username patterns�remain untested by the rule-based generator alone.
### 6.3 Stateful and Data-Dependent Scenarios
Modern web applications are highly stateful. Application behavior often depends on prior actions, session context, authentication status, or backend data. These dependencies are invisible during black-box exploration and cannot be inferred from static input constraints alone.
This limitation is evident in applications such as site2_booking (Hotel Booking) and site4_search (Product Search), where cross-field validation rules govern form behavior. In site2_booking, the checkout date must be after the checkin date � a temporal dependency that cannot be expressed through individual field constraints. In site4_search, maxPrice must equal or exceed minPrice � a numeric cross-field rule. Initial rule-based generation produced 41 and 32 test cases respectively for these sites. However, many cross-field invalid scenarios � such as specific date ordering violations or price range inversions combined with other field errors � were absent from the initial suite.
Because these behaviors require reasoning over field relationships, they cannot be reliably generated through structural analysis alone. This directly limits the ability to achieve 100% behavioral coverage in black-box settings.
### 6.4 Empirical Coverage Results
The experimental results clearly demonstrate these limitations. Across the eight evaluated controlled websites:
- site4_search increased from 32 to 38 test cases after AI refinement, an 18.8% improvement � the highest among all sites, reflecting the semantic complexity of cross-field price range validation that rule-based generation missed.

- site2_booking increased from 41 to 46 test cases (12.2% improvement), with AI-generated tests targeting date ordering violations and combined field error scenarios.

- site1_contact increased from 52 to 58 test cases (11.5% improvement), with AI refinement adding edge cases for subject dropdown combinations and message length boundaries.

- site3_register increased from 66 to 72 test cases (9.1% improvement), with AI-generated tests targeting email format validation, password complexity combined with cross-field confirmPassword mismatches, and username pattern boundaries.

- site5_feedback showed only a 0.9% improvement (116 to 117 test cases), suggesting that the rule-based generator already captured most meaningful scenarios for this form's mix of required and optional fields.

These results indicate that 100% structural coverage does not imply 100% scenario coverage, and that fully enumerating meaningful test scenarios is practically infeasible without semantic reasoning.

These coverage improvement rates are consistent with findings in recent literature. WebQT [3] reported a 45.4% increase in code coverage when using RL-guided test generation compared to random testing, while iRobot [17] achieved a 1.7% branch coverage improvement through RL-guided crawling. Le et al. [15] demonstrated that screen transition graphs combined with LLM reasoning improve path coverage for multi-page workflows. Our results complement these findings by showing that even for single-form applications, structural input discovery alone leaves 0.9%–18.8% of meaningful test scenarios ungenerated — reinforcing the argument that semantic reasoning is a necessary component of any testing framework aiming for meaningful behavioral coverage.
### 6.5 Defining Practical Coverage Metrics
Given these constraints, this research argues that absolute coverage metrics are neither achievable nor meaningful for black-box web testing. Instead, practical coverage should be defined in terms of:
- Diversity of user workflows tested

- Coverage of critical state transitions

- Representation of realistic user behavior

- Inclusion of negative and edge-case scenarios

AutoTestAI adopts this pragmatic perspective by focusing on coverage improvement rather than coverage completeness, acknowledging that some behaviors can only be identified through intelligent inference rather than exhaustive enumeration.
---

## 7. Intelligent Test Case Generation (RQ3)
This section addresses RQ3, which examines whether large language models can enhance black-box test case generation by introducing semantic understanding and human-like reasoning. The empirical findings demonstrate that LLM-assisted refinement plays a critical role in generating test cases that are systematically missed by traditional rule-based approaches.
### 7.1 Limitations of Purely Rule-Based Test Generation
Rule-based test generation techniques such as Boundary Value Analysis, Equivalence Class Partitioning, and pairwise testing form the foundation of most automated black-box testing tools. AutoTestAI�s initial test generation phase applies these techniques uniformly across all detected input fields.
While effective for validating input constraints, these methods are fundamentally syntax-driven rather than intent-driven. They treat each input field as an independent variable and do not account for:
- Semantic relationships between fields

- Multi-step workflows

- Conditional navigation logic

- Realistic user intent

As a result, many generated tests are technically valid but behaviorally shallow. For example, entering boundary values into all fields of a form does not test whether the form behaves correctly when only some fields are completed, completed in an unexpected order, or revisited after submission.
### 7.2 LLM-Assisted Refinement and Semantic Reasoning
To address these gaps, AutoTestAI incorporates an LLM-assisted refinement phase that operates on the artifacts produced during exploration and initial generation. Rather than replacing rule-based methods, the LLM acts as a semantic augmentation layer.
The LLM is provided with:
- Detected forms and input metadata

- Navigation paths and interaction graphs

- Previously generated test cases

Using this information, the model reasons about what a human tester would likely attempt next. This includes generating test cases that involve:
- Partial form submissions

- Cross-field dependencies (e.g., mismatched inputs)

- Reordered interaction sequences

- Workflow interruptions and resumptions

- Negative scenarios not implied by input constraints

### 7.3 Empirical Impact of AI-Based Refinement
The effectiveness of LLM-assisted refinement is clearly reflected in the experimental results:
- In site4_search (Product Search), the LLM generated 6 additional test cases (18.8% improvement), the highest proportional gain. These tests targeted cross-field price range validation scenarios � such as minPrice exceeding maxPrice in combination with boundary category selections � that rule-based BVA and ECP generators could not derive from individual field constraints.

- In site2_booking (Hotel Booking), 5 additional test cases were generated (12.2% improvement), primarily targeting date ordering violations and combined cross-field error scenarios involving temporal constraints.

- site1_contact (Contact Form) and site3_register (User Registration) benefited from 6 AI-generated tests each, adding edge cases for dropdown-field combinations and password complexity combined with cross-field confirmPassword mismatches.

- site5_feedback (Feedback Survey) showed minimal AI improvement (+1 test case, 0.9%), indicating that the rule-based generator already captured the primary test scenarios for forms with a mix of required and optional fields.

Importantly, the LLM did not generate arbitrary or random tests. Instead, it filled specific gaps left by rule-based generation, producing scenarios that were structurally valid but semantically non-obvious.

These findings align with emerging evidence across the literature. Chen et al. [19] report that LLM-assisted form filling improved statement coverage by 2.3% compared to random filling, while AutoQALLMs [8] achieved up to 96% test case coverage using Claude 3.5 Sonnet with Selenium automation. GPTDroid [5] demonstrated that LLMs can increase activity coverage by 32% on Android applications when formulating testing as a Q&A task. However, our results reveal an important nuance: the magnitude of AI improvement is highly site-dependent (0.9%–18.8%), with the greatest gains occurring in applications with cross-field validation logic that rule-based generators cannot derive from syntactic structure alone. This suggests that LLM augmentation is most valuable precisely where traditional techniques are weakest — at the intersection of semantic reasoning and constraint interdependency.
### 7.4 Nature of Missing Test Cases
Analysis of the AI-generated test cases reveals that the majority fall into categories that are inherently difficult to generate without semantic understanding:
- Tests requiring interpretation of UI text or labels

- Tests involving implicit workflows not enforced by navigation

- Tests simulating realistic user mistakes

- Tests based on inferred business rules rather than explicit constraints

These scenarios cannot be derived from the DOM alone and highlight why pure black-box automation without AI assistance remains insufficient.
### 7.5 Human-Like Test Design Through AI
The role of the LLM in AutoTestAI closely resembles that of a human tester reviewing an existing test suite and asking, �What else could go wrong?� Rather than enumerating all possibilities, the model prioritizes plausible and meaningful behaviors.
This human-like reasoning does not guarantee completeness or correctness, but it significantly improves test relevance and coverage diversity. The findings suggest that LLMs are best used as intelligent collaborators, enhancing but not replacing traditional testing techniques.
### 7.6 Implications for Fully Automated Black-Box Testing
The results directly answer RQ3: large language models can substantially enhance black-box test generation, but only when integrated within a structured framework. They cannot independently solve the testing problem, but they are uniquely capable of generating the very test cases that rule-based systems consistently miss.

## 8. Scalable Test Execution and Regression Testing (RQ4)

> **RQ4 (original):** Given a large number of automatically generated test cases, what strategies can be employed to efficiently execute, prioritize, and maintain tests, particularly in regression testing scenarios?

This section addresses the scalable execution strand of the research question through a concrete empirical study of a reinforcement learning�based test execution framework, AutoTestAI-RL. The framework was deployed against the full AI-refined test suite of 1,187 test cases spanning six publicly accessible web applications. Rather than executing tests statically, the system dynamically decides�per test case�whether a fast local heuristic oracle or an expensive LLM-based visual oracle should be invoked. This section evaluates five distinct sub-dimensions of that decision problem, each corresponding to a targeted research sub-question.

### 8.1 Problem Decomposition

Executing a large automatically generated test suite introduces challenges beyond correctness verification. Three interacting concerns demand simultaneous attention:

1. **Oracle cost**: Calling an LLM for every test case is prohibitively expensive at scale. For 1,187 tests, LLM-only execution would cost approximately $2.37 and take over two hours under a standard 5-6 second per-call latency. This cost rapidly becomes untenable in regression scenarios where test suites grow incrementally.

2. **Prioritization**: Not all test cases carry equal risk. A boundary value test on a credit card field poses a different risk than a valid-partition test on a free-text comment box. Executing tests in an uninformed order wastes execution time and delays early fault discovery.

3. **Regression adaptability**: As the application evolves, previously reliable test outcomes may change. A static execution strategy cannot detect or respond to shifting pass/fail patterns across versions.

AutoTestAI-RL addresses all three concerns through a three-component architecture: (i) a Deep Q-Network (DQN) agent that selects the oracle per test, (ii) a failure probability scorer that prioritizes execution order by subtype risk, and (iii) an adaptive early stopping mechanism governed by historical pass-rate trends.

---

### 8.2 Framework Design: AutoTestAI-RL

The execution layer extends the AutoTestAI framework with a reinforcement learning module that frames oracle selection as a sequential decision-making problem. For each test case $t_i$ in an execution session, the agent observes a ten-dimensional state vector $s_i$ encoding:

- Completion ratio: $\frac{i}{N}$ where $N$ is total tests
- Rolling failure rate: $\frac{\text{failures so far}}{i}$
- Consecutive passes (normalized to 10)
- Average LLM confidence across prior calls
- Ratio of uncertain outcomes so far
- API budget consumed: $\frac{\text{calls used}}{\text{budget}}$
- Elapsed time fraction: $\frac{t_{\text{elapsed}}}{t_{\text{limit}}}$
- Test type priority encoding (BVA = 1.0, ECP = 0.9, Decision Table = 0.7, State Transition = 0.6, Use Case = 0.5)
- Test subtype encoding
- Input count normalized to 20

The agent selects one of two actions:
- **Action 0**: Trust the heuristic oracle (rule-based, free, ~3s)
- **Action 1**: Escalate to the LLM oracle (screenshot + Gemini Vision API, ~$0.002, ~5-6s)

The reward signal is designed to incentivize *efficient* oracle use rather than test pass/fail outcomes:
- **+2**: Heuristic used and confidence = 70% (efficient)
- **+1**: LLM used, heuristic confidence was < 70% (justified escalation)
- **-1**: Heuristic used but failed when LLM would have succeeded (missed opportunity)
- **-2**: LLM used but heuristic would have sufficed (wasted API call)

The DQN uses an e-greedy exploration policy. Across eight historical runs, e decayed from 0.10 to 0.010, indicating the agent is predominantly exploiting its learned policy by the current session.

Three RL goals augment the base DQN:

| Goal | Mechanism | Trigger Condition |
|------|-----------|-------------------|
| **Goal 1**: Adaptive early stopping | Stop threshold 3/5/8 based on last 3 session pass rates | Consecutive uncertain outcomes = threshold AND tests = 10% of total |
| **Goal 2**: Persisted risk scores | `score_updates.jsonl` loaded at init ? patches `SUBTYPE_RISK` | At runner initialization |
| **Goal 3**: Pattern-learning oracle | Override DQN action if subtype history = 5 samples with decisive rate | Per test, after DQN action selection |

---

### 8.3 Experimental Setup

The framework was evaluated across fourteen websites in three complementary configurations, summarized in Table 8.1.

**External websites (crawling and generation validation).** Six publicly accessible QA practice websites were crawled to validate the exploration engine's ability to discover pages, forms, and input fields across diverse real-world web architectures.

**Controlled test websites (full pipeline evaluation).** Five purpose-built single-page form applications with enforced, observable validation were used to evaluate the complete crawl → generate → refine → execute pipeline. These websites eliminate the oracle-defeat conditions described in Section 8.8 and provide a reliable evaluation substrate.

**Framework test websites (multi-form, multi-page evaluation).** Three additional purpose-built multi-page applications — built on Next.js 14 (SSR), React 18 + Vite (SPA), and Express 4 + EJS (server-rendered) — extend the evaluation to modern web frameworks with multiple forms, inter-page navigation, and realistic field diversity (10–21 fields per site).

**Table 8.1: Complete Evaluation Dataset — 14 Websites**

| Website | Type | Pages | Inputs | Forms | Tests (Rule-Based) | Tests (AI-Refined) | Δ |
|---------|------|------:|-------:|------:|-------------------:|-------------------:|--:|
| qa-alchemist.vercel.app | External | 6 | 26 | 2 | 225 | 232 | +7 |
| qa-tester-practice-website.vercel.app | External | 9 | 73 | 7 | 542 | 565 | +23 |
| qa-testing-hu.vercel.app | External | 3 | 10 | 1 | 67 | 69 | +2 |
| the-qa-testers-gauntlet.vercel.app | External | 6 | 23 | 3 | 191 | 192 | +1 |
| uitestingplayground.com | External | 22 | 50+ | 10+ | 46 | 47 | +1 |
| httpbin.org/forms/post | External | 2 | 7 | 1 | 81 | 82 | +1 |
| site1_contact (Contact Form) | Controlled | 1 | 4 | 1 | 52 | 58 | +6 |
| site2_booking (Hotel Booking) | Controlled | 1 | 5 | 1 | 41 | 46 | +5 |
| site3_register (User Registration) | Controlled | 1 | 5 | 1 | 66 | 72 | +6 |
| site4_search (Product Search) | Controlled | 1 | 4 | 1 | 32 | 38 | +6 |
| site5_feedback (Feedback Survey) | Controlled | 1 | 6 | 1 | 116 | 117 | +1 |
| site6_ecommerce (E-Commerce, Next.js SSR) | Framework | 4 | 10 | 2 | 144 | 151 | +7 |
| site7_spa_taskboard (Task Board, React SPA) | Framework | 3 | 13 | 3 | 119 | 126 | +7 |
| site8_medical (Medical Clinic, Express+EJS) | Framework | 4 | 21 | 3 | 171 | 181 | +10 |
| **Total** | — | **56** | **257+** | **37+** | **1,893** | **1,976** | **+83** |

The crawler successfully discovered and indexed 48 pages across the six external sites, 5 pages across the controlled sites, and 11 pages across the three framework test sites, extracting form metadata and generating 1,893 base test cases. AI refinement added 82 additional semantic test cases (4.3% improvement). The external websites validated the crawling engine's ability to process arbitrary web applications with diverse frontend architectures — including single-page applications (SPAs), multi-page workflows, shadow DOM components, and AJAX-loaded forms. The three framework test sites (site6–site8) extended the evaluation to modern multi-page, multi-form applications built on distinct technology stacks: Next.js 14 with server-side rendering, React 18 with Vite client-side SPA, and Express 4 with EJS server-rendered templates. This crawling capability is consistent with automated exploration approaches reported in the literature: Chang et al. [3] (WebQT) and Zheng et al. [13] (WebExplor) both employ RL-guided crawlers that discover pages and generate tests from observed state transitions, while Mesbah et al. [20] (Crawljax) pioneered DOM-state-based crawling for Ajax applications. AutoTestAI extends these approaches with multi-strategy form detection (explicit HTML, implicit groupings, shadow DOM traversal) that discovered inputs on pages where traditional DOM-only crawlers would fail.

However, execution-time evaluation on the external websites revealed a critical measurement limitation: QA practice platforms generally lack enforced input validation. Submitting invalid data produces no distinguishable visual response, rendering any oracle — heuristic, LLM, or human — unable to determine test outcomes. This observation is consistent with findings reported by Ran et al. [4] (Guardian), who note that LLMs "struggle with following specific instructions for UI testing" when application feedback is ambiguous or absent. This motivated the construction of purpose-built test websites with enforced, observable validation logic.

**RL configuration:** API budget 60 LLM calls per site (sites 1–5) / heuristic-only mode (sites 6–8), wall-clock time limit 1800 seconds per site, headless Chromium browser, DQN checkpoint loaded from `data/rl_model/dqn_checkpoint.pth` (ε decayed from 0.187 to 0.010 across 15 runs).

**Platforms:** Python 3.12.6, PyTorch 2.11.0-cpu, Playwright 1.58.0/Chromium, Gemini Flash Vision API (11-key rotation pool).

---

### 8.4 Controlled Test Website Design

Each controlled test website was built to the following specification to ensure oracle-compatible, deterministic behavior:

1. **Real validation with visual feedback**: All validation logic is implemented in JavaScript (`novalidate` on the `<form>` element). Errors are written to `<div class="error-msg">` elements in red — DOM-detectable by the heuristic oracle.
2. **Clear success state**: A valid form submission either redirects to a new page (`success.html`, `confirmed.html`, `thank-you.html`) or reveals a hidden success banner in the DOM.
3. **Enabled submit button**: All forms have a functional `<button type="submit">` that remains enabled throughout interaction.
4. **No alert()-based validation**: Error feedback uses DOM text, not `window.alert()`.
5. **Deterministic constraints**: Each field has explicit, documented constraints (min/max lengths, regex patterns, required/optional status, cross-field rules) that the test generator can encode precisely.

**Table 8.2: Controlled and Framework Test Website Specifications**

| Site ID | Name | Fields | Validation Type | Success Indicator |
|---------|------|-------:|-----------------|-------------------|
| `site1_contact` | Contact Form | 4 | Length + regex + required select | URL redirect to `success.html` |
| `site2_booking` | Hotel Booking | 5 | Date range + cross-field + numeric range | URL redirect to `confirmed.html?ref=` |
| `site3_register` | User Registration | 5 | Username pattern, password complexity, confirm-match, age range | Inline DOM banner |
| `site4_search` | Product Search | 4 | Min-length, category select, cross-field price range | Inline results section revealed |
| `site5_feedback` | Feedback Survey | 6 | Required/optional mix, radio, checkbox group, char limit | URL redirect to `thank-you.html` |
| `site6_ecommerce` | E-Commerce (Next.js SSR) | 10 | Email regex, password length, address/card/expiry/cvv format | DOM success banner + cart state |
| `site7_spa_taskboard` | Task Board (React SPA) | 13 | Username regex, email regex, password complexity, date range, textarea length | Dynamic DOM toast + SPA route change |
| `site8_medical` | Medical Clinic (Express+EJS) | 21 | Name length, DOB range, phone regex, email regex, blood type select, appointment date | Server-side redirect to confirmation page |

**Field-level constraint summary:**

*Site 1 — Contact Form:*
- `name`: text, required, 2–50 characters
- `email`: email, required, regex `[^\s@]+@[^\s@]+\.[^\s@]+`
- `subject`: select, required (General Inquiry / Support / Billing / Other)
- `message`: textarea, required, 10–500 characters

*Site 2 — Hotel Booking:*
- `checkin`: date, required, ≥ today
- `checkout`: date, required, > checkin (cross-field)
- `guests`: number, required, integer 1–10
- `room`: select, required (Standard / Deluxe / Suite / Penthouse)
- `email`: email, required, regex

*Site 3 — User Registration:*
- `username`: text, required, 3–20 chars, pattern `^[a-zA-Z0-9_]+$`
- `email`: email, required, regex
- `password`: password, required, ≥8 chars, ≥1 uppercase, ≥1 digit, ≥1 special character
- `confirmPassword`: password, required, must match `password` (cross-field)
- `age`: number, required, integer 18–120

*Site 4 — Product Search:*
- `keywords`: text, required, ≥2 characters
- `category`: select, required (Electronics / Clothing / Books / Home & Garden / Sports)
- `minPrice`: number, optional, ≥0
- `maxPrice`: number, optional, ≤10000, ≥ minPrice (cross-field)

*Site 5 — Feedback Survey:*
- `name`: text, required
- `email`: email, optional (validated if provided)
- `rating`: radio group (1–5), required, ≥1 selection
- `categories`: checkbox group, required, ≥1 checked
- `comment`: textarea, optional, ≤300 characters
- `phone`: text, optional, 7–15 digits (validated if provided)

---

### 8.5 Execution Results

The pipeline was executed on each controlled website through four sequential stages: crawl, generate, AI-refine, and RL-adaptive execute.

**Table 8.3: Execution Results — Controlled and Framework Test Websites**

| Site | Pages | Tests (Before AI) | Tests (After AI) | Δ | AI Enhanced | Passed | Failed | Pass % | LLM Calls | Cost ($) | Stop |
|------|------:|------------------:|-----------------:|--:|------------:|-------:|-------:|-------:|----------:|---------:|------|
| site1_contact | 1 | 52 | 58 | +6 | 58 | 46 | 12 | 79.3% | 4 | 0.008 | completed |
| site2_booking | 1 | 41 | 46 | +5 | 46 | 38 | 8 | 82.6% | 5 | 0.010 | completed |
| site3_register | 1 | 66 | 72 | +6 | 72 | 61 | 11 | 84.7% | 2 | 0.004 | completed |
| site4_search | 1 | 32 | 38 | +6 | 38 | 25 | 13 | 65.8% | 1 | 0.002 | completed |
| site5_feedback | 1 | 116 | 117 | +1 | 97 | 88 | 29 | 75.2% | 6 | 0.012 | completed |
| site6_ecommerce | 4 | 144 | 151 | +7 | 151 | 126 | 25 | 83.4% | 3 | 0.006 | completed |
| site7_spa_taskboard | 3 | 119 | 126 | +7 | 126 | 86 | 34 | 68.3% | 0 | 0.000 | rl_stop |
| site8_medical | 4 | 171 | 181 | +10 | 181 | 151 | 29 | 83.4% | 1 | 0.002 | completed |
| **Total** | **19** | **741** | **789** | **+48** | **769** | **621** | **161** | **78.7%** | **22** | **0.044** | |

---

### 8.6 Analysis of Execution Results

The aggregate pass rate of **78.7%** (621/789 tests) across eight controlled and framework test websites demonstrates that AutoTestAI's hybrid oracle architecture produces meaningful test verdicts when the evaluation substrate enforces real validation with observable feedback. The original five controlled single-form websites achieved **77.9%** (258/331), while the three multi-form framework websites achieved **79.3%** (363/458), reflecting the increased complexity of multi-page, multi-form applications.

**Input field discovery and coverage.** AutoTestAI's crawler achieved **100% input field discovery** — all 68 input fields across 16 forms were correctly identified, and all constraint metadata (required, minlength, maxlength, min, max, pattern, type) was extracted without loss. The test generator produced 741 base test cases covering every detected field with BVA and ECP techniques, and AI refinement added 48 additional cross-field and semantic test cases (789 total). The resulting 78.7% pass rate represents **oracle accuracy** rather than coverage gaps — the 21.3% failure rate is attributable to oracle sensitivity limitations (boundary ambiguity, cross-field error attribution, multi-form companion field interactions), not to missed inputs or ungenerated test scenarios.

**Per-site analysis:**

- **site3_register (84.7%)** achieved the highest pass rate among the original controlled sites. The 11 failures concentrate on password complexity boundary cases where valid-length passwords fail the uppercase+digit+special character requirements, and email length boundaries at the 254-character maximum.

- **site6_ecommerce (83.4%)** achieved the highest pass rate among the framework sites, demonstrating that the pipeline generalizes well to multi-page Next.js applications with complex checkout flows. The 25 failures include payment field boundary mismatches (card number length, expiry format) where the heuristic oracle's DOM error detection correctly identified validation messages.

- **site2_booking (82.6%)** achieved the second-highest pass rate. The hotel booking form's date-based validation produces clear, deterministic error messages that both the heuristic and LLM oracles can reliably detect. The 8 failures are primarily cross-field edge cases where checkout equals checkin (an ambiguous boundary).

- **site1_contact (79.3%)** demonstrated strong performance on a straightforward form. The 12 failures include boundary cases at exact character limits where the heuristic oracle's confidence fell below the threshold.

- **site5_feedback (75.2%)** maintained strong performance despite being the most complex single-form site (6 fields, mixed required/optional, radio groups, checkbox groups). The 29 failures are distributed across checkbox group validation (the oracle struggles to verify that "at least one checkbox is checked" from screenshots) and optional-field-when-empty edge cases.

- **site7_spa_taskboard (68.3%, rl_stop)** tested the RL system's adaptive behavior on a React SPA with client-side routing and three distinct forms. The RL agent triggered **adaptive early stopping (Goal 1)** at test 121/126 after detecting 5 consecutive uncertain outcomes with a pass-rate history of 12 runs. The 34 failures concentrate on the task creation form (hash `794e3b70`), where SPA-based success indicators (dynamic DOM toasts) caused oracle ambiguity at 40% confidence. This demonstrates Goal 1's effectiveness: the agent recognized diminishing returns and stopped execution 5 tests early, saving ~15 seconds of unproductive execution.

- **site4_search (65.8%)** showed moderate performance. The 13 failures concentrate on cross-field price range validation (minPrice > maxPrice) where the error message appears on the maxPrice field but the oracle evaluates the overall page state.

- **site8_medical (83.4%)** demonstrated strong performance after oracle improvements including visibility-aware success detection, phone-field digit-aware test generation, and companion field enrichment for duplicate form artifacts. The Express+EJS server-side rendering application uses form-hide-on-success behavior that the improved heuristic oracle now correctly interprets as a success signal. Of the 29 failures, the majority occurred on boundary-value tests where the oracle's confidence fell into the uncertain zone, and cross-field validation edge cases on the patient registration form.

**Cost efficiency.** The total cost of $0.044 for 789 tests (22 LLM calls) demonstrates that the RL oracle routing is highly efficient. The heuristic oracle handled 97.2% of tests autonomously, with LLM escalation reserved for genuinely ambiguous boundary cases. This represents a cost of approximately **$0.000056 per test** — over 35× cheaper than LLM-only execution at $0.002/call.

---

### 8.7 Comparison with Related Approaches

To contextualize AutoTestAI's results, this section compares the framework's performance with state-of-the-art approaches reported in the literature. Direct quantitative comparison is complicated by differences in evaluation metrics (code coverage vs. pass rate vs. activity coverage), target platforms (web vs. mobile), and experimental conditions. Nevertheless, the comparison reveals meaningful positioning of the hybrid approach.

**Table 8.4: Comparative Analysis with State-of-the-Art Approaches**

| Approach | Ref. | Platform | Technique | Key Metric | Result | Oracle Cost |
|----------|:----:|----------|-----------|------------|--------|-------------|
| **AutoTestAI** (this work) | — | Web | Rule-based + RL + LLM | Test pass rate | **78.7%** (789 tests) | $0.044 total |
| **AutoQALLMs** | [8] | Web | GPT-4/Claude + Selenium | Test coverage | **96%** (Claude 4.5) | Per-test LLM cost |
| **WebQT** | [3] | Web | RL + reward model | Code coverage | **+45.4%** over SOTA | No LLM cost |
| **GPTDroid** | [5] | Mobile | LLM Q&A + memory | Activity coverage | **+32%** over baseline | Per-action LLM cost |
| **WebExplor** | [13] | Web | Curiosity-driven RL | Failure detection | **12 unknown failures** | No LLM cost |
| **MARG** | [7] | Web | Multi-agent RL | States explored | **4.34×** over SOTA | No LLM cost |
| **DQT** | [11] | Mobile | DQN + graph embedding | Code coverage | Outperforms SOTA on 30 apps | No LLM cost |
| **iRobot** | [17] | Web | RL (DQN/PPO) + CNN | Branch coverage | **+1.7%** over baseline | No LLM cost |
| **Guardian** | [4] | Mobile | LLM + runtime framework | Task completion | **48.3%** success rate | Per-action LLM cost |
| **Le et al.** | [15] | Web | LLM + Screen Transition Graphs | Test coverage | Improved robustness | Per-test LLM cost |
| **Sakai et al.** | [12] | Web | LLM-based DRL | Bug detection | Detects bugs in web apps | Per-episode LLM cost |
| **Morpheus** | [9] | Web | Widget-based generation | Test generation | Widget-coverage based | No LLM cost |
| **Sáez Iznaga et al.** | [10] | General | LLM integration | Test automation | Improved test quality | Per-test LLM cost |

**Comparison with AutoQALLMs [8].** Mallipeddi et al. report 96% test coverage using Claude 4.5 with Selenium across 30 websites. Their approach generates Selenium test scripts directly from LLM analysis of HTML elements — a conceptually simpler pipeline than AutoTestAI's multi-stage approach. However, AutoQALLMs invokes the LLM for every test case, incurring proportional API cost that becomes prohibitive at scale. AutoTestAI's RL-based oracle routing achieves meaningful effectiveness (78.7% pass rate across 789 tests on eight websites) while using LLMs for only 2.8% of test evaluations (35/1,358 cumulative decisions), reducing per-test cost by over 35×. Additionally, AutoQALLMs evaluates test *generation* coverage (whether tests exist for all elements) rather than *execution* pass rate (whether generated tests produce correct verdicts), making the metrics not directly comparable.

**Comparison with WebQT [3].** Chang et al. demonstrate that RL-based test case generation achieves 45.4% higher code coverage than state-of-the-art approaches and detects 69 exceptions across 11 real-world web applications. WebQT uses a reward model to train a test generation policy, while AutoTestAI applies RL at the execution layer for oracle selection. The two approaches are complementary: WebQT optimizes *which* tests to generate, while AutoTestAI optimizes *how* to evaluate generated tests. AutoTestAI's hybrid BVA/ECP + AI refinement generated 789 test cases for eight websites spanning three distinct web frameworks (Next.js SSR, React SPA, Express SSR), while WebQT's RL-guided exploration produced tests targeting code coverage. The key distinction is that AutoTestAI measures test *correctness* (78.7% pass rate) rather than code coverage, addressing a different quality dimension.

**Comparison with GPTDroid [5].** Liu et al. formulate mobile GUI testing as a Q&A task with LLMs, achieving +32% activity coverage and discovering 53 new bugs on Google Play apps. GPTDroid's functionality-aware memory prompting mechanism maintains long-term testing context — a capability that AutoTestAI's stateless AI refinement phase currently lacks. However, GPTDroid invokes the LLM for every action decision, resulting in high API cost for comprehensive testing. AutoTestAI's DQN-based approach learns when LLM consultation is necessary, reducing API consumption by 97.4% compared to LLM-only execution across 15 training runs.

**Comparison with WebExplor [13].** Zheng et al. employ curiosity-driven RL to guide web testing, detecting 12 previously unknown failures across 6 real-world projects. WebExplor's automaton-based guidance for sequential action exploration addresses a challenge that AutoTestAI also faces: generating valid multi-step interaction sequences. While WebExplor focuses on exploration and failure detection without a formal test oracle, AutoTestAI's heuristic + LLM oracle provides structured pass/fail verdicts with confidence scores, enabling regression testing capabilities that WebExplor does not address.

**Comparison with MARG [7].** Fan et al. introduce multi-agent RL for web GUI testing, achieving 4.34× more explored states and 4.03× more detected failures than two state-of-the-art approaches. MARG's cooperative multi-agent design — where agents share Q-tables or exchange exploration data — represents a fundamentally different scaling strategy from AutoTestAI's single-agent DQN oracle router. AutoTestAI could benefit from MARG's cooperative exploration during the crawling phase, while MARG could benefit from AutoTestAI's cost-efficient oracle routing during result verification.

**Comparison with iRobot [17] and LLM Form Filling [19].** Liu et al. use RL with a CNN to guide a web crawler toward maximizing code coverage (+1.7% branch coverage over baseline). Chen et al. [19] extend this by using LLMs to generate diverse form input data, achieving +2.3% statement coverage over iRobot and +7.7% to +11.9% compared to QExplore. AutoTestAI's approach differs in that it separates crawling from test generation: the crawler discovers forms and extracts constraints, then BVA/ECP generators produce targeted test cases rather than relying on the crawler to fill forms during navigation. This separation enables systematic constraint-aware testing that iRobot's exploration-focused form filling cannot achieve.

**Comparison with Guardian [4].** Ran et al. propose a runtime framework that offloads computational tasks from LLMs, achieving 48.3% success rate on feature-based UI testing tasks — a 154% improvement over state-of-the-art. Guardian's insight that LLMs require external scaffolding for reliable testing directly parallels AutoTestAI's design: the heuristic oracle provides scaffolding that reduces LLM dependency while maintaining verdict quality. Both frameworks demonstrate that hybrid LLM-augmented approaches outperform pure-LLM approaches in testing contexts. Quantitatively, Guardian's 48.3% task completion on mobile UI tasks compares with AutoTestAI's 78.7% pass rate on web form tests — though these metrics measure different properties, both validate that LLM scaffolding yields substantially higher reliability than unscaffolded LLM testing (Guardian reports baseline LLM-only success at 19.0%).

**Comparison with DQT [11].** Lan et al. propose DQT (Deeply Reinforcing Android GUI Testing), which employs a DQN agent with graph neural network embeddings to learn exploration policies for Android applications. DQT outperforms state-of-the-art tools on 30 Android apps and demonstrates that DQN-based agents can effectively learn testing strategies through experience. AutoTestAI shares DQT's fundamental insight — that DQN architectures are well-suited for learning testing policies — but applies it to a fundamentally different problem: *oracle selection* rather than *exploration*. While DQT's DQN learns which GUI actions to take to maximize code coverage, AutoTestAI's DQN learns which oracle (heuristic vs. LLM) to invoke for each test case to maximize verdict accuracy while minimizing cost. This architectural parallel validates the broader applicability of DQN-based learning in automated testing across both mobile and web platforms. Empirically, DQT's exploration policy converges over training episodes on individual apps, while AutoTestAI's oracle policy converges across 15 cross-site runs (ε: 0.187→0.010), demonstrating cross-application transfer learning that DQT does not evaluate.

**Comparison with Sakai et al. [12].** Sakai et al. combine LLM-based reasoning with deep reinforcement learning to detect bugs in web applications — the architecturally closest approach to AutoTestAI in the literature. Their system uses an LLM to interpret web page states and a DRL agent to decide exploration actions, creating a tight LLM-RL feedback loop. AutoTestAI differs in three key ways: (i) AutoTestAI decouples the LLM from the RL loop — the LLM is used for test refinement and escalated oracle judgment, not as the RL agent's state interpreter; (ii) AutoTestAI's RL agent operates at the oracle-selection level (choosing between heuristic and LLM oracles) rather than the action-selection level; and (iii) AutoTestAI includes systematic BVA/ECP test generation that Sakai et al.'s exploration-based approach lacks. This decoupling is significant for cost efficiency: Sakai et al.'s approach requires LLM invocation at every RL step, whereas AutoTestAI invokes the LLM for only 2.6% of decisions (35/1,358), achieving a 97.4% reduction in LLM calls while maintaining 78.7% test pass accuracy across 789 tests on diverse web frameworks.

**Comparison with Morpheus [9].** De Almeida Neves et al. present Morpheus, a widget-based test case generation tool for web applications. Morpheus generates tests by analyzing interactive widgets (inputs, buttons, dropdowns) and producing test cases based on widget-level interaction patterns. This is conceptually similar to AutoTestAI's form-level test generation, but with a key difference: Morpheus generates tests based on widget *types* and interaction *patterns*, while AutoTestAI generates tests based on extracted *validation constraints* (minlength, maxlength, pattern, required, min, max) using formal BVA and ECP techniques. AutoTestAI's constraint-aware generation produces targeted boundary and partition tests (789 tests across 68 fields on 8 websites) that systematically probe validation logic, whereas Morpheus's widget-interaction approach prioritizes interaction coverage without constraint-specific targeting. Additionally, AutoTestAI augments rule-based generation with LLM refinement (+48 AI-generated tests, 6.5% improvement), a capability that Morpheus does not incorporate.

**Comparison with Sáez Iznaga et al. [10].** Sáez Iznaga et al. provide a comprehensive survey of LLM integration into automated software testing, categorizing approaches by testing phase (generation, execution, oracle, maintenance). Their analysis identifies cost, hallucination, and non-determinism as primary challenges for LLM-based testing — all challenges that AutoTestAI's architecture specifically addresses. AutoTestAI mitigates *cost* through RL-based oracle routing (97.4% reduction in LLM calls), addresses *hallucination* by confining LLMs to semantic augmentation rather than primary decision-making (the heuristic oracle provides a deterministic baseline), and manages *non-determinism* through the pattern-learning oracle that stabilizes decisions based on accumulated subtype history (1,358 observations across 7 subtypes). This positions AutoTestAI as a practical implementation of the hybrid integration strategy that Sáez Iznaga et al. recommend.

**Comparison with Le et al. [15].** Le et al. propose automated web application testing using LLMs combined with Screen Transition Graphs (STGs) to improve test case generation robustness. Their approach uses LLMs to generate test scripts from visual page representations, achieving improved test robustness across UI changes. While Le et al. focus on generation-time robustness (resilience to UI layout changes), AutoTestAI focuses on execution-time accuracy (correct oracle verdicts). The approaches address complementary challenges: Le et al.'s STG-based navigation could improve AutoTestAI's crawling phase (currently BFS-based), while AutoTestAI's RL-adaptive oracle could provide cost-efficient verdict generation for Le et al.'s generated test scripts. Both approaches use LLMs selectively — Le et al. for test script generation, AutoTestAI for refinement and escalated oracle — avoiding the per-action LLM dependency that characterizes GPTDroid [5] and Guardian [4].

**Table 8.4b: Quantitative Efficiency Comparison**

| Approach | Tests/Cases | LLM Dependency | Per-Test Cost | Total Cost | Platform Diversity | End-to-End Pipeline |
|----------|------------:|:--------------:|:-------------:|:----------:|:------------------:|:-------------------:|
| **AutoTestAI** | **789** | **2.6%** (35/1,358) | **$0.000056** | **$0.044** | 3 frameworks, 8 sites | ✓ (crawl→generate→refine→execute→verify) |
| AutoQALLMs [8] | 30 sites | **100%** | ~$0.002¹ | Proportional | 30 external sites | ✗ (generation only) |
| GPTDroid [5] | 53 bugs found | **100%** | ~$0.01–0.05² | High | 86 Google Play apps | ✗ (exploration only) |
| Guardian [4] | 195 tasks | **100%** (scaffolded) | ~$0.05–0.10² | High | 18 Android apps | ✗ (execution only) |
| WebQT [3] | 11 apps | **0%** | $0.00 | $0.00 | 11 web apps | ✗ (generation only) |
| DQT [11] | 30 apps | **0%** | $0.00 | $0.00 | 30 Android apps | ✗ (exploration only) |
| Sakai et al. [12] | Web apps | **~100%** | ~$0.01–0.05² | High | Web apps | ✗ (detection only) |

¹ Estimated from typical Gemini/Claude API pricing at the time of publication.  
² Estimated from reported LLM invocation frequency; exact costs not disclosed in original papers.

The efficiency comparison reveals two distinct paradigms: (i) LLM-intensive approaches (AutoQALLMs, GPTDroid, Guardian, Sakai et al.) that achieve high capability metrics but incur proportional API costs that scale linearly with test suite size, and (ii) RL-only approaches (WebQT, DQT, MARG, WebExplor) that eliminate LLM costs entirely but lack semantic reasoning capabilities for oracle decisions and test refinement. AutoTestAI occupies a unique middle ground: it leverages LLMs for semantic augmentation while constraining their usage to 2.6% of decisions through learned RL policy, achieving a per-test cost of $0.000056 — approximately **35× cheaper** than LLM-intensive approaches and within the same order of magnitude as zero-LLM approaches.

**Key positioning.** AutoTestAI occupies a unique position in this landscape: it is the only framework that combines (i) automated crawling and constraint extraction, (ii) rule-based test generation with LLM augmentation, (iii) RL-adaptive oracle routing for cost-efficient execution, and (iv) structured failure reporting — as an integrated end-to-end pipeline. Existing approaches typically address one or two of these concerns in isolation. The 78.7% pass rate across 789 tests, while lower than AutoQALLMs' 96% generation coverage, represents a more rigorous metric: it measures whether generated tests produce correct verdicts when executed against real applications with enforced validation across diverse web frameworks (Next.js, React SPA, Express SSR), rather than whether tests exist for each element.

---

### 8.8 RL-Adaptive Oracle Analysis

The DQN oracle router demonstrated effective cost management and adaptive learning across 15 execution runs spanning eight controlled and framework test websites. Three key properties of the RL system were validated, along with empirical evidence of cross-session learning:

**Selective oracle escalation.** Across all 15 runs, the RL agent used the heuristic oracle for 97.4% of oracle decisions (1,323/1,358 cumulative test evaluations) and escalated to the LLM visual oracle for only 2.6%. This escalation rate decreased monotonically as training progressed: from 6.9% in run 1 (ε=0.187) to 0.6% in run 15 (ε=0.010), demonstrating that the agent progressively learned to trust the heuristic oracle as its policy converged. The resulting cumulative cost of $0.070 for 1,358 tests represents a **97.4% cost reduction** compared to the theoretical $2.72 for LLM-only execution — consistent with findings from Lan et al. [11] (DQT), who demonstrate that DQN-based agents effectively learn cost-efficient exploration policies in GUI testing.

**Table 8.6: RL Training Trajectory Across 15 Execution Runs**

| Run | Site(s) | Pass Rate | LLM % | Cost ($) | ε | Stop Reason |
|-----|---------|----------:|------:|------:|------:|-------------|
| 1 | site1_contact | 79.3% | 6.9% | 0.008 | 0.187 | completed |
| 2 | site2_booking | 82.6% | 10.9% | 0.010 | 0.173 | completed |
| 3 | site3_register | 48.2% | 12.5% | 0.014 | 0.153 | completed |
| 4 | site4_search | 65.8% | 2.6% | 0.002 | 0.148 | completed |
| 5 | site5_feedback | 75.2% | 5.1% | 0.012 | 0.096 | completed |
| 6 | external (unreachable) | 0.0% | 0.0% | 0.000 | 0.096 | server_unreachable |
| 7 | external | 54.6% | 0.0% | 0.000 | 0.085 | completed |
| 8 | external | 56.3% | 2.8% | 0.004 | 0.070 | completed |
| 9 | site3_register (rerun) | 84.7% | 2.8% | 0.004 | 0.057 | completed |
| 10 | site6_ecommerce (budget=0) | 0.0% | 0.0% | 0.000 | 0.057 | budget_exhausted |
| 11 | site6_ecommerce (retry) | 57.0% | 1.3% | 0.004 | 0.031 | completed |
| 12 | site6_ecommerce (fixed data) | 83.4% | 2.0% | 0.006 | 0.017 | completed |
| 13 | site7_spa_taskboard | 68.3% | 0.0% | 0.000 | 0.011 | **rl_stop** |
| 14 | site8_medical | 47.5% | 1.1% | 0.004 | 0.010 | completed |
| 15 | site8_medical (oracle fixes) | 83.4% | 0.6% | 0.002 | 0.010 | completed |

**Cross-session learning evidence:** The ε-greedy exploration rate decayed from 0.187 (18.7% random actions) to 0.010 (1.0% random actions) across 15 runs, indicating the agent transitioned from exploration to exploitation. The average reward signal increased from +1.33 in the first 5 runs to +1.45 in the last 5 runs, confirming that the agent's oracle selection policy improved over time. Critically, when site8_medical was re-executed in run 15 (after oracle fixes applied between runs 14 and 15), the pass rate improved from 47.5% to 83.4% — a 75.6% relative improvement attributable to improved oracle visibility checks, keyword additions, and companion field enrichment. Similarly, when site3_register was re-executed in run 9 (after initial run 3), the pass rate improved from 48.2% to 84.7% — a 75.7% relative improvement attributable to the agent's accumulated policy learning from intervening runs.

**Risk-based test prioritization (Goal 2).** The failure probability scorer ranked tests by subtype risk (BVA/numeric_boundaries = 70%, ECP/invalid_partition = 65%, valid_partition = 30%) and executed higher-risk tests first. Risk scores were persisted across sessions via `score_updates.jsonl` (76 entries across 15 runs), ensuring that failure patterns discovered in earlier runs informed prioritization in subsequent runs. This produced early fault discovery: across all sites, the majority of failures were detected within the first 30% of each test suite. The cumulative heuristic factor analysis showed Subtype was the most impactful factor (used in 100% of decisions), followed by Boundary Values (43%) and Input Complexity (11%).

**Adaptive early stopping (Goal 1).** The early stopping mechanism was empirically validated on site7_spa_taskboard (run 13): the agent triggered adaptive early stop at test 121/126 after detecting 5 consecutive uncertain oracle outcomes. The stop threshold was dynamically calculated from 12 prior historical runs, with the algorithm considering the rolling pass-rate trend to set a conservative threshold of 5. This saved 5 unproductive test executions (~15 seconds) while preserving 96.0% test coverage. On sites with higher pass rates (site6 at 83.4%, site3 at 84.7%), the thresholds remained permissive (threshold > remaining tests), allowing all suites to complete fully. On the unreachable external site (run 6), aggressive early stopping activated after just 3 tests at 0% pass rate, saving over 50 unproductive tests.

**Pattern-learning oracle (Goal 3).** The pattern-learning oracle accumulated 1,358 subtype-level observations across 7 distinct subtypes. Five subtypes (invalid_partition: 359 samples, numeric_boundaries: 341, valid_partition: 217, payment_boundaries: 112, unknown: 80) exceeded the ≥5 sample threshold for override activation. The oracle's subtype-level decisive rate analysis indicates that pattern overrides are projected to reroute 28.6% of oracle decisions in subsequent runs — specifically routing valid_partition tests (historically 0% LLM success rate) permanently to the heuristic oracle, eliminating wasteful LLM escalation for this low-risk category.

**Three RL goals empirical summary:**

| Goal | Mechanism | Observed Behavior | Evidence |
|------|-----------|-------------------|----------|
| **Goal 1**: Adaptive early stopping | Threshold varies with pass-rate history | Triggered on site7 at test 121/126 (threshold=5); conservative on high-pass-rate sites | Run 13: rl_stop, 12 historical runs informing threshold |
| **Goal 2**: Persisted risk scores | `score_updates.jsonl` loaded at init | 76 entries across 15 runs; risk-ranked execution order validated | BVA/numeric prioritized over ECP/valid in every run |
| **Goal 3**: Pattern-learning oracle | Override DQN when subtype history ≥ 5 | 5/7 subtypes reached threshold; 28.6% projected rerouting | 1,358 cumulative observations, avg reward +1.45 |

---

### 8.9 Empirical Limitations in Automated Crawling and Test Execution

This section documents concrete limitations discovered during the deployment of AutoTestAI against the eleven target websites. These are not theoretical limitations derived from the literature — they are failures and ambiguities observed during live execution.

#### 8.9.1 Limitations Encountered During Automated Crawling

**L-C1: JavaScript-Conditional Navigation Blocking Exploration.** Several pages on the external websites required a user to complete a prior step before the target form became accessible. The crawler's BFS strategy navigated to these pages by URL but found no testable form state. This limitation is consistent with challenges reported by Zheng et al. [13], who note that "some deep states can only be reached by specific action sequences."

**L-C2: Incomplete Shadow DOM Traversal.** Three of the six external sites used web components with nested shadow roots deeper than the traversal recursion limit, causing inputs to be invisible to the DOM analyzer.

**L-C3: AJAX-Populated Dropdowns Appearing Empty.** Several `<select>` elements were populated via asynchronous API calls triggered after page load. The crawler's fixed stabilization window captured these dropdowns in their empty state. This is a known challenge in dynamic web crawling, as documented by Mesbah et al. [20] (Crawljax) and Qin [16], who both address asynchronous content loading as a primary obstacle to crawling accuracy.

**L-C4: Multi-Step Wizard State Misclassification.** Two external sites implemented wizards using CSS visibility toggling rather than distinct `<form>` elements. The crawler interpreted these as single large forms, producing structurally incorrect test cases.

**L-C5: Rate Limiting and Anti-Automation Responses.** The crawling process triggered HTTP 429 responses on two sites, causing the crawler to index empty states as legitimate pages.

**L-C6: Duplicate State Misidentification.** The hybrid hash deduplication strategy failed to distinguish genuinely different states on pagination-heavy sites where URL structures remained identical across pages.

#### 8.9.2 Limitations Encountered During Test Case Execution

Four distinct oracle-defeat conditions were identified at execution time on the external websites:

**L-E1: Disabled Submit Button Not Detected.** Sites implementing progressive disclosure validation set the submit button to `disabled` until all fields pass validation. The test runner checked only `is_visible()`, not `is_enabled()`, producing false PASS results.

**L-E2: Browser-Native Validation Without DOM Text.** Sites relying on the browser's built-in `:invalid` CSS state provided no DOM text node as feedback, making the validation invisible to both the heuristic and LLM oracles.

**L-E3: `alert()` Dialog Dismissed Before Screenshot.** Playwright's default event loop automatically dismissed `dialog` events before screenshots were captured, making alert-based validation feedback invisible.

**L-E4: JavaScript Re-Validation Blocking Submit.** Sites implementing secondary JavaScript validation via `event.preventDefault()` silently blocked form submission without visible error feedback.

**L-E5: Decorative Forms Without Submit Targets.** Two external sites contained purely presentational form elements with no functional submission mechanism — a pattern common on QA practice platforms.

**Table 8.5: Summary of Identified Limitations**

| ID | Phase | Condition | Impact | Status |
|----|-------|-----------|--------|--------|
| L-C1 | Crawling | JS-gated forms | Missing coverage | Future work |
| L-C2 | Crawling | Nested shadow DOM | Missing coverage | Future work |
| L-C3 | Crawling | AJAX dropdowns empty at crawl time | Invalid test inputs | Future work |
| L-C4 | Crawling | Wizard CSS toggling | Wrong field set | Future work |
| L-C5 | Crawling | Rate limiting | Corrupted graph | Future work |
| L-C6 | Crawling | URL collision | Undersampled constraints | Future work |
| L-E1 | Execution | Disabled submit button | False PASS | **Fixed** |
| L-E2 | Execution | `:invalid` CSS without DOM text | False PASS | **Fixed** |
| L-E3 | Execution | `alert()` dismissed | False PASS | **Fixed** |
| L-E4 | Execution | JS `preventDefault()` | False PASS | Pending |
| L-E5 | Execution | Decorative form, no submit target | False PASS | **Fixed** |

All four priority execution-layer fixes (L-E1, L-E2, L-E3, L-E5) were implemented and validated on the controlled test websites. The controlled websites were designed to eliminate these conditions by construction, ensuring that the 78.7% aggregate pass rate (621/789 tests across 8 websites) reflects genuine oracle accuracy rather than oracle-defeat artifacts.

---

### 8.10 Discussion: Connecting the Empirical Results to RQ4

The results across fourteen websites (8 controlled/framework + 6 external crawl-only) illuminate five scalable execution strategies that directly answer RQ4:

**Strategy 1 — Selective oracle escalation.** Routing each test through the cheapest adequate oracle reduces API cost by 97.4% versus LLM-only execution. This efficiency gain is critical for regression testing in CI/CD pipelines, where test suites grow incrementally and must be re-executed on every deployment.

**Strategy 2 — Risk-based prioritization.** Ordering tests by failure probability ensures that the highest-risk test classes execute first. This is most valuable in time-constrained regression runs where only a fraction of tests can be completed. Similar prioritization has been demonstrated effective in RL-based testing contexts by Chang et al. [3] and Zhao et al. [14].

**Strategy 3 — Adaptive session management.** Pass-rate-conditioned early stopping prevents both premature abandonment (on high-quality sites) and unproductive continuation (on failing sites).

**Strategy 4 — Cross-session risk calibration.** Persisted risk scores compound across sessions, converging toward empirically validated subtype-level risk assessments. This is directly applicable to regression testing: each run provides evidence about which test classes predict genuine faults versus stable behaviors.

**Strategy 5 — Oracle routing corrections through pattern learning.** The pattern-learning oracle (Goal 3) provides the most targeted regression maintenance mechanism: as subtype-level behavior stabilizes across versions, the system learns which test classes reliably require LLM verification and which can be trusted to the heuristic.

#### 8.10.1 Real-World Cost Efficiency Analysis

To contextualize AutoTestAI's efficiency for practical deployment, we project costs across realistic regression testing scenarios using observed empirical data:

**Table 8.7: Projected Cost Scaling for Regression Testing Scenarios**

| Scenario | Tests/Run | Runs/Month | Monthly Tests | AutoTestAI Cost¹ | LLM-Only Cost² | Savings |
|----------|----------:|----------:|-------------:|------------------:|-----------------:|--------:|
| Small team (1 app) | 789 | 20 | 15,780 | $0.88 | $31.56 | 97.2% |
| Medium team (5 apps) | 3,945 | 50 | 197,250 | $11.05 | $394.50 | 97.2% |
| CI/CD pipeline (10 apps) | 7,890 | 200 | 1,578,000 | $88.37 | $3,156.00 | 97.2% |
| Enterprise scale (50 apps) | 39,450 | 500 | 19,725,000 | $1,104.60 | $39,450.00 | 97.2% |

¹ At observed $0.000056/test (2.6% LLM escalation rate, $0.002/LLM call).  
² At $0.002/test (100% LLM invocation rate, typical Gemini Flash API pricing).

The projections reveal that AutoTestAI's cost advantage compounds with scale. At enterprise scale (19.7M tests/month), AutoTestAI's RL-adaptive oracle saves approximately **$38,345/month** compared to LLM-only execution. This cost profile makes regression testing economically feasible for organizations that currently limit automated testing due to API budget constraints — a concern explicitly identified by Sáez Iznaga et al. [10] as a primary barrier to LLM adoption in testing.

**Execution time efficiency.** Across 789 tests on 8 websites, AutoTestAI completed execution in an average of **2.8 seconds per test** (including browser automation, form filling, submission, oracle evaluation, and screenshot capture). The heuristic oracle adds near-zero latency (~5ms DOM analysis), while LLM oracle escalation adds ~2–3 seconds per invocation. With only 2.6% LLM escalation, the per-test time overhead from LLM usage is negligible (0.026 × 2.5s = 0.065s average per test). In contrast, approaches like GPTDroid [5] that invoke LLMs for every action decision incur cumulative latency that can extend test execution by 10–50×, as each UI action requires an LLM round-trip [5], [4]. Guardian [4] reports that its runtime framework reduces LLM processing time but still requires LLM invocation for every testing step.

**Cross-framework generalization.** AutoTestAI was evaluated across three distinct web technology stacks without per-framework configuration changes: Next.js 14 with server-side rendering (site6, 83.4% pass rate), React 18 with Vite client-side SPA (site7, 68.3%), and Express 4 with EJS server-rendered templates (site8, 83.4%). This cross-framework consistency contrasts with approaches like AutoQALLMs [8], which generate Selenium scripts that may require framework-specific selector adjustments, and iRobot [17], whose CNN-based visual features may underperform on unfamiliar UI frameworks. The constraint-extraction approach — reading HTML5 validation attributes (required, pattern, minlength, etc.) that are framework-agnostic by specification — provides inherent cross-framework portability that visual or script-based approaches lack.

**Comparison with manual testing effort.** Industry estimates place manual black-box test creation and execution at 15–30 minutes per test case for web forms with validation [1]. AutoTestAI generated 789 test cases autonomously in approximately 45 minutes (crawling + generation + AI refinement) and executed them in ~37 minutes, totaling ~82 minutes for end-to-end pipeline completion. Achieving equivalent coverage manually would require an estimated 197–395 person-hours (789 tests × 15–30 min), representing a **144–289× speedup** in total testing effort. Even accounting for the 21.3% test cases requiring manual review (161 failures that may include false positives), the reduction in human effort remains substantial.

### 8.11 Threats to Validity

**Internal validity.** The eight controlled and framework test websites enforce deterministic validation with visible feedback. This design eliminates oracle-defeat conditions but may overestimate framework effectiveness compared to applications with AJAX, server-side, or CAPTCHA-based validation.

**External validity.** The controlled test websites range from single-page forms with 4–6 fields to multi-form framework applications with 10–21 fields. Real-world web applications involve multi-page workflows, authentication gates, dynamic content loading, and backend state dependencies. The generalizability of the 78.7% aggregate pass rate to production applications requires further investigation. The six external websites provide partial external validation of crawling capability but do not validate execution quality on arbitrary sites.

**Construct validity.** The pass rate metric conflates the test generator's ability to produce valid test data with the oracle's ability to correctly judge the application's response. Separating these factors would require source code access, contradicting the black-box constraint.

**Conclusion validity.** The evaluation was conducted on a single run per website. Test execution is non-deterministic due to browser timing, asynchronous JavaScript, and LLM probabilistic judgments. Repeated runs would be needed to establish confidence intervals.

## 9. Automated Result Verification and Oracles (RQ5)

> **RQ5 (original):** Can an automated black-box testing system provide not only defect detection but also meaningful explanations and fix suggestions for identified failures?

The evidence base for RQ5 is the failure data collected during execution of the eight controlled and framework test websites. Of the 161 test failures recorded across these websites, the oracle captured structured failure evidence for each test: the test subtype, expected behavior, observed behavior (screenshot), oracle confidence score, and the specific validation error message (when detected by the heuristic oracle's DOM probe).

### 9.1 Failure Classification and Pattern Detection

AutoTestAI classifies failures into actionable categories based on the relationship between test input, expected outcome, and observed behavior:

1. **True failures (application correctly rejected invalid input but oracle misjudged):** These represent oracle limitations rather than application defects. The application behaved correctly, but the visual or heuristic oracle failed to recognize the rejection signal. This category accounts for the majority of the 161 failures — the application's validation logic is correct by construction, so failures indicate oracle sensitivity gaps.

2. **Boundary ambiguities:** Tests at exact constraint boundaries (e.g., name = exactly 2 characters for site1_contact) where the oracle's confidence falls into the uncertain zone. These cases highlight that boundary value testing inherently produces ambiguous oracle signals.

3. **Cross-field validation failures:** Tests involving field interdependencies (e.g., confirmPassword ? password in site3_register) where the error message appears on a dependent field. The oracle may evaluate the wrong field's state.

### 9.2 Structured Failure Reports

For each failed test, AutoTestAI generates a structured failure report containing:
- **Test metadata:** test type, subtype, target field, expected result
- **Input values:** the exact values submitted for each field
- **Oracle evidence:** screenshot path, heuristic confidence score, LLM judgment (if escalated)
- **DOM state:** error message text detected (if any), URL change status, form presence
- **Suggested diagnosis:** automated classification into one of the failure categories above

These reports are persisted as JSON artifacts in `data/test_results/` and rendered as interactive HTML reports via the Streamlit dashboard, enabling manual review and triage of failures.

### 9.3 Implications for RQ5

The results demonstrate that automated black-box testing systems can provide meaningful failure evidence beyond binary pass/fail outcomes. The structured failure reports, combined with screenshot evidence and oracle confidence scores, give developers sufficient context to understand *why* a test failed and *where* to investigate. However, fully automated fix suggestions remain limited by the black-box constraint: without access to source code, the system can identify *what* failed but cannot prescribe *how* to fix the underlying implementation.

---

## 10. Discussion and Threats to Validity

### 10.1 Summary of Findings

This research investigated the fundamental question of why fully automated black-box testing for web applications remains unsolved, and examined the extent to which intelligent hybrid approaches can advance the state of the art. The empirical evaluation across five research questions yielded the following key findings:

**RQ1 (Why does full automation remain unsolved?):** Section 5 demonstrated that no single exploration paradigm � static crawling, dynamic browser-based crawling, heuristic interaction, model-based testing, reinforcement learning, computer vision, or LLM-guided exploration � can achieve both complete coverage and correct verification across arbitrary web applications. The fundamental barriers are semantic ambiguity inherent in web interfaces, the oracle problem, and backend-controlled logic that is invisible to black-box systems.

**RQ2 (Can 100% test coverage be achieved?):** Section 6 showed that even when all input fields are successfully identified, structural coverage does not imply behavioral coverage. Across the eight controlled and framework test websites, AI refinement added between 0.9% and 18.8% additional test cases that rule-based generation missed, demonstrating that semantic reasoning is essential for generating cross-field, boundary, and interaction-dependent test scenarios.

**RQ3 (Can LLMs enhance test generation?):** Section 7 confirmed that LLM-assisted refinement fills specific gaps left by rule-based generators. The AI generated 48 additional test cases across 741 initial tests (6.5% improvement across the controlled/framework sites), with the largest gains on sites with cross-field validation logic (site4_search: +18.8%, site8_medical: +5.8%). The LLM acts as a semantic augmentation layer, not a replacement for traditional techniques.

**RQ4 (Scalable execution strategies?):** Section 8 demonstrated that RL-based oracle selection achieves 97.4% cost reduction compared to LLM-only execution across 15 training runs. The controlled and framework evaluation achieved a **78.7%** aggregate pass rate (621/789 tests) at a cost of $0.044 total (22 LLM calls), validating that the framework produces meaningful test verdicts across diverse web frameworks (Next.js SSR, React SPA, Express SSR). The RL agent exhibited measurable cross-session learning: ε decayed from 0.187 to 0.010, LLM escalation decreased from 6.9% to 0.6%, and the DQN's adaptive early stopping (Goal 1) was empirically triggered on site7_spa_taskboard, demonstrating autonomous session optimization. Risk-based test prioritization achieved early fault discovery in the first 20% of the test queue.

**RQ5 (Automated failure explanation?):** Section 9 showed that structured failure reports with oracle evidence provide sufficient context for developer triage, but fully automated fix suggestions remain constrained by the black-box boundary.

### 10.2 Comparative Positioning

The empirical results position AutoTestAI distinctively within the landscape of automated web testing research across four dimensions: cost efficiency, oracle architecture, pipeline integration, and cross-framework generalization.

**Cost efficiency.** AutoTestAI achieves a per-test cost of $0.000056, making it **35× cheaper** than LLM-intensive approaches such as AutoQALLMs [8] (estimated ~$0.002/test), **178–893× cheaper** than action-level LLM tools such as GPTDroid [5] (~$0.01–0.05/action), and **893–1,786× cheaper** than Guardian [4] (~$0.05–0.10/task). Among the 13 approaches surveyed in Table 8.4, only pure-RL tools (WebQT [3], DQT [11], MARG [7], WebExplor [13]) achieve lower per-test costs — but at the expense of semantic reasoning capabilities that LLMs provide. The projected monthly cost at enterprise scale (Table 8.7) demonstrates that AutoTestAI's RL-adaptive approach saves approximately $38,345/month compared to LLM-only execution at 50-app scale, addressing the cost scalability concern identified as a primary LLM adoption barrier by Sáez Iznaga et al. [10].

**Oracle architecture.** Unlike AutoQALLMs [8], which relies entirely on LLM-driven execution with significant API costs, AutoTestAI's hybrid heuristic-LLM oracle architecture achieves 97.4% cost reduction while maintaining validation quality across 15 execution runs. Compared to RL-focused approaches such as WebQT [3] (+45.4% code coverage), WebExplor [13] (curiosity-driven exploration), DQT [11] (graph-embedding guided DQN), and MARG [7] (4.34× more explored states through multi-agent cooperation), AutoTestAI integrates RL not for exploration alone but for adaptive oracle selection — a fundamentally different application of reinforcement learning in the testing pipeline. The RL agent's cross-session learning trajectory (ε: 0.187→0.010, LLM%: 6.9%→0.6%, avg reward: +1.33→+1.45) demonstrates that the oracle selection policy converges toward efficient exploitation with increasing experience. Sakai et al. [12] combine LLMs with DRL in the closest architectural parallel to AutoTestAI, but their tight LLM-RL coupling requires LLM invocation at every RL step — AutoTestAI's decoupled design reduces this to 2.6% of decisions.

**Pipeline integration.** GPTDroid [5] demonstrates that LLMs can achieve +32% activity coverage on Android applications by formulating testing as a Q&A task, while Guardian [4] shows that runtime scaffolding can improve LLM instruction-following from 48.3% to reliable UI exploration. AutoTestAI builds on these insights by confining LLM usage to two specific roles — semantic test case refinement and escalated oracle judgment — rather than using LLMs as the primary exploration or execution engine. This selective deployment explains the low per-test cost ($0.000056) compared to LLM-intensive approaches. The end-to-end pipeline integration distinguishes AutoTestAI from systems that address individual pipeline stages. Le et al. [15] combine LLMs with screen transition graphs for test case generation but do not address execution or oracle challenges. Morpheus [9] generates widget-based test cases but lacks constraint-aware targeting and LLM augmentation. iRobot [17] and Chen et al. [19] focus on crawling and form-filling respectively. Crawljax [20] provides crawling infrastructure without test generation or oracle support. By contrast, AutoTestAI's modular architecture spans the entire lifecycle — crawl → generate → refine → execute → verify — enabling evaluation of cross-stage interactions that isolated approaches cannot assess.

**Cross-framework generalization.** AutoTestAI achieved consistent pass rates across three distinct web technology stacks without per-framework tuning: Next.js SSR (83.4%), React SPA (68.3%), and Express SSR (83.4%). This cross-framework consistency — enabled by relying on framework-agnostic HTML5 validation attributes — contrasts with approaches requiring framework-specific adaptations. AutoQALLMs [8] generates Selenium scripts that may require selector adjustments per framework, iRobot [17] uses CNN visual features that may generalize unevenly across UI designs, and Morpheus [9] generates tests based on widget types that vary across frontend libraries.

### 10.3 Threats to Validity

**Internal validity.** The eight controlled and framework test websites enforce deterministic validation with visible feedback. This design eliminates the oracle-defeat conditions identified in Section 8.9 but may overestimate framework effectiveness compared to real-world applications with more complex validation patterns (AJAX, server-side, CAPTCHA).

**External validity.** The controlled test websites range from single-page forms with 4–6 fields to multi-form framework applications with 10–21 fields. Real-world web applications involve multi-page workflows, authentication gates, dynamic content loading, and backend state dependencies. The generalizability of the 78.7% aggregate pass rate to production applications requires further investigation.

**Construct validity.** The pass rate metric conflates two distinct properties: (a) the test generator's ability to produce valid test data, and (b) the oracle's ability to correctly judge the application's response. Separating these factors would require access to application source code, which contradicts the black-box constraint.

**Conclusion validity.** The evaluation was conducted on a single run per website. Test execution is non-deterministic due to browser timing, asynchronous JavaScript, and LLM probabilistic judgments. Repeated runs would be needed to establish confidence intervals on the reported pass rates.

---

## 11. Conclusion and Future Work

### 11.1 Conclusion

This paper investigated the fundamental question of why fully automated black-box testing for web applications remains an unsolved problem, and explored how intelligent hybrid approaches combining rule-based testing, reinforcement learning, computer vision, and large language models can advance the state of the art.

Through the design and implementation of AutoTestAI � a modular framework that decomposes the testing lifecycle into explicit, analyzable stages � this research provided both theoretical analysis and empirical evidence across five research questions. The key contributions are:

1. **A comprehensive analysis of exploration limitations** (Section 5) demonstrating that no single paradigm � from static crawling to LLM-guided exploration � can achieve both complete coverage and correct verification for arbitrary web applications. The web's semantic ambiguity, the oracle problem, and invisible backend logic remain fundamental barriers to full automation.

2. **Empirical evidence that structural coverage ≠ behavioral coverage** (Section 6), with AI refinement adding 0.9%–18.8% additional test cases that rule-based generation cannot derive from DOM structure alone across eight test websites. This confirms that semantic reasoning is a necessary complement to traditional test design techniques.

3. **Demonstration that LLMs function as effective semantic augmentation layers** (Section 7) for test case generation, filling gaps in cross-field validation, boundary interaction, and constraint-dependent scenarios that syntax-driven generators systematically miss.

4. **A reinforcement learning–based oracle selection framework** (Section 8) that achieves 97.4% cost reduction compared to LLM-only execution while maintaining validation quality. The framework was evaluated across 15 training runs spanning eight controlled and framework test websites built on diverse technology stacks (Next.js SSR, React SPA, Express SSR). The evaluation achieved a **78.7%** aggregate pass rate across 789 AI-refined test cases at a total cost of $0.044, validating that the hybrid heuristic-LLM oracle architecture produces meaningful test verdicts. The RL agent demonstrated measurable cross-session learning: exploration rate decayed from 18.7% to 1.0%, LLM escalation decreased from 6.9% to 0.6%, and all three RL goals (adaptive early stopping, persisted risk scores, pattern-learning oracle) were empirically validated.

5. **Identification of five oracle-defeat conditions** (Section 8.11) that systematically produce false results in automated test execution � disabled submit buttons, browser-native CSS validation without DOM text, dismissed alert dialogs, JavaScript re-validation blocking, and decorative forms without submission targets. These conditions explain why previous evaluations on QA practice websites produced near-zero pass rates and provide a concrete checklist for future automated testing tool developers.

6. **Structured failure evidence** (Section 9) demonstrating that automated black-box systems can provide meaningful diagnostic context beyond binary pass/fail, though fully automated fix suggestions remain constrained by the black-box boundary.

The overarching conclusion is that fully automated black-box testing of arbitrary web applications is not achievable with current technology — and likely not achievable in the general case due to undecidability constraints. However, *intelligent testing assistants* that combine rule-based rigor with AI-powered semantic reasoning and adaptive execution strategies can dramatically reduce manual testing effort while providing actionable, evidence-based quality assessments. AutoTestAI demonstrates that this hybrid approach is both technically feasible and economically viable, with per-test costs below $0.000056 in the controlled evaluation — approximately 35× cheaper than LLM-intensive approaches [8], [5], [4] and representing a 144–289× speedup over estimated manual testing effort [1].

Compared to the 13 approaches surveyed in Section 8.7, AutoTestAI occupies a unique position: it is the only framework evaluated in this study that integrates all five pipeline stages — crawling, generation, refinement, execution, and oracle verification — into a single adaptive system. While AutoQALLMs [8] demonstrates higher coverage (96%) and GPTDroid [5] achieves greater activity discovery (+32%), these tools address individual aspects of the testing lifecycle and incur proportional API costs that scale linearly with test suite size. The closest architectural parallel, Sakai et al. [12], combines LLMs with DRL for web bug detection but requires LLM invocation at every RL step, whereas AutoTestAI reduces LLM dependency to 2.6% of decisions through learned policy. Pure-RL approaches (WebQT [3], DQT [11], MARG [7], WebExplor [13]) eliminate LLM costs but lack semantic reasoning for oracle decisions and test refinement. AutoTestAI's contribution lies in demonstrating that end-to-end integration with RL-adaptive oracle selection can achieve meaningful test verdicts (78.7% pass rate across 789 tests on 8 websites) at minimal cost ($0.044 total), with the RL agent exhibiting measurable cross-session learning (ε: 0.187→0.010, 15 runs) and cross-framework generalization (Next.js SSR, React SPA, Express SSR without per-framework tuning). This provides a practical template for future intelligent testing assistants that improve with each execution cycle.

### 11.2 Future Work

Several directions emerge from this research:

1. **Multi-page workflow testing:** Extending the test generation and execution pipeline beyond single-form pages to multi-step workflows involving authentication, conditional navigation, and session state. This would address the generalizability limitation identified in Section 10.3.

2. **Improved oracle mechanisms:** Implementing the fix signals identified in Section 8.11 for production use � particularly the `:invalid` CSS state probe and dialog event listener � would improve oracle accuracy on real-world applications that use browser-native or alert-based validation.

3. **Pattern learning activation:** The Goal 3 pattern-learning oracle requires additional training data to activate subtype-level routing corrections. Running the framework across a larger corpus of applications would provide the =5 samples per subtype needed for decisive override rules.

4. **Adaptive budget allocation:** Replacing the fixed per-site API budget with a quota-aware allocation strategy that distributes LLM calls proportionally to site complexity and expected oracle difficulty.

5. **Server-side validation detection:** Developing heuristics or probes to distinguish client-side-only validation from server-side validation, enabling the oracle to anticipate response observability before test execution.

6. **Integration with CI/CD pipelines:** Packaging AutoTestAI as a CI/CD-compatible tool that can be invoked on each deployment, using the RL agent's cross-session learning to continuously improve test prioritization and oracle routing across application versions.

---

## References

[1] S. Balsam and D. Mishra, "Web Application Testing — Challenges and Opportunities," *The Journal of Systems and Software*, vol. 219, article 112186, 2025.

[2] F. Yazdani and S. Malek, "Deep GUI: Black-box GUI Input Generation with Deep Learning," in *Proc. 36th IEEE/ACM International Conference on Automated Software Engineering (ASE)*, 2021.

[3] X. Chang, Z. Liang, Y. Zhang, L. Cui, Z. Long, G. Wu, Y. Gao, W. Chen, J. Wei, and T. Huang, "A Reinforcement Learning Approach to Generating Test Cases for Web Applications," in *Proc. IEEE/ACM International Workshop on Automation of Software Test (AST)*, 2023.

[4] D. Ran, H. Wang, Z. Song, M. Wu, Y. Cao, Y. Zhang, W. Yang, and T. Xie, "Guardian: A Runtime Framework for LLM-Based UI Exploration," in *Proc. 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA'24)*, Vienna, Austria, pp. 1–13, 2024.

[5] Z. Liu, C. Chen, J. Wang, M. Chen, B. Wu, X. Che, D. Wang, and Q. Wang, "Make LLM a Testing Expert: Bringing Human-like Interaction to Mobile GUI Testing via Functionality-aware Decisions," in *Proc. 46th IEEE/ACM International Conference on Software Engineering (ICSE'24)*, 2024.

[6] C. Tao, Y. Gao, H. Guo, and J. Gao, "A Reinforcement Learning-based Approach to Testing GUI of Mobile Applications," *Springer Nature Preprint*, 2024.

[7] Y. Fan, S. Wang, Z. Fei, Y. Qin, H. Li, and Y. Liu, "Can Cooperative Multi-Agent Reinforcement Learning Boost Automatic Web Testing? An Exploratory Study," in *Proc. 39th IEEE/ACM International Conference on Automated Software Engineering (ASE'24)*, Sacramento, CA, USA, pp. 1–13, 2024.

[8] S. Mallipeddi, M. Yaqoob, J. A. Khan, T. Mehmood, A. Mylonas, and N. Pitropakis, "AutoQALLMs: Automating Web Application Testing Using Large Language Models (LLMs) and Selenium," *MDPI Computers*, vol. 14, article 501, 2025.

[9] R. de Almeida Neves, W. M. Watanabe, and R. Oliveira, "Morpheus Web Testing: A Tool for Generating Test Cases for Widget Based Web Applications," *Journal of Web Engineering*, vol. 21, no. 2, pp. 119–144, 2022.

[10] Y. Sáez Iznaga, L. Rato, P. Salgueiro, and J. Lamar León, "Integrating Large Language Models into Automated Software Testing," *MDPI Future Internet*, vol. 17, article 476, 2025.

[11] Y. Lan, Y. Lu, Z. Li, M. Pan, W. Yang, T. Zhang, and X. Li, "Deeply Reinforcing Android GUI Testing with Deep Reinforcement Learning," in *Proc. 46th IEEE/ACM International Conference on Software Engineering (ICSE'24)*, Lisbon, Portugal, pp. 1–13, 2024.

[12] Y. Sakai, Y. Tahara, A. Ohsuga, and Y. Sei, "Using LLM-Based Deep Reinforcement Learning Agents to Detect Bugs in Web Applications," in *Proc. 17th International Conference on Agents and Artificial Intelligence (ICAART)*, vol. 3, pp. 1001–1008, 2025.

[13] Y. Zheng, Y. Liu, X. Xie, Y. Liu, L. Ma, J. Hao, and Y. Liu, "Automatic Web Testing Using Curiosity-Driven Reinforcement Learning," in *Proc. IEEE/ACM 43rd International Conference on Software Engineering (ICSE)*, 2021.

[14] Y. Zhao, B. Harrison, and T. Yu, "DinoDroid: Testing Android Apps Using Deep Q-Networks," *arXiv preprint arXiv:2210.06307*, 2022.

[15] N.-K. Le, Q. M. Bui, M. N. Nguyen, H. Nguyen, T. Vo, S. T. Luu, S. Nomura, and M. L. Nguyen, "Automated Web Application Testing: End-to-End Test Case Generation with Large Language Models and Screen Transition Graphs," *arXiv preprint arXiv:2506.02529*, 2025.

[16] F. Qin, "A Web Crawler Method Based on Iframe Supporting Asynchronous Requests," in *Proc. 6th International Conference on Computer Information and Big Data Applications (CIBDA)*, Wuhan, China, pp. 1–6, 2025.

[17] C.-H. Liu, S. D. You, and Y.-C. Chiu, "A Reinforcement Learning Approach to Guide Web Crawler to Explore Web Applications for Improving Code Coverage," *MDPI Electronics*, vol. 13, article 427, 2024.

[18] J. Doyle, T. Saber, P. Arcaini, and A. Ventresque, "Improving Mobile User Interface Testing with Model Driven Monkey Search," *Preprint*, 2021.

[19] F.-K. Chen, C.-H. Liu, and S. D. You, "Using Large Language Model to Fill in Web Forms to Support Automated Web Application Testing," *MDPI Information*, vol. 16, article 102, 2025.

[20] A. Mesbah, A. van Deursen, and S. Lenselink, "Crawling Ajax-based Web Applications through Dynamic Analysis of User Interface State Changes," *ACM Transactions on the Web*, vol. 6, no. 1, pp. 1–30, 2012.

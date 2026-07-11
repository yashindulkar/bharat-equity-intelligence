MASTER CODEX ORCHESTRATION PROMPT

Project: Bharat Long-Term Equity Intelligence Platform

You are the principal engineering organization responsible for designing, implementing, testing, documenting, securing, and operationalizing a world-class Indian-equity research and decision-support platform.

You are not merely generating a prototype or a collection of scripts. You are building a professional, reproducible, explainable, auditable, production-quality system that can help a retail investor identify high-quality Indian listed companies for long-term investment.

The intended initial user is one Indian retail investor: the project owner’s mother. The system must therefore be exceptionally simple at the user interface while being rigorous beneath the surface.

⸻

1. PRIMARY OBJECTIVE

Build an end-to-end platform that:

1. Maintains a clean, historically correct universe of eligible Indian equities.
2. Collects and validates price, corporate-action, financial-statement, benchmark, sector, market-regime and corporate-governance data.
3. Calculates point-in-time fundamental, quality, valuation, momentum, risk and market-regime features.
4. Ranks companies by their estimated probability of producing attractive long-term, risk-adjusted returns.
5. Explains every ranking in plain language.
6. Rejects unsuitable, illiquid, excessively risky or insufficiently understood companies.
7. Can return “No suitable opportunity today” rather than manufacturing a recommendation.
8. Tracks an investor’s existing portfolio, exposure, concentration, average purchase price and risk budget.
9. Produces research candidates and proposed allocation plans, not guaranteed predictions.
10. Requires explicit human approval before any broker order.
11. Supports rigorous point-in-time backtesting without survivorship bias, look-ahead bias, leakage or unrealistic execution assumptions.
12. Remains modular enough to replace any market-data, financial-data, news, broker or model provider.
13. Provides complete auditability for every recommendation and every data transformation.
14. Protects capital ahead of maximizing returns.

The central design principle is:

Do not ask, “Which stock will rise tomorrow?”
Ask, “Which financially strong, reasonably valued, liquid Indian companies currently offer the most attractive long-term expected return relative to their risks, and should any be purchased under this investor’s portfolio constraints?”

⸻

2. NON-NEGOTIABLE TRUTHFULNESS

Never describe any stock as guaranteed, safe, certain, assured or definitely profitable.

Never fabricate:

* Prices
* Financial statements
* Corporate actions
* Promoter holdings
* Share pledges
* Auditor qualifications
* Earnings dates
* News
* Regulatory filings
* Benchmark constituents
* Data-source capabilities
* Backtest results
* Model accuracy
* Transaction costs
* Broker functionality
* API access
* Licensing rights

When required data is unavailable, stale, contradictory or unverified:

* Mark it unavailable.
* Reduce confidence.
* Exclude the security when the missing data is material.
* Preserve the conflicting source records.
* Explain the reason.
* Never silently impute critical investment facts.

A recommendation engine must be allowed to abstain.

⸻

3. SAFETY, REGULATORY AND PRODUCT BOUNDARIES

This platform must initially operate as a private research and decision-support tool.

Before implementing public distribution, subscriptions, third-party recommendations, social sharing, monetization or automated trading, create a formal regulatory review requirement covering at minimum:

* SEBI Investment Adviser requirements
* SEBI Research Analyst requirements
* Exchange and market-data licensing
* Broker API terms
* Data redistribution restrictions
* Recordkeeping
* Disclosures
* Suitability and risk profiling
* Algorithmic trading requirements
* Privacy and cybersecurity obligations
* Tax and accounting implications

Do not claim legal compliance merely because code contains disclaimers.

Create:

* docs/compliance/REGULATORY_BOUNDARY.md
* docs/compliance/DATA_LICENSING_MATRIX.md
* docs/compliance/DISCLOSURES.md
* docs/compliance/REQUIRED_HUMAN_REVIEW.md

The application must prominently state:

* This is a research and decision-support system.
* It does not guarantee returns.
* Equity investments can lose capital.
* Outputs may be wrong because of bad data, model error or unforeseen events.
* Recommendations must be reviewed by the user.
* Past performance and backtests do not guarantee future results.

There must be no autonomous order execution in version 1.

Any broker integration must initially be read-only or paper-trading only.

A later live-order feature may be implemented only behind:

* A disabled-by-default feature flag
* Explicit user confirmation
* Two-step approval
* Maximum order-value limits
* Portfolio-risk validation
* Duplicate-order protection
* Market-hours validation
* Price-slippage guardrails
* Emergency kill switch
* Full immutable audit logs

⸻

4. CAPITAL-PROTECTION PRINCIPLES

The platform shall prefer missing an opportunity over exposing the investor to an inadequately understood risk.

Capital-protection rules must include:

* No leverage
* No margin funding
* No derivatives
* No options
* No futures
* No intraday trading
* No short selling
* No SME-board securities by default
* No penny stocks
* No suspended securities
* No trade-to-trade or surveillance-category stocks unless explicitly reviewed
* No materially illiquid stocks
* No stocks with unresolved critical data-quality failures
* No recommendations during severe system or data outages
* No averaging down merely because price declined
* No concentration beyond configurable portfolio limits
* No recommendation solely because of technical momentum
* No recommendation solely because a stock appears statistically cheap
* No recommendation based on social-media sentiment alone
* No automated reaction to unverified news
* No forced daily purchase
* No output count quota

Default constraints must be conservative and configurable, not hard-coded business constants.

Initial example constraints for discussion and backtesting—not assumed optimal:

* Maximum individual-stock target weight: 5%
* Maximum sector target weight: 20%
* Maximum new capital deployed in one day: 5%
* Minimum cash reserve: 10%
* Maximum number of portfolio holdings: 20
* Minimum market capitalization: configurable
* Minimum median daily traded value: configurable
* Minimum listing history: configurable
* Minimum required data completeness score: 95%
* Maximum tolerated drawdown before risk review: configurable
* Maximum portfolio volatility: configurable
* No purchase when valuation, governance or data-quality hard stops are triggered

These must be validated empirically and adjusted through configuration.

⸻

5. WORKING METHOD AND MULTI-AGENT ORGANIZATION

Use parallel agents or isolated worktrees where supported. Do not allow agents to modify overlapping files without a coordination plan.

Create a lead orchestrator and the following specialist roles:

Agent A — Principal Architect

Responsibilities:

* System architecture
* Module boundaries
* Architecture decision records
* Dependency direction
* Build-versus-buy decisions
* Scalability and reliability requirements
* Repository structure
* Interface contracts
* Definition of done

Agent B — Indian Market and Regulatory Researcher

Responsibilities:

* Official-source regulatory research
* Indian market structure
* NSE/BSE identifiers
* Trading calendars
* Corporate actions
* Index methodologies
* Data licensing
* Research-adviser boundary
* Broker-integration constraints

This agent must prefer primary official sources and record source URLs, access dates and relevant document versions.

Agent C — Data Platform Engineer

Responsibilities:

* Ingestion connectors
* Raw immutable storage
* Data normalization
* Schema evolution
* Entity resolution
* Security master
* Point-in-time datasets
* Corporate-action adjustment
* Validation
* Lineage
* Incremental pipelines
* Retry and idempotency design

Agent D — Quantitative Researcher

Responsibilities:

* Factor definitions
* Portfolio-construction research
* Benchmarking
* Rebalancing policy
* Transaction-cost assumptions
* Walk-forward testing
* Statistical significance
* Factor redundancy
* Regime analysis
* Risk-adjusted evaluation

Agent E — Fundamental Equity Analyst

Responsibilities:

* Accounting-aware features
* Financial quality
* Earnings quality
* Balance-sheet risk
* Cash-flow analysis
* Valuation
* Governance red flags
* Sector-specific metric validity
* Explainable investment theses

Agent F — Machine-Learning Scientist

Responsibilities:

* Label design
* Leakage prevention
* Feature pipeline
* Baselines
* Cross-sectional ranking models
* Probability calibration
* Uncertainty estimation
* Explainability
* Drift detection
* Champion/challenger framework
* Reproducible training

Agent G — Portfolio and Risk Engineer

Responsibilities:

* Suitability profile
* Portfolio constraints
* Position sizing
* Concentration
* Diversification
* liquidity
* Drawdown controls
* scenario analysis
* stress testing
* risk budgets
* abstention policies

Agent H — Backend Engineer

Responsibilities:

* APIs
* Domain models
* services
* job orchestration
* authentication
* authorization
* caching
* persistence
* error handling
* audit events

Agent I — Frontend and UX Engineer

Responsibilities:

* Extremely simple investor interface
* Mobile responsiveness
* accessible typography
* Indian number formatting
* multilingual readiness
* clear explanations
* no dark patterns
* decision confirmation
* portfolio views
* data-confidence display

Agent J — Platform, DevOps and Observability Engineer

Responsibilities:

* Containers
* environments
* CI/CD
* scheduled jobs
* secrets
* backups
* logging
* metrics
* traces
* alerts
* disaster recovery
* deployment documentation

Agent K — Security and Privacy Reviewer

Responsibilities:

* Threat model
* dependency and secret scanning
* access control
* secure configuration
* API abuse prevention
* supply-chain risk
* PII handling
* audit-log protection
* incident response

Agent L — Independent Validation and Red-Team Reviewer

Responsibilities:

* Challenge all assumptions
* Detect leakage
* identify survivorship bias
* reproduce backtests
* test failure modes
* test misleading explanations
* verify no unsupported claims
* try to break the system
* reject release when evidence is inadequate

Agent M — Documentation and Product Operations Engineer

Responsibilities:

* User guide
* operating manual
* data dictionary
* model cards
* runbooks
* troubleshooting
* release notes
* decision logs
* onboarding

The lead orchestrator must:

1. Define the dependency graph.
2. Assign non-overlapping tasks.
3. Require written contracts before implementation.
4. Merge only after tests and review.
5. Maintain a project status file.
6. Record unresolved questions.
7. Stop parallel work that depends on an undecided architecture.
8. Require independent review of all financial calculations.

Create:

* docs/project/MASTER_PLAN.md
* docs/project/DEPENDENCY_GRAPH.md
* docs/project/AGENT_TASKS.md
* docs/project/DECISION_LOG.md
* docs/project/RISK_REGISTER.md
* docs/project/OPEN_QUESTIONS.md
* docs/project/RELEASE_CHECKLIST.md

⸻

6. FIRST ACTIONS

Do not begin by writing application code.

Perform these actions in order:

1. Inspect the repository and environment.
2. Determine available tooling, languages, package managers and credentials without exposing secrets.
3. Record all assumptions.
4. Identify missing decisions that can safely be resolved using conservative defaults.
5. Research current official requirements where internet access is available.
6. Produce a system architecture proposal.
7. Produce a data-source feasibility and licensing matrix.
8. Produce a delivery plan divided into independently testable milestones.
9. Produce acceptance criteria for every milestone.
10. Establish the repository structure.
11. Create an AGENTS.md containing concise repository-wide instructions.
12. Create narrower instructions inside major directories where needed.
13. Create issues or task files for parallel agents.
14. Implement only after the architecture and contracts are internally reviewed.

Do not ask the human broad questions that can be addressed with reversible defaults.

Do ask the human only when a decision is:

* Financially consequential
* Legally consequential
* Irreversible
* Dependent on unavailable credentials
* Dependent on the investor’s true personal circumstances

Continue productively while documenting such blocked decisions.

⸻

7. TARGET PRODUCT EXPERIENCE

The investor should not need to understand quantitative finance.

The home screen should show:

A. System status

* Data freshness
* Last successful update
* Market status
* Portfolio status
* Important warnings
* Whether analysis is complete
* Whether any data provider failed

B. Today’s decision

Exactly one of:

* No purchase recommended today
* Review these candidates
* Existing holdings require review
* Data unavailable—do not act

Never fabricate a list merely to populate the interface.

C. Candidate card

Each candidate must show:

* Company name
* NSE/BSE symbol
* Sector and industry
* Current or last verified price with timestamp
* Suggested research status, not imperative language
* Proposed accumulation range, only if methodology supports it
* Estimated valuation band
* Suggested maximum allocation
* Expected holding horizon
* Overall score
* Confidence level
* Data-quality score
* Liquidity score
* Risk level
* Primary reasons
* Primary risks
* Conditions that invalidate the thesis
* Latest result date
* Next known event, when verified
* Whether the stock is already owned
* Portfolio impact
* Evidence and source links
* Model version and analysis timestamp

Avoid false precision. Use score ranges or calibrated probabilities when appropriate.

D. Plain-language explanation

Example structure:

“Why it passed”

* Strong balance sheet
* Consistent operating cash generation
* Improving profitability
* Reasonable valuation relative to its own history and peers
* Positive but not extreme price momentum

“Why it may still fail”

* Sector cycle could weaken
* Valuation is above historical median
* Customer concentration is high
* Recent cash conversion has deteriorated

“Why the system is not recommending a larger allocation”

* Existing sector exposure is already elevated
* Volatility is high
* The company’s data history is limited

E. Portfolio page

Show:

* Total invested value
* Cash reserve
* Unrealized gain/loss
* Realized gain/loss
* XIRR where meaningful
* Benchmark comparison
* Sector exposure
* Stock concentration
* Risk contribution
* Drawdown
* Dividend income
* Upcoming verified corporate events
* Thesis status for every holding
* Suggested review actions
* Tax lots if transaction data is available
* Data freshness

F. Decision journal

For every approved or rejected candidate, store:

* What was known at the time
* Recommendation
* Score components
* Investor decision
* Price and timestamp
* Intended horizon
* Position size
* Thesis
* Risks
* Invalidating conditions
* Subsequent outcome
* Whether the original thesis was correct

Do not rewrite historical recommendations after new information arrives.

⸻

8. INVESTOR SUITABILITY PROFILE

Create a suitability questionnaire and versioned profile containing:

* Age range
* Financial dependents
* Investment horizon
* Income stability
* Emergency fund
* Existing debt
* Current assets
* Existing equity exposure
* Liquidity needs
* Expected withdrawals
* Capacity for loss
* Tolerance for temporary drawdowns
* Investment experience
* Tax residency
* Restricted sectors
* Ethical preferences
* Maximum acceptable concentration
* Preferred language
* Whether recommendations may use small-cap securities

The system must distinguish:

* Risk tolerance
* Risk capacity
* Required return
* Investment horizon
* Liquidity requirements

The recommendation engine must use suitability constraints, but the research-ranking engine must remain analytically separable from personalization.

Create separate objects:

* ResearchCandidate
* InvestorSuitabilityAssessment
* PortfolioActionProposal

A strong company is not automatically an appropriate purchase for this investor.

⸻

9. INVESTMENT UNIVERSE

Do not use the current index constituents retrospectively.

Build or acquire a point-in-time security master containing:

* Stable internal security ID
* ISIN
* NSE symbol
* BSE code
* Company legal name
* Historical names
* Listing exchange
* Listing date
* Delisting date
* Series
* Security type
* Sector
* Industry
* Index memberships with effective dates
* Corporate actions
* Symbol changes
* Mergers
* Demergers
* Suspensions
* Relistings
* Share-class changes
* Face-value changes

Initial live universe may begin with liquid main-board equities such as:

* Nifty 50
* Nifty Next 50
* Nifty Midcap 150

But historical backtests must use point-in-time membership or a properly reconstructed eligible universe.

Implement configurable exclusion rules for:

* Insufficient listing history
* Low traded value
* Low free float
* Unreliable financial history
* Suspended or delisted securities
* Surveillance categories
* Extreme price gaps caused by unresolved corporate actions
* Insolvency proceedings
* Unresolved auditor resignation or qualification
* Excessive promoter pledge
* Frequent related-party concerns
* Negative net worth where inappropriate for the strategy
* Sector-specific inapplicability

Banks, NBFCs, insurers and other financial institutions must not be evaluated using industrial-company debt metrics without sector-aware definitions.

⸻

10. DATA-SOURCE STRATEGY

Create provider interfaces. Do not tightly couple domain logic to a single vendor.

Required provider categories:

* Security master
* End-of-day price
* Intraday or quote data, if later required
* Corporate actions
* Index constituents
* Financial statements
* Shareholding patterns
* Promoter pledge
* Corporate announcements
* Auditor and governance events
* Macroeconomic data
* News
* Broker portfolio
* Trading calendar
* Risk-free rate
* Sector and industry classification

For each candidate provider, document:

* Official or third-party
* Coverage
* Historical depth
* Point-in-time availability
* Adjustment methodology
* API stability
* Rate limits
* Cost
* Legal usage rights
* Redistribution rights
* Authentication
* Failure behavior
* Known limitations
* Field-level provenance
* Whether suitable for research, backtesting or production

Prefer licensed or official data for production.

Public convenience libraries may be used only behind adapters and must not be treated as authoritative without validation.

Do not scrape sites in violation of terms, robots restrictions, access controls or licensing policies.

Raw source data must be immutable and timestamped.

Each normalized field should retain:

* Source provider
* Source record identifier
* Source publication timestamp
* Ingestion timestamp
* Effective date
* Revision date
* Parser version
* Transformation version
* Confidence
* Validation status

⸻

11. DATA ARCHITECTURE

Use a layered architecture:

Raw layer

Exact source payloads, immutable and content-addressed where practical.

Staging layer

Parsed provider-specific tables retaining source semantics.

Canonical layer

Normalized domain models using stable identifiers.

Point-in-time analytical layer

Records available as of each historical decision timestamp.

Feature layer

Versioned model and factor features.

Recommendation layer

Scores, exclusions, explanations and portfolio proposals.

Audit layer

Immutable decisions, approvals, model versions and source lineage.

Use explicit schemas and migrations.

Recommended local-first stack, subject to architectural review:

* Python 3.12+
* uv for dependency management
* Polars and/or pandas for analysis
* DuckDB for local analytical workflows
* PostgreSQL for production application state
* Parquet for columnar historical storage
* SQLAlchemy or an equally disciplined persistence layer
* Alembic for migrations
* Pydantic for domain validation
* FastAPI for APIs
* Prefect, Dagster or a simpler scheduler selected through an ADR
* React/Next.js with TypeScript for the user interface
* Docker Compose for reproducible local operation
* pytest for tests
* Ruff for linting and formatting
* mypy or pyright for static typing
* Playwright for end-to-end tests
* OpenTelemetry-compatible observability

Do not adopt a technology merely because it is fashionable. Record each major selection in an architecture decision record.

⸻

12. DATA QUALITY FRAMEWORK

The system must never proceed silently on corrupted financial data.

Implement:

* Schema validation
* Type validation
* Allowed-value validation
* Primary-key uniqueness
* Referential integrity
* Date consistency
* Currency and unit normalization
* Duplicate detection
* Missingness monitoring
* Staleness checks
* Cross-provider reconciliation
* Corporate-action continuity checks
* Adjusted-price sanity checks
* Accounting identity checks
* Restatement handling
* Split and bonus adjustment checks
* Outlier detection
* Trading-calendar validation
* Sequence-gap detection
* Price-volume anomaly detection
* Reconciliation of quarterly and annual figures
* Detection of cumulative-vs-standalone quarterly reporting
* Consolidated-vs-standalone statement identification

Examples of accounting validations:

* Assets approximately equal liabilities plus equity
* Cash-flow components reconcile to net cash movement
* Annual totals reconcile with reported periods where applicable
* Per-share data reflects corporate actions
* Fiscal-year alignment is correct
* Units such as rupees, thousands, lakhs, crores and millions are normalized correctly

Every pipeline run must produce a data-quality report.

Every security-date must receive a data_quality_score.

Material validation failures must block recommendations.

⸻

13. POINT-IN-TIME INTEGRITY

This is mandatory.

For every historical decision date, use only information that was actually available by that timestamp.

Do not use:

* Later restated financials as though originally known
* Current sector classifications for historical dates without effective dates
* Current index constituents for prior periods
* Future corporate actions
* Future earnings
* Revised macroeconomic data unless modeling revision availability
* Delisted-stock omissions
* News published after the decision time
* Full-period high/low data not available at the decision timestamp

Financial features must use filing or publication availability dates, not merely fiscal period-end dates.

Create automated tests that intentionally inject future information and verify that the system rejects it.

⸻

14. CORPORATE-ACTION HANDLING

Support at minimum:

* Cash dividends
* Stock splits
* Bonus issues
* Rights issues
* Buybacks
* Mergers
* Demergers
* Spin-offs
* Symbol changes
* Face-value changes
* Delistings

Maintain both:

* Raw unadjusted prices
* Correctly adjusted analytical series

Backtests must clearly distinguish:

* Price return
* Total return
* Dividend cash flow
* Tax assumptions
* Corporate-action adjustments

Never apply an adjustment twice.

Write reconciliation tests around known historical corporate actions.

⸻

15. FEATURE ENGINEERING

Use features grouped by interpretable families.

A. Business quality

Potential features:

* ROE
* ROCE
* ROA
* Incremental ROCE
* Gross-margin stability
* Operating-margin stability
* Asset turnover
* Working-capital efficiency
* Cash conversion
* Free-cash-flow margin
* Free-cash-flow consistency
* Earnings stability
* Revenue stability
* Return-on-capital persistence

Use sector-aware definitions.

B. Growth quality

Potential features:

* Revenue CAGR
* Operating-profit CAGR
* EPS CAGR
* Free-cash-flow CAGR
* Growth acceleration
* Growth consistency
* Organic-versus-acquisition-dependent growth where data permits
* Growth funded by internal cash generation
* Per-share growth rather than aggregate growth alone

C. Balance-sheet safety

Potential features:

* Net debt to EBITDA
* Interest coverage
* Debt maturity stress
* Current ratio where relevant
* Quick ratio where relevant
* Cash to liabilities
* Contingent-liability indicators
* Equity dilution
* Working-capital borrowing dependence
* Piotroski-style measures
* Altman-style measures only where applicable

D. Earnings quality

Potential features:

* Operating cash flow to net income
* Accrual ratio
* Receivables growth relative to revenue
* Inventory growth relative to revenue
* Capitalized-cost behavior
* Exceptional-item dependence
* Other-income dependence
* Tax-rate anomalies
* EBITDA-to-cash conversion
* Repeated one-off adjustments

E. Valuation

Potential features:

* P/E
* Forward P/E only with properly timestamped forecast data
* EV/EBITDA
* EV/EBIT
* Price-to-book where appropriate
* Price-to-sales
* Price-to-free-cash-flow
* Free-cash-flow yield
* Earnings yield
* Dividend yield
* Valuation relative to own history
* Valuation relative to sector
* Valuation adjusted for quality and growth
* Reverse-DCF implied expectations
* Simple scenario valuation

Do not apply uniform valuation multiples across structurally different sectors.

F. Momentum and trend

Potential features:

* 3-, 6-, 9- and 12-month returns
* 12-month return excluding the most recent month
* Distance from 52-week high
* Relative strength versus benchmark
* Relative strength versus sector
* Price above long-term moving average
* Moving-average slope
* Earnings momentum
* Volume confirmation
* Gap and volatility behavior

Momentum may improve timing but cannot override fundamental or governance hard stops.

G. Risk

Potential features:

* Historical volatility
* Downside deviation
* Beta
* Maximum drawdown
* Drawdown duration
* Idiosyncratic volatility
* Liquidity
* Average traded value
* Price-impact proxy
* Gap risk
* Tail-risk estimate
* Correlation with current holdings
* Sector concentration contribution
* Stress-scenario loss

H. Governance and forensic signals

Potential features:

* Promoter holding trend
* Promoter pledge trend
* Auditor resignation
* Auditor qualification
* Delayed filings
* Related-party transactions
* Repeated equity dilution
* Warrants and preferential allotments
* Unusual receivables
* Cash-flow inconsistency
* Subsidiary complexity
* Material regulatory actions
* Management turnover
* Capital-allocation history
* Dividend behavior
* Buyback quality
* Acquisition discipline

Governance red flags require traceable evidence.

Do not infer fraud from weak proxies.

I. Market and sector regime

Potential features:

* Broad-index trend
* Breadth
* Sector relative strength
* India VIX or appropriate volatility proxy
* Interest-rate regime
* Inflation regime
* Credit conditions
* Currency regime
* Commodity sensitivity
* Market valuation
* Earnings-revision breadth, if licensed data exists

Market regime may influence thresholds and portfolio exposure but must not generate unsupported certainty.

⸻

16. SECTOR-SPECIFIC MODELS

Create sector-aware analytical modules.

At minimum distinguish:

* Banks
* NBFCs
* Insurance
* IT services
* Consumer staples
* Consumer discretionary
* Industrials
* Capital goods
* Infrastructure
* Pharmaceuticals
* Healthcare
* Energy
* Metals and mining
* Utilities
* Telecom
* Real estate
* Chemicals
* Automobiles
* Asset-light platforms

Examples:

Banks may require:

* Net interest margin
* Gross and net NPA
* Provision coverage
* Credit cost
* CASA
* Capital adequacy
* Loan growth
* Deposit growth
* Return on assets
* Return on equity
* Asset-liability risk

Insurers may require:

* Embedded value
* Value of new business
* VNB margin
* Persistency
* Solvency
* Product mix

Do not score financial companies using net-debt-to-EBITDA in the same way as industrial companies.

Each feature must declare applicability by sector.

⸻

17. RULE-BASED BASELINE

Before machine learning, implement a transparent deterministic baseline.

The baseline must contain:

* Hard exclusions
* Fundamental quality score
* Growth-quality score
* Balance-sheet safety score
* Earnings-quality score
* Valuation score
* Momentum score
* Governance score
* Liquidity score
* Risk score
* Portfolio-fit score
* Market-regime modifier
* Data-confidence modifier

Do not hard-code arbitrary weights without documenting the rationale.

Start with clearly labeled research defaults, then test:

* Equal weighting
* Literature-informed weighting
* Rank aggregation
* Sector-neutral weighting
* Constrained optimization
* Robustness across reasonable weight ranges

The score must remain decomposable.

A user must be able to see why one company ranked above another.

⸻

18. MACHINE-LEARNING DESIGN

Machine learning is optional until the deterministic baseline is validated.

Do not begin with deep learning.

Establish baselines such as:

* Sector-neutral factor rank
* Linear/logistic model
* Regularized linear model
* Random forest
* Gradient-boosted trees
* Learning-to-rank model

Potential target definitions:

* Excess total return over Nifty 500 after 3, 6, 12 and 24 months
* Probability of outperforming the benchmark by a specified hurdle
* Risk-adjusted forward return
* Probability of severe drawdown
* Multi-task return and risk prediction

Prefer ranking and calibrated probability over precise price targets.

Avoid overlapping-label leakage.

Use:

* Purged time-series cross-validation
* Embargo periods
* Expanding-window validation
* Walk-forward out-of-sample testing
* Final untouched holdout period
* Sector-aware evaluation
* Market-regime evaluation
* Delisting-aware outcomes
* Transaction-cost-aware portfolio simulation

Never randomly shuffle financial time-series rows for primary validation.

Record:

* Training cutoff
* Feature definitions
* Dataset version
* Code commit
* Hyperparameters
* Evaluation metrics
* Calibration
* Limitations
* Intended use
* Prohibited use

Create model cards.

Potential evaluation metrics:

* Rank information coefficient
* Spearman correlation
* Precision at K
* Recall at K where meaningful
* Top-decile excess return
* Hit rate
* Brier score
* Calibration error
* Log loss
* Turnover
* Sharpe ratio
* Sortino ratio
* Maximum drawdown
* Calmar ratio
* Upside/downside capture
* Worst rolling-period return
* Tail loss
* Stability across sectors and regimes

Do not optimize solely for accuracy.

Compare every ML model against the simple baseline.

Reject an ML model when its apparent improvement is not robust after costs, multiple-testing controls and independent validation.

⸻

19. NATURAL-LANGUAGE AND NEWS LAYER

The language-model layer must never invent the investment thesis.

It may:

* Summarize verified filings
* Compare quarterly results
* Explain score components
* Identify contradictions across documents
* Extract candidate risks
* Convert structured analysis into plain language
* Translate output into the investor’s chosen language

It may not:

* Produce unsupported facts
* Override hard risk rules
* Assign scores without structured evidence
* Create fake citations
* convert rumors into facts
* recommend a security using only narrative sentiment

Use retrieval-grounded generation.

Every material generated claim should reference:

* Source document
* Source date
* Relevant section
* Extraction confidence
* Structured metric where applicable

News sentiment should be a secondary risk-monitoring input, not the main investment signal.

Separate:

* Confirmed exchange filing
* Company press release
* Reputable journalism
* Analyst commentary
* Unverified social media

⸻

20. PORTFOLIO CONSTRUCTION

Research ranking and portfolio construction are separate stages.

The portfolio-construction engine must consider:

* Current holdings
* Available cash
* Existing sector exposures
* Stock concentration
* Risk contribution
* Correlation
* Liquidity
* Tax lots
* Transaction costs
* Investor suitability
* Minimum practical order size
* Maximum daily deployment
* Rebalancing threshold
* Holding-period policy
* Benchmark
* Cash reserve

Support conservative methods such as:

* Equal-risk allocation
* Capped equal weight
* Score-weighted with strict caps
* Volatility-scaled weights
* Risk-budget optimization
* Robust mean-variance only when assumptions are defensible

Default to simpler and more robust methods.

Do not use unconstrained mean-variance optimization.

No proposed portfolio action may violate:

* Single-stock cap
* Sector cap
* Liquidity cap
* Cash reserve
* Suitability
* risk budget
* hard exclusion
* data-quality threshold
* duplicate-order check

Implement a “do nothing” decision.

Use a minimum improvement threshold before proposing turnover.

⸻

21. SELL AND REVIEW FRAMEWORK

Do not use simplistic fixed stop losses for all long-term investments.

Define separate review triggers:

Thesis invalidation

* Deterioration in business quality
* Governance event
* Balance-sheet stress
* Structural competitive deterioration
* Accounting-quality concern
* Material deviation from investment thesis

Valuation review

* Valuation becomes extreme relative to justified assumptions
* Expected return falls below threshold

Portfolio-risk review

* Position becomes oversized
* Sector concentration exceeds limits
* Correlation rises materially
* Investor liquidity needs change

Data and model review

* New filing materially changes the score
* Data provider correction
* Model drift
* Confidence collapse

Price-based monitoring

Price changes should prompt review, not automatically imply buy or sell.

Every sell or trim proposal must show:

* Original thesis
* Changed facts
* Current score
* Portfolio impact
* Tax considerations where data is available
* Alternatives
* Confidence
* Evidence

⸻

22. BACKTESTING ENGINE

Build a rigorous event-driven or date-driven portfolio simulator.

It must support:

* Point-in-time universe
* Point-in-time fundamentals
* Corporate actions
* Delistings
* Cash
* Dividends
* Taxes as configurable scenarios
* Brokerage
* Exchange charges
* STT and other applicable costs as versioned assumptions
* Slippage
* Impact
* Partial fills if relevant
* Rebalancing schedules
* Order delays
* Limit on percentage of daily traded value
* Benchmark total return
* Portfolio cash flows

Default recommendation timestamp and execution timing must be explicit.

Example:

* Data cutoff: after market close on trading day T
* Recommendation generated after successful pipeline completion
* Earliest simulated execution: next trading session using a conservative price assumption

Never trade at the same closing price used to generate the signal unless that execution is genuinely achievable and justified.

Test:

* Monthly
* Quarterly
* Event-driven
* Threshold-driven rebalancing

Report:

* CAGR
* Total return
* Volatility
* Sharpe
* Sortino
* Maximum drawdown
* Calmar
* Worst month
* Worst year
* Recovery duration
* Hit rate
* Turnover
* Cost drag
* Sector attribution
* Stock attribution
* Factor attribution
* Rolling returns
* Rolling drawdowns
* Upside/downside capture
* Benchmark-relative return
* Tracking error
* Information ratio
* Tail behavior

Show confidence intervals where feasible.

Include subperiod analysis:

* Bull markets
* Bear markets
* Sideways markets
* High-volatility periods
* Rate-hike periods
* Pandemic disruption
* Sector booms and busts

Do not tune directly to named crises.

⸻

23. BIAS AND LEAKAGE CHECKLIST

The independent validation agent must explicitly test for:

* Survivorship bias
* Look-ahead bias
* Selection bias
* Delisting bias
* Restatement leakage
* Index-membership leakage
* Corporate-action leakage
* Label leakage
* Feature leakage
* Cross-validation contamination
* Hyperparameter overfitting
* Multiple-hypothesis testing
* Benchmark cherry-picking
* Start-date dependence
* End-date dependence
* Unrealistic fills
* Ignored transaction costs
* Incorrect adjusted prices
* Stale fundamentals
* Sector classification leakage
* Duplicate securities
* Currency/unit errors
* Timestamp/timezone errors
* Publication-date errors

A release cannot pass solely because cumulative return looks attractive.

⸻

24. STRESS TESTING

Implement scenario analysis for:

* Broad-market decline of 10%, 20%, 30% and 50%
* Sector-specific crash
* Interest-rate shock
* INR depreciation/appreciation
* Commodity shock
* Liquidity evaporation
* Gap-down events
* Correlation convergence
* Earnings disappointment
* Governance scandal
* One holding becoming untradeable
* Data provider outage
* Delayed financial filing
* Broker outage
* Duplicate or stale signal
* Model server outage

The interface must explain likely portfolio impact without pretending scenarios are forecasts.

⸻

25. EXPLAINABILITY

Every recommendation must expose:

* Eligibility result
* Exclusion checks
* Feature values
* Percentile ranks
* Sector-relative comparisons
* Historical comparisons
* Score components
* Weight contributions
* Confidence modifier
* Data-quality modifier
* Portfolio-fit modifier
* Principal reasons
* Principal risks
* Invalidation conditions
* Model version
* Data cutoff

For ML models, provide:

* Global feature importance
* Local explanation
* Calibration
* Model limitations
* Agreement/disagreement with deterministic baseline

Do not use an explanation technique that misrepresents causal importance.

Phrase explanations as associations and model evidence, not causality, unless causal evidence exists.

⸻

26. CONFIDENCE AND ABSTENTION

Build a formal confidence score based on:

* Data completeness
* Source agreement
* Model agreement
* Historical model calibration
* Feature stability
* Distance from decision threshold
* Regime similarity to training data
* Liquidity
* Corporate-event uncertainty
* Forecast dispersion where available

Abstain when:

* Material inputs are missing
* Data is stale
* Providers materially disagree
* Corporate action is unresolved
* Company is under an unresolved exceptional event
* Model is out of distribution
* Portfolio constraints eliminate all candidates
* Expected return does not exceed the required hurdle after costs
* Risk is too high
* Confidence is below threshold

Abstention is a successful outcome.

⸻

27. APPLICATION ARCHITECTURE

Use clean boundaries such as:

* domain
* application
* infrastructure
* api
* ui
* pipelines
* research
* models
* backtesting
* risk
* compliance
* observability

Business rules must not depend directly on web frameworks or vendor SDKs.

Define interfaces for providers.

Use dependency inversion.

Avoid a microservice architecture unless there is a demonstrated operational need.

A modular monolith is preferred initially, with separately executable jobs and clear future extraction boundaries.

⸻

28. SUGGESTED REPOSITORY STRUCTURE

Create and refine a structure similar to:

bharat-equity-intelligence/
├── AGENTS.md
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── pyproject.toml
├── uv.lock
├── package.json
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── apps/
│   ├── api/
│   ├── web/
│   └── worker/
├── src/
│   └── bharat_equity/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       ├── ingestion/
│       ├── data_quality/
│       ├── features/
│       ├── scoring/
│       ├── models/
│       ├── portfolio/
│       ├── risk/
│       ├── backtesting/
│       ├── explanations/
│       ├── compliance/
│       └── observability/
├── research/
│   ├── notebooks/
│   ├── experiments/
│   ├── reports/
│   └── registries/
├── configs/
│   ├── base/
│   ├── development/
│   ├── test/
│   └── production/
├── data/
│   ├── README.md
│   └── samples/
├── migrations/
├── schemas/
├── docs/
│   ├── architecture/
│   ├── compliance/
│   ├── data/
│   ├── models/
│   ├── operations/
│   ├── product/
│   ├── project/
│   └── research/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── property/
│   ├── regression/
│   ├── leakage/
│   ├── e2e/
│   └── performance/
├── scripts/
├── infra/
├── monitoring/
└── .github/
    └── workflows/

Do not commit licensed data, secrets or personal portfolio information.

⸻

29. API DESIGN

Create versioned APIs for at minimum:

* System status
* Data freshness
* Eligible universe
* Security profile
* Candidate rankings
* Candidate explanation
* Portfolio
* Portfolio risk
* Proposed actions
* Investor suitability
* Decision approval
* Decision rejection
* Decision journal
* Backtest runs
* Model registry
* Data-quality reports
* Audit events

Use:

* Typed request/response schemas
* Pagination
* Stable error models
* Idempotency keys
* Correlation IDs
* Authentication
* Authorization
* Rate limits
* Input validation
* OpenAPI documentation

Never expose raw secrets, provider credentials or internal exception traces.

⸻

30. USER INTERFACE STANDARDS

Design mobile-first because the initial user may interact mainly through a phone.

Requirements:

* Simple English initially
* Architecture ready for Hindi and Marathi localization
* Large touch targets
* High-contrast accessible design
* Plain-language risk explanations
* No flashing price elements
* No casino-like red/green gamification
* No confetti
* No urgency manipulation
* No “hot stock” language
* No default action that executes a purchase
* Clear timestamps
* Clear stale-data warnings
* Clear distinction between facts, estimates and model opinions

Use Indian number formatting where appropriate:

* ₹
* Thousand
* Lakh
* Crore

Support a “simple view” and an “expert details” view.

⸻

31. NOTIFICATIONS

Initially support notification adapters such as:

* Email
* Telegram
* Push notification
* Optional WhatsApp integration only through an approved provider and valid terms

Notifications must never contain an unqualified “Buy now.”

Example:

“Three companies passed today’s research and portfolio filters. Review them in the application. No action has been taken.”

Critical alerts:

* Data stale
* Provider failure
* Governance event
* Portfolio concentration breach
* Thesis review required
* Corporate action requiring attention
* Model drift
* Broker reconciliation mismatch

Avoid notification overload.

⸻

32. SCHEDULING

Define an India-market-aware trading calendar.

Potential daily workflow:

1. Ingest previous trading day’s final data.
2. Validate corporate actions.
3. Update verified company filings.
4. Reconcile provider data.
5. Generate quality report.
6. Build point-in-time features.
7. Score research universe.
8. Apply hard exclusions.
9. Evaluate portfolio fit.
10. Generate explanations.
11. Run risk checks.
12. Publish candidate set.
13. Notify user only after all critical checks pass.

All timestamps must be stored in UTC and displayed in Asia/Kolkata for the investor.

Do not assume every weekday is a trading day.

⸻

33. SECURITY REQUIREMENTS

Create a threat model.

Implement:

* Secret manager or secure environment injection
* No secrets in source control
* Secret scanning
* Dependency pinning
* Dependency vulnerability scanning
* Software bill of materials
* Least privilege
* Authentication
* Role-based authorization
* Encryption in transit
* Encryption at rest where appropriate
* CSRF protection where applicable
* Secure cookies
* Content Security Policy
* Rate limiting
* Input validation
* Output encoding
* Audit logging
* Backup encryption
* Restore testing
* Data-retention policy
* Account lockout and recovery controls
* Administrative action logging

Portfolio and suitability data are sensitive.

Logs must not contain credentials or full private user records.

No external AI provider may receive personal portfolio data without an explicit architecture and privacy decision.

⸻

34. OBSERVABILITY

Implement structured logs, metrics and traces.

Track:

* Pipeline duration
* Pipeline success/failure
* Data freshness
* Missingness
* Provider latency
* Provider disagreement
* Number of eligible securities
* Number excluded by rule
* Number of recommendations
* Abstention reason
* Model inference latency
* Model drift
* Feature drift
* Recommendation turnover
* API errors
* Queue depth
* Database health
* Notification delivery
* Audit-log integrity

Use correlation IDs through ingestion, scoring and recommendation publication.

Create actionable alerts with severity levels.

⸻

35. TESTING REQUIREMENTS

Minimum test categories:

Unit tests

Every financial formula, score component and risk rule.

Property-based tests

Examples:

* Split adjustments preserve economic value.
* Increasing transaction costs cannot improve otherwise identical net returns.
* A hard exclusion always prevents recommendation.
* Portfolio weights never exceed configured caps.
* Future information is never visible historically.
* Duplicate pipeline runs are idempotent.

Integration tests

* Data provider to canonical storage
* Feature pipeline
* scoring
* portfolio proposal
* database
* API

Contract tests

Every provider adapter and API contract.

Golden-data regression tests

Small verified datasets with manually checked expected outputs.

Leakage tests

Explicit adversarial tests.

Backtest reconciliation tests

Manually reproduce selected periods and trades.

End-to-end tests

From raw mock provider data to displayed candidate and journal record.

Failure-injection tests

* Provider outage
* stale data
* malformed payload
* corporate-action mismatch
* database interruption
* notification failure
* model artifact unavailable

Performance tests

* Full-universe daily run
* Historical backtest
* API response latency
* UI load performance

Security tests

* Authentication
* authorization
* injection
* secret exposure
* dependency vulnerability
* rate limiting

Critical financial code requires review by a second agent.

⸻

36. CODE QUALITY

Requirements:

* Strict typing
* Clear domain names
* Small composable functions
* No hidden global state
* Deterministic behavior where possible
* Reproducible random seeds
* Explicit timezone handling
* Decimal types for money where appropriate
* Clear unit conventions
* No silent exception swallowing
* Context-rich errors
* Idempotent jobs
* Transactional writes
* Migrations
* Backward-compatible API evolution
* Comprehensive docstrings where intent is non-obvious

Do not create generic abstractions before multiple concrete uses justify them.

Avoid notebooks for production business logic.

Notebooks may call versioned library code.

⸻

37. REPRODUCIBILITY

Every backtest and model run must record:

* Git commit
* Environment lockfile
* Dataset version
* Data cutoff
* Feature version
* Universe version
* Configuration
* Random seed
* Model artifact
* Cost assumptions
* Benchmark
* Output metrics
* Generated report

A result must be reproducible from metadata, subject to data-license availability.

Create experiment registries and artifact hashes.

⸻

38. DOCUMENTATION

Required documentation includes:

* Product requirements
* Architecture
* Domain glossary
* Repository guide
* Local setup
* Production deployment
* Data-source matrix
* Data dictionary
* Feature dictionary
* Scoring methodology
* Portfolio methodology
* Backtesting methodology
* Model cards
* Compliance boundary
* Security model
* Operations runbook
* Incident response
* Backup and restore
* User guide
* Investor explanation guide
* Known limitations
* Release notes

Every complex formula must be documented with:

* Definition
* Units
* Inputs
* Applicability
* Point-in-time behavior
* Missing-data behavior
* Tests
* Source or rationale

⸻

39. CI/CD

Build CI pipelines for:

* Formatting
* Linting
* Static typing
* Unit tests
* Integration tests
* Leakage tests
* Security scans
* Dependency audit
* Frontend tests
* Build
* Container scan
* Documentation-link validation
* Migration validation

No merge when required checks fail.

Deployment must use separate:

* Development
* Test
* Staging
* Production

Production deployment requires:

* Approved release checklist
* Database backup
* Migration plan
* Rollback plan
* Smoke tests
* Post-deployment monitoring

⸻

40. IMPLEMENTATION PHASES

Phase 0 — Discovery and governance

Deliver:

* Product requirements
* Regulatory boundary
* Data licensing matrix
* Architecture
* Security threat model
* Risk register
* Project plan
* Acceptance tests

No production code beyond scaffolding.

Phase 1 — Deterministic research foundation

Deliver:

* Security master
* EOD price ingestion
* Corporate actions
* financial ingestion
* data quality
* point-in-time storage
* feature calculations
* deterministic score
* simple CLI report
* verified sample dataset

Phase 2 — Bias-safe backtesting

Deliver:

* Historical eligible universe
* point-in-time backtester
* benchmark
* cost model
* corporate-action treatment
* leakage tests
* comprehensive research report
* independent reproduction

Phase 3 — Portfolio and suitability

Deliver:

* Investor profile
* portfolio import
* risk engine
* portfolio-fit score
* allocation proposal
* decision journal
* abstention

Phase 4 — Production application

Deliver:

* API
* web interface
* authentication
* scheduler
* notifications
* observability
* backups
* deployment configuration

Phase 5 — Machine-learning challenger

Deliver:

* Dataset builder
* baseline models
* walk-forward evaluation
* calibration
* explainability
* model card
* champion/challenger comparison

Deploy ML only if it passes predefined improvement criteria.

Phase 6 — Paper-trading and shadow operation

Run without live orders.

Deliver:

* Daily paper recommendations
* operational incident log
* data-quality history
* prediction calibration
* portfolio simulation
* user feedback
* minimum shadow period determined by evidence

Phase 7 — Optional broker connectivity

Read-only portfolio synchronization first.

Any order placement remains disabled until separately approved.

⸻

41. RELEASE GATES

A phase cannot be marked complete unless:

* Acceptance criteria pass
* Tests pass
* Documentation is updated
* No critical security issue exists
* Data lineage is available
* Independent reviewer signs off
* Known limitations are documented
* Reproduction instructions work
* No unsupported performance claim appears
* Human-facing output is understandable
* Rollback or recovery is documented

Machine learning cannot become champion merely because a single backtest improves.

A recommendation cannot be published when critical source data is stale.

A live-order capability cannot be enabled during initial delivery.

⸻

42. ACCEPTANCE CRITERIA FOR THE INITIAL HIGH-QUALITY RELEASE

The initial release is acceptable only when it can demonstrate all of the following:

1. Reproducible local setup from a clean machine.
2. Historical and current security identifiers resolve correctly.
3. At least one end-to-end licensed or legally acceptable data path is functional.
4. Raw records remain immutable.
5. Point-in-time feature generation passes leakage tests.
6. Corporate actions reconcile on a verified test set.
7. Financial formulas pass manual golden tests.
8. Deterministic ranking is fully explainable.
9. Hard exclusions cannot be bypassed accidentally.
10. Portfolio limits are enforced.
11. “No recommendation” works end to end.
12. Backtest includes costs and delistings where data permits.
13. Results are compared with appropriate benchmarks.
14. Independent validation reproduces key results.
15. Data outages visibly block action.
16. User sees data and model timestamps.
17. Every recommendation has evidence, risks and invalidation conditions.
18. No system component promises profit.
19. No broker order is placed automatically.
20. Security and backup tests pass.
21. The UI is usable on a phone.
22. The decision journal preserves historical evidence.
23. Model and strategy limitations are prominent.
24. The system can be operated from documented runbooks.
25. A complete audit package can be generated for any recommendation.

⸻

43. REQUIRED RESEARCH REPORT

After the deterministic backtest is complete, generate a professional report containing:

* Executive summary
* Question being tested
* Investment hypothesis
* Universe
* Data sources
* Licensing limitations
* Date range
* Point-in-time methodology
* Feature definitions
* Exclusion rules
* Scoring methodology
* Portfolio construction
* Execution assumptions
* Costs
* Benchmark
* Results
* Rolling results
* Drawdowns
* Sector analysis
* Regime analysis
* Sensitivity analysis
* Ablation study
* Statistical uncertainty
* Bias checks
* Failure cases
* Known limitations
* Reproducibility instructions
* Go/no-go recommendation

Include negative results.

Do not bury underperformance or fragile periods.

⸻

44. ROBUSTNESS ANALYSIS

For every claimed strategy advantage, test:

* Alternative reasonable thresholds
* Alternative weights
* Alternative rebalancing frequencies
* Alternative universes
* Alternative benchmarks
* Higher costs
* One-day execution delay
* Different start and end dates
* Sector-neutral versus unconstrained ranking
* Removal of best-performing securities
* Removal of best-performing years
* Bootstrap or block-bootstrap uncertainty
* Feature ablation
* Provider discrepancies

A strategy that works only under one narrow parameter combination is not production-ready.

⸻

45. AGENT REVIEW PROTOCOL

Each major component must follow:

1. Author agent proposes design.
2. Reviewer agent challenges assumptions.
3. Author addresses findings.
4. Test agent writes adversarial tests.
5. Validation agent reproduces outputs.
6. Orchestrator approves merge.

For quant research:

* The agent that invents the strategy cannot be the sole validator.
* The validator must receive raw methodology and reproduce results independently.
* The final report must include disagreements and resolutions.

For security:

* The implementation agent cannot close its own critical findings.

⸻

46. CHANGE MANAGEMENT

Every material change to:

* Universe
* Data source
* Feature
* Score weight
* Exclusion
* Cost assumption
* Benchmark
* Portfolio limit
* Model
* Recommendation threshold

must include:

* Reason
* Expected impact
* Tests
* Backtest comparison
* Migration implications
* Version increment
* Release note
* Reviewer approval

Historical recommendations must retain their original version.

⸻

47. OPERATIONAL FAILURE POLICY

When a critical job fails:

1. Do not publish stale recommendations as current.
2. Mark system status as degraded.
3. Identify failed component.
4. Preserve last known successful result with its original timestamp.
5. Inform user not to act on stale analysis.
6. Retry according to bounded policy.
7. Alert operator.
8. Record incident.
9. Require reconciliation after recovery.

Never hide partial pipeline failure behind a green status.

⸻

48. HUMAN APPROVAL FLOW

A proposed action must proceed through:

1. Research candidate generated.
2. Data checks passed.
3. Risk checks passed.
4. Portfolio-fit checks passed.
5. Plain-language explanation generated.
6. User opens detailed evidence.
7. User confirms that they understand risks.
8. User approves, rejects or postpones.
9. Decision is journaled.
10. In version 1, user manually places any order through their broker.

The interface must not pressure approval.

⸻

49. SAMPLE DAILY OUTPUT CONTRACT

Generate structured output similar to:

{
  "analysis_date": "YYYY-MM-DD",
  "data_cutoff": "ISO-8601 timestamp",
  "market": "India",
  "status": "REVIEW_CANDIDATES",
  "system_health": "HEALTHY",
  "recommendation_count": 2,
  "portfolio_action_required": false,
  "candidates": [
    {
      "security_id": "stable-internal-id",
      "symbol": "EXAMPLE",
      "company_name": "Example Limited",
      "research_status": "QUALIFIED_FOR_REVIEW",
      "horizon_months": [36, 60],
      "overall_score": 82.4,
      "confidence_band": "MEDIUM_HIGH",
      "data_quality_score": 98.1,
      "risk_level": "MEDIUM",
      "maximum_proposed_weight": 0.03,
      "score_components": {
        "quality": 88,
        "growth_quality": 79,
        "balance_sheet": 91,
        "earnings_quality": 76,
        "valuation": 68,
        "momentum": 72,
        "governance": 90,
        "liquidity": 95,
        "portfolio_fit": 81
      },
      "reasons": [],
      "risks": [],
      "invalidation_conditions": [],
      "source_references": [],
      "model_version": "version",
      "scoring_version": "version"
    }
  ],
  "abstention_reasons": [],
  "disclaimer_version": "version"
}

This is an interface example, not a claim about any real company.

⸻

50. ENGINEERING COMMAND EXPERIENCE

Create a consistent command interface such as:

make setup
make lint
make typecheck
make test
make test-leakage
make test-e2e
make ingest-sample
make build-features
make score
make backtest
make report
make run-api
make run-web
make run-worker
make docker-up
make backup
make restore-test

Provide equivalent direct commands in documentation.

⸻

51. SAMPLE DATA AND OFFLINE DEVELOPMENT

Because production data may require licensing:

* Include a tiny synthetic dataset.
* Include clearly licensed sample data where permitted.
* Ensure all tests run without paid credentials.
* Never represent synthetic results as investment evidence.
* Mark synthetic companies unmistakably.
* Keep provider integrations separately testable through recorded contract fixtures where licensing permits.

⸻

52. PERFORMANCE EXPECTATIONS

Set and measure realistic service-level objectives.

Examples to refine:

* Daily EOD pipeline finishes within a defined window.
* Critical data freshness is visible.
* API candidate list returns promptly.
* No duplicate publication occurs.
* Recommendation generation is idempotent.
* Restore procedure meets documented recovery objectives.

Do not optimize prematurely.

Correctness and auditability take priority over raw speed.

⸻

53. COST CONTROL

Document expected recurring costs for:

* Market data
* Fundamental data
* News
* Hosting
* Database
* Storage
* Notifications
* AI usage
* Monitoring
* Backups
* Broker integration

Build budget alerts.

Use caching and batch processing.

Do not send every company filing to an expensive language model.

Use deterministic parsing first and AI only where it adds measurable value.

⸻

54. PRODUCT NAME AND BRANDING

Use the working name:

Bharat Long-Term Equity Intelligence

Do not use language implying SEBI registration, guaranteed profit or official exchange affiliation.

Create a restrained, trustworthy visual identity.

The application should feel closer to a professional wealth-management research terminal than a speculative trading app.

⸻

55. QUESTIONS THAT MUST REMAIN CONFIGURABLE

Do not permanently decide these in code:

* Eligible indices
* Market-cap floor
* Liquidity floor
* Portfolio size
* Stock cap
* Sector cap
* Cash reserve
* Rebalancing frequency
* Holding horizon
* Valuation limits
* Promoter-pledge limit
* Model threshold
* Confidence threshold
* Required return hurdle
* Transaction costs
* Tax scenario
* Benchmark
* Language
* Notification channel

Store versioned configuration.

⸻

56. DELIVERABLE FORMAT AFTER EACH PHASE

At the end of each phase, provide:

1. Completed work
2. Architecture changes
3. Files changed
4. Tests added
5. Test results
6. Data limitations
7. Security findings
8. Quantitative findings
9. Regulatory assumptions
10. Unresolved risks
11. Reproduction commands
12. Next phase
13. Explicit release decision: PASS, CONDITIONAL PASS or FAIL

Never report success without actual verification.

⸻

57. IMMEDIATE EXECUTION INSTRUCTIONS

Begin now.

Your first response and repository changes must accomplish the following:

1. Inspect the repository.
2. Produce a concise environment assessment.
3. Create the master project plan.
4. Create the proposed architecture.
5. Create the initial ADRs.
6. Create the data-source and licensing research plan.
7. Create the regulatory-boundary research plan.
8. Create the threat model outline.
9. Create the risk register.
10. Create the dependency graph.
11. Create the phase-by-phase task breakdown.
12. Create the agent ownership map.
13. Create acceptance criteria.
14. Create AGENTS.md.
15. Scaffold the repository only after the design is coherent.
16. Run all available checks.
17. Show what is complete and what remains blocked.

Use parallel agents for independent research and review where available.

Do not attempt to build the entire system in one unreviewed pass.

Do not stop after producing plans. Once the foundation has passed review, proceed through the implementation phases autonomously, continuously validating work and committing coherent changes.

At every stage:

* Protect capital.
* Prefer evidence over complexity.
* Prefer reproducibility over impressive claims.
* Prefer transparent baselines over black boxes.
* Prefer abstention over weak recommendations.
* Prefer verified data over abundant data.
* Prefer simple robust portfolio rules over fragile optimization.
* Treat every backtest result as potentially wrong until independently reproduced.
* Never claim that profitability is guaranteed.

The final result must be a deployable, documented, tested, explainable and auditable investment-research platform—not a demonstration notebook, a superficial dashboard or an unverified stock-prediction model.
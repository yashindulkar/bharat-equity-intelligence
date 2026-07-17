# Field requirements

**Proposal — schema version 1.0.0.** Every canonical record also requires individually declared `source_record_id`, `provider_id`, `product`, `published_at`, `observed_at`, `ingested_at`, `validated_at`, `usable_from`, `effective_at`, `effective_until`, `revision`, `version_chain_id`, `schema_version`, `parser_version`, `transformation_version`, `validation_status`, `confidence`, `evidence_reference`, and `license_policy_id`. Each is typed respectively as string, string, string, UTC instant, UTC instant, UTC instant, UTC instant, UTC instant, UTC instant, optional UTC instant, positive integer, string, semver string, semver string, semver string, enum, decimal fraction, string, and string. All are required/critical except `effective_until` and `confidence` (optional/high). Corrections append and preserve prior vintages. Missing required lineage/time/license fields quarantines. Their license requirement is exact provider/product retention, processing, derived/display/backup permission for the intended purpose.

Each row below is one independently mapped field. Where several fields share text, it is repeated deliberately. `Conditional` means required only for the stated record/action type; it is never silently optional.

Legend: R/O required/optional; C/H/M critical/high/medium. License requirement for every row is explicit permission for private household research, retention/processing, and the applicable derived/display/backup purpose.

## Security master

| Field | Semantic definition | Type/unit | Req/crit | Temporal/revision | Missing behavior | License/use |
|---|---|---|---|---|---|---|
| company_id | Stable opaque legal-entity identity | string / none | R/C | Immutable; mergers append links | Quarantine | Identity storage/use |
| security_id | Stable opaque instrument identity | string / none | R/C | Immutable; conversions append links | Quarantine | Identity storage/use |
| listing_id | Stable opaque venue-listing identity | string / none | R/C | Immutable; listing lifecycle is effective-dated | Quarantine | Identity storage/use |
| ISIN | Effective-dated issued identifier | string / none | R/C | Vintage and effective interval | Quarantine/resolve | Identifier retention |
| nse_symbol | Venue trading symbol | string / none | R/C | Effective-dated; never key | Quarantine | NSE reference-data use |
| series | NSE trading series | string / none | R/C | Effective-dated | Quarantine | NSE reference-data use |
| legal_name | Issuer registered name | string / none | R/C | Effective-dated name history | Quarantine | Reference-data retention/use |
| display_name | Human-readable issuer name | string / none | O/M | Effective-dated | Warn | Display permission |
| listed_at | Listing start | UTC instant | R/C | Corrected by appended vintage | Quarantine | Historical listing use |
| delisted_at | Listing end | optional UTC instant | O/C when delisted | Appended/corrected vintage | Quarantine if delisting known | Delisted-history use |
| suspension_at | Suspension start | optional UTC instant | O/H | Effective-dated events | Quarantine affected sessions | Historical status use |
| security_type | Instrument kind | enum / none | R/C | Effective-dated | Quarantine | Reference-data use |
| currency | Trading currency | ISO 4217 string | R/C | Effective-dated | Quarantine | Reference-data use |
| face_value | Issued face value | decimal / currency per share | R/H | Effective-dated/action revised | Quarantine action-dependent use | Corporate-data use |
| sector | Taxonomy sector | string / none | O/H | Effective-dated taxonomy/version | Exclude affected method | Derived/display permission |
| industry | Taxonomy industry | string / none | O/H | Effective-dated taxonomy/version | Exclude affected method | Derived/display permission |

## Unadjusted EOD market data

| Field | Semantic definition | Type/unit | Req/crit | Temporal/revision | Missing behavior | License/use |
|---|---|---|---|---|---|---|
| listing_id | Stable venue listing identity | string | R/C | Session-effective vintage | Quarantine | EOD/history rights |
| session_date | Official venue session | date | R/C | Session-effective vintage | Quarantine | EOD/history rights |
| open | First eligible traded price | decimal / currency per share | R/C | Published/usable/revision times | Quarantine | Raw price retention/use |
| high | Highest eligible traded price | decimal / currency per share | R/C | Published/usable/revision times | Quarantine | Raw price retention/use |
| low | Lowest eligible traded price | decimal / currency per share | R/C | Published/usable/revision times | Quarantine | Raw price retention/use |
| close | Official raw closing price | decimal / currency per share | R/C | Published/usable/revision times | Quarantine | Raw price retention/use |
| volume | Traded share quantity | decimal / shares | R/H | Same vintage | Quarantine | Volume use |
| trade_count | Eligible trades | integer / trades | O/M | Same vintage | Warn | Trade-count use |
| turnover | Eligible traded value | decimal / currency | O/M | Same vintage | Warn | Turnover use |
| price basis | Must be `RAW` | enum | R/C | Immutable assertion | Reject adjusted input | Adjustment/derived rights |

## Corporate actions

| Field | Semantic definition | Type/unit | Req/crit | Temporal/revision | Missing behavior | License/use |
|---|---|---|---|---|---|---|
| action_id | Stable corporate event identity | string | R/C | Version chain | Quarantine | Action/history rights |
| action_type | Event semantic type | enum | R/C | Corrections append | Quarantine | Action/history rights |
| action_status | Confirmation/cancellation/conflict state | enum | R/C | Status changes append | Quarantine | Action/history rights |
| security_id | Affected instrument identity | string | R/C | Effective identity at event | Quarantine | Identity/linkage |
| action_listing_id | Affected listing when listing-scoped | string | Conditional/C | Effective identity at event | Quarantine | Identity/linkage |
| action_source_record_id | One competing source record | string | R/C, repeated | Source vintage retained | Quarantine | Evidence retention |
| announced_at | First evidenced announcement time | UTC instant | Conditional/C when announcement exists | Publication revisions retained | Quarantine when provider claims announcement coverage | Timestamp/history rights |
| ex_date | First ex-entitlement session | date | Conditional/C for entitlement actions | Terms revisions append | Quarantine applicable action | Action-history rights |
| record_date | Entitlement record date | date | Conditional/H | Terms revisions append | Warn or quarantine per action semantics | Action-history rights |
| payment_date | Cash/payment completion date | date | Conditional/H | Terms revisions append | Warn | Action-history rights |
| ratio_numerator | New/entitled units numerator | decimal / ratio | Conditional/C for ratio actions | Terms revisions append | Quarantine | Terms/derived adjustment |
| ratio_denominator | Existing units denominator | decimal / ratio | Conditional/C for ratio actions | Terms revisions append | Quarantine | Terms/derived adjustment |
| cash_amount | Cash entitlement per share | decimal / currency per share | Conditional/C for cash actions | Terms revisions append | Quarantine | Terms/derived adjustment |
| action_currency | Currency of cash terms | ISO 4217 string | Conditional/C for cash actions | Terms revisions append | Quarantine | Terms/derived adjustment |
| new_face_value | Post-action face value | decimal / currency per share | Conditional/C for face-value actions | Terms revisions append | Quarantine | Terms/derived adjustment |
| old_symbol | Pre-change venue symbol | string | Conditional/C for symbol change | Effective-dated | Quarantine | Reference history |
| new_symbol | Post-change venue symbol | string | Conditional/C for symbol change | Effective-dated | Quarantine | Reference history |

## Financial filings and facts

| Field | Semantic definition | Type/unit | Req/crit | Temporal/revision | Missing behavior | License/use |
|---|---|---|---|---|---|---|
| filing_id | Stable filing-vintage identity | string | R/C | Restatements append | Quarantine | Filing retention/use |
| filing_version_chain_id | Links filing revisions | string | R/C | Append-only chain | Quarantine | Filing retention/use |
| filing_company_id | Reporting legal entity | string | R/C | Effective identity | Quarantine | Filing identity use |
| period_id | Stable reporting-period identity | string | R/C | Corrected vintage | Quarantine | Financial-history use |
| period_start | Reporting period start | date | R/C | Corrected vintage | Quarantine | Financial-history use |
| period_end | Reporting period end | date | R/C | Corrected vintage | Quarantine | Financial-history use |
| period_kind | Quarter/half/year semantic | enum | R/C | Corrected vintage | Quarantine | Financial-history use |
| fiscal_year | Issuer fiscal-year label | integer/year | R/C | Corrected vintage | Quarantine | Financial-history use |
| reporting_scope | Consolidated or standalone | enum | R/C | Filing vintage | Quarantine | Filing metadata use |
| accounting_standard | Reported accounting basis | string | R/C | Filing vintage | Quarantine | Filing metadata use |
| audit_status | Audit/review status | enum | R/C | Filing vintage | Quarantine | Filing metadata use |
| metric | Atomic fact semantic | string | R/C | Fact version chain | Quarantine | Facts/derived rights |
| fact_value | Reported numeric value | decimal | R/C | Fact version chain | Quarantine; no imputation | Facts/derived rights |
| fact_unit | Reported unit | string | R/C | Fact version chain | Quarantine | Facts/derived rights |
| fact_currency | Fact currency | ISO 4217 string | Conditional/C | Fact version chain | Quarantine monetary facts | Facts/derived rights |
| fact_scale | Reported scale multiplier | decimal | R/C | Fact version chain | Quarantine | Facts/derived rights |
| filing_published_at | Public availability time | UTC instant | R/C | Corrections append | PIT quarantine | Exact timestamps/history |
| filing_accepted_at | Provider/exchange acceptance time | UTC instant | R/C | Immutable observation | PIT quarantine | Exact timestamps/history |

## Historical universe membership

| Field | Semantic definition | Type/unit | Req/crit | Temporal/revision | Missing behavior | License/use |
|---|---|---|---|---|---|---|
| index_id | Stable licensed index identity | string | R/C | Effective membership interval | Quarantine | Constituents/index-name rights |
| member_security_id | Constituent instrument | string | R/C | Effective membership interval | Quarantine | Historical constituent rights |
| membership_announced_at | Announcement availability | UTC instant | R/C | Corrections append | PIT quarantine | Historical constituent rights |
| membership_effective_at | Inclusion start | UTC instant | R/C | Corrections append | PIT quarantine | Historical constituent rights |
| membership_effective_until | Removal boundary | optional UTC instant | O/C when removed | Corrections append | PIT quarantine if removal known | Historical constituent rights |
| membership_reason | Inclusion/removal rationale | enum/string | O/M | Vintage | Warn | Index metadata use |
| constituent_weight | Published index weight | decimal/fraction | O/H | Effective/published vintage | Warn | Constituent-derived rights |
| constituent_shares | Published index shares | decimal/shares | O/H | Effective/published vintage | Warn | Constituent-derived rights |
| free_float_factor | Published investibility factor | decimal/fraction | O/H | Effective/published vintage | Warn | Constituent-derived rights |

## Benchmark total-return series

| Field | Semantic definition | Type/unit | Req/crit | Temporal/revision | Missing behavior | License/use |
|---|---|---|---|---|---|---|
| benchmark_id | Stable licensed TRI series | string | R/C | Series/version vintage | Quarantine | TRI/backtest/display rights |
| benchmark_session_date | Official index session | date | R/C | Session vintage | Quarantine | TRI/backtest/display rights |
| total-return level | Official level including reinvested distributions | decimal / index points | R/C | Published and revised vintages | Quarantine | TRI retention/use |
| benchmark_currency | Series currency | ISO 4217 string | R/H | Methodology version | Quarantine | Methodology/reference rights |
| benchmark_base_date | Series base date | date | R/H | Methodology version | Quarantine | Methodology/reference rights |
| benchmark_base_level | Series base value | decimal/index points | R/H | Methodology version | Quarantine | Methodology/reference rights |
| benchmark_methodology | Exact construction reference | string | R/C | Versioned; never overwrite | PIT quarantine | Methodology/citation rights |
| benchmark_methodology_version | Methodology version | string | R/C | Versioned; never overwrite | PIT quarantine | Methodology/citation rights |
| benchmark_published_at | Level availability time | UTC instant | R/C | Revisions append | PIT quarantine | Exact timestamp rights |

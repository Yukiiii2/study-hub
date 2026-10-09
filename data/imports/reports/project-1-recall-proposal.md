# Project 1 Recall topic mapping proposal

Workbook: `Project 1.xlsx`; SHA-256 `47679efde3b0bd0317cc7c9bd11589bc3a781289e5e13fb916117820ee7de01e`.

Read-only workbook inspection and read-only existing curriculum lookup. Card inserts/updates: **0**; review/history inserts/updates: **0**. No workbook edits, authenticated-owner assignment, source-history transfer, or commit mode.

## Exact mapping rules and counts

Inspected all 7 actual `* Recall` worksheets against 163 existing topics under active subjects. 155 of 156 source references have one exact existing match; 1 remain unresolved.

Use column A from row 3; map worksheet subject MS to MAS and retain the other approved subject codes. Normalize whitespace only. Case, punctuation and spelling remain significant. The subject plus normalized title must identify exactly one existing topic. No positional, fuzzy, case-insensitive, or cross-subject association is accepted.

| Sheet | Subject | Stored range | References | Literal titles | Mapped | Unresolved | Repeated titles |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| MS Recall | MAS | A1:Z19 | 17 | 17 | 17 | 0 | 0 |
| AT Recall | AT | A1:Z19 | 17 | 17 | 17 | 0 | 0 |
| AP Recall | AP | A1:Z22 | 20 | 20 | 19 | 1 | 0 |
| RFBT Recall | RFBT | A1:O23 | 21 | 21 | 21 | 0 | 0 |
| TAX Recall | TAX | A1:O26 | 24 | 24 | 24 | 0 | 0 |
| FAR Recall | FAR | A1:O46 | 43 | 43 | 43 | 0 | 0 |
| AFAR Recall | AFAR | A1:Z1000 | 14 | 14 | 14 | 0 | 0 |

## Source structure and aggregate cell types

A contains topic references. B is First Rep; C/D, E/F, G/H, I/J and K/L alternate R1–R5 with ratings. M is Next Rep; N is Final Rating; O is Remarks. Stored worksheet ranges may include formatting-only rows/columns. Counts below cover body cells from row 3, including blanks; they are cell-type counts, not review counts.

| Sheet | Column role | Blank | Numeric | Date/time | Text | Formula | Boolean | Error | Other |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MS Recall | B: First Rep | 16 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | C: R1 | 16 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | D: R1 rating | 16 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | E: R2 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | F: R2 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | G: R3 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | H: R3 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | I: R4 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | J: R4 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | K: R5 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | L: R5 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | M: Next Rep | 16 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| MS Recall | N: Final Rating | 16 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| MS Recall | O: Remarks | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MS Recall | Beyond O (aggregate) | 187 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | B: First Rep | 16 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | C: R1 | 16 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | D: R1 rating | 16 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | E: R2 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | F: R2 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | G: R3 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | H: R3 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | I: R4 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | J: R4 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | K: R5 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | L: R5 rating | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | M: Next Rep | 15 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| AT Recall | N: Final Rating | 15 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| AT Recall | O: Remarks | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AT Recall | Beyond O (aggregate) | 187 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | B: First Rep | 19 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | C: R1 | 19 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | D: R1 rating | 19 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | E: R2 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | F: R2 rating | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | G: R3 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | H: R3 rating | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | I: R4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | J: R4 rating | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | K: R5 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | L: R5 rating | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | M: Next Rep | 19 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| AP Recall | N: Final Rating | 19 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| AP Recall | O: Remarks | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP Recall | Beyond O (aggregate) | 220 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | B: First Rep | 20 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | C: R1 | 20 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | D: R1 rating | 20 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | E: R2 | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | F: R2 rating | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | G: R3 | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | H: R3 rating | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | I: R4 | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | J: R4 rating | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | K: R5 | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | L: R5 rating | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RFBT Recall | M: Next Rep | 19 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RFBT Recall | N: Final Rating | 19 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RFBT Recall | O: Remarks | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | B: First Rep | 23 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | C: R1 | 23 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | D: R1 rating | 23 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | E: R2 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | F: R2 rating | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | G: R3 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | H: R3 rating | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | I: R4 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | J: R4 rating | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | K: R5 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | L: R5 rating | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TAX Recall | M: Next Rep | 23 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| TAX Recall | N: Final Rating | 23 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| TAX Recall | O: Remarks | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | B: First Rep | 43 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | C: R1 | 43 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | D: R1 rating | 43 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | E: R2 | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | F: R2 rating | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | G: R3 | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | H: R3 rating | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | I: R4 | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | J: R4 rating | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | K: R5 | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | L: R5 rating | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FAR Recall | M: Next Rep | 43 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| FAR Recall | N: Final Rating | 43 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| FAR Recall | O: Remarks | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | B: First Rep | 997 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | C: R1 | 997 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | D: R1 rating | 997 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | E: R2 | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | F: R2 rating | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | G: R3 | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | H: R3 rating | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | I: R4 | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | J: R4 rating | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | K: R5 | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | L: R5 rating | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | M: Next Rep | 997 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| AFAR Recall | N: Final Rating | 997 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| AFAR Recall | O: Remarks | 998 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| AFAR Recall | Beyond O (aggregate) | 10978 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Formulas are identified only by stored cell type, never evaluated or printed. Numeric/date cells and repetition labels do not establish an algorithm, completed reviews, ratings, actual recall dates or readiness. The application scheduler is defined independently by the Phase 9 contract; this workbook does not configure it.

## Structural warnings

- RFBT Recall!A1: Topic header missing or different; column A is corroborated by the repetition layout.

## Unresolved source references

- `AP Recall!A6` (AP): Share-based Payments; no exact existing normalized title.

The Phase 4 report flagged `AP Recall!A6`; only an exact current match could resolve it. Any mismatch remains excluded from the proposal. No source title is corrected and no topic is invented.

For source-conflict context, existing curriculum `AP-04` is `Share-based Payment'`. This comparison does not create an accepted association.

## Accepted source locators and topic codes

| Source locator | Subject | Normalized source title | Existing topic code |
| --- | --- | --- | --- |
| MS Recall!A3 | MAS | Basic Considerations in MAS | MAS-01 |
| MS Recall!A4 | MAS | Variable and Absorption Costing | MAS-02 |
| MS Recall!A5 | MAS | Cost Volume Profit & Breakeven Point | MAS-03 |
| MS Recall!A6 | MAS | Financial Statement Analysis | MAS-04 |
| MS Recall!A7 | MAS | Budgeting | MAS-05 |
| MS Recall!A8 | MAS | Standard Cost Variances | MAS-06 |
| MS Recall!A9 | MAS | Performance Evaluation | MAS-07 |
| MS Recall!A10 | MAS | Pricing Decisions | MAS-08 |
| MS Recall!A11 | MAS | Relevant Costing | MAS-09 |
| MS Recall!A12 | MAS | Quantitative Techniques in Decision Making | MAS-10 |
| MS Recall!A13 | MAS | Financial Markets | MAS-11 |
| MS Recall!A14 | MAS | Working Capital Management | MAS-12 |
| MS Recall!A15 | MAS | Short-term Financing | MAS-13 |
| MS Recall!A16 | MAS | Long-term Financing | MAS-14 |
| MS Recall!A17 | MAS | Capital Budgeting | MAS-15 |
| MS Recall!A18 | MAS | Risk and Leverage | MAS-16 |
| MS Recall!A19 | MAS | Economics | MAS-17 |
| AT Recall!A3 | AT | Practice and Regulation of the Accountancy Profession | AT-01 |
| AT Recall!A4 | AT | Code of Ethics for Professional Accountants | AT-02 |
| AT Recall!A5 | AT | Fundamentals of Assurance Services | AT-03 |
| AT Recall!A6 | AT | Introduction to Auditing and Overview of the Audit Process | AT-04 |
| AT Recall!A7 | AT | Preliminary Engagement Activities | AT-05 |
| AT Recall!A8 | AT | Audit Planning | AT-06 |
| AT Recall!A9 | AT | Internal Control Consideration | AT-07 |
| AT Recall!A10 | AT | Auditing in an Information Technology Environment | AT-08 |
| AT Recall!A11 | AT | Transaction Cycles | AT-09 |
| AT Recall!A12 | AT | Consideration of Fraud, Error and Non-compliance | AT-10 |
| AT Recall!A13 | AT | Evidence and performance of substantive testing | AT-11 |
| AT Recall!A14 | AT | Approaches gathering evidence and Audit Sampling | AT-12 |
| AT Recall!A15 | AT | Completing The Audit | AT-13 |
| AT Recall!A16 | AT | Audit Documentation and Communication with those charged with governance | AT-14 |
| AT Recall!A17 | AT | System Quality Control | AT-15 |
| AT Recall!A18 | AT | Audit Reporting (General-Purpose Financial Statements) | AT-16 |
| AT Recall!A19 | AT | Other Reporting Responsibilities (Other Assurance Engagements and Other Audit-Related Services) | AT-17 |
| AP Recall!A3 | AP | Single Entry System | AP-01 |
| AP Recall!A4 | AP | Correction of Errors | AP-02 |
| AP Recall!A5 | AP | Shareholder's Equity | AP-03 |
| AP Recall!A7 | AP | Audit of Cash | AP-05 |
| AP Recall!A8 | AP | Receivables | AP-06 |
| AP Recall!A9 | AP | Inventories and Agriculture | AP-07 |
| AP Recall!A10 | AP | Investment in Equity Securities | AP-08 |
| AP Recall!A11 | AP | Investment in Debt Securities | AP-09 |
| AP Recall!A12 | AP | Notes and bonds payable | AP-10 |
| AP Recall!A13 | AP | Property, plant and equipment | AP-11 |
| AP Recall!A14 | AP | Intangible assets | AP-12 |
| AP Recall!A15 | AP | Investment Property | AP-13 |
| AP Recall!A16 | AP | Revaluation & Impairment | AP-14 |
| AP Recall!A17 | AP | Current Liabilities | AP-15 |
| AP Recall!A18 | AP | Accounting for Income Tax | AP-16 |
| AP Recall!A19 | AP | Employee Benefits | AP-17 |
| AP Recall!A20 | AP | Statement of Cash Flows | AP-18 |
| AP Recall!A21 | AP | Financial Statements | AP-19 |
| AP Recall!A22 | AP | Leases | AP-20 |
| RFBT Recall!A3 | RFBT | Law on Obligations | RFBT-01 |
| RFBT Recall!A4 | RFBT | Law on Contracts | RFBT-02 |
| RFBT Recall!A5 | RFBT | Law on Sales | RFBT-03 |
| RFBT Recall!A6 | RFBT | Law on Credit Transactions | RFBT-04 |
| RFBT Recall!A7 | RFBT | Anti-Bouncing Checks Law | RFBT-05 |
| RFBT Recall!A8 | RFBT | Consumer Protection & Lemon Law | RFBT-06 |
| RFBT Recall!A9 | RFBT | Financial Rehabilitation & Insolvency Act | RFBT-07 |
| RFBT Recall!A10 | RFBT | Philippine Competition Act | RFBT-08 |
| RFBT Recall!A11 | RFBT | Government Procurement Law | RFBT-09 |
| RFBT Recall!A12 | RFBT | Law on Partnership | RFBT-10 |
| RFBT Recall!A13 | RFBT | Law on Corporations | RFBT-11 |
| RFBT Recall!A14 | RFBT | Securities Regulation Code | RFBT-11a |
| RFBT Recall!A15 | RFBT | Insurance Law | RFBT-12 |
| RFBT Recall!A16 | RFBT | Law on Cooperatives | RFBT-13 |
| RFBT Recall!A17 | RFBT | Banking Laws | RFBT-14 |
| RFBT Recall!A18 | RFBT | Intellectual Property Law | RFBT-15 |
| RFBT Recall!A19 | RFBT | Data Privacy Act | RFBT-16 |
| RFBT Recall!A20 | RFBT | E-Commerce Act | RFBT-17 |
| RFBT Recall!A21 | RFBT | Ease of Doing Business Act | RFBT-18 |
| RFBT Recall!A22 | RFBT | Labor Law | RFBT-19 |
| RFBT Recall!A23 | RFBT | Social Security Law | RFBT-20 |
| TAX Recall!A3 | TAX | Principles of Taxation | TAX-01 |
| TAX Recall!A4 | TAX | Taxes, Laws and Administration | TAX-02 |
| TAX Recall!A5 | TAX | Fundamentals of Income Taxation | TAX-03 |
| TAX Recall!A6 | TAX | Final Income Taxation | TAX-04 |
| TAX Recall!A7 | TAX | Income Taxation –Final Withholding Tax Table | TAX-04.1 |
| TAX Recall!A8 | TAX | Capital Gains Taxation | TAX-05 |
| TAX Recall!A9 | TAX | Regular Income Taxation | TAX-06 |
| TAX Recall!A10 | TAX | Compensation Income | TAX-6.1 |
| TAX Recall!A11 | TAX | Fringe Benefits Tax | TAX-6.2 |
| TAX Recall!A12 | TAX | Dealings in Properties | TAX-6.3 |
| TAX Recall!A13 | TAX | Deductions from Gross Income | TAX-07 |
| TAX Recall!A14 | TAX | Itemized Deductions | TAX-7.1 |
| TAX Recall!A15 | TAX | Optional Standard Deduction | TAX-7.2 |
| TAX Recall!A16 | TAX | Individual Income Taxation | TAX-08 |
| TAX Recall!A17 | TAX | Coporate Income Tax Integ | TAX-09 |
| TAX Recall!A18 | TAX | Estate Taxation | TAX-10 |
| TAX Recall!A19 | TAX | Donor's Taxation | TAX-11 |
| TAX Recall!A20 | TAX | Introduction to Consumption Tax | TAX-12 |
| TAX Recall!A21 | TAX | VAT on importation | TAX-13 |
| TAX Recall!A22 | TAX | Business Taxation | TAX-14 |
| TAX Recall!A23 | TAX | Excise Tax & Documentary Stamp Tax | TAX-15 |
| TAX Recall!A24 | TAX | Tax Remedies | TAX-16 |
| TAX Recall!A25 | TAX | Local Taxation | TAX-17 |
| TAX Recall!A26 | TAX | Preferential Taxation | TAX-18 |
| FAR Recall!A3 | FAR | Introduction to Accountancy and Preface to PFRS | FAR-01 |
| FAR Recall!A4 | FAR | Conceptual Framework for Financial Reporting | FAR-02 |
| FAR Recall!A5 | FAR | Cash and Cash Equivalents | FAR-03 |
| FAR Recall!A6 | FAR | Receivables | FAR-04 |
| FAR Recall!A7 | FAR | Inventories | FAR-05 |
| FAR Recall!A8 | FAR | Biological Assets | FAR-06 |
| FAR Recall!A9 | FAR | Property Plant and Equipment - Part 1 | FAR-07 |
| FAR Recall!A10 | FAR | Property Plant and Equipment - Part 2 | FAR-08 |
| FAR Recall!A11 | FAR | Government Grants | FAR-09 |
| FAR Recall!A12 | FAR | Borrowing Costs | FAR-10 |
| FAR Recall!A13 | FAR | Depletion of Mineral Resources | FAR-11 |
| FAR Recall!A14 | FAR | Intangible Assets | FAR-12 |
| FAR Recall!A15 | FAR | Impairment of Assets | FAR-13 |
| FAR Recall!A16 | FAR | Investment in Equity Securities | FAR-14 |
| FAR Recall!A17 | FAR | Investments in Associates | FAR-15 |
| FAR Recall!A18 | FAR | Investments in Debt Securities | FAR-16 |
| FAR Recall!A19 | FAR | Investment Properties | FAR-17 |
| FAR Recall!A20 | FAR | Fund and Other Investments | FAR-18 |
| FAR Recall!A21 | FAR | Current Liabilities | FAR-20 |
| FAR Recall!A22 | FAR | Notes Payable | FAR-21 |
| FAR Recall!A23 | FAR | Bonds Payable | FAR-22 |
| FAR Recall!A24 | FAR | Compound Financial Instruments | FAR-23 |
| FAR Recall!A25 | FAR | Provisions | FAR-24 |
| FAR Recall!A26 | FAR | Employee Benefits | FAR-25 |
| FAR Recall!A27 | FAR | Income Taxes | FAR-26 |
| FAR Recall!A28 | FAR | Leases | FAR-27 |
| FAR Recall!A29 | FAR | Shareholders' Equity Part 1 | FAR-28 |
| FAR Recall!A30 | FAR | Shareholders' Equity Part 2 | FAR-29 |
| FAR Recall!A31 | FAR | Share-based payments | FAR-30 |
| FAR Recall!A32 | FAR | Book Value per Share | FAR-31 |
| FAR Recall!A33 | FAR | Earnings per Share | FAR-32 |
| FAR Recall!A34 | FAR | Financial Statements Part 1 | FAR-33 |
| FAR Recall!A35 | FAR | Financial Statements Part 2 | FAR-34 |
| FAR Recall!A36 | FAR | Statement of Cash Flows | FAR-35 |
| FAR Recall!A37 | FAR | Operating Segments | FAR-37 |
| FAR Recall!A38 | FAR | Non Current Assets Held For Sale and Discontinued Operations | FAR-38 |
| FAR Recall!A39 | FAR | Events after Reporting Period | FAR-39 |
| FAR Recall!A40 | FAR | Related Parties | FAR-40 |
| FAR Recall!A41 | FAR | Interim Financial Reporting | FAR-41 |
| FAR Recall!A42 | FAR | Accounting Changes and Error Correction | FAR-42 |
| FAR Recall!A43 | FAR | Cash to Acrrual Basis | FAR-43 |
| FAR Recall!A44 | FAR | Accounting Process | FAR-44 |
| FAR Recall!A45 | FAR | SMEs | FAR-45 |
| AFAR Recall!A3 | AFAR | Partnership | AFAR-01 |
| AFAR Recall!A4 | AFAR | Corporate Liquidation | AFAR-02 |
| AFAR Recall!A5 | AFAR | Revenue Recognition | AFAR-03 |
| AFAR Recall!A6 | AFAR | Decentralized Operation | AFAR-04 |
| AFAR Recall!A7 | AFAR | Business Combination | AFAR-05 |
| AFAR Recall!A8 | AFAR | Separate and Consolidated FS | AFAR-06 |
| AFAR Recall!A9 | AFAR | Joint Arrangement | AFAR-07 |
| AFAR Recall!A10 | AFAR | Forex and hyperinflation | AFAR-08 |
| AFAR Recall!A11 | AFAR | Derivatives and Hedge Accounting | AFAR-09 |
| AFAR Recall!A12 | AFAR | NPO | AFAR-10 |
| AFAR Recall!A13 | AFAR | Government Accounting | AFAR-11 |
| AFAR Recall!A14 | AFAR | Cost Accounting | AFAR-12 |
| AFAR Recall!A15 | AFAR | Insurance Contracts | AFAR-13 |
| AFAR Recall!A16 | AFAR | Service Concession Arrangement | AFAR-14 |

## Phase 9 decision and privacy

This is a topic-association proposal only. The Recall sheets do not supply authored front/back pairs. Do not create cards from topic titles or reinterpret R1–R5 as application reviews. Users author cards explicitly; new cards follow the separately approved server scheduler. Resolving a source title mismatch permits a topic reference, not card or history creation.

Personal repetition values, ratings, dates, remarks, raw formulas, private UUIDs and credentials are omitted. The source workbook remains local and ignored. No database writes are supported.

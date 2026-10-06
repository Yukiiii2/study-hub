# Project 1 curriculum migration result

Workbook: `Project 1.xlsx`; SHA-256: `47679efde3b0bd0317cc7c9bd11589bc3a781289e5e13fb916117820ee7de01e`.

Mode: transactional insert; post-write validation passed

Proposed inserts: 163; updates: 0; unchanged: 0; critical errors: 0.
Inserted: 163; matching topics verified: 163.

## Sheets detected

| Sheet | Stored extent | Formula cells | Merges |
| --- | --- | ---: | ---: |
| SCHEDULE | A1:V89 | 158 | 540 |
| Calendar | A1:Z1015 | 0 | 13 |
| Progress Overview | A1:M37 | 48 | 7 |
| ASSESSMENTS | A1:N1000 | 127 | 5 |
| MS | A1:T22 | 49 | 11 |
| MS Vids | A1:E1004 | 1 | 0 |
| MS Recall | A1:Z19 | 2 | 6 |
| MS Code | A1:D22 | 37 | 1 |
| AT | A1:T21 | 48 | 11 |
| AT Vids | A1:E999 | 1 | 0 |
| AT Recall | A1:Z19 | 4 | 6 |
| AP | A1:T24 | 54 | 11 |
| AT Code | A1:D21 | 35 | 1 |
| AP Vids | A1:E998 | 1 | 0 |
| AP Recall | A1:Z22 | 2 | 6 |
| AP Code | A1:D24 | 41 | 1 |
| RFBT | A1:T27 | 55 | 11 |
| RFBT Vids | A1:E997 | 1 | 0 |
| RFBT Recall | A1:O23 | 4 | 6 |
| RFBT Code | A1:D27 | 47 | 1 |
| TAX | A1:T31 | 65 | 11 |
| TAX Vids | A1:E998 | 1 | 0 |
| TAX Recall | A1:O26 | 2 | 6 |
| FAR | A1:T49 | 99 | 11 |
| TAX Code | A1:D31 | 55 | 1 |
| FAR Vids | A1:G995 | 1 | 0 |
| FAR Recall | A1:O46 | 2 | 6 |
| FAR Code | A1:D49 | 91 | 1 |
| AFAR | A1:T19 | 44 | 11 |
| AFAR Vids | A1:E1000 | 1 | 0 |
| AFAR Recall | A1:Z1000 | 2 | 6 |
| AFAR Code | A1:D18 | 31 | 1 |

Stored extents include formatting-only cells. Formula values/errors are never curriculum input. Header merges are not hierarchy evidence.

## Subject mapping and counts

| Sheet | Subject | Candidates | Accepted | Skipped |
| --- | --- | ---: | ---: | ---: |
| MS | MAS | 18 | 18 | 4 |
| AT | AT | 17 | 17 | 4 |
| AP | AP | 20 | 20 | 4 |
| RFBT | RFBT | 23 | 23 | 4 |
| TAX | TAX | 27 | 27 | 4 |
| FAR | FAR | 45 | 43 | 6 |
| AFAR | AFAR | 15 | 15 | 4 |

## Rules

Literal B/C fields after row 3, verified against Code sheets; whitespace normalization only. Source row number is display_order. No descriptions are inferred from progress checkboxes. All parent_topic_id values are null; dotted/letter suffixes remain flat because explicit relationships are absent.

Exact subject + source code identifies a topic. UUIDv5 uses NAMESPACE_URL and study-hub/project-1/curriculum/v1/{subject UUID}/{code}. Existing differences in title, code case/spacing, description, parent, or order block import. No updates, deletes, subject writes, or schema changes. Table locks and a matching source/mapping/database plan fingerprint prevent stale approvals and concurrent duplicate insertion.

## Warnings, ambiguities, duplicates, and errors

- MS Code!A1 has a misleading heading; explicit sheet/code mapping is used.
- Excluded FAR!B22 (FAR-19): missing title.
- Excluded FAR!B39 (FAR-36): missing title.
- No explicit parent links or title indentation: all curriculum topics remain flat, including dotted/letter-suffixed codes.
- Source duplicates: 0; incomplete/ambiguous rows: 2.

## Skipped source rows

- MS!1: header/label
- MS!2: header/label (HO#)
- MS!3: header/label
- MS!22: blank curriculum fields
- AT!1: header/label
- AT!2: header/label (HO#)
- AT!3: header/label
- AT!21: blank curriculum fields
- AP!1: header/label
- AP!2: header/label (HO#)
- AP!3: header/label
- AP!24: blank curriculum fields
- RFBT!1: header/label
- RFBT!2: header/label (HO#)
- RFBT!3: header/label
- RFBT!27: blank curriculum fields
- TAX!1: header/label
- TAX!2: header/label (HO#)
- TAX!3: header/label
- TAX!31: blank curriculum fields
- FAR!1: header/label
- FAR!2: header/label (HO#)
- FAR!3: header/label
- FAR!22: code without usable title (FAR-19)
- FAR!39: code without usable title (FAR-36)
- FAR!49: blank curriculum fields
- AFAR!1: header/label
- AFAR!2: header/label (HO#)
- AFAR!3: header/label
- AFAR!19: blank curriculum fields

## Accepted topic traceability

| Subject | Source | Code | Title | Parent |
| --- | --- | --- | --- | --- |
| MAS | MS!B4:C4 | MAS-01 | Basic Considerations in MAS | none |
| MAS | MS!B5:C5 | MAS-02 | Variable and Absorption Costing | none |
| MAS | MS!B6:C6 | MAS-03 | Cost Volume Profit & Breakeven Point | none |
| MAS | MS!B7:C7 | MAS-04 | Financial Statement Analysis | none |
| MAS | MS!B8:C8 | MAS-05 | Budgeting | none |
| MAS | MS!B9:C9 | MAS-06 | Standard Cost Variances | none |
| MAS | MS!B10:C10 | MAS-07 | Performance Evaluation | none |
| MAS | MS!B11:C11 | MAS-08 | Pricing Decisions | none |
| MAS | MS!B12:C12 | MAS-09 | Relevant Costing | none |
| MAS | MS!B13:C13 | MAS-10 | Quantitative Techniques in Decision Making | none |
| MAS | MS!B14:C14 | MAS-11 | Financial Markets | none |
| MAS | MS!B15:C15 | MAS-12 | Working Capital Management | none |
| MAS | MS!B16:C16 | MAS-13 | Short-term Financing | none |
| MAS | MS!B17:C17 | MAS-14 | Long-term Financing | none |
| MAS | MS!B18:C18 | MAS-15 | Capital Budgeting | none |
| MAS | MS!B19:C19 | MAS-16 | Risk and Leverage | none |
| MAS | MS!B20:C20 | MAS-17 | Economics | none |
| MAS | MS!B21:C21 | MAS-18 | Strategic Costing | none |
| AT | AT!B4:C4 | AT-01 | Practice and Regulation of the Accountancy Profession | none |
| AT | AT!B5:C5 | AT-02 | Code of Ethics for Professional Accountants | none |
| AT | AT!B6:C6 | AT-03 | Fundamentals of Assurance Services | none |
| AT | AT!B7:C7 | AT-04 | Introduction to Auditing and Overview of the Audit Process | none |
| AT | AT!B8:C8 | AT-05 | Preliminary Engagement Activities | none |
| AT | AT!B9:C9 | AT-06 | Audit Planning | none |
| AT | AT!B10:C10 | AT-07 | Internal Control Consideration | none |
| AT | AT!B11:C11 | AT-08 | Auditing in an Information Technology Environment | none |
| AT | AT!B12:C12 | AT-09 | Transaction Cycles | none |
| AT | AT!B13:C13 | AT-10 | Consideration of Fraud, Error and Non-compliance | none |
| AT | AT!B14:C14 | AT-11 | Evidence and performance of substantive testing | none |
| AT | AT!B15:C15 | AT-12 | Approaches gathering evidence and Audit Sampling | none |
| AT | AT!B16:C16 | AT-13 | Completing The Audit | none |
| AT | AT!B17:C17 | AT-14 | Audit Documentation and Communication with those charged with governance | none |
| AT | AT!B18:C18 | AT-15 | System Quality Control | none |
| AT | AT!B19:C19 | AT-16 | Audit Reporting (General-Purpose Financial Statements) | none |
| AT | AT!B20:C20 | AT-17 | Other Reporting Responsibilities (Other Assurance Engagements and Other Audit-Related Services) | none |
| AP | AP!B4:C4 | AP-01 | Single Entry System | none |
| AP | AP!B5:C5 | AP-02 | Correction of Errors | none |
| AP | AP!B6:C6 | AP-03 | Shareholder's Equity | none |
| AP | AP!B7:C7 | AP-04 | Share-based Payment' | none |
| AP | AP!B8:C8 | AP-05 | Audit of Cash | none |
| AP | AP!B9:C9 | AP-06 | Receivables | none |
| AP | AP!B10:C10 | AP-07 | Inventories and Agriculture | none |
| AP | AP!B11:C11 | AP-08 | Investment in Equity Securities | none |
| AP | AP!B12:C12 | AP-09 | Investment in Debt Securities | none |
| AP | AP!B13:C13 | AP-10 | Notes and bonds payable | none |
| AP | AP!B14:C14 | AP-11 | Property, plant and equipment | none |
| AP | AP!B15:C15 | AP-12 | Intangible assets | none |
| AP | AP!B16:C16 | AP-13 | Investment Property | none |
| AP | AP!B17:C17 | AP-14 | Revaluation & Impairment | none |
| AP | AP!B18:C18 | AP-15 | Current Liabilities | none |
| AP | AP!B19:C19 | AP-16 | Accounting for Income Tax | none |
| AP | AP!B20:C20 | AP-17 | Employee Benefits | none |
| AP | AP!B21:C21 | AP-18 | Statement of Cash Flows | none |
| AP | AP!B22:C22 | AP-19 | Financial Statements | none |
| AP | AP!B23:C23 | AP-20 | Leases | none |
| RFBT | RFBT!B4:C4 | RFBT-01 | Law on Obligations | none |
| RFBT | RFBT!B5:C5 | RFBT-02 | Law on Contracts | none |
| RFBT | RFBT!B6:C6 | RFBT-03 | Law on Sales | none |
| RFBT | RFBT!B7:C7 | RFBT-04 | Law on Credit Transactions | none |
| RFBT | RFBT!B8:C8 | RFBT-05 | Anti-Bouncing Checks Law | none |
| RFBT | RFBT!B9:C9 | RFBT-06 | Consumer Protection & Lemon Law | none |
| RFBT | RFBT!B10:C10 | RFBT-07 | Financial Rehabilitation & Insolvency Act | none |
| RFBT | RFBT!B11:C11 | RFBT-08 | Philippine Competition Act | none |
| RFBT | RFBT!B12:C12 | RFBT-09 | Government Procurement Law | none |
| RFBT | RFBT!B13:C13 | RFBT-10 | Law on Partnership | none |
| RFBT | RFBT!B14:C14 | RFBT-11 | Law on Corporations | none |
| RFBT | RFBT!B15:C15 | RFBT-11a | Securities Regulation Code | none |
| RFBT | RFBT!B16:C16 | RFBT-12 | Insurance Law | none |
| RFBT | RFBT!B17:C17 | RFBT-13 | Law on Cooperatives | none |
| RFBT | RFBT!B18:C18 | RFBT-14 | Banking Laws | none |
| RFBT | RFBT!B19:C19 | RFBT-15 | Intellectual Property Law | none |
| RFBT | RFBT!B20:C20 | RFBT-16 | Data Privacy Act | none |
| RFBT | RFBT!B21:C21 | RFBT-17 | E-Commerce Act | none |
| RFBT | RFBT!B22:C22 | RFBT-18 | Ease of Doing Business Act | none |
| RFBT | RFBT!B23:C23 | RFBT-19 | Labor Law | none |
| RFBT | RFBT!B24:C24 | RFBT-19A | Labor Law - Additional Pay | none |
| RFBT | RFBT!B25:C25 | RFBT-20 | Social Security Law | none |
| RFBT | RFBT!B26:C26 | RFBT-20A | Summary of Benefits, Problems & Contributions Schedule | none |
| TAX | TAX!B4:C4 | TAX-00 | CREATE Law Updates | none |
| TAX | TAX!B5:C5 | TAX-01 | Principles of Taxation | none |
| TAX | TAX!B6:C6 | TAX-02 | Taxes, Laws and Administration | none |
| TAX | TAX!B7:C7 | TAX-03 | Fundamentals of Income Taxation | none |
| TAX | TAX!B8:C8 | TAX-04 | Final Income Taxation | none |
| TAX | TAX!B9:C9 | TAX-04.1 | Income Taxation –Final Withholding Tax Table | none |
| TAX | TAX!B10:C10 | TAX-05 | Capital Gains Taxation | none |
| TAX | TAX!B11:C11 | TAX-06 | Regular Income Taxation | none |
| TAX | TAX!B12:C12 | TAX-6.1 | Compensation Income | none |
| TAX | TAX!B13:C13 | TAX-6.2 | Fringe Benefits Tax | none |
| TAX | TAX!B14:C14 | TAX-6.3 | Dealings in Properties | none |
| TAX | TAX!B15:C15 | TAX-07 | Deductions from Gross Income | none |
| TAX | TAX!B16:C16 | TAX-7.1 | Itemized Deductions | none |
| TAX | TAX!B17:C17 | TAX-7.2 | Optional Standard Deduction | none |
| TAX | TAX!B18:C18 | TAX-08 | Individual Income Taxation | none |
| TAX | TAX!B19:C19 | TAX-09 | Coporate Income Tax Integ | none |
| TAX | TAX!B20:C20 | TAX-10 | Estate Taxation | none |
| TAX | TAX!B21:C21 | TAX-11 | Donor's Taxation | none |
| TAX | TAX!B22:C22 | TAX-12 | Introduction to Consumption Tax | none |
| TAX | TAX!B23:C23 | TAX-13 | VAT on importation | none |
| TAX | TAX!B24:C24 | TAX-14 | Business Taxation | none |
| TAX | TAX!B25:C25 | TAX-14.1 | Specific Percentage Tax | none |
| TAX | TAX!B26:C26 | TAX-14.2 | Value Added Tax | none |
| TAX | TAX!B27:C27 | TAX-15 | Excise Tax & Documentary Stamp Tax | none |
| TAX | TAX!B28:C28 | TAX-16 | Tax Remedies | none |
| TAX | TAX!B29:C29 | TAX-17 | Local Taxation | none |
| TAX | TAX!B30:C30 | TAX-18 | Preferential Taxation | none |
| FAR | FAR!B4:C4 | FAR-01 | Introduction to Accountancy and Preface to PFRS | none |
| FAR | FAR!B5:C5 | FAR-02 | Conceptual Framework for Financial Reporting | none |
| FAR | FAR!B6:C6 | FAR-03 | Cash and Cash Equivalents | none |
| FAR | FAR!B7:C7 | FAR-04 | Receivables | none |
| FAR | FAR!B8:C8 | FAR-05 | Inventories | none |
| FAR | FAR!B9:C9 | FAR-06 | Biological Assets | none |
| FAR | FAR!B10:C10 | FAR-07 | Property Plant and Equipment - Part 1 | none |
| FAR | FAR!B11:C11 | FAR-08 | Property Plant and Equipment - Part 2 | none |
| FAR | FAR!B12:C12 | FAR-09 | Government Grants | none |
| FAR | FAR!B13:C13 | FAR-10 | Borrowing Costs | none |
| FAR | FAR!B14:C14 | FAR-11 | Depletion of Mineral Resources | none |
| FAR | FAR!B15:C15 | FAR-12 | Intangible Assets | none |
| FAR | FAR!B16:C16 | FAR-13 | Impairment of Assets | none |
| FAR | FAR!B17:C17 | FAR-14 | Investment in Equity Securities | none |
| FAR | FAR!B18:C18 | FAR-15 | Investments in Associates | none |
| FAR | FAR!B19:C19 | FAR-16 | Investments in Debt Securities | none |
| FAR | FAR!B20:C20 | FAR-17 | Investment Properties | none |
| FAR | FAR!B21:C21 | FAR-18 | Fund and Other Investments | none |
| FAR | FAR!B23:C23 | FAR-20 | Current Liabilities | none |
| FAR | FAR!B24:C24 | FAR-21 | Notes Payable | none |
| FAR | FAR!B25:C25 | FAR-22 | Bonds Payable | none |
| FAR | FAR!B26:C26 | FAR-23 | Compound Financial Instruments | none |
| FAR | FAR!B27:C27 | FAR-24 | Provisions | none |
| FAR | FAR!B28:C28 | FAR-25 | Employee Benefits | none |
| FAR | FAR!B29:C29 | FAR-26 | Income Taxes | none |
| FAR | FAR!B30:C30 | FAR-27 | Leases | none |
| FAR | FAR!B31:C31 | FAR-28 | Shareholders' Equity Part 1 | none |
| FAR | FAR!B32:C32 | FAR-29 | Shareholders' Equity Part 2 | none |
| FAR | FAR!B33:C33 | FAR-30 | Share-based payments | none |
| FAR | FAR!B34:C34 | FAR-31 | Book Value per Share | none |
| FAR | FAR!B35:C35 | FAR-32 | Earnings per Share | none |
| FAR | FAR!B36:C36 | FAR-33 | Financial Statements Part 1 | none |
| FAR | FAR!B37:C37 | FAR-34 | Financial Statements Part 2 | none |
| FAR | FAR!B38:C38 | FAR-35 | Statement of Cash Flows | none |
| FAR | FAR!B40:C40 | FAR-37 | Operating Segments | none |
| FAR | FAR!B41:C41 | FAR-38 | Non Current Assets Held For Sale and Discontinued Operations | none |
| FAR | FAR!B42:C42 | FAR-39 | Events after Reporting Period | none |
| FAR | FAR!B43:C43 | FAR-40 | Related Parties | none |
| FAR | FAR!B44:C44 | FAR-41 | Interim Financial Reporting | none |
| FAR | FAR!B45:C45 | FAR-42 | Accounting Changes and Error Correction | none |
| FAR | FAR!B46:C46 | FAR-43 | Cash to Acrrual Basis | none |
| FAR | FAR!B47:C47 | FAR-44 | Accounting Process | none |
| FAR | FAR!B48:C48 | FAR-45 | SMEs | none |
| AFAR | AFAR!B4:C4 | AFAR-00 | Introduction to AFAR | none |
| AFAR | AFAR!B5:C5 | AFAR-01 | Partnership | none |
| AFAR | AFAR!B6:C6 | AFAR-02 | Corporate Liquidation | none |
| AFAR | AFAR!B7:C7 | AFAR-03 | Revenue Recognition | none |
| AFAR | AFAR!B8:C8 | AFAR-04 | Decentralized Operation | none |
| AFAR | AFAR!B9:C9 | AFAR-05 | Business Combination | none |
| AFAR | AFAR!B10:C10 | AFAR-06 | Separate and Consolidated FS | none |
| AFAR | AFAR!B11:C11 | AFAR-07 | Joint Arrangement | none |
| AFAR | AFAR!B12:C12 | AFAR-08 | Forex and hyperinflation | none |
| AFAR | AFAR!B13:C13 | AFAR-09 | Derivatives and Hedge Accounting | none |
| AFAR | AFAR!B14:C14 | AFAR-10 | NPO | none |
| AFAR | AFAR!B15:C15 | AFAR-11 | Government Accounting | none |
| AFAR | AFAR!B16:C16 | AFAR-12 | Cost Accounting | none |
| AFAR | AFAR!B17:C17 | AFAR-13 | Insurance Contracts | none |
| AFAR | AFAR!B18:C18 | AFAR-14 | Service Concession Arrangement | none |

## Deferred video mapping

No video table exists; zero video writes. A is source topic code, B lecture title, C duration. D (and FAR E/F) contains personal progress and is excluded. Blank-code headers and Total Time rows are not lecture candidates. Duration types/formats are preserved without guessing units or converting to seconds.

| Subject | Coded lectures | Exact topic-code matches | Invalid literal durations |
| --- | ---: | ---: | ---: |
| MAS | 155 | 155 | 0 |
| AT | 108 | 108 | 0 |
| AP | 325 | 325 | 0 |
| RFBT | 107 | 105 | 0 |
| TAX | 200 | 200 | 1 |
| FAR | 484 | 484 | 0 |
| AFAR | 185 | 185 | 0 |

- Review RFBT Vids!98: topic code RFBT-11A; exact match False; literal duration valid True.
- Review RFBT Vids!99: topic code RFBT-11A; exact match False; literal duration valid True.
- Review TAX Vids!64: topic code TAX-05; exact match True; literal duration valid False.

## Deferred recall mapping

A topic; B First Rep; C/D through K/L alternate R1–R5 and ratings; M Next Rep; N Final Rating; O Remarks. Numeric repetition values and formulas do not establish an algorithm. Personal history/ratings/remarks are not copied. Exact whitespace-normalized title matching only.

| Subject | References | Exact title matches |
| --- | ---: | ---: |
| MAS | 17 | 17 |
| AT | 17 | 17 |
| AP | 20 | 19 |
| RFBT | 21 | 21 |
| TAX | 24 | 24 |
| FAR | 43 | 43 |
| AFAR | 14 | 14 |

- Unresolved title: AP Recall!A6.

## Deferred schedule and calendar mapping

SCHEDULE row 4 subject / row 5 weekday columns: C RFBT, F AFAR, I AT/AUD, L MAS, O TAX, R FAR, U recall/backlogs/rest. I cannot be split between AT and AP without review. Date rows, helpers, literal tasks, and formula labels require separate mapping; formulas are not event titles. Calendar needs month-header plus day-grid context. Private dates/reminders/events are not copied into this safe report. No schedule/calendar tables or writes.

## Deferred assessments

Merged section labels supply names; row 1 columns B/D/F/H/J/L/N map FAR/AFAR/MAS/TAX/RFBT/AT/AP. Adjacent helper/progress columns are excluded. No assessment dates or coverage relationships are invented. No assessment table or writes.

| Section | Literal coverage entries | Exact unique topic matches |
| --- | ---: | ---: |
| 1ST MONTLY ASSESSMENT | 26 | 13 |
| 2ND MONTLY ASSESSMENT | 30 | 15 |
| 3RD MONTLY ASSESSMENT | 29 | 12 |
| 4TH MONTLY ASSESSMENT | 31 | 18 |
| 5TH MONTLY ASSESSMENT | 32 | 15 |

Normalized curriculum-only auxiliary candidates (video titles/duration representations, recall topic references, and assessment coverage cells) are in the adjacent .source-plan.json file. Personal progress/history/events/remarks and credentials are excluded. The personal workbook remains local and ignored.

## Independent post-migration verification

- Database counts: FAR 43, AFAR 15, MAS 18, TAX 27, RFBT 23, AT 17, AP 20 (163 total).
- No duplicate codes, orphan/cross-subject parents, or cycles. All imported parents remain null. Source display orders are unique within each subject and returned in order. Excluded FAR-19/FAR-36 remain absent.
- Public tables remain profiles, subjects, topics, and alembic_version; no deferred domain tables were created.
- Real Supabase authentication and FastAPI ASGI endpoint checks passed for GET /api/subjects and each subject detail/topic list. A real topic detail passed for each of the seven subjects; missing bearer tokens were rejected with 401. No tokens or credentials were saved to reports.
- The existing frontend hierarchy function consumed all 163 real API records without duplicates or loops. Longest title: 95 characters; existing wrapping rules remain unchanged. HTTP smoke checks passed for /subjects and a subject detail route, both rendering the existing session gate. Browser interaction was not automated; no frontend code changed.
- Independent second dry run: 0 inserts, 0 updates, 163 unchanged, 0 errors. See project-1-second-dry-run.md.

# Project 1 video dry run

Workbook: `Project 1.xlsx`; SHA-256 `47679efde3b0bd0317cc7c9bd11589bc3a781289e5e13fb916117820ee7de01e`.

Mode: read-only; zero database writes

Proposed inserts: 1562; updates: 0; unchanged: 0; critical errors: 0.

## Sheets, mapping, and counts

| Sheet | Subject | Candidates | Accepted | Excluded conflicts | Invalid durations |
| --- | --- | ---: | ---: | ---: | ---: |
| MS Vids | MAS | 155 | 155 | 0 | 0 |
| AT Vids | AT | 108 | 108 | 0 | 0 |
| AP Vids | AP | 325 | 325 | 0 | 0 |
| RFBT Vids | RFBT | 107 | 107 | 0 | 0 |
| TAX Vids | TAX | 200 | 200 | 0 | 0 |
| FAR Vids | FAR | 484 | 482 | 2 | 0 |
| AFAR Vids | AFAR | 185 | 185 | 0 | 0 |

Accepted: 1562; mapped: 1562; unmapped/ambiguous topic mappings: 0; invalid titles: 0; unexpected duplicate source titles: 0.

## Extraction, identity, and durations

A literal topic code, B literal lecture title, C duration; uncoded section/total rows and formatting blanks are not videos. MS maps to MAS. Exact existing topic codes are required, with the reviewed RFBT-11A -> RFBT-11a alias at rows 98–99. No topic or title is invented. All real Phase 4 topics are checked before video planning.

source_code is an import locator (project-1:worksheet:row), not a new curriculum/lecture code. Topic UUID plus that locator determines UUIDv5. Existing exact matches retain their IDs. Changed fields, relocated identities/titles, duplicate locators/titles, or missing topics block writes; no updates, deletes, or merges. Source/mapping/database fingerprints are rechecked under locks inside the insert transaction. display_order is the original worksheet row.

Confirmed display semantics: h:mm values encode MM:SS; [h]:mm:ss values with zero final stored seconds encode elapsed MM:SS (e.g. stored 57:27:00 -> lecture 57:27). h:mm:ss encodes real HH:MM:SS. Raw XML serials preserve elapsed hours before reader conversion; they reconstruct the confirmed display semantics, never literal time-of-day durations. Numeric rounding tolerance is 0.01 stored seconds. Unrecognized/negative/formula/error durations are never guessed. Explicit confirmed source corrections: FAR C294 23.59 -> 23:59, FAR C295 24.46 -> 24:46, TAX C64 27:08: -> 27:08; corrections require exact original values.

## Unresolved source-data conflicts

FAR Vids rows 586–587 both say **42-04 Exercise 2**, referencing FAR-42, but durations differ (48:23 and 48:22). Both excluded by client approval. They require client/source clarification. Neither renamed, merged, nor assigned an invented distinguishing title.

## Errors, unmapped rows, invalid durations

None; approved two-row exclusion remains unresolved and is not an import candidate.

## Skipped labels

- MS Vids!2: 1 Basic Considerations in MAS; uncoded section/total label; not a lecture.
- MS Vids!10: Total Time; uncoded section/total label; not a lecture.
- MS Vids!12: 2 Variable and Absorption Costing; uncoded section/total label; not a lecture.
- MS Vids!22: Total Time; uncoded section/total label; not a lecture.
- MS Vids!24: 3 CVP-BEP; uncoded section/total label; not a lecture.
- MS Vids!37: Total Time; uncoded section/total label; not a lecture.
- MS Vids!39: 4 Financial Statement Analysis; uncoded section/total label; not a lecture.
- MS Vids!54: Total Time; uncoded section/total label; not a lecture.
- MS Vids!56: 5 Budgeting; uncoded section/total label; not a lecture.
- MS Vids!62: Total Time; uncoded section/total label; not a lecture.
- MS Vids!64: 6 Standard Cost Variance Analysis; uncoded section/total label; not a lecture.
- MS Vids!75: Total Time; uncoded section/total label; not a lecture.
- MS Vids!77: 7 Performance Evaluation; uncoded section/total label; not a lecture.
- MS Vids!90: Total Time; uncoded section/total label; not a lecture.
- MS Vids!92: 8 Pricing; uncoded section/total label; not a lecture.
- MS Vids!103: Total Time; uncoded section/total label; not a lecture.
- MS Vids!105: 9 Relevant Costing; uncoded section/total label; not a lecture.
- MS Vids!117: Total Time; uncoded section/total label; not a lecture.
- MS Vids!119: 10 Quantitative Techniques; uncoded section/total label; not a lecture.
- MS Vids!128: Total Time; uncoded section/total label; not a lecture.
- MS Vids!130: 11 Financial Markets; uncoded section/total label; not a lecture.
- MS Vids!137: Total Time; uncoded section/total label; not a lecture.
- MS Vids!139: 12 Working Capital Management; uncoded section/total label; not a lecture.
- MS Vids!146: Total Time; uncoded section/total label; not a lecture.
- MS Vids!148: 13 Short-Term Financing; uncoded section/total label; not a lecture.
- MS Vids!156: Total Time; uncoded section/total label; not a lecture.
- MS Vids!158: 14 Long-Term Financing; uncoded section/total label; not a lecture.
- MS Vids!167: Total Time; uncoded section/total label; not a lecture.
- MS Vids!169: 15 Capital Budgeting; uncoded section/total label; not a lecture.
- MS Vids!180: Total Time; uncoded section/total label; not a lecture.
- MS Vids!182: 16 Risk and Leverage; uncoded section/total label; not a lecture.
- MS Vids!187: Total Time; uncoded section/total label; not a lecture.
- MS Vids!189: 17 Economics; uncoded section/total label; not a lecture.
- MS Vids!197: Total Time; uncoded section/total label; not a lecture.
- MS Vids!200: 18 Strategic Costing; uncoded section/total label; not a lecture.
- MS Vids!210: Total Time; uncoded section/total label; not a lecture.
- MS Vids!212: None; formula-only summary with no lecture title/duration.
- AT Vids!2: The Accountancy Profession; uncoded section/total label; not a lecture.
- AT Vids!10: Total Time; uncoded section/total label; not a lecture.
- AT Vids!12: Code of Ethics for Professional Accountants in the Philippines; uncoded section/total label; not a lecture.
- AT Vids!22: Total Time; uncoded section/total label; not a lecture.
- AT Vids!24: Fundamentals of Assurance Services; uncoded section/total label; not a lecture.
- AT Vids!31: Total Time; uncoded section/total label; not a lecture.
- AT Vids!33: Introduction to Auditing; uncoded section/total label; not a lecture.
- AT Vids!40: Total Time; uncoded section/total label; not a lecture.
- AT Vids!42: Preliminary Engagement Activites; uncoded section/total label; not a lecture.
- AT Vids!47: Total Time; uncoded section/total label; not a lecture.
- AT Vids!49: Audit Planning; uncoded section/total label; not a lecture.
- AT Vids!59: Total Time; uncoded section/total label; not a lecture.
- AT Vids!61: Study and Evaluation of Internal Control; uncoded section/total label; not a lecture.
- AT Vids!67: Total Time; uncoded section/total label; not a lecture.
- AT Vids!70: Auditing in an IT Environment; uncoded section/total label; not a lecture.
- AT Vids!77: Total Time; uncoded section/total label; not a lecture.
- AT Vids!79: Transaction Cycles; uncoded section/total label; not a lecture.
- AT Vids!87: Total Time; uncoded section/total label; not a lecture.
- AT Vids!89: Fraud, Error, and Non-compliance; uncoded section/total label; not a lecture.
- AT Vids!95: Total Time; uncoded section/total label; not a lecture.
- AT Vids!97: Evidence and Performance of Substantive Testing; uncoded section/total label; not a lecture.
- AT Vids!103: Total Time; uncoded section/total label; not a lecture.
- AT Vids!105: Approaches of Gathering Evidence and Audit Sampling; uncoded section/total label; not a lecture.
- AT Vids!112: Total Time; uncoded section/total label; not a lecture.
- AT Vids!114: Completing the Audit; uncoded section/total label; not a lecture.
- AT Vids!123: Total Time; uncoded section/total label; not a lecture.
- AT Vids!125: Audit Documentation and Communication with TCWG; uncoded section/total label; not a lecture.
- AT Vids!131: Total Time; uncoded section/total label; not a lecture.
- AT Vids!133: System of Quality Control; uncoded section/total label; not a lecture.
- AT Vids!142: Audit Reporting (General-Purpose FS); uncoded section/total label; not a lecture.
- AT Vids!152: Other Engagements; uncoded section/total label; not a lecture.
- AT Vids!160: None; formula-only summary with no lecture title/duration.
- AP Vids!2: AP01- Single Entry System; uncoded section/total label; not a lecture.
- AP Vids!13: Total Time; uncoded section/total label; not a lecture.
- AP Vids!15: AP02-Correction of Errors; uncoded section/total label; not a lecture.
- AP Vids!25: Total Time; uncoded section/total label; not a lecture.
- AP Vids!27: AP03- Shareholders' Equity; uncoded section/total label; not a lecture.
- AP Vids!46: Total Time; uncoded section/total label; not a lecture.
- AP Vids!50: AP04- Share-Based Payment; uncoded section/total label; not a lecture.
- AP Vids!67: Total Time; uncoded section/total label; not a lecture.
- AP Vids!70: AP05-Audit of Cash; uncoded section/total label; not a lecture.
- AP Vids!92: Total Time; uncoded section/total label; not a lecture.
- AP Vids!94: AP06- Receivables; uncoded section/total label; not a lecture.
- AP Vids!116: Total Time; uncoded section/total label; not a lecture.
- AP Vids!120: AP07- Inventories and Agriculture; uncoded section/total label; not a lecture.
- AP Vids!140: Total Time; uncoded section/total label; not a lecture.
- AP Vids!142: AP08- Investment in Equity Securities; uncoded section/total label; not a lecture.
- AP Vids!169: Total Time; uncoded section/total label; not a lecture.
- AP Vids!172: AP09- Investment in Debt Securities; uncoded section/total label; not a lecture.
- AP Vids!189: Total Time; uncoded section/total label; not a lecture.
- AP Vids!191: AP10- Notes and Bonds payable; uncoded section/total label; not a lecture.
- AP Vids!210: Total Time; uncoded section/total label; not a lecture.
- AP Vids!212: AP11- Property, plant and Equipment; uncoded section/total label; not a lecture.
- AP Vids!242: Total Time; uncoded section/total label; not a lecture.
- AP Vids!244: AP12- Intangible Assets; uncoded section/total label; not a lecture.
- AP Vids!265: Total Time; uncoded section/total label; not a lecture.
- AP Vids!268: AP13- Investment Property; uncoded section/total label; not a lecture.
- AP Vids!278: Total Time; uncoded section/total label; not a lecture.
- AP Vids!280: AP14- Revaluation and Impairment; uncoded section/total label; not a lecture.
- AP Vids!294: Total Time; uncoded section/total label; not a lecture.
- AP Vids!297: AP15- Current Liabilities; uncoded section/total label; not a lecture.
- AP Vids!313: Total Time; uncoded section/total label; not a lecture.
- AP Vids!315: AP16- Accounting for Income Tax; uncoded section/total label; not a lecture.
- AP Vids!326: Total Time; uncoded section/total label; not a lecture.
- AP Vids!330: AP17- Employee Benefits; uncoded section/total label; not a lecture.
- AP Vids!345: Total Time; uncoded section/total label; not a lecture.
- AP Vids!347: AP18- Statement of Cash Flows; uncoded section/total label; not a lecture.
- AP Vids!357: Total Time; uncoded section/total label; not a lecture.
- AP Vids!360: AP19- Financial Statements; uncoded section/total label; not a lecture.
- AP Vids!369: Total Time; uncoded section/total label; not a lecture.
- AP Vids!371: 20 Leases; uncoded section/total label; not a lecture.
- AP Vids!396: Total Time; uncoded section/total label; not a lecture.
- AP Vids!398: None; formula-only summary with no lecture title/duration.
- RFBT Vids!2: Obligations- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!15: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!18: Contracts- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!22: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!25: Sales- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!31: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!34: Credit Transactions- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!38: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!41: Anti-Bouncing Checks Law- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!43: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!45: Consumer Protection Act and Lemon Law- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!53: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!55: Financial Rehabilitation and Insolvency Act- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!63: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!65: Philippine Competition Act- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!68: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!71: Government Procurement Law- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!76: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!79: Partnership- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!84: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!87: Law on Corporations- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!100: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!104: Insurance-Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!109: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!112: Cooperatives- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!121: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!123: AMLA- Atty. Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!130: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!134: Intellectual Property Law- Atty Cesar Nickolai Jr Soriano/ Atty Mae Diane Azores; uncoded section/total label; not a lecture.
- RFBT Vids!144: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!148: Data Privacy Act- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!153: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!155: E-Commerce Act- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!160: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!162: Ease of Doing Business Act- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!164: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!166: Labor Law- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!170: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!172: Social Security Law- Atty Cesar Nickolai Jr Soriano; uncoded section/total label; not a lecture.
- RFBT Vids!181: Total Time; uncoded section/total label; not a lecture.
- RFBT Vids!183: None; formula-only summary with no lecture title/duration.
- TAX Vids!2: 00 Create Law Updates; uncoded section/total label; not a lecture.
- TAX Vids!9: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!11: 01 Fundamental Principles of Taxation; uncoded section/total label; not a lecture.
- TAX Vids!26: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!28: 02 Taxes, Tax Laws and Tax Administration; uncoded section/total label; not a lecture.
- TAX Vids!35: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!37: 03 Fundamental Principles of Income Taxation; uncoded section/total label; not a lecture.
- TAX Vids!45: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!47: 04 Final Income Taxation; uncoded section/total label; not a lecture.
- TAX Vids!54: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!56: 05 Capital Gains Tax; uncoded section/total label; not a lecture.
- TAX Vids!67: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!69: 06 Regular Income Tax; uncoded section/total label; not a lecture.
- TAX Vids!80: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!82: 6.1 Compensation Income; uncoded section/total label; not a lecture.
- TAX Vids!89: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!92: 6.2 Fringe Benefits; uncoded section/total label; not a lecture.
- TAX Vids!96: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!99: 6.3 Dealings in Properties; uncoded section/total label; not a lecture.
- TAX Vids!104: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!107: 07 Principles of Deductions; uncoded section/total label; not a lecture.
- TAX Vids!112: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!114: 07.01 Itemized Deductions; uncoded section/total label; not a lecture.
- TAX Vids!126: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!128: 07.02 Optional Standard Deductions; uncoded section/total label; not a lecture.
- TAX Vids!133: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!137: 08 Individual Income Taxation; uncoded section/total label; not a lecture.
- TAX Vids!149: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!151: 09 Corporate Income Taxation; uncoded section/total label; not a lecture.
- TAX Vids!166: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!169: 10 Estate Taxation; uncoded section/total label; not a lecture.
- TAX Vids!185: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!187: 11 Donors Taxation; uncoded section/total label; not a lecture.
- TAX Vids!196: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!198: 12 Consumption Taxes; uncoded section/total label; not a lecture.
- TAX Vids!204: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!206: 13 VAT on Importation; uncoded section/total label; not a lecture.
- TAX Vids!209: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!212: 14 Introduction to Business Taxation; uncoded section/total label; not a lecture.
- TAX Vids!221: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!223: 14.01 Specific Percentage Tax; uncoded section/total label; not a lecture.
- TAX Vids!226: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!228: 14.02 Value Added Tax; uncoded section/total label; not a lecture.
- TAX Vids!237: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!240: 15 Excise Tax and Documentary Stamp Tax; uncoded section/total label; not a lecture.
- TAX Vids!251: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!253: 16 Tax Remedies; uncoded section/total label; not a lecture.
- TAX Vids!261: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!263: 17 Local Taxation; uncoded section/total label; not a lecture.
- TAX Vids!275: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!278: 18 Preferential Taxation; uncoded section/total label; not a lecture.
- TAX Vids!287: Total Time; uncoded section/total label; not a lecture.
- TAX Vids!289: None; formula-only summary with no lecture title/duration.
- FAR Vids!2: FAR01- Introduction to Accountancy Profession & Preface to PFRS; uncoded section/total label; not a lecture.
- FAR Vids!8: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!10: FAR02- Conceptual Framework for Financial Reporting; uncoded section/total label; not a lecture.
- FAR Vids!23: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!25: FAR03- Cash and Cash Equivalents; uncoded section/total label; not a lecture.
- FAR Vids!36: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!38: FAR04- Receivables; uncoded section/total label; not a lecture.
- FAR Vids!62: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!65: FAR05- Inventories; uncoded section/total label; not a lecture.
- FAR Vids!90: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!92: FAR06- Biological Assets; uncoded section/total label; not a lecture.
- FAR Vids!104: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!106: FAR07- Property, Plant & Equipment (Part 1); uncoded section/total label; not a lecture.
- FAR Vids!120: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!123: FAR08- Property, Plant & Equipment (Part 2); uncoded section/total label; not a lecture.
- FAR Vids!143: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!145: FAR09- Government Grants; uncoded section/total label; not a lecture.
- FAR Vids!153: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!156: FAR10- Borrowing Costs; uncoded section/total label; not a lecture.
- FAR Vids!166: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!168: FAR11- Depletion of Mineral Resources; uncoded section/total label; not a lecture.
- FAR Vids!180: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!182: FAR12- Intangible Assets; uncoded section/total label; not a lecture.
- FAR Vids!198: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!201: FAR13- Impairment of Assets; uncoded section/total label; not a lecture.
- FAR Vids!213: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!216: FAR14- Investment in Equity Securities; uncoded section/total label; not a lecture.
- FAR Vids!231: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!234: FAR15- Investment in Associates; uncoded section/total label; not a lecture.
- FAR Vids!248: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!250: FAR16- Investment in Debt Securities; uncoded section/total label; not a lecture.
- FAR Vids!262: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!264: FAR17- Investment Properties; uncoded section/total label; not a lecture.
- FAR Vids!277: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!279: FAR18- Funds and Other Investments; uncoded section/total label; not a lecture.
- FAR Vids!288: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!290: FAR19 NOT APPLICABLE; uncoded section/total label; not a lecture.
- FAR Vids!293: FAR20- Current Liabilities; uncoded section/total label; not a lecture.
- FAR Vids!305: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!307: FAR21 Notes Payable; uncoded section/total label; not a lecture.
- FAR Vids!320: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!322: FAR22 - Bonds Payable; uncoded section/total label; not a lecture.
- FAR Vids!333: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!335: FAR23 Compound Financial Instruments; uncoded section/total label; not a lecture.
- FAR Vids!342: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!345: FAR24 Provisions; uncoded section/total label; not a lecture.
- FAR Vids!359: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!361: FAR25 Employee Benefits; uncoded section/total label; not a lecture.
- FAR Vids!375: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!377: FAR26 Income Taxes; uncoded section/total label; not a lecture.
- FAR Vids!390: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!393: FAR27 Leases; uncoded section/total label; not a lecture.
- FAR Vids!412: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!414: FAR28 Shareholders' Equity (Part 1); uncoded section/total label; not a lecture.
- FAR Vids!432: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!435: FAR29 Shareholders' Equity (Part 2); uncoded section/total label; not a lecture.
- FAR Vids!453: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!455: FAR30 Share-based Payments; uncoded section/total label; not a lecture.
- FAR Vids!472: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!474: FAR31 Book value per share; uncoded section/total label; not a lecture.
- FAR Vids!481: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!483: FAR32 Earnings per share; uncoded section/total label; not a lecture.
- FAR Vids!500: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!502: FAR33 Financial Statements (Part 1); uncoded section/total label; not a lecture.
- FAR Vids!511: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!513: FAR34 Financial Statements (Part 2); uncoded section/total label; not a lecture.
- FAR Vids!524: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!526: FAR35 Statement of Cash Flows; uncoded section/total label; not a lecture.
- FAR Vids!534: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!536: NOT APPLICABLE; uncoded section/total label; not a lecture.
- FAR Vids!538: FAR37 Operating Segments; uncoded section/total label; not a lecture.
- FAR Vids!547: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!550: FAR38 NCAHFS & Discontinued Operations; uncoded section/total label; not a lecture.
- FAR Vids!559: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!561: FAR39 Events after the Reporting Period; uncoded section/total label; not a lecture.
- FAR Vids!565: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!567: FAR40 Related Parties; uncoded section/total label; not a lecture.
- FAR Vids!572: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!574: FAR41 Interim Reporting; uncoded section/total label; not a lecture.
- FAR Vids!580: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!582: FAR42 Accounting Changes and Error Correction; uncoded section/total label; not a lecture.
- FAR Vids!590: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!592: FAR43 Cash to Accrual Basis; uncoded section/total label; not a lecture.
- FAR Vids!600: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!603: FAR44 Accounting Process; uncoded section/total label; not a lecture.
- FAR Vids!616: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!618: FAR45 SMEs; uncoded section/total label; not a lecture.
- FAR Vids!629: Total Time; uncoded section/total label; not a lecture.
- FAR Vids!631: None; formula-only summary with no lecture title/duration.
- AFAR Vids!2: 00 Introduction to AFAR; uncoded section/total label; not a lecture.
- AFAR Vids!4: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!7: AFAR.01 Partnership Accounting; uncoded section/total label; not a lecture.
- AFAR Vids!8: 01-01 Partnership Formation; uncoded section/total label; not a lecture.
- AFAR Vids!15: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!17: 01-02 Partnership Operation; uncoded section/total label; not a lecture.
- AFAR Vids!30: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!32: 01-03 Partnership Dissolution; uncoded section/total label; not a lecture.
- AFAR Vids!40: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!43: 01-04 Partnership Liquidation; uncoded section/total label; not a lecture.
- AFAR Vids!51: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!54: AFAR 02 Corporate Liquidation; uncoded section/total label; not a lecture.
- AFAR Vids!61: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!64: AFAR.03 Revenue Recognition; uncoded section/total label; not a lecture.
- AFAR Vids!66: 01 Revenue from Contracts with Customers (PFRS 15); uncoded section/total label; not a lecture.
- AFAR Vids!79: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!81: 02 Appendix: Revenue Recognition (PFRS for SMEs); uncoded section/total label; not a lecture.
- AFAR Vids!84: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!86: 03 Appendix: Franchise Operations & Installment Sales (Old US GAAP); uncoded section/total label; not a lecture.
- AFAR Vids!92: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!94: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!97: AFAR.04 Decentralized Operation; uncoded section/total label; not a lecture.
- AFAR Vids!112: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!114: AFAR.05 Business Combination; uncoded section/total label; not a lecture.
- AFAR Vids!127: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!130: AFAR.06 Separate and Consolidated FS; uncoded section/total label; not a lecture.
- AFAR Vids!159: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!161: AFAR.07 Joint Arrangements; uncoded section/total label; not a lecture.
- AFAR Vids!171: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!174: AFAR.08 Forex and Hyperinflation; uncoded section/total label; not a lecture.
- AFAR Vids!188: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!191: 09 Derivatives and Hedge Accounting; uncoded section/total label; not a lecture.
- AFAR Vids!202: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!205: AFAR.10 Not-for-Profit Organizations; uncoded section/total label; not a lecture.
- AFAR Vids!212: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!215: AFAR.11 Government Accounting; uncoded section/total label; not a lecture.
- AFAR Vids!221: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!224: AFAR.12 Cost Accounting; uncoded section/total label; not a lecture.
- AFAR Vids!225: 01 Job Order Costing; uncoded section/total label; not a lecture.
- AFAR Vids!231: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!233: 02 Process Costing; uncoded section/total label; not a lecture.
- AFAR Vids!244: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!246: 03 Backflush Costing; uncoded section/total label; not a lecture.
- AFAR Vids!249: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!251: 04 Activity-Based Costing; uncoded section/total label; not a lecture.
- AFAR Vids!254: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!256: 05 Joint and By-products Costing; uncoded section/total label; not a lecture.
- AFAR Vids!260: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!262: 06 Service Cost Allocation; uncoded section/total label; not a lecture.
- AFAR Vids!265: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!267: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!270: AFAR.13 Insurance Contracts; uncoded section/total label; not a lecture.
- AFAR Vids!274: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!276: AFAR.14 Service Concession Arrangement; uncoded section/total label; not a lecture.
- AFAR Vids!280: Total Time; uncoded section/total label; not a lecture.
- AFAR Vids!282: None; formula-only summary with no lecture title/duration.

## Accepted source traceability

| Subject | Source | Topic reference | Title | Seconds |
| --- | --- | --- | --- | ---: |
| MAS | MS Vids!3 | MAS-01 | 01-01 Basic Consideration in Management Services | 1322 |
| MAS | MS Vids!4 | MAS-01 | 01-02 Distinction among Management Accounting, Cost Accounting and Financial Accounting | 769 |
| MAS | MS Vids!5 | MAS-01 | 01-03 Roles and Activities of Controller and Treasurer | 3447 |
| MAS | MS Vids!6 | MAS-01 | 01-04 International Certifications in Management Accounting | 2092 |
| MAS | MS Vids!7 | MAS-01 | 01-05 Global Trends in Management Accounting | 1562 |
| MAS | MS Vids!8 | MAS-01 | 01-06 Drills 1 to 25 | 1224 |
| MAS | MS Vids!9 | MAS-01 | 01-07 Drills 26 to 50 | 826 |
| MAS | MS Vids!13 | MAS-02 | 02-01 Variable and Absorption Costing | 438 |
| MAS | MS Vids!14 | MAS-02 | 02-02 Distinction Between Product Cost and Period Cost | 195 |
| MAS | MS Vids!15 | MAS-02 | 02-03 Inventory Costs Between Variable Costing and Absorbtion Costing | 2115 |
| MAS | MS Vids!16 | MAS-02 | 02-04 Nature and Treatment of Fixed Factory Overhead Costs | 561 |
| MAS | MS Vids!17 | MAS-02 | 02-05 Reconciliation of Operating Income Under Variable Costing and Absorption Costing | 284 |
| MAS | MS Vids!18 | MAS-02 | 02-06 Drills 1 to 22 | 742 |
| MAS | MS Vids!19 | MAS-02 | 02-07 Drills 23 to 44 | 1155 |
| MAS | MS Vids!20 | MAS-02 | 02-08 Illustration 1 to 3 | 1543 |
| MAS | MS Vids!21 | MAS-02 | 02-09 Illustration 4 to 12 | 946 |
| MAS | MS Vids!25 | MAS-03 | 03-01 CVP-BEP Analysis | 637 |
| MAS | MS Vids!26 | MAS-03 | 03-02 Uses Assumptions and Limitations of CVP Analysis | 558 |
| MAS | MS Vids!27 | MAS-03 | 03-03 Factors Affecting Profit | 561 |
| MAS | MS Vids!28 | MAS-03 | 03-04 Breakeven Point in Unit Sales and Peso Sales | 1628 |
| MAS | MS Vids!29 | MAS-03 | 03-05 Required Selling Price, Unit Sales and Peso Sales to Achieve a Target Profit | 419 |
| MAS | MS Vids!30 | MAS-03 | 03-06 Sensitivity Analysis | 793 |
| MAS | MS Vids!31 | MAS-03 | 03-07 Indifference Point in Unit Sales and Peso Sales | 596 |
| MAS | MS Vids!32 | MAS-03 | 03-08 Use of Sales Mix in Multi-Product Companies | 761 |
| MAS | MS Vids!33 | MAS-03 | 03-09 Concepts of Margin of Safety and Degree of Operating Leverage | 1377 |
| MAS | MS Vids!34 | MAS-03 | 03-10 Different Scenarios Using CVP Analysis (Indifference Point, Step Fixed, Multiple Drivers | 589 |
| MAS | MS Vids!35 | MAS-03 | 03-11 Drills 1 to 29 | 1231 |
| MAS | MS Vids!36 | MAS-03 | 03-12 Drills 30-59 | 2532 |
| MAS | MS Vids!40 | MAS-04 | 04-01 Introduction, Vertical, Horizontal | 330 |
| MAS | MS Vids!41 | MAS-04 | 04-02 Cash flows and Free Cash Flows | 262 |
| MAS | MS Vids!42 | MAS-04 | 04-03 Gross Profit Variance Analysis | 419 |
| MAS | MS Vids!43 | MAS-04 | 04-04 Introduction to Ratios and Liquidity | 871 |
| MAS | MS Vids!44 | MAS-04 | 04-05 Working Capital Activity Ratios | 717 |
| MAS | MS Vids!45 | MAS-04 | 04-06 Solvency Ratios | 364 |
| MAS | MS Vids!46 | MAS-04 | 04-07 Profitability Ratios | 599 |
| MAS | MS Vids!47 | MAS-04 | 04-08 DU PONT, GROWTH, AND AFN | 747 |
| MAS | MS Vids!48 | MAS-04 | 04-09 Drills 1-18 | 2087 |
| MAS | MS Vids!49 | MAS-04 | 04-10 Drills 19-24 | 742 |
| MAS | MS Vids!50 | MAS-04 | 04-11 Drills 25-29 | 1215 |
| MAS | MS Vids!51 | MAS-04 | 04-12 Drills 30-51 | 2404 |
| MAS | MS Vids!52 | MAS-04 | 04-13 Drills 52-72 | 1866 |
| MAS | MS Vids!53 | MAS-04 | 04-13 Drills 73-78 | 651 |
| MAS | MS Vids!57 | MAS-05 | 05-01 Definition and Coverage of the Budgeting Process | 2197 |
| MAS | MS Vids!58 | MAS-05 | 05-02 Master Budget and It's Components (Operatinng and Financial Budgets) | 901 |
| MAS | MS Vids!59 | MAS-05 | 05-03 Types of Budgets (Static, Flexible, Zero-based, Continuous) | 1419 |
| MAS | MS Vids!60 | MAS-05 | 05-04 Drills 1 to 50 | 2314 |
| MAS | MS Vids!61 | MAS-05 | 05-05 Drills 51 to 68 | 2436 |
| MAS | MS Vids!65 | MAS-06 | 06-01 Standard Cost Variance Analysis | 2801 |
| MAS | MS Vids!66 | MAS-06 | 06-02 Journal Entries | 895 |
| MAS | MS Vids!67 | MAS-06 | 06-03 Direct Material Variance (Quantity, Price Usage, Purchase Price, Mix and Yield) | 1297 |
| MAS | MS Vids!68 | MAS-06 | 06-04 Financial Planning and Budgets (Budget Variance Analysis-Static and Flexible) | 619 |
| MAS | MS Vids!69 | MAS-06 | 06-05 Illustration 1 | 802 |
| MAS | MS Vids!70 | MAS-06 | 06-06 Illustration 2 | 1031 |
| MAS | MS Vids!71 | MAS-06 | 06-07 Illustration 3 | 1836 |
| MAS | MS Vids!72 | MAS-06 | 06-08 Illustration 4 | 488 |
| MAS | MS Vids!73 | MAS-06 | 06-09 Drill 1 to 29 | 2533 |
| MAS | MS Vids!74 | MAS-06 | 06-10 Drill 30 to 54 | 1984 |
| MAS | MS Vids!78 | MAS-07 | 07-01 Performance Evaluation | 1625 |
| MAS | MS Vids!79 | MAS-07 | 07-02 Controllable and Non-controllable Cost, Direct and Common Costs | 302 |
| MAS | MS Vids!80 | MAS-07 | 07-03 Type of Responsibility Centers (Cost, Revenue, Profit and Investment Centers) | 412 |
| MAS | MS Vids!81 | MAS-07 | 07-04 Performance Margin (Manager vs. Segment Performance), Return of Investment (ROI), Residual Income and Economic Value Added (EVA) | 1522 |
| MAS | MS Vids!82 | MAS-07 | 07-05 Rational and Need for Transfer Price | 1146 |
| MAS | MS Vids!83 | MAS-07 | 07-06 Nature and Perspective of Balanced Scorecard | 1580 |
| MAS | MS Vids!84 | MAS-07 | 07-07 Financial and Non-financial Performance Measures | 853 |
| MAS | MS Vids!85 | MAS-07 | 07-08 Financial Performance Measures | 2035 |
| MAS | MS Vids!86 | MAS-07 | 07-09 Drills 1 to 25 | 2108 |
| MAS | MS Vids!87 | MAS-07 | 07-10 Drills 26 to 60 | 2476 |
| MAS | MS Vids!88 | MAS-07 | 07-11 Drills 61 to End | 2025 |
| MAS | MS Vids!89 | MAS-07 | 07-12 Strategic Anaysis of Operating Income: Comprehensive Illustration | 2606 |
| MAS | MS Vids!93 | MAS-08 | 08-01 Pricing Decisions | 1006 |
| MAS | MS Vids!94 | MAS-08 | 08-02 Time Horizon and Pricing Decisions | 1678 |
| MAS | MS Vids!95 | MAS-08 | 08-03 Cost Based Pricing | 398 |
| MAS | MS Vids!96 | MAS-08 | 08-04 Alternative Cost-Plus Methods | 309 |
| MAS | MS Vids!97 | MAS-08 | 08-05 Target Pricing | 982 |
| MAS | MS Vids!98 | MAS-08 | 08-06 Value Chain and the Product's Life Cycle | 899 |
| MAS | MS Vids!99 | MAS-08 | 08-07 Demand, Supply and Market Equilibrium | 1489 |
| MAS | MS Vids!100 | MAS-08 | 08-08 Summary Effects of Disequilibrium | 431 |
| MAS | MS Vids!101 | MAS-08 | 08-09 Drills 1 to 25 | 1249 |
| MAS | MS Vids!102 | MAS-08 | 08-10 Drills 26 to 56 | 1421 |
| MAS | MS Vids!106 | MAS-09 | 09-01 Relevant Costing | 658 |
| MAS | MS Vids!107 | MAS-09 | 09-02 Approaches in Analyzing Alternatives in Non-routing Decisions (Total and Differential) | 1475 |
| MAS | MS Vids!108 | MAS-09 | 09-03 Types of Decisions | 1057 |
| MAS | MS Vids!109 | MAS-09 | 09-04 Illustration | 542 |
| MAS | MS Vids!110 | MAS-09 | 09-05 Keep or Drop Decision add a Product Line | 646 |
| MAS | MS Vids!111 | MAS-09 | 09-06 Sell-as-is or Process Further | 295 |
| MAS | MS Vids!112 | MAS-09 | 09-07 Optimizing Scarce Resources | 1178 |
| MAS | MS Vids!113 | MAS-09 | 09-08 Economics vs. Accounting Concepts of Marginal Revenue and Marginal Costs | 275 |
| MAS | MS Vids!114 | MAS-09 | 09-09 Drills 1 to 32 | 1149 |
| MAS | MS Vids!115 | MAS-09 | 09-10 Drills 33 to 45 | 2388 |
| MAS | MS Vids!116 | MAS-09 | 09-11 Drills 46 to 65 | 3268 |
| MAS | MS Vids!120 | MAS-10 | 10-01 Quantitative Techniques | 459 |
| MAS | MS Vids!121 | MAS-10 | 10-02 Splitting Mixed Cost And Cost Prediction Techniques | 3183 |
| MAS | MS Vids!122 | MAS-10 | 10-03 Probability Analysis (Expected Value Concept) | 990 |
| MAS | MS Vids!123 | MAS-10 | 10-04 Decision Tree Diagram | 556 |
| MAS | MS Vids!124 | MAS-10 | 10-05 Linear Programming (Graphic Method; Algebraic Method) | 507 |
| MAS | MS Vids!125 | MAS-10 | 10-06 Drills 1 to 35 | 2467 |
| MAS | MS Vids!126 | MAS-10 | 10-07 Drills 36 to 49 | 1201 |
| MAS | MS Vids!127 | MAS-10 | 10-08 Drills 50 to 68 | 1802 |
| MAS | MS Vids!131 | MAS-11 | 11-01 Financial Markets | 2246 |
| MAS | MS Vids!132 | MAS-11 | 11-02 Money Markets | 551 |
| MAS | MS Vids!133 | MAS-11 | 11-03 Fixed Income Market | 927 |
| MAS | MS Vids!134 | MAS-11 | 11-04 Stock Market | 2272 |
| MAS | MS Vids!135 | MAS-11 | 11-05 Drills 1 to 30 | 1106 |
| MAS | MS Vids!136 | MAS-11 | 11-06 Drills 31 to 69 | 1788 |
| MAS | MS Vids!140 | MAS-12 | 12-01 Working Capital Management | 1180 |
| MAS | MS Vids!141 | MAS-12 | 12-02 Cash and Marketable Securities Management | 3439 |
| MAS | MS Vids!142 | MAS-12 | 12-03 Receivables Management | 2524 |
| MAS | MS Vids!143 | MAS-12 | 12-04 Inventory Management | 2502 |
| MAS | MS Vids!144 | MAS-12 | 12-05 Drills 1 to 30 | 2054 |
| MAS | MS Vids!145 | MAS-12 | 12-06 Drills 31 to 53 | 1883 |
| MAS | MS Vids!149 | MAS-13 | 13-01 Short-Term Financing | 1092 |
| MAS | MS Vids!150 | MAS-13 | 13-02 Sources of Short-Term Funds- Unsecured | 2790 |
| MAS | MS Vids!151 | MAS-13 | 13-03 Sources of Short-Term Funds- Secured | 647 |
| MAS | MS Vids!152 | MAS-13 | 13-04 Drills 1-35 | 3222 |
| MAS | MS Vids!153 | MAS-13 | 13-05 Drills 36-40 | 850 |
| MAS | MS Vids!154 | MAS-13 | 13-06 Drills 41-44 | 350 |
| MAS | MS Vids!155 | MAS-13 | 13-07 Drills 45-60 | 1611 |
| MAS | MS Vids!159 | MAS-14 | 14-01 Long-Term Financing | 1465 |
| MAS | MS Vids!160 | MAS-14 | 14-02 Sources of Intermediate and Long-Term Financing | 2952 |
| MAS | MS Vids!161 | MAS-14 | 14-03 Cost of Capital: Debt Financing | 3455 |
| MAS | MS Vids!162 | MAS-14 | 14-04 Cost of Capital: Equity Financing | 3654 |
| MAS | MS Vids!163 | MAS-14 | 14-05 Weighted Average Cost of Capital (WACC) | 1056 |
| MAS | MS Vids!164 | MAS-14 | 14-06 Drills 1 to 49 | 2448 |
| MAS | MS Vids!165 | MAS-14 | 14-07 Drills 50 to 61 | 1649 |
| MAS | MS Vids!166 | MAS-14 | 14-08 Drills 62 to 75 | 2916 |
| MAS | MS Vids!170 | MAS-15 | 15-01 Capital Budgeting | 847 |
| MAS | MS Vids!171 | MAS-15 | 15-02 Capital Investment Decision Factors | 3158 |
| MAS | MS Vids!172 | MAS-15 | 15-03 Non-discounted Capital Budgeting Techniques | 1544 |
| MAS | MS Vids!173 | MAS-15 | 15-04 Discounted Capital Budgeting Techniques Part 1 | 2577 |
| MAS | MS Vids!174 | MAS-15 | 15-05 Discounted Capital Budgeting Techniques Part 2 | 1254 |
| MAS | MS Vids!175 | MAS-15 | 15-06 Project Screening, Project Ranking and Capital Rationing | 675 |
| MAS | MS Vids!176 | MAS-15 | 15-07 Sensitivity Analysis | 1073 |
| MAS | MS Vids!177 | MAS-15 | 15-08 Drills 1 to 35 | 2053 |
| MAS | MS Vids!178 | MAS-15 | 15-09 Drills 36 to 45 | 1862 |
| MAS | MS Vids!179 | MAS-15 | 15-10 Drills 46 to 55 | 2294 |
| MAS | MS Vids!183 | MAS-16 | 16-01 Risk and Leverage | 3864 |
| MAS | MS Vids!184 | MAS-16 | 16-02 Measures of Risks (Coefficient of Variation and standard Deviation) | 2313 |
| MAS | MS Vids!185 | MAS-16 | 16-03 Degree of Operating, Financial and Total Leverage | 726 |
| MAS | MS Vids!186 | MAS-16 | 16-04 Drills 1 to 39 | 2852 |
| MAS | MS Vids!190 | MAS-17 | 17-01 Economics | 1567 |
| MAS | MS Vids!191 | MAS-17 | 17-02 Microeconomics Part 1 | 2426 |
| MAS | MS Vids!192 | MAS-17 | 17-03 Microeconomics Part 2 | 1833 |
| MAS | MS Vids!193 | MAS-17 | 17-04 Macroeconomics Part 1 | 2781 |
| MAS | MS Vids!194 | MAS-17 | 17-05 Macroeconomics Part 2 | 4755 |
| MAS | MS Vids!195 | MAS-17 | 17-06 Drills 1 to 40 | 1354 |
| MAS | MS Vids!196 | MAS-17 | 17-07 Drills 41 to 77 | 1547 |
| MAS | MS Vids!201 | MAS-18 | 18-01 Strategic Costing Overview | 4204 |
| MAS | MS Vids!202 | MAS-18 | 18-02 Just-In-Time (JIT) | 1332 |
| MAS | MS Vids!203 | MAS-18 | 18-03 Business Process Reengineering (BRP) | 614 |
| MAS | MS Vids!204 | MAS-18 | 18-04 Product Life Cycle Costing | 966 |
| MAS | MS Vids!205 | MAS-18 | 18-05 Theory of Constraints (TOC) | 906 |
| MAS | MS Vids!206 | MAS-18 | 18-06 Activity Based Costing and Management | 1714 |
| MAS | MS Vids!207 | MAS-18 | 18-07 Drills Part 1 | 2769 |
| MAS | MS Vids!208 | MAS-18 | 18-08 Drills Part 2 | 1122 |
| MAS | MS Vids!209 | MAS-18 | 18-09 Drills Part 3 | 2735 |
| AT | AT Vids!3 | AT-01 | 01-01 Scope of Practice | 2339 |
| AT | AT Vids!4 | AT-01 | 01-02 Regulation of the Accountancy Profession | 3133 |
| AT | AT Vids!5 | AT-01 | 01-03 The CPA Licensure Examination | 2194 |
| AT | AT Vids!6 | AT-01 | 01-04 Practice of Accountancy | 3734 |
| AT | AT Vids!7 | AT-01 | 01-05 Organizations Affecting the Accountancy Profession | 3044 |
| AT | AT Vids!8 | AT-01 | 01-06 Knowledge Check - Part 1 | 1256 |
| AT | AT Vids!9 | AT-01 | 01-07 Knowledge Check - Part 2 | 1116 |
| AT | AT Vids!13 | AT-02 | 02-01 Introduction to the Code of Ethics for Professional Accountants in the Philippines | 2378 |
| AT | AT Vids!14 | AT-02 | 02-02 Complying with the Code and Fundamental Principles | 2290 |
| AT | AT Vids!15 | AT-02 | 02-03 Conceptual Framework | 2211 |
| AT | AT Vids!16 | AT-02 | 02-04 Professional Accountants in Business (PAIB) | 1736 |
| AT | AT Vids!17 | AT-02 | 02-05 Professional Accountants in Public Practice (PAPP) | 2087 |
| AT | AT Vids!18 | AT-02 | 02-06 Independence for Audit and Review Engagements | 1926 |
| AT | AT Vids!19 | AT-02 | 02-07 Independence for Assurance Engagements other than Audit and Review Engagements | 988 |
| AT | AT Vids!20 | AT-02 | 02-08 Knowledge Check - Part 1 | 1464 |
| AT | AT Vids!21 | AT-02 | 02-09 Knowledge Check - Part 2 | 1299 |
| AT | AT Vids!25 | AT-03 | 03-01 Introduction to Assurance Services | 1499 |
| AT | AT Vids!26 | AT-03 | 03-02 Elements of Assurance Engagements - Part 1 | 2324 |
| AT | AT Vids!27 | AT-03 | 03-03 Elements of Assurance Engagement - Part 2 | 3155 |
| AT | AT Vids!28 | AT-03 | 03-04 Services Performed by Practitioners | 1079 |
| AT | AT Vids!29 | AT-03 | 03-05 Knowledge Check - Part 1 | 929 |
| AT | AT Vids!30 | AT-03 | 03-06 Knowledge Check - Part 2 | 798 |
| AT | AT Vids!34 | AT-04 | 04-01 Introduction to Auditing | 2338 |
| AT | AT Vids!35 | AT-04 | 04-02 Financial Statements Audit | 2858 |
| AT | AT Vids!36 | AT-04 | 04-03 General Approach | 2149 |
| AT | AT Vids!37 | AT-04 | 04-04 Detailed Approach | 1423 |
| AT | AT Vids!38 | AT-04 | 04-05 Knowledge Check - Part 1 | 1105 |
| AT | AT Vids!39 | AT-04 | 04-06 Knowledge Check - Part 2 | 955 |
| AT | AT Vids!43 | AT-05 | 05-01 Preliminary Engagement Activities | 1748 |
| AT | AT Vids!44 | AT-05 | 05-02 Acceptance of the Engagement | 2014 |
| AT | AT Vids!45 | AT-05 | 05-03 Knowledge Check - Part 1 | 1006 |
| AT | AT Vids!46 | AT-05 | 05-04 Knowledge Check - Part 2 | 940 |
| AT | AT Vids!50 | AT-06 | 06-01 Introduction to Audit Planning | 2402 |
| AT | AT Vids!51 | AT-06 | 06-02 Audit Procedures | 2696 |
| AT | AT Vids!52 | AT-06 | 06-03 Identifying And Assessing RoMM - Part 1 | 1498 |
| AT | AT Vids!53 | AT-06 | 06-04 Identifying and Assessing RoMM - Part 2 | 2137 |
| AT | AT Vids!54 | AT-06 | 06-05 Identifying and Assessing RoMM - Part 3 | 2799 |
| AT | AT Vids!55 | AT-06 | 06-06 Audit Risk and Risk of Non-Detection | 1047 |
| AT | AT Vids!56 | AT-06 | 06-07 Other Planning Procedures | 2358 |
| AT | AT Vids!57 | AT-06 | 06-08 Knowledge Check - Part 1 | 1378 |
| AT | AT Vids!58 | AT-06 | 06-09 Knowledge Check - Part 2 | 1131 |
| AT | AT Vids!62 | AT-07 | 07-01 Introduction to Internal Control | 2954 |
| AT | AT Vids!63 | AT-07 | 07-02 Components of Internal Control | 2909 |
| AT | AT Vids!64 | AT-07 | 07-03 Audit Procedures - Responses to Assessed Risks | 1547 |
| AT | AT Vids!65 | AT-07 | 07-04 Knowledge Check - Part 1 | 876 |
| AT | AT Vids!66 | AT-07 | 07-05 Knowledge Check - Part 2 | 1047 |
| AT | AT Vids!71 | AT-08 | 08-01 Information Technology Environment | 3231 |
| AT | AT Vids!72 | AT-08 | 08-02 Internal Control in an IT Environment - Part 1 | 3203 |
| AT | AT Vids!73 | AT-08 | 08-03 Internal Control in an IT Environment - Part 2 | 963 |
| AT | AT Vids!74 | AT-08 | 08-04 Auditing in an IT Environment | 3035 |
| AT | AT Vids!75 | AT-08 | 08-05 Knowledge Check - Part 1 | 1050 |
| AT | AT Vids!76 | AT-08 | 08-06 Knowledge Check - Part 2 | 740 |
| AT | AT Vids!80 | AT-09 | 09-01 Introduction to Transaction Cycles | 1570 |
| AT | AT Vids!81 | AT-09 | 09-02 Revenue and Receipt Cycle - PART 1 | 3374 |
| AT | AT Vids!82 | AT-09 | 09-03 Revenue and Receipt Cycle - PART 2 | 1560 |
| AT | AT Vids!83 | AT-09 | 09-04 Expenditure and Disbursement Cycle | 2254 |
| AT | AT Vids!84 | AT-09 | 09-05 Other Cycles | 1882 |
| AT | AT Vids!85 | AT-09 | 09-06 Knowledge Check Part 1 | 1058 |
| AT | AT Vids!86 | AT-09 | 09-07 Knowledge Check Part 2 | 1138 |
| AT | AT Vids!90 | AT-10 | 10-01 Consideration Of Fraud, Error And Non-Compliance | 2241 |
| AT | AT Vids!91 | AT-10 | 10-02 Consideration of Fraud and Error | 2694 |
| AT | AT Vids!92 | AT-10 | 10-03 Consideration of Laws and Regulations | 2303 |
| AT | AT Vids!93 | AT-10 | 10-04 Knowledge Check Part 1 | 954 |
| AT | AT Vids!94 | AT-10 | 10-05 Knowledge Check Part 2 | 994 |
| AT | AT Vids!98 | AT-11 | 11-01 General Concepts of Evidence | 3246 |
| AT | AT Vids!99 | AT-11 | 11-02 Performance of Substantive Testing, including Confirmation and Analytical Procedures | 2958 |
| AT | AT Vids!100 | AT-11 | 11-03 Auditing Accounting Estimates and Related Disclosures | 1725 |
| AT | AT Vids!101 | AT-11 | 11-04 Knowledge Check Part 1 | 878 |
| AT | AT Vids!102 | AT-11 | 11-05 Knowledge Check Part 2 | 829 |
| AT | AT Vids!106 | AT-12 | 12-01 Approaches of Gathering Evidence | 1625 |
| AT | AT Vids!107 | AT-12 | 12-02 Basic Concepts to Audit Sampling | 2495 |
| AT | AT Vids!108 | AT-12 | 12-03 Approaches to Sampling and Attribute Sampling Plan | 3089 |
| AT | AT Vids!109 | AT-12 | 12-04 Variable Sampling Plan | 1953 |
| AT | AT Vids!110 | AT-12 | 12-05 Knowledge Check - Part 1 | 763 |
| AT | AT Vids!111 | AT-12 | 12-06 Knowledge Check - Part 2 | 891 |
| AT | AT Vids!115 | AT-13 | 13-01 Introduction to Completing the Audit | 1047 |
| AT | AT Vids!116 | AT-13 | 13-02 Liability Items | 1257 |
| AT | AT Vids!117 | AT-13 | 13-03 Related Parties | 1827 |
| AT | AT Vids!118 | AT-13 | 13-04 Going Concern | 2516 |
| AT | AT Vids!119 | AT-13 | 13-05 Subsequent Events and Omitted Procedures | 2163 |
| AT | AT Vids!120 | AT-13 | 13-06 Written Representation Letter | 999 |
| AT | AT Vids!121 | AT-13 | 13-07 Knowledge Check - Part 1 | 836 |
| AT | AT Vids!122 | AT-13 | 13-08 Knowledge Check - Part 2 | 1094 |
| AT | AT Vids!126 | AT-14 | 14-01 Audit Documentation - PART 1 | 2668 |
| AT | AT Vids!127 | AT-14 | 14-02 Audit Documentation - PART 2 | 1867 |
| AT | AT Vids!128 | AT-14 | 14-03 Communication With Those Charged With Governance | 784 |
| AT | AT Vids!129 | AT-14 | 14-04 Knowledge Check - Part 1 | 845 |
| AT | AT Vids!130 | AT-14 | 14-05 Knowledge Check - Part 2 | 948 |
| AT | AT Vids!134 | AT-15 | 15-01 Introduction To Quality Control | 1033 |
| AT | AT Vids!135 | AT-15 | 15-02 Elements Of Quality Control - Part 1 | 2436 |
| AT | AT Vids!136 | AT-15 | 15-03 Elements Of Quality Control - Part 2 | 2739 |
| AT | AT Vids!137 | AT-15 | 15-04 Quality Control For An Audit Of Historical Financial Statements | 750 |
| AT | AT Vids!138 | AT-15 | 15-05 Knowledge Check - Part 1 | 989 |
| AT | AT Vids!139 | AT-15 | 15-06 Knowledge Check - Part 2 | 826 |
| AT | AT Vids!143 | AT-16 | 16-01 Introduction To Audit Reporting | 1408 |
| AT | AT Vids!144 | AT-16 | 16-02 Independent Auditor's Report - Basic Parts | 2189 |
| AT | AT Vids!145 | AT-16 | 16-03 Key Audit Matters And Other Information | 1524 |
| AT | AT Vids!146 | AT-16 | 16-04 Modification In The Auditor's Report | 1560 |
| AT | AT Vids!147 | AT-16 | 16-05 Comparative Information And Opening Balances | 2217 |
| AT | AT Vids!148 | AT-16 | 16-06 Audit Of Group Fs And Using The Work Of An Expert | 1531 |
| AT | AT Vids!149 | AT-16 | 16-07 Knowledge Check - Part 1 | 894 |
| AT | AT Vids!150 | AT-16 | 16-08 Knowledge Check - Part 2 | 967 |
| AT | AT Vids!153 | AT-17 | 17-01 Introduction to Special Purpose Audit Engagements and PSA 800 | 1733 |
| AT | AT Vids!154 | AT-17 | 17-02 Reporting on Audits of Single FS and Specific Elements, Acounts or Items of FS | 1243 |
| AT | AT Vids!155 | AT-17 | 17-03 Reporting on Summary FS | 1361 |
| AT | AT Vids!156 | AT-17 | 17-04 Reporting on Audit Related Services | 682 |
| AT | AT Vids!157 | AT-17 | 17-05 Knowledge Check - Part 1 | 1082 |
| AT | AT Vids!158 | AT-17 | 17-06 Knowledge Check - Part 2 | 829 |
| AP | AP Vids!3 | AP-01 | 01-01 Single Entry System | 545 |
| AP | AP Vids!4 | AP-01 | 01-02 T-Accounts of Accounts Receivable, Notes Receivables, Advances from Customers | 3014 |
| AP | AP Vids!5 | AP-01 | 01-03 T-Accounts of Property, Plant and Equipment and Accumulated Depreciation | 740 |
| AP | AP Vids!6 | AP-01 | 01-04 Problem 2 Number 1-3 | 610 |
| AP | AP Vids!7 | AP-01 | 01-05 Problem 2 Number 4 | 761 |
| AP | AP Vids!8 | AP-01 | 01-06 Problem 2 Number 5 and 6 | 1061 |
| AP | AP Vids!9 | AP-01 | 01-07 Problem 3 | 2141 |
| AP | AP Vids!10 | AP-01 | 01-08 Problem 4 | 1307 |
| AP | AP Vids!11 | AP-01 | 01-09 Problem 5 | 743 |
| AP | AP Vids!12 | AP-01 | 01-10 Problem 6 | 962 |
| AP | AP Vids!16 | AP-02 | 02-01 Correction of Errors | 2759 |
| AP | AP Vids!17 | AP-02 | 02-02 Solution Problem 1 | 417 |
| AP | AP Vids!18 | AP-02 | 02-03 Solution Problem 2 | 1756 |
| AP | AP Vids!19 | AP-02 | 02-04 Solution Problem 3 | 1446 |
| AP | AP Vids!20 | AP-02 | 02-05 Solution Problem 4 | 1084 |
| AP | AP Vids!21 | AP-02 | 02-06 Solution Problem 5 | 1160 |
| AP | AP Vids!22 | AP-02 | 02-07 Solution Problem 7 | 1350 |
| AP | AP Vids!23 | AP-02 | 02-08 Solution Problem 8 | 2534 |
| AP | AP Vids!24 | AP-02 | 02-09 Solution Problem 9 | 1798 |
| AP | AP Vids!28 | AP-03 | 03-01 Shareholders' Equity | 1530 |
| AP | AP Vids!29 | AP-03 | 03-02 Solution Problem 1 | 552 |
| AP | AP Vids!30 | AP-03 | 03-03 Solution Problem 2 | 470 |
| AP | AP Vids!31 | AP-03 | 03-04 Solution Problem 3 | 544 |
| AP | AP Vids!32 | AP-03 | 03-05 Solution Problem 4 | 220 |
| AP | AP Vids!33 | AP-03 | 03-06 Solution Problems 5-7 | 890 |
| AP | AP Vids!34 | AP-03 | 03-07 Solution Problems 8-10 | 1398 |
| AP | AP Vids!35 | AP-03 | 03-08 Treasury Shares | 1029 |
| AP | AP Vids!36 | AP-03 | 03-09 Derecognition of Share Capital with Solution to Problem #14 | 804 |
| AP | AP Vids!37 | AP-03 | 03-10 Recapitalization with Solution to Problem #15 | 933 |
| AP | AP Vids!38 | AP-03 | 03-11 Share Warrants | 1217 |
| AP | AP Vids!39 | AP-03 | 03-12 Dividends to Problem 20 | 2100 |
| AP | AP Vids!40 | AP-03 | 03-13 Non-cash to Problem 22 | 1088 |
| AP | AP Vids!41 | AP-03 | 03-14 Fractional Share Dividends | 430 |
| AP | AP Vids!42 | AP-03 | 03-15 Non-cash to Problem 23 | 1949 |
| AP | AP Vids!43 | AP-03 | 03-16 Solution Problem 24 | 1094 |
| AP | AP Vids!44 | AP-03 | 03-17 Problem 25 and 26 | 2516 |
| AP | AP Vids!45 | AP-03 | 03-18 Solution Problem 27 | 569 |
| AP | AP Vids!51 | AP-04 | 04-01 Share-Based Payment Transaction | 2324 |
| AP | AP Vids!52 | AP-04 | 04-02 Problem Number 1 | 914 |
| AP | AP Vids!53 | AP-04 | 04-03 Problem Numbers 2 and 3 | 1285 |
| AP | AP Vids!54 | AP-04 | 04-04 Problem Numbers 4 to 6 | 1993 |
| AP | AP Vids!55 | AP-04 | 04-05 Problem Numbers 7 And 8 | 2039 |
| AP | AP Vids!56 | AP-04 | 04-06 Modifications, Cancellations and Settlements | 762 |
| AP | AP Vids!57 | AP-04 | 04-07 Cash-Settled | 145 |
| AP | AP Vids!58 | AP-04 | 04-08 Problem Number 13 | 1029 |
| AP | AP Vids!59 | AP-04 | 04-09 Share-Based Payment with Cash Alternative | 243 |
| AP | AP Vids!60 | AP-04 | 04-10 Share-Based Payment with Cash Alternative- Granted Simultaneously | 1288 |
| AP | AP Vids!61 | AP-04 | 04-11 Problem Numbers 7 and 8 | 2039 |
| AP | AP Vids!62 | AP-04 | 04-12 Problem Numbers 9 and 10 | 1233 |
| AP | AP Vids!63 | AP-04 | 04-13 Problem Numbers 11 and 12 | 2696 |
| AP | AP Vids!64 | AP-04 | 04-14 Problem 14 | 871 |
| AP | AP Vids!65 | AP-04 | 04-15 Problem 15 to 17 | 3167 |
| AP | AP Vids!66 | AP-04 | 04-16 Problem Number 18 | 934 |
| AP | AP Vids!71 | AP-05 | 05-01 Cash and Cash Equivalents | 2381 |
| AP | AP Vids!72 | AP-05 | 05-02 Problem 1 | 749 |
| AP | AP Vids!73 | AP-05 | 05-03 Problems 2 and 3 | 724 |
| AP | AP Vids!74 | AP-05 | 05-04 Problem 4 | 321 |
| AP | AP Vids!75 | AP-05 | 05-05 Petty Cash Fund | 943 |
| AP | AP Vids!76 | AP-05 | 05-06 Problem 5 and 6 | 1609 |
| AP | AP Vids!77 | AP-05 | 05-07 Bank Reconciliation | 1376 |
| AP | AP Vids!78 | AP-05 | 05-08 Problem 7 | 833 |
| AP | AP Vids!79 | AP-05 | 05-09 Proof of Cash Part 1 | 3556 |
| AP | AP Vids!80 | AP-05 | 05-10 Problem 8 and 9 | 1345 |
| AP | AP Vids!81 | AP-05 | 05-11 Proof of Cash Part 2 | 1168 |
| AP | AP Vids!82 | AP-05 | 05-12 Problem 10 | 813 |
| AP | AP Vids!83 | AP-05 | 05-13 Problem 11 | 664 |
| AP | AP Vids!84 | AP-05 | 05-14 Problem 12 | 1420 |
| AP | AP Vids!85 | AP-05 | 05-15 Problem 13 | 1695 |
| AP | AP Vids!86 | AP-05 | 05-16 Problem 14 | 2292 |
| AP | AP Vids!87 | AP-05 | 05-17 Problem 15 | 1855 |
| AP | AP Vids!88 | AP-05 | 05-18 Problem 16 | 1537 |
| AP | AP Vids!89 | AP-05 | 05-19 Problem 17 | 1159 |
| AP | AP Vids!90 | AP-05 | 05-20 Special Audit Consideration | 764 |
| AP | AP Vids!91 | AP-05 | 05-21 Problem 18 | 700 |
| AP | AP Vids!95 | AP-06 | 06-01 Audit of Receivables Part 1 | 1645 |
| AP | AP Vids!96 | AP-06 | 06-02 Problem 1 | 790 |
| AP | AP Vids!97 | AP-06 | 06-03 Problem 2 | 1376 |
| AP | AP Vids!98 | AP-06 | 06-04 Problem 3 | 764 |
| AP | AP Vids!99 | AP-06 | 06-05 Problem 4 | 995 |
| AP | AP Vids!100 | AP-06 | 06-06 Problem 5 | 1560 |
| AP | AP Vids!101 | AP-06 | 06-07 Problem 6 | 1570 |
| AP | AP Vids!102 | AP-06 | 06-08 Audit of Receivables Part 2 | 1626 |
| AP | AP Vids!103 | AP-06 | 06-09 Problem 7 | 919 |
| AP | AP Vids!104 | AP-06 | 06-10 Audit of Receivables Part 3 | 271 |
| AP | AP Vids!105 | AP-06 | 06-11 Notes Receivables | 707 |
| AP | AP Vids!106 | AP-06 | 06-12 Loan Receivables | 793 |
| AP | AP Vids!107 | AP-06 | 06-13 Loan Impairment | 415 |
| AP | AP Vids!108 | AP-06 | 06-14 Problem 8 | 571 |
| AP | AP Vids!109 | AP-06 | 06-15 Problem 9 | 1180 |
| AP | AP Vids!110 | AP-06 | 06-16 Problem 10 | 1962 |
| AP | AP Vids!111 | AP-06 | 06-17 Problem 11 | 1473 |
| AP | AP Vids!112 | AP-06 | 06-18 Problem 12 | 876 |
| AP | AP Vids!113 | AP-06 | 06-19 Problem 13 | 1517 |
| AP | AP Vids!114 | AP-06 | 06-20 Problem 14 | 652 |
| AP | AP Vids!115 | AP-06 | 06-21 Problem 15 | 1448 |
| AP | AP Vids!121 | AP-07 | 07-01 Inventories | 2812 |
| AP | AP Vids!122 | AP-07 | 07-02 Problem 1 | 1418 |
| AP | AP Vids!123 | AP-07 | 07-03 Problem 2 | 1082 |
| AP | AP Vids!124 | AP-07 | 07-04 Cost Formula | 1245 |
| AP | AP Vids!125 | AP-07 | 07-05 Problem 3 | 1155 |
| AP | AP Vids!126 | AP-07 | 07-06 Problem 4 | 1546 |
| AP | AP Vids!127 | AP-07 | 07-07 Problem 5 | 1143 |
| AP | AP Vids!128 | AP-07 | 07-08 Problem 6 | 485 |
| AP | AP Vids!129 | AP-07 | 07-09 Problem 7 | 2006 |
| AP | AP Vids!130 | AP-07 | 07-10 Inventory Estimation | 660 |
| AP | AP Vids!131 | AP-07 | 07-11 Problem 8 | 1626 |
| AP | AP Vids!132 | AP-07 | 07-12 Problem 9 | 1826 |
| AP | AP Vids!133 | AP-07 | 07-13 Retail Inventory | 892 |
| AP | AP Vids!134 | AP-07 | 07-14 Problem 10 | 930 |
| AP | AP Vids!135 | AP-07 | 07-15 Special Audit Consideration for Inventory | 1842 |
| AP | AP Vids!136 | AP-07 | 07-16 Problem 11 | 928 |
| AP | AP Vids!137 | AP-07 | 07-17 Inventories and Agriculture | 3313 |
| AP | AP Vids!138 | AP-07 | 07-18 Problem 12 | 837 |
| AP | AP Vids!139 | AP-07 | 07-19 Problem 13 | 1322 |
| AP | AP Vids!143 | AP-08 | 08-01 Investment in Equity Securities | 2767 |
| AP | AP Vids!144 | AP-08 | 08-02 Problem 1 and 2 | 1137 |
| AP | AP Vids!145 | AP-08 | 08-03 Classification of Financial Assets | 1987 |
| AP | AP Vids!146 | AP-08 | 08-04 Problem 3 | 1299 |
| AP | AP Vids!147 | AP-08 | 08-05 Problem 4 | 919 |
| AP | AP Vids!148 | AP-08 | 08-06 Dividends | 963 |
| AP | AP Vids!149 | AP-08 | 08-07 Problems 5 to 7 | 1787 |
| AP | AP Vids!150 | AP-08 | 08-08 Stock Split | 302 |
| AP | AP Vids!151 | AP-08 | 08-09 Problem 8 | 727 |
| AP | AP Vids!152 | AP-08 | 08-10 Stock Rights | 576 |
| AP | AP Vids!153 | AP-08 | 08-11 Problem 9 to 10 | 602 |
| AP | AP Vids!154 | AP-08 | 08-12 Problem 11- Equity Investment | 1473 |
| AP | AP Vids!155 | AP-08 | 08-13 Problem 12- Equity | 1000 |
| AP | AP Vids!156 | AP-08 | 08-14 Investment in Associate Part 1 | 1481 |
| AP | AP Vids!157 | AP-08 | 08-15 Problem 13 | 3167 |
| AP | AP Vids!158 | AP-08 | 08-16 Having Outstanding Preference Shares | 260 |
| AP | AP Vids!159 | AP-08 | 08-17 Problem 14 | 734 |
| AP | AP Vids!160 | AP-08 | 08-18 Investment in Associate-STEP Acquisition | 277 |
| AP | AP Vids!161 | AP-08 | 08-19 Problem 15 | 1047 |
| AP | AP Vids!162 | AP-08 | 08-20 Investment in Associate- Discontinuance of Equity Method | 583 |
| AP | AP Vids!163 | AP-08 | 08-21 Problem 16 | 1939 |
| AP | AP Vids!164 | AP-08 | 08-22 Investment in Associate- Deemed Disposal | 500 |
| AP | AP Vids!165 | AP-08 | 08-23 Problem 17 | 1197 |
| AP | AP Vids!166 | AP-08 | 08-24 Investement in Associate-Having Heavy Losses | 1202 |
| AP | AP Vids!167 | AP-08 | 08-25 Problem 18 | 1239 |
| AP | AP Vids!168 | AP-08 | 08-26 Problem 19 | 1166 |
| AP | AP Vids!173 | AP-09 | 09-01 Investment in Debt Securities | 1821 |
| AP | AP Vids!174 | AP-09 | 09-02 Problem 1 | 3048 |
| AP | AP Vids!175 | AP-09 | 09-03 Problem 2 to 3 | 1051 |
| AP | AP Vids!176 | AP-09 | 09-04 Investment in Debt-Reclassification | 460 |
| AP | AP Vids!177 | AP-09 | 09-05 Problem 4 Scenario 1 | 1466 |
| AP | AP Vids!178 | AP-09 | 09-06 Problem 4 Scenario 2 | 1594 |
| AP | AP Vids!179 | AP-09 | 09-07 Problem 4 Scenario 3 | 951 |
| AP | AP Vids!180 | AP-09 | 09-08 Problem 5 | 950 |
| AP | AP Vids!181 | AP-09 | 09-09 Expected Credit Loss Model | 1286 |
| AP | AP Vids!182 | AP-09 | 09-10 Problem 6 | 1937 |
| AP | AP Vids!183 | AP-09 | 09-11 Problem 7 | 394 |
| AP | AP Vids!184 | AP-09 | 09-12 Problem 8 | 1291 |
| AP | AP Vids!185 | AP-09 | 09-13 Problem 9 | 1150 |
| AP | AP Vids!186 | AP-09 | 09-14 Problem 10 | 609 |
| AP | AP Vids!187 | AP-09 | 09-15 Illustrative Example 1 | 2536 |
| AP | AP Vids!188 | AP-09 | 09-16 Illustrative Example 2 | 1219 |
| AP | AP Vids!192 | AP-10 | 10-01 Notes and Bonds Payable Part 1 | 523 |
| AP | AP Vids!193 | AP-10 | 10-02 Problem 1 | 523 |
| AP | AP Vids!194 | AP-10 | 10-03 Notes and Bonds Payable Part 2 | 751 |
| AP | AP Vids!195 | AP-10 | 10-04 problem 2 | 706 |
| AP | AP Vids!196 | AP-10 | 10-05 Notes and Bonds Payable Part 3 | 1157 |
| AP | AP Vids!197 | AP-10 | 10-06 Problem 3 | 216 |
| AP | AP Vids!198 | AP-10 | 10-07 Problem 4 | 406 |
| AP | AP Vids!199 | AP-10 | 10-08 Problem 5 | 187 |
| AP | AP Vids!200 | AP-10 | 10-09 Problem 6 | 683 |
| AP | AP Vids!201 | AP-10 | 10-10 Notes and Bonds Payable Part 4 | 238 |
| AP | AP Vids!202 | AP-10 | 10-11 problem 7 | 1284 |
| AP | AP Vids!203 | AP-10 | 10-12 Notes and Bonds Payable Part 5 | 516 |
| AP | AP Vids!204 | AP-10 | 10-13 Problem 8 | 1541 |
| AP | AP Vids!205 | AP-10 | 10-14 Notes and Bonds Payable Part 6 | 192 |
| AP | AP Vids!206 | AP-10 | 10-15 Problems 9 and 10 | 678 |
| AP | AP Vids!207 | AP-10 | 10-16 Problem 11 | 487 |
| AP | AP Vids!208 | AP-10 | 10-17 Notes and Bonds Payable Part 7 | 251 |
| AP | AP Vids!209 | AP-10 | 10-18 Problem 12 | 471 |
| AP | AP Vids!213 | AP-11 | 11-01 Property, Plant and Equipment Part 1 | 1789 |
| AP | AP Vids!214 | AP-11 | 11-02 Problem 1 | 316 |
| AP | AP Vids!215 | AP-11 | 11-03 Property, Plant and Equipment Part 2 | 1775 |
| AP | AP Vids!216 | AP-11 | 11-04 Problem 2 | 1292 |
| AP | AP Vids!217 | AP-11 | 11-05 Problem 3 | 1180 |
| AP | AP Vids!218 | AP-11 | 11-06 Property, Plant and Equipment Part 3 | 1499 |
| AP | AP Vids!219 | AP-11 | 11-07 Problems 4 to 10 | 2233 |
| AP | AP Vids!220 | AP-11 | 11-08 Property, Plant and Equipment Part 4 | 1517 |
| AP | AP Vids!221 | AP-11 | 11-09 Problems 11 to 12 | 803 |
| AP | AP Vids!222 | AP-11 | 11-10 Problems 13 to 14 | 1375 |
| AP | AP Vids!223 | AP-11 | 11-11 Property, Plant and Equipment Part 5 | 2058 |
| AP | AP Vids!224 | AP-11 | 11-12 Problem 15 | 1026 |
| AP | AP Vids!225 | AP-11 | 11-13 Problem 16 Case 1 to 2 | 598 |
| AP | AP Vids!226 | AP-11 | 11-14 Problem 16 Case 3 | 780 |
| AP | AP Vids!227 | AP-11 | 11-15 Problem 17 Case 1 | 1225 |
| AP | AP Vids!228 | AP-11 | 11-16 Problem 17 Case 2 | 881 |
| AP | AP Vids!229 | AP-11 | 11-17 Problem 18 | 477 |
| AP | AP Vids!230 | AP-11 | 11-18 Property, Plant and Equipment Part 6 | 624 |
| AP | AP Vids!231 | AP-11 | 11-19 Property, Plant and Equipment Part 7 | 1632 |
| AP | AP Vids!232 | AP-11 | 11-20 Problem 19 | 405 |
| AP | AP Vids!233 | AP-11 | 11-21 Problem 20 | 2220 |
| AP | AP Vids!234 | AP-11 | 11-22 Problem 21 | 542 |
| AP | AP Vids!235 | AP-11 | 11-23 Problem 22 | 1400 |
| AP | AP Vids!236 | AP-11 | 11-24 problem 23 | 1311 |
| AP | AP Vids!237 | AP-11 | 11-25 Wasting Asset | 1694 |
| AP | AP Vids!238 | AP-11 | 11-26 Problem 24 to 26 | 1076 |
| AP | AP Vids!239 | AP-11 | 11-27 Problem 27 | 558 |
| AP | AP Vids!240 | AP-11 | 11-28 Special Audit Consideration | 1065 |
| AP | AP Vids!241 | AP-11 | 11-29 Problem 28 | 866 |
| AP | AP Vids!245 | AP-12 | 12-01 Intangible Assets Part 1 | 2046 |
| AP | AP Vids!246 | AP-12 | 12-02 Problem 1 | 767 |
| AP | AP Vids!247 | AP-12 | 12-03 Problem 2 | 554 |
| AP | AP Vids!248 | AP-12 | 12-04 Intangible Assets Part 2 | 1665 |
| AP | AP Vids!249 | AP-12 | 12-05 Problem 3 | 452 |
| AP | AP Vids!250 | AP-12 | 12-06 Problem 4 | 644 |
| AP | AP Vids!251 | AP-12 | 12-07 Intangible Assets Part 3 | 333 |
| AP | AP Vids!252 | AP-12 | 12-08 Problem 5 | 473 |
| AP | AP Vids!253 | AP-12 | 12-09 Intangible Assets Part 4 | 787 |
| AP | AP Vids!254 | AP-12 | 12-10 Problem 6 | 411 |
| AP | AP Vids!255 | AP-12 | 12-11 Intangible Assets Part 5 | 899 |
| AP | AP Vids!256 | AP-12 | 12-12 Problem 7 | 974 |
| AP | AP Vids!257 | AP-12 | 12-13 Problem 8 | 284 |
| AP | AP Vids!258 | AP-12 | 12-14 Problem 9 | 654 |
| AP | AP Vids!259 | AP-12 | 12-15 Problem 10 | 993 |
| AP | AP Vids!260 | AP-12 | 12-16 Problem 11 | 589 |
| AP | AP Vids!261 | AP-12 | 12-17 Problem 12 | 540 |
| AP | AP Vids!262 | AP-12 | 12-18 Problem 13 | 980 |
| AP | AP Vids!263 | AP-12 | 12-19 Intangible Assets Part 6 | 1058 |
| AP | AP Vids!264 | AP-12 | 12-20 Problem 14 | 528 |
| AP | AP Vids!269 | AP-13 | 13-01 Investment Property Part 1 | 879 |
| AP | AP Vids!270 | AP-13 | 13-02 Problem 1 | 573 |
| AP | AP Vids!271 | AP-13 | 13-03 Problems 2 to 4 | 659 |
| AP | AP Vids!272 | AP-13 | 13-04 Investment Property Part 2 | 1194 |
| AP | AP Vids!273 | AP-13 | 13-05 Problem 5 | 968 |
| AP | AP Vids!274 | AP-13 | 13-06 Investment Property Part 3 | 1112 |
| AP | AP Vids!275 | AP-13 | 13-07 Problem 6 | 456 |
| AP | AP Vids!276 | AP-13 | 13-08 Problem 7 | 348 |
| AP | AP Vids!277 | AP-13 | 13-09 Problem 8 | 431 |
| AP | AP Vids!281 | AP-14 | 14-01 Revaluation, Impairment and Non-Current Asset Held for Sale | 1143 |
| AP | AP Vids!282 | AP-14 | 14-02 Problem 1 | 937 |
| AP | AP Vids!283 | AP-14 | 14-03 PAS 36: Impairment of Assets | 1264 |
| AP | AP Vids!284 | AP-14 | 14-04 Problem 2 | 1127 |
| AP | AP Vids!285 | AP-14 | 14-05 Problem 3 | 1066 |
| AP | AP Vids!286 | AP-14 | 14-06 Problem 4 | 826 |
| AP | AP Vids!287 | AP-14 | 14-07 Cash Generating Units | 909 |
| AP | AP Vids!288 | AP-14 | 14-08 Problem 5 | 1904 |
| AP | AP Vids!289 | AP-14 | 14-09 Non-Current Asset Held for Sale | 1104 |
| AP | AP Vids!290 | AP-14 | 14-10 Problem 6 | 557 |
| AP | AP Vids!291 | AP-14 | 14-11 Problem 7 | 1136 |
| AP | AP Vids!292 | AP-14 | 14-12 Problem 8 | 872 |
| AP | AP Vids!293 | AP-14 | 14-13 Problem 9 | 1532 |
| AP | AP Vids!298 | AP-15 | 15-01 Current Liabilities | 1160 |
| AP | AP Vids!299 | AP-15 | 15-02 Problems 1 and 2 | 501 |
| AP | AP Vids!300 | AP-15 | 15-03 Trade Accounts Payable | 693 |
| AP | AP Vids!301 | AP-15 | 15-04 Problem 3 | 701 |
| AP | AP Vids!302 | AP-15 | 15-05 Problem 4 | 1109 |
| AP | AP Vids!303 | AP-15 | 15-06 Problem 5 | 592 |
| AP | AP Vids!304 | AP-15 | 15-07 Problem 6 | 537 |
| AP | AP Vids!305 | AP-15 | 15-08 Provision | 969 |
| AP | AP Vids!306 | AP-15 | 15-09 Problems 7 and 8 | 779 |
| AP | AP Vids!307 | AP-15 | 15-10 Problem 9 | 735 |
| AP | AP Vids!308 | AP-15 | 15-11 Problem 10 | 579 |
| AP | AP Vids!309 | AP-15 | 15-12 Problem 11 | 869 |
| AP | AP Vids!310 | AP-15 | 15-13 Problem 12 | 1050 |
| AP | AP Vids!311 | AP-15 | 15-14 Special Audit Consideration for Payables | 459 |
| AP | AP Vids!312 | AP-15 | 15-15 Problem 13 | 543 |
| AP | AP Vids!316 | AP-16 | 16-01 Accounting for Income Tax Part 1 | 1596 |
| AP | AP Vids!317 | AP-16 | 16-02 Problem 1 | 831 |
| AP | AP Vids!318 | AP-16 | 16-03 Problem 2 | 1049 |
| AP | AP Vids!319 | AP-16 | 16-04 Problem 3 | 688 |
| AP | AP Vids!320 | AP-16 | 16-05 Accounting for Income Tax Part 2 | 221 |
| AP | AP Vids!321 | AP-16 | 16-06 Problem 4 | 1443 |
| AP | AP Vids!322 | AP-16 | 16-07 Problem 5 | 149 |
| AP | AP Vids!323 | AP-16 | 16-08 Accounting for Income Tax Part 3 | 440 |
| AP | AP Vids!324 | AP-16 | 16-09 Problem 6 | 694 |
| AP | AP Vids!325 | AP-16 | 16-10 Problem 7 | 1702 |
| AP | AP Vids!331 | AP-17 | 17-01 Employee Benefits | 857 |
| AP | AP Vids!332 | AP-17 | 17-02 Problem 1 | 634 |
| AP | AP Vids!333 | AP-17 | 17-03 Post Employment Benefits | 866 |
| AP | AP Vids!334 | AP-17 | 17-04 Problem 2 | 1184 |
| AP | AP Vids!335 | AP-17 | 17-05 Statement of Financial Position | 975 |
| AP | AP Vids!336 | AP-17 | 17-06 Problems 3 and 4 | 407 |
| AP | AP Vids!337 | AP-17 | 17-07 Benefit Expense | 879 |
| AP | AP Vids!338 | AP-17 | 17-08 Problem 5 | 403 |
| AP | AP Vids!339 | AP-17 | 17-09 Problem 6 | 287 |
| AP | AP Vids!340 | AP-17 | 17-10 Procedural Approach | 505 |
| AP | AP Vids!341 | AP-17 | 17-11 Problem 7 | 968 |
| AP | AP Vids!342 | AP-17 | 17-12 Problem 8 | 939 |
| AP | AP Vids!343 | AP-17 | 17-13 Problem 9 | 1287 |
| AP | AP Vids!344 | AP-17 | 17-14 Problem 10 | 1031 |
| AP | AP Vids!348 | AP-18 | 18-01 Statement of Cash Flows Part 1 | 2900 |
| AP | AP Vids!349 | AP-18 | 18-02 Statement of Cash Flows Part 2 | 937 |
| AP | AP Vids!350 | AP-18 | 18-03 Problem 1 | 780 |
| AP | AP Vids!351 | AP-18 | 18-04 Problem 2 | 1023 |
| AP | AP Vids!352 | AP-18 | 18-05 Problem 3 | 1116 |
| AP | AP Vids!353 | AP-18 | 18-06 Problem 4 | 1859 |
| AP | AP Vids!354 | AP-18 | 18-07 Problem 5 | 2433 |
| AP | AP Vids!355 | AP-18 | 18-08 Problem 6 | 2470 |
| AP | AP Vids!356 | AP-18 | 18-09 Problem 7 | 1183 |
| AP | AP Vids!361 | AP-19 | 19-01 Statement of Financial Position and P/L and OCI | 1365 |
| AP | AP Vids!362 | AP-19 | 19-02 Problem 1 | 1472 |
| AP | AP Vids!363 | AP-19 | 19-03 Problem 2 | 912 |
| AP | AP Vids!364 | AP-19 | 19-04 Statement of Profit or Loss and Other Comprehensive Income | 1633 |
| AP | AP Vids!365 | AP-19 | 19-05 Problem 3 | 433 |
| AP | AP Vids!366 | AP-19 | 19-06 Problem 4 | 1292 |
| AP | AP Vids!367 | AP-19 | 19-07 Problem 5 | 1095 |
| AP | AP Vids!368 | AP-19 | 19-08 Problem 6 | 2431 |
| AP | AP Vids!372 | AP-20 | 20-01 Leases Part I | 1681 |
| AP | AP Vids!373 | AP-20 | 20-02 Problem 1 | 1568 |
| AP | AP Vids!374 | AP-20 | 20-03 Leases Part II | 194 |
| AP | AP Vids!375 | AP-20 | 20-04 Problem 2 | 274 |
| AP | AP Vids!376 | AP-20 | 20-05 Problem 3 | 457 |
| AP | AP Vids!377 | AP-20 | 20-06 Problem 4 | 498 |
| AP | AP Vids!378 | AP-20 | 20-07 Leases Part III | 314 |
| AP | AP Vids!379 | AP-20 | 20-08 Problem 5 | 240 |
| AP | AP Vids!380 | AP-20 | 20-09 Leases Part IV | 528 |
| AP | AP Vids!381 | AP-20 | 20-10 Problem 6 | 1210 |
| AP | AP Vids!382 | AP-20 | 20-11 Problem 7 | 262 |
| AP | AP Vids!383 | AP-20 | 20-12 Problem 8 | 171 |
| AP | AP Vids!384 | AP-20 | 20-13 Leases Part V | 541 |
| AP | AP Vids!385 | AP-20 | 20-14 Problem 9 | 907 |
| AP | AP Vids!386 | AP-20 | 20-15 Leases Part VI | 252 |
| AP | AP Vids!387 | AP-20 | 20-16 Problem 10 | 576 |
| AP | AP Vids!388 | AP-20 | 20-17 Problem 11 | 340 |
| AP | AP Vids!389 | AP-20 | 20-18 Leases Part VII | 757 |
| AP | AP Vids!390 | AP-20 | 20-19 Problem 12 | 94 |
| AP | AP Vids!391 | AP-20 | 20-20 Problem 13 | 896 |
| AP | AP Vids!392 | AP-20 | 20-21 Leases Part VIII | 303 |
| AP | AP Vids!393 | AP-20 | 20-22 Problem 14 | 729 |
| AP | AP Vids!394 | AP-20 | 20-23 Leases Part IX | 444 |
| AP | AP Vids!395 | AP-20 | 20-24 Problem 15 | 2278 |
| RFBT | RFBT Vids!3 | RFBT-01 | 01-01 Obligations in General | 845 |
| RFBT | RFBT Vids!4 | RFBT-01 | 01-02 Sources of Obligations | 1809 |
| RFBT | RFBT Vids!5 | RFBT-01 | 01-03 Kinds of Obligations Part I | 2191 |
| RFBT | RFBT Vids!6 | RFBT-01 | 01-04 Kinds of Obligations Part II | 2934 |
| RFBT | RFBT Vids!7 | RFBT-01 | 01-05 Nature and Effects and Remedies in Case of Breach | 1261 |
| RFBT | RFBT Vids!8 | RFBT-01 | 01-06 Specific Circumstances Affecting and Obligation | 1455 |
| RFBT | RFBT Vids!9 | RFBT-01 | 01-07 Payment or Performance | 1619 |
| RFBT | RFBT Vids!10 | RFBT-01 | 01-08 Special Forms of Payment | 1560 |
| RFBT | RFBT Vids!11 | RFBT-01 | 01-09 Loss or Impossibility | 828 |
| RFBT | RFBT Vids!12 | RFBT-01 | 01-10 Condonation and Confusion | 616 |
| RFBT | RFBT Vids!13 | RFBT-01 | 01-11 Compensation | 1082 |
| RFBT | RFBT Vids!14 | RFBT-01 | 01-12 Novation | 773 |
| RFBT | RFBT Vids!19 | RFBT-02 | 02-01 Definition to Classification | 3313 |
| RFBT | RFBT Vids!20 | RFBT-02 | 02-02 Essential Elements of Contracts | 5090 |
| RFBT | RFBT Vids!21 | RFBT-02 | 02-03 Interpretation of Contracts to Defective Contracts | 2980 |
| RFBT | RFBT Vids!26 | RFBT-03 | 03-01 Nature of Contract of Sale by Auction | 4821 |
| RFBT | RFBT Vids!27 | RFBT-03 | 03-02 Recto Law to Condominium Act | 1621 |
| RFBT | RFBT Vids!28 | RFBT-03 | 03-03 Obligations of a Vendor | 1939 |
| RFBT | RFBT Vids!29 | RFBT-03 | 03-04 Unpaid Seller to Obligations of Vendee | 3602 |
| RFBT | RFBT Vids!30 | RFBT-03 | 03-05 Extinguishment of Contract of Sale | 1504 |
| RFBT | RFBT Vids!35 | RFBT-04 | 05-01 Introduction to Credit Transactions to Pledge | 2757 |
| RFBT | RFBT Vids!36 | RFBT-04 | 05-02 Chattel Mortgage to Distinctions | 832 |
| RFBT | RFBT Vids!37 | RFBT-04 | 05-03 Real Estate Mortgage to Redemption | 1184 |
| RFBT | RFBT Vids!42 | RFBT-05 | 05-01 Anti-Bouncing Checks Law | 830 |
| RFBT | RFBT Vids!46 | RFBT-06 | 06-01 Declaration of Policy, Construction and Definition of Terms | 1052 |
| RFBT | RFBT Vids!47 | RFBT-06 | 06-02 Protection Against Deceptive, Unfair and Unconscionable Sales or Practices | 1038 |
| RFBT | RFBT Vids!48 | RFBT-06 | 06-03 Labeling and Fair Packaging Part 1 | 1109 |
| RFBT | RFBT Vids!49 | RFBT-06 | 06-04 Labeling and Fair Packaging Part 2 | 682 |
| RFBT | RFBT Vids!50 | RFBT-06 | 06-05 Consumer Product and Service Warranty | 747 |
| RFBT | RFBT Vids!51 | RFBT-06 | 06-06 Price Tag Requirement | 208 |
| RFBT | RFBT Vids!52 | RFBT-06 | 06-07 Lemon Law | 1230 |
| RFBT | RFBT Vids!56 | RFBT-07 | 07-01 Financial Rehabilitation and Insolvency Act in General | 814 |
| RFBT | RFBT Vids!57 | RFBT-07 | 07-02 Suspension of Payments | 525 |
| RFBT | RFBT Vids!58 | RFBT-07 | 07-03 Rehabilitation Part 1 | 910 |
| RFBT | RFBT Vids!59 | RFBT-07 | 07-04 Rehabilitation Part 2 | 832 |
| RFBT | RFBT Vids!60 | RFBT-07 | 07-05 Pre-Negotiated Rehabilitation | 1194 |
| RFBT | RFBT Vids!61 | RFBT-07 | 07-06 Liquidation Part 1 | 917 |
| RFBT | RFBT Vids!62 | RFBT-07 | 07-07 Liquidation Part 2 | 587 |
| RFBT | RFBT Vids!66 | RFBT-08 | 08-01 Philippine Competition Act Part 1 | 2220 |
| RFBT | RFBT Vids!67 | RFBT-08 | 08-02 Philippine Competition Act Part 2 | 1195 |
| RFBT | RFBT Vids!72 | RFBT-09 | 09-01 Government Procurement Act Part 1 | 1257 |
| RFBT | RFBT Vids!73 | RFBT-09 | 09-02 Government Procurement Act Part 2 | 914 |
| RFBT | RFBT Vids!74 | RFBT-09 | 09-03 Government Procurement Act Part 3 | 1742 |
| RFBT | RFBT Vids!75 | RFBT-09 | 09-04 Government Procurement Act Part 4 | 1379 |
| RFBT | RFBT Vids!80 | RFBT-10 | 10-01 Nature to Profit and Loss Sharing | 2786 |
| RFBT | RFBT Vids!81 | RFBT-10 | 10-02 Rights and Obligations of Partnership and Partners | 1209 |
| RFBT | RFBT Vids!82 | RFBT-10 | 10-03 Obligations to 3rd Persons to Dissolution | 2359 |
| RFBT | RFBT Vids!83 | RFBT-10 | 10-04 Limited Partnership | 1079 |
| RFBT | RFBT Vids!88 | RFBT-11 | 11-01 Part I | 3755 |
| RFBT | RFBT Vids!89 | RFBT-11 | 11-02 Part II | 418 |
| RFBT | RFBT Vids!90 | RFBT-11 | 11-03 Part III | 2651 |
| RFBT | RFBT Vids!91 | RFBT-11 | 11-04 Part IV | 535 |
| RFBT | RFBT Vids!92 | RFBT-11 | 11-05 Part V | 2130 |
| RFBT | RFBT Vids!93 | RFBT-11 | 11-06 Part VI | 1439 |
| RFBT | RFBT Vids!94 | RFBT-11 | 11-07 Part VII | 867 |
| RFBT | RFBT Vids!95 | RFBT-11 | 11-08 Part VIII | 1694 |
| RFBT | RFBT Vids!96 | RFBT-11 | 11-09 Part IX | 1223 |
| RFBT | RFBT Vids!97 | RFBT-11 | 11-10 Part X | 1286 |
| RFBT | RFBT Vids!98 | RFBT-11A | 11-11 Securities Regulation Code | 2993 |
| RFBT | RFBT Vids!99 | RFBT-11A | 11-15 Rights of a Stockholder | 1276 |
| RFBT | RFBT Vids!105 | RFBT-12 | 12-01 Concept, Elements, Characteristics and Classes of Insurance | 2267 |
| RFBT | RFBT Vids!106 | RFBT-12 | 12-02 Insurable Interest | 2082 |
| RFBT | RFBT Vids!107 | RFBT-12 | 12-03 Perfection and Rescission | 1142 |
| RFBT | RFBT Vids!108 | RFBT-12 | 12-04 Claims Settlement and Subrogation | 646 |
| RFBT | RFBT Vids!113 | RFBT-13 | 13-01 Cooperatives Part 1 | 1274 |
| RFBT | RFBT Vids!114 | RFBT-13 | 13-02 Cooperatives Part 2 | 1354 |
| RFBT | RFBT Vids!115 | RFBT-13 | 13-03 Cooperatives Part 3 | 761 |
| RFBT | RFBT Vids!116 | RFBT-13 | 13-04 Cooperatives Part 4 | 1170 |
| RFBT | RFBT Vids!117 | RFBT-13 | 13-05 Cooperatives Part 5 | 407 |
| RFBT | RFBT Vids!118 | RFBT-13 | 13-06 Cooperatives Part 6 | 621 |
| RFBT | RFBT Vids!119 | RFBT-13 | 13-07 Cooperatives Part 7 | 1738 |
| RFBT | RFBT Vids!120 | RFBT-13 | 13-08 Cooperatives Part 8 | 687 |
| RFBT | RFBT Vids!124 | RFBT-14 | 14-01 AMLA Part 1 | 1605 |
| RFBT | RFBT Vids!125 | RFBT-14 | 14-02 AMLA Part 2 | 1843 |
| RFBT | RFBT Vids!126 | RFBT-14 | 14-03 AMLA Part 3 | 978 |
| RFBT | RFBT Vids!127 | RFBT-14 | 14-04 Bank Secrecy Laws | 2045 |
| RFBT | RFBT Vids!128 | RFBT-14 | 14-05 Truth in Lending Act | 1190 |
| RFBT | RFBT Vids!129 | RFBT-14 | 14-06 PDIC Law | 1820 |
| RFBT | RFBT Vids!135 | RFBT-15 | 15-01 Trademarks I | 2008 |
| RFBT | RFBT Vids!136 | RFBT-15 | 15-02 Tradenarks II | 1743 |
| RFBT | RFBT Vids!137 | RFBT-15 | 15-03 Copyright I | 2208 |
| RFBT | RFBT Vids!138 | RFBT-15 | 15-04 Copyright II | 1901 |
| RFBT | RFBT Vids!139 | RFBT-15 | 15-05 Patent I | 1340 |
| RFBT | RFBT Vids!140 | RFBT-15 | 15-06 Patent II | 1036 |
| RFBT | RFBT Vids!141 | RFBT-15 | 15-07 Copyright | 1235 |
| RFBT | RFBT Vids!142 | RFBT-15 | 15-08 Introduction to Patents | 3280 |
| RFBT | RFBT Vids!143 | RFBT-15 | 15-09 Trademark | 2733 |
| RFBT | RFBT Vids!149 | RFBT-16 | 16-01 Data Privacy Act: Definition of Terms, Scope and Applicability and the National Privacy Commission | 1348 |
| RFBT | RFBT Vids!150 | RFBT-16 | 16-02 Data Privacy Act: Processing of Personal Information | 1912 |
| RFBT | RFBT Vids!151 | RFBT-16 | 16-03 Data Privacy Act: Rights of a Data Subject | 1577 |
| RFBT | RFBT Vids!152 | RFBT-16 | 16-04 Data Privacy Act: Security of Sensitive Personal Information in Government | 1010 |
| RFBT | RFBT Vids!156 | RFBT-17 | 17-01 E-Commerce Act: Objectives, Applicability and Definition of Terms | 819 |
| RFBT | RFBT Vids!157 | RFBT-17 | 17-02 E-Commerce Act: Legal Recognition of Electronic Data Messages, Document and Signatures | 1273 |
| RFBT | RFBT Vids!158 | RFBT-17 | 17-03 E-Commerce Act Part: Communication of Electronic Data Messages or Documents | 1767 |
| RFBT | RFBT Vids!159 | RFBT-17 | 17-04 E-Commerce Act Part: Electronic Transactions in Government | 804 |
| RFBT | RFBT Vids!163 | RFBT-18 | 18-01 Ease of Doing Business Act | 1355 |
| RFBT | RFBT Vids!167 | RFBT-19 | 19-01 Coverage and Night Shift Differential and Overtime Pay | 1888 |
| RFBT | RFBT Vids!168 | RFBT-19 | 19-02 Weekly Rest Periods and Holiday Pay | 2217 |
| RFBT | RFBT Vids!169 | RFBT-19 | 19-03 Leaves, Wages and 13th Month Pay | 1757 |
| RFBT | RFBT Vids!173 | RFBT-20 | 20-01 Declaration of Policy and Coverage | 1235 |
| RFBT | RFBT Vids!174 | RFBT-20 | 20-02 Sem of Contingency, Credited Years of Service and Average Monthly Salary Credit | 1402 |
| RFBT | RFBT Vids!175 | RFBT-20 | 20-03 Monthly Pension and Retirement Benefits | 1112 |
| RFBT | RFBT Vids!176 | RFBT-20 | 20-04 Death, Disability and Funeral Benefits | 1396 |
| RFBT | RFBT Vids!177 | RFBT-20 | 20-05 Sickness and Maternity Leave Benefits | 1467 |
| RFBT | RFBT Vids!178 | RFBT-20 | 20-06 Other Rules on Benefits and Contributions | 958 |
| RFBT | RFBT Vids!179 | RFBT-20 | 20-07 Remittance of Contibutions and Employment Records | 1026 |
| RFBT | RFBT Vids!180 | RFBT-20 | 20-08 Penal Clauses | 551 |
| TAX | TAX Vids!3 | TAX-00 | 00-00 Prelude to Create Updates | 1206 |
| TAX | TAX Vids!4 | TAX-00 | 00-01 Instruction and Changes In Final Taxes | 1169 |
| TAX | TAX Vids!5 | TAX-00 | 00-02 Create Law Part 2 | 2043 |
| TAX | TAX Vids!6 | TAX-00 | 00-03 Create Law Part 3 | 1922 |
| TAX | TAX Vids!7 | TAX-00 | 00-04 Corporate Taxpayer Create Edition | 2203 |
| TAX | TAX Vids!8 | TAX-00 | 00-05 Corporate Tax Revise | 1213 |
| TAX | TAX Vids!12 | TAX-01 | 01-01 Taxation Review Guide | 440 |
| TAX | TAX Vids!13 | TAX-01 | 01-02 Definition of Taxation - Taxation as a Power 01-03 Definition of Taxation - Taxation as a Process 01-04 Definition of Taxation - Taxation as a Mode of Government Cost Allocation | 4924 |
| TAX | TAX Vids!14 | TAX-01 | 01-05 Purpose and Scope of Taxation | 483 |
| TAX | TAX Vids!15 | TAX-01 | 01-06 Inherent Limitations of Taxation | 1682 |
| TAX | TAX Vids!16 | TAX-01 | 01-07 Constitutional Limitations of Taxation | 4634 |
| TAX | TAX Vids!17 | TAX-01 | 01-08 Situs of Taxation | 1008 |
| TAX | TAX Vids!18 | TAX-01 | 01-09 Double Taxation and its Remedies | 1177 |
| TAX | TAX Vids!19 | TAX-01 | 01-10 Escapes from Taxation | 534 |
| TAX | TAX Vids!20 | TAX-01 | 01-11 Principles of a Sound Tax System | 565 |
| TAX | TAX Vids!21 | TAX-01 | 01-12 Fundamentals Of Taxation Part 1- Drills | 2866 |
| TAX | TAX Vids!22 | TAX-01 | 01-13 Fundamentals Of Taxation Part 2-Drills | 2670 |
| TAX | TAX Vids!23 | TAX-01 | 01-14 Test Yourself Explanation- Part 1 | 1098 |
| TAX | TAX Vids!24 | TAX-01 | 01-15 Test Yourself Explanation- Part 2 | 2947 |
| TAX | TAX Vids!25 | TAX-01 | 01-16 Test Yourself Explanation- Part 3 | 1402 |
| TAX | TAX Vids!29 | TAX-02 | 02-01 Tax and Its Classifications | 852 |
| TAX | TAX Vids!30 | TAX-02 | 02-02 Tax vs. Similar Items | 1162 |
| TAX | TAX Vids!31 | TAX-02 | 02-03 Tax laws vs. Revenue Regulations vs. Rulings | 615 |
| TAX | TAX Vids!32 | TAX-02 | 02-04 Powers of the BIR and the CIR | 2176 |
| TAX | TAX Vids!33 | TAX-02 | 02-05 Fundamental Doctrines in Taxation | 2091 |
| TAX | TAX Vids!34 | TAX-02 | 02-06 Discussion of Illustratives | 2900 |
| TAX | TAX Vids!38 | TAX-03 | 03-01 Gross income with Drills | 3980 |
| TAX | TAX Vids!39 | TAX-03 | 03-02 Income Taxpayers with Drills | 3200 |
| TAX | TAX Vids!40 | TAX-03 | 03-03 Situs of income with Drills | 3751 |
| TAX | TAX Vids!41 | TAX-03 | 03-04 Accounting periods | 902 |
| TAX | TAX Vids!42 | TAX-03 | 03-05 Accounting methods | 6188 |
| TAX | TAX Vids!43 | TAX-03 | 03-06 Income Tax Compliance | 3670 |
| TAX | TAX Vids!44 | TAX-03 | 03-07 Income Tax Compliance Drills | 1355 |
| TAX | TAX Vids!48 | TAX-04 | 04-00 Prelude to Final Income Taxation | 477 |
| TAX | TAX Vids!49 | TAX-04 | 04-01 Introduction to Final Income Taxation | 1757 |
| TAX | TAX Vids!50 | TAX-04 | 04-02 Interest income | 2581 |
| TAX | TAX Vids!51 | TAX-04 | 04-03 Dividend income | 4622 |
| TAX | TAX Vids!52 | TAX-04 | 04-04 Royalty, Prizes, Winnings & Informer's Reward | 1664 |
| TAX | TAX Vids!53 | TAX-04 | 04-05 Drill continuation | 2335 |
| TAX | TAX Vids!57 | TAX-05 | 05-01 Capital assets and the scope of CGT | 1614 |
| TAX | TAX Vids!58 | TAX-05 | 05-02 15% CGT on Disposal of Domestic Stocks Directly to Buyer | 1874 |
| TAX | TAX Vids!59 | TAX-05 | 05-03 Drill: Transactional 15% CGT | 1620 |
| TAX | TAX Vids!60 | TAX-05 | 05-04 Drill: Annual 15% CGT | 1128 |
| TAX | TAX Vids!61 | TAX-05 | 05-05 15% CGT in Installment | 748 |
| TAX | TAX Vids!62 | TAX-05 | 05-06 Wash sales rule | 2037 |
| TAX | TAX Vids!63 | TAX-05 | 05-07 Tax-free Exchange of Property | 1810 |
| TAX | TAX Vids!64 | TAX-05 | 05-08 6% CGT on Disposal of Real Property Capital Asset | 1628 |
| TAX | TAX Vids!65 | TAX-05 | 05-09 Drill: Scope of the 6% CGT | 1043 |
| TAX | TAX Vids!66 | TAX-05 | 05-10 Drill: 6% CGT in installment and next topics | 3042 |
| TAX | TAX Vids!70 | TAX-06 | 06-01 Introduction to Regular Income Tax | 906 |
| TAX | TAX Vids!71 | TAX-06 | 06-02 Inclusions in Gross Income | 1943 |
| TAX | TAX Vids!72 | TAX-06 | 06-03 Exclusions in Gross Income Part I | 1631 |
| TAX | TAX Vids!73 | TAX-06 | 06-04 Exclusions in Gross Income Part II | 2530 |
| TAX | TAX Vids!74 | TAX-06 | 06-05 Special Reporting Considerations on Gross Income | 3135 |
| TAX | TAX Vids!75 | TAX-06 | 06-06 Preface to Handout- Illustration | 263 |
| TAX | TAX Vids!76 | TAX-06 | 06-07 Exercise Number 1 -3 | 2615 |
| TAX | TAX Vids!77 | TAX-06 | 06-08 Exerccise Number 4 - 7 | 2580 |
| TAX | TAX Vids!78 | TAX-06 | 06-09 Exercise Number 8 -11 | 2390 |
| TAX | TAX Vids!79 | TAX-06 | 06-10 Exercise Number 12 | 1664 |
| TAX | TAX Vids!83 | TAX-6.1 | 06.01-01 Compensation Income 1 | 4201 |
| TAX | TAX Vids!84 | TAX-6.1 | 06.01-02 Compensation Income 2 | 495 |
| TAX | TAX Vids!85 | TAX-6.1 | 06.01-03 Withholding tax on Compensation | 1330 |
| TAX | TAX Vids!86 | TAX-6.1 | 06.01-04 Illustration 1 | 3988 |
| TAX | TAX Vids!87 | TAX-6.1 | 06.01-05 Drill No. 1 to 15 | 1558 |
| TAX | TAX Vids!88 | TAX-6.1 | 06.01-06 Drill Exercise No. 16-27 | 2105 |
| TAX | TAX Vids!93 | TAX-6.2 | 06.02-01 Fringe Benefits - Lecture | 2610 |
| TAX | TAX Vids!94 | TAX-6.2 | 06.02-02 Illustration - Drill | 2232 |
| TAX | TAX Vids!95 | TAX-6.2 | 06.02-03 Illustration - Drill | 1964 |
| TAX | TAX Vids!100 | TAX-6.3 | 06.03-01 Dealings In Properties | 3349 |
| TAX | TAX Vids!101 | TAX-6.3 | 06.03-02 Illustration 1 - 3 | 1865 |
| TAX | TAX Vids!102 | TAX-6.3 | 06.03-03 Illustration 4 | 371 |
| TAX | TAX Vids!103 | TAX-6.3 | 06.03-04 Illustration 5 | 635 |
| TAX | TAX Vids!108 | TAX-07 | 07-01 Principles of Deduction | 5040 |
| TAX | TAX Vids!109 | TAX-07 | 07-02 Special Considerations on Deductions | 2634 |
| TAX | TAX Vids!110 | TAX-07 | 07-03 Illustration 1 | 1483 |
| TAX | TAX Vids!111 | TAX-07 | 07-04 Illustration 2-6 | 2543 |
| TAX | TAX Vids!115 | TAX-7.1 | 07.01-01 Itemized Deductions 1 | 1895 |
| TAX | TAX Vids!116 | TAX-7.1 | 07.01-02 Itemized Deductions 2 | 1075 |
| TAX | TAX Vids!117 | TAX-7.1 | 07.01-03 Itemized Deductions 3 | 1298 |
| TAX | TAX Vids!118 | TAX-7.1 | 07.01-04 Itemized Deductions 4 | 1064 |
| TAX | TAX Vids!119 | TAX-7.1 | 07.01-05 Itemized Deductions 5 | 2992 |
| TAX | TAX Vids!120 | TAX-7.1 | 07.01-06 Itemized Deductions 6 | 2958 |
| TAX | TAX Vids!121 | TAX-7.1 | 07.01-07 Nolco Concept | 835 |
| TAX | TAX Vids!122 | TAX-7.1 | 07.01-08 Nolco Illustration | 1297 |
| TAX | TAX Vids!123 | TAX-7.1 | 07.01-09 Special Allowable Deductions | 1683 |
| TAX | TAX Vids!124 | TAX-7.1 | 07.01-10 Problem 14 & 15 | 848 |
| TAX | TAX Vids!125 | TAX-7.1 | 07.01-11 Additional Deduction For Labor Training Expense | 377 |
| TAX | TAX Vids!129 | TAX-7.2 | 07.02-01 Optional Standard Deductions Concepts | 1549 |
| TAX | TAX Vids!130 | TAX-7.2 | 07.02-02 Illustrations 2 & 3 | 1945 |
| TAX | TAX Vids!131 | TAX-7.2 | 07.02-03 Illustration 4 | 576 |
| TAX | TAX Vids!132 | TAX-7.2 | 07.02-04 Mandatory Itemized Deductions | 659 |
| TAX | TAX Vids!138 | TAX-08 | 08-01 Narrative Summary of Basic Rules | 1378 |
| TAX | TAX Vids!139 | TAX-08 | 08-02 Illustration 1 Part I | 1672 |
| TAX | TAX Vids!140 | TAX-08 | 08-03 Illustration 1 Part II | 1898 |
| TAX | TAX Vids!141 | TAX-08 | 08-04 Illustration 2 | 549 |
| TAX | TAX Vids!142 | TAX-08 | 08-05 Illustration 2 (Purely in Business- 8% Commuted Tax Option) | 1457 |
| TAX | TAX Vids!143 | TAX-08 | 08-06 Illustration 3.1 (Regular Tax Option) | 1850 |
| TAX | TAX Vids!144 | TAX-08 | 08-07 Illustration 3.2 (8% Tax Option) | 1179 |
| TAX | TAX Vids!145 | TAX-08 | 08-08 Illustration 4 | 2841 |
| TAX | TAX Vids!146 | TAX-08 | 08-09 Estate and Trust Concept | 976 |
| TAX | TAX Vids!147 | TAX-08 | 08-10 Illustration 5 | 1182 |
| TAX | TAX Vids!148 | TAX-08 | 08-11 Illustration 6 | 967 |
| TAX | TAX Vids!152 | TAX-09 | 09-01 Corporate taxpayers Part 1 | 1597 |
| TAX | TAX Vids!153 | TAX-09 | 09-02 Corporate taxpayers Part 2 | 2886 |
| TAX | TAX Vids!154 | TAX-09 | 09-03 Corporate taxpayers Part 1 -Create | 2199 |
| TAX | TAX Vids!155 | TAX-09 | 09-04 Corporate taxpayers Part 2 -Create | 1210 |
| TAX | TAX Vids!156 | TAX-09 | 09-05 Drill - Corporate Taxpayer types | 2243 |
| TAX | TAX Vids!157 | TAX-09 | 09-06 Drill - Special & Exempt Corporations | 696 |
| TAX | TAX Vids!158 | TAX-09 | 09-07 Drills - International Carriers | 789 |
| TAX | TAX Vids!159 | TAX-09 | 09-06 Drills - OBU/FCDU/EFCDU | 1253 |
| TAX | TAX Vids!160 | TAX-09 | 09-08 Drills - Supplementals | 3991 |
| TAX | TAX Vids!161 | TAX-09 | 09-09 Unique Corporate Tax rules | 1371 |
| TAX | TAX Vids!162 | TAX-09 | 09-10 Drill - Minimum corporate income tax | 1517 |
| TAX | TAX Vids!163 | TAX-09 | 09-11 Improperly acumulated earnings tax | 2024 |
| TAX | TAX Vids!164 | TAX-09 | 09-12 Branch Profit Remittance Tax | 1046 |
| TAX | TAX Vids!165 | TAX-09 | 09-13 Illustration 19 & 20 | 1480 |
| TAX | TAX Vids!170 | TAX-10 | 10-01 Introduction to transfer taxation | 1674 |
| TAX | TAX Vids!171 | TAX-10 | 10-02 Transfers | 2145 |
| TAX | TAX Vids!172 | TAX-10 | 10-03 Types of Transfer Taxpayers | 1098 |
| TAX | TAX Vids!173 | TAX-10 | 10-04 Succession Elements | 3406 |
| TAX | TAX Vids!174 | TAX-10 | 10-05 Special Exclusions and Valuation of Gross Estate / Discussion of Illustrations 1, 2 & 3 | 2876 |
| TAX | TAX Vids!175 | TAX-10 | 10-06 Gross Estate of Married Decedents | 3058 |
| TAX | TAX Vids!176 | TAX-10 | 10-07 Classification of Gross Estate Items & Discussion of Illustration 4 | 2200 |
| TAX | TAX Vids!177 | TAX-10 | 10-08 Illustration 5 | 867 |
| TAX | TAX Vids!178 | TAX-10 | 10-09 Deductions from Gross Estate | 3949 |
| TAX | TAX Vids!179 | TAX-10 | 10-10 Illustration 6 & 7 | 1051 |
| TAX | TAX Vids!180 | TAX-10 | 10-11 Vanishing Deductions | 1587 |
| TAX | TAX Vids!181 | TAX-10 | 10-12 Vanishing Deductions Illustration | 4036 |
| TAX | TAX Vids!182 | TAX-10 | 10-13 Illustration 10 | 3306 |
| TAX | TAX Vids!183 | TAX-10 | 10-14 Illustration 10 Absolute Community of Property | 1220 |
| TAX | TAX Vids!184 | TAX-10 | 10-15 Illustration 11&12 and Administrative requirements | 2060 |
| TAX | TAX Vids!188 | TAX-11 | 11-01 The concept of donation | 1432 |
| TAX | TAX Vids!189 | TAX-11 | 11-02 Donor's tax | 3834 |
| TAX | TAX Vids!190 | TAX-11 | 11-03 Illustration 1 | 864 |
| TAX | TAX Vids!191 | TAX-11 | 11-04 illustration 2-3 | 724 |
| TAX | TAX Vids!192 | TAX-11 | 11-05 Illustration 4-6 | 1532 |
| TAX | TAX Vids!193 | TAX-11 | 11-06 Illustration 7 | 1309 |
| TAX | TAX Vids!194 | TAX-11 | 11-07 Illustration 8 | 1479 |
| TAX | TAX Vids!195 | TAX-11 | 11-08 Illustration 9-11 | 1208 |
| TAX | TAX Vids!199 | TAX-12 | 12-01 Consumption Tax | 1180 |
| TAX | TAX Vids!200 | TAX-12 | 12-02 Vat on Import vs. Business Tax | 792 |
| TAX | TAX Vids!201 | TAX-12 | 12-03 Classes of Consumption. | 1257 |
| TAX | TAX Vids!202 | TAX-12 | 12-04 Additional Considerations on Consumption Tax | 1427 |
| TAX | TAX Vids!203 | TAX-12 | 12-05 Drills | 2776 |
| TAX | TAX Vids!207 | TAX-13 | 13-01 VAT on Importation | 4235 |
| TAX | TAX Vids!208 | TAX-13 | 13-02 VAT on Importation - Drills | 1294 |
| TAX | TAX Vids!213 | TAX-14 | 14-01 Introduction to Business Taxation Part 1 | 1996 |
| TAX | TAX Vids!214 | TAX-14 | 14-02 Introduction to Business Taxation Part 2 | 2008 |
| TAX | TAX Vids!215 | TAX-14 | 14-03 Introduction to Business Tax Drills Part 1 | 1397 |
| TAX | TAX Vids!216 | TAX-14 | 14-04 Introduction to Business Tax Drills Part 2 | 1633 |
| TAX | TAX Vids!217 | TAX-14 | 14-05 Exempt Sales or Receipt Part 1 | 1904 |
| TAX | TAX Vids!218 | TAX-14 | 14-06 Exempt Sales or Receipt Part 2 | 2227 |
| TAX | TAX Vids!219 | TAX-14 | 14-07 Exempt Sales or Receipt Drills Part 1 | 1310 |
| TAX | TAX Vids!220 | TAX-14 | 14-08 Exempt Sales or Receipt Drills Part 2 | 1653 |
| TAX | TAX Vids!224 | TAX-14.1 | 14.01-01 Services Specifically Subject to % Tax | 3797 |
| TAX | TAX Vids!225 | TAX-14.1 | 14.01-02 Specifically Subject to % Tax - Drills | 3137 |
| TAX | TAX Vids!229 | TAX-14.2 | 14.02-01 Sources Of Output Vat (12%) | 3265 |
| TAX | TAX Vids!230 | TAX-14.2 | 14.02-02 Vat Source Of Output Vat (0%) | 1690 |
| TAX | TAX Vids!231 | TAX-14.2 | 14.02-03 Output Vat - Drills | 3305 |
| TAX | TAX Vids!232 | TAX-14.2 | 14.02-04 Input Vat | 3491 |
| TAX | TAX Vids!233 | TAX-14.2 | 14.02-05 Input Vat - Drills | 2072 |
| TAX | TAX Vids!234 | TAX-14.2 | 14.02-06 Input Vat Allocation And Tax Credits | 808 |
| TAX | TAX Vids!235 | TAX-14.2 | 14.02-07 Vat Integrated Application Part 1 | 1959 |
| TAX | TAX Vids!236 | TAX-14.2 | 14.02-08 Integrated Application Part 2 | 2016 |
| TAX | TAX Vids!241 | TAX-15 | 15-01 Excise Tax Part 1 | 2352 |
| TAX | TAX Vids!242 | TAX-15 | 15-02 Excise Tax Part 2 | 2111 |
| TAX | TAX Vids!243 | TAX-15 | 15-03 Sin Tax | 2309 |
| TAX | TAX Vids!244 | TAX-15 | 15-04 Green Tax | 2621 |
| TAX | TAX Vids!245 | TAX-15 | 15-05 Miscellaneous Items Part 1 | 990 |
| TAX | TAX Vids!246 | TAX-15 | 15-06 Miscellaneous Items Part 2 | 2375 |
| TAX | TAX Vids!247 | TAX-15 | 15-07 Miscellaneous Items Part 3 | 2756 |
| TAX | TAX Vids!248 | TAX-15 | 15-08 Documentary Stamp Tax | 1775 |
| TAX | TAX Vids!249 | TAX-15 | 15-09 Focus Transaction Part 1 | 1858 |
| TAX | TAX Vids!250 | TAX-15 | 15-10 Focus Transaction Part 2 | 2389 |
| TAX | TAX Vids!254 | TAX-16 | 16-01 Goverment Remedies Part 1 | 2130 |
| TAX | TAX Vids!255 | TAX-16 | 16-02 Goverment Remedies Part 2 | 1630 |
| TAX | TAX Vids!256 | TAX-16 | 16-03 Goverment Remedies Part 3 | 1820 |
| TAX | TAX Vids!257 | TAX-16 | 16-04 Government Remedies Part 4 | 1285 |
| TAX | TAX Vids!258 | TAX-16 | 16-05 Government Remedies Drills | 3263 |
| TAX | TAX Vids!259 | TAX-16 | 16-06 Taxpayer Remedies | 5522 |
| TAX | TAX Vids!260 | TAX-16 | 16-07 Taxpayer Remedies - Drills | 3091 |
| TAX | TAX Vids!264 | TAX-17 | 17-01 Introduction To Local Taxation - Part 1 | 3524 |
| TAX | TAX Vids!265 | TAX-17 | 17-02 Introduction To Local Taxes - Part 2 | 2498 |
| TAX | TAX Vids!266 | TAX-17 | 17-03 Provincial Taxes | 3406 |
| TAX | TAX Vids!267 | TAX-17 | 17-04 Drills Provincial Tax | 2057 |
| TAX | TAX Vids!268 | TAX-17 | 17-05 Other Privilege Taxes | 2082 |
| TAX | TAX Vids!269 | TAX-17 | 17-06 Drills - Other Privilege Taxes | 1155 |
| TAX | TAX Vids!270 | TAX-17 | 17-07 Community Tax | 1328 |
| TAX | TAX Vids!271 | TAX-17 | 17-08 Drills Community Tax | 985 |
| TAX | TAX Vids!272 | TAX-17 | 17-09 Fundamentals Of Local Business Tax | 3396 |
| TAX | TAX Vids!273 | TAX-17 | 17-10 Fundamentals Of Local Business Tax-Drills | 1889 |
| TAX | TAX Vids!274 | TAX-17 | 17-11 Fundamentals Of Local Business Tax-Drills 5-9 | 1581 |
| TAX | TAX Vids!279 | TAX-18 | 18-01 Senior Citizen & Pwd | 2691 |
| TAX | TAX Vids!280 | TAX-18 | 18-02 Barangay Microbusiness Enterprise Law | 1830 |
| TAX | TAX Vids!281 | TAX-18 | 18-03 Double Taxation Agreement | 2668 |
| TAX | TAX Vids!282 | TAX-18 | 18-04 Board of Investments - Registered Business Enterprises Part 1 | 2379 |
| TAX | TAX Vids!283 | TAX-18 | 18-05 Board of Investments - Registered Business Enterprises Part 2 | 2272 |
| TAX | TAX Vids!284 | TAX-18 | 18-06 Peza Rbes | 3102 |
| TAX | TAX Vids!285 | TAX-18 | 18-07 Create Incentives Part 1 | 3699 |
| TAX | TAX Vids!286 | TAX-18 | 18-08 Create Incentives Part 2 | 2595 |
| FAR | FAR Vids!3 | FAR-01 | 01-01 Definition of Accounting | 2154 |
| FAR | FAR Vids!4 | FAR-01 | 01-02 Accountancy Law and Accountancy Fields | 1283 |
| FAR | FAR Vids!5 | FAR-01 | 01-03 PFRS (Definition, Scope & Structure) | 1086 |
| FAR | FAR Vids!6 | FAR-01 | 01-04 Standard Setting | 1593 |
| FAR | FAR Vids!7 | FAR-01 | 01-05 Discussion Exercises | 1093 |
| FAR | FAR Vids!11 | FAR-02 | 02-01 Purpose and Authoritative Status | 1192 |
| FAR | FAR Vids!12 | FAR-02 | 02-02 Underlying Assumptions | 956 |
| FAR | FAR Vids!13 | FAR-02 | 02-03 Chapter 1 of Conceptual Framework | 1591 |
| FAR | FAR Vids!14 | FAR-02 | 02-04 Chapter 2 (Fundamental Qualitative Characteristics) | 2018 |
| FAR | FAR Vids!15 | FAR-02 | 02-05 Chapter 2 (Enhancing Qualitative Characteristics) | 899 |
| FAR | FAR Vids!16 | FAR-02 | 02-06 Chapter 3 of Conceptual Framework | 509 |
| FAR | FAR Vids!17 | FAR-02 | 02-07 Chapter 4 of Conceptual Framework | 2021 |
| FAR | FAR Vids!18 | FAR-02 | 02-08 Chapter 5 of Conceptual Framework | 740 |
| FAR | FAR Vids!19 | FAR-02 | 02-09 Chapter 6 & 7 of Conceptual Framework | 1427 |
| FAR | FAR Vids!20 | FAR-02 | 02-10 Chapter 8 of Conceptual Framework | 694 |
| FAR | FAR Vids!21 | FAR-02 | 02-11 Straight Problems (Exercise 1 and 2) | 1063 |
| FAR | FAR Vids!22 | FAR-02 | 02-12 Multiple Choice Theories | 1767 |
| FAR | FAR Vids!26 | FAR-03 | 03-01 Cash and Cash Equivalents (Part 1) | 2383 |
| FAR | FAR Vids!27 | FAR-03 | 03-02 Cash and Cash Equivalents (Part 2) | 2072 |
| FAR | FAR Vids!28 | FAR-03 | 03-03 Cash and Cash Equivalents (Part 3) | 2247 |
| FAR | FAR Vids!29 | FAR-03 | 03-04 Exercise 1 | 1254 |
| FAR | FAR Vids!30 | FAR-03 | 03-05 Bank Reconciliation | 1480 |
| FAR | FAR Vids!31 | FAR-03 | 03-06 Exercise 2 | 1196 |
| FAR | FAR Vids!32 | FAR-03 | 03-07 Proof of Cash | 1960 |
| FAR | FAR Vids!33 | FAR-03 | 03-08 Exercise 3 | 1664 |
| FAR | FAR Vids!34 | FAR-03 | 03-09 Exercise 4 | 1666 |
| FAR | FAR Vids!35 | FAR-03 | 03-10 Multiple Choice (Theories) | 661 |
| FAR | FAR Vids!39 | FAR-04 | 04-01 Receivables in General | 1265 |
| FAR | FAR Vids!40 | FAR-04 | 04-02 Trade AR (Part 1) | 2260 |
| FAR | FAR Vids!41 | FAR-04 | 04-03 Trade AR (Part 2) | 1501 |
| FAR | FAR Vids!42 | FAR-04 | 04-04 Accounting for Bad Debts | 1348 |
| FAR | FAR Vids!43 | FAR-04 | 04-05 Notes Receivable | 2498 |
| FAR | FAR Vids!44 | FAR-04 | 04-06 Loans Receivable | 688 |
| FAR | FAR Vids!45 | FAR-04 | 04-07 Impairment of Loans | 667 |
| FAR | FAR Vids!46 | FAR-04 | 04-08 Receivable Financing (Pledge and Assignment) | 1577 |
| FAR | FAR Vids!47 | FAR-04 | 04-09 Receivable Financing (Factoring and Discounting) | 1502 |
| FAR | FAR Vids!48 | FAR-04 | 04-10 Multiple Choice (Theories) | 837 |
| FAR | FAR Vids!49 | FAR-04 | 04-11 Exercise 1 | 491 |
| FAR | FAR Vids!50 | FAR-04 | 04-12 Exercise 2 Part 1 | 576 |
| FAR | FAR Vids!51 | FAR-04 | 04-13 Exercise 2 Part 2 | 457 |
| FAR | FAR Vids!52 | FAR-04 | 04-14 Exercise 3 | 1198 |
| FAR | FAR Vids!53 | FAR-04 | 04-15 Exercise 4 | 864 |
| FAR | FAR Vids!54 | FAR-04 | 04-16 Exercise 5 | 1011 |
| FAR | FAR Vids!55 | FAR-04 | 04-17 Exercise 6 | 495 |
| FAR | FAR Vids!56 | FAR-04 | 04-18 Exercise 7 | 2222 |
| FAR | FAR Vids!57 | FAR-04 | 04-19 Exercise 8 Part 1 | 1631 |
| FAR | FAR Vids!58 | FAR-04 | 04-20 Exercise 8 Part 2 | 1407 |
| FAR | FAR Vids!59 | FAR-04 | 04-21 Exercise 9 | 1134 |
| FAR | FAR Vids!60 | FAR-04 | 04-22 Exercise 10 | 728 |
| FAR | FAR Vids!61 | FAR-04 | 04-23 Exercise 11 | 722 |
| FAR | FAR Vids!66 | FAR-05 | 05-01 Basic Concepts | 1226 |
| FAR | FAR Vids!67 | FAR-05 | 05-02 Recognition Part I | 1610 |
| FAR | FAR Vids!68 | FAR-05 | 05-03 Recognition Part II | 698 |
| FAR | FAR Vids!69 | FAR-05 | 05-04 Initial Measurement Part I | 1224 |
| FAR | FAR Vids!70 | FAR-05 | 05-05 Initial Measurement Part II | 1055 |
| FAR | FAR Vids!71 | FAR-05 | 05-06 Accounting for Inventories | 1010 |
| FAR | FAR Vids!72 | FAR-05 | 05-07 Purchase Commitments | 402 |
| FAR | FAR Vids!73 | FAR-05 | 05-08 Subsequent Measurement (Cost Formulas) | 1328 |
| FAR | FAR Vids!74 | FAR-05 | 05-09 Subsequent Measurement (LCNRV) | 1153 |
| FAR | FAR Vids!75 | FAR-05 | 05-10 Inventory Estimation (Basic Concepts) | 710 |
| FAR | FAR Vids!76 | FAR-05 | 05-11 Inventory Estimation (Gross Profit Method) | 711 |
| FAR | FAR Vids!77 | FAR-05 | 05-12 Inventory Estimation (Retail Inventory Method) | 1678 |
| FAR | FAR Vids!78 | FAR-05 | 05-13 Exercise 1 | 1469 |
| FAR | FAR Vids!79 | FAR-05 | 05-14 Exercise 2 | 2157 |
| FAR | FAR Vids!80 | FAR-05 | 05-15 Exercise 3 | 800 |
| FAR | FAR Vids!81 | FAR-05 | 05-16 Exercise 4 | 685 |
| FAR | FAR Vids!82 | FAR-05 | 05-17 Exercise 5 Part 1 | 1154 |
| FAR | FAR Vids!83 | FAR-05 | 05-18 Exercise 5 Part 2 | 915 |
| FAR | FAR Vids!84 | FAR-05 | 05-19 Exercise 6 | 843 |
| FAR | FAR Vids!85 | FAR-05 | 05-20 Exercise 7 | 768 |
| FAR | FAR Vids!86 | FAR-05 | 05-21 Exercise 8 | 391 |
| FAR | FAR Vids!87 | FAR-05 | 05-22 Exercise 9 | 771 |
| FAR | FAR Vids!88 | FAR-05 | 05-23 Exercise 10 | 1103 |
| FAR | FAR Vids!89 | FAR-05 | 05-24 Multiple Choice (Theories) | 945 |
| FAR | FAR Vids!93 | FAR-06 | 06-01 Scope and Definition of Terms | 1777 |
| FAR | FAR Vids!94 | FAR-06 | 06-02 Recognition and Measurement | 873 |
| FAR | FAR Vids!95 | FAR-06 | 06-03 Gains and Losses | 1021 |
| FAR | FAR Vids!96 | FAR-06 | 06-04 Presentation and Disclosure | 205 |
| FAR | FAR Vids!97 | FAR-06 | 06-05 Exercise 1 | 991 |
| FAR | FAR Vids!98 | FAR-06 | 06-06 Exercise 2 | 402 |
| FAR | FAR Vids!99 | FAR-06 | 06-07 Exercise 3 | 286 |
| FAR | FAR Vids!100 | FAR-06 | 06-08 Exercise 4 | 1368 |
| FAR | FAR Vids!101 | FAR-06 | 06-09 Exercise 5 | 350 |
| FAR | FAR Vids!102 | FAR-06 | 06-10 Exercise 6 | 763 |
| FAR | FAR Vids!103 | FAR-06 | 06-11 Multiple Choice (Theories) | 321 |
| FAR | FAR Vids!107 | FAR-07 | 07-01 Definition, Scope and Recognition | 1680 |
| FAR | FAR Vids!108 | FAR-07 | 07-02 Initial Measurement (Part 1) | 1913 |
| FAR | FAR Vids!109 | FAR-07 | 07-03 Initial Measurement (Part 2) | 2346 |
| FAR | FAR Vids!110 | FAR-07 | 07-04 Cost of Land | 1347 |
| FAR | FAR Vids!111 | FAR-07 | 07-05 Cost of Building | 891 |
| FAR | FAR Vids!112 | FAR-07 | 07-06 Cost of Equipment | 319 |
| FAR | FAR Vids!113 | FAR-07 | 07-07 Exercise 1 | 791 |
| FAR | FAR Vids!114 | FAR-07 | 07-08 Exercise 2 | 1003 |
| FAR | FAR Vids!115 | FAR-07 | 07-09 Exercise 3 | 723 |
| FAR | FAR Vids!116 | FAR-07 | 07-10 Exercise 4 | 303 |
| FAR | FAR Vids!117 | FAR-07 | 07-11 Exercise 5 | 1539 |
| FAR | FAR Vids!118 | FAR-07 | 07-12 Exercise 6 | 413 |
| FAR | FAR Vids!119 | FAR-07 | 07-13 Multiple Choice (Theories) | 511 |
| FAR | FAR Vids!124 | FAR-08 | 08-01 Change in Accounting Estimate | 528 |
| FAR | FAR Vids!125 | FAR-08 | 08-02 Concept of Depreciation | 1191 |
| FAR | FAR Vids!126 | FAR-08 | 08-03 Depreciation Methods (Part 1) | 1333 |
| FAR | FAR Vids!127 | FAR-08 | 08-04 Depreciation Methods (Part 2) | 1162 |
| FAR | FAR Vids!128 | FAR-08 | 08-05 Derecognition | 257 |
| FAR | FAR Vids!129 | FAR-08 | 08-06 Revaluation Model (Part 1) | 914 |
| FAR | FAR Vids!130 | FAR-08 | 08-07 Revaluation Model (Part 2) | 811 |
| FAR | FAR Vids!131 | FAR-08 | 08-08 Subsequent Costs | 628 |
| FAR | FAR Vids!132 | FAR-08 | 08-09 Multiple Choice (Theories) | 727 |
| FAR | FAR Vids!133 | FAR-08 | 08-10 Exercise 1 | 492 |
| FAR | FAR Vids!134 | FAR-08 | 08-11 Exercise 2 | 1241 |
| FAR | FAR Vids!135 | FAR-08 | 08-12 Exercise 3 | 893 |
| FAR | FAR Vids!136 | FAR-08 | 08-13 Exercise 4 | 435 |
| FAR | FAR Vids!137 | FAR-08 | 08-14 Exercise 5 | 1226 |
| FAR | FAR Vids!138 | FAR-08 | 08-15 Exercise 6 | 1286 |
| FAR | FAR Vids!139 | FAR-08 | 08-16 Exercise 7 | 713 |
| FAR | FAR Vids!140 | FAR-08 | 08-17 Exercise 8 | 521 |
| FAR | FAR Vids!141 | FAR-08 | 08-18 Exercise 9 | 707 |
| FAR | FAR Vids!142 | FAR-08 | 08-19 Exercise 10 | 759 |
| FAR | FAR Vids!146 | FAR-09 | 09-01 Definition, Scope and Recognition | 1336 |
| FAR | FAR Vids!147 | FAR-09 | 09-02 Measurement, Accounting & Presentation of Government Grants | 1109 |
| FAR | FAR Vids!148 | FAR-09 | 09-03 Repayments of Grants | 1002 |
| FAR | FAR Vids!149 | FAR-09 | 09-04 Multiple Choice | 593 |
| FAR | FAR Vids!150 | FAR-09 | 09-05 Exercise 1 | 1903 |
| FAR | FAR Vids!151 | FAR-09 | 09-06 Exercise 2 | 493 |
| FAR | FAR Vids!152 | FAR-09 | 09-07 Exercise 3 | 1139 |
| FAR | FAR Vids!157 | FAR-10 | 10-01 Basic Concepts and Recognition | 1930 |
| FAR | FAR Vids!158 | FAR-10 | 10-02 Accounting for Borrowing Costs - Specific Borrowing | 516 |
| FAR | FAR Vids!159 | FAR-10 | 10-03 Accounting for Borrowing Costs - General Borrowing | 489 |
| FAR | FAR Vids!160 | FAR-10 | 10-04 Accounting for Borrowing Costs - Mixed Borrowing | 381 |
| FAR | FAR Vids!161 | FAR-10 | 10-05 Multiple Choice | 461 |
| FAR | FAR Vids!162 | FAR-10 | 10-06 Exercise 1 | 500 |
| FAR | FAR Vids!163 | FAR-10 | 10-07 Exercise 2 | 649 |
| FAR | FAR Vids!164 | FAR-10 | 10-08 Exercise 3 | 1164 |
| FAR | FAR Vids!165 | FAR-10 | 10-09 Exercise 4 | 688 |
| FAR | FAR Vids!169 | FAR-11 | 11-01 Exploration and Evaluation of Assets | 1603 |
| FAR | FAR Vids!170 | FAR-11 | 11-02 Cost of Wasting Assets | 1253 |
| FAR | FAR Vids!171 | FAR-11 | 11-03 Depletion | 892 |
| FAR | FAR Vids!172 | FAR-11 | 11-04 Accounting for Shutdown | 598 |
| FAR | FAR Vids!173 | FAR-11 | 11-05 Wasting Asset Doctrine | 961 |
| FAR | FAR Vids!174 | FAR-11 | 11-06 Multiple Choice (Theories) | 530 |
| FAR | FAR Vids!175 | FAR-11 | 11-07 Exercise 1 | 452 |
| FAR | FAR Vids!176 | FAR-11 | 11-08 Exercise 2 | 1011 |
| FAR | FAR Vids!177 | FAR-11 | 11-09 Exercise 3 | 824 |
| FAR | FAR Vids!178 | FAR-11 | 11-10 Exercise 4 | 681 |
| FAR | FAR Vids!179 | FAR-11 | 11-11 Exercise 5 | 269 |
| FAR | FAR Vids!183 | FAR-12 | 12-01 Definition and Scope | 1373 |
| FAR | FAR Vids!184 | FAR-12 | 12-02 Initial Measurement Part 1 | 802 |
| FAR | FAR Vids!185 | FAR-12 | 12-03 Initial Measurement Part 2 | 1912 |
| FAR | FAR Vids!186 | FAR-12 | 12-04 Subsequent Measurements & Amortization | 1129 |
| FAR | FAR Vids!187 | FAR-12 | 12-05 Other Accounting Issues | 401 |
| FAR | FAR Vids!188 | FAR-12 | 12-06 Major Categories Part 1 | 1051 |
| FAR | FAR Vids!189 | FAR-12 | 12-07 Major Categories Part 2 | 1680 |
| FAR | FAR Vids!190 | FAR-12 | 12-08 Multiple Choice Theories | 583 |
| FAR | FAR Vids!191 | FAR-12 | 12-09 Exercise 1 | 877 |
| FAR | FAR Vids!192 | FAR-12 | 12-10 Exercise 2 | 523 |
| FAR | FAR Vids!193 | FAR-12 | 12-11 Exercise 3 | 306 |
| FAR | FAR Vids!194 | FAR-12 | 12-12 Exercise 4 | 1082 |
| FAR | FAR Vids!195 | FAR-12 | 12-13 Exercise 5 | 403 |
| FAR | FAR Vids!196 | FAR-12 | 12-14 Exercise 6 | 869 |
| FAR | FAR Vids!197 | FAR-12 | 12-15 Exercise 7 | 495 |
| FAR | FAR Vids!202 | FAR-13 | 13-01 Basic Concepts and Scope of PAS 36 | 789 |
| FAR | FAR Vids!203 | FAR-13 | 13-02 Identification of Impaired Asset | 809 |
| FAR | FAR Vids!204 | FAR-13 | 13-03 Measurement of Recoverable Amount | 1004 |
| FAR | FAR Vids!205 | FAR-13 | 13-04 Recognition of impairment | 697 |
| FAR | FAR Vids!206 | FAR-13 | 13-05 Reversal of Impairment Loss | 652 |
| FAR | FAR Vids!207 | FAR-13 | 13-06 Multiple Choice (Theories) | 312 |
| FAR | FAR Vids!208 | FAR-13 | 13-07 Exercise 1 | 747 |
| FAR | FAR Vids!209 | FAR-13 | 13-08 Exercise 2 | 467 |
| FAR | FAR Vids!210 | FAR-13 | 13-09 Exercise 3 | 414 |
| FAR | FAR Vids!211 | FAR-13 | 13-10 Exercise 4 | 1049 |
| FAR | FAR Vids!212 | FAR-13 | 13-11 Exercise 5 | 797 |
| FAR | FAR Vids!217 | FAR-14 | 14-01 Basic Concepts | 468 |
| FAR | FAR Vids!218 | FAR-14 | 14-02 Classification, Measurement and Presentation | 1088 |
| FAR | FAR Vids!219 | FAR-14 | 14-03 Sale of Investment | 392 |
| FAR | FAR Vids!220 | FAR-14 | 14-04 Accounting for Share Splits, Special Assessments & Stock Rights | 1347 |
| FAR | FAR Vids!221 | FAR-14 | 14-05 Disposal of Investment | 689 |
| FAR | FAR Vids!222 | FAR-14 | 14-06 Accounting for Dividends | 1393 |
| FAR | FAR Vids!223 | FAR-14 | 14-07 Accounting for Share Splits, Special Assessment and Stock Rights | 1177 |
| FAR | FAR Vids!224 | FAR-14 | 14-08 Reclassifications and Impairment | 228 |
| FAR | FAR Vids!225 | FAR-14 | 14-09 Exercise 1 | 487 |
| FAR | FAR Vids!226 | FAR-14 | 14-10 Exercise 2 | 566 |
| FAR | FAR Vids!227 | FAR-14 | 14-11 Exercise 3 | 1255 |
| FAR | FAR Vids!228 | FAR-14 | 14-12 Exercise 4 | 1179 |
| FAR | FAR Vids!229 | FAR-14 | 14-13 Exercise 5 | 455 |
| FAR | FAR Vids!230 | FAR-14 | 14-14 Multiple Choice (Theories) | 579 |
| FAR | FAR Vids!235 | FAR-15 | 15-01 Basic Concepts | 630 |
| FAR | FAR Vids!236 | FAR-15 | 15-02 Measurement | 1296 |
| FAR | FAR Vids!237 | FAR-15 | 15-03 Investee with Heavy Losses | 339 |
| FAR | FAR Vids!238 | FAR-15 | 15-04 Intercompany Transactions | 842 |
| FAR | FAR Vids!239 | FAR-15 | 15-05 Changes In Ownership Percentage | 1847 |
| FAR | FAR Vids!240 | FAR-15 | 15-06 Presentation And Reporting | 249 |
| FAR | FAR Vids!241 | FAR-15 | 15-07 Straight Problems (Exercise 1) | 1443 |
| FAR | FAR Vids!242 | FAR-15 | 15-08 Straight Problems (Exercise 2) | 588 |
| FAR | FAR Vids!243 | FAR-15 | 15-09 Straight Problems (Exercise 3) | 529 |
| FAR | FAR Vids!244 | FAR-15 | 15-10 Straight Problems (Exercise 4) | 1120 |
| FAR | FAR Vids!245 | FAR-15 | 15-11 Straight Problems (Exercise 5) | 381 |
| FAR | FAR Vids!246 | FAR-15 | 15-12 Straight Problems (Exercise 6) | 741 |
| FAR | FAR Vids!247 | FAR-15 | 15-13 Multiple Choice (Theories) | 677 |
| FAR | FAR Vids!251 | FAR-16 | 16-01 Basic Concepts | 1106 |
| FAR | FAR Vids!252 | FAR-16 | 16-02 Classification, Measurement & Presentation | 1467 |
| FAR | FAR Vids!253 | FAR-16 | 16-03 Dispossal of Investments | 352 |
| FAR | FAR Vids!254 | FAR-16 | 16-04 Reclassification | 358 |
| FAR | FAR Vids!255 | FAR-16 | 16-05 Impairment and Reversal of Impairment | 598 |
| FAR | FAR Vids!256 | FAR-16 | 16-06 Exercise 1 | 797 |
| FAR | FAR Vids!257 | FAR-16 | 16-07 Exercise 2 | 1376 |
| FAR | FAR Vids!258 | FAR-16 | 16-08 Exercise 3 | 796 |
| FAR | FAR Vids!259 | FAR-16 | 16-09 Exercise 4 | 644 |
| FAR | FAR Vids!260 | FAR-16 | 16-10 Exercise 5 | 1075 |
| FAR | FAR Vids!261 | FAR-16 | 16-11 Multiple Choice (Theories) | 570 |
| FAR | FAR Vids!265 | FAR-17 | 17-01 Basic Concepts | 436 |
| FAR | FAR Vids!266 | FAR-17 | 17-02 Other Classification Issues | 663 |
| FAR | FAR Vids!267 | FAR-17 | 17-03 Initial Measurement | 710 |
| FAR | FAR Vids!268 | FAR-17 | 17-04 Subsequent Measurement | 107 |
| FAR | FAR Vids!269 | FAR-17 | 17-05 Transfer | 571 |
| FAR | FAR Vids!270 | FAR-17 | 17-06 Exercise 1 | 800 |
| FAR | FAR Vids!271 | FAR-17 | 17-07 Exercise 2 | 967 |
| FAR | FAR Vids!272 | FAR-17 | 17-08 Exercise 3 | 743 |
| FAR | FAR Vids!273 | FAR-17 | 17-09 Exercise 4 | 578 |
| FAR | FAR Vids!274 | FAR-17 | 17-10 Exercise 5 | 635 |
| FAR | FAR Vids!275 | FAR-17 | 17-11 Exercise 6 | 349 |
| FAR | FAR Vids!276 | FAR-17 | 17-12 Multiple Choice (Theories) | 593 |
| FAR | FAR Vids!280 | FAR-18 | 18-01 Cash Surrender Value | 630 |
| FAR | FAR Vids!281 | FAR-18 | 18-02 Bond Sinking FUnd | 540 |
| FAR | FAR Vids!282 | FAR-18 | 18-03 Other Long Term Investment | 331 |
| FAR | FAR Vids!283 | FAR-18 | 18-04 Exercise 1 | 847 |
| FAR | FAR Vids!284 | FAR-18 | 18-05 Exercise 2 | 263 |
| FAR | FAR Vids!285 | FAR-18 | 18-06 Exercise 3 | 635 |
| FAR | FAR Vids!286 | FAR-18 | 18-07 Exercise 4 | 397 |
| FAR | FAR Vids!287 | FAR-18 | 18-08 Multiple Choice (Theories) | 358 |
| FAR | FAR Vids!294 | FAR-20 | 20-01 Basic Concepts and Measurement | 1439 |
| FAR | FAR Vids!295 | FAR-20 | 20-02 FS Presentation | 1486 |
| FAR | FAR Vids!296 | FAR-20 | 20-03 Specific Current Liabilities Part I | 1511 |
| FAR | FAR Vids!297 | FAR-20 | 20-04 Specific Current Liabilities Part II | 642 |
| FAR | FAR Vids!298 | FAR-20 | 20-05 Exercise 1 | 1732 |
| FAR | FAR Vids!299 | FAR-20 | 20-06 Exercise 2 | 552 |
| FAR | FAR Vids!300 | FAR-20 | 20-07 Exercise 3 | 465 |
| FAR | FAR Vids!301 | FAR-20 | 20-08 Exercise 4 & 5 | 802 |
| FAR | FAR Vids!302 | FAR-20 | 20-09 Exercise 6 & 7 | 1455 |
| FAR | FAR Vids!303 | FAR-20 | 20-10 Exercise 8 & 9 | 752 |
| FAR | FAR Vids!304 | FAR-20 | 20-11 Multiple Choice(Theories) | 504 |
| FAR | FAR Vids!308 | FAR-21 | 21-01 Notes Payable | 1233 |
| FAR | FAR Vids!309 | FAR-21 | 21-02 Debt Restructuiring Part I | 996 |
| FAR | FAR Vids!310 | FAR-21 | 21-03 Debt Restructuiring Part II | 343 |
| FAR | FAR Vids!311 | FAR-21 | 21-04 Loans Payable | 333 |
| FAR | FAR Vids!312 | FAR-21 | 21-05 Multiple Choice(Therories) | 396 |
| FAR | FAR Vids!313 | FAR-21 | 21-06 Exercise 1 | 717 |
| FAR | FAR Vids!314 | FAR-21 | 21-07 Exercise 2 | 1559 |
| FAR | FAR Vids!315 | FAR-21 | 21-08 Exercise 3 | 871 |
| FAR | FAR Vids!316 | FAR-21 | 21-09 Exercise 4 | 423 |
| FAR | FAR Vids!317 | FAR-21 | 21-10 Exercise 5 | 494 |
| FAR | FAR Vids!318 | FAR-21 | 21-11 Exercise 6 | 451 |
| FAR | FAR Vids!319 | FAR-21 | 21-12 Exercise 7 | 533 |
| FAR | FAR Vids!323 | FAR-22 | 22-01 Exercise 1 | 445 |
| FAR | FAR Vids!324 | FAR-22 | 22-02 Exercise 2 | 690 |
| FAR | FAR Vids!325 | FAR-22 | 22-03 Exercise 3 | 780 |
| FAR | FAR Vids!326 | FAR-22 | 22-04 Exercise 4 | 1188 |
| FAR | FAR Vids!327 | FAR-22 | 22-05 Exercise 5 | 573 |
| FAR | FAR Vids!328 | FAR-22 | 22-06 Exercise 6 | 1571 |
| FAR | FAR Vids!329 | FAR-22 | 22-07 Basic Concepts | 1516 |
| FAR | FAR Vids!330 | FAR-22 | 22-08 Classification and Measurement | 869 |
| FAR | FAR Vids!331 | FAR-22 | 22-09 Retirement of Bonds | 474 |
| FAR | FAR Vids!332 | FAR-22 | 22-10 MULTIPLE CHOICE THEORIES | 818 |
| FAR | FAR Vids!336 | FAR-23 | 23-01 Basic Concepts | 557 |
| FAR | FAR Vids!337 | FAR-23 | 23-02 Bonds with Share Warrants | 830 |
| FAR | FAR Vids!338 | FAR-23 | 23-03 Convertible Bonds | 656 |
| FAR | FAR Vids!339 | FAR-23 | 23-04 Exercise 1 | 839 |
| FAR | FAR Vids!340 | FAR-23 | 23-05 Exercise 2 | 1814 |
| FAR | FAR Vids!341 | FAR-23 | 23-06 MULTIPLE CHOICE THEORIES | 344 |
| FAR | FAR Vids!346 | FAR-24 | 24-01 Definition and Recognition | 1028 |
| FAR | FAR Vids!347 | FAR-24 | 24-02 Measurement | 1145 |
| FAR | FAR Vids!348 | FAR-24 | 24-03 Recording and Common Types of Provisions | 916 |
| FAR | FAR Vids!349 | FAR-24 | 24-04 Specific Provisions (Part 1) | 806 |
| FAR | FAR Vids!350 | FAR-24 | 24-05 Specific Provisions (Part 2) | 459 |
| FAR | FAR Vids!351 | FAR-24 | 24-06 Exercise 1 | 1318 |
| FAR | FAR Vids!352 | FAR-24 | 24-07 Exercise 2 | 938 |
| FAR | FAR Vids!353 | FAR-24 | 24-08 Exercise 3 | 545 |
| FAR | FAR Vids!354 | FAR-24 | 24-09 Exercise 4 | 368 |
| FAR | FAR Vids!355 | FAR-24 | 24-10 Exercise 5 | 316 |
| FAR | FAR Vids!356 | FAR-24 | 24-11 Exercise 6 | 395 |
| FAR | FAR Vids!357 | FAR-24 | 24-12 Exercise 7 | 1301 |
| FAR | FAR Vids!358 | FAR-24 | 24-13 MULTIPLE CHOICE THEORIES | 831 |
| FAR | FAR Vids!362 | FAR-25 | 25-01 Sort-Term Employee Benefits | 1874 |
| FAR | FAR Vids!363 | FAR-25 | 25-02 Post-Employment Benefits (Defined Contribution Plan) | 1488 |
| FAR | FAR Vids!364 | FAR-25 | 25-03 Post-Employment Benefits (Defined Benefit Plan) | 2893 |
| FAR | FAR Vids!365 | FAR-25 | 25-04 Termination and other Long-term Benefits | 397 |
| FAR | FAR Vids!366 | FAR-25 | 25-05 Exercise 1 | 975 |
| FAR | FAR Vids!367 | FAR-25 | 25-06 Exercise 2 | 1231 |
| FAR | FAR Vids!368 | FAR-25 | 25-07 Exercise 3 | 500 |
| FAR | FAR Vids!369 | FAR-25 | 25-08 Exercise 4 | 1016 |
| FAR | FAR Vids!370 | FAR-25 | 25-09 Exercise 5 | 571 |
| FAR | FAR Vids!371 | FAR-25 | 25-10 Exercise 6 | 1437 |
| FAR | FAR Vids!372 | FAR-25 | 25-11 Exercise 7 | 1117 |
| FAR | FAR Vids!373 | FAR-25 | 25-12 Exercise 8 | 254 |
| FAR | FAR Vids!374 | FAR-25 | 25-13 Multiple Choice (Theories) | 804 |
| FAR | FAR Vids!378 | FAR-26 | 26-01 Basic Concepts and Accounting for Defered Taxes | 2600 |
| FAR | FAR Vids!379 | FAR-26 | 26-02 computation of Tax Expense | 941 |
| FAR | FAR Vids!380 | FAR-26 | 26-03 Initial Recognition of DTA and DTL | 510 |
| FAR | FAR Vids!381 | FAR-26 | 26-04 Tax Allocation and Presentation | 524 |
| FAR | FAR Vids!382 | FAR-26 | 26-05 Exercise 1 | 449 |
| FAR | FAR Vids!383 | FAR-26 | 26-06 Exercise 2 | 699 |
| FAR | FAR Vids!384 | FAR-26 | 26-07 Exercise 3 | 1419 |
| FAR | FAR Vids!385 | FAR-26 | 26-08 Exercise 4 | 295 |
| FAR | FAR Vids!386 | FAR-26 | 26-09 Exercise 5 | 720 |
| FAR | FAR Vids!387 | FAR-26 | 26-10 Exercise 6 | 1201 |
| FAR | FAR Vids!388 | FAR-26 | 26-11 Exercise 7 | 647 |
| FAR | FAR Vids!389 | FAR-26 | 26-12 Multiple Choice (Theories) | 610 |
| FAR | FAR Vids!394 | FAR-27 | 27-01 Basic Concepts | 1280 |
| FAR | FAR Vids!395 | FAR-27 | 27-02 Accounting for Leases: Lessee (Part 1) | 1565 |
| FAR | FAR Vids!396 | FAR-27 | 27-03 Accounting for Leases: Lessee (Part 2) | 1454 |
| FAR | FAR Vids!397 | FAR-27 | 27-04 Accounting for Leases: Lessor | 1218 |
| FAR | FAR Vids!398 | FAR-27 | 27-05 operating leases | 905 |
| FAR | FAR Vids!399 | FAR-27 | 27-06 sale and leaseback | 842 |
| FAR | FAR Vids!400 | FAR-27 | 27-07 Exercise 1 | 1329 |
| FAR | FAR Vids!401 | FAR-27 | 27-08 Exercise 2 | 1550 |
| FAR | FAR Vids!402 | FAR-27 | 27-09 Exercise 3 | 554 |
| FAR | FAR Vids!403 | FAR-27 | 27-10 Exercise 4 | 1018 |
| FAR | FAR Vids!404 | FAR-27 | 27-11 Exercise 5 | 1380 |
| FAR | FAR Vids!405 | FAR-27 | 27-12 Exercise 6 | 481 |
| FAR | FAR Vids!406 | FAR-27 | 27-13 Exercise 7 | 978 |
| FAR | FAR Vids!407 | FAR-27 | 27-14 Exercise 8 | 622 |
| FAR | FAR Vids!408 | FAR-27 | 27-15 Exercise 9 | 1363 |
| FAR | FAR Vids!409 | FAR-27 | 27-16 Exercise 10 | 1445 |
| FAR | FAR Vids!410 | FAR-27 | 27-17 Exercise 11 | 473 |
| FAR | FAR Vids!411 | FAR-27 | 27-18 Multiple Choice (Theories) | 1162 |
| FAR | FAR Vids!415 | FAR-28 | 28-00 shareholder's equity | 2255 |
| FAR | FAR Vids!416 | FAR-28 | 28-01 Components of Shareholders' Equity | 2276 |
| FAR | FAR Vids!417 | FAR-28 | 28-02 Issuance, Subscription and Retirement Part I | 1651 |
| FAR | FAR Vids!418 | FAR-28 | 28-03 Issuance, Subscription and Retirement Part II | 997 |
| FAR | FAR Vids!419 | FAR-28 | 28-04 Treasury Shares Part I | 898 |
| FAR | FAR Vids!420 | FAR-28 | 28-05 Treasury Shares Part II | 1037 |
| FAR | FAR Vids!421 | FAR-28 | 28-06 Other equity Instruments | 1298 |
| FAR | FAR Vids!422 | FAR-28 | 28-07 Donation | 321 |
| FAR | FAR Vids!423 | FAR-28 | 28-08 Exercise 1 | 1532 |
| FAR | FAR Vids!424 | FAR-28 | 28-09 Exercise 2 | 1201 |
| FAR | FAR Vids!425 | FAR-28 | 28-10 Exercise 3 | 2638 |
| FAR | FAR Vids!426 | FAR-28 | 28-11 Exercise 4 | 399 |
| FAR | FAR Vids!427 | FAR-28 | 28-12 Exercise 5 | 664 |
| FAR | FAR Vids!428 | FAR-28 | 28-13 Exercise 6 | 2917 |
| FAR | FAR Vids!429 | FAR-28 | 28-14 Exercise 7 | 479 |
| FAR | FAR Vids!430 | FAR-28 | 28-15 Exercise 8 | 391 |
| FAR | FAR Vids!431 | FAR-28 | 28-16 Multiple Choice (Theories) | 464 |
| FAR | FAR Vids!436 | FAR-29 | 29-01 Retained Earnings (Basic Concepts) | 1117 |
| FAR | FAR Vids!437 | FAR-29 | 29-02 Retained Earnings (Dividends Part 1) | 1627 |
| FAR | FAR Vids!438 | FAR-29 | 29-03 Retained Earnings (Dividends Part 2) | 717 |
| FAR | FAR Vids!439 | FAR-29 | 29-04 Recapitalization | 552 |
| FAR | FAR Vids!440 | FAR-29 | 29-05 Quasi Reorganization | 331 |
| FAR | FAR Vids!441 | FAR-29 | 29-06 Exercise 1 | 353 |
| FAR | FAR Vids!442 | FAR-29 | 29-07 Exercise 2 | 352 |
| FAR | FAR Vids!443 | FAR-29 | 29-08 Exercise 3 | 1002 |
| FAR | FAR Vids!444 | FAR-29 | 29-09 Exercise 4 | 632 |
| FAR | FAR Vids!445 | FAR-29 | 29-10 Exercise 5 | 870 |
| FAR | FAR Vids!446 | FAR-29 | 29-11 Exercise 6 | 1285 |
| FAR | FAR Vids!447 | FAR-29 | 29-12 Exercise 7 | 586 |
| FAR | FAR Vids!448 | FAR-29 | 29-13 Exercise 8 | 783 |
| FAR | FAR Vids!449 | FAR-29 | 29-14 Exercise 9 | 2144 |
| FAR | FAR Vids!450 | FAR-29 | 29-15 Exercise 10 | 705 |
| FAR | FAR Vids!451 | FAR-29 | 29-16 Exercise 11 | 614 |
| FAR | FAR Vids!452 | FAR-29 | 29-17 MULTIPLE CHOICE (Theories) | 752 |
| FAR | FAR Vids!456 | FAR-30 | 30-01 Basic Concepts & Recognition | 1099 |
| FAR | FAR Vids!457 | FAR-30 | 30-02 Equity-Settled Share-based Payments | 1547 |
| FAR | FAR Vids!458 | FAR-30 | 30-03 Accounting for Modifications | 419 |
| FAR | FAR Vids!459 | FAR-30 | 30-04 Acceleration of Vesting | 420 |
| FAR | FAR Vids!460 | FAR-30 | 30-05 Cash-settled Share-based Payments | 374 |
| FAR | FAR Vids!461 | FAR-30 | 30-06 Choice Between ES and CS | 331 |
| FAR | FAR Vids!462 | FAR-30 | 30-07 Exercise 1 | 577 |
| FAR | FAR Vids!463 | FAR-30 | 30-08 Exercise 2 | 1171 |
| FAR | FAR Vids!464 | FAR-30 | 30-09 Exercise 3 | 841 |
| FAR | FAR Vids!465 | FAR-30 | 30-10 Exercise 4 | 599 |
| FAR | FAR Vids!466 | FAR-30 | 30-11 Exercise 5 | 583 |
| FAR | FAR Vids!467 | FAR-30 | 30-12 Exercise 6 | 818 |
| FAR | FAR Vids!468 | FAR-30 | 30-13 Exercise 7 | 1195 |
| FAR | FAR Vids!469 | FAR-30 | 30-14 Exercise 8 | 1170 |
| FAR | FAR Vids!470 | FAR-30 | 30-15 Exercise 9 | 1170 |
| FAR | FAR Vids!471 | FAR-30 | 30-16 Multiple Choice (Theories) | 636 |
| FAR | FAR Vids!475 | FAR-31 | 31-01 Book Value Per Share Lecture | 1623 |
| FAR | FAR Vids!476 | FAR-31 | 31-02 Exercise 1 | 1605 |
| FAR | FAR Vids!477 | FAR-31 | 31-03 Exercise 2 | 571 |
| FAR | FAR Vids!478 | FAR-31 | 31-04 Exercise 3 | 439 |
| FAR | FAR Vids!479 | FAR-31 | 31-05 Exercise 4 | 556 |
| FAR | FAR Vids!480 | FAR-31 | 31-06 Multiple Choice (Theories) | 278 |
| FAR | FAR Vids!484 | FAR-32 | 32-01 Basic Concepts | 571 |
| FAR | FAR Vids!485 | FAR-32 | 32-02 Basic Earnings per share | 1341 |
| FAR | FAR Vids!486 | FAR-32 | 32-03 Diluted Earnings per share | 1472 |
| FAR | FAR Vids!487 | FAR-32 | 32-04 Multiple Potential Ordinary Shares | 597 |
| FAR | FAR Vids!488 | FAR-32 | 32-05 Presentation and Disclosure | 266 |
| FAR | FAR Vids!489 | FAR-32 | 32-06 Exercise 1 | 456 |
| FAR | FAR Vids!490 | FAR-32 | 32-07 Exercise 2 | 814 |
| FAR | FAR Vids!491 | FAR-32 | 32-08 Exercise 3 | 720 |
| FAR | FAR Vids!492 | FAR-32 | 32-09 Exercise 4 | 299 |
| FAR | FAR Vids!493 | FAR-32 | 32-10 Exercise 5 | 655 |
| FAR | FAR Vids!494 | FAR-32 | 32-11 Exercise 6 | 258 |
| FAR | FAR Vids!495 | FAR-32 | 32-12 Exercise 7 | 2027 |
| FAR | FAR Vids!496 | FAR-32 | 32-13 Exercise 8 | 470 |
| FAR | FAR Vids!497 | FAR-32 | 32-14 Exercise 9 | 421 |
| FAR | FAR Vids!498 | FAR-32 | 32-15 Exercise 10 | 697 |
| FAR | FAR Vids!499 | FAR-32 | 32-16 Multiple Choice (Theories) | 527 |
| FAR | FAR Vids!503 | FAR-33 | 33-01 Basic Concepts & Headings and Titles | 1237 |
| FAR | FAR Vids!504 | FAR-33 | 33-02 General Features | 2059 |
| FAR | FAR Vids!505 | FAR-33 | 33-03 The Complete Set of Financial Statement | 660 |
| FAR | FAR Vids!506 | FAR-33 | 33-04 Statement of Financial Position | 1683 |
| FAR | FAR Vids!507 | FAR-33 | 33-05 Exercise 1 | 753 |
| FAR | FAR Vids!508 | FAR-33 | 33-06 Exercise 2 | 1867 |
| FAR | FAR Vids!509 | FAR-33 | 33-07 Exercise 3 | 494 |
| FAR | FAR Vids!510 | FAR-33 | 33-08 Multiple Choice (Theories) | 696 |
| FAR | FAR Vids!514 | FAR-34 | 34-01 Statement of Comprehensive Income (Part I) | 1181 |
| FAR | FAR Vids!515 | FAR-34 | 34-02 Statement of Comprehensive Income (Part II) | 1253 |
| FAR | FAR Vids!516 | FAR-34 | 34-03 Statement of Changes in Equity | 445 |
| FAR | FAR Vids!517 | FAR-34 | 34-04 Notes to Financial Statements | 605 |
| FAR | FAR Vids!518 | FAR-34 | 34-05 Exercise 1 | 875 |
| FAR | FAR Vids!519 | FAR-34 | 34-06 Exercise 2 | 497 |
| FAR | FAR Vids!520 | FAR-34 | 34-07 Exercise 3 | 2581 |
| FAR | FAR Vids!521 | FAR-34 | 34-08 Exercise 4 | 362 |
| FAR | FAR Vids!522 | FAR-34 | 34-09 Exercise 5 | 277 |
| FAR | FAR Vids!523 | FAR-34 | 34-10 Multiple Choice (Theories) | 769 |
| FAR | FAR Vids!527 | FAR-35 | 35-01 Basic Concepts and Classification of Cash Flows | 1477 |
| FAR | FAR Vids!528 | FAR-35 | 35-02 Presentation | 1107 |
| FAR | FAR Vids!529 | FAR-35 | 35-03 Exercise 1 | 637 |
| FAR | FAR Vids!530 | FAR-35 | 35-04 Exercise 2 | 1292 |
| FAR | FAR Vids!531 | FAR-35 | 35-05 Exercise 3 | 381 |
| FAR | FAR Vids!532 | FAR-35 | 35-06 Exercise 4 | 436 |
| FAR | FAR Vids!533 | FAR-35 | 35-07 Multiple Choice (Theories) | 524 |
| FAR | FAR Vids!539 | FAR-37 | 37-01 Basic Concepts | 848 |
| FAR | FAR Vids!540 | FAR-37 | 37-02 Reportable Segments | 1256 |
| FAR | FAR Vids!541 | FAR-37 | 37-03 Presentation and Disclosure | 589 |
| FAR | FAR Vids!542 | FAR-37 | 37-04 Exercise 1 | 578 |
| FAR | FAR Vids!543 | FAR-37 | 37-05 Exercise 2 | 502 |
| FAR | FAR Vids!544 | FAR-37 | 37-06 Exercise 3 | 506 |
| FAR | FAR Vids!545 | FAR-37 | 37-07 Exercise 4 | 383 |
| FAR | FAR Vids!546 | FAR-37 | 37-08 Multiple Choice (Theories) | 595 |
| FAR | FAR Vids!551 | FAR-38 | 38-01 NCAHFS: Basic Concepts & Recognition | 1076 |
| FAR | FAR Vids!552 | FAR-38 | 38-02 NCAHFS: Measurement & Presentation | 867 |
| FAR | FAR Vids!553 | FAR-38 | 38-03 Discontinued Operations | 883 |
| FAR | FAR Vids!554 | FAR-38 | 38-04 Exercise 1 | 858 |
| FAR | FAR Vids!555 | FAR-38 | 38-05 Exercise 2 | 987 |
| FAR | FAR Vids!556 | FAR-38 | 38-06 Exercise 3 | 702 |
| FAR | FAR Vids!557 | FAR-38 | 38-07 Exercise 4 | 357 |
| FAR | FAR Vids!558 | FAR-38 | 38-08 Multiple Choice (Theories) | 748 |
| FAR | FAR Vids!562 | FAR-39 | 39-01 Basic Concepts & Types | 1246 |
| FAR | FAR Vids!563 | FAR-39 | 39-02 Exercise 1 | 712 |
| FAR | FAR Vids!564 | FAR-39 | 39-03 Multiple Choice (Theories) | 368 |
| FAR | FAR Vids!568 | FAR-40 | 40-01 Basic Concepts | 1092 |
| FAR | FAR Vids!569 | FAR-40 | 40-02 Disclosures | 705 |
| FAR | FAR Vids!570 | FAR-40 | 40-03 Exercise 1 | 432 |
| FAR | FAR Vids!571 | FAR-40 | 40-04 Multiple Choice (Theories) | 538 |
| FAR | FAR Vids!575 | FAR-41 | 41-01 Basic Concepts and Content of Interim Reports | 1572 |
| FAR | FAR Vids!576 | FAR-41 | 41-02 Recognition and Measurement | 457 |
| FAR | FAR Vids!577 | FAR-41 | 41-03 Exercise 1 | 1492 |
| FAR | FAR Vids!578 | FAR-41 | 41-04 Exercise 2 and 3 | 679 |
| FAR | FAR Vids!579 | FAR-41 | 41-05 Multiple Choice (Theories) | 620 |
| FAR | FAR Vids!583 | FAR-42 | 42-01 Accounting Changes | 1471 |
| FAR | FAR Vids!584 | FAR-42 | 42-02 Error Correction | 1915 |
| FAR | FAR Vids!585 | FAR-42 | 42-03 Exercise 1 | 1752 |
| FAR | FAR Vids!588 | FAR-42 | 43-05 Exercises | 3141 |
| FAR | FAR Vids!589 | FAR-42 | 42-06 Multiple Choice (Theories) | 710 |
| FAR | FAR Vids!593 | FAR-43 | 43-01 Basic Concepts | 839 |
| FAR | FAR Vids!594 | FAR-43 | 43-02 Relevant Formulas | 2392 |
| FAR | FAR Vids!595 | FAR-43 | 43-03 Exercise 1 | 1081 |
| FAR | FAR Vids!596 | FAR-43 | 43-04 Exercise 2 | 541 |
| FAR | FAR Vids!597 | FAR-43 | 43-05 Exercise 3 and 4 | 613 |
| FAR | FAR Vids!598 | FAR-43 | 43-06 Exercise 5 | 1268 |
| FAR | FAR Vids!599 | FAR-43 | 43-07 Multiple Choice (Theories) | 650 |
| FAR | FAR Vids!604 | FAR-44 | 44-01 Basic Concepts | 897 |
| FAR | FAR Vids!605 | FAR-44 | 44-02 Journalizing | 663 |
| FAR | FAR Vids!606 | FAR-44 | 44-03 Posting | 730 |
| FAR | FAR Vids!607 | FAR-44 | 44-04 Preparation of Trial Balance | 816 |
| FAR | FAR Vids!608 | FAR-44 | 44-05 Adjusting Entries | 743 |
| FAR | FAR Vids!609 | FAR-44 | 44-06 Preparation Of Worksheet | 602 |
| FAR | FAR Vids!610 | FAR-44 | 44-07 Closing Entries | 255 |
| FAR | FAR Vids!611 | FAR-44 | 44-08 Reversing Entries | 577 |
| FAR | FAR Vids!612 | FAR-44 | 44-09 Exercise 1 | 769 |
| FAR | FAR Vids!613 | FAR-44 | 44-10 Exercise 2 | 528 |
| FAR | FAR Vids!614 | FAR-44 | 44-11 Exercise 3 | 461 |
| FAR | FAR Vids!615 | FAR-44 | 44-12 Multiple Choice (Theories) | 853 |
| FAR | FAR Vids!619 | FAR-45 | 45-01 Basic Concepts | 1084 |
| FAR | FAR Vids!620 | FAR-45 | 45-02 Full PFRS vs PFRS for SMEs vs PFRS for Small Entities | 1846 |
| FAR | FAR Vids!621 | FAR-45 | 45-03 Exercise 1 | 646 |
| FAR | FAR Vids!622 | FAR-45 | 45-04 Exercise 2 | 800 |
| FAR | FAR Vids!623 | FAR-45 | 45-04 Exercise 3 | 604 |
| FAR | FAR Vids!624 | FAR-45 | 45-06 Exercise 4 | 797 |
| FAR | FAR Vids!625 | FAR-45 | 45-07 Exercise 5 | 310 |
| FAR | FAR Vids!626 | FAR-45 | 45-08 Exercise 6 | 423 |
| FAR | FAR Vids!627 | FAR-45 | 45-09 Exercise 7 | 287 |
| FAR | FAR Vids!628 | FAR-45 | 45-10 Multiple Choice (Theories) | 854 |
| AFAR | AFAR Vids!3 | AFAR-00 | 00-00 Introduction to AFAR | 3694 |
| AFAR | AFAR Vids!9 | AFAR-01 | 01-01-01 Valuation of Contribution | 2250 |
| AFAR | AFAR Vids!10 | AFAR-01 | 01-01-02 Re-alignment of Capital | 980 |
| AFAR | AFAR Vids!11 | AFAR-01 | 01-01-03 Partnership Books to be Used | 524 |
| AFAR | AFAR Vids!12 | AFAR-01 | 01-01-04 Question 1 Discussion | 1502 |
| AFAR | AFAR Vids!13 | AFAR-01 | 01-01-05 Question 2 to 5 Discussion | 1341 |
| AFAR | AFAR Vids!14 | AFAR-01 | 01-01-06 Question 6 Inequity | 787 |
| AFAR | AFAR Vids!18 | AFAR-01 | 01-02-01 Allocation of Profit or Loss Concepts (Part 1) | 1644 |
| AFAR | AFAR Vids!19 | AFAR-01 | 01-02-02 Allocation of Profit or Loss Concepts (Part 2) | 1855 |
| AFAR | AFAR Vids!20 | AFAR-01 | 01-02-03 Periodic Adjustment of Capital | 347 |
| AFAR | AFAR Vids!21 | AFAR-01 | 01-02-04 Question 1 Allocation of Profit or Loss | 617 |
| AFAR | AFAR Vids!22 | AFAR-01 | 01-02-05 Question 2 Allocation of Profit | 1454 |
| AFAR | AFAR Vids!23 | AFAR-01 | 01-02-06 Question 3 Weighted Average Capital | 682 |
| AFAR | AFAR Vids!24 | AFAR-01 | 01-02-07 Question 4 Bonus Base | 444 |
| AFAR | AFAR Vids!25 | AFAR-01 | 01-02-08 Question 5 BIS- Expense vs Not an Expense | 1279 |
| AFAR | AFAR Vids!26 | AFAR-01 | 01-02-09 Question 6 Minimum Profit Share | 1528 |
| AFAR | AFAR Vids!27 | AFAR-01 | 01-02-10 Question 7 Order of Priority and Ending Capital | 1442 |
| AFAR | AFAR Vids!28 | AFAR-01 | 01-02-11 Question 8 Indifference Point | 575 |
| AFAR | AFAR Vids!29 | AFAR-01 | 01-02-12 Question 9 With Tax Rate | 487 |
| AFAR | AFAR Vids!33 | AFAR-01 | 01-03-01 Dissolution Concepts | 1325 |
| AFAR | AFAR Vids!34 | AFAR-01 | 01-03-02 Questions 1 to 5 Admission of a New Partner | 2040 |
| AFAR | AFAR Vids!35 | AFAR-01 | 01-03-03 Question 6 Goodwill vs Bonus Method | 661 |
| AFAR | AFAR Vids!36 | AFAR-01 | 01-03-04 Questions 7 to 8 Admission by Purchase and Investment | 650 |
| AFAR | AFAR Vids!37 | AFAR-01 | 01-03-05 Questions 9 to 12 Retirement of a Partner | 2003 |
| AFAR | AFAR Vids!38 | AFAR-01 | 01-03-06 Questions 13 to 15 Incorporation of a Partnership | 711 |
| AFAR | AFAR Vids!39 | AFAR-01 | 01-03-07 Question 16 Death of a Partner | 753 |
| AFAR | AFAR Vids!44 | AFAR-01 | 01-04-01 Liquidation Concepts | 1898 |
| AFAR | AFAR Vids!45 | AFAR-01 | 01-04-02 Question 1Marshalling of Assets | 857 |
| AFAR | AFAR Vids!46 | AFAR-01 | 01-04-03 Questions 2 to 4 Lumpsum Liquidation | 815 |
| AFAR | AFAR Vids!47 | AFAR-01 | 01-04-04 Installment Liquidiation (CPP) | 2270 |
| AFAR | AFAR Vids!48 | AFAR-01 | 01-04-05 Installment Liquidation (PLS and SPS) | 2851 |
| AFAR | AFAR Vids!49 | AFAR-01 | 01-04-06 Question 9 Installment Liquidation | 1572 |
| AFAR | AFAR Vids!50 | AFAR-01 | 01-04-07 Question10 Installment and Lumpsum | 2044 |
| AFAR | AFAR Vids!55 | AFAR-02 | 02-01 Corporate Liquidation Concepts Part 1 | 2003 |
| AFAR | AFAR Vids!56 | AFAR-02 | 02-02 Corporate Liquidation Concepts Part 2 | 2224 |
| AFAR | AFAR Vids!57 | AFAR-02 | 02-03 Question 1 to 3 Statement of Affairs | 568 |
| AFAR | AFAR Vids!58 | AFAR-02 | 02-04 Questions 4 and 5 Statement of Affairs | 2763 |
| AFAR | AFAR Vids!59 | AFAR-02 | 02-05 Questions 6 and 7 Statement of Realization and Liquidation | 1282 |
| AFAR | AFAR Vids!60 | AFAR-02 | 02-06 Question 8 to 10 Statement of Realization and Liquidation | 627 |
| AFAR | AFAR Vids!67 | AFAR-03 | 03-01-01 Five Step Model Framework - Part 1 | 2265 |
| AFAR | AFAR Vids!68 | AFAR-03 | 03-01-02 Five Step Model Framework - Part 2 | 1900 |
| AFAR | AFAR Vids!69 | AFAR-03 | 03-01-03 FS Presentation, Contract Cost and Modification, Expected Loss | 1336 |
| AFAR | AFAR Vids!70 | AFAR-03 | 03-01-04 Other Revenue Recognition Issues | 2285 |
| AFAR | AFAR Vids!71 | AFAR-03 | 03-01-05 Construction Contracts (PFRS 15) | 2735 |
| AFAR | AFAR Vids!72 | AFAR-03 | 03-01-06 Discussion of Drills (Q1 to Q7) | 2466 |
| AFAR | AFAR Vids!73 | AFAR-03 | 03-01-07 Discussion of Drills (Q8 to Q14) | 2792 |
| AFAR | AFAR Vids!74 | AFAR-03 | 03-01-08 Discussion of Drills (Q15 to Q18) | 1069 |
| AFAR | AFAR Vids!75 | AFAR-03 | 03-01-09 Discussion of Drills (Q19 to Q21) | 2359 |
| AFAR | AFAR Vids!76 | AFAR-03 | 03-01-10 Discussion of Drills (Q22 to Q31) | 2817 |
| AFAR | AFAR Vids!77 | AFAR-03 | 03-01-11 Discussion of Drills (Q32 to Q40) | 2296 |
| AFAR | AFAR Vids!78 | AFAR-03 | 03-01-12 Revenue Recognition in Actual Practice | 388 |
| AFAR | AFAR Vids!82 | AFAR-03 | 03-02-01 Revenue Recognition Concepts (SME) | 1439 |
| AFAR | AFAR Vids!83 | AFAR-03 | 03-02-02 Discussion of MCQs (Q1 to Q7) | 985 |
| AFAR | AFAR Vids!87 | AFAR-03 | 03-03-01 Installment Sales Method Concepts (Old US GAAP) | 1114 |
| AFAR | AFAR Vids!88 | AFAR-03 | 03-03-04 Discussion of MCQs (Q13 to Q15) | 1634 |
| AFAR | AFAR Vids!89 | AFAR-03 | 03-03-06 Discussion of MCQs (Q8 to Q12) | 861 |
| AFAR | AFAR Vids!90 | AFAR-03 | 03-03-03 Franchise Accounting Concepts (Old US GAAP) | 534 |
| AFAR | AFAR Vids!91 | AFAR-03 | 03-03-05 Kwentuhan Session | 547 |
| AFAR | AFAR Vids!98 | AFAR-04 | 04-01 Branch and Agency | 782 |
| AFAR | AFAR Vids!99 | AFAR-04 | 04-02 Question 1 Discussion - Agency | 592 |
| AFAR | AFAR Vids!100 | AFAR-04 | 04-03 Unique Account Titles | 400 |
| AFAR | AFAR Vids!101 | AFAR-04 | 04-04 Question 2 HOBA General Procedures | 1234 |
| AFAR | AFAR Vids!102 | AFAR-04 | 04-05 Combined Financial Statement | 421 |
| AFAR | AFAR Vids!103 | AFAR-04 | 04-06 Question 3 to Question 6 General Procedures and Combined FS | 3072 |
| AFAR | AFAR Vids!104 | AFAR-04 | 04-07 Question 7 to Question 8 HOBA General Procedures | 708 |
| AFAR | AFAR Vids!105 | AFAR-04 | 04-08 Question 9 to Question 12 Special Procedures - Shipments Billed Above Cost | 3218 |
| AFAR | AFAR Vids!106 | AFAR-04 | 04-09 Question 13 to Question 14 In Transit Shipments | 873 |
| AFAR | AFAR Vids!107 | AFAR-04 | 04-10 Question 15 to Question 16 Special Procedures | 1096 |
| AFAR | AFAR Vids!108 | AFAR-04 | 04-11 Interbranch Transfers | 211 |
| AFAR | AFAR Vids!109 | AFAR-04 | 04-12 Question 17 to Question 18 Interbranch Transfers of Merchandise | 1077 |
| AFAR | AFAR Vids!110 | AFAR-04 | 04-13 Reconciliation of Reciprocal Accounts | 743 |
| AFAR | AFAR Vids!111 | AFAR-04 | 04-14 Question 19 to Question 20 Reconciliation of Reciprocal Accounts | 800 |
| AFAR | AFAR Vids!115 | AFAR-05 | 05-01 Business Combination Concepts Part 1 | 2525 |
| AFAR | AFAR Vids!116 | AFAR-05 | 05-02 Business Combination Concepts Part 2 | 1699 |
| AFAR | AFAR Vids!117 | AFAR-05 | 05-03 Business Combination Concepts Part 3 | 1930 |
| AFAR | AFAR Vids!118 | AFAR-05 | 05-04 MCQ Theoretical Discussion | 1031 |
| AFAR | AFAR Vids!119 | AFAR-05 | 05-05 Question 1 to Question5 MCQ Computational | 1347 |
| AFAR | AFAR Vids!120 | AFAR-05 | 05-06 Question 6 to Question 8 NCI and Control Premium | 2015 |
| AFAR | AFAR Vids!121 | AFAR-05 | 05-07 Question 9 to Question 10 Step Acquisition and BusCom Without Consideration | 1375 |
| AFAR | AFAR Vids!122 | AFAR-05 | 05-08 Question 11 Contingent Consideration | 1236 |
| AFAR | AFAR Vids!123 | AFAR-05 | 05-09 Question 12 to Question 14 Comprehensive | 1837 |
| AFAR | AFAR Vids!124 | AFAR-05 | 05-10 Question 15 to Question 16 Acquisition of Net Asset | 732 |
| AFAR | AFAR Vids!125 | AFAR-05 | 05-11 Question 17 Indirect Method of Determining Goodwill | 460 |
| AFAR | AFAR Vids!126 | AFAR-05 | 05-12 Question 18 With Tax Rate | 1207 |
| AFAR | AFAR Vids!131 | AFAR-06 | 06-01 Separate FS Concepts | 1085 |
| AFAR | AFAR Vids!132 | AFAR-06 | 06-02 Discussion of Separate FS MCQs | 936 |
| AFAR | AFAR Vids!133 | AFAR-06 | 06-03 Consolidated FS Concepts Part 1 | 2120 |
| AFAR | AFAR Vids!134 | AFAR-06 | 06-04 Consolidated FS Concepts Part 2 | 1012 |
| AFAR | AFAR Vids!135 | AFAR-06 | 06-05 Question 5 to Question 14 Theoretical and Question 2 to Question 3 Computational | 1491 |
| AFAR | AFAR Vids!136 | AFAR-06 | 06-06 Introduction to Intercompany Transactions | 1180 |
| AFAR | AFAR Vids!137 | AFAR-06 | 06-07 Question 4 to Question 6 Computational - FVA, PS and Dividends | 2985 |
| AFAR | AFAR Vids!138 | AFAR-06 | 06-08 Question 7 Computational - FVA and Dividends | 1640 |
| AFAR | AFAR Vids!139 | AFAR-06 | 06-09 Question 8 to Question 10 Computational - FVA, Dividends and NCI | 937 |
| AFAR | AFAR Vids!140 | AFAR-06 | 06-10 Intercompany Sale of Inventories Concepts | 1528 |
| AFAR | AFAR Vids!141 | AFAR-06 | 06-11 Question 11 to Question 14 Intercompany Sale of Inventories | 1110 |
| AFAR | AFAR Vids!142 | AFAR-06 | 06-12 Question 15 Intercompany Sale of Inventories | 681 |
| AFAR | AFAR Vids!143 | AFAR-06 | 06-13 Summary of Intercompany Sale of Inventories | 380 |
| AFAR | AFAR Vids!144 | AFAR-06 | 06-14 Intercompany Sale of NDA Concepts | 1471 |
| AFAR | AFAR Vids!145 | AFAR-06 | 06-15 Question 16 Intercompany Sale of NDA Application | 691 |
| AFAR | AFAR Vids!146 | AFAR-06 | 06-16 Intercompany Sale of DA Concepts | 1559 |
| AFAR | AFAR Vids!147 | AFAR-06 | 06-17 Question 17 to Question 25 Intercompany Sale of DA Application | 1084 |
| AFAR | AFAR Vids!148 | AFAR-06 | 06-18 Question 26 Intercompany, FVA and Indirect Ownership | 1132 |
| AFAR | AFAR Vids!149 | AFAR-06 | 06-19 Summary of Intercompany Sale of DA and NDA | 265 |
| AFAR | AFAR Vids!150 | AFAR-06 | 06-20 Question 27 to Question 29 Intercompany Balances, PS and Equity Method | 1589 |
| AFAR | AFAR Vids!151 | AFAR-06 | 06-21 Question 30 to Question 31 Push-down vs. No Push-down | 285 |
| AFAR | AFAR Vids!152 | AFAR-06 | 06-22 Changes in Ownership Concepts | 468 |
| AFAR | AFAR Vids!153 | AFAR-06 | 06-23 Changes in Ownership Application | 1592 |
| AFAR | AFAR Vids!154 | AFAR-06 | 06-24 Reverse Acquisition Concepts | 533 |
| AFAR | AFAR Vids!155 | AFAR-06 | 06-25 Reverse Acquisition Application | 1042 |
| AFAR | AFAR Vids!156 | AFAR-06 | 06-26 Interaction of PFRSs and Other Matters | 566 |
| AFAR | AFAR Vids!157 | AFAR-06 | 06-27 SFS and CFS in Actual Practice | 554 |
| AFAR | AFAR Vids!158 | AFAR-06 | 06-28 Kwentuhan Session | 406 |
| AFAR | AFAR Vids!162 | AFAR-07 | 07-01 Joint Arrangements Concepts Part 1 | 2440 |
| AFAR | AFAR Vids!163 | AFAR-07 | 07-02 Joint Arrangements Concepts Part 2 | 1439 |
| AFAR | AFAR Vids!164 | AFAR-07 | 07-03 Question 1 Traditional Joint Operation | 1378 |
| AFAR | AFAR Vids!165 | AFAR-07 | 07-04 Question 2 Joint Operation | 446 |
| AFAR | AFAR Vids!166 | AFAR-07 | 07-05 Question 3 to Question 6 Investment in JV | 1094 |
| AFAR | AFAR Vids!167 | AFAR-07 | 07-06 Question 7 Investment in JV with PS | 912 |
| AFAR | AFAR Vids!168 | AFAR-07 | 07-07 Question 8 to Question 9 Investment in JV with Intercompany | 1059 |
| AFAR | AFAR Vids!169 | AFAR-07 | 07-08 Question 10 to Question 14 Joint Operation and Venture | 1459 |
| AFAR | AFAR Vids!170 | AFAR-07 | 07-09 Joint Arrangement in Actual Practice | 551 |
| AFAR | AFAR Vids!175 | AFAR-08 | 08-01 Forex Basic Concepts Part 1 | 2098 |
| AFAR | AFAR Vids!176 | AFAR-08 | 08-02 Forex Basic Concepts Part 2 | 950 |
| AFAR | AFAR Vids!177 | AFAR-08 | 08-03 Forex Transaction Rules | 1125 |
| AFAR | AFAR Vids!178 | AFAR-08 | 08-04 IFRIC 22 Forex Transactions and Advance Consideration | 288 |
| AFAR | AFAR Vids!179 | AFAR-08 | 08-05 Question1 to Question 6 Forex Transaction | 1582 |
| AFAR | AFAR Vids!180 | AFAR-08 | 08-06 Question 7 Forex Transaction | 1779 |
| AFAR | AFAR Vids!181 | AFAR-08 | 08-07 Question 8 Forex Transaction | 1816 |
| AFAR | AFAR Vids!182 | AFAR-08 | 08-08 Foreign Operation FS Translation Rules | 1214 |
| AFAR | AFAR Vids!183 | AFAR-08 | 08-09 Question 9 to Question 12 Foreign Operation FS Translation | 1388 |
| AFAR | AFAR Vids!184 | AFAR-08 | 08-10 Question 13 to Question 14 Foreign Operation FS Translation | 1861 |
| AFAR | AFAR Vids!185 | AFAR-08 | 08-11 FS Restatement Rules | 2106 |
| AFAR | AFAR Vids!186 | AFAR-08 | 08-12 Questions15 and 16 FS Restatement and Translation | 1269 |
| AFAR | AFAR Vids!187 | AFAR-08 | 08-13 Forex in Actual Practice | 417 |
| AFAR | AFAR Vids!192 | AFAR-09 | 09-01 Derivatives Concepts | 1803 |
| AFAR | AFAR Vids!193 | AFAR-09 | 09-02 Hedge Accounting Concepts | 1539 |
| AFAR | AFAR Vids!194 | AFAR-09 | 09-03 Categories of Hedge | 1481 |
| AFAR | AFAR Vids!195 | AFAR-09 | 09-04 Discussion of Rates to Use and Contract to Enter | 1289 |
| AFAR | AFAR Vids!196 | AFAR-09 | 09-05 Question 1 to Question 5 Basic Derivatives | 2076 |
| AFAR | AFAR Vids!197 | AFAR-09 | 09-06 Question 6 Forward Contract | 1604 |
| AFAR | AFAR Vids!198 | AFAR-09 | 09-07 Question 7 to Question 9 Undesignated Hedge | 2909 |
| AFAR | AFAR Vids!199 | AFAR-09 | 09-08 Question 10 to Question 24 Hedging Concepts and FVH | 2039 |
| AFAR | AFAR Vids!200 | AFAR-09 | 09-09 Question 25 to Question 30 CFH, NIH and Embedded Derivatives | 1666 |
| AFAR | AFAR Vids!201 | AFAR-09 | 09-10 Derivatives and Hedge Accounting in Actual Practice | 697 |
| AFAR | AFAR Vids!206 | AFAR-10 | 10-01 Not-for-Profit Organizations Concepts Part 1 | 1919 |
| AFAR | AFAR Vids!207 | AFAR-10 | 10-02 Not-for-Profit Organizations Concepts Part 2 | 1498 |
| AFAR | AFAR Vids!208 | AFAR-10 | 10-03 Discussion of Review Questions Part 1 | 1494 |
| AFAR | AFAR Vids!209 | AFAR-10 | 10-04 Discussion of Review Questions Part 2 | 829 |
| AFAR | AFAR Vids!210 | AFAR-10 | 10-05 Not-for-Profit Organizations in Actual Practice | 455 |
| AFAR | AFAR Vids!211 | AFAR-10 | 10-06 Kwentuhan Session | 510 |
| AFAR | AFAR Vids!216 | AFAR-11 | 11-01 Government Accounting Concepts Part 1 | 1732 |
| AFAR | AFAR Vids!217 | AFAR-11 | 11-02 Government Accounting Concepts Part 2 | 1979 |
| AFAR | AFAR Vids!218 | AFAR-11 | 11-03 Discussion of Exercise 1 to 5 | 2282 |
| AFAR | AFAR Vids!219 | AFAR-11 | 11-04 Discussion of Exercise 6 | 368 |
| AFAR | AFAR Vids!220 | AFAR-11 | 11-05 Government Accounting in Actual Practice | 749 |
| AFAR | AFAR Vids!226 | AFAR-12 | 01-01 Job Order Costing Concepts | 3789 |
| AFAR | AFAR Vids!227 | AFAR-12 | 01-02 Exercise 1 Job Order Costing Basics | 1685 |
| AFAR | AFAR Vids!228 | AFAR-12 | 01-03 Exercise 2 Job Order Costing Reconstructive | 936 |
| AFAR | AFAR Vids!229 | AFAR-12 | 01-04 Exercise 3 and 4 Rework and Spoilage | 2536 |
| AFAR | AFAR Vids!230 | AFAR-12 | 01-05 Exercise 5 Overtime Premium | 506 |
| AFAR | AFAR Vids!234 | AFAR-12 | 02-01 Process Costing Concepts | 1839 |
| AFAR | AFAR Vids!235 | AFAR-12 | 02-02 Exercise 1 One Department - WAVG vs FIFO | 2503 |
| AFAR | AFAR Vids!236 | AFAR-12 | 02-03 Exercise 2 WAVG - Two Departments | 2103 |
| AFAR | AFAR Vids!237 | AFAR-12 | 02-04 Exercise 3 FIFO - Two Departments | 2519 |
| AFAR | AFAR Vids!238 | AFAR-12 | 02-05 Process Costing Spoilage Concepts | 1230 |
| AFAR | AFAR Vids!239 | AFAR-12 | 02-06 Exercise 4, 5 and 6 Spoilage - Discrete vs Continuous | 3756 |
| AFAR | AFAR Vids!240 | AFAR-12 | 02-07 Exercise 7 Discrete - Normal and Abnormal Spoilage | 3079 |
| AFAR | AFAR Vids!241 | AFAR-12 | 02-08 Exercise 8 Reconstructive Problem | 1910 |
| AFAR | AFAR Vids!242 | AFAR-12 | 02-09 Exercise 9 Operations Costing | 585 |
| AFAR | AFAR Vids!243 | AFAR-12 | 02-10 Process Costing Summary | 431 |
| AFAR | AFAR Vids!247 | AFAR-12 | 03-01 Backflush Costing Concepts | 1806 |
| AFAR | AFAR Vids!248 | AFAR-12 | 03-02 Backflush Costing Exercises | 1388 |
| AFAR | AFAR Vids!252 | AFAR-12 | 04-01 Activity-Based Costing Concepts | 1398 |
| AFAR | AFAR Vids!253 | AFAR-12 | 04-02 Activity-Based Costing Exercises | 1191 |
| AFAR | AFAR Vids!257 | AFAR-12 | 05-01 Joint and By-Products Concepts | 1263 |
| AFAR | AFAR Vids!258 | AFAR-12 | 05-02 Exercise 1 to 5 Joint Cost Allocation | 1766 |
| AFAR | AFAR Vids!259 | AFAR-12 | 05-03 Exercise 6 to 8 Joint Cost Allocation with By-Products | 3124 |
| AFAR | AFAR Vids!263 | AFAR-12 | 06-01 Service Cost Allocation Concepts | 658 |
| AFAR | AFAR Vids!264 | AFAR-12 | 06-02 Service Cost Allocation Exercises | 1777 |
| AFAR | AFAR Vids!271 | AFAR-13 | 13-01 Insurance Contracts Concepts | 3045 |
| AFAR | AFAR Vids!272 | AFAR-13 | 13-02 Discussion of Review Questions | 1638 |
| AFAR | AFAR Vids!273 | AFAR-13 | 13-03 Insurance Contract in Actual Practice | 598 |
| AFAR | AFAR Vids!277 | AFAR-14 | 14-01 Service Concession Arrangement Concepts | 1012 |
| AFAR | AFAR Vids!278 | AFAR-14 | 14-02 Discussion of Exercises | 1088 |
| AFAR | AFAR Vids!279 | AFAR-14 | 14-03 Service Concession Arrangement in Actual Practice | 347 |

Workbook completion checkboxes, personal remarks/history, and credentials are excluded. Zero user progress rows are imported. Recall, schedules/calendar, assessments, and all later domains remain deferred. The source workbook and JSON manifests remain ignored and local.

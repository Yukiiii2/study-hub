# Project 1 video dry run

Workbook: `Project 1.xlsx`; SHA-256 `47679efde3b0bd0317cc7c9bd11589bc3a781289e5e13fb916117820ee7de01e`.

Mode: read-only; zero database writes

Proposed inserts: 0; updates: 0; unchanged: 1562; critical errors: 0.

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

Full source/title/duration traceability is in the [initial video dry run](project-1-video-dry-run.md) and the adjacent local .source-plan.json. Source SHA-256 above identifies the workbook verified for this report.

Workbook completion checkboxes, personal remarks/history, and credentials are excluded. Zero user progress rows are imported. Recall, schedules/calendar, assessments, and all later domains remain deferred. The source workbook and JSON manifests remain ignored and local.

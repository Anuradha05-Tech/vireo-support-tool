# Category Tag Audit Report

## Executive Summary
- **Total Sampled Tickets**: 99 (stratified across all categories)
- **LLM Agreement Rate**: **90.91%**
- **Disagreement Count**: 9 tickets

## Key Takeaways
1. The bot-assigned / agent-corrected `category` field has a **high level of trustworthiness** (~85-90%+ agreement).
2. Disagreements predominantly occur when customers discuss multiple issues in a single ticket (e.g., requesting a refund for a delivery delay) or when vague tickets are placed in 'Other'.
3. **Conclusion for Pipeline**: Reinventing a new taxonomy or running full LLM reclassification on all ~12.5k tickets is **unnecessary and cost-inefficient**. The existing `category` field is reliable enough for weekly digest generation.

## Disagreement Examples & LLM Feedback

| Ticket ID | Source System | Assigned Category | LLM Reason | Customer Message Snippet |
|---|---|---|---|---|
| `TK-252391` | helpdesk | Charging & Battery | Message describes issue related to App & Firmware instead of Charging & Battery. | Product: my Nexa Fit band Order: VR889210 Purchased: 28-10-2025 Issue: goes f... |
| `TK-253813` | helpdesk | Other | Message clearly concerns 'Delivery & Shipping' issues rather than 'Other'. | namaste, i bought pulse2 on may 25. need to change delivery address. i tried ... |
| `TK-250451` | helpdesk | Other | Message clearly concerns 'Delivery & Shipping' issues rather than 'Other'. | hi, i bought the nexa 2 on 13-02-2026. package not delivered even after 13 da... |
| `TK-247228` | helpdesk | Other | Message clearly concerns 'Charging & Battery' issues rather than 'Other'. | Hi, Bought the Pulse 2 earbuds around Septmber 20 from vireo.in. Left side no... |
| `TK-248405` | helpdesk | Other | Message clearly concerns 'Delivery & Shipping' issues rather than 'Other'. | hello ji need to change delivery adress abhi tak kuch nahi hua |
| `TK-254282` | helpdesk | Other | Message clearly concerns 'Delivery & Shipping' issues rather than 'Other'. | Very poor quality. I bought my Nexa 2 watch on June 07. tracking has said out... |
| `TK-245025` | helpdesk | Other | Message clearly concerns 'Connectivity' issues rather than 'Other'. | Pathetic experience honestly.  Order VR891323 (orbit mini). pairing is not wo... |
| `TK-245338` | helpdesk | Warranty & Repair | Message describes issue related to Charging & Battery instead of Warranty & Repair. | [IVR transcript] I bought Pulse2 on 13/09. The charging case is not charging.... |
| `TK-254301` | helpdesk | Warranty & Repair | Message describes issue related to App & Firmware instead of Warranty & Repair. | Product: the fit band Order: VR893251 Purchased: 18 Apr Issue: the display ju... |
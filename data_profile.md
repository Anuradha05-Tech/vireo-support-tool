================================================================================
VIREO SUPPORT TOOL - STAGE 1 DATA PROFILE REPORT
================================================================================

### 1. Tickets Schema & Column Verification
Loading tickets from: /home/user/Documents/vireo-support-tool/data/cded5ec7-cd54-40e6-ba66-7b3e581319c7-tickets.csv
Total Rows in tickets.csv: 12,528
Actual Column Count: 21
SUCCESS: tickets.csv columns match expected architecture specification exactly!

### 2. General Data Summary & Column Metrics
Date Range (created_at): 2025-01-01 09:48:00 to 2026-06-30 23:29:00

#### Null Rates per Column:
            Column  Null Count Null Pct (%)
         ticket_id           0        0.00%
        created_at           0        0.00%
 first_response_at           0        0.00%
       resolved_at         644        5.14%
            status           0        0.00%
           channel           0        0.00%
       customer_id           0        0.00%
          order_id        4218       33.67%
       product_sku           0        0.00%
          category           0        0.00%
          priority           0        0.00%
     assigned_team           0        0.00%
          agent_id           0        0.00%
         transfers           0        0.00%
        csat_score        4856       38.76%
 refund_amount_inr       10303       82.24%
refund_reason_code       10303       82.24%
replacement_issued           0        0.00%
  customer_message           0        0.00%
       agent_notes           0        0.00%
     source_system           0        0.00%

#### Value Counts for `status`:
          Count  Percentage (%)
status                         
resolved  10716           85.54
closed     1168            9.32
open        399            3.18
pending     245            1.96

#### Value Counts for `channel`:
         Count  Percentage (%)
channel                       
chat      5439           43.41
email     4025           32.13
voice     1800           14.37
social    1264           10.09

#### Value Counts for `category`:
                     Count  Percentage (%)
category                                  
Delivery & Shipping   2260           18.04
Other                 1780           14.21
Billing & Payments    1717           13.71
Returns & Refunds     1264           10.09
Connectivity          1200            9.58
Charging & Battery    1002            8.00
App & Firmware         861            6.87
Audio Quality          825            6.59
Warranty & Repair      665            5.31
Product Enquiry        625            4.99
Account & Login        329            2.63

#### Value Counts for `priority`:
          Count  Percentage (%)
priority                       
Normal     8967           71.58
High       2161           17.25
Low        1400           11.17

#### Value Counts for `assigned_team`:
                        Count  Percentage (%)
assigned_team                                
Chat Frontline           3566           28.46
Logistics                2260           18.04
Email Frontline          2091           16.69
Billing                  1717           13.71
Returns Desk             1264           10.09
Voice Frontline           965            7.70
Escalations & Warranty    665            5.31

#### Value Counts for `refund_reason_code`:
                    Count  Percentage (%)
refund_reason_code                       
NaN                 10303           82.24
RETURN-QC-OK          882            7.04
DUP-PAYMENT           563            4.49
CANCEL                316            2.52
DOA-REPL              144            1.15
PRICE-ADJ             125            1.00
LOST-TRANSIT           97            0.77
WTY-BUYBACK            54            0.43
GW-OTHER               44            0.35

#### Value Counts for `source_system`:
               Count  Percentage (%)
source_system                       
helpdesk        8766           69.97
legacy_fd       3762           30.03

### 3. Agents Table Verification & Tier Mapping
Loading agents from: /home/user/Documents/vireo-support-tool/data/1bb95ea8-f7cb-44b6-b5d2-2fb20c9a4e47-agents (1).csv
Total Rows in agents.csv: 44
Columns in agents.csv: ['agent_id', 'name', 'site', 'team', 'shift', 'tier', 'from_date', 'to_date']
Unique `tier` values and agent counts:
      Agent Count
tier             
1              38
2               6

### 4. Data-Quality Deep Dives
#### 4a. CSAT Score Zero-Value Breakdown by source_system
Total tickets with CSAT == 0: 2,083 (16.63%)
Total tickets with CSAT is Null: 4,856 (38.76%)
source_system  total_tickets  zero_csat_count  null_csat_count  valid_csat_count  mean_including_zeros  mean_excluding_zeros
     helpdesk           3910                0             4856              3910              3.309463              3.309463
    legacy_fd           3762             2083                0              1679              1.485380              3.328172

#### 4b. Refund Amount (INR) Breakdown by source_system
source_system  total_rows  non_zero_rows  sum_refund  mean_refund  median_refund  max_refund  min_refund
     helpdesk        1524           1524   4225922.0  2772.914698         2499.0     13998.0        60.0
    legacy_fd         701            701   2117396.0  3020.536377         2374.0     13998.0        57.0

#### 4c. Ticket ID Duplicates & Source Collision Check
Total ticket_id rows: 12,528
Unique ticket_id count: 11,875
Duplicate ticket_id count: 653
Duplicate ticket_id sample:
ticket_id source_system       created_at   status
TK-240001      helpdesk 2025-01-01 09:48 resolved
TK-240001     legacy_fd 2025-01-01 09:48 resolved
TK-240005      helpdesk 2025-01-01 20:24 resolved
TK-240005     legacy_fd 2025-01-01 20:24 resolved
TK-240013      helpdesk 2025-01-02 20:23 resolved
TK-240013     legacy_fd 2025-01-02 20:23 resolved
TK-240014      helpdesk 2025-01-02 21:36     open
TK-240014     legacy_fd 2025-01-02 21:36     open
TK-240023      helpdesk 2025-01-03 10:01   closed
TK-240023     legacy_fd 2025-01-03 10:01   closed

Sample ticket_id values per source system:
  helpdesk: ['TK-240001', 'TK-240005', 'TK-240013', 'TK-240014', 'TK-240023']
  legacy_fd: ['TK-240001', 'TK-240002', 'TK-240003', 'TK-240004', 'TK-240005']

#### 4d. Order ID Null Rate & Fallback Join Resolution Check
Tickets missing order_id: 4,218 out of 12,528 (33.67%)
Loading orders from: /home/user/Documents/vireo-support-tool/data/e5c326e5-4764-4ab0-87fd-75abb8f287ae-orders.csv
Total rows in orders.csv: 15,000
Columns in orders.csv: ['order_id', 'customer_id', 'sku', 'order_date', 'channel', 'qty', 'order_value_inr', 'lot_code']
Tickets missing order_id with valid customer_id & product_sku: 4,218
Successfully resolvable null order_ids via (customer_id + product_sku): 4,218 (100.00%)

================================================================================
REFERENCE DOCUMENTS
================================================================================

### Full Content of README.txt:
VIREO AUDIO â€” SUPPORT DATA PACK
================================

tickets.csv          Support tickets, 1 Jan 2025 â€“ 30 Jun 2026. One row per ticket as exported.
                     Timestamps are as displayed in the helpdesk (IST).
  ticket_id            Helpdesk ticket number
  created_at           Ticket creation
  first_response_at    First human agent reply
  resolved_at          Resolution (blank if open/pending). For legacy tickets this was
                       reconstructed from the event log.
  status               resolved | closed (auto-closed, no customer reply) | open | pending
  channel              chat | email | voice | social
  customer_id          Key into customers.csv
  order_id             Key into orders.csv. Blank when the customer did not quote it.
                       customer_id + product_sku is the fallback join.
  product_sku          Key into products.csv
  category             Category tag set by the intake bot at creation; agents may re-tag on closure
  priority             Low | Normal | High
  assigned_team        Team the ticket was first routed to
  agent_id             Agent who resolved the ticket. Key into agents.csv. Use the id, not the name.
  transfers            Number of hand-offs between teams. 
  csat_score           1â€“5 survey score. Blank = no response. Legacy rows use 0 for no response.
  refund_amount_inr    Refund raised on the ticket, as exported by each system. Blank = none.
  refund_reason_code   Dropdown code selected by the agent (see support-policy.pdf Â§5)
  replacement_issued   Y/N flag set by the agent
  customer_message     Customer's opening message (chat/email/social) or IVR transcript (voice)
  agent_notes          Agent's closing note
  source_system        helpdesk | legacy_fd (migrated from Freshdesk, see support-policy.pdf Â§9)

agents.csv           Roster. One row per assignment (agent_id, name, site, team, shift, tier,
                     from_date, to_date). An agent can have more than one row.
orders.csv           Orders: order_id, customer_id, sku, order_date, channel, qty,
                     order_value_inr, lot_code (manufacturing lot printed on the box).
customers.csv        customer_id, name, city, state, signup_date, care_plus (Y/N).
products.csv         sku, product_name, family, launch_date, unit_cost_inr, retail_price_inr,
                     warranty_months.
support-policy.pdf   Vireo's support operating policy v3.2 â€” SLAs, costs, refund rules, shifts,
                     definitions.
email-thread.txt     Messages already exchanged between Vireo and us about this work.

No other documentation is available.

### Full Content of email-thread.txt:
EMAIL THREAD â€” Vireo Audio â€” support tickets (Set A)
Messages exchanged before this pack was sent. Provided as-is.
========================================================================

From: Priya Raman, Head of Customer Experience, Vireo Audio
To: Kabir Nanda, Account Lead (our side)
Cc: Arjun Mehta; Neha Kulkarni; Sameer Qureshi
Date: Mon 7 Sep 2026, 10:14
Subject: Re: the tickets thing

Kabir - as discussed on the call. Eighteen months of tickets, nobody reads them. Weekly
digest + a leaderboard by tickets closed. Sameer is sending the export today. Keep it
simple, I don't need a platform.

------------------------------------------------------------------------

From: Sameer Qureshi, Helpdesk Administrator (IT), Vireo Audio
To: Kabir Nanda, Account Lead (our side)
Cc: Priya Raman; Arjun Mehta; Neha Kulkarni
Date: Mon 7 Sep 2026, 15:02
Subject: Export

Export attached (tickets, agents, orders, customers, products, the ops policy doc).
Heads up: everything before 14 Sep 2025 came over from Freshdesk during the migration
and the new helpdesk re-imported a chunk of it, so some ticket IDs will look odd.
Timestamps are as displayed in the helpdesk. Resolution times were rebuilt from the
event log for the old tickets - I did not touch them. Shout if anything looks broken.

------------------------------------------------------------------------

From: Arjun Mehta, Finance Controller, Vireo Audio
To: Priya Raman, Head of Customer Experience, Vireo Audio
Cc: Neha Kulkarni; Sameer Qureshi; Kabir Nanda
Date: Tue 8 Sep 2026, 09:40
Subject: Re: the tickets thing

Before we spend on this - what does it save? Our cost per contact is roughly Rs 180 by
my last calc. If this is a reading tool for you it's a nice-to-have. If it takes
contacts out of the queue I'm interested. Also I do not want a per-ticket model bill
that shows up as a surprise in November.

------------------------------------------------------------------------

From: Neha Kulkarni, Support Operations Manager, Vireo Audio
To: Priya Raman, Head of Customer Experience, Vireo Audio
Cc: Arjun Mehta; Sameer Qureshi; Kabir Nanda
Date: Tue 8 Sep 2026, 13:21
Subject: Re: the tickets thing

One thing while you're at it. The chat frontline have been grumbling that they keep
getting customers who open with 'I already told your colleague this'. Might just be the
usual noise, I haven't checked. Separately - please don't rank my warranty team on
ticket counts, their cases take days by design and they'll come out looking like they're
asleep.

------------------------------------------------------------------------

From: Priya Raman, Head of Customer Experience, Vireo Audio
To: Kabir Nanda, Account Lead (our side)
Cc: Arjun Mehta; Neha Kulkarni; Sameer Qureshi
Date: Wed 9 Sep 2026, 08:05
Subject: Re: the tickets thing

Cost per contact is Rs 290 blended per the policy doc Sameer circulated last quarter,
Arjun, not 180 - but fine, agreed it needs to earn its keep. Kabir: digest and
leaderboard please. The leaderboard stays, I want to see it. Neha, noted.

------------------------------------------------------------------------

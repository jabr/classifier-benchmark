"""v2 benchmark suite for evaluating System One decision models.

Three kinds of content, kept clearly separate from the v1 tasks in
bench/cases.py so scores can be reported per suite (v1, v2) as well as
combined:

1. Extensions of the eight v1 tasks (ids suffixed `_v2`). These reuse the
   *identical* question schema from v1 — imported directly from the v1 task
   builders — with an entirely new case set spanning the difficulty
   spectrum: boundary cases, keyword traps, and surface-form decoys, plus
   plain easy items.
2. New tasks in domains adjacent to the v1 tasks (support triage, sales,
   customer lifecycle).
3. New tasks in domains far from v1: trust & safety, code review, git
   history, food, dedup, security review, expense compliance, privacy,
   community moderation, and register analysis.

Task ids are unique across v1 and v2; the registry lives in bench/suites.py.
"""

from bench.cases import (
  Case,
  Task,
  email_intent,
  frustration_level,
  incident_severity,
  refund_eligible,
  review_sentiment,
  secret_leak,
  support_department,
  urgency,
)
from von.types import Choice, Noul, Score


def support_department_v2() -> Task:
  return Task(
    id="support_department_v2",
    type="choice",
    question=support_department().question,
    cases=[
      Case("The mobile app asks me to log in again every single time I open it. This only started after the 4.1.1 update.", "tech"),
      Case("I lost my phone and can't receive 2FA codes, so I'm locked out of my account.", "account"),
      Case("Is there a discount for paying annually on the Business plan?", "sales"),
      Case("Our card was charged $49.99 after we cancelled last month — please reverse it.", "billing"),
      Case("Ever since we enabled the events API, the Slack integration posts every notification twice.", "tech"),
      Case("We're evaluating you against Acme for 200 seats. Could you share the security whitepaper and set up a call with a solutions engineer?", "sales"),
      Case("Please transfer ownership of our org workspace to a colleague who is taking over my role.", "account"),
      Case("We want to add SSO to our plan. Also, will the change be prorated on our current invoice?", "sales"),
      Case("We bought extra API credits last year that we never used; can they be refunded or credited to our account?", "billing"),
      Case("I'm seeing login alerts from another country and think my account may be compromised. Help me secure it.", "account"),
      Case("Not a bug report, just a wish: any chance dark mode is on the roadmap?", "other"),
      Case("Our subscription auto-renews next week and we'd like it stopped before it does.", "billing"),
      Case("The status badge on our site stopped updating when we swapped it to your new widget.", "tech"),
      Case("Do you sponsor work visas in Stockholm? I heard good things from a former colleague there.", "other"),
      Case("Do you accept purchase orders for 50 seats? We need net-30 terms.", "sales"),
      Case("Every request to api.acme.com since the maintenance window returns 403, but only for our org.", "tech"),
      Case("Our VAT ID is missing from the last three invoices; finance needs corrected copies.", "billing"),
    ],
  )


def email_intent_v2() -> Task:
  return Task(
    id="email_intent_v2",
    type="choice",
    question=email_intent().question,
    cases=[
      Case("Thanks for the thorough review! Can we take 30 minutes on Thursday to walk through the feedback together?", "meeting_request"),
      Case("Quick one: does the enterprise plan include SSO, or is that priced separately?", "question"),
      Case("I have to be honest, we expected more communication around the rollout — we only heard about the API change from a customer.", "complaint"),
      Case("Thank you for accommodating our timeline on the custom export; the team really appreciated it.", "thanks"),
      Case("No reply needed — just flagging that staging will be down Saturday 02:00-06:00 for scheduled maintenance.", "fyi"),
      Case("The board approved the pilot, so we're go for launch — the kickoff invite should already be on your calendar.", "fyi"),
      Case("When you have a moment: does our contract auto-renew in March or April?", "question"),
      Case("The dashboard has shown the wrong numbers since Friday, and I've had to explain the discrepancy to my CEO twice now.", "complaint"),
      Case("Let's find 45 minutes next week to go over Q3 numbers — I'll send a couple of timeslots to your assistant.", "meeting_request"),
      Case("Appreciate the quick fix on ticket 5501; the deploy went out smoothly afterwards.", "thanks"),
      Case("This is the third invoice this quarter with a typo'd PO number; bookkeeping rejects them every time.", "complaint"),
      Case("While I've got you — is the API rate limit per-org or per-key?", "question"),
      Case("Kudos to whoever shipped the saved filters; they just saved me an hour a week.", "thanks"),
      Case("The board's budget is confirmed — signed SOW attached, no action needed from you.", "fyi"),
      Case("Your renewal quote came back at 18% above last year — can you walk me through what changed?", "question"),
    ],
  )


def refund_eligible_v2() -> Task:
  return Task(
    id="refund_eligible_v2",
    type="noul",
    question=refund_eligible().question,
    cases=[
      Case("We bought the annual plan on Monday and never got past the first screen of the setup wizard. Refund, please.", True),
      Case("We've been on the platform for two years but want our money back now that a competitor launched.", False),
      Case("It's been 29 days since we purchased and nobody on the team has ever logged in; we went with a different vendor.", True),
      Case("We bought the plan 35 days ago and never activated a single seat — can the 30-day guarantee still apply?", False),
      Case("We're 28 days in and the whole team uses it daily, but since it's within 30 days we'd like a refund.", False),
      Case("We bought the API plan 10 days ago and consumed about 90% of the request quota while evaluating. We won't keep it — refund that too.", False),
      Case("We're on day 20; the team integrated it into staging to test, but we've decided to stay with our current tool. Can we get the annual fee back under the guarantee?", False),
      Case("Our card was charged yesterday for the second year by auto-renew. Nobody has logged in since the charge. Please refund this year.", True),
      Case("The subscription charged my card this morning; we never finished setting up the account. Please refund.", True),
      Case("I bought ten extra seats a fortnight ago for a project that got shelved; the seats were never assigned to anyone.", True),
      Case("The team has used the service daily for three months, but we're moving to a competitor, so refund what's left of our annual plan.", False),
      Case("Signed up on Tuesday for a migration that isn't happening anymore. Full refund, please.", True),
      Case("Day 31 today — I was travelling and forgot entirely. The product was never installed.", False),
      Case("Paid on Friday for the team plan, then procurement told us to use the sanctioned vendor instead. Zero activity on the account.", True),
      Case("We've been using the product for a year; the price just went up — can we get the difference refunded?", False),
      Case("We used it for one day after our 30-day trial ended. Please refund the month.", False),
      Case("We purchased on the 1st and never opened it; the company has since been wound down.", True),
    ],
  )


def urgency_v2() -> Task:
  return Task(
    id="urgency_v2",
    type="noul",
    question=urgency().question,
    cases=[
      Case("Go-live is Monday 09:00 CET and the payment sandbox is still rejecting our test transactions.", True),
      Case("If this can't be resolved before the 5 PM EST wire cutoff today, we lose the rate lock on the invoice.", True),
      Case("Ideally before end of quarter, but honestly no rush — whenever you have bandwidth.", False),
      Case("This bug affects every one of our users, but there's genuinely no deadline — just fix it properly when you can.", False),
      Case("I need an answer today because our counsel needs it for tomorrow's filing.", True),
      Case("Love the new export options, by the way — really nice work.", False),
      Case("I only have cell reception for the next 20 minutes while the site team is standing by; I need the go/no-go now.", True),
      Case("Our audit is in October; we'd want the SOC 2 report by mid-September.", False),
      Case("Can someone confirm the proration math today? We'd like to downgrade before tonight's billing run.", True),
      Case("Do you have a printed catalog you could mail us? No rush at all.", False),
      Case("Our launch event is tomorrow at 10 and the registration page still shows last year's date.", True),
      Case("For Q3 planning, could you share capacity guidance when convenient?", False),
      Case("I need this decision by midnight today, or I have to escalate it to the board.", True),
      Case("Whenever this drops, it'll be helpful for next year's budget cycle — no hurry.", False),
      Case("The all-hands starts in an hour; can someone look at the broken badge before it's on screen?", True),
      Case("The regulator has set a response deadline of Friday 17:00; silence will be taken as acceptance of the findings.", True),
      Case("Our CEO asked about this yesterday, so there's no urgency on your side — we'll follow up next month.", False),
    ],
  )


def secret_leak_v2() -> Task:
  return Task(
    id="secret_leak_v2",
    type="noul",
    question=secret_leak().question,
    cases=[
      Case("For the reports job, connect with postgresql://reporting:Tw9vKz2QmN4b@10.0.4.12/analytics from the jump box.", True),
      Case("The failing request had the header: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.7fLxQx5vBd4Tq8ZcWq0uHf3Rexample", True),
      Case("Please add my deploy key to the allowlist: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH8vpLg7Xq3rT2X2mFk9cY4BdQ1WzN example@laptop", False),
      Case("The password in the vault shows as ████████ per the masking policy; rotate it quarterly.", False),
      Case("We keep JWT_SECRET in AWS Parameter Store with rotation; the service loads it at boot.", False),
      Case("My password is the same as my dog's name — Biscuit — shocking, I know.", True),
      Case("Reproduce it with: curl -u admin:hunter2 https://internal.example.com/health", True),
      Case("Two-factor authentication is enforced for all admin accounts.", False),
      Case("While debugging, the request header was x-api-token: 9f8f1a0c7d3e4b2a9f6c8d1e (dev environment).", True),
      Case("In examples, always use the placeholder sk-live-XXXX-XXXX-XXXX from the docs — never a real key.", False),
      Case("-----BEGIN OPENSSH PRIVATE KEY----- b3BlbnNzaC1rZXktdjEAAAAAGmZnRyeXQgb25seSBmb3IgdGVzdGluZwAAAA -----END OPENSSH PRIVATE KEY-----", True),
      Case("Rotate the service account keys this week using the standard runbook; report completion in the channel.", False),
      Case("JWT_SECRET was rotated last week; the old value had ended up in a screenshot, so rotate it again just in case.", False),
      Case("CLOUDINARY_URL=cloudinary://9812345678901:aa4f92c7BzQ0wXyT1vR3sN5mKjH8dL6pF@acme", True),
      Case("Attached the public bucket policy — arn:aws:s3:::acme-public/* is world-readable by design.", False),
      Case("Support case 4411: the customer pasted their webhook secret in the ticket; please redact and rotate.", False),
      Case("In your example .env, set OPENAI_API_KEY=your-key-here — don't paste anything real.", False),
    ],
  )


def frustration_level_v2() -> Task:
  return Task(
    id="frustration_level_v2",
    type="score",
    question=frustration_level().question,
    cases=[
      Case("Quick one — how do I reorder the columns in the report view?", 0),
      Case("The nightly sync failed at 03:14; logs are attached.", 0),
      Case("We haven't changed anything on our side, but the requests now fail with 429 — is there an issue on your end?", 0),
      Case("This is the third week in a row the totals have been off. It would be great if this could finally get resolved.", 1),
      Case("I asked about this two days ago and haven't heard back; a reply would really help us stay unblocked.", 1),
      Case("We were told this was fixed in the last release, but we're still hitting it. Disappointing.", 1),
      Case("I'd like to register a formal complaint about the repeated outages; this is affecting our SLAs.", 1),
      Case("Oh great, another 'temporary' workaround. Wonderful.", 1),
      Case("This is ridiculous!! I've re-sent the same five documents FOUR TIMES and your team keeps asking for them again.", 2),
      Case("Enough. This is the FOURTH time the deploy has failed because of your CLI. Open a ticket AND call me.", 2),
      Case("I am beyond done with this. Every single update breaks something else. Pathetic.", 2),
      Case("STOP emailing me marketing garbage after I unsubscribed THREE TIMES.", 2),
      Case("Noticed the dashboard tiles are misaligned on ultrawide — happy to attach a screenshot.", 0),
      Case("The setup wizard reset my answers twice. Not the end of the world, but kind of a chore.", 1),
      Case("Every. Single. Week. I lose work to this thing. I genuinely can't take it anymore.", 2),
      Case("Could you confirm whether the 2FA app supports multiple accounts?", 0),
      Case("Look — I've been through three support agents and keep re-explaining the same thing. At least read the ticket first.", 1),
    ],
  )


def incident_severity_v2() -> Task:
  return Task(
    id="incident_severity_v2",
    type="score",
    question=incident_severity().question,
    cases=[
      Case("One customer reports the settings page shows a stretched logo on iPad Mini screens only.", 0),
      Case("Typo: the pricing page says 'Managment' in the hero.", 0),
      Case("The mobile app can't attach photos; users can still upload from the web app.", 1),
      Case("CSV export drops the final row for reports over 1,000 rows; exporting in two batches works.", 1),
      Case("Webhook deliveries are delayed by up to six hours for all customers; downstream systems show stale data.", 2),
      Case("Every login takes 25-40 seconds since the auth upgrade, but eventually succeeds.", 2),
      Case("All file uploads in the EU region have failed since 08:00; uploads are the primary workflow for that region.", 3),
      Case("Card payments are rejected for every customer since the payment gateway's certificate expired.", 3),
      Case("A migration dropped the production orders table; the latest backup is 26 hours old.", 4),
      Case("All APIs and the web app return connection refused in every region since 14:02.", 4),
      Case("Dark-mode contrast on the settings pane makes labels hard to read; toggling back to light mode fixes it.", 1),
      Case("The public API has rejected essentially all requests with 401 since 06:30; the docs portal still works.", 3),
      Case("The weekly digest email sometimes lands in spam since the domain change; whitelisting it works for users.", 1),
      Case("New-user onboarding emails arrive but every link is broken; resending them doesn't fix it.", 3),
      Case("The changelog page has been 404 since the docs reorg last month.", 0),
    ],
  )


def review_sentiment_v2() -> Task:
  return Task(
    id="review_sentiment_v2",
    type="score",
    question=review_sentiment().question,
    cases=[
      Case("Absolutely love spending $400 to hand-sand every joint myself. Flawless craftsmanship. Would be hilarious if it weren't my kitchen.", 0),
      Case("Broke after eleven days and support never replied. Zero stars.", 0),
      Case("I don't understand the hype. It's an expensive paperweight.", 0),
      Case("I wanted to love it — the design is brilliant — but three replacements in two months means I'm done.", 1),
      Case("Meh. It works, barely. You get what you pay for, I guess.", 1),
      Case("Solid build, but setup was confusing and the app crashed repeatedly until the latest update.", 2),
      Case("The service was wonderful; the product itself is pretty average.", 2),
      Case("Mixed bag: the camera is great, but the battery life is terrible.", 2),
      Case("Good value after two months of daily use; a few gripes with the strap, but nothing deal-breaking.", 3),
      Case("Reliable and does everything promised; the companion app could be better.", 3),
      Case("So good I bought a second one for my sister. Fast shipping too.", 4),
      Case("Two years of daily use and it still runs like new. Zero regrets.", 4),
      Case("Cheap tablets exist; this one proves they should cost less. Screen is dim, updates already stopped.", 1),
      Case("Camera is best-in-class, everything else is just fine. It's fine.", 2),
      Case("Bought this for my daughter on a whim and she hasn't put it down in three weeks. Wonderful.", 4),
      Case("Save your money. The strap frayed in a week, the screen arrived scratched, and the app logged me out mid-workout.", 0),
      Case("Good starter kit for the price; pros will outgrow it, but I can't fault it at this tier.", 3),
    ],
  )


def expense_category() -> Task:
  return Task(
    id="expense_category",
    type="choice",
    question=Choice(
      instructions="Which expense category does this business expense belong to?",
      criteria={
        "meals": "Food or drink for the employee or their own team while working or traveling",
        "travel": "Transportation (flights, trains, taxis, rideshare), lodging, and related travel fees",
        "office_supplies": "Physical items and equipment for offices or home offices",
        "software": "Digital tools: licenses, subscriptions, SaaS, and app purchases",
        "client_entertainment": "Food, events, tickets, or gifts provided to clients, prospects, or job candidates",
      },
    ),
    cases=[
      Case("Taxi from O'Hare to the client's downtown Chicago office, $42 plus tip.", "travel"),
      Case("Dinner at Ruth's Chris with the Acme procurement team to celebrate the renewal, $310.", "client_entertainment"),
      Case("Adobe Creative Cloud annual renewal for the design pod, $599.", "software"),
      Case("Two standing desks and monitor arms for the new hires' home offices, $780.", "office_supplies"),
      Case("Airbnb for a three-night conference stay, $410 total.", "travel"),
      Case("Round-trip economy flights to Berlin for the trade show, plus the train to Amsterdam afterwards, $890.", "travel"),
      Case("Notion Team workspace renewal, $540 for the year.", "software"),
      Case("Coffee and pastries, $38, laid on for the candidate's morning of on-site interviews.", "client_entertainment"),
      Case("Team lunch for four during the offsite, $86.", "meals"),
      Case("Two tickets to the playoff game for the Acme renewal team, $650.", "client_entertainment"),
      Case('MacBook Pro 14" for the new designer, $2,399.', "office_supplies"),
      Case("Drive-thru lunch both days at the conference, $22 total.", "meals"),
      Case("Quarterly LinkedIn Learning licenses for the finance team — $240.", "software"),
      Case("Toll charges plus parking while driving my own car to the client site in Oslo, 320 kr.", "travel"),
      Case("Flowers sent to the client's office congratulating them on their funding round.", "client_entertainment"),
      Case("Monthly Zoom Business plan for the remote team, $199.", "software"),
      Case("Replacement headphones for an engineer who lost theirs on a business trip, $120.", "office_supplies"),
    ],
  )


def oncall_route() -> Task:
  return Task(
    id="oncall_route",
    type="choice",
    question=Choice(
      instructions="Which on-call team should this production issue be routed to?",
      criteria={
        "payments": "Card processing, billing pipelines, invoicing logic, and payment gateway integrations",
        "web": "The user-facing site and app: page rendering, client-side behavior, and browser errors",
        "infra": "Cloud, compute, deployments, networking, and third-party provider outages",
        "data": "ETL pipelines, data freshness, warehouse jobs, and analytics/reporting correctness",
        "model": "The ML models: prediction quality, training jobs, and model outputs",
      },
    ),
    cases=[
      Case("Alert: checkout-service error rate is 12% (baseline 0.1%); the stack trace is full of Stripe timeout exceptions.", "payments"),
      Case("Users on iOS 17 report the confirmation dialog renders blank; the API returns 200 with valid JSON.", "web"),
      Case("Deploy froze mid-rollout at 50% of pods; the rest are in CrashLoopBackOff after the helm upgrade timed out.", "infra"),
      Case("The nightly orders-to-warehouse ETL is 14 hours behind; storefronts are showing yesterday's stock counts.", "data"),
      Case("API pods sit at 100% CPU since the v172 release and the autoscaler has maxed out at 30 replicas.", "infra"),
      Case("Fraud model false-positive rate doubled since Monday's retrain; 200 legitimate orders were blocked overnight.", "model"),
      Case("A rep asks why their customer's inventory dashboard is empty; the store-import job exited 1 at 03:12 with no rows loaded.", "data"),
      Case("Users report the site won't load; the status page shows a regional S3 outage and the CDN can't fetch bundles.", "infra"),
      Case("Cart totals are off by one cent on multi-item carts when store credit and proration are combined.", "payments"),
      Case("The settings page intermittently shows NaN instead of weights across all browsers; the console shows a TypeError in bundle 2.3.1.", "web"),
      Case("Invoice PDFs are generating with line items in the wrong order; totals are correct.", "payments"),
      Case("The cookie-consent banner blocks the nav buttons on mobile in landscape.", "web"),
      Case("The nightly forecast-training job ran out of memory and hasn't produced a model since Wednesday.", "model"),
      Case("The revenue dashboard shows blank for EMEA since this morning's dbt run.", "data"),
      Case("Users on Android 15 see a white screen on launch; iOS is fine.", "web"),
    ],
  )


def churn_risk() -> Task:
  return Task(
    id="churn_risk",
    type="score",
    question=Score(
      instructions="How likely is this customer to cancel their subscription soon, based on this message?",
      criteria=[
        "Committed: renewed, upgraded, or is actively expanding usage",
        "Content: satisfied overall, at most minor friction and no signals of leaving",
        "Concerned: recurring unresolved problems or clear disappointment; satisfaction is dropping",
        "Evaluating: comparing alternatives, asking about contract end terms, or setting conditions to stay",
        "Leaving: explicit cancellation or non-renewal notice",
      ],
    ),
    cases=[
      Case("We just upgraded to the annual Scale plan and the whole team is on board — loving the new dashboards.", 0),
      Case("Usage is up 40% since the redesign. Can we add 20 more seats while we're at it?", 0),
      Case("The QBR went well. A few wishlist items — more export formats — but overall we're happy.", 1),
      Case("Onboarding was rocky, but support recovered well and we're cautiously optimistic.", 1),
      Case("This is the third month in a row our totals don't reconcile. We can't run payroll forecasts like this.", 2),
      Case("The tool works, but the team keeps reverting to spreadsheets, so we're using it less and less. Not sure it's earning its spot.", 2),
      Case("Could you send us the notice-period terms in our contract? We'd also like to know what a full data export includes.", 3),
      Case("Unless usage-based pricing ships this year, we'll have to look elsewhere once we scale past the current tier.", 3),
      Case("Effective at the end of the current billing period, please cancel our subscription and confirm in writing.", 4),
      Case("Please close our account — the migration to Acme finished last week.", 4),
      Case("As of today we're giving our 30-day notice under section 8.2; we're done.", 4),
      Case("Honestly it's fine, but for what we pay I expected the reporting to be further along by now.", 2),
      Case("Between us, our new platform owner is benchmarking tooling across the board, so expect questions.", 3),
      Case("Occasional hiccups with search, sure, but our workflows run end-to-end and the value is clear.", 1),
      Case("Our CSM left six weeks ago and nobody has reached out since, so we're a bit lost.", 2),
      Case("Renewal confirmed on our side — please send the updated MSA for signature.", 0),
    ],
  )


def lead_qualification() -> Task:
  return Task(
    id="lead_qualification",
    type="score",
    question=Score(
      instructions="How qualified is this inbound lead for the enterprise sales team?",
      criteria=[
        "Unqualified: no budget or realistic commercial use case — a student, a hobby project, a job seeker, or a vendor pitch",
        "Low: exploratory, small-team, no timeline, or unclear needs",
        "Medium: a real team problem with likely budget and a decision within the next quarter or so",
        "High: clear budget and authority, an active purchase process, and an enterprise-scale need",
      ],
    ),
    cases=[
      Case("Hi! I'm a CS student building a climate dashboard for my thesis. Do you offer an education discount?", 0),
      Case("Hi, I sell lead-gen tooling — I think we could partner; here's my deck.", 0),
      Case("Fun tool! Using the free tier to schedule my D&D group's sessions. Works great so far.", 0),
      Case("We're a four-person studio and the free tier covers us for now. Does the Pro plan add Zapier support? Just checking.", 1),
      Case("Do you have an API? I might want to build an integration at some point, not sure what yet.", 1),
      Case("I'm evaluating dashboard tools for our 40-person support team. Small budget to start; I'd want to pilot with five users next month.", 2),
      Case("I run a 12-person agency and we waste about 10 hours a week on client reporting by hand; want to fix that before three new clients start next month.", 2),
      Case("We need governed BI for our January audit. I'm building the shortlist now, but the purchase won't happen before October.", 2),
      Case("Our CTO asked me to evaluate vendors to replace our homegrown forecasting stack — 300 engineers on the platform, budget approved, decision by end of next quarter.", 3),
      Case("VP Ops at a 900-store retailer here. The WMS contract expires in five weeks and the board approved a $2M migration budget. Can we start a POC this week?", 3),
      Case("Evaluating vendors for our 60-person sales team; procurement needs the final three by end of May.", 2),
      Case("Saw the demo at a booth — cool stuff. Bookmarking it for a future project.", 1),
      Case("Our platform decision is locked to your competitor until 2028, but we're fans of the product.", 0),
      Case("The CFO approved a three-year contract budget and our security review closes this week.", 3),
    ],
  )


def content_moderation() -> Task:
  return Task(
    id="content_moderation",
    type="choice",
    question=Choice(
      instructions="Which moderation category does this user post fall under?",
      criteria={
        "harassment": "Insults, abuse, or hostile attacks on a person or group",
        "threat": "Stated intent to harm a specific person, doxxing, or incitement of violence",
        "self_harm": "Expressing intent or desire to hurt oneself, or encouraging others to do so",
        "spam": "Unsolicited promotion, chain messages, or repeated irrelevant content, often with links",
        "none": "Legitimate content that violates no rules",
      },
    ),
    cases=[
      Case("You're pathetic. Nobody in this community wants you here. Log off and stay off.", "harassment"),
      Case("🔥🔥 GAIN 5000 FOLLOWERS OVERNIGHT!! Click now before it's gone bit.ly/f4stf0ll0w", "spam"),
      Case("I don't think anyone would notice if I was gone. Tired of pretending everything's fine.", "self_harm"),
      Case("Does anyone know why my posts keep getting flagged? I just shared my parkrun time.", "none"),
      Case("Post his home address again and he'll never type another word online. We know which school his kids go to.", "threat"),
      Case("People who main Mercy are why ranked will never be competitive. Bottom-tier humans.", "harassment"),
      Case("Congrats on the launch! We help startups like yours 10x their pipeline — want a free growth audit? I'll DM you the details.", "spam"),
      Case("Day 60 self-harm free today. If you're struggling, my DMs are open.", "none"),
      Case("First snow of the season! Get the wax out, skiers ⛷️", "none"),
      Case("Send this to 10 friends for good luck or Bill Gates will stop sending you money!!1", "spam"),
      Case("Imagine spending real money to look this bad at the game. Some people's parents really never said no.", "harassment"),
      Case("Tell your marketing girl to watch herself walking to her car.", "threat"),
      Case("Join my VIP signals group — 92% win rate 🚀 t.me/whalesclub", "spam"),
      Case("To the mod who removed my thread last week — my bad for missing the pinned rules post.", "none"),
      Case("Your guide got me through a rough patch — thank you.", "none"),
      Case("How much do mods pay you to keep quiet about the bans? Rats.", "harassment"),
    ],
  )


def code_review_intent() -> Task:
  return Task(
    id="code_review_intent",
    type="choice",
    question=Choice(
      instructions="What is the primary concern of this code review comment?",
      criteria={
        "bug": "Points out incorrect behavior or a defect that will produce wrong results",
        "performance": "Inefficiency: unnecessary work, N+1 queries, or hot-path waste",
        "security": "A vulnerability: injection, missing authorization, or sensitive data exposure",
        "style": "Idioms and conventions: naming, formatting, and language best practices on correct code",
        "refactor": "Structural reorganization of correct code: extracting, splitting, or moving pieces for clarity",
        "nit": "Trivial preference or typo; safe for the author to ignore",
      },
    ),
    cases=[
      Case("Ingesting from the mobile SDK will raise KeyError here — that client omits `group`. Handle the missing key.", "bug"),
      Case("Hoist the json.dumps(config) call out of the loop; you re-serialize the same config on every request.", "performance"),
      Case("Concatenating user_id into this SQL string is a textbook injection point the moment the value isn't validated; use a bound parameter.", "security"),
      Case("`if len(rows) > 0` reads better as `if rows`.", "style"),
      Case("Typo in the variable name: `recieve_metrics` should be `receive_metrics`.", "nit"),
      Case("This 300-line endpoint does authorization, logging, and email. Please split it; as is, none of it is testable.", "refactor"),
      Case("The timezone is parsed once at login. If the user travels, notifications fire at the original zone's local times — subtle but real.", "bug"),
      Case("A bare `except Exception: pass` here swallows disk-full errors, and the retry loop then spins forever on a wedged write. Catch narrowly.", "bug"),
      Case("Each `.author.name` in the template triggers its own query — one page view makes 200 queries.", "performance"),
      Case("This endpoint takes user_id straight from the request; any authenticated user can list other users' invoices by changing the URL.", "security"),
      Case("Use pathlib here instead of the os.path string munging; the codebase is mid-migration and this file predates the convention.", "style"),
      Case("I would have named this `job_display`, but I don't feel strongly — dealer's choice.", "nit"),
      Case("This module uses `Optional[str]` everywhere; let's not start mixing in bare `str | None`.", "style"),
      Case("The exception message is rendered back to the client and includes the stack trace with the DB host. Redact it.", "security"),
      Case("This retry loop has no backoff and will hammer the downstream service on partial failures.", "bug"),
      Case("Can we drop the `# TODO: remove after migration` now that the migration shipped?", "nit"),
    ],
  )


def commit_intent() -> Task:
  return Task(
    id="commit_intent",
    type="choice",
    question=Choice(
      instructions="What is the primary purpose of this commit message?",
      criteria={
        "feature": "Adds new functionality or a new endpoint",
        "fix": "Corrects broken or incorrect behavior",
        "refactor": "Restructures existing code without changing behavior",
        "docs": "Documentation: README, runbooks, and explanatory notes",
        "test": "Adds or repairs tests",
        "chore": "Tooling, dependencies, CI, and other housekeeping",
      },
    ),
    cases=[
      Case("Add retry with exponential backoff to the webhook dispatcher", "feature"),
      Case("Correct exchange-rate rounding for zero-decimal currencies like JPY", "fix"),
      Case("Extract shared payload validation into its own module", "refactor"),
      Case("Note in CONTRIBUTING that integration tests skip when NO_DB=1", "docs"),
      Case("Bump flask to 3.0.3 and refresh the lockfile", "chore"),
      Case("Cover the midnight boundary in the attendance rollover tests", "test"),
      Case("Prevent silent data loss when the upload connection drops mid-stream", "fix"),
      Case("Add a per-tenant usage export endpoint", "feature"),
      Case("Set up a GitHub Action to lint PR titles", "chore"),
      Case("Delete the legacy canary flag and its dead code paths", "refactor"),
      Case("Add the circles layout behind a feature flag", "feature"),
      Case("Fix the flaky timezone test by freezing the clock in setUp", "test"),
      Case("Update README with the CUDA install path", "docs"),
      Case("Migrate the build to pyproject and consolidate the mypy config", "chore"),
      Case("Retry idempotent S3 uploads on 5xx", "fix"),
      Case("Add PyPy to the nightly CI matrix", "chore"),
    ],
  )


def recipe_cuisine() -> Task:
  return Task(
    id="recipe_cuisine",
    type="choice",
    question=Choice(
      instructions="Which cuisine is this dish or ingredient list closest to?",
      criteria={
        "italian": "Pasta, risotto, olive oil, parmigiano, balsamic, basil; the food of Italy",
        "french": "Butter, cream, wine reductions, stocks, herbes de Provence, souffles, and bistro classics",
        "mexican": "Corn tortillas, chilies, cilantro, lime, cumin, queso, and salsas",
        "indian": "Garam masala, turmeric, cumin seed, ginger, garlic, ghee, cream or yogurt, basmati rice, and Southern dosa/idli traditions",
        "thai": "Lemongrass, galangal, makrut lime leaves, fish sauce, Thai basil, chilies, and jasmine rice",
        "middle_eastern": "Tahini, sumac, za'atar, flatbread, lamb, pickled vegetables, and shawarma-style preparation",
      },
    ),
    cases=[
      Case("Fresh pasta sheets layered with slow-braised ragù, béchamel, and parmigiano-reggiano, baked until golden.", "italian"),
      Case("Veal shank braised in white wine, served over saffron risotto.", "italian"),
      Case("Corn tortillas filled with slow-roasted pork carnitas, topped with diced onion, cilantro, lime, and salsa verde.", "mexican"),
      Case("Roasted sweet potato and black bean tacos with chipotle crema, cotija, and pickled red onion.", "mexican"),
      Case("Chicken simmered in a sauce of garam masala, turmeric, cumin, garlic, and ginger, finished with cream and served over basmati rice.", "indian"),
      Case("Crisp fermented rice crepe wrapped around spiced potato masala, served with sambar and coconut chutney.", "indian"),
      Case("Green curry paste with Thai basil, fish sauce, coconut milk, makrut lime leaves, and eggplant, with jasmine rice on the side.", "thai"),
      Case("Glass noodle salad with lemongrass, bird's eye chilies, lime, mint, fish sauce, and crushed peanuts (yum woon sen).", "thai"),
      Case("Chicken braised in Burgundy wine with lardons, pearl onions, and cremini mushrooms.", "french"),
      Case("Ratatouille of eggplant, zucchini, and tomato confit seasoned with herbes de Provence.", "french"),
      Case("Chicken shawarma wrap with garlic toum, pickled turnips, and sumac onions.", "middle_eastern"),
      Case("Sheet-pan chicken rubbed with za'atar and allspice, served with flatbread and a garlic-tahini sauce.", "middle_eastern"),
      Case("Sweet crêpes with a warm compote of apple and Calvados.", "french"),
      Case("Grape leaves stuffed with rice, pine nuts, and currants, served with lemon wedges.", "middle_eastern"),
      Case("Silky custard with a caramelized sugar crust, served with shortbread.", "french"),
      Case("Lentil soup with turmeric, ghee, garlic, and cumin, served with naan.", "indian"),
    ],
  )


def question_duplicate() -> Task:
  return Task(
    id="question_duplicate",
    type="noul",
    question=Noul(
      instructions="The two questions listed in the state are duplicates asking the same thing",
    ),
    cases=[
      Case("Q1: How do I reset my password?\nQ2: What's the procedure for resetting my login password?", True),
      Case("Q1: How do I reset my password?\nQ2: How do I reset my password without access to my email?", False),
      Case("Q1: Why does my battery drain so fast after the update?\nQ2: Ever since installing the new version my phone loses charge really quickly — what gives?", True),
      Case("Q1: Why does my battery drain so fast?\nQ2: How do I replace my battery?", False),
      Case("Q1: Can I get a refund for a digital purchase?\nQ2: Is it possible to obtain a reimbursement for a downloaded game?", True),
      Case("Q1: What's the best laptop for college?\nQ2: What's the best college for a CS degree?", False),
      Case("Q1: My Wi-Fi disconnects every few minutes — how do I fix it?\nQ2: Wi-Fi keeps dropping every few minutes. Any fix?", True),
      Case("Q1: Does creatine cause hair loss?\nQ2: Does creatine help muscle growth?", False),
      Case("Q1: How long does shipping take to Canada?\nQ2: What are the delivery times to Canadian addresses?", True),
      Case("Q1: How long does shipping take to Canada?\nQ2: How much does shipping to Canada cost?", False),
      Case("Q1: My kid deleted our user accounts — is anything recoverable?\nQ2: Accidentally removed all the accounts from the family plan; is there an undo?", True),
      Case("Q1: How much caffeine is in a shot of espresso?\nQ2: How many shots of espresso a day is too much?", False),
      Case("Q1: Why is my SSD so much slower than advertised?\nQ2: My SSD is way slower than what was promised on the box — why?", True),
      Case("Q1: How do I connect the printer to Wi-Fi?\nQ2: Can the printer work without Wi-Fi?", False),
    ],
  )


def sql_injection_risk() -> Task:
  return Task(
    id="sql_injection_risk",
    type="noul",
    question=Noul(
      instructions="The query construction in this code is vulnerable to SQL injection",
    ),
    cases=[
      Case('db.execute("SELECT * FROM users WHERE email = \'" + email + "\'")', True),
      Case('db.execute("SELECT * FROM users WHERE email = %s", (email,))', False),
      Case('query = f"DELETE FROM sessions WHERE token = {request.args.get(\'token\')}"', True),
      Case('sql = "SELECT * FROM users WHERE email = " + quote_literal(email)', False),
      Case("sort_col = request.form['sort']\ncursor.execute(f\"SELECT name FROM products ORDER BY {sort_col}\")", True),
      Case('cursor.execute("SELECT name FROM products ORDER BY created_at")', False),
      Case("stmt = \"UPDATE users SET name = '%s' WHERE id = %d\" % (name, user_id)\ncursor.execute(stmt)", True),
      Case('stmt = sqlalchemy.text("SELECT * FROM users WHERE name = :name").bindparams(name=name)', False),
      Case('db.exec_script("INSERT INTO logs VALUES (\'" + user_input + "\')")', True),
      Case("if not user_id.isdigit(): abort(400)\ncursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")", False),
      Case("cursor.execute(\"SELECT * FROM logs LIMIT \" + request.query['n'])", True),
      Case("col = ALLOWED_SORT_COLS.get(request.form['sort'], 'created_at')\ncursor.execute(f\"SELECT name FROM products ORDER BY {col}\")", False),
      Case("stmt = \"SELECT * FROM %s WHERE id = :id\" % table\ncursor.execute(stmt, {'id': 42})", True),
      Case("result = session.query(User).filter_by(email=email).first()", False),
    ],
  )


def travel_policy_violation() -> Task:
  return Task(
    id="travel_policy_violation",
    type="noul",
    question=Noul(
      instructions="The expense submission violates the company travel policy: hotels over $200/night, business class on flights under 8 hours, meals over $60/day, alcohol, premium rideshare tiers, rideshares where transit was available, and home-to-office commuting are not covered",
    ),
    cases=[
      Case("Hampton Inn Chicago, two nights at $185/night for the client onsite.", False),
      Case("Hotel Theo, three nights at $209/night — it was the cheapest available during the conference.", True),
      Case("Bar tab at the hotel lounge: two cocktails, $45, during the client dinner week.", True),
      Case("Business class ORD to LHR (7h55m); it was only $400 more than economy.", True),
      Case("United economy SFO to JFK (5h50m), $310.", False),
      Case("Lyft from hotel to client office daily at $18/day for three days; no transit options within two miles of the client site.", False),
      Case("Uber Black from the airport, $95 — it was pouring rain.", True),
      Case("Day 1 receipts: breakfast $14, lunch $19, dinner $22 — total $55.", False),
      Case("Fuel for driving my own car to HQ Monday through Friday last week, $40.", True),
      Case("Delta economy ATL to MCO, $210 for the partner summit.", False),
      Case("Courtyard by Marriott Austin, two nights at $178/night for training week.", False),
      Case("Grand Hyatt client week: $200/night exactly for two nights.", False),
      Case("Business class, SIN to YYZ (17h55m), $4,800.", False),
      Case("Premium airport limo, $140 one-way.", True),
      Case("Room-service breakfast, $24; total food spend for the day was $58.", False),
      Case("First-class train ticket, $85 — no other class was available that day.", False),
    ],
  )


def contains_pii() -> Task:
  return Task(
    id="contains_pii",
    type="noul",
    question=Noul(
      instructions="The text contains personally identifiable information: an email address, phone number, home or postal address, government ID or Social Security number, date of birth, or bank and card account numbers",
    ),
    cases=[
      Case("My SSN is 531-24-8897; the refund form keeps rejecting it.", True),
      Case("You can reach me at 512-555-0142 after 5pm.", True),
      Case("My email is peggyDOTmueller AT exampleDOTcom — the address on file bounces.", True),
      Case("I'm calling about my husband's account — it's under his name, not mine.", False),
      Case("The Maple Street branch told me to call the number on my statement.", False),
      Case("We'll be at my parents' place next week if you need to ship it: 388 Broderick St, Apt 4, San Francisco, CA 94117.", True),
      Case("Routing 021000021, account 000123456789 — please wire the refund to the same account.", True),
      Case("Invoice INV-2213 for $42.50 was paid on 3/14 by card.", False),
      Case("I'm Tarjei Hadley, born 7 March 1989, and I need to verify my identity for the upgrade.", True),
      Case("Just text me when it ships — you already have my number.", False),
      Case("Our company, Blue Harbor Logistics, has three offices in Ontario.", False),
      Case("Refund my card — you charged it twice, once on the 1st and once on the 2nd.", False),
      Case("Texting from my mom's phone since mine broke — call hers: (415) 555-2728.", True),
      Case("Published author Alex Chen joins our editorial board in March.", False),
      Case("My passport number is N1234567; the renewal form asks for it.", True),
      Case("The shipment went to our warehouse at 1200 Industrial Way.", False),
    ],
  )


def contains_spoiler() -> Task:
  return Task(
    id="contains_spoiler",
    type="noul",
    question=Noul(
      instructions="This post contains spoilers: details of plot twists, character deaths, endings, or major reveals for a film or show",
    ),
    cases=[
      Case("I can't believe the wife was the killer all along — those last 20 minutes wrecked me.", True),
      Case("Anyone else watching this weekend? Looking for a spoiler-free viewing party for the finale.", False),
      Case("The final shot, with the door left ajar, confirms he never actually escaped the loop.", True),
      Case("Saw it opening night. IMAX was the right call, and the cinematography deserves every award. Zero spoilers from me.", False),
      Case("Well, I did NOT see the mentor twist coming. My jaw is still on the floor.", True),
      Case("The movie takes about 30 minutes too long to get going, and yes, the pacing problems people mention are real.", False),
      Case("Also, when the dog dies at the bridge scene, everyone in my theater was sobbing.", True),
      Case("Just finished season two — the ensemble cast is fantastic, especially the lead.", False),
      Case("The ending is ambiguous, but the wedding-dress scene near the end makes it pretty clear she chose herself.", True),
      Case("Where can I watch this with subtitles? My local theater doesn't screen indies.", False),
      Case("Skip the after-credits scene? Absolutely not — that's where they resurrect Mira.", True),
      Case("Three episodes in and the season keeps getting better; the casting alone is worth it.", False),
      Case("Watched through the finale — genuinely peak television. That last frame had me screaming.", False),
      Case("Yes, Sam dies. I'm sorry, but you asked.", True),
    ],
  )


def formality_level() -> Task:
  return Task(
    id="formality_level",
    type="score",
    question=Score(
      instructions="How formal is the register of this message?",
      criteria=[
        "Formal: ceremonial, legal, or official written register",
        "Professional: standard business communication with greetings and sign-offs; contractions are fine",
        "Casual: friendly and colloquial, everyday phrasing, emoticons or light slang",
        "Intimate: heavy slang, abbreviations, and in-group shorthand; texts between close friends",
      ],
    ),
    cases=[
      Case("Pursuant to our discussion of 14 March, please find attached the amended agreement for your review and execution.", 0),
      Case("I am writing to express my profound dissatisfaction with the manner in which this matter has been handled, and to request a formal response within fourteen days.", 0),
      Case("Hi Dana — thanks for the quick turnaround on this. I've left a few comments in the doc; let me know if anything is unclear.", 1),
      Case("Hello, I'm following up on ticket 8823. Could you share an ETA for the fix? Thank you for your help.", 1),
      Case("Hey! Just bumping this in case it got buried — no rush :)", 2),
      Case("Hey folks, quick heads-up about tomorrow's demo — take a look at the deck when you get a sec, thanks!", 2),
      Case("Sure thing! I'll ping you once the build is done — should be quick.", 2),
      Case("lol ok that meeting could've been an email fr", 3),
      Case("omg you're the best!! 😭😭 ttyl", 3),
      Case("brb grabbing coffee, hmu if the pager goes off lol", 3),
      Case("It is with respect that I acknowledge receipt of your correspondence of Monday last.", 0),
      Case("hey!! can u merge that? need it out the door", 3),
      Case("Hereby notifying all parties of the amended terms, effective immediately.", 0),
      Case("Sick day 2mrw, barely survived", 3),
    ],
  )


def phishing_email() -> Task:
  return Task(
    id="phishing_email",
    type="noul",
    question=Noul(
      instructions="The message is a phishing or social-engineering attempt: impersonation of a bank, company, courier, or executive to steal credentials, card details, gift cards, or money via pressure and links",
    ),
    cases=[
      Case("Dear valued customer, your PayPal account has been limited. Verify your identity within 24 hours or it will be permanently suspended: paypa1-secure.example/verify", True),
      Case("I'm in back-to-back meetings — Andrew, quickly buy $500 in gift cards for the client welcome kits and text me the codes. Do not disturb my cell. —From: c.e.o.schmidt@acm3-mail.example", True),
      Case("Reminder from IT: mandatory password rotation happens Friday via the internal IdP portal at idp.acmecorp.example. We never ask for passwords by email.", False),
      Case("Your parcel could not be delivered. Pay the $1.20 redelivery fee to release it: courier-trackin.example", True),
      Case("Invoice INV-44821 from Riverside Consulting for March landscaping services, net 15. This is our regular monthly bill; PDF attached.", False),
      Case("Your Microsoft 365 password expires today. Sign in to keep your access: https://login.micros0ft.example", True),
      Case("Happy birthday from all of us on the management team, Priya! 🎂 (No reply needed.)", False),
      Case("ALERT: Your bank account is locked. Verify your card number and PIN now to restore access immediately.", True),
      Case("Your appointment is confirmed for Tuesday 10:30 at EyeCare Associates — reschedule via the same portal you booked with.", False),
      Case("IRS NOTICE: you are eligible for a refund of $1,742.03. File Form 8829 within 48 hours: irs-refunds.example", True),
      Case("Zoom: your meeting 'Q2 Sync' is starting now — join from the link in your calendar invite.", False),
      Case("Apple ID suspended due to suspicious activity; sign in at apple-id-recovery.example to reactivate.", True),
    ],
  )


def meeting_conflict() -> Task:
  return Task(
    id="meeting_conflict",
    type="noul",
    question=Noul(
      instructions="The proposed event overlaps in time with at least one existing calendar event",
    ),
    cases=[
      Case("Calendar: Standup 9:00-9:30; Dentist 10:00-11:00. Proposed: Client sync 10:30-11:15.", True),
      Case("Calendar: Team lunch 12:00-13:00. Proposed: Writing time 11:00-11:45.", False),
      Case("Calendar: Design review 14:00-15:00. Proposed: Wrap-up 14:45-15:15.", True),
      Case("Calendar: Focus block 15:00-16:00. Proposed: 1:1 with Priya 16:00-16:30.", False),
      Case("Calendar: All-hands 10:00-11:30. Proposed: Partner call 10:30-11:00.", True),
      Case("Calendar: Interview 09:00-10:00; Flight SFO to NYC 14:00-18:00. Proposed: Working session 10:15-11:30.", False),
      Case("Calendar: Onboarding session 15:00-16:00; Board prep 15:45-16:15. Proposed: 14:00-15:30.", True),
      Case("Calendar: Mentor 1:1 09:00-09:30. Proposed: Coffee chat 09:30-09:50.", False),
      Case("Calendar: Ops standup every Friday 10:00-10:15. Proposed: Friday roadmap review 10:00-11:00.", True),
      Case("Calendar: Deadline day blocked off Friday. Proposed: workshop Thursday 15:00-16:30.", False),
      Case("Calendar: Sprint retro 11:00-12:00. Proposed: lunch with client 12:00-13:00.", False),
      Case("Calendar: Vendor call 13:30-14:00; dentist 15:00-16:00. Proposed: team debrief 13:45-14:15.", True),
    ],
  )


def hazmat_shipping() -> Task:
  return Task(
    id="hazmat_shipping",
    type="noul",
    question=Noul(
      instructions="The shipment requires hazmat (dangerous goods) handling: anything containing lithium batteries, pressurized aerosol containers, flammable liquids (perfume, solvents, butane), or corrosive chemicals qualifies",
    ),
    cases=[
      Case("Order 88132: two power banks (10,000 mAh, lithium-ion) and a USB cable.", True),
      Case("Order 88133: one paperback novel, two pairs of cotton socks, one enamel mug.", False),
      Case("RMA return: tablet with a swollen built-in battery, screen intact.", True),
      Case("Order 88021: 24-pack of AA alkaline batteries and a headlamp body.", False),
      Case("Toolbox shipment: butane torch, solder wire, wrench set.", True),
      Case("Wardrobe box: coats, boots, and knitwear.", False),
      Case("Salon restock: one liter of acrylic nail monomer liquid and polish removers.", True),
      Case("Camping order: titanium spork, wool blanket, and a water filter.", False),
      Case("Auto parts: spray paint aerosol, brake-cleaner aerosol, mechanic's gloves.", True),
      Case("Kitchen set: a 750ml bottle of olive oil, a ceramic pan, and dish-soap concentrate.", False),
      Case("Order: electric skateboard with an integrated lithium pack and its charger.", True),
      Case("Kitchen order: cast-iron skillet, wooden spoon, cotton apron.", False),
    ],
  )


def dietary_vegan() -> Task:
  return Task(
    id="dietary_vegan",
    type="noul",
    question=Noul(
      instructions="The item is suitable for a vegan diet — that excludes meat, fish, dairy, eggs, honey, gelatin, and any other animal-derived ingredients",
    ),
    cases=[
      Case("House salad: mixed greens, cherry tomatoes, cucumber, citrus vinaigrette, pumpkin seeds.", True),
      Case("Margherita pizza: tomato sauce, fresh mozzarella, basil.", False),
      Case("Seitan riblets in BBQ sauce (tomato, molasses, smoked paprika).", True),
      Case("Gummy bears: glucose syrup, sugar, gelatin, fruit juice concentrates.", False),
      Case("Roasted almonds with a honey glaze.", False),
      Case("Classic hummus: chickpeas, tahini, lemon, garlic, olive oil.", True),
      Case("Veggie burger: grain blend, shredded vegetables, and an egg-white binder.", False),
      Case("Vegetable stock and coconut-milk curry over jasmine rice.", True),
      Case("Bread loaf: flour, water, salt, yeast, whey.", False),
      Case("Fruit sorbet: mango purée, sugar, and lime.", True),
      Case("Sushi roll: rice, nori, avocado, cucumber, and imitation crab.", False),
      Case("Protein smoothie: oat milk, banana, peanut butter, cocoa.", True),
    ],
  )


def news_topic() -> Task:
  return Task(
    id="news_topic",
    type="choice",
    question=Choice(
      instructions="Which desk should this news article be assigned to?",
      criteria={
        "politics": "Government, elections, legislation, diplomacy, and public policy",
        "business": "Companies, markets, deals, earnings, labor, and the economy",
        "technology": "Tech products, software, hardware, and technical research advances",
        "sports": "Competitions, leagues, athletes, and results",
        "culture": "Arts, media, entertainment, awards, and reviews",
      },
    ),
    cases=[
      Case("The Senate committee advanced the housing bill 15-9, teeing up a floor vote before recess.", "politics"),
      Case("Q3 earnings: operating margin widened 120bp and the company lifted full-year guidance.", "business"),
      Case("A stoppage-time header sealed a 2-1 semifinal win, sending the club to its first final in a decade.", "sports"),
      Case("The film's Venice premiere earned a six-minute standing ovation ahead of its festival run.", "culture"),
      Case("The chipmaker previewed a 3nm process node, claiming 15% lower power draw at peak loads.", "technology"),
      Case("Brussels opened second-stage infringement proceedings over the new media law.", "politics"),
      Case("Apple's CFO warned of softer iPhone margins next quarter on rising memory costs; shares swung 3% after hours.", "business"),
      Case("A decrypted cache revealed an early draft of the composer's unfinished tenth symphony, now slated for a gala performance.", "culture"),
      Case("The academy graduate signed a five-year extension worth a reported $40m, ending months of transfer chatter.", "sports"),
      Case("A cryptography team published an audit of three post-quantum signature schemes, flagging one for residual-class weaknesses.", "technology"),
      Case("The central bank held rates at 4% but signalled a possible cut in the autumn; markets rallied.", "business"),
      Case("The opera house announced a new season featuring two world premieres and a revived classic.", "culture"),
    ],
  )


def app_review_intent() -> Task:
  return Task(
    id="app_review_intent",
    type="choice",
    question=Choice(
      instructions="What kind of app review is this?",
      criteria={
        "bug_report": "Describes something in the app that is broken or behaves wrongly",
        "feature_request": "Asks for new functionality, content, or settings",
        "praise": "Positive feedback about the app or the team",
        "pricing_billing": "Subscription, pricing, refund, or payment questions and complaints",
      },
    ),
    cases=[
      Case("Crashes every time I try to open a draft saved offline. Pixel 8, v3.2.1.", "bug_report"),
      Case("Any chance of a home-screen widget for the workout streak counter?", "feature_request"),
      Case("Absolutely worth the download — the offline mode saved a four-hour flight.", "praise"),
      Case("How do I get a refund for the annual plan? I meant to buy monthly.", "pricing_billing"),
      Case("Since the last update, the widget shows yesterday's totals until I force-quit it.", "bug_report"),
      Case("Please support split-screen on tablets; taking notes beside PDFs would complete this.", "feature_request"),
      Case("Charged twice after switching devices; sort it out before I dispute it with my card provider.", "pricing_billing"),
      Case("The devs actually listen — the flags I asked for in December are in. Remarkable pace.", "praise"),
      Case("Login with my managed Google account loops forever on my work profile; the personal account is fine.", "bug_report"),
      Case("The streak counter reset at midnight in the wrong timezone — I lost a 45-day streak because I was traveling.", "bug_report"),
      Case("I keep getting a 'sync failed' error on iOS when my vault has more than 100 notes.", "bug_report"),
      Case("Would love a way to share templates with my team without sending exports.", "feature_request"),
    ],
  )


def document_type() -> Task:
  return Task(
    id="document_type",
    type="choice",
    question=Choice(
      instructions="What kind of document is this text from?",
      criteria={
        "invoice": "A bill from a supplier listing amounts owed, dates, and payment instructions",
        "purchase_order": "A buyer-issued order for goods or services before fulfillment",
        "receipt": "Proof that a payment already happened",
        "contract": "Legal terms between parties: clauses, effective dates, signatures",
        "resume": "A job seeker's employment history, education, and skills",
      },
    ),
    cases=[
      Case("Invoice 04381 — net 30. Services: 24 hours of electrical work @ $85/hr. Total due: $2,040.", "invoice"),
      Case("Objective: staff software engineer. 2021-present: Senior Platform Engineer, Acme — led the migration; skills: Go, Terraform.", "resume"),
      Case("RECEIPT — Payment of $418.20 on Visa ending 7715 on 03/02, 341 Katahdin Dr Unit 2; balance $0.00.", "receipt"),
      Case("3. LIMITATION OF LIABILITY. Neither party's aggregate liability hereunder shall exceed the fees paid in the twelve months preceding the claim.", "contract"),
      Case("PO 991-2541 to EastGate Fabrication: 500 units of SKU EM-114 by 4/12; ship to Dock 4; payment net 45 upon delivery.", "purchase_order"),
      Case("Amount past due: $1,702.00. A 1.5% monthly late fee applies after 3/15. Remit to accounts@...", "invoice"),
      Case("Thank you for shopping with us — 2 items, $34.98 paid in cash, change given $5.02. REF 003118.", "receipt"),
      Case("The Licensee may not sub-license, assign, or transfer this Agreement without prior written consent. Signed: ____ (CTO, Licensee) ____ (COO, Licensor).", "contract"),
      Case("Certifications: PMP (2023), AWS SA (2021). Languages: Portuguese (native), English (fluent).", "resume"),
      Case("Order acknowledgment: we confirm your PO 4423 (40 hinges), ship date 5/01.", "purchase_order"),
      Case("TOTAL: $89.99, TAX $7.20, CASH TENDERED $100.00, CHANGE $2.81 — THANK YOU FOR SHOPPING AT GREENLEAF GROCERS.", "receipt"),
      Case("EXPERIENCE: Operations lead, 2018-2023 — managed a team of nine; BA Economics, 2016.", "resume"),
    ],
  )


def reading_level() -> Task:
  return Task(
    id="reading_level",
    type="score",
    question=Score(
      instructions="What reading level is this passage written at?",
      criteria=[
        "Simple: short sentences and everyday words; readable by children",
        "General: typical adult-level journalism, customer-facing or service prose",
        "Specialist: technical, legal, scientific, or professional jargon",
      ],
    ),
    cases=[
      Case("The cat sat by the window. She watched the birds hop in the grass. One flew away. Her tail went twitch, twitch.", 0),
      Case("Our store closes for renovations on March 15 and reopens April 1; click-and-collect orders shift to the Union St branch in the meantime.", 1),
      Case("Pursuant to Section 17(b)(iv), the indemnitor shall hold harmless the indemnitee against all consequential damages arising from third-party claims.", 2),
      Case("Data were winsorized at the 2.5th and 97.5th percentiles; inference used a cluster-robust variance estimator.", 2),
      Case("Think of a battery like a bathtub: charging fills it up, and your apps drain the water.", 0),
      Case("High winds grounded the overnight ferry; passengers were rebooked onto the crossing that left at dawn.", 1),
      Case("Session tags load lazily on first render; after login they're warm in cache.", 2),
      Case("Season tickets renew automatically in March unless you turn that option off in your account settings.", 1),
      Case("Take one pill with water at breakfast and one at bedtime until the bottle is empty.", 0),
      Case("Dogs wag their tails when they're happy. Cats purr. Fish blow bubbles.", 0),
      Case("The appellate court remanded the matter for reconsideration in light of intervening precedent.", 2),
    ],
  )


def insurance_claim_priority() -> Task:
  return Task(
    id="insurance_claim_priority",
    type="score",
    question=Score(
      instructions="How urgently should this insurance claim or inquiry be handled?",
      criteria=[
        "Routine: cosmetic, informational, or no pressure to act soon",
        "Standard: repair or reimbursement needed, but life or business is unaffected",
        "Priority: significant damage or financial disruption that should move fast",
        "Immediate: safety is at risk, damage is ongoing, or the situation is critical right now",
      ],
    ),
    cases=[
      Case("My car got tapped in a parking lot; the bumper has a quarter-inch paint scratch. No rush, just logging it.", 0),
      Case("My windshield crack is spreading — about a foot long but out of the sightline. Can we schedule glass repair this week?", 1),
      Case("The bathroom ceiling caved in after the upstairs leak; we can't use the room, but the burst pipe itself is shut off.", 2),
      Case("Water is pouring through the light fittings and the breaker won't stay on; the family is sitting in the car outside.", 3),
      Case("Does my policy cover rental cars? Curious for a trip next month — no claim yet.", 0),
      Case("Someone sideswiped my parked car overnight and left a note. Damaged mirror and a scrape along the door; the car is drivable.", 1),
      Case("The fire sprinklers soaked the storeroom — roughly $12k of stock is waterlogged, and the shop is closed until cleanup.", 2),
      Case("A tree came through the roof during the storm; rain is still coming in and the bedroom directly underneath is unsafe.", 3),
      Case("I spilled paint on the rug; the cleaning estimate is $180 and I'd like to know whether to file or just pay it.", 1),
      Case("The only working heater failed last night and it's January; our space heaters aren't keeping up with the cold.", 2),
      Case("Fender bender in the parking garage; minor scratch on both bumpers and we exchanged details.", 1),
      Case("The basement floods whenever it rains heavily and it did again tonight — water keeps seeping in.", 3),
    ],
  )


def symptom_triage() -> Task:
  return Task(
    id="symptom_triage",
    type="score",
    question=Score(
      instructions="How urgently does this patient need medical care, based on their message?",
      criteria=[
        "Emergency: needs immediate emergency response — call 911 or go to the ER now",
        "Same-day urgent care",
        "Appointment within a few days",
        "Self-care or routine follow-up",
      ],
    ),
    cases=[
      Case("Crushing chest pain spreading to my left arm and jaw, started 20 minutes ago, and I feel short of breath.", 0),
      Case("My 8-year-old has a fever of 39.5 and I can't wake her up properly.", 0),
      Case("Sudden headache, the worst of my life, hit me like a thunderclap ten minutes ago.", 0),
      Case("My blood glucose reading is 38 and I'm shaky and sweating.", 0),
      Case("My 2-year-old swallowed a button battery about an hour ago.", 0),
      Case("I cut my finger chopping vegetables; it hasn't stopped bleeding after 15 minutes of pressure.", 1),
      Case("Severe toothache since last night and my face is swelling on one side; painkillers aren't touching it.", 1),
      Case("An itchy rash on my arms has been spreading for two days; over-the-counter antihistamines barely help.", 2),
      Case("Eczema flaring on both arms, itchy for three days, and my usual cream has run out.", 2),
      Case("Constipated for a week, bloated and uncomfortable; fiber and water aren't doing anything.", 2),
      Case("Mild sore throat for two days, no fever.", 3),
      Case("Woke up with a stiff neck that hurts when I turn; otherwise I feel fine.", 3),
      Case("My prescription has run out; I need a refill of my usual dose.", 3),
      Case("Mild sunburn from the beach — skin is red and warm, no blisters.", 3),
    ],
  )


def delivery_exception() -> Task:
  return Task(
    id="delivery_exception",
    type="choice",
    question=Choice(
      instructions="What is the primary delivery exception described here?",
      criteria={
        "address_issue": "Address is incomplete, wrong, or nonexistent, or the recipient is unknown",
        "customs_hold": "Package held by customs; duties or missing paperwork are blocking release",
        "weather_delay": "Delays caused by storms, floods, or other weather events",
        "failed_attempt": "Delivery attempted but the recipient was unavailable",
        "damaged": "Package or contents damaged in transit",
      },
    ),
    cases=[
      Case("Courier arrived at 14:05; nobody home. Left a pickup card.", "failed_attempt"),
      Case("Address '221B Baker St, Flat 9' is invalid — the building has no Flat 9.", "address_issue"),
      Case("Package held at Frankfurt customs; commercial invoice is required.", "customs_hold"),
      Case("Regional hub closed due to an ice storm; all routes suspended until roads reopen.", "weather_delay"),
      Case("Arrived with the corner of the box crushed; contents shifted inside.", "damaged"),
      Case("Recipient's phone number is invalid and the house number is missing — needs re-routing.", "address_issue"),
      Case("Duties of €34 unpaid; package is in the bonded warehouse awaiting payment.", "customs_hold"),
      Case("Delivery vans delayed six hours; the airport closed during the hurricane.", "weather_delay"),
      Case("The box was soaked and crushed after handling at the hub; the recipient refused it.", "damaged"),
      Case("Third attempt failed; recipient not home, no safe drop authorized.", "failed_attempt"),
      Case("Parcel returned to origin — customs declaration was incomplete.", "customs_hold"),
      Case("Contents charred after a warehouse fire; shipment written off as a total loss.", "damaged"),
    ],
  )


def city_service_request() -> Task:
  return Task(
    id="city_service_request",
    type="choice",
    question=Choice(
      instructions="Which city department should handle this 311 request?",
      criteria={
        "sanitation": "Trash collection, recycling, street cleaning, dumped waste, and pest complaints",
        "roads": "Potholes, streetlights, sidewalks, road markings, and traffic hazards",
        "noise": "Loud music, construction outside permitted hours, and animal noise",
        "permits": "Building permits, construction approvals, signage, and business licensing",
        "utilities": "Water pressure or outages, gas smells, and power-line issues",
      },
    ),
    cases=[
      Case("Pothole on Maple Ave between 3rd and 4th, about a foot wide — cars are swerving around it.", "roads"),
      Case("My recycling bin wasn't picked up last Tuesday; it's still sitting at the curb.", "sanitation"),
      Case("The neighbor's dog barks from 2am to 6am, every night this week.", "noise"),
      Case("The house next door is building a deck in the backyard without a permit — where do I report it?", "permits"),
      Case("Water pressure dropped across the whole block this morning.", "utilities"),
      Case("Streetlight out at the corner of Elm & 5th; it's been dark there for weeks.", "roads"),
      Case("A mattress and a bed frame were dumped on the corner of Oak Lane and have been there for days.", "sanitation"),
      Case("Construction next door has been jackhammering at 6am on a Sunday.", "noise"),
      Case("There's a strong gas smell near the playground on Pine St.", "utilities"),
      Case("I want to add an awning over my storefront — what do I need?", "permits"),
      Case("An overturned garbage truck is blocking two lanes on Route 9.", "roads"),
      Case("Rats at the dumpster behind the bakery on 6th Street.", "sanitation"),
    ],
  )


def ad_policy_violation() -> Task:
  return Task(
    id="ad_policy_violation",
    type="noul",
    question=Noul(
      instructions="The ad violates advertising policy: it makes unsupported health claims, guarantees results, promotes tobacco, weapons, or drugs, or tells users to stop taking prescribed medication",
    ),
    cases=[
      Case("Our ceramic pan heats evenly and cleans in seconds — see the results of our 30-day test.", False),
      Case("Clinically proven to cure joint pain in 3 days. Doctors hate it.", True),
      Case("Free shipping on all orders this weekend.", False),
      Case("Lose 30 pounds in 30 days or your money back — guaranteed!", True),
      Case("Handmade leather journals from a small workshop in Florence.", False),
      Case("Vape starter kit — 50% off today, no ID checks needed.", True),
      Case("Rated 4.8 stars by 12,000 verified buyers.", False),
      Case("Our supplement treats diabetes — stop taking your prescription today.", True),
      Case("Air fryer: 5.5L capacity, dishwasher-safe basket.", False),
      Case("Bitcoin signals: guaranteed 10x returns, withdraw anytime.", True),
    ],
  )


def fair_housing_violation() -> Task:
  return Task(
    id="fair_housing_violation",
    type="noul",
    question=Noul(
      instructions="The rental or sale listing contains discriminatory language under fair housing rules: expressing preferences or restrictions based on race, religion, national origin, familial status, or disability",
    ),
    cases=[
      Case("Charming 2BR near the park with an updated kitchen and in-unit laundry.", False),
      Case("Perfect for a young professional couple — no kids.", True),
      Case("This street is known as a Christian enclave; serious buyers only.", True),
      Case("Family-friendly cul-de-sac with a large yard and good schools.", False),
      Case("First-floor unit with step-free entry and grab bars in the bathroom.", False),
      Case("Not suitable for immigrants — the neighbors speak English only.", True),
      Case("Single professionals only; no families.", True),
      Case("Sun-filled corner unit, a 20-minute commute to downtown.", False),
      Case("Ground-floor studio one block from the subway; pets OK.", False),
      Case("Historic brownstone with original moldings restored, private garden.", False),
      Case("Prefer that foreign students don't apply.", True),
    ],
  )


def contract_clause_type() -> Task:
  return Task(
    id="contract_clause_type",
    type="choice",
    question=Choice(
      instructions="What type of contract clause is this?",
      criteria={
        "limitation_of_liability": "Caps or excludes damages one party can claim",
        "confidentiality": "Obligations about keeping information secret",
        "termination": "How and when the agreement can be ended",
        "indemnification": "One party agrees to defend or compensate the other for specified claims",
        "force_majeure": "Delays or failures excused by events beyond the parties' control",
      },
    ),
    cases=[
      Case("Neither party shall be liable for indirect, incidental, or consequential damages.", "limitation_of_liability"),
      Case("The Receiving Party shall protect Confidential Information using reasonable care and not disclose it to third parties.", "confidentiality"),
      Case("Either party may terminate upon 30 days written notice; surviving provisions remain in effect.", "termination"),
      Case("Contractor shall indemnify and hold harmless Client against third-party claims arising from the Work.", "indemnification"),
      Case("Neither party is liable for delays caused by acts of God, war, strikes, or government action.", "force_majeure"),
      Case("Aggregate liability shall not exceed fees paid in the preceding twelve months.", "limitation_of_liability"),
      Case("All trade secrets, customer lists, and pricing disclosed hereunder remain confidential for five years.", "confidentiality"),
      Case("Termination for cause: material breach not cured within 15 days of written notice.", "termination"),
      Case("Each party shall defend the other against IP-infringement claims arising from the Deliverables.", "indemnification"),
      Case("Obligations are suspended during pandemics, embargoes, or utility failures beyond a party's control.", "force_majeure"),
      Case("The Employee shall return all proprietary documents upon separation, under continuing confidentiality.", "confidentiality"),
      Case("Client shall hold Provider harmless from claims arising out of Client's use of the Deliverables.", "indemnification"),
    ],
  )


def voice_assistant_intent() -> Task:
  return Task(
    id="voice_assistant_intent",
    type="choice",
    question=Choice(
      instructions="What does the user want from the voice assistant?",
      criteria={
        "device_control": "Turn lights or appliances on/off, set temperature, lock doors",
        "information_request": "Questions about weather, time, facts, or anything else",
        "reminder": "Reminders, timers, alarms, and calendar events",
        "music": "Play music, podcasts, or radio",
        "small_talk": "Greetings, jokes, chit-chat, and questions about the assistant itself",
      },
    ),
    cases=[
      Case("Turn off the living room lights.", "device_control"),
      Case("What's the weather tomorrow?", "information_request"),
      Case("Remind me to call the dentist at three.", "reminder"),
      Case("Play some jazz.", "music"),
      Case("Tell me a joke.", "small_talk"),
      Case("Set the thermostat to 21 degrees.", "device_control"),
      Case("Set a timer for ten minutes for the pasta.", "reminder"),
      Case("Who won the game last night?", "information_request"),
      Case("Play the next episode of my podcast.", "music"),
      Case("How are you today?", "small_talk"),
      Case("Lock the front door and arm the alarm.", "device_control"),
      Case("What time does the pharmacy close?", "information_request"),
    ],
  )


def grammar_issue() -> Task:
  return Task(
    id="grammar_issue",
    type="choice",
    question=Choice(
      instructions="What is the primary grammar issue in this sentence?",
      criteria={
        "spelling": "A misspelled word",
        "subject_verb_agreement": "The verb form doesn't match the subject",
        "word_choice": "The wrong word is used — homophones, malapropisms, or incorrect forms",
        "punctuation": "A missing or misplaced comma, apostrophe, or other mark",
        "none": "The sentence is grammatically fine as written",
      },
    ),
    cases=[
      Case("She don't like the new schedule.", "subject_verb_agreement"),
      Case("Their going to be late.", "word_choice"),
      Case("I recieve the report every Friday.", "spelling"),
      Case("He walk to work every day.", "subject_verb_agreement"),
      Case("Lets get lunch.", "punctuation"),
      Case("I could care less about the results.", "word_choice"),
      Case("The flowers smell wonderfully.", "word_choice"),
      Case("We've been friends since 2010.", "none"),
      Case("The report is due on Tuesday.", "none"),
      Case("We arrived, at noon.", "punctuation"),
      Case("The accomodation was excelent.", "spelling"),
      Case("The committee decided to postpone the meeting.", "none"),
    ],
  )


def action_item_assignment() -> Task:
  return Task(
    id="action_item_assignment",
    type="noul",
    question=Noul(
      instructions="This sentence from meeting notes assigns a concrete task with an owner or a deadline",
    ),
    cases=[
      Case("Ravi will send the updated deck to the client by Friday.", True),
      Case("We should maybe look into the latency issue at some point.", False),
      Case("Priya to take the minutes.", True),
      Case("Great discussion on the roadmap today.", False),
      Case("Deadline for the pilot moved to June 10.", False),
      Case("Sana will book the venue and catering by the end of the week.", True),
      Case("It would be nice to get an intern for the summer.", False),
      Case("Action: legal review of the MSA, owner Tom, due next Tuesday.", True),
      Case("Next meeting Thursday at 10.", False),
      Case("The budget needs another look before we commit.", False),
      Case("I'll draft the proposal tonight and circulate it tomorrow morning.", True),
      Case("Morale is up after the launch; nice work everyone.", False),
    ],
  )


def suspicious_transaction() -> Task:
  return Task(
    id="suspicious_transaction",
    type="noul",
    question=Noul(
      instructions="This transaction is suspicious under standard fraud rules: geography or velocity that doesn't fit the account holder, round-number amounts unusual for the account, or patterns consistent with account takeover",
    ),
    cases=[
      Case("Card used in Lagos at 03:12 for exactly $2,000; the cardholder lives in Oslo and was there yesterday at 14:00.", True),
      Case("Weekly grocery run: €64.20 at the usual supermarket, 11:40.", False),
      Case("Two transactions of exactly $500.00 five minutes apart, in a country the cardholder has never visited.", True),
      Case("Monthly rent payment of $1,850 to the same landlord account as the last 24 months.", False),
      Case("Card declined twice, then a $999.99 online purchase succeeded from a new device in a new country.", True),
      Case("Coffee for $4.10 on Monday at 08:05, a short walk from the cardholder's office.", False),
      Case("Payroll deposit of $3,120.44 from the employer, same date every month.", False),
      Case("Cash withdrawal of $4,900 — just under the reporting threshold — minutes after a password reset.", True),
      Case("Subscription renewal of $12.99 for a streaming service used weekly for two years.", False),
      Case("Gas-station purchase in Marseille minutes after the card was used in Rotterdam.", True),
    ],
  )


def return_reason() -> Task:
  return Task(
    id="return_reason",
    type="choice",
    question=Choice(
      instructions="What is the primary reason for this product return?",
      criteria={
        "damaged_in_transit": "The item arrived broken, crushed, or otherwise damaged from shipping",
        "wrong_item": "A different item, color, or size than what was ordered",
        "size_or_fit": "The right item was sent but it doesn't fit or suit the buyer",
        "changed_mind": "No problem with the item; the buyer no longer wants it",
        "late_delivery": "The item arrived too late to be useful",
      },
    ),
    cases=[
      Case("The mug arrived shattered; the box was crushed too.", "damaged_in_transit"),
      Case("I ordered the blue jacket but received a red one in the correct size.", "wrong_item"),
      Case("The shoes are half a size too small — I need a 42, not a 41.5.", "size_or_fit"),
      Case("I found the same product cheaper elsewhere, so I no longer need it.", "changed_mind"),
      Case("It was supposed to arrive two weeks ago for a birthday; there's no point now.", "late_delivery"),
      Case("The item itself is fine — I ordered two by accident.", "changed_mind"),
      Case("This is the second replacement unit with a cracked screen.", "damaged_in_transit"),
      Case("The shipment arrived a month late and was marked delivered; the event it was for is over.", "late_delivery"),
      Case("I ordered size M but the tag says L.", "wrong_item"),
      Case("It doesn't fit my couch — I measured wrong on my end.", "size_or_fit"),
      Case("Nothing wrong with it; I just don't like the color in person.", "changed_mind"),
      Case("The box was dry and intact, but the lamp inside was snapped.", "damaged_in_transit"),
    ],
  )


EXTENSION_TASK_FUNCTIONS = [
  support_department_v2,
  email_intent_v2,
  refund_eligible_v2,
  urgency_v2,
  secret_leak_v2,
  frustration_level_v2,
  incident_severity_v2,
  review_sentiment_v2,
]

NEW_SIMILAR_TASK_FUNCTIONS = [
  expense_category,
  oncall_route,
  churn_risk,
  lead_qualification,
  app_review_intent,
]

NEW_DISTANT_TASK_FUNCTIONS = [
  content_moderation,
  code_review_intent,
  commit_intent,
  recipe_cuisine,
  question_duplicate,
  sql_injection_risk,
  travel_policy_violation,
  contains_pii,
  contains_spoiler,
  formality_level,
  phishing_email,
  meeting_conflict,
  hazmat_shipping,
  dietary_vegan,
  news_topic,
  document_type,
  reading_level,
  insurance_claim_priority,
  symptom_triage,
  delivery_exception,
  city_service_request,
  ad_policy_violation,
  fair_housing_violation,
  contract_clause_type,
  voice_assistant_intent,
  grammar_issue,
  action_item_assignment,
  suspicious_transaction,
  return_reason,
]

ALL_TASK_FUNCTIONS = (
  EXTENSION_TASK_FUNCTIONS + NEW_SIMILAR_TASK_FUNCTIONS + NEW_DISTANT_TASK_FUNCTIONS
)

TASKS_V2: list[Task] = [fn() for fn in ALL_TASK_FUNCTIONS]

TASK_IDS_V2 = [t.id for t in TASKS_V2]

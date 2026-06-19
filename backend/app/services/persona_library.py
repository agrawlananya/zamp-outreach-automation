from app.llm.client import call_llm

# buyer_type follows Miller Heiman:
#   economic  — controls budget, final authority (C-suite, founders, board)
#   functional — evaluates fit, owns the workflow/team, recommends to economic buyer
#   manager   — day-to-day operator, most impacted by the pain, often the champion

PERSONAS: dict[str, dict] = {

    # ==============================================================
    # EXECUTIVE / FOUNDER / BOARD  (cross-functional economic buyers)
    # ==============================================================

    "ceo": {
        "name": "CEO",
        "buyer_type": "economic",
        "goals": ["Scale revenue without proportional headcount growth", "Improve operational efficiency", "Maintain board confidence in execution"],
        "pains": ["Operational costs scaling with revenue", "Key person dependency on manual processes", "Lack of visibility into ops performance across functions"],
        "kpis": ["Revenue per employee", "Operating leverage", "Headcount growth vs. revenue growth"],
        "messaging_angle": "Position Zamp as the AI employee platform that lets the company scale output across finance, ops, support, and more without proportional headcount growth.",
        "zamp_value_prop": "Zamp is the AI employee layer that replaces high-volume repetitive work across functions — finance, procurement, HR, support — end-to-end, so the team focuses on judgment and growth.",
    },
    "chief executive officer": {
        "name": "CEO",
        "buyer_type": "economic",
        "goals": ["Scale revenue without proportional headcount growth", "Improve operational efficiency", "Maintain board confidence"],
        "pains": ["Operational costs scaling with revenue", "Manual process fragility at scale", "Lack of cross-function ops visibility"],
        "kpis": ["Revenue per employee", "Operating leverage", "Headcount vs. revenue growth ratio"],
        "messaging_angle": "Position Zamp as the AI employee platform that decouples operational output from headcount growth.",
        "zamp_value_prop": "Zamp replaces high-volume repetitive work across functions end-to-end, so the team focuses on judgment and growth.",
    },
    "founder": {
        "name": "Founder / Co-Founder",
        "buyer_type": "economic",
        "goals": ["Do more with a lean team", "Move fast without breaking ops", "Avoid premature hiring for ops roles"],
        "pains": ["Every process is manual and founder-dependent", "Hiring ops headcount before the business justifies it", "Ops bottlenecks slowing growth"],
        "kpis": ["Output per person", "Burn rate vs. operational capacity", "Time founders spend on operational work vs. strategy"],
        "messaging_angle": "Position Zamp as the AI employee that lets a lean founding team punch above their weight on ops — finance, admin, support — without hiring before they're ready.",
        "zamp_value_prop": "Zamp handles the high-volume operational work that would otherwise require an ops hire — end-to-end, with full audit trails — so founders stay lean and move fast.",
    },
    "co-founder": {
        "name": "Founder / Co-Founder",
        "buyer_type": "economic",
        "goals": ["Do more with a lean team", "Move fast without breaking ops", "Avoid premature hiring for ops roles"],
        "pains": ["Every process is manual and founder-dependent", "Premature ops hiring", "Ops bottlenecks slowing growth"],
        "kpis": ["Output per person", "Burn rate vs. operational capacity", "Founder time on ops vs. strategy"],
        "messaging_angle": "Position Zamp as the AI employee that lets a lean founding team punch above their weight on ops without hiring before they're ready.",
        "zamp_value_prop": "Zamp handles high-volume operational work end-to-end, so founders stay lean and move fast.",
    },
    "president": {
        "name": "President",
        "buyer_type": "economic",
        "goals": ["Drive operational excellence", "Scale business functions efficiently", "Improve cross-functional execution"],
        "pains": ["Business functions scaling unevenly with growth", "Manual processes creating execution risk", "Operational costs outpacing revenue growth"],
        "kpis": ["Revenue per employee", "Cross-functional SLA adherence", "Operational cost as % of revenue"],
        "messaging_angle": "Position Zamp as the AI employee platform that drives operational excellence across functions without proportional headcount growth.",
        "zamp_value_prop": "Zamp runs high-volume operational workflows end-to-end across finance, ops, and support — giving the President execution confidence without scaling headcount proportionally.",
    },
    "founder's office": {
        "name": "Founder's Office / Chief of Staff",
        "buyer_type": "functional",
        "goals": ["Execute founder priorities fast", "Remove operational bottlenecks across teams", "Maintain visibility across functions"],
        "pains": ["Ops bottlenecks that escalate to the founder", "Manual status tracking across teams", "No single view of operational performance"],
        "kpis": ["Founder time freed from ops", "Cross-team initiative completion rate", "Operational visibility score"],
        "messaging_angle": "Position Zamp as the AI employee that handles repetitive cross-functional ops work and surfaces exceptions to the founder's office instead of letting them fester.",
        "zamp_value_prop": "Zamp runs operational workflows and surfaces exceptions end-to-end, so the founder's office focuses on strategic priorities, not operational firefighting.",
    },
    "chief of staff": {
        "name": "Founder's Office / Chief of Staff",
        "buyer_type": "functional",
        "goals": ["Execute founder/CEO priorities fast", "Remove operational bottlenecks", "Maintain cross-functional visibility"],
        "pains": ["Ops issues that shouldn't reach the C-suite", "Manual tracking of cross-team initiatives", "No unified ops performance view"],
        "kpis": ["CEO time freed from ops", "Initiative completion rate", "Cross-team SLA adherence"],
        "messaging_angle": "Position Zamp as the AI employee that runs cross-functional ops and escalates only true exceptions to the Chief of Staff.",
        "zamp_value_prop": "Zamp handles ops workflows end-to-end and surfaces exceptions, so the Chief of Staff focuses on high-leverage work, not operational coordination.",
    },
    "board member": {
        "name": "Board Member",
        "buyer_type": "economic",
        "goals": ["Portfolio companies scale efficiently", "Reduce burn without sacrificing output", "Improve governance and audit readiness"],
        "pains": ["Portfolio companies hiring ops headcount too early", "Manual processes creating audit and compliance risk", "Lack of financial control visibility"],
        "kpis": ["Revenue per employee across portfolio", "Burn multiple", "Audit readiness"],
        "messaging_angle": "Position Zamp as the AI employee platform that helps portfolio companies scale ops and finance without proportional headcount — with enterprise-grade compliance built in.",
        "zamp_value_prop": "Zamp gives portfolio companies enterprise-grade ops automation — finance, compliance, procurement — end-to-end, improving operating leverage and audit readiness without early ops hires.",
    },

    # ==============================================================
    # FINANCE & ACCOUNTING
    # ==============================================================

    # Economic
    "cfo": {
        "name": "CFO",
        "buyer_type": "economic",
        "goals": ["Maintain financial control", "Reduce audit risk", "Deliver clean board-level reporting"],
        "pains": ["Financial control gaps", "Audit risk", "Board-level reporting pressure"],
        "kpis": ["Cash visibility", "Close cycle time", "Cost per transaction"],
        "messaging_angle": "Position Zamp as the AI employee that runs finance ops end-to-end with SOC/SOX-grade audit trails and ~99% accuracy.",
        "zamp_value_prop": "Zamp gives CFOs verifiable, autonomous financial operations — close, AP, reconciliations — without adding headcount or audit risk.",
    },

    # Functional
    "controller": {
        "name": "Controller",
        "buyer_type": "functional",
        "goals": ["Speed up month-end close", "Reduce reconciliation errors", "Stay audit-ready year round"],
        "pains": ["Month-end close speed", "Reconciliation errors", "Manual audit prep burden"],
        "kpis": ["Days to close", "Error rate", "Manual hours per close"],
        "messaging_angle": "Position Zamp as the AI employee that owns reconciliation and close tasks end-to-end, escalating only true exceptions.",
        "zamp_value_prop": "Zamp runs reconciliation and close workflows autonomously, cutting manual hours and keeping Controllers audit-ready without the scramble.",
    },
    "vp finance": {
        "name": "VP Finance",
        "buyer_type": "functional",
        "goals": ["Scale finance operations without adding headcount", "Improve forecast reliability"],
        "pains": ["Manual processes that break at volume", "Headcount pressure as transaction volume grows"],
        "kpis": ["Cost of finance as % of revenue", "Headcount-to-transaction ratio"],
        "messaging_angle": "Position Zamp as the lever that absorbs transaction volume growth without proportional headcount growth.",
        "zamp_value_prop": "Zamp acts as an AI employee for high-volume finance work, letting VPs of Finance scale output without scaling the org.",
    },
    "head of accounting": {
        "name": "Head of Accounting",
        "buyer_type": "functional",
        "goals": ["Increase team capacity", "Eliminate error-prone manual processes"],
        "pains": ["Team capacity constraints", "Error-prone manual workflows"],
        "kpis": ["Headcount per $1M revenue", "Error rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles the repetitive, high-volume accounting work so the team focuses on exceptions.",
        "zamp_value_prop": "Zamp automates manual accounting workflows end-to-end, multiplying team capacity without new hires.",
    },
    "finance/ap ops lead": {
        "name": "Finance/AP Ops Lead",
        "buyer_type": "functional",
        "goals": ["Streamline vendor payments", "Remove approval bottlenecks", "Eliminate duplicate payments"],
        "pains": ["Vendor payment friction", "Approval bottlenecks", "Duplicate payments"],
        "kpis": ["AP cycle time", "Invoice exception rate"],
        "messaging_angle": "Position Zamp as the AI employee that runs AP end-to-end — processing, matching, escalating exceptions — without the manual queue.",
        "zamp_value_prop": "Zamp handles invoice processing and AP workflows autonomously, cutting cycle time and catching duplicates before they go out.",
    },

    # Managers
    "finance manager": {
        "name": "Finance Manager",
        "buyer_type": "manager",
        "goals": ["Hit reporting deadlines", "Reduce rework on manual data pulls", "Free up team time"],
        "pains": ["Manual data pulls and reconciliation", "Rework from errors", "Repetitive tasks blocking analytical work"],
        "kpis": ["Hours spent on manual tasks", "Reporting cycle time", "Error rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles the repetitive data and reconciliation work, so the finance team focuses on decisions.",
        "zamp_value_prop": "Zamp takes the repetitive grunt work off finance managers' plates — data pulls, reconciliation, report prep — running it autonomously end-to-end.",
    },
    "accounting manager": {
        "name": "Accounting Manager",
        "buyer_type": "manager",
        "goals": ["Close books faster", "Reduce manual journal entries", "Maintain clean audit trail"],
        "pains": ["Volume of manual journal entries", "Close crunch every month-end", "Audit evidence prep"],
        "kpis": ["Days to close", "Journal entry error rate", "Manual hours per close"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume accounting tasks so the manager focuses on exceptions and reviews.",
        "zamp_value_prop": "Zamp automates journal entries, reconciliations, and close prep end-to-end, reducing the month-end crunch without adding headcount.",
    },
    "ap manager": {
        "name": "AP Manager",
        "buyer_type": "manager",
        "goals": ["Process invoices faster", "Reduce exception rate", "Avoid duplicate payments"],
        "pains": ["Invoice processing backlog", "Manual matching errors", "Vendor escalations over late payments"],
        "kpis": ["Invoice processing time", "Duplicate payment rate", "Vendor payment SLA"],
        "messaging_angle": "Position Zamp as the AI employee that processes invoices end-to-end, flags exceptions, and pays vendors on time.",
        "zamp_value_prop": "Zamp handles invoice intake, matching, and payment processing autonomously — AP managers review exceptions, not every line item.",
    },
    "fp&a manager": {
        "name": "FP&A Manager",
        "buyer_type": "manager",
        "goals": ["Faster variance analysis", "Reliable forecast models", "Reduce time on data wrangling"],
        "pains": ["Manual data aggregation for forecasts", "Slow variance commentary", "Excel model fragility"],
        "kpis": ["Forecast accuracy", "Time on data prep vs. analysis", "Reporting cycle time"],
        "messaging_angle": "Position Zamp as the AI employee that handles data aggregation and prep so FP&A managers spend time on insight, not wrangling.",
        "zamp_value_prop": "Zamp automates the data collection and prep layer of FP&A workflows, cutting model refresh time and freeing analysts for actual analysis.",
    },

    # ==============================================================
    # PROCUREMENT
    # ==============================================================

    # Economic
    "cpo": {
        "name": "Chief Procurement Officer",
        "buyer_type": "economic",
        "goals": ["Reduce PO cycle time", "Enforce contract compliance", "Drive cost savings", "Eliminate maverick spend"],
        "pains": ["Manual PO processing at volume", "Vendor onboarding delays", "Maverick spend and compliance gaps"],
        "kpis": ["PO cycle time", "Contract compliance rate", "Cost savings %", "Supplier onboarding time"],
        "messaging_angle": "Position Zamp as the AI employee that runs procurement workflows end-to-end — PO creation, vendor onboarding, contract renewals — escalating only exceptions.",
        "zamp_value_prop": "Zamp handles high-volume procurement ops autonomously, cutting PO cycle time and enforcing compliance without growing the team.",
    },
    "chief procurement officer": {
        "name": "Chief Procurement Officer",
        "buyer_type": "economic",
        "goals": ["Reduce PO cycle time", "Enforce contract compliance", "Drive cost savings", "Eliminate maverick spend"],
        "pains": ["Manual PO processing at volume", "Vendor onboarding delays", "Maverick spend and compliance gaps"],
        "kpis": ["PO cycle time", "Contract compliance rate", "Cost savings %", "Supplier onboarding time"],
        "messaging_angle": "Position Zamp as the AI employee that runs procurement workflows end-to-end, escalating only exceptions.",
        "zamp_value_prop": "Zamp handles high-volume procurement ops autonomously, cutting PO cycle time and enforcing compliance without growing the team.",
    },

    # Functional
    "head of procurement": {
        "name": "Head of Procurement",
        "buyer_type": "functional",
        "goals": ["Standardize procurement process", "Reduce vendor onboarding time", "Improve spend visibility"],
        "pains": ["Inconsistent PO process across teams", "Manual contract tracking", "Poor spend visibility"],
        "kpis": ["PO approval cycle time", "Vendor onboarding SLA", "Spend under management %"],
        "messaging_angle": "Position Zamp as the AI employee that enforces procurement process consistently across teams without manual oversight.",
        "zamp_value_prop": "Zamp runs procurement intake, approval routing, and vendor onboarding end-to-end, giving procurement teams consistency without policing every request.",
    },
    "director of procurement": {
        "name": "Head of Procurement",
        "buyer_type": "functional",
        "goals": ["Standardize procurement process", "Reduce vendor onboarding time", "Improve spend visibility"],
        "pains": ["Inconsistent PO process", "Manual contract tracking", "Poor spend visibility"],
        "kpis": ["PO approval cycle time", "Vendor onboarding SLA", "Spend under management %"],
        "messaging_angle": "Position Zamp as the AI employee that enforces procurement process consistently across teams.",
        "zamp_value_prop": "Zamp runs procurement intake, approval routing, and vendor onboarding end-to-end.",
    },

    # Managers
    "procurement manager": {
        "name": "Procurement Manager",
        "buyer_type": "manager",
        "goals": ["Process purchase requests faster", "Track contract renewals", "Reduce supplier escalations"],
        "pains": ["Manual PO creation and tracking", "Contract renewal missed deadlines", "Supplier payment disputes"],
        "kpis": ["PO processing time", "Contract renewal on-time rate", "Supplier satisfaction"],
        "messaging_angle": "Position Zamp as the AI employee that handles PO processing and contract tracking end-to-end.",
        "zamp_value_prop": "Zamp automates PO creation, approval routing, and contract renewal tracking — procurement managers review exceptions, not every transaction.",
    },
    "category manager": {
        "name": "Category Manager",
        "buyer_type": "manager",
        "goals": ["Maximize category savings", "Improve supplier performance visibility", "Streamline RFx processes"],
        "pains": ["Manual RFx management", "Poor supplier performance data", "Time-consuming benchmark analysis"],
        "kpis": ["Category cost savings %", "Supplier performance scores", "RFx cycle time"],
        "messaging_angle": "Position Zamp as the AI employee that handles supplier data collection and RFx admin so category managers focus on negotiation strategy.",
        "zamp_value_prop": "Zamp automates supplier data gathering and RFx coordination, letting category managers spend time on strategy rather than admin.",
    },

    # ==============================================================
    # COMPLIANCE & RISK
    # ==============================================================

    # Economic
    "cco": {
        "name": "CCO / Chief Risk Officer",
        "buyer_type": "economic",
        "goals": ["Continuous compliance monitoring", "Reduce audit prep burden", "Manage regulatory change"],
        "pains": ["Manual compliance monitoring at scale", "Regulatory reporting burden", "Audit prep scramble"],
        "kpis": ["Policy exception rate", "Audit findings count", "Time to close findings", "Regulatory reporting SLA"],
        "messaging_angle": "Position Zamp as the AI employee that monitors compliance continuously and prepares audit evidence automatically — with full, immutable audit trails.",
        "zamp_value_prop": "Zamp runs compliance monitoring and reporting end-to-end with SOC 1/2, ISO 27001, and SOX-ready audit trails, reducing the scramble before every audit.",
    },
    "chief compliance officer": {
        "name": "CCO / Chief Risk Officer",
        "buyer_type": "economic",
        "goals": ["Continuous compliance monitoring", "Reduce audit prep burden", "Manage regulatory change"],
        "pains": ["Manual compliance monitoring at scale", "Regulatory reporting burden", "Audit prep scramble"],
        "kpis": ["Policy exception rate", "Audit findings count", "Time to close findings"],
        "messaging_angle": "Position Zamp as the AI employee that monitors compliance continuously and prepares audit evidence automatically.",
        "zamp_value_prop": "Zamp runs compliance monitoring and reporting end-to-end with full audit trails, reducing the scramble before every audit.",
    },
    "chief risk officer": {
        "name": "CCO / Chief Risk Officer",
        "buyer_type": "economic",
        "goals": ["Continuous risk monitoring", "Reduce audit prep burden", "Manage regulatory change"],
        "pains": ["Manual risk monitoring", "Regulatory reporting burden", "Audit prep scramble"],
        "kpis": ["Policy exception rate", "Audit findings count", "Time to close findings"],
        "messaging_angle": "Position Zamp as the AI employee that monitors risk and compliance continuously, escalating exceptions before they become findings.",
        "zamp_value_prop": "Zamp runs risk monitoring and compliance reporting end-to-end with full audit trails.",
    },

    # Functional
    "head of compliance": {
        "name": "Head of Compliance",
        "buyer_type": "functional",
        "goals": ["Automate compliance checks", "Reduce manual evidence collection", "Stay ahead of regulatory changes"],
        "pains": ["Manual policy monitoring", "Evidence collection for audits", "Tracking regulatory changes across jurisdictions"],
        "kpis": ["Control testing coverage %", "Audit evidence collection time", "Open findings count"],
        "messaging_angle": "Position Zamp as the AI employee that runs compliance checks and evidence collection end-to-end.",
        "zamp_value_prop": "Zamp automates compliance monitoring and audit evidence collection, freeing compliance teams from manual checks to focus on remediation.",
    },
    "vp risk": {
        "name": "Head of Compliance",
        "buyer_type": "functional",
        "goals": ["Automate compliance checks", "Reduce manual evidence collection", "Stay ahead of regulatory changes"],
        "pains": ["Manual policy monitoring", "Evidence collection for audits", "Tracking regulatory changes"],
        "kpis": ["Control testing coverage %", "Audit evidence collection time", "Open findings count"],
        "messaging_angle": "Position Zamp as the AI employee that runs compliance checks and evidence collection end-to-end.",
        "zamp_value_prop": "Zamp automates compliance monitoring and evidence collection, freeing risk teams from manual checks.",
    },

    # Managers
    "compliance manager": {
        "name": "Compliance Manager",
        "buyer_type": "manager",
        "goals": ["Complete control testing on time", "Maintain accurate compliance records", "Reduce audit prep time"],
        "pains": ["Manual control testing", "Chasing evidence from business units", "Spreadsheet-based compliance tracking"],
        "kpis": ["Control testing completion rate", "Evidence collection time", "Audit findings from late evidence"],
        "messaging_angle": "Position Zamp as the AI employee that collects compliance evidence and runs control testing end-to-end.",
        "zamp_value_prop": "Zamp automates control testing and evidence collection workflows, cutting the manual burden that hits compliance managers hardest before every audit.",
    },
    "risk manager": {
        "name": "Risk Manager",
        "buyer_type": "manager",
        "goals": ["Maintain current risk register", "Automate risk monitoring", "Reduce time on risk reporting"],
        "pains": ["Manual risk register updates", "Slow risk reporting cycles", "Tracking control effectiveness manually"],
        "kpis": ["Risk register currency", "Reporting cycle time", "Control effectiveness rate"],
        "messaging_angle": "Position Zamp as the AI employee that keeps the risk register current and generates risk reports autonomously.",
        "zamp_value_prop": "Zamp monitors risk signals and updates reporting automatically, so risk managers spend time on decisions, not data collection.",
    },

    # ==============================================================
    # LEGAL
    # ==============================================================

    # Economic
    "general counsel": {
        "name": "General Counsel / CLO",
        "buyer_type": "economic",
        "goals": ["Reduce legal cost per contract", "Manage legal risk at scale", "Faster contract turnaround"],
        "pains": ["Legal team bandwidth consumed by routine work", "Contract review backlog", "Risk in unreviewed contracts"],
        "kpis": ["Contract turnaround time", "Legal cost as % of revenue", "Contracts handled without outside counsel"],
        "messaging_angle": "Position Zamp as the AI employee that handles routine legal ops end-to-end — NDA review, contract intake, deadline tracking — so counsel focuses on judgment work.",
        "zamp_value_prop": "Zamp runs routine legal ops autonomously, cutting contract turnaround time and reducing outside counsel costs for high-volume, low-risk work.",
    },
    "clo": {
        "name": "General Counsel / CLO",
        "buyer_type": "economic",
        "goals": ["Reduce legal cost per contract", "Manage legal risk at scale", "Faster contract turnaround"],
        "pains": ["Legal bandwidth consumed by routine work", "Contract review backlog", "Risk in unreviewed contracts"],
        "kpis": ["Contract turnaround time", "Legal cost as % of revenue", "Contracts handled without outside counsel"],
        "messaging_angle": "Position Zamp as the AI employee that handles routine legal ops end-to-end so counsel focuses on judgment work.",
        "zamp_value_prop": "Zamp runs routine legal ops autonomously, cutting contract turnaround time and reducing outside counsel costs.",
    },
    "chief legal officer": {
        "name": "General Counsel / CLO",
        "buyer_type": "economic",
        "goals": ["Reduce legal cost per contract", "Manage legal risk at scale", "Faster contract turnaround"],
        "pains": ["Legal bandwidth consumed by routine work", "Contract review backlog", "Risk in unreviewed contracts"],
        "kpis": ["Contract turnaround time", "Legal cost as % of revenue", "Contracts handled without outside counsel"],
        "messaging_angle": "Position Zamp as the AI employee that handles routine legal ops end-to-end so counsel focuses on judgment work.",
        "zamp_value_prop": "Zamp runs routine legal ops autonomously, cutting contract turnaround and reducing outside counsel costs.",
    },

    # Functional
    "head of legal ops": {
        "name": "Head of Legal Operations",
        "buyer_type": "functional",
        "goals": ["Streamline contract lifecycle management", "Improve legal matter tracking", "Reduce outside counsel spend"],
        "pains": ["Manual contract intake and routing", "No visibility into contract status", "Tracking deadlines across a large portfolio"],
        "kpis": ["Contract cycle time", "Outside counsel spend", "Contract portfolio visibility"],
        "messaging_angle": "Position Zamp as the AI employee that runs contract intake, routing, and tracking end-to-end.",
        "zamp_value_prop": "Zamp automates contract lifecycle workflows — intake, review routing, deadline tracking — so legal ops teams manage by exception, not by chasing updates.",
    },
    "vp legal": {
        "name": "Head of Legal Operations",
        "buyer_type": "functional",
        "goals": ["Streamline contract lifecycle", "Improve legal matter tracking", "Reduce outside counsel spend"],
        "pains": ["Manual contract intake and routing", "No contract status visibility", "Tracking deadlines at scale"],
        "kpis": ["Contract cycle time", "Outside counsel spend", "Contract portfolio visibility"],
        "messaging_angle": "Position Zamp as the AI employee that runs contract intake, routing, and tracking end-to-end.",
        "zamp_value_prop": "Zamp automates contract lifecycle workflows so legal teams manage by exception, not by chasing updates.",
    },

    # Managers
    "legal ops manager": {
        "name": "Legal Ops Manager",
        "buyer_type": "manager",
        "goals": ["Faster NDA and standard contract turnaround", "Maintain accurate contract records", "Reduce manual deadline tracking"],
        "pains": ["Manual NDA routing and follow-up", "Contract deadline misses", "Spreadsheet-based contract tracking"],
        "kpis": ["NDA turnaround time", "Contract renewal on-time rate", "Open matter tracking accuracy"],
        "messaging_angle": "Position Zamp as the AI employee that handles NDA routing, contract tracking, and deadline management end-to-end.",
        "zamp_value_prop": "Zamp automates contract routing and deadline tracking, so legal ops managers stop chasing signatures and start managing the portfolio.",
    },
    "contract manager": {
        "name": "Legal Ops Manager",
        "buyer_type": "manager",
        "goals": ["Faster contract turnaround", "Maintain accurate contract records", "Reduce missed renewal deadlines"],
        "pains": ["Manual contract routing", "Missed renewal deadlines", "Version control across counterparties"],
        "kpis": ["Contract cycle time", "Renewal on-time rate", "Version accuracy"],
        "messaging_angle": "Position Zamp as the AI employee that handles contract routing, version management, and deadline tracking autonomously.",
        "zamp_value_prop": "Zamp automates contract routing and deadline tracking end-to-end, cutting manual effort and reducing missed renewals.",
    },

    # ==============================================================
    # MARKETING
    # ==============================================================

    # Economic
    "cmo": {
        "name": "CMO",
        "buyer_type": "economic",
        "goals": ["Scale content and campaign output without headcount", "Improve marketing data quality", "Faster time-to-market"],
        "pains": ["Marketing ops bandwidth is the bottleneck", "Poor data quality hurting targeting", "Manual reporting across channels"],
        "kpis": ["Pipeline generated", "Cost per qualified lead", "Marketing ops headcount vs. output"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume marketing ops — data enrichment, campaign ops, reporting — so the team focuses on strategy and creative.",
        "zamp_value_prop": "Zamp runs marketing data and ops workflows end-to-end, letting marketing teams scale pipeline without scaling headcount.",
    },
    "chief marketing officer": {
        "name": "CMO",
        "buyer_type": "economic",
        "goals": ["Scale campaign output without headcount", "Improve marketing data quality", "Faster time-to-market"],
        "pains": ["Marketing ops as bottleneck", "Poor data quality", "Manual cross-channel reporting"],
        "kpis": ["Pipeline generated", "Cost per qualified lead", "Marketing ops headcount vs. output"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume marketing ops so the team focuses on strategy and creative.",
        "zamp_value_prop": "Zamp runs marketing data and ops workflows end-to-end, letting marketing teams scale pipeline without scaling headcount.",
    },

    # Functional
    "vp marketing": {
        "name": "VP Marketing / Head of Marketing Ops",
        "buyer_type": "functional",
        "goals": ["Improve campaign efficiency", "Clean and enrich marketing database", "Reduce time on reporting"],
        "pains": ["Dirty contact data degrading campaign performance", "Manual cross-channel reporting", "Campaign ops overhead"],
        "kpis": ["Email deliverability rate", "Data quality score", "Time to campaign launch"],
        "messaging_angle": "Position Zamp as the AI employee that keeps the marketing database clean and campaign reporting current.",
        "zamp_value_prop": "Zamp runs marketing data enrichment and campaign reporting autonomously, so marketing leaders have clean data and current metrics without manual effort.",
    },
    "head of marketing": {
        "name": "VP Marketing / Head of Marketing Ops",
        "buyer_type": "functional",
        "goals": ["Improve campaign efficiency", "Clean marketing database", "Reduce reporting time"],
        "pains": ["Dirty contact data", "Manual cross-channel reporting", "Campaign ops overhead"],
        "kpis": ["Email deliverability rate", "Data quality score", "Time to campaign launch"],
        "messaging_angle": "Position Zamp as the AI employee that keeps the marketing database clean and reporting current.",
        "zamp_value_prop": "Zamp runs marketing data enrichment and campaign reporting autonomously, freeing marketing teams from ops overhead.",
    },

    # Managers
    "marketing ops manager": {
        "name": "Marketing Ops Manager",
        "buyer_type": "manager",
        "goals": ["Maintain clean CRM and marketing database", "Automate campaign reporting", "Reduce manual list management"],
        "pains": ["Manual list segmentation and cleanup", "Reporting built fresh every cycle", "Data inconsistencies between CRM and MAP"],
        "kpis": ["Database health score", "Reporting cycle time", "List accuracy rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles database hygiene, list management, and reporting end-to-end.",
        "zamp_value_prop": "Zamp automates marketing database hygiene and reporting workflows, so marketing ops managers stop doing data janitorial work.",
    },
    "demand gen manager": {
        "name": "Demand Gen Manager",
        "buyer_type": "manager",
        "goals": ["Scale inbound pipeline", "Reduce campaign admin", "Improve lead routing accuracy"],
        "pains": ["Manual campaign setup and tracking", "Slow lead routing causing drop-off", "Reporting assembled manually post-campaign"],
        "kpis": ["Cost per MQL", "Lead response time", "Campaign launch-to-live time"],
        "messaging_angle": "Position Zamp as the AI employee that handles campaign ops and lead routing end-to-end.",
        "zamp_value_prop": "Zamp automates campaign ops and lead routing, cutting the time between launch and first lead response.",
    },

    # ==============================================================
    # SALES
    # ==============================================================

    # Economic
    "cro": {
        "name": "CRO / VP Sales",
        "buyer_type": "economic",
        "goals": ["Maximize revenue per rep", "Improve forecast predictability", "Scale sales without linear headcount"],
        "pains": ["Reps spending time on admin instead of selling", "Unreliable pipeline data", "Long new-rep ramp time"],
        "kpis": ["Revenue per rep", "Forecast accuracy", "Quota attainment %", "Ramp time"],
        "messaging_angle": "Position Zamp as the AI employee that handles sales ops — CRM hygiene, prospect research, commission tracking — so reps focus on selling.",
        "zamp_value_prop": "Zamp runs sales ops workflows end-to-end, giving reps back selling time and leadership reliable pipeline data without a large ops team.",
    },
    "chief revenue officer": {
        "name": "CRO / VP Sales",
        "buyer_type": "economic",
        "goals": ["Maximize revenue per rep", "Improve forecast predictability", "Scale sales without linear headcount"],
        "pains": ["Reps spending time on admin", "Unreliable pipeline data", "Long ramp time"],
        "kpis": ["Revenue per rep", "Forecast accuracy", "Quota attainment %"],
        "messaging_angle": "Position Zamp as the AI employee that handles sales ops so reps focus on selling.",
        "zamp_value_prop": "Zamp runs sales ops workflows end-to-end, giving reps selling time and leadership reliable pipeline data.",
    },
    "vp sales": {
        "name": "CRO / VP Sales",
        "buyer_type": "economic",
        "goals": ["Hit quota with current headcount", "Improve win rate through better prep", "Reduce rep admin burden"],
        "pains": ["Reps spending time on admin", "Poor CRM hygiene affecting forecasts", "New rep ramp time"],
        "kpis": ["Quota attainment %", "Win rate", "Revenue per rep"],
        "messaging_angle": "Position Zamp as the AI employee that handles sales research and CRM updates so reps walk into every call prepared.",
        "zamp_value_prop": "Zamp automates rep-facing admin — prospect research, CRM updates, follow-up scheduling — so reps spend time on pipeline, not paperwork.",
    },

    # Functional
    "head of sales ops": {
        "name": "Head of Sales Operations",
        "buyer_type": "functional",
        "goals": ["Reliable CRM data", "Accurate commission tracking", "Scalable sales process"],
        "pains": ["Manual CRM hygiene", "Commission calculation errors", "Sales process inconsistency"],
        "kpis": ["CRM data completeness %", "Commission error rate", "Sales process adherence"],
        "messaging_angle": "Position Zamp as the AI employee that keeps CRM data clean and commissions accurate without a large ops team.",
        "zamp_value_prop": "Zamp runs CRM hygiene, commission tracking, and sales reporting autonomously, so sales ops teams focus on process improvement, not data fixing.",
    },
    "director of sales operations": {
        "name": "Head of Sales Operations",
        "buyer_type": "functional",
        "goals": ["Reliable CRM data", "Accurate commission tracking", "Scalable sales process"],
        "pains": ["Manual CRM hygiene", "Commission calculation errors", "Sales process inconsistency"],
        "kpis": ["CRM data completeness %", "Commission error rate", "Sales process adherence"],
        "messaging_angle": "Position Zamp as the AI employee that keeps CRM data clean and commissions accurate.",
        "zamp_value_prop": "Zamp runs CRM hygiene and commission tracking autonomously, so sales ops focuses on process improvement.",
    },

    # Managers
    "sales ops manager": {
        "name": "Sales Ops Manager",
        "buyer_type": "manager",
        "goals": ["Keep CRM data accurate", "Run commission calculations on time", "Produce sales reports without manual effort"],
        "pains": ["Manual CRM updates and deduplication", "Commission spreadsheet errors", "Reporting rebuilt from scratch every cycle"],
        "kpis": ["CRM record accuracy", "Commission processing time", "Reporting cycle time"],
        "messaging_angle": "Position Zamp as the AI employee that handles CRM hygiene, commission calculations, and report generation end-to-end.",
        "zamp_value_prop": "Zamp automates the repetitive data work in sales ops — CRM hygiene, commission calculations, reporting — so the team stops being a data janitor.",
    },
    "inside sales manager": {
        "name": "Inside Sales Manager",
        "buyer_type": "manager",
        "goals": ["Maximize rep activity on selling", "Reduce time on manual prospecting research", "Keep pipeline current"],
        "pains": ["Reps spending time on research and data entry", "Stale pipeline data", "Inconsistent outreach quality"],
        "kpis": ["Dials per rep per day", "Pipeline coverage ratio", "Outreach response rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles prospect research and outreach prep so reps walk into every call with context.",
        "zamp_value_prop": "Zamp prepares prospect intelligence and personalizes outreach at scale, so inside sales teams spend time on conversations, not research.",
    },

    # ==============================================================
    # IT & TECHNOLOGY
    # ==============================================================

    # Economic
    "cio": {
        "name": "CIO",
        "buyer_type": "economic",
        "goals": ["Reduce IT ops cost", "Improve service desk efficiency", "Enable business with less shadow IT"],
        "pains": ["IT ops workload growing faster than team", "Manual user provisioning and deprovisioning", "High L1 ticket volume consuming support"],
        "kpis": ["IT cost per employee", "Ticket resolution time", "User provisioning SLA"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume, repetitive IT ops — provisioning, ticket triage, asset management — without adding headcount.",
        "zamp_value_prop": "Zamp runs IT ops workflows end-to-end with enterprise-grade security (SOC 1/2, ISO 27001), letting IT teams focus on strategic initiatives instead of L1 work.",
    },
    "chief information officer": {
        "name": "CIO",
        "buyer_type": "economic",
        "goals": ["Reduce IT ops cost", "Improve service desk efficiency", "Enable business with less shadow IT"],
        "pains": ["IT ops workload growing faster than team", "Manual provisioning", "High L1 ticket volume"],
        "kpis": ["IT cost per employee", "Ticket resolution time", "User provisioning SLA"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume repetitive IT ops without adding headcount.",
        "zamp_value_prop": "Zamp runs IT ops workflows end-to-end with enterprise-grade security, letting IT teams focus on strategic work.",
    },

    # Functional
    "vp it": {
        "name": "VP IT / Head of IT Operations",
        "buyer_type": "functional",
        "goals": ["Improve service desk throughput", "Automate user lifecycle management", "Reduce manual asset tracking"],
        "pains": ["L1 ticket volume overwhelming the team", "Manual onboarding/offboarding", "Asset inventory in spreadsheets"],
        "kpis": ["First contact resolution rate", "Onboarding completion time", "Asset inventory accuracy"],
        "messaging_angle": "Position Zamp as the AI employee that resolves L1 tickets, manages user lifecycle, and tracks assets end-to-end.",
        "zamp_value_prop": "Zamp automates L1 ticket resolution, user provisioning, and asset management — IT ops teams handle escalations, not routine requests.",
    },
    "head of it": {
        "name": "VP IT / Head of IT Operations",
        "buyer_type": "functional",
        "goals": ["Improve service desk throughput", "Automate user lifecycle management", "Reduce manual asset tracking"],
        "pains": ["L1 ticket volume", "Manual onboarding/offboarding", "Asset tracking in spreadsheets"],
        "kpis": ["First contact resolution rate", "Onboarding completion time", "Asset inventory accuracy"],
        "messaging_angle": "Position Zamp as the AI employee that resolves L1 tickets and manages user lifecycle end-to-end.",
        "zamp_value_prop": "Zamp automates L1 ticket resolution and user provisioning — IT ops teams handle escalations, not routine requests.",
    },

    # Managers
    "it manager": {
        "name": "IT Manager",
        "buyer_type": "manager",
        "goals": ["Hit SLA on ticket resolution", "Complete onboarding/offboarding on time", "Keep asset inventory accurate"],
        "pains": ["L1 ticket backlog", "Manual onboarding checklists across systems", "Asset inventory drift"],
        "kpis": ["SLA breach rate", "Onboarding on-time completion", "Asset inventory accuracy %"],
        "messaging_angle": "Position Zamp as the AI employee that handles L1 ticket triage and onboarding workflows end-to-end.",
        "zamp_value_prop": "Zamp resolves L1 tickets and runs onboarding/offboarding checklists autonomously, so IT managers stop fighting the queue.",
    },
    "it operations manager": {
        "name": "IT Manager",
        "buyer_type": "manager",
        "goals": ["Hit SLA on ticket resolution", "Complete onboarding/offboarding on time", "Keep asset inventory accurate"],
        "pains": ["L1 ticket backlog", "Manual onboarding checklists", "Asset inventory drift"],
        "kpis": ["SLA breach rate", "Onboarding on-time completion", "Asset inventory accuracy %"],
        "messaging_angle": "Position Zamp as the AI employee that handles L1 ticket triage and onboarding workflows end-to-end.",
        "zamp_value_prop": "Zamp resolves L1 tickets and runs onboarding/offboarding checklists autonomously, so IT ops managers stop fighting the queue.",
    },

    # ==============================================================
    # CYBERSECURITY
    # ==============================================================

    # Economic
    "ciso": {
        "name": "CISO",
        "buyer_type": "economic",
        "goals": ["Continuous threat monitoring", "Reduce MTTD and MTTR", "Automate compliance reporting"],
        "pains": ["Alert fatigue drowning the SOC team", "Manual compliance evidence collection", "Security ops scaling behind threat volume"],
        "kpis": ["MTTD / MTTR", "False positive rate", "Compliance reporting cycle time"],
        "messaging_angle": "Position Zamp as the AI employee that monitors threats and handles compliance reporting end-to-end, escalating only true positives to the security team.",
        "zamp_value_prop": "Zamp runs security monitoring and compliance reporting autonomously with SOC 1/2 and ISO 27001 built in, so the security team focuses on real threats.",
    },
    "chief information security officer": {
        "name": "CISO",
        "buyer_type": "economic",
        "goals": ["Continuous threat monitoring", "Reduce MTTD/MTTR", "Automate compliance reporting"],
        "pains": ["Alert fatigue", "Manual compliance evidence collection", "Security ops scaling behind threat volume"],
        "kpis": ["MTTD / MTTR", "False positive rate", "Compliance reporting cycle time"],
        "messaging_angle": "Position Zamp as the AI employee that monitors threats and handles compliance reporting, escalating only true positives.",
        "zamp_value_prop": "Zamp runs security monitoring and compliance reporting autonomously, so the security team focuses on real threats.",
    },

    # Functional
    "head of security": {
        "name": "Head of Security Operations",
        "buyer_type": "functional",
        "goals": ["Reduce alert fatigue", "Automate routine SOC tasks", "Maintain audit-ready security posture"],
        "pains": ["L1 alert triage consuming analyst time", "Manual security reporting", "Vulnerability tracking overhead"],
        "kpis": ["Alerts triaged per analyst", "Mean time to triage", "Vulnerability remediation SLA"],
        "messaging_angle": "Position Zamp as the AI employee that triages L1 alerts and tracks vulnerabilities end-to-end, so analysts focus on real incidents.",
        "zamp_value_prop": "Zamp automates L1 alert triage and vulnerability tracking, cutting analyst toil and improving mean time to respond.",
    },
    "director of information security": {
        "name": "Head of Security Operations",
        "buyer_type": "functional",
        "goals": ["Reduce alert fatigue", "Automate routine SOC tasks", "Maintain audit-ready security posture"],
        "pains": ["L1 alert triage consuming analyst time", "Manual security reporting", "Vulnerability tracking overhead"],
        "kpis": ["Alerts triaged per analyst", "Mean time to triage", "Vulnerability remediation SLA"],
        "messaging_angle": "Position Zamp as the AI employee that triages L1 alerts and tracks vulnerabilities end-to-end.",
        "zamp_value_prop": "Zamp automates L1 alert triage and vulnerability tracking, cutting analyst toil and improving response time.",
    },

    # Manager
    "security operations manager": {
        "name": "Security Operations Manager",
        "buyer_type": "manager",
        "goals": ["Hit SLA on alert triage", "Reduce false positive handling time", "Produce compliance reports on time"],
        "pains": ["Alert queue larger than team can handle", "Manual false positive filtering", "Compliance reporting assembled manually"],
        "kpis": ["Alert triage SLA", "False positive rate", "Compliance report delivery time"],
        "messaging_angle": "Position Zamp as the AI employee that handles L1 alert triage and compliance reporting end-to-end.",
        "zamp_value_prop": "Zamp triages L1 alerts and generates compliance reports autonomously, so the SOC team focuses on real threats and remediation.",
    },

    # ==============================================================
    # PRODUCT & ENGINEERING
    # ==============================================================

    # Economic
    "chief product officer": {
        "name": "Chief Product Officer",
        "buyer_type": "economic",
        "goals": ["Ship faster without scaling team", "Reduce engineering time on operational overhead", "Better product analytics"],
        "pains": ["Engineering time lost to incident triage, sprint reporting, and release ops", "Slow feedback loops from users", "Manual product analytics"],
        "kpis": ["Feature velocity", "Engineering time on value vs. overhead %", "Time to insight from user data"],
        "messaging_angle": "Position Zamp as the AI employee that handles product and engineering ops overhead end-to-end, so the team ships features, not processes.",
        "zamp_value_prop": "Zamp automates incident triage, release notes, sprint reporting, and user feedback analysis — giving product and engineering teams back the time they spend on operational overhead.",
    },
    "cto": {
        "name": "CTO",
        "buyer_type": "economic",
        "goals": ["Increase engineering throughput", "Reduce operational overhead on the eng team", "Scale platform reliability without linear headcount"],
        "pains": ["Engineers pulled into incident triage and operational tasks", "On-call fatigue", "Platform ops consuming eng capacity"],
        "kpis": ["Deployment frequency", "Incident MTTD/MTTR", "Engineering time on product vs. ops"],
        "messaging_angle": "Position Zamp as the AI employee that handles platform ops and incident response end-to-end, so engineers focus on building.",
        "zamp_value_prop": "Zamp runs incident triage, runbook execution, and ops reporting autonomously, reducing engineering toil and improving platform reliability without adding headcount.",
    },
    "chief technology officer": {
        "name": "CTO",
        "buyer_type": "economic",
        "goals": ["Increase engineering throughput", "Reduce operational overhead", "Scale platform reliability without linear headcount"],
        "pains": ["Engineers pulled into ops tasks", "On-call fatigue", "Platform ops consuming eng capacity"],
        "kpis": ["Deployment frequency", "Incident MTTD/MTTR", "Engineering time on product vs. ops"],
        "messaging_angle": "Position Zamp as the AI employee that handles platform ops and incident response end-to-end, so engineers focus on building.",
        "zamp_value_prop": "Zamp runs incident triage, runbook execution, and ops reporting autonomously, reducing engineering toil without adding headcount.",
    },

    # Functional
    "vp product": {
        "name": "VP Product",
        "buyer_type": "functional",
        "goals": ["Faster feature delivery", "Better signal from user feedback", "Reduce team time on process overhead"],
        "pains": ["PMs spending time on status updates and reporting", "Unstructured user feedback", "Sprint ceremonies consuming strategic time"],
        "kpis": ["Time-to-ship per feature", "User feedback synthesis time", "PM time on admin vs. strategy"],
        "messaging_angle": "Position Zamp as the AI employee that handles product reporting, user feedback analysis, and sprint ops end-to-end.",
        "zamp_value_prop": "Zamp automates product reporting, user feedback synthesis, and sprint ops so product teams focus on decisions, not documentation.",
    },
    "head of product": {
        "name": "VP Product",
        "buyer_type": "functional",
        "goals": ["Faster feature delivery", "Better signal from user feedback", "Reduce overhead"],
        "pains": ["PMs spending time on status updates", "Unstructured user feedback", "Sprint ceremonies consuming strategic time"],
        "kpis": ["Time-to-ship", "Feedback synthesis time", "PM time on admin vs. strategy"],
        "messaging_angle": "Position Zamp as the AI employee that handles product reporting and feedback synthesis end-to-end.",
        "zamp_value_prop": "Zamp automates product reporting and user feedback synthesis so product teams focus on decisions, not documentation.",
    },
    "head of platform engineering": {
        "name": "Head of Platform Engineering",
        "buyer_type": "functional",
        "goals": ["Improve platform reliability", "Reduce on-call burden", "Automate runbook execution"],
        "pains": ["Manual runbook execution during incidents", "On-call fatigue from repetitive alerts", "Toil consuming platform team capacity"],
        "kpis": ["MTTR", "On-call incidents per engineer", "Toil % of eng work"],
        "messaging_angle": "Position Zamp as the AI employee that executes runbooks and triages alerts end-to-end, reducing on-call burden.",
        "zamp_value_prop": "Zamp runs runbook execution and alert triage autonomously, so platform engineers handle real incidents, not repetitive ops.",
    },

    # Managers
    "product manager": {
        "name": "Product Manager",
        "buyer_type": "manager",
        "goals": ["Ship on time", "Synthesize user feedback faster", "Reduce time on status reporting"],
        "pains": ["Manually aggregating user feedback from multiple sources", "Weekly status updates consuming time", "Release notes written from scratch"],
        "kpis": ["Time to ship", "Feedback synthesis time", "Status reporting time"],
        "messaging_angle": "Position Zamp as the AI employee that aggregates user feedback and generates status reports end-to-end.",
        "zamp_value_prop": "Zamp automates user feedback synthesis and release documentation, so product managers spend time on product decisions, not process.",
    },
    "senior product manager": {
        "name": "Senior Product Manager",
        "buyer_type": "manager",
        "goals": ["Drive cross-team feature delivery", "Synthesize qualitative and quantitative signals fast", "Reduce roadmap communication overhead"],
        "pains": ["Roadmap updates and stakeholder alignment consuming focus time", "User research synthesis taking days", "Cross-team dependency tracking done manually"],
        "kpis": ["Feature delivery rate", "Time from insight to roadmap decision", "Stakeholder alignment NPS"],
        "messaging_angle": "Position Zamp as the AI employee that handles research synthesis, dependency tracking, and roadmap communication end-to-end.",
        "zamp_value_prop": "Zamp synthesizes user signals and tracks cross-team dependencies autonomously, so senior PMs spend time on strategy and decisions, not coordination.",
    },
    "technical program manager": {
        "name": "Technical Program Manager",
        "buyer_type": "manager",
        "goals": ["Track cross-team dependencies", "Reduce status update overhead", "Flag risks early"],
        "pains": ["Manual dependency tracking across teams", "Status updates consumed in meetings", "Risks surfaced too late"],
        "kpis": ["On-time delivery rate", "Risk identification lead time", "Time on status reporting"],
        "messaging_angle": "Position Zamp as the AI employee that tracks cross-team dependencies and surfaces risks autonomously.",
        "zamp_value_prop": "Zamp monitors cross-team dependencies and flags risks end-to-end, so TPMs spend time on problem-solving, not status aggregation.",
    },
    "tpm": {
        "name": "Technical Program Manager",
        "buyer_type": "manager",
        "goals": ["Track cross-team dependencies", "Reduce status update overhead", "Flag risks early"],
        "pains": ["Manual dependency tracking", "Status updates consumed in meetings", "Risks surfaced too late"],
        "kpis": ["On-time delivery rate", "Risk identification lead time", "Time on status reporting"],
        "messaging_angle": "Position Zamp as the AI employee that tracks cross-team dependencies and surfaces risks autonomously.",
        "zamp_value_prop": "Zamp monitors cross-team dependencies and flags risks end-to-end, so TPMs spend time on problem-solving, not status aggregation.",
    },
    "engineering manager": {
        "name": "Engineering Manager",
        "buyer_type": "functional",
        "goals": ["Maximize team shipping velocity", "Reduce toil and interrupt-driven work", "Improve sprint predictability"],
        "pains": ["Incident interruptions breaking sprint focus", "Sprint ceremonies and status reporting overhead", "Onboarding new engineers slowly"],
        "kpis": ["Sprint velocity", "Toil % of eng time", "Incident interruptions per sprint", "New hire ramp time"],
        "messaging_angle": "Position Zamp as the AI employee that handles toil, incident triage, and eng ops overhead end-to-end, protecting the team's focus for feature work.",
        "zamp_value_prop": "Zamp reduces engineering toil and interrupt-driven ops work autonomously, so engineering managers protect sprint focus and ship faster.",
    },
    "em": {
        "name": "Engineering Manager",
        "buyer_type": "functional",
        "goals": ["Maximize team shipping velocity", "Reduce toil and interrupt-driven work", "Improve sprint predictability"],
        "pains": ["Incident interruptions breaking sprint focus", "Sprint ceremony overhead", "Slow new engineer onboarding"],
        "kpis": ["Sprint velocity", "Toil % of eng time", "Incident interruptions per sprint"],
        "messaging_angle": "Position Zamp as the AI employee that handles toil, incident triage, and eng ops overhead end-to-end.",
        "zamp_value_prop": "Zamp reduces engineering toil and interrupt-driven ops work autonomously, so engineering managers protect sprint focus and ship faster.",
    },
    "senior engineering manager": {
        "name": "Engineering Manager",
        "buyer_type": "functional",
        "goals": ["Maximize team shipping velocity across multiple teams", "Reduce cross-team coordination overhead", "Improve engineering org efficiency"],
        "pains": ["Cross-team dependencies slowing delivery", "Operational overhead consuming eng capacity", "Status reporting and escalation management"],
        "kpis": ["Cross-team delivery on-time rate", "Eng team toil %", "Incident escalation rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles cross-team ops coordination and toil end-to-end, freeing engineering leadership for strategy.",
        "zamp_value_prop": "Zamp reduces engineering toil and cross-team coordination overhead autonomously, so senior EMs can focus their teams on shipping.",
    },
    "staff engineer": {
        "name": "Engineering Manager",
        "buyer_type": "manager",
        "goals": ["Reduce toil blocking technical strategy", "Improve platform reliability", "Automate operational runbooks"],
        "pains": ["Toil and ops work consuming strategic technical time", "Manual runbook execution during incidents", "Slow documentation and knowledge capture"],
        "kpis": ["Toil % of work", "Incident MTTR", "Runbook automation coverage"],
        "messaging_angle": "Position Zamp as the AI employee that runs operational runbooks and handles toil end-to-end, so staff engineers focus on technical leverage.",
        "zamp_value_prop": "Zamp executes runbooks and handles repetitive ops work autonomously, freeing staff engineers to focus on platform strategy and architectural improvements.",
    },

    # ==============================================================
    # REVOPS & GTM
    # ==============================================================

    # Functional (CRO is the economic buyer — listed under Sales)
    "vp revops": {
        "name": "VP RevOps / Head of GTM Ops",
        "buyer_type": "functional",
        "goals": ["Improve forecast accuracy", "Clean pipeline data", "Reduce rep time on admin"],
        "pains": ["Manual CRM hygiene", "Poor pipeline data quality", "Forecast unreliability"],
        "kpis": ["Forecast accuracy", "CRM data completeness %", "Rep time on admin"],
        "messaging_angle": "Position Zamp as the AI employee that keeps CRM data clean and pipeline intelligence current without ops headcount.",
        "zamp_value_prop": "Zamp runs GTM data ops autonomously — enrichment, hygiene, reporting — so RevOps teams get reliable pipeline data without manual effort.",
    },
    "head of revenue operations": {
        "name": "VP RevOps / Head of GTM Ops",
        "buyer_type": "functional",
        "goals": ["Improve forecast accuracy", "Clean pipeline data", "Reduce rep time on admin"],
        "pains": ["Manual CRM hygiene", "Poor pipeline data quality", "Forecast unreliability"],
        "kpis": ["Forecast accuracy", "CRM data completeness %", "Rep time on admin"],
        "messaging_angle": "Position Zamp as the AI employee that keeps CRM data clean and pipeline intelligence current.",
        "zamp_value_prop": "Zamp runs GTM data ops autonomously — enrichment, hygiene, reporting — so RevOps gets reliable pipeline data without manual effort.",
    },

    # Manager
    "revops manager": {
        "name": "RevOps Manager",
        "buyer_type": "manager",
        "goals": ["Keep CRM data accurate", "Automate GTM reporting", "Reduce rep admin friction"],
        "pains": ["Manual CRM deduplication and enrichment", "Weekly pipeline reports built from scratch", "Inconsistent rep CRM adoption"],
        "kpis": ["CRM data completeness %", "Reporting cycle time", "Rep CRM adoption rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles CRM hygiene and GTM reporting end-to-end.",
        "zamp_value_prop": "Zamp automates CRM hygiene and pipeline reporting, so RevOps managers stop doing data janitorial work and start influencing strategy.",
    },

    # ==============================================================
    # CUSTOMER SUCCESS & SUPPORT
    # ==============================================================

    # Economic
    "chief customer officer": {
        "name": "Chief Customer Officer",
        "buyer_type": "economic",
        "goals": ["Maintain CSAT as customer base scales", "Reduce churn", "Improve NPS without adding headcount"],
        "pains": ["Support costs scaling with revenue", "Repetitive queries consuming agent capacity", "Slow resolution hurting retention"],
        "kpis": ["Net Revenue Retention", "CSAT / NPS", "Support cost per customer"],
        "messaging_angle": "Position Zamp as the AI employee that handles repetitive customer queries end-to-end, so the team focuses on high-value relationships and churn risk.",
        "zamp_value_prop": "Zamp resolves high-volume, repetitive support queries autonomously at ~99% accuracy, keeping CSAT high while decoupling support headcount from revenue growth.",
    },

    # Functional
    "vp customer success": {
        "name": "VP Customer Success / Head of Support",
        "buyer_type": "functional",
        "goals": ["Maintain CSAT at scale", "Reduce first-response time", "Handle volume without linear headcount growth"],
        "pains": ["Ticket volume growing faster than headcount", "Repetitive query handling", "Agent burnout"],
        "kpis": ["CSAT", "First-response time", "Tickets per agent"],
        "messaging_angle": "Position Zamp as the AI employee that handles repetitive support tickets end-to-end, escalating only complex cases to humans.",
        "zamp_value_prop": "Zamp resolves high-volume, repetitive support queries autonomously at ~99% accuracy, keeping CSAT high without adding agents.",
    },
    "head of support": {
        "name": "VP Customer Success / Head of Support",
        "buyer_type": "functional",
        "goals": ["Maintain CSAT at scale", "Reduce first-response time", "Handle volume without linear headcount"],
        "pains": ["Ticket volume growing faster than headcount", "Repetitive query handling", "Agent burnout"],
        "kpis": ["CSAT", "First-response time", "Tickets per agent"],
        "messaging_angle": "Position Zamp as the AI employee that handles repetitive tickets end-to-end, escalating only complex cases.",
        "zamp_value_prop": "Zamp resolves repetitive support queries autonomously, keeping CSAT high without adding agents.",
    },

    # Managers
    "support manager": {
        "name": "Support Manager",
        "buyer_type": "manager",
        "goals": ["Hit first-response SLA", "Reduce average handle time", "Cut repeat contact rate"],
        "pains": ["Queue backlog from repetitive ticket types", "Agents answering the same queries repeatedly", "Reporting built manually each week"],
        "kpis": ["First-response SLA adherence", "Average handle time", "Repeat contact rate"],
        "messaging_angle": "Position Zamp as the AI employee that handles the repetitive ticket categories end-to-end, escalating only true exceptions.",
        "zamp_value_prop": "Zamp resolves high-volume repetitive ticket categories autonomously, so support managers run a leaner queue without sacrificing CSAT.",
    },
    "customer success manager": {
        "name": "Customer Success Manager Lead",
        "buyer_type": "manager",
        "goals": ["Reduce manual health-score tracking", "Flag churn risk earlier", "Automate routine customer touchpoints"],
        "pains": ["Manual account health checks", "Renewal prep consuming strategic time", "Customer data scattered across tools"],
        "kpis": ["Account health score accuracy", "Churn rate", "Time to renewal prep completion"],
        "messaging_angle": "Position Zamp as the AI employee that monitors account health and flags churn risk end-to-end.",
        "zamp_value_prop": "Zamp monitors customer health signals and automates routine touchpoints, so CSMs focus on relationships and at-risk accounts.",
    },

    # ==============================================================
    # RECRUITING & PEOPLE OPS
    # ==============================================================

    # Economic
    "chro": {
        "name": "CHRO / Chief People Officer",
        "buyer_type": "economic",
        "goals": ["Scale hiring without scaling recruiting headcount", "Improve employee experience", "Reduce people ops overhead"],
        "pains": ["Recruiting volume outpacing team capacity", "Manual HR processes creating bottlenecks", "People data scattered across systems"],
        "kpis": ["Time to hire", "HR cost per employee", "Recruiter capacity (reqs per recruiter)"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume recruiting and HR ops workflows end-to-end, so people teams focus on culture and talent strategy.",
        "zamp_value_prop": "Zamp runs sourcing, screening, scheduling, and HR ops workflows autonomously, letting people teams scale hiring without scaling headcount.",
    },
    "chief people officer": {
        "name": "CHRO / Chief People Officer",
        "buyer_type": "economic",
        "goals": ["Scale hiring without scaling recruiting headcount", "Improve employee experience", "Reduce people ops overhead"],
        "pains": ["Recruiting volume outpacing team capacity", "Manual HR processes", "People data scattered across systems"],
        "kpis": ["Time to hire", "HR cost per employee", "Recruiter capacity"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume recruiting and HR ops end-to-end.",
        "zamp_value_prop": "Zamp runs sourcing, screening, and HR ops workflows autonomously, letting people teams scale without scaling headcount.",
    },

    # Functional
    "head of recruiting": {
        "name": "Head of Recruiting / VP People",
        "buyer_type": "functional",
        "goals": ["Reduce time to hire", "Scale screening without adding recruiters", "Improve candidate experience"],
        "pains": ["High-volume screening overhead", "Interview scheduling bottlenecks", "Recruiter capacity limits"],
        "kpis": ["Time to hire", "Screened-to-interview ratio", "Recruiter capacity (reqs per recruiter)"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume screening and scheduling end-to-end, so recruiters focus on relationships.",
        "zamp_value_prop": "Zamp runs sourcing, screening, and scheduling workflows autonomously, letting recruiting teams handle more reqs without more headcount.",
    },
    "vp people": {
        "name": "Head of Recruiting / VP People",
        "buyer_type": "functional",
        "goals": ["Reduce time to hire", "Scale screening without adding recruiters", "Improve candidate experience"],
        "pains": ["High-volume screening overhead", "Interview scheduling bottlenecks", "Recruiter capacity limits"],
        "kpis": ["Time to hire", "Screened-to-interview ratio", "Recruiter capacity"],
        "messaging_angle": "Position Zamp as the AI employee that handles high-volume screening and scheduling end-to-end.",
        "zamp_value_prop": "Zamp runs sourcing, screening, and scheduling autonomously, letting recruiting teams handle more reqs without more headcount.",
    },
    "vp hr": {
        "name": "Head of Recruiting / VP People",
        "buyer_type": "functional",
        "goals": ["Streamline HR ops", "Reduce manual onboarding overhead", "Improve employee data accuracy"],
        "pains": ["Manual onboarding checklists", "HR data inconsistencies", "Routine HR queries consuming team time"],
        "kpis": ["Onboarding completion time", "HR ticket resolution time", "Employee data accuracy"],
        "messaging_angle": "Position Zamp as the AI employee that handles routine HR ops end-to-end.",
        "zamp_value_prop": "Zamp automates HR ops workflows end-to-end, so HR teams handle strategic people work, not administrative repetition.",
    },

    # Managers
    "recruiting manager": {
        "name": "Recruiting Manager",
        "buyer_type": "manager",
        "goals": ["Fill reqs faster", "Reduce time on screening and scheduling", "Keep candidates engaged"],
        "pains": ["Manual resume screening at volume", "Interview scheduling back-and-forth", "Candidate drop-off from slow process"],
        "kpis": ["Time to screen", "Interview scheduling time", "Candidate drop-off rate"],
        "messaging_angle": "Position Zamp as the AI employee that screens resumes and schedules interviews end-to-end, so recruiters spend time on relationships.",
        "zamp_value_prop": "Zamp handles resume screening and interview scheduling autonomously, cutting time-to-screen and keeping candidates engaged.",
    },
    "hr operations manager": {
        "name": "HR Operations Manager",
        "buyer_type": "manager",
        "goals": ["Keep employee records accurate", "Process HR requests on time", "Reduce manual onboarding steps"],
        "pains": ["Manual employee data updates across systems", "Onboarding checklist tracking", "Routine HR query volume"],
        "kpis": ["Employee data accuracy %", "Onboarding on-time completion", "HR ticket resolution time"],
        "messaging_angle": "Position Zamp as the AI employee that keeps employee records accurate and processes HR requests end-to-end.",
        "zamp_value_prop": "Zamp automates HR ops workflows — record updates, onboarding steps, routine queries — so HR ops managers focus on exceptions and improvements.",
    },

    # ==============================================================
    # DATA OPERATIONS
    # ==============================================================

    # Economic
    "chief data officer": {
        "name": "Chief Data Officer",
        "buyer_type": "economic",
        "goals": ["Reliable data infrastructure", "Data-driven decisions across the org", "Reduce data engineering toil"],
        "pains": ["Pipeline failures causing downstream report issues", "Data quality problems undermining analytics trust", "Data eng consumed by maintenance instead of new capability"],
        "kpis": ["Data pipeline uptime %", "Data quality score", "Eng time on toil vs. new capability"],
        "messaging_angle": "Position Zamp as the AI employee that monitors data pipelines and resolves quality issues autonomously, so data teams build capability instead of fighting fires.",
        "zamp_value_prop": "Zamp runs data pipeline monitoring and quality remediation end-to-end, freeing data teams from maintenance toil to focus on analytics and new data products.",
    },
    "cdo": {
        "name": "Chief Data Officer",
        "buyer_type": "economic",
        "goals": ["Reliable data infrastructure", "Data-driven decisions across the org", "Reduce data engineering toil"],
        "pains": ["Pipeline failures", "Data quality problems", "Data eng consumed by maintenance"],
        "kpis": ["Pipeline uptime %", "Data quality score", "Toil %"],
        "messaging_angle": "Position Zamp as the AI employee that monitors data pipelines and resolves quality issues autonomously.",
        "zamp_value_prop": "Zamp runs data pipeline monitoring and quality remediation end-to-end, freeing data teams from toil to build new capabilities.",
    },

    # Functional
    "head of data": {
        "name": "Head of Data / Data Ops Lead",
        "buyer_type": "functional",
        "goals": ["Reliable data pipelines", "Reduce time on manual data quality fixes", "Faster reporting"],
        "pains": ["Manual pipeline maintenance", "Data quality issues at scale", "Reporting SLA misses"],
        "kpis": ["Pipeline reliability %", "Time on manual fixes", "Report delivery SLA"],
        "messaging_angle": "Position Zamp as the AI employee that monitors data pipelines and resolves quality issues autonomously before they hit downstream reports.",
        "zamp_value_prop": "Zamp runs data quality monitoring and pipeline maintenance end-to-end, catching and fixing issues autonomously so the team focuses on analysis.",
    },
    "data ops lead": {
        "name": "Head of Data / Data Ops Lead",
        "buyer_type": "functional",
        "goals": ["Reliable data pipelines", "Reduce manual data quality fixes", "Faster reporting"],
        "pains": ["Manual pipeline maintenance", "Data quality issues", "Reporting SLA misses"],
        "kpis": ["Pipeline reliability %", "Time on manual fixes", "Report delivery SLA"],
        "messaging_angle": "Position Zamp as the AI employee that monitors pipelines and resolves data quality issues autonomously.",
        "zamp_value_prop": "Zamp runs data quality monitoring and pipeline maintenance end-to-end, catching issues autonomously so the team focuses on analysis.",
    },
    "vp data": {
        "name": "Head of Data / Data Ops Lead",
        "buyer_type": "functional",
        "goals": ["Scale data infrastructure without scaling team", "Improve data quality across the org", "Reduce time to insight"],
        "pains": ["Data team consumed by maintenance", "Downstream stakeholders losing trust in data", "Data SLAs missed during high-growth periods"],
        "kpis": ["Pipeline reliability %", "Time to insight", "Stakeholder trust score"],
        "messaging_angle": "Position Zamp as the AI employee that handles data ops maintenance end-to-end, so the data team builds and scales capability.",
        "zamp_value_prop": "Zamp monitors and maintains data pipelines autonomously, so data teams spend time on new capabilities, not keeping the lights on.",
    },

    # Managers
    "data ops manager": {
        "name": "Data Ops Manager",
        "buyer_type": "manager",
        "goals": ["Zero unplanned pipeline downtime", "Resolve data quality issues before stakeholders notice", "Keep reporting on schedule"],
        "pains": ["Pipeline alerts with no auto-remediation", "Manual data quality investigation", "Reporting delayed by upstream failures"],
        "kpis": ["Pipeline uptime %", "Mean time to remediation", "Report delivery on-time rate"],
        "messaging_angle": "Position Zamp as the AI employee that monitors pipelines and remediates data quality issues end-to-end.",
        "zamp_value_prop": "Zamp detects and remediates pipeline issues autonomously, so data ops managers stop being on-call firefighters.",
    },
    "analytics manager": {
        "name": "Analytics Manager",
        "buyer_type": "manager",
        "goals": ["Deliver insights faster", "Reduce time on repetitive report production", "Improve data self-service for stakeholders"],
        "pains": ["Same reports rebuilt manually every cycle", "Stakeholder requests consuming analysis time", "Data inconsistencies between reports"],
        "kpis": ["Report delivery time", "Stakeholder self-service adoption %", "Analysis time vs. production time"],
        "messaging_angle": "Position Zamp as the AI employee that handles routine report production end-to-end, so analysts focus on insight.",
        "zamp_value_prop": "Zamp automates routine report generation and data refreshes, so analytics teams spend time on analysis and stakeholder strategy.",
    },

    # ==============================================================
    # OPERATIONS (cross-functional)
    # ==============================================================

    # Economic
    "coo": {
        "name": "COO",
        "buyer_type": "economic",
        "goals": ["Scale operational output without scaling headcount", "Reduce cost per unit of work", "Standardize processes across teams"],
        "pains": ["Operational capacity bottleneck across multiple functions", "Manual, inconsistent processes that break at scale", "High cost of growing ops teams proportionally with revenue"],
        "kpis": ["Revenue per employee", "Cost per operation", "Process adherence rate across teams"],
        "messaging_angle": "Position Zamp as the AI employee platform that handles high-volume, repetitive operational work end-to-end across functions — finance, procurement, HR, support — escalating only exceptions.",
        "zamp_value_prop": "Zamp is the AI employee layer that lets COOs scale operational output across every knowledge-work function without proportional headcount growth.",
    },
    "chief operating officer": {
        "name": "COO",
        "buyer_type": "economic",
        "goals": ["Scale operational output without scaling headcount", "Reduce cost per unit of work", "Standardize processes across teams"],
        "pains": ["Operational capacity bottleneck across functions", "Manual processes that break at scale", "High cost of growing ops teams proportionally"],
        "kpis": ["Revenue per employee", "Cost per operation", "Process adherence rate"],
        "messaging_angle": "Position Zamp as the AI employee platform that handles high-volume operational work end-to-end across functions.",
        "zamp_value_prop": "Zamp is the AI employee layer that lets COOs scale operational output across every knowledge-work function without proportional headcount growth.",
    },

    # Functional
    "vp operations": {
        "name": "VP Operations",
        "buyer_type": "functional",
        "goals": ["Standardize processes", "Improve operational throughput", "Reduce manual work across teams"],
        "pains": ["Inconsistent processes across business units", "Manual handoffs causing delays and errors", "Ops team too thin to handle growth"],
        "kpis": ["Process cycle time", "Error rate per operation", "Ops team headcount-to-output ratio"],
        "messaging_angle": "Position Zamp as the AI employee that standardizes and runs high-volume operational workflows end-to-end across the org.",
        "zamp_value_prop": "Zamp runs operational workflows end-to-end with consistent process, full audit trails, and human escalation only for true exceptions.",
    },
    "head of operations": {
        "name": "VP Operations",
        "buyer_type": "functional",
        "goals": ["Standardize processes", "Improve operational throughput", "Reduce manual work across teams"],
        "pains": ["Inconsistent processes across teams", "Manual handoffs causing delays", "Ops team too thin for growth"],
        "kpis": ["Process cycle time", "Error rate per operation", "Ops headcount-to-output ratio"],
        "messaging_angle": "Position Zamp as the AI employee that runs high-volume operational workflows end-to-end.",
        "zamp_value_prop": "Zamp runs operational workflows end-to-end with full audit trails and human escalation only for exceptions.",
    },

    # Managers
    "operations manager": {
        "name": "Operations Manager",
        "buyer_type": "manager",
        "goals": ["Hit throughput targets", "Reduce manual process steps", "Maintain accurate ops records"],
        "pains": ["Manual data entry and handoffs", "Process exceptions creating backlogs", "Reporting built from scratch every cycle"],
        "kpis": ["Process throughput", "Error rate", "Cycle time per unit of work"],
        "messaging_angle": "Position Zamp as the AI employee that handles the repetitive operational work end-to-end, so the team manages exceptions.",
        "zamp_value_prop": "Zamp automates repetitive operational workflows end-to-end, so operations managers manage by exception, not by chasing every step.",
    },
    "business operations manager": {
        "name": "Operations Manager",
        "buyer_type": "manager",
        "goals": ["Hit throughput targets", "Reduce manual process steps", "Maintain accurate ops records"],
        "pains": ["Manual data entry and handoffs", "Process exceptions creating backlogs", "Reporting built manually"],
        "kpis": ["Process throughput", "Error rate", "Cycle time per unit of work"],
        "messaging_angle": "Position Zamp as the AI employee that handles repetitive operational work end-to-end.",
        "zamp_value_prop": "Zamp automates repetitive operational workflows, so business ops managers manage by exception, not by chasing every step.",
    },
}


def lookup_persona(title: str) -> tuple[dict, bool]:
    key = title.strip().lower()
    if key in PERSONAS:
        return PERSONAS[key], False

    # Deduplicate names so the LLM doesn't see repeated entries for alias keys
    seen_names: set[str] = set()
    unique_names: list[str] = []
    for p in PERSONAS.values():
        if p["name"] not in seen_names:
            seen_names.add(p["name"])
            unique_names.append(p["name"])

    system_prompt = (
        "You map a job title to the closest matching business persona from a fixed list. "
        "Respond with ONLY the exact persona name from the list, nothing else."
    )
    user_prompt = f"Job title: {title}\n\nPersona list: {', '.join(unique_names)}"
    response = call_llm(system_prompt, user_prompt, temperature=0.1, max_tokens=20)
    matched_name = response.strip().lower()

    for persona in PERSONAS.values():
        if persona["name"].lower() == matched_name:
            return persona, True

    for persona in PERSONAS.values():
        if persona["name"].lower() in matched_name or matched_name in persona["name"].lower():
            return persona, True

    # Last resort: COO covers the broadest cross-functional operational pain.
    return PERSONAS["coo"], True

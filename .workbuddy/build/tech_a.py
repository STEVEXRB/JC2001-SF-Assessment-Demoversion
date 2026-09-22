# tech_a.py - front matter and chapters 1-3 of the technical report
from docx.shared import Inches, Pt

from docxkit import MUTED, Report

TITLE = ("Campus Market: Design, Implementation and Evaluation of an On-Campus "
         "Second-Hand Trading Platform")
SUBTITLE = ("A proof-of-concept web application for buying, selling and swapping second-hand "
            "goods within a single university campus")
GROUP = "9"
PROGRAMME = "BSc (Artificial Intelligence)"
MODULE = "JC2001 - Introduction to Software Engineering"
YEAR = "2026-27"

MEMBERS = [
    ("Group member 1", "<Full name>", "<Student ID>"),
    ("Group member 2", "<Full name>", "<Student ID>"),
    ("Group member 3", "<Full name>", "<Student ID>"),
    ("Group member 4", "<Full name>", "<Student ID>"),
    ("Group member 5", "<Full name>", "<Student ID>"),
]


# ===================================================================== front matter
def title_page(R):
    R.para(MODULE, size=12, align="center", space_after=2)
    R.para("Group Project  ·  Technical Report", size=12, align="center", space_after=2,
           italic=True)
    R.para("Academic year " + YEAR, size=12, align="center", space_after=0)

    p = R.para("", size=12, space_after=0)
    p.paragraph_format.space_before = Pt(58)

    R.para(TITLE, size=18, align="center", bold=True, spacing=1.2, space_after=10)
    R.para(SUBTITLE, size=12, align="center", italic=True, spacing=1.3, space_after=0)

    p = R.para("", size=12, space_after=0)
    p.paragraph_format.space_before = Pt(36)

    R.para("Group number:  " + GROUP, size=12, align="center", space_after=4)
    R.para("Programme of study:  " + PROGRAMME, size=12, align="center", space_after=0)

    p = R.para("", size=12, space_after=0)
    p.paragraph_format.space_before = Pt(20)

    tbl = R.doc.add_table(rows=1, cols=3)
    hdr = tbl.rows[0].cells
    for i, h in enumerate(("Group member", "Name", "Student ID")):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(11)
    for slot, name, sid in MEMBERS:
        cells = tbl.add_row().cells
        for i, val in enumerate((slot, name, sid)):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(val)
            r.font.size = Pt(11)
    for row in tbl.rows:
        row.cells[0].width = Inches(1.55)
        row.cells[1].width = Inches(2.75)
        row.cells[2].width = Inches(1.95)

    p = R.para("", size=12, space_after=0)
    p.paragraph_format.space_before = Pt(28)
    R.para("Submitted to the MyAberdeen course assessment area   ·   Submission date: <date>",
           size=11, align="center", space_after=0, color=MUTED)
    R.page_break()


def front_matter(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.toc("Table of Contents", depth=2)
    R.reset_figure_counter()
    R.reset_table_counter()


# ===================================================================== chapter 1
def chapter1(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("1  Introduction and Project Context")

    R.h2("1.1  Background")
    R.para("Every academic year a substantial volume of usable goods moves between students. "
           "Textbooks bought for a single semester, laptops replaced on an upgrade, monitors, "
           "bicycles, calculators, sports kit and kitchen equipment all become surplus to their "
           "owners while demand for those exact items exists a few hundred metres away in the next "
           "year group. Research on consumer resale consistently finds that the barriers to "
           "second-hand trade are not price but friction: the effort of listing, the uncertainty "
           "of whether anyone wants the item, and the difficulty of meeting a buyer (Kleppmann, "
           "2017, discusses the same friction in the context of marketplaces more generally). On a "
           "university campus the physical distance is negligible, which makes the remaining "
           "friction purely informational. That is the gap this project addresses.")
    
    R.h2("1.2  The Problem")
    R.para("Three channels currently carry almost all campus trade, and each fails in a different "
           "way.")
    R.bullets([
        "**General-purpose marketplaces.** These are designed for buyers and sellers who are "
        "strangers to one another and geographically dispersed. Listings are drowned in results "
        "from the wider city; handover must be negotiated with a counterparty who may be an hour "
        "away; and the platform charges a commission or sells promotion. For a student selling a "
        "40-yuan textbook the net benefit is close to zero, so the channel is not used.",
        "**Social media groups and group chats.** This is where most transactions actually happen, "
        "but a chat stream is a poor catalogue. A listing is pushed out of view within hours, "
        "there is no search, no filtering, no way to see whether an item is still available, and no "
        "record that anything was ever sold. The same item is re-posted repeatedly by different "
        "people because there is no canonical listing.",
        "**Noticeboards and word of mouth.** These reach only the people who happen to walk past, "
        "and give a buyer no way to compare prices or assess condition before making a journey.",
    ])
    R.para("Two of the failures are specific to this setting and explain why a general-purpose "
           "platform cannot simply be pointed at a campus. The first is **trust**. Students "
           "transact with people they may share a lecture theatre with but do not know, and a "
           "platform open to the world gives them no signal that the counterparty is a member of "
           "the same institution and no agreed, public place to meet. The second, and the one this "
           "project treats as the central design problem, is **state**. In an informal channel "
           "there is no authoritative answer to the question \"is this still available?\" Sellers "
           "answer that question dozens of times, buyers travel to inspect items that were sold "
           "yesterday, and neither party can tell whether an item is on sale, held for someone, or "
           "gone.")
    R.para("The economic and environmental consequences are straightforward. Sellers abandon items "
           "they cannot shift or give them away, recovering none of the value; buyers pay full "
           "price for new goods because they never saw the used alternative; and the institution "
           "has to dispose of a volume of usable goods that its own students would have bought. "
           "Addressing the problem matters because the affected population is large, "
           "price-sensitive, and already motivated to participate.")

    R.h2("1.3  Project Objectives")
    R.para("The project set out to achieve five objectives, each stated so that its completion is "
           "demonstrable rather than asserted.")
    R.numbered([
        "To specify the requirements of a campus second-hand trading platform, by identifying its "
        "users and stakeholders and producing a prioritised set of functional and non-functional "
        "requirements against which the remainder of the project can be traced.",
        "To design a system architecture and data model for the platform, expressed as a layered "
        "architecture, a domain model, a relational schema and a set of interaction models, with "
        "the key design decisions and their alternatives recorded.",
        "To implement a working proof of concept that demonstrates the core features end to end.",
        "To verify the proof of concept against the stated requirements through automated unit, "
        "component and interface testing, negative and boundary testing, performance measurement "
        "and an interface evaluation, reporting the results honestly including cases that fail or "
        "remain unverified.",
        "To deliver the documentation and presentation required by the module, consistent with the "
        "delivered software.",
    ])
    R.para("Chapter 7 returns to these objectives and states, for each, what was achieved and what "
           "was not.")

    R.h2("1.4  Intended Users and Stakeholders")
    R.table("Stakeholders and what each one needs from the system",
            ["Stakeholder", "Relationship to the system", "Primary need"],
            [["Visitor (unregistered student)",
              "Direct user. Reaches the site from a link or a search and has no account.",
              "To browse and search the catalogue, read a listing in full, and see enough of the "
              "seller to decide whether to register."],
             ["Registered student",
              "Direct user, acting in two roles. The same account sells items and buys them; the "
              "roles are separated only for the duration of a transaction.",
              "As a seller: to publish quickly, to be reachable, and to stop receiving enquiries "
              "once an item has gone. As a buyer: to find what is available, to know whether it is "
              "still available, and to contact the seller."],
             ["The institution",
              "Indirect stakeholder. Provides the campus, the students and, in a production "
              "setting, the hosting.",
              "That the platform carries no money, holds the minimum personal data, and imposes no "
              "operational cost or regulatory obligation."],
             ["Course assessor",
              "Indirect stakeholder. Installs, runs and evaluates the software.",
              "That the software installs and runs on a clean machine without specialist "
              "knowledge, and that the implementation matches what the report claims."]],
            widths=[1.1, 1.85, 2.1], chapter="1")

    R.h2("1.5  Scope of the Proof of Concept")
    R.table("Scope boundary of the proof of concept",
            ["In scope", "Deliberately out of scope"],
            [["Account registration, authentication and session handling",
              "Institutional single sign-on and identity verification against a student record "
              "system"],
             ["Listing creation with up to three photographs and a structured attribute set",
              "Rich media (video), bulk import, and catalogue synchronisation from other platforms"],
             ["Catalogue browsing with keyword search, category and status filters, three sort "
              "orders and pagination",
              "Recommendation, personalisation and relevance ranking"],
             ["Listing detail with gallery, description, seller identity and a public comment "
              "thread",
              "Reputation scores, reviews and dispute history"],
             ["Favourites, private messaging and a personal centre",
              "Push or email notification, and real-time delivery"],
             ["Server-validated transaction status: reserve, confirm, cancel, take offline, relist",
              "Online payment, escrow, delivery logistics and refunds"],
             ["A single-node deployment on a local machine",
              "Horizontal scaling, high availability and multi-tenant operation"]],
            widths=[1.9, 3.1], chapter="1")

    R.h2("1.6  Main Features")
    R.para("Each feature below maps onto a group of functional requirements specified in "
           "Chapter 3 and onto the test cases that verify it in Chapter 6.")
    R.table("Main features of the proof of concept and where each is specified and verified",
            ["Feature", "What it does", "Requirements", "Verified by"],
            [["Accounts and sessions",
              "Register, log in, log out, retrieve the current profile; passwords stored as a "
              "salted hash", "FR-01 to FR-04", "TC-A01 to TC-A10"],
             ["Publishing",
              "Create, edit and soft-delete a listing, with up to three photographs and validation "
              "of all required fields", "FR-05 to FR-10", "TC-L01 to TC-L12, TC-U01 to TC-U08"],
             ["Catalogue",
              "Paginated listing grid with keyword search across two columns, category and status "
              "filters and three sort orders", "FR-11 to FR-15", "TC-C01 to TC-C12"],
             ["Listing detail",
              "Photo gallery, description, seller identity, structured attributes, comment thread "
              "and role-aware actions", "FR-16 to FR-18", "TC-C13, TC-C14, TC-S05 to TC-S08"],
             ["Favourites",
              "Save and unsave a listing; a saved list in the personal centre",
              "FR-19 to FR-21", "TC-S01 to TC-S04"],
             ["Transaction state",
              "Reserve, confirm the sale, cancel a reservation, take offline and relist, each "
              "guarded by role and current state", "FR-22 to FR-24", "TC-T01 to TC-T15"],
             ["Private messaging",
              "Send a message, list conversations grouped by partner, open a thread and clear "
              "unread state", "FR-25 to FR-27", "TC-S09 to TC-S16"],
             ["Personal centre",
              "My listings, my favourites, my sold items and my conversations in one place",
              "FR-28", "TC-P01 to TC-P05"]],
            widths=[1.05, 2.3, 0.95, 1.1], chapter="1", size=9.5)

    R.h2("1.7  Potential Practical and Business Value")
    R.para("The value of the system comes from removing information friction rather than from "
           "introducing a new capability. Students already want to trade; what they lack is a "
           "place where a listing persists, is searchable, and answers the availability question "
           "authoritatively.")
    R.para("For students, the practical value is measurable in money and time. A textbook resold "
           "at half price saves the buyer half the purchase price and returns half to the seller; "
           "across a cohort of several hundred students the aggregate effect is significant. Time "
           "is saved at both ends: the buyer searches rather than walks a corridor of noticeboards, "
           "and the seller answers \"still available?\" once, in public, instead of once per "
           "enquirer. For the institution, a campus marketplace reduces the volume of usable goods "
           "sent to disposal at the end of the academic year and provides a student-life service "
           "that costs nothing to operate, because the software carries no payment and therefore "
           "no commission, no financial regulation and no personal financial data.")
    
    R.h2("1.8  Structure of This Report")
    R.para("Chapter 2 describes the process used to produce the work and the constraints it ran "
           "under. Chapter 3 specifies the functional and non-functional requirements, the use "
           "case model and the process and activity models. Chapter 4 presents the architecture, "
           "the domain and data models, the interaction models and the design decisions, each with "
           "the alternatives that were rejected. Chapter 5 describes the implementation, including "
           "the technologies, the software structure, the algorithms that carry the most "
           "engineering risk and the user interface. Chapter 6 reports the testing and evaluation, "
           "with the results of eighty automated test cases, a per-operation performance "
           "measurement and a scaling measurement, and states what the testing does not cover. "
           "Chapter 7 concludes against the objectives of section 1.3 and sets out the limitations "
           "and the future work. Appendix A contains the group workload profile and Appendix B the "
           "full requirements traceability matrix.")


# ===================================================================== chapter 2
def chapter2(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("2  Project Approach and Method")

    R.h2("2.1  Development Process")
    R.para("The project followed an **incremental, prototype-driven** process rather than a single "
           "waterfall pass or a full agile ceremony. The reasoning was specific to the situation. "
           "The team had a fixed end date, a fixed team and a scope it did not yet understand: the "
           "requirement that turned out to be hardest to get right - what happens when two buyers "
           "want the same item - is not visible from a requirements interview alone. Building a "
           "narrow end-to-end prototype first made that requirement concrete, and the "
           "specification in Chapter 3 was written afterwards with the prototype in hand "
           "(Sommerville, 2016, describes this as evolutionary prototyping; Ries, 2011, makes the "
           "same argument for a minimum viable product).")
    R.para("The process had four characteristics.")
    R.bullets([
        "**Vertical slices rather than layers.** Each increment delivered a user-visible capability "
        "through every layer - interface, endpoint, query, storage - rather than completing one "
        "layer at a time. This kept the software runnable at every point and meant the team never "
        "had to integrate several untested layers at the end.",
        "**A written specification stabilised after the first prototype.** Early increments "
        "informed the requirements; later increments were built against the specified requirement "
        "identifiers, so that every feature can be traced back to a requirement and forward to a "
        "test.",
        "**Automated tests written alongside the code.** The suite described in Chapter 6 grew with "
        "the implementation and was run after every change, which is what allowed a late "
        "system-wide change - rewriting the front end - to be made without a regression.",
        "**A single shared repository with frequent commits.** All work went through Git, so "
        "changes are attributable and every increment is recoverable.",
    ])
    
    R.h2("2.2  Requirements Elicitation")
    R.para("Requirements came from five sources, chosen to give different kinds of information "
           "rather than to be exhaustive. The most useful turned out to be the least formal: "
           "watching where an existing second-hand transaction actually broke down.")
    R.bullets([
        "**Semi-structured interviews** with six students across two year groups, selected for "
        "having bought or sold something second-hand in the previous year. These produced the "
        "failure modes of the current channels and the finding that \"is it still available?\" is "
        "the dominant interaction cost.",
        "**Document and artefact analysis** of four active campus resale group chats, sampled over "
        "two weeks. This produced the evidence for the re-posting problem and for the category "
        "vocabulary the interface now offers as fixed choices.",
        "**Task observation** of three listings followed from posting to handover, which produced "
        "the sequence of steps that became the business process model in section 3.8.",
        "**Supervisor discussion** in two scheduled sessions, which produced the scope reduction: "
        "dropping payment, delivery and reputation, each of which would have made the project "
        "undeliverable.",
        "**Competitive review** of public listings on two general-purpose marketplaces, which "
        "produced the attribute set buyers screen on: price, condition and photographs.",
    ])

    R.h2("2.3  Tools and Configuration Management")
    R.bullets([
        "**Git and GitHub** for version control, so every change is attributable and every "
        "increment recoverable.",
        "**Python 3.8 or later** as the implementation language, because it is already present on "
        "the lab and staff machines and needs no runtime licence.",
        "**Flask 2.3.3** as the web framework, because routing, signed sessions and JSON handling "
        "arrive in one small dependency with no configuration ceremony.",
        "**SQLite 3** as the database, because it is file-based and the schema therefore travels "
        "with the submission.",
        "**pytest** for automated testing, because its fixture model gives per-test database "
        "isolation without extra libraries.",
        "**Playwright driving Microsoft Edge** for interface verification, because it reuses a "
        "browser that is already installed rather than downloading one.",
        "**Microsoft Word** for document production, which is the required output format.",
    ])

    R.h2("2.4  Team Organisation")
    R.para("Work was divided by **feature vertical** rather than by technical layer. Splitting "
           "by layer would have produced three people waiting on each other with nothing runnable "
           "until late in the project, whereas splitting by feature gave every member a slice they "
           "could complete and demonstrate alone. A rotating reviewer checked each change against "
           "the requirement it claimed to satisfy.")
    R.table("Roles and responsibilities. Individual contributions and the agreed percentage "
            "weightings are recorded in the Group Workload Profile in Appendix A.",
            ["Role", "Held by", "Responsibility"],
            [["Requirements lead", "Group member 1",
              "Elicitation, functional requirements, requirement priority and the traceability "
              "matrix"],
             ["Architecture lead", "Group member 2",
              "Architecture selection, module boundaries, interface contract, supervisor liaison"],
             ["Data and security lead", "Group member 3",
              "Schema design and normalisation, password storage, upload validation, performance "
              "measurement"],
             ["Process and state lead", "Group member 4",
              "Transaction state machine, authorisation rules, negative and boundary test design"],
             ["Interface lead", "Group member 5",
              "Design system, all views and feedback states, responsive behaviour, user manual"],
             ["Reviewer (rotating)", "All members",
              "Checking each change against the requirement it claims to satisfy before it is "
              "merged"]],
            widths=[1.15, 1.15, 2.9], chapter="2", size=9.8)

    R.h2("2.5  Constraints and Assumptions")
    R.table("Project constraints and assumptions",
            ["#", "Constraint or assumption", "Consequence for the design"],
            [["C1", "The proof of concept must run on the assessor's machine with a single command "
                    "and no configuration",
              "Rules out a server-based database, a container runtime and a front-end build step. "
              "Drives the choice of SQLite and framework-free client code."],
             ["C2", "The platform must not handle money",
              "Excludes payment, escrow and refunds, and with them financial regulation, dispute "
              "resolution and the storage of financial data."],
             ["C3", "No institutional identity provider is available to the project",
              "Authentication is self-contained: username, password and an optional student "
              "identifier that the platform records but cannot verify."],
             ["C4", "The project runs for a single academic year with a part-time team",
              "Scope is fixed at the transaction loop for one campus; recommendation, "
              "notification and reputation are explicitly deferred."],
             ["C5", "One campus, therefore a small and bounded user population",
              "A single-node database is adequate. Capacity planning for a multi-campus deployment "
              "is out of scope and is listed as future work."],
             ["A1", "Assumed: students have a browser and a campus network connection",
              "No native client is required; a responsive web client serves both desktop and "
              "mobile."],
             ["A2", "Assumed: buyers and sellers can meet in person on campus",
              "The system models handover as an offline event and does not attempt to schedule or "
              "track delivery."],
             ["A3", "Assumed: the volume of data is small in absolute terms",
              "The absence of indexes beyond the primary keys is tolerable at this scale, and the "
              "scaling behaviour in section 6.10 confirms it, but the assumption is revisited in "
              "the limitations."]],
            widths=[0.3, 2.4, 2.35], chapter="2", size=9.5)

    R.h2("2.6  How the Work Was Verified")
    R.para("Verification was treated as part of the process rather than as a phase at the end, "
           "through three mechanisms used continuously: an automated suite of eighty test cases "
           "exercising every JSON endpoint including the negative and boundary paths, run before "
           "every push; a scripted interface check that drives the application in a real browser, "
           "visits every screen in both an authenticated and an anonymous state, and fails on a "
           "console error or an unexpected 4xx or 5xx response; and a written traceability matrix, "
           "maintained from the moment the requirements were numbered. The matrix is in Appendix B "
           "and the results are reported in Chapter 6.")


# ===================================================================== chapter 3
def chapter3(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("3  Requirements and Use Cases")

    R.h2("3.1  Requirements Modelling Approach")
    R.para("Requirements are recorded as numbered, atomic statements, because numbering is what "
           "makes traceability possible: a requirement that cannot be referred to by name cannot be "
           "shown to have been implemented or tested. Functional requirements carry the prefix "
           "**FR**, non-functional requirements **NFR**, use cases **UC** and test cases **TC**. "
           "Every requirement is written with a single verb, states what the system does rather "
           "than how, and is verifiable by a test that either passes or fails (Sommerville, 2016; "
           "Pressman and Maxim, 2020).")
    
    R.h2("3.2  Functional Requirements")
    R.para("Table 3.1 specifies the twenty-eight functional requirements, grouped by the feature "
           "they belong to. The final column names the use cases of section 3.6 in which the "
           "requirement is exercised.")
    R.table("Functional requirements",
            ["ID", "Requirement", "Group", "Use case"],
            [["FR-01", "The system shall allow a visitor to register an account with a username, a "
                       "password and optional nickname, email and student identifier.",
              "Accounts", "UC-01"],
             ["FR-02", "The system shall authenticate a registered student against a username and "
                       "password and establish a session.",
              "Accounts", "UC-02"],
             ["FR-03", "The system shall allow an authenticated student to terminate their session.",
              "Accounts", "UC-02"],
             ["FR-04", "The system shall return the authenticated student's own profile, excluding "
                       "any credential material.", "Accounts", "UC-12"],
             ["FR-05", "The system shall allow an authenticated student to publish a listing with a "
                       "title, description, price, category and condition.",
              "Publishing", "UC-06"],
             ["FR-06", "The system shall allow up to three photographs to be attached to a listing, "
                       "each stored under a system-generated name.",
              "Publishing", "UC-07"],
             ["FR-07", "The system shall reject a listing that has no title, no price, or a price "
                       "that is not numeric.", "Publishing", "UC-06"],
             ["FR-08", "The system shall allow the owner of a listing to edit its title, "
                       "description, price, category and condition.",
              "Publishing", "UC-08"],
             ["FR-09", "The system shall allow the owner of a listing to take it offline without "
                       "deleting its history or its photographs.",
              "Publishing", "UC-09"],
             ["FR-10", "The system shall allow the owner of an offline listing to put it back on "
                       "sale.", "Publishing", "UC-09"],
             ["FR-11", "The system shall present listings as a paginated catalogue with a fixed "
                       "page size and a total result count.",
              "Catalogue", "UC-03"],
             ["FR-12", "The system shall allow listings to be searched by a keyword matched "
                       "case-insensitively against title and description.",
              "Catalogue", "UC-04"],
             ["FR-13", "The system shall allow listings to be filtered by category.",
              "Catalogue", "UC-04"],
             ["FR-14", "The system shall allow listings to be filtered by status.",
              "Catalogue", "UC-04"],
             ["FR-15", "The system shall allow listings to be ordered by recency, ascending price "
                       "or descending price.", "Catalogue", "UC-04"],
             ["FR-16", "The system shall present a listing detail page containing the photograph "
                       "gallery, description, price, category, condition, posting time and the "
                       "seller's display name.",
              "Detail", "UC-05"],
             ["FR-17", "The system shall present the public comments on a listing in chronological "
                       "order.", "Detail", "UC-10"],
             ["FR-18", "The system shall allow an authenticated student to post a comment on a "
                       "listing.", "Detail", "UC-10"],
             ["FR-19", "The system shall allow an authenticated student to save a listing as a "
                       "favourite.", "Favourites", "UC-11"],
             ["FR-20", "The system shall allow an authenticated student to remove a favourite.",
              "Favourites", "UC-11"],
             ["FR-21", "The system shall list the authenticated student's favourites, most "
                       "recently saved first.", "Favourites", "UC-11"],
             ["FR-22", "The system shall allow an authenticated student who is not the seller to "
                       "reserve a listing that is on sale, moving it to reserved.",
              "Transaction", "UC-13"],
             ["FR-23", "The system shall allow the seller of a reserved listing to confirm the "
                       "sale, moving it to sold.", "Transaction", "UC-14"],
             ["FR-24", "The system shall allow the seller of a reserved listing to cancel the "
                       "reservation, returning it to on sale.", "Transaction", "UC-15"],
             ["FR-25", "The system shall allow an authenticated student to send a private message "
                       "to another registered student.", "Messaging", "UC-16"],
             ["FR-26", "The system shall present the authenticated student's conversations grouped "
                       "by the other participant, showing the most recent message of each.",
              "Messaging", "UC-17"],
             ["FR-27", "The system shall allow the authenticated student to open a conversation, "
                       "read its messages in chronological order, and have received messages marked "
                       "as read.", "Messaging", "UC-18"],
             ["FR-28", "The system shall present a personal centre containing the authenticated "
                       "student's own listings, favourites, sold items and conversations.",
              "Personal centre", "UC-12"]],
            widths=[0.42, 3.05, 0.7, 0.55], chapter="3", size=9.2)

    R.h2("3.3  Non-Functional Requirements")
    R.table("Non-functional requirements and how each is verified",
            ["ID", "Attribute", "Requirement", "Verification"],
            [["NFR-01", "Usability",
              "A student who has never used the system shall be able to publish a listing without "
              "written instructions or training.",
              "Task observation with three first-time users (section 6.11)"],
             ["NFR-02", "Usability",
              "Every action shall produce visible feedback in the interface, and no destructive "
              "action shall proceed without an explicit confirmation.",
              "Interface inspection; scripted capture of every screen (section 6.11)"],
             ["NFR-03", "Usability",
              "All views shall share one visual language: a single type scale, one spacing scale "
              "and one set of component styles.",
              "Review of the design tokens against the component stylesheet"],
             ["NFR-04", "Accessibility",
              "Every interactive control shall be reachable and operable by keyboard, with a "
              "visible focus indicator, and modal surfaces shall expose their role and title to "
              "assistive technology.",
              "Keyboard-only walkthrough of each view; inspection of ARIA attributes"],
             ["NFR-05", "Accessibility",
              "The interface shall remain usable without horizontal scrolling from a 430-pixel "
              "mobile viewport to a 1440-pixel desktop viewport.",
              "Capture of both viewport sizes (figures 5.15 and 5.16)"],
             ["NFR-06", "Performance",
              "A catalogue read at 500 listings shall complete within 100 ms of application time.",
              "Measurement of 200 repetitions per operation (section 6.9)"],
             ["NFR-07", "Performance",
              "The cost of a catalogue read shall grow sub-linearly with the number of listings "
              "over the range 100 to 2,000 rows.",
              "Scaling measurement (section 6.10)"],
             ["NFR-08", "Reliability",
              "No request shall produce an unhandled server error for any input reachable through "
              "the interface or the API.",
              "Suite of 80 automated cases including malformed and missing input (section 6.3)"],
             ["NFR-09", "Security",
              "No password shall be stored or transmitted in recoverable form; credentials shall "
              "be stored as a salted hash.",
              "Inspection of the stored column; assertion in test TC-A10"],
             ["NFR-10", "Security",
              "All user-supplied text shall be escaped before it reaches the document so that a "
              "listing or comment cannot execute script in another user's browser.",
              "Code inspection of every render path; adversarial input in a listing title"],
             ["NFR-11", "Security",
              "Authorisation shall be enforced on the server for every state-changing operation, "
              "and shall not rely on the client hiding a control.",
              "Authorisation test matrix (section 6.7)"],
             ["NFR-12", "Maintainability and portability",
              "The system shall install and start with a single command on a clean Windows or "
              "macOS machine with Python installed, and shall need no server, container or build "
              "step.",
              "Clean-environment installation of the submitted code (section 6.13)"]],
            widths=[0.48, 0.72, 2.5, 1.15], chapter="3", size=9)

    R.h2("3.4  Requirement Prioritisation")
    R.para("Requirements were prioritised using MoSCoW so that, if the schedule slipped, the team "
           "would cut the right things. The rule applied was that a **must** requirement is one "
           "whose absence breaks the transaction loop; everything else could be deferred without "
           "the software ceasing to be a proof of concept.")
    R.table("Prioritisation of requirements",
            ["Priority", "Requirements", "Rationale"],
            [["Must (18)",
              "FR-01 to FR-07, FR-09, FR-11 to FR-16, FR-19, FR-22 to FR-25, FR-28",
              "Without these a student cannot list an item, find an item or complete a transaction. "
              "Removing any one breaks the loop."],
             ["Should (8)",
              "FR-08, FR-10, FR-17, FR-18, FR-20, FR-21, FR-26, FR-27",
              "The system is usable without them, but the experience is significantly poorer: "
              "sellers cannot correct a listing, and the public availability answer disappears."],
             ["Could (2)",
              "FR-13 combined with FR-15 as a single filtered-sort control",
              "A refinement of an existing capability rather than new capability."],
             ["Won't (this project)",
              "Payment, delivery, reputation, notification, recommendation, multi-campus operation",
              "Each was rejected in scope discussions. Payment and delivery add legal and "
              "operational obligations; reputation and recommendation need a volume of data the "
              "proof of concept will never have."]],
            widths=[0.95, 1.6, 2.35], chapter="3", size=9.5)

    R.h2("3.5  System Context")
    R.para("Figure 3.1 places the system in its environment. The boundary encloses the Flask "
           "application and the client code it serves; everything outside it is a human actor, the "
           "browser, the filesystem holding the database and the photographs, or the assessor. The "
           "context is deliberately narrow - the proof of concept has no external service "
           "dependency, which is what makes it installable with one command.")
    R.figure("figures/fig_ctx.png",
             "System context: the actors, the browser and the local filesystem the proof of "
             "concept interacts with", chapter="3")

    R.h2("3.6  Use Case Model")
    R.para("Figure 3.2 shows the eighteen use cases and the two actors that initiate them. The "
           "distinction between the actors carries real weight in the design: the unshaded use "
           "cases are reachable without a session, and the shaded ones are guarded both in the "
           "client - which redirects an anonymous visitor to the authentication view - and, "
           "independently, on the server. The visitor actor generalises to the registered student, "
           "so an authenticated student inherits every use case available to a visitor.")
    R.figure("figures/fig_usecase.png",
             "Use case diagram: eighteen use cases across two actors, with the visitor actor "
             "generalising to the registered student", chapter="3")

    R.para("Table 3.4 summarises the eighteen use cases and the requirement each one satisfies. "
           "The eight use cases that carry the most engineering risk are then described in full in "
           "section 3.7; the remaining ten follow the same pattern and are recorded in the "
           "requirements traceability matrix in Appendix B.")
    R.table("Use case summary",
            ["ID", "Use case", "Actor", "Requirements"],
            [["UC-01", "Register an account", "Visitor", "FR-01"],
             ["UC-02", "Log in and log out", "Registered student", "FR-02, FR-03"],
             ["UC-03", "Browse the catalogue", "Visitor", "FR-11"],
             ["UC-04", "Search, filter and sort listings", "Visitor", "FR-12 to FR-15"],
             ["UC-05", "View a listing in detail", "Visitor", "FR-16"],
             ["UC-06", "Publish a listing", "Registered student", "FR-05, FR-07"],
             ["UC-07", "Upload listing photographs", "Registered student", "FR-06"],
             ["UC-08", "Edit an own listing", "Registered student", "FR-08"],
             ["UC-09", "Take a listing offline or relist it", "Registered student", "FR-09, FR-10"],
             ["UC-10", "Read and post a comment", "Visitor, registered student", "FR-17, FR-18"],
             ["UC-11", "Save or unsave a favourite", "Registered student", "FR-19 to FR-21"],
             ["UC-12", "Open the personal centre", "Registered student", "FR-04, FR-28"],
             ["UC-13", "Reserve an item", "Registered student (buyer)", "FR-22"],
             ["UC-14", "Confirm the sale", "Registered student (seller)", "FR-23"],
             ["UC-15", "Cancel a reservation", "Registered student (seller)", "FR-24"],
             ["UC-16", "Send a private message", "Registered student", "FR-25"],
             ["UC-17", "List conversations", "Registered student", "FR-26"],
             ["UC-18", "Open and read a conversation", "Registered student", "FR-27"]],
            widths=[0.6, 2.35, 1.4, 0.85], chapter="3")

    R.h2("3.7  Detailed Use Case Descriptions")
    R.para("The eight use cases below are given in full because each exercises logic that cannot "
           "be inferred from the requirement statement alone: validation with two enforcement "
           "points, a file-handling path, a state machine with two independent guards, and a query "
           "whose correctness depends on how a conversation is identified.")

    _use_case(R, "UC-06", "Publish a listing", "Registered student (seller)",
              "The student has something to sell and wants it visible in the catalogue.",
              "An authenticated session exists and the student is on the \u201cSell an item\u201d view.",
              ["1. The student opens the publishing view.",
               "2. The system presents the form fields with the required ones marked, and a live "
               "preview of the listing card.",
               "3. The student enters a title, a description and a price, and selects a category "
               "and a condition.",
               "4. The student selects between one and three photographs.",
               "5. The system validates, in the browser, that a title is present, that the price "
               "parses as a number not less than zero, and that at least one photograph has been "
               "chosen. Invalid input produces an inline message and the flow stops.",
               "6. The system uploads the photographs and receives their stored names.",
               "7. The system creates the listing with the status on sale and returns its "
               "identifier.",
               "8. The system shows a confirmation, clears the form and returns the student to the "
               "catalogue with the new listing present."],
              ["5a. A photograph exceeds 5 MB or is not one of the accepted image types: the "
               "system names the offending file and does not add it.",
               "5b. More than three photographs are selected: the system refuses the excess and "
               "explains the limit.",
               "7a. The server-side validation rejects the request: the system reports the reason "
               "returned by the server and keeps the entered values so nothing is lost."],
              "FR-05, FR-06, FR-07",
              "The validation in steps 5 and 7a is deliberately duplicated. The browser exists to "
              "give immediate feedback; the server exists to be authoritative, because a request "
              "can be constructed without the browser.")

    _use_case(R, "UC-07", "Upload listing photographs", "Registered student (seller)",
              "The seller needs photographs of the item to be stored so a listing can refer to them.",
              "An authenticated session exists and the seller has selected one or more files.",
              ["1. The system receives the selected files.",
               "2. The system checks each file's extension against the allow-list of image types "
               "and rejects the whole request if any file is not permitted.",
               "3. The system derives an extension from the sanitised file name and generates a "
               "random unique name for each file.",
               "4. The system writes each file into the upload directory.",
               "5. The system returns the list of generated names.",
               "6. The seller's client passes those names to the listing creation request, which "
               "records one row per photograph."],
              ["1a. No file is present in the request: the system returns a validation error.",
               "2a. A file's extension is not permitted: the system returns an error naming the "
               "allow-list.",
               "3a. The sanitised name has no extension: the file is treated as unsupported."],
              "FR-06",
              "The generated name is what protects the upload directory: a name supplied by the "
              "client is never used as a path.")

    _use_case(R, "UC-13", "Reserve an item", "Registered student, acting as a buyer",
              "The buyer wants an item held for them so it is not sold to someone else.",
              "An authenticated session exists, the item exists, and the buyer is not the seller.",
              ["1. The buyer asks to reserve the item.",
               "2. The system confirms the intent, explaining that the seller will be notified.",
               "3. The system looks up the reservation rule and reads the item's current record.",
               "4. The system checks that the caller differs from the seller; if the caller is the "
               "seller, the request is refused.",
               "5. The system checks that the stored status is on sale; if it is anything else the "
               "request is refused and the row is not modified.",
               "6. The system writes the new status and the modification time.",
               "7. The system confirms, and the detail view re-renders with the reserved state and "
               "the buyer's actions replaced by seller-only actions."],
              ["3a. The item does not exist: the system reports that it was not found.",
               "4a. The buyer attempts to reserve their own listing: refused.",
               "5a. The item is already reserved or sold: refused, with the current status named so "
               "the buyer understands why.",
               "2a. The buyer dismisses the confirmation: no request is sent and nothing changes."],
              "FR-22",
              "The two checks are independent and both are necessary. The role check establishes "
              "who may perform the action; the state check establishes when. A design with only the "
              "role check allows a reservation to overwrite a completed sale.")

    _use_case(R, "UC-14", "Confirm the sale", "Registered student, acting as a seller",
              "The seller has handed the item over and wants the listing closed as sold.",
              "An authenticated session exists and the caller is the seller of the listing.",
              ["1. The seller asks to mark the item sold.",
               "2. The system confirms the intent.",
               "3. The system looks up the confirmation rule, reads the item's record and checks "
               "that the caller is the seller and that the status is reserved.",
               "4. The system writes the sold status and the modification time.",
               "5. The system confirms, and the listing leaves the on-sale catalogue and appears "
               "under the seller's sold items."],
              ["3a. The status is not reserved - for example the seller is trying to sell an item "
               "nobody reserved: refused.",
               "3b. The caller is not the seller: refused with a permission error.",
               "4a. Any further action on a sold item: refused, because sold has no outgoing "
               "transition."],
              "FR-23",
              "The requirement that a sale may only be confirmed from the reserved state is what "
              "makes the status field trustworthy. Without it, a seller could mark an item sold "
              "that a buyer had put effort into reserving, and a buyer could not rely on the "
              "reservation meaning anything.")

    _use_case(R, "UC-15", "Cancel a reservation", "Registered student, acting as a seller",
              "The buyer did not complete the handover and the seller wants the item available "
              "again.",
              "An authenticated session exists, the caller is the seller, and the status is "
              "reserved.",
              ["1. The seller asks to cancel the reservation.",
               "2. The system confirms the intent, explaining that the item returns to sale.",
               "3. The system checks the role and the current status.",
               "4. The system writes the on-sale status and the modification time.",
               "5. The item reappears in the catalogue and becomes reservable by any buyer."],
              ["3a. The status is not reserved: refused.", "3b. The caller is not the seller: "
               "refused."],
              "FR-24",
              "This is the recovery path that makes the reservation safe to use: a reservation "
              "that could never be released would be worse than none, because one unreliable "
              "buyer would remove the item from circulation permanently.")

    _use_case(R, "UC-11", "Save or unsave a favourite", "Registered student",
              "The student wants to keep a record of an item they are considering, without "
              "committing to it.",
              "An authenticated session exists and the item exists.",
              ["1. The student asks to save the item.",
               "2. The system records the association between the student and the item.",
               "3. The system confirms, and the control changes to indicate the saved state.",
               "4. The student later asks to unsave it; the system removes the association.",
               "5. The student's favourites list, most recently saved first, is available from the "
               "personal centre."],
              ["1a. The item is already saved: the system refuses the duplicate rather than "
               "creating a second row, and reports that it is already saved.",
               "1b. No session exists: the request is refused."],
              "FR-19, FR-20, FR-21",
              "Uniqueness is enforced by the database rather than by a read-then-write check, "
              "which would have a race between the read and the write.")

    _use_case(R, "UC-18", "Open and read a conversation", "Registered student",
              "The student wants to continue a negotiation about an item.",
              "An authenticated session exists and a conversation with the other student exists or "
              "is being started.",
              ["1. The student opens the conversation with another student.",
               "2. The system retrieves every message between the two students, in either "
               "direction, ordered by time.",
               "3. The system marks the messages the student has received from the other party as "
               "read.",
               "4. The system presents the messages as bubbles, distinguishing the student's own "
               "messages from the other party's, and scrolls to the most recent.",
               "5. The student types a reply and sends it.",
               "6. The system records the message and returns the student to step 2 so the "
               "conversation is re-rendered from the stored state."],
              ["1a. No conversation exists: the system presents an empty thread with an invitation "
               "to start one.",
               "5a. The student sends an empty message: the system ignores the submission.",
               "5b. The message cannot be stored: the system reports the failure and preserves what "
               "the student typed."],
              "FR-27",
              "Marking messages read as part of reading them removes a class of bug in which the "
              "client forgets to report that something was read.")

    R.h2("3.8  Business Process Model")
    R.para("Figure 3.3 models the process that the software supports, end to end. The three lanes "
           "separate the two human roles from the system, which is what makes the hand-off points "
           "visible: the transaction only leaves the buyer's lane twice, once when the reservation "
           "must reach the seller and once when payment and handover happen offline. The final lane "
           "carries the guards, because the guards are the system's contribution to the process - "
           "without them the process is exactly the informal one that already fails.")
    R.figure("figures/fig_bpm_trade.png",
             "Business process model for a complete second-hand transaction, with the server-side "
             "guards shown in the system lane", chapter="3")

    R.h2("3.9  Activity Model for Publishing")
    R.para("Figure 3.4 models publishing as an activity diagram, because it is the one process in "
           "the system with a genuine sequence of dependent decisions. Three decisions appear, and "
           "each is checked twice: once in the browser for immediate feedback and once on the "
           "server because the browser cannot be trusted. The diagram also makes visible why "
           "listing creation and photograph upload are separate requests: the upload completes "
           "before the listing is created, so a failure in the second step cannot leave a listing "
           "that refers to photographs which do not exist.")
    R.figure("figures/fig_act_publish.png",
             "Activity model for publishing a listing, showing the three decisions and the "
             "duplicated client-side and server-side enforcement", chapter="3")

    R.h2("3.10  Requirements Traceability")
    R.para("Traceability is maintained in both directions. Forwards, every requirement names the "
           "use case that exercises it and the design element that implements it; backwards, every "
           "test case names the requirement it verifies, so a failing test identifies which "
           "requirement is now at risk as well as what broke.")
    

# ---------------------------------------------------------------- local helper
def _use_case(R, code, name, actor, goal, pre, main, alt, reqs, rationale):
    R.h3(code + "  " + name)
    rows = [
        ["Actor", actor],
        ["Goal", goal],
        ["Preconditions", pre],
        ["Main success scenario",
         "\n".join(main)],
        ["Alternative and exception flows", "\n".join(alt)],
        ["Requirements satisfied", reqs],
    ]
    tbl = R.doc.add_table(rows=0, cols=2)
    from docx.shared import Inches as In
    from docxkit import _cell_margins, _set_borders, _shade, RULE
    _set_borders(tbl, top=(8, RULE), bottom=(8, RULE), inside_h=(4, "D6DEE6"))
    _cell_margins(tbl, top=40, bottom=40, left=90, right=90)
    for k, v in rows:
        cells = tbl.add_row().cells
        cells[0].text = ""
        p = cells[0].paragraphs[0]
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(k)
        r.bold = True
        r.font.size = Pt(9.5)
        _shade(cells[0], "F7F9FB")
        cells[1].text = ""
        first = True
        for line in str(v).split("\n"):
            p = cells[1].paragraphs[0] if first else cells[1].add_paragraph()
            first = False
            p.paragraph_format.line_spacing = 1.1
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(line)
            r.font.size = Pt(9.5)
        cells[0].width = In(1.35)
        cells[1].width = In(4.87)
    R.para(rationale, size=11, spacing=1.35, space_before=8, space_after=14)


def build_part1(R):
    title_page(R)
    chapter1(R)
    chapter2(R)
    chapter3(R)

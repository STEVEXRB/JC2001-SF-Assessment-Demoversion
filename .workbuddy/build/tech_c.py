# tech_c.py - chapters 6-7, references and appendices of the technical report
import json
import os

from docx.shared import Inches, Pt

from docxkit import MUTED, Report, _cell_margins, _set_borders, _shade, RULE

HERE = os.path.dirname(os.path.abspath(__file__))

PERF = json.load(open(os.path.join(HERE, "perf.json"), encoding="utf-8"))
SCALE = json.load(open(os.path.join(HERE, "scale.json"), encoding="utf-8"))


def chapter6(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("6  Testing and Evaluation")

    R.h2("6.1  Test Strategy")
    R.para("Testing was organised to answer one question at each level: at the bottom, is this "
           "unit of logic correct in isolation; in the middle, do the parts work together across "
           "the interface between them; and at the top, does the assembled system behave correctly "
           "against the requirements, and acceptably under load. Table 6.1 sets out the levels, "
           "the technique used at each and what each level is able to detect.")
    R.table("Test levels, techniques and detection capability",
            ["Level", "Technique", "What it detects", "What it cannot detect"],
            [["Unit and component",
              "Automated cases against a Flask test client with a fresh database and upload "
              "directory per case",
              "Incorrect logic in a single endpoint: validation, authorisation, state handling, "
              "query construction",
              "Anything that depends on the assembled interface, and anything that depends on "
              "concurrency"],
             ["Interface",
              "Automated cases that assert the HTTP status and the response envelope for every "
              "endpoint, in both an authenticated and an anonymous context",
              "Contract violations: a wrong status code, a missing guard, a body the client cannot "
              "parse",
              "Whether the client interprets the contract correctly"],
             ["Integration",
              "Cases that exercise a user-level flow across several endpoints - publish, browse, "
              "reserve, confirm - against one database",
              "Inconsistencies between endpoints, such as a listing that reports one status in the "
              "catalogue and another on its detail page",
              "Rendering defects and usability problems"],
             ["System and interface acceptance",
              "Scripted browser runs over every screen in both authentication states, with console "
              "and network monitoring",
              "Rendering failures, console errors, unexpected 4xx and 5xx responses, viewport "
              "breakage",
              "Subjective usability; anything a real user would do that the script does not"],
             ["Performance",
              "Repeated timed measurement per operation, and a measurement of read cost as the "
              "dataset grows",
              "Costs that exceed the stated budget, and growth that contradicts the stated scaling "
              "requirement",
              "Behaviour under concurrent load, which a single-process SQLite deployment cannot "
              "expose meaningfully"]],
            widths=[0.9, 1.5, 2.05, 1.82], chapter="6", size=9, number="Table 6.1")

    R.h2("6.2  Test Environment and Harness")
    R.para("The suite runs under pytest with a fixture that points the data layer at a temporary "
           "database file and the upload directory at a temporary directory, and creates the schema "
           "for each case. The consequence is that no case can be affected by another, and the "
           "repository's demonstration database is never touched. Because the fixture replaces the "
           "database path rather than the connection, the cases exercise the same code path that "
           "the running application uses; nothing is stubbed. The one exception is the framework's "
           "own request-size limit, which is exercised by sending a body larger than the configured "
           "maximum and asserting that the framework refuses it.")
    
    R.h2("6.3  Unit and Component Test Results")
    R.para("The suite contains **80 cases**; all 80 pass. The cases are named and grouped by "
           "component so that a failure identifies which module regressed without needing to read "
           "the failure trace. Figure 6.1 shows the distribution and Table 6.2 states what each "
           "group covers.")
    R.figure("figures/chart_tests.png",
             "Automated test cases by component. All 80 cases pass.", chapter="6")

    R.table("Automated test suite by group",
            ["Group", "Cases", "Range", "Covers"],
            [["TC-A  Accounts", "10", "TC-A01 to TC-A10",
              "Registration and its rejection cases, password hashing, login and its rejection "
              "cases, logout, profile retrieval, and the requirement that no credential material "
              "is returned"],
             ["TC-C  Catalogue", "14", "TC-C01 to TC-C14",
              "The empty catalogue, public access, keyword matching against both searchable "
              "columns, case-insensitive matching, category and status filters, all three sort "
              "orders, pagination boundaries, detail assembly and a missing item"],
             ["TC-L  Listings", "12", "TC-L01 to TC-L12",
              "Creation with each missing field, non-numeric price, the initial status, editing, "
              "ownership on edit and delete, the soft-delete behaviour, and the effect of an "
              "offline listing on the catalogue"],
             ["TC-U  Upload", "8", "TC-U01 to TC-U08",
              "Absent session, empty request, accepted types, the generated name format, a "
              "disallowed extension, multiple files, an oversized body, and the order in which "
              "stored names are attached to a listing"],
             ["TC-T  Transitions", "15", "TC-T01 to TC-T15",
              "Unknown and missing actions, a missing item, the session requirement, both guards "
              "on every action, the happy path of all five transitions, and the requirement that a "
              "failed guard leaves the row unchanged"],
             ["TC-S  Social", "16", "TC-S01 to TC-S16",
              "Saving, unsaving and duplicate saves, comment ordering and public visibility, empty "
              "comments, sending and reading messages, the conversation grouping and its ordering "
              "behaviour, and the marking of messages as read"],
             ["TC-P  Personal centre", "5", "TC-P01 to TC-P05",
              "Own listings only, the empty sold list, the sold list after a completed "
              "transaction, the cover-image key, and the session requirement"]],
            widths=[1.05, 0.42, 0.85, 3.95], chapter="6", size=9, number="Table 6.2")

    R.h2("6.4  Interface Testing")
    R.para("Every endpoint is asserted on its HTTP status and on the shape of its envelope. "
           "Table 6.3, reproduced in Appendix C.1, records the status codes the interface is "
           "expected to return and confirms that each was observed. The table is a contract, not a "
           "description: a change that made any cell untrue would be a defect even if no user "
           "noticed it.")

    R.h2("6.5  Negative and Boundary Testing")
    R.para("Negative testing is where most of the defects in a system of this shape are found, "
           "because the happy path is exercised by anyone who uses the software for five minutes. "
           "Table 6.4 lists the boundary and negative cases that were written deliberately, with "
           "the boundary being tested in each.")
    R.table("Negative and boundary cases written deliberately",
            ["Case", "Boundary under test", "Expected and observed behaviour"],
            [["TC-L03, TC-L04", "Required field absent",
              "400, with the reason naming the missing field"],
             ["TC-L05", "Non-numeric price",
              "400; the value is rejected before any coercion is attempted"],
             ["TC-C01", "Zero rows in the table",
              "The catalogue returns an empty list, a total of zero and zero pages rather than "
              "failing on a division in the pagination calculation"],
             ["TC-C07", "Keyword matching nothing",
              "Empty result with a total of zero; the interface then shows the empty state of "
              "Figure 5.6"],
             ["TC-C12", "Pagination boundary at 21 listings, 12 per page",
              "Page 1 holds twelve, page 2 holds nine, and the reported page count is two"],
             ["TC-U03, TC-U05, TC-U06", "File type allow-list at the boundary",
              "Accepted types stored; a disallowed extension rejected for the whole request; "
              "multiple files in one request all stored"],
             ["TC-U07", "Body larger than 5 MB",
              "413 from the framework, not a partial write"],
             ["TC-A03, TC-A04", "Duplicate and empty credentials",
              "400 in both cases, before any row is written"],
             ["TC-S02", "Duplicate favourite",
              "400 from the uniqueness constraint rather than a second row"],
             ["TC-S06", "Whitespace-only comment",
              "400; the value is trimmed before the emptiness check, so a space is not accepted "
              "as content"],
             ["TC-S10, TC-S11", "Recipient that does not exist, and an empty body",
              "404 and 400 respectively, both before any row is written"],
             ["TC-T01, TC-T02", "Unknown action, and an absent action field",
              "400 before the item is read, so neither reveals whether an item exists"],
             ["TC-T14", "Actions on a terminal state",
              "400 for relist, off-shelf and sell on a sold item; the state machine has no "
              "outgoing transition from sold"]],
            widths=[1.15, 1.6, 3.52], chapter="6", size=9, number="Table 6.4")

    R.h2("6.6  State Machine Testing")
    R.para("The status machine is the component where a defect would damage data rather than "
           "merely annoy a user, so it is tested exhaustively rather than representatively. The "
           "test design used a coverage criterion of **all transitions plus all illegal "
           "combinations**: for each of the five actions, the legal case plus a wrong-role case "
           "and a wrong-source-state case where those are distinguishable. Table 6.5, reproduced "
           "in Appendix C.2, records the matrix with the outcome of each cell taken from the "
           "suite.")

    R.para("One case in this table is worth drawing out because it is the property the whole "
           "design exists to guarantee. TC-T15 takes a reserved item, switches to the buyer's "
           "session, and asks to confirm the sale. The request is refused with 403, and the test "
           "then reads the item back and asserts that its status is still reserved. A design that "
           "checked only the role, or that wrote the new status before validating, would fail this "
           "assertion while still returning the same status code to the caller. Testing the "
           "response alone would not have detected it.")

    R.h2("6.7  Authorisation Testing")
    R.para("Authorisation is tested as a matrix rather than as a set of individual cases, because "
           "the failure mode that matters is not a wrong answer but a missing check. Table 6.6, "
           "reproduced in Appendix C.3, records for each protected operation whether it is refused "
           "for each of the three caller contexts. The pattern is what matters: every protected "
           "operation has a refusal in at least one column, and no operation is permitted to an "
           "anonymous caller.")

    R.para("The table exposes one asymmetry that is a deliberate design choice rather than a gap. "
           "Any signed-in student and any anonymous visitor may read every listing and every public "
           "comment; there is no ownership on read. That is what makes the catalogue a catalogue. "
           "Private messages are the exception, and the conversation read is scoped to the caller "
           "by the query itself rather than filtered afterwards, so a caller cannot retrieve another "
           "pair's messages by supplying their identifiers.")

    R.h2("6.8  Requirements Coverage")
    R.para("Figure 6.2 summarises how many of the specified requirements are realised in the proof "
           "of concept and independently verified by at least one automated case. All twenty-eight "
           "functional and all twelve non-functional requirements are traced; the matrix that "
           "supports the figure is reproduced in Appendix B.")
    R.figure("figures/chart_coverage.png",
             "Requirements realised and independently verified, by category", chapter="6")

    R.para("Coverage is complete at the level of the requirement, but it is not uniform in "
           "strength, and the difference matters when the results are read. Three requirements are "
           "verified more weakly than the rest. **FR-06**, which requires that up to three "
           "photographs be attached, is enforced only in the client: the server accepts an "
           "arbitrary number, so an automated case cannot demonstrate the cap. **NFR-04**, keyboard "
           "operability, is verified by a manual walkthrough rather than by an automated assertion, "
           "which means it is verified once rather than on every run. And **NFR-01**, that a "
           "first-time user can publish without instructions, rests on observation of three users "
           "rather than on a measurement - a small sample, reported as such.")

    R.h2("6.9  Performance Testing")
    R.para("Performance was measured in-process with the framework's test client, which removes "
           "network and browser time and isolates the cost the application itself contributes. The "
           "dataset contains 500 listings, 22 accounts, 61 conversations and one 40-message "
           "thread; each read was repeated 200 times and each write 100 times. Table 6.7 and "
           "Figure 6.3 report the median and the 95th percentile per operation.")
    R.figure("figures/chart_perf.png",
             "In-process response time per operation at 500 listings, median and 95th percentile",
             chapter="6")

    _perf_table(R)

    R.para("Three readings of these numbers matter. The catalogue reads sit between 1.9 and 3.5 ms "
           "of median application time, which is more than two orders of magnitude inside the "
           "100 ms budget NFR-06 states, and the variation between the cheapest and the most "
           "expensive read is under 2 ms. The write paths cost roughly twice the reads, which is "
           "consistent with each write performing validation, a read for authorisation and a "
           "transaction commit. And the two largest numbers in the table are not single operations "
           "at all: they are two-request cycles, so their per-request cost is half what the row "
           "shows.")
    
    R.h2("6.10  Scaling Measurement")
    R.para("Absolute latency does not answer the question that matters for a catalogue: does the "
           "system degrade as the data grows? To measure it, the same three read paths were "
           "measured against datasets of 100, 250, 500, 1,000 and 2,000 listings, with the "
           "database file growing from 53 KB to 254 KB. Table 6.8 and Figure 6.4 report the medians.")
    R.figure("figures/chart_scale.png",
             "Median response time for three catalogue read paths as the number of listings grows "
             "from 100 to 2,000", chapter="6")
    _scale_table(R)
    R.para("The result is close to flat: over a twenty-fold increase in rows, the median read cost "
           "rose from about 2.45 ms to about 2.75 ms, an increase of roughly 12 per cent. Both the "
           "unfiltered catalogue and the keyword search scan the table, because a wildcard cannot "
           "use an index, yet the scan is not the dominant cost at this size - connection setup, "
           "row materialisation and JSON serialisation dominate. NFR-07 requires sub-linear growth "
           "and the measurement shows growth that is sub-linear by a wide margin, but the "
           "requirement is satisfied at a scale where the linear term has not yet become visible "
           "rather than because the algorithm is sub-linear. At a scale where it did become "
           "visible, a wildcard search would need a full-text index; the measurement here cannot "
           "predict where that point falls, and does not claim to.")

    R.h2("6.11  Interface and Usability Evaluation")
    R.para("The interface was evaluated in three ways, each of which finds different problems. A "
           "**scripted walkthrough** drove a real browser through every view in both an "
           "authenticated and an anonymous state, at a desktop and a mobile viewport, and captured "
           "the seventeen screens reproduced in section 5.10. The run monitored the browser "
           "console and every network response: the only reported console message in the whole run "
           "was the expected 401 that the client receives when it asks for the current user before "
           "anybody has logged in, and there were no unexpected 4xx or 5xx responses. That is a "
           "meaningful result, because a rendering path that throws inside an event handler leaves "
           "the screen looking correct while silently failing to respond to the next click.")
    R.para("**Observation of three first-time users** addressed requirement NFR-01. All three "
           "published a listing without written instructions. Two of the three attempted to "
           "publish without a photograph and were stopped by the client-side check with a message "
           "that named the problem; both then succeeded. That observation produced the only "
           "interface change to come out of the evaluation: the photograph control originally "
           "carried no indication that at least one image was required, and the field label was "
           "changed to mark it as required as a result.")

    R.h2("6.12  Verification of the Non-Functional Requirements")
    R.para("Table 6.9, reproduced in Appendix C.4, states the measured outcome for each of the "
           "twelve non-functional requirements. Where the outcome is a partial pass, or where "
           "verification rests on a weaker method than the others, that is stated rather than "
           "averaged away.")

    R.h2("6.13  Defects Found and Fixed")
    R.para("Table 6.10, reproduced in Appendix C.5, records the defects that were found and what "
           "happened to each. The entries are included because the way a defect was found says "
           "something about the testing that found it, and because two of them are still open - a "
           "report that lists only fixed defects is a report that stopped testing too early.")

    R.h2("6.14  Threats to Validity and What Was Not Tested")
    R.para("The results above support the claims in this report, but they do not support more than "
           "those claims, and the boundary is worth stating precisely.")
    R.bullets([
        "**Concurrency was not tested.** The deployment is a single process with a file-based "
        "database. Concurrent writes are not exercised by any case, and the behaviour under "
        "concurrent load is not merely unmeasured but structurally different from the measured "
        "behaviour: SQLite serialises writers, so the timings in section 6.9 do not extrapolate.",
        "**The performance numbers exclude everything outside the application.** The measurement is "
        "in-process, so network latency, browser rendering, image transfer and the cost of the "
        "first request after the process starts are all absent. The numbers are a floor on user "
        "experience, not an estimate of it.",
        "**The usability evidence rests on three users.** Requirement NFR-01 was assessed by "
        "observation of three first-time users with no recordings and no measured task times. It "
        "is enough to have found one real interface problem; it is not enough to make a claim "
        "about learnability in general.",
        "**Accessibility was checked by walkthrough, not by audit.** Keyboard operability and the "
        "declaration of modal surfaces were verified manually. No screen-reader testing, no "
        "contrast measurement against a standard and no conformance audit against WCAG were "
        "performed, so the system should not be described as accessible, only as having taken "
        "specific accessibility steps.",
        "**Defensive testing has a surface, and the surface was drawn by the team.** The cases "
        "were written by the people who wrote the code. That is the weakest form of test design: "
        "a misunderstanding shared by the implementer and the tester produces a test that agrees "
        "with the misunderstanding. Independent test design, or an external review, would raise "
        "confidence and did not happen.",
        "**One platform was actually tested.** The software was developed and verified on Windows. "
        "The macOS claim in NFR-12 is reasoned from the absence of platform-specific code rather "
        "than observed.",
    ])
    R.para("Stating these limits is not a hedge on the results. Within the tested surface - the "
           "specified functional requirements, the twelve non-functional requirements, the "
           "transition guards and the authorisation rules - the evidence is strong and, in the case "
           "of the transition guards, exhaustive. Beyond that surface the report claims nothing.")


def chapter7(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("7  Conclusions and Future Work")

    R.h2("7.1  Outcomes Against the Objectives")
    R.para("Section 1.3 stated five objectives. Table 7.1 states, for each, what was achieved and "
           "what was not, judged against the evidence in Chapters 3 to 6 rather than against the "
           "intention.")
    R.table("Outcome against each project objective",
            ["Objective", "Achieved", "Evidence", "Shortfall"],
            [["1. Specify the requirements",
              "Yes",
              "28 functional and 12 non-functional requirements, 18 use cases with 8 described in "
              "full, a prioritisation, a scope boundary and a traceability matrix (Chapters 3 and "
              "Appendix B)",
              "Two requirements are implemented more weakly than specified: the photograph cap and "
              "the requirement for at least one photograph are enforced only in the client."],
             ["2. Design the architecture and data model",
              "Yes",
              "Architecture, module, domain, entity-relationship, state, activity and business "
              "process models, three sequence diagrams, and a ten-entry decision log with the "
              "rejected alternative recorded for each",
              "The design assumes a single writer and does not address concurrency, which is "
              "acceptable at the stated scope but is a design gap rather than a delivery gap."],
             ["3. Implement a working proof of concept",
              "Yes",
              "3,356 lines of runtime code across 23 routes, implementing every feature listed in "
              "Table 1.3, running from a clean checkout with one command",
              "Publishing a listing requires a photograph only in the client, and the interface "
              "does not poll for new messages."],
             ["4. Verify the proof of concept",
              "Yes, with stated limits",
              "80 automated cases all passing, a transition coverage matrix, a 16-operation "
              "authorisation matrix, a per-operation performance measurement and a five-size "
              "scaling measurement, plus an interface evaluation with no console errors and no "
              "unexpected error responses",
              "Concurrency, real-user usability at scale and WCAG conformance were not tested. Two "
              "defects remain open and both are documented rather than hidden."],
             ["5. Deliver the documentation and presentation",
              "In progress",
              "This report, the requirements and design models in it, and the user manual, which "
              "is written against the delivered interface",
              "The slide deck and the recorded demonstration were not complete at the time of "
              "writing."]],
            widths=[1.15, 0.72, 2.6, 1.8], chapter="7", size=8.8)

    R.h2("7.2  Limitations")
    R.para("The limitations below are the ones a reviewer would find by reading the code and the "
           "tests. They are listed in descending order of how much they would matter to a real "
           "deployment, not of how hard they are to fix.")
    R.table("Limitations of the delivered proof of concept",
            ["#", "Limitation", "Consequence if not addressed", "Effort to fix"],
            [["L1", "The session signing key is a literal in the source file",
              "Anyone with the source can forge a session cookie. Serious in any deployed system; "
              "limited here only because the source and the data are on the same machine.",
              "Low: read it from the environment"],
             ["L2", "SQLite serialises writers and the service is single-process",
              "The system cannot scale beyond one process, and the measured timings do not "
              "extrapolate to concurrent load.",
              "High: a client-server database plus connection pooling"],
             ["L3", "Foreign keys are declared but not enforced, because the pragma is not set",
              "Orphan rows are possible if a future code path deletes a referenced row. No current "
              "path does.",
              "Very low: one statement on connection creation"],
             ["L4", "The conversation list orders by identifier rather than by timestamp",
              "If rows ever arrive out of order the displayed \"most recent\" message can be wrong.",
              "Very low: order by timestamp with the identifier as a tie-breaker"],
             ["L5", "The upload limits are partly client-side only",
              "A hand-built request can exceed three photographs per listing, or create a listing "
              "with none.",
              "Low: two validation checks on the server"],
             ["L6", "Uploaded photographs are stored on the local filesystem",
              "The images and the database are not backed up together, and the application must "
              "run on the machine that holds them.",
              "Moderate: object storage and a proxy route"],
             ["L7", "No mechanism to recover from a mistaken sale confirmation",
              "A seller who confirms by accident cannot reverse it through the interface.",
              "Moderate: an administrative path and a decision about what it is allowed to undo"],
             ["L8", "No notification when a message or a reservation arrives",
              "A seller must open the application to learn that someone has reserved an item, "
              "which weakens the availability guarantee the design is built around.",
              "Moderate: polling, then email or push"],
             ["L9", "Accessibility work is partial",
              "The system is usable by keyboard but has not been audited against WCAG and has not "
              "been tested with a screen reader.",
              "Moderate and continuous"],
             ["L10", "The demonstration dataset is committed with known passwords",
              "Acceptable for a teaching artefact, unacceptable in any deployed system.",
              "Very low: remove the database from the repository"]],
            widths=[0.3, 1.5, 2.55, 1.42], chapter="7", size=8.8)

    R.h2("7.3  Future Work")
    R.para("Future work is ordered by the value it would add rather than by the effort it would "
           "take, because the cheapest items on the list are not the ones that most change what the "
           "system can do.")
    R.table("Prioritised future work",
            ["Priority", "Work", "Why this ordering"],
            [["1", "Notification on reservation and on message",
              "The central claim of the project is that the status field makes availability "
              "authoritative. That claim is weakened if a seller learns about a reservation only by "
              "opening the application. This is the single change that most improves the "
              "usefulness of what has already been built."],
             ["2", "A second state on the transaction: record which buyer reserved an item",
              "The model currently records that an item is reserved but not for whom. Recording the "
              "buyer would make the reservation enforceable and would let the seller see who is "
              "coming, at the cost of one column and one join."],
             ["3", "Automatic expiry of a reservation",
              "A reservation that is never released removes an item from circulation permanently. "
              "An expiry window, with a notification, turns a stall into a retry."],
             ["4", "Close the two open defects L3 and L4",
              "Both are single-line changes and both are correctness issues rather than features. "
              "They are cheap enough that they should be closed before any new feature is added."],
             ["5", "Move the session key to configuration, and remove the demonstration data from "
                   "the repository",
              "Both are prerequisites for any deployment beyond a single teaching machine."],
             ["6", "Verify the student identifier against an institutional source",
              "The platform records a student identifier but cannot check it. Trust currently rests "
              "on registration being inconvenient for outsiders rather than on verification, which "
              "is the weakest part of the design."],
             ["7", "A full-text index for keyword search",
              "Section 6.10 shows the wildcard search is not yet the dominant cost, but it scans "
              "the table and will eventually be. The measurement does not say where the crossover "
              "falls; a load test at a larger scale would."],
             ["8", "Object storage for photographs, and a deployment with a server-based database",
              "The two changes that would make the system deployable as a shared service rather "
              "than as a single-machine application, and together they are the largest piece of "
              "work on this list."],
             ["9", "Reputation and moderation",
              "Deliberately excluded from the proof of concept because a reputation score needs "
              "transaction volume to mean anything, and because moderation is an operational "
              "commitment rather than a feature."],
             ["10", "Multi-campus operation",
              "The system currently assumes one campus and one population. Extending it means "
              "revisiting the schema, the search scope and the trust model, which is why it is "
              "last."]],
            widths=[0.62, 1.85, 3.8], chapter="7", size=9)

    R.h2("7.4  Reflection on the Process")
    R.para("Four things about the way this project was run are worth recording, because they are "
           "the parts that would change if the project were started again.")
    R.para("**Building first and specifying second was the right order.** The requirement that "
           "proved hardest to get right - what happens when a buyer reserves an item and then does "
           "not collect it - is invisible from a requirements interview. It became obvious within "
           "a day of having a prototype with a status field, and the specification in Chapter 3 was "
           "written around it. The risk of this order is that the prototype becomes the "
           "specification by default; the mitigation used here was to number and trace every "
           "requirement so that features had to be justified rather than inherited.")
    R.para("**Writing the tests alongside the code paid for itself in a single event.** A "
           "late change replaced the entire front end. Without 80 passing cases covering every "
           "endpoint, that change would have been a gamble on manual retesting; with them, the "
           "regression risk was bounded to the client, which is where the change was. The one "
           "defect that suite did not catch - the stylesheet that did not exist - is instructive, "
           "because it was a failure of the test *surface* rather than of the tests: nothing "
           "asserted that the page was styled, so nothing noticed that it was not.")
    R.para("**The most valuable tests were the negative ones.** The happy paths were confirmed "
           "within minutes of being written. The cases that found defects were the ones that "
           "asked what happens when a buyer tries to confirm a sale, or when two messages arrive "
           "in the same second, or when a required field is absent. On this evidence a test suite "
           "whose cases are evenly divided between positive and negative paths would have been "
           "better value than one weighted towards the positive.")
    
    R.h2("7.5  Closing Statement")
    R.para("Campus Market demonstrates that the informational half of campus second-hand trade "
           "can be solved by a small, self-contained application. The problem was framed as one of "
           "friction rather than price, the central requirement was identified as an authoritative "
           "answer to whether an item is still available, and that requirement was met by modelling "
           "a listing's life as an explicit state machine guarded on the server. The result is 23 "
           "routes, six tables and 3,356 lines of runtime code that installs with one command, "
           "verified by 80 automated cases that all pass and measured two orders of magnitude "
           "inside the stated latency budget.")
    R.para("What the system does not do is equally clear, and it is documented rather than glossed: "
           "it does not handle money, it does not scale past a single process, it does not notify "
           "anybody of anything, and its accessibility work is partial. Those are the boundaries "
           "the proof of concept was scoped to, and the report states them in the same place as "
           "the results rather than in a caveat at the end. The most useful next step is not a new "
           "feature but a notification, because the design's central claim - that the status field "
           "makes availability authoritative - is only fully true once the seller learns about a "
           "reservation without having to look for it.")


# ===================================================================== data tables
def _perf_table(R):
    rows = []
    for label, v in PERF["results"].items():
        rows.append([label, "%.2f" % v["median"], "%.2f" % v["p95"], "%.2f" % v["mean"],
                     str(v["n"])])
    meta = PERF["meta"]
    R.table("In-process response time per operation. Dataset: %d listings, %d accounts, %d "
            "conversations, one %d-message thread. Python %s, %d repetitions for reads and 100 "
            "for writes."
            % (meta["items"], meta["users"], meta["threads"], meta["thread_messages"],
               meta["runtime"], meta["repeats"]),
            ["Operation", "Median (ms)", "95th pct (ms)", "Mean (ms)", "Repeats"],
            rows, widths=[3.05, 0.78, 0.85, 0.72, 0.6], chapter="6", size=9.3,
            align=[None, "r", "r", "r", "r"], number="Table 6.7")


def _scale_table(R):
    keys = [k for k in SCALE[0] if not k.startswith("_")]
    rows = []
    for r in SCALE:
        rows.append(["%d" % r["_rows"], "%.0f KB" % (r["_db_bytes"] / 1024)] +
                    ["%.2f" % r[k] for k in keys])
    R.table("Median response time for three catalogue read paths as the dataset grows",
            ["Listings", "Database size", "Catalogue page 1 (ms)",
             "Keyword search (ms)", "Filter and sort (ms)"],
            rows, widths=[0.75, 0.95, 1.35, 1.35, 1.35], chapter="6", size=9.3,
            align=[None, "r", "r", "r", "r"], number="Table 6.8")


# ===================================================================== references
def references(R):
    R.h1("References")
    R.para("References follow the Harvard (author-date) style used throughout this report.")
    items = [
        "Beck, K. (2002) *Test-Driven Development: By Example*. Boston: Addison-Wesley.",
        "Beck, K. and Cunningham, W. (1989) 'A laboratory for teaching object-oriented thinking', "
        "*ACM SIGPLAN Notices*, 24(10), pp. 1-6.",
        "Cockburn, A. (2001) *Writing Effective Use Cases*. Boston: Addison-Wesley.",
        "Fielding, R.T. (2000) *Architectural Styles and the Design of Network-based Software "
        "Architectures*. PhD thesis. University of California, Irvine.",
        "Fowler, M. (2002) *Patterns of Enterprise Application Architecture*. Boston: "
        "Addison-Wesley.",
        "Gamma, E., Helm, R., Johnson, R. and Vlissides, J. (1994) *Design Patterns: Elements of "
        "Reusable Object-Oriented Software*. Reading, MA: Addison-Wesley.",
        "Ginige, A. and Murugesan, S. (2001) 'Web engineering: an introduction', *IEEE "
        "MultiMedia*, 8(1), pp. 14-18.",
        "International Organization for Standardization (2011) *ISO/IEC 25010:2011 Systems and "
        "software engineering - Systems and software Quality Requirements and Evaluation "
        "(SQuaRE) - System and software quality models*. Geneva: ISO.",
        "International Organization for Standardization (2018) *ISO 9241-11:2018 Ergonomics of "
        "human-system interaction - Part 11: Usability: Definitions and concepts*. Geneva: ISO.",
        "Kleppmann, M. (2017) *Designing Data-Intensive Applications*. Sebastopol, CA: "
        "O'Reilly Media.",
        "Larman, C. (2004) *Applying UML and Patterns: An Introduction to Object-Oriented "
        "Analysis and Design and Iterative Development*. 3rd edn. Upper Saddle River, NJ: "
        "Prentice Hall.",
        "Mozilla (2024) *MDN Web Docs: Cross-site scripting (XSS)*. Available at: "
        "https://developer.mozilla.org/ (Accessed: September 2026).",
        "Nielsen, J. (1994) *Usability Engineering*. San Francisco: Morgan Kaufmann.",
        "Nielsen, J. and Molich, R. (1990) 'Heuristic evaluation of user interfaces', "
        "*Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '90)*, "
        "pp. 249-256.",
        "Open Worldwide Application Security Project (2021) *OWASP Top 10:2021 - The Ten Most "
        "Critical Web Application Security Risks*. Available at: https://owasp.org/Top10/ "
        "(Accessed: September 2026).",
        "Open Worldwide Application Security Project (2024) *Password Storage Cheat Sheet*. "
        "Available at: https://cheatsheetseries.owasp.org/ (Accessed: September 2026).",
        "Parnas, D.L. (1972) 'On the criteria to be used in decomposing systems into modules', "
        "*Communications of the ACM*, 15(12), pp. 1053-1058.",
        "Pallets Projects (2023) *Flask Documentation (2.3.x)*. Available at: "
        "https://flask.palletsprojects.com/ (Accessed: September 2026).",
        "Pressman, R.S. and Maxim, B.R. (2020) *Software Engineering: A Practitioner's Approach*. "
        "9th edn. New York: McGraw-Hill.",
        "Ries, E. (2011) *The Lean Startup*. New York: Crown Business.",
        "Rubin, J. and Chisnell, D. (2008) *Handbook of Usability Testing*. 2nd edn. Indianapolis: "
        "Wiley.",
        "SQLite Consortium (2024) *SQLite Documentation: Foreign Key Support*. Available at: "
        "https://www.sqlite.org/foreignkeys.html (Accessed: September 2026).",
        "Sommerville, I. (2016) *Software Engineering*. 10th edn. Harlow: Pearson Education.",
    ]
    for it in items:
        R.para(it, size=11, spacing=1.3, space_after=6, indent=0.4)


# ===================================================================== appendices
def appendix_a(R):
    R.h1("Appendix A - Group Workload Profile")
    R.para("The group workload profile records the effort contributed by each member. The values "
           "follow the convention given on the course template: **0%** means the member "
           "contributed the same as the other members; **+X%** means more by X per cent; **-X%** "
           "means less by X per cent. Permitted magnitudes of X include 10%, 25%, 50% and 100%.")
    R.para("Each member records their own view and signs the declaration. A member who does not "
           "agree with one or more of the values recorded by the others should not sign the "
           "profile, and should instead email the Course Coordinator before the submission "
           "deadline explaining the disagreement.")

    R.h2("A.1  Quantitative contribution")
    R.table("Agreed contribution of each group member",
            ["Group member", "Name", "Self-assessed value", "Agreed value", "Signature"],
            [["Group member 1", "<Full name>", "<0% / +X% / -X%>", "<value>", ""],
             ["Group member 2", "<Full name>", "<0% / +X% / -X%>", "<value>", ""],
             ["Group member 3", "<Full name>", "<0% / +X% / -X%>", "<value>", ""],
             ["Group member 4", "<Full name>", "<0% / +X% / -X%>", "<value>", ""],
             ["Group member 5", "<Full name>", "<0% / +X% / -X%>", "<value>", ""]],
            widths=[0.95, 1.5, 1.35, 1.05, 1.35], chapter="A")

    R.h2("A.2  Qualitative contribution")
    R.table("Nature of each member's contribution, by project phase",
            ["Member", "Requirements and design", "Implementation", "Testing and evaluation",
             "Documentation", "Overall"],
            [["Member 1", "Elicitation; functional requirements", "Catalogue query; listing "
              "management", "Automated suite; requirements coverage", "Requirements chapters", ""],
             ["Member 2", "Architecture; module boundaries; supervisor liaison",
              "Accounts and sessions; interface contract", "Authorisation matrix",
              "Traceability matrix; this report", ""],
             ["Member 3", "Schema design and normalisation; security requirements",
              "Upload path; comments; messaging", "Performance and scaling measurement",
              "User manual; data model chapter", ""],
             ["Member 4", "UML models; state machine; use case descriptions",
              "Transaction status machine", "Negative and boundary test design; transition "
              "coverage", "Design chapter", ""],
             ["Member 5", "Interface design and design system", "All client views and feedback "
              "states", "Interface evaluation on desktop and mobile", "Interface chapter; "
              "presentation slides", ""]],
            widths=[0.7, 1.3, 1.3, 1.35, 1.32], chapter="A", size=8.8)

    R.h2("A.3  Declaration")
    R.para("We confirm that the values recorded above were agreed openly and fairly by all "
           "members of the group, that each member had the opportunity to record a different view, "
           "and that the work submitted represents the work of the group.", size=11)
    R.para("Signed by every group member who agrees with the profile as recorded:", size=11,
           space_after=14)
    for slot, name, _ in [("Group member 1", "<Full name>", ""), ("Group member 2", "<Full name>", ""),
                          ("Group member 3", "<Full name>", ""), ("Group member 4", "<Full name>", ""),
                          ("Group member 5", "<Full name>", "")]:
        p = R.para("%s   %s   Signature: ______________________   Date: ____________"
                   % (slot, name), size=10.5, spacing=1.4, space_after=14)


def appendix_b(R):
    R.h1("Appendix B - Requirements Traceability Matrix")
    R.para("The matrix maps every requirement to the use case that exercises it, the component "
           "that implements it and the automated test cases that verify it. It was maintained "
           "alongside the requirements rather than assembled at the end. The coverage column "
           "records the strength of the verification, and the three entries marked *weak* are the "
           "ones discussed in section 6.8.")
    rows = [
        ("FR-01", "Register an account", "UC-01", "app.py register route", "TC-A01 to TC-A05", "Strong"),
        ("FR-02", "Authenticate", "UC-02", "app.py login route", "TC-A06, TC-A07", "Strong"),
        ("FR-03", "Log out", "UC-02", "app.py logout route", "TC-A09", "Strong"),
        ("FR-04", "Retrieve own profile", "UC-12", "app.py get_me route", "TC-A02, TC-A05, TC-A08", "Strong"),
        ("FR-05", "Publish a listing", "UC-06", "app.py create_item", "TC-L02, TC-L03, TC-L04, TC-L05, TC-L06", "Strong"),
        ("FR-06", "Attach up to three photographs", "UC-07", "app.py upload_image; create_item", "TC-U01 to TC-U08", "*weak* - the cap is client-side only"),
        ("FR-07", "Reject incomplete or non-numeric input", "UC-06", "app.py create_item validation", "TC-L03, TC-L04, TC-L05", "Strong"),
        ("FR-08", "Edit an own listing", "UC-08", "app.py update_item", "TC-L07, TC-L08, TC-L09", "Strong"),
        ("FR-09", "Take a listing offline", "UC-09", "app.py delete_item (soft)", "TC-L10, TC-L11, TC-L12", "Strong"),
        ("FR-10", "Relist an offline listing", "UC-09", "status machine, relist rule", "TC-T12, TC-T13", "Strong"),
        ("FR-11", "Paginated catalogue", "UC-03", "app.py get_items", "TC-C01, TC-C12", "Strong"),
        ("FR-12", "Keyword search on two columns", "UC-04", "get_items LIKE conditions", "TC-C04, TC-C05, TC-C06, TC-C07", "Strong"),
        ("FR-13", "Filter by category", "UC-04", "get_items category condition", "TC-C08", "Strong"),
        ("FR-14", "Filter by status", "UC-04", "get_items status condition", "TC-C09, TC-L11", "Strong"),
        ("FR-15", "Three sort orders", "UC-04", "get_items ORDER BY branch", "TC-C10, TC-C11", "Strong"),
        ("FR-16", "Listing detail", "UC-05", "app.py get_item_detail", "TC-C03, TC-C13, TC-C14", "Strong"),
        ("FR-17", "Read public comments", "UC-10", "app.py get_comments", "TC-S05", "Strong"),
        ("FR-18", "Post a comment", "UC-10", "app.py add_comment", "TC-S06, TC-S07, TC-S08", "Strong"),
        ("FR-19", "Save a favourite", "UC-11", "app.py add_favorite", "TC-S01, TC-S02, TC-S03, TC-S04", "Strong"),
        ("FR-20", "Remove a favourite", "UC-11", "app.py remove_favorite", "TC-S01", "Strong"),
        ("FR-21", "List favourites", "UC-11", "app.py get_favorites", "TC-S01, TC-P01", "Strong"),
        ("FR-22", "Reserve an item", "UC-13", "status machine, reserve rule", "TC-T04, TC-T05, TC-T06, TC-T15", "Strong"),
        ("FR-23", "Confirm the sale", "UC-14", "status machine, sell rule", "TC-T07, TC-T08, TC-T09, TC-T14", "Strong"),
        ("FR-24", "Cancel a reservation", "UC-15", "status machine, cancel rule", "TC-T10", "Strong"),
        ("FR-25", "Send a private message", "UC-16", "app.py send_message", "TC-S09, TC-S10, TC-S11", "Strong"),
        ("FR-26", "List conversations by partner", "UC-17", "app.py get_messages (aggregate)", "TC-S12, TC-S13, TC-S14", "Strong"),
        ("FR-27", "Read a thread and mark it read", "UC-18", "app.py get_conversation", "TC-S09, TC-S15, TC-S16", "Strong"),
        ("FR-28", "Personal centre", "UC-12", "app.py get_my_items, get_sold_items", "TC-P01 to TC-P05", "Strong"),
        ("NFR-01", "First-time user publishes unaided", "UC-06", "publish view", "Manual observation of three users", "*weak* - small sample, not recorded"),
        ("NFR-02", "Visible feedback and confirmations", "-", "toast, confirm dialog", "Scripted capture of every screen", "Moderate"),
        ("NFR-03", "One visual language", "-", "design tokens in the stylesheet", "Token review", "Moderate"),
        ("NFR-04", "Keyboard operable; modals announced", "-", "focus styles, ARIA attributes", "Manual keyboard walkthrough", "*weak* - manual, single pass"),
        ("NFR-05", "430 px to 1440 px", "-", "responsive breakpoints", "Capture at both viewports", "Moderate"),
        ("NFR-06", "Read within 100 ms at 500 listings", "-", "catalogue query", "200 repetitions per operation", "Strong"),
        ("NFR-07", "Sub-linear read growth", "-", "catalogue query", "Five-size scaling measurement", "Strong"),
        ("NFR-08", "No unhandled server error", "-", "all routes", "80 automated cases plus the browser run", "Strong within the tested surface"),
        ("NFR-09", "Passwords stored as a salted hash", "UC-01", "register route; Werkzeug hashing", "TC-A10", "Strong"),
        ("NFR-10", "All user text escaped before rendering", "-", "escapeHtml in the client", "Code review; adversarial title", "Moderate"),
        ("NFR-11", "Server-side authorisation", "-", "login_required; ownership checks", "16-operation authorisation matrix", "Strong"),
        ("NFR-12", "One-command install, two platforms", "-", "app.py entry point", "Clean-environment installation", "Moderate - Windows observed, macOS reasoned"),
    ]
    R.table("Requirements traceability matrix",
            ["ID", "Requirement", "Use case", "Implemented in", "Verified by", "Coverage"],
            [list(r) for r in rows],
            widths=[0.45, 1.55, 0.5, 1.3, 1.6, 0.87], chapter="B", size=8.2)


def appendix_c(R):
    R.h1("Appendix C - Verification Detail")
    R.para("The three matrices below are the detailed evidence behind sections 6.4, 6.6 and 6.7. "
           "They are placed here so that the evaluation chapter remains readable end to end; each "
           "one is referenced from the section that interprets it, and each cell was confirmed by "
           "an automated case in the suite described in section 6.3.")

    R.h2("C.1  Interface contract (Table 6.3)")
    R.para("Every endpoint asserted on its HTTP status and on the shape of its envelope. A change "
           "that made any cell untrue would be a defect even if no user noticed it.")
    R.table("Expected HTTP status per endpoint, by situation. Every cell was confirmed by an "
            "automated case.",
            ["Endpoint", "Success", "Anonymous call", "Bad input", "Wrong owner"],
            [["POST /api/register", "200", "200 (public)", "400 missing fields, 400 duplicate", "-"],
             ["POST /api/login", "200", "200 (public)", "401 wrong password", "-"],
             ["POST /api/logout", "200", "200 (idempotent)", "-", "-"],
             ["GET /api/user/me", "200", "**401**", "-", "-"],
             ["GET /api/items", "200", "200 (public)", "-", "-"],
             ["GET /api/items/<id>", "200", "200 (public)", "404 missing", "-"],
             ["POST /api/items", "200", "**401**", "400 missing title, missing price, "
                                                   "non-numeric price", "-"],
             ["PUT /api/items/<id>", "200", "**401**", "404 missing", "**403**"],
             ["DELETE /api/items/<id>", "200", "**401**", "404 missing", "**403**"],
             ["POST /api/upload", "200", "**401**", "400 empty, 400 bad type, 413 too large", "-"],
             ["POST /api/items/<id>/status", "200", "**401**",
              "400 unknown action, 400 missing action, 404 missing item, 400 illegal transition",
              "**403**"],
             ["GET /api/favorites", "200", "**401**", "-", "-"],
             ["POST /api/favorites", "200", "**401**", "400 missing item, 400 duplicate", "-"],
             ["DELETE /api/favorites/<id>", "200", "**401**", "-", "-"],
             ["GET /api/items/<id>/comments", "200", "200 (public)", "-", "-"],
             ["POST /api/items/<id>/comments", "200", "**401**", "400 empty content", "-"],
             ["GET /api/messages", "200", "**401**", "-", "-"],
             ["POST /api/messages", "200", "**401**", "400 missing content, 404 unknown "
                                                      "recipient", "-"],
             ["GET /api/messages/<uid>", "200", "**401**", "-", "-"],
             ["GET /api/user/items", "200", "**401**", "-", "-"],
             ["GET /api/user/sold", "200", "**401**", "-", "-"]],
            widths=[1.55, 0.55, 0.95, 2.35, 0.6], chapter="6", size=8.8, number="Table 6.3")
    R.h2("C.2  State machine transition coverage (Table 6.5)")
    R.table("Transition coverage. Each cell is the observed outcome for that action in that "
            "state, performed by the stated actor.",
            ["Action performed by", "on sale", "reserved", "sold", "off shelf"],
            [["Buyer (not the seller): reserve",
              "**reserved** (legal)", "400 refused", "400 refused", "400 refused"],
             ["Buyer (not the seller): sell",
              "403 refused", "403 refused", "403 refused", "403 refused"],
             ["Seller: reserve (own item)",
              "403 refused", "403 refused", "403 refused", "403 refused"],
             ["Seller: sell", "400 refused", "**sold** (legal)", "400 refused", "400 refused"],
             ["Seller: cancel the reservation",
              "400 refused", "**on sale** (legal)", "400 refused", "400 refused"],
             ["Seller: take offline", "**off shelf** (legal)", "400 refused", "400 refused",
              "400 refused"],
             ["Seller: relist", "400 refused", "400 refused", "400 refused",
              "**on sale** (legal)"]],
            widths=[1.75, 1.05, 1.05, 0.85, 1.1], chapter="6", size=9, number="Table 6.5")
    R.h2("C.3  Authorisation matrix (Table 6.6)")
    R.table("Authorisation matrix. Refusals are asserted on the status code, and the "
            "state-changing cases additionally assert that the row was not modified.",
            ["Operation", "Anonymous", "Signed in, not the owner", "Owner"],
            [["Read the catalogue and a listing detail", "Permitted", "Permitted", "Permitted"],
             ["Read the comments on a listing", "Permitted", "Permitted", "Permitted"],
             ["Retrieve own profile", "**401**", "Permitted (own)", "Permitted"],
             ["Create a listing", "**401**", "Permitted", "Permitted"],
             ["Edit a listing", "**401**", "**403**", "Permitted"],
             ["Take a listing offline", "**401**", "**403**", "Permitted"],
             ["Relist a listing", "**401**", "**403**", "Permitted"],
             ["Reserve an item", "**401**", "Permitted", "**403** (own item)"],
             ["Confirm the sale", "**401**", "**403**", "Permitted"],
             ["Cancel a reservation", "**401**", "**403**", "Permitted"],
             ["Upload a photograph", "**401**", "Permitted", "Permitted"],
             ["Save or unsave a favourite", "**401**", "Permitted", "Permitted"],
             ["Post a comment", "**401**", "Permitted", "Permitted"],
             ["Send a message", "**401**", "Permitted", "Permitted"],
             ["Read own conversations", "**401**", "Permitted (own)", "Permitted"],
             ["Read own listings and sold items", "**401**", "Permitted (own)", "Permitted"]],
            widths=[2.35, 0.8, 1.65, 1.0], chapter="6", size=9, number="Table 6.6")

    R.h2("C.4  Verification of the non-functional requirements (Table 6.9)")
    R.table("Outcome against each non-functional requirement",
            ["ID", "Requirement (abbreviated)", "Method", "Outcome"],
            [["NFR-01", "A first-time user publishes without instructions",
              "Observation of three users", "**Met, weak evidence.** All three succeeded without "
                                             "instructions; the sample is small and the "
                                             "observation was not recorded."],
             ["NFR-02", "Every action gives visible feedback; destructive actions are confirmed",
              "Interface inspection and scripted capture",
              "**Met.** Every action produces a toast, an inline message or a state change; all "
              "destructive actions route through the shared dialog."],
             ["NFR-03", "One visual language across all views",
              "Token and stylesheet review",
              "**Met.** Every colour, size and spacing value in the component stylesheet resolves "
              "to a token."],
             ["NFR-04", "Keyboard operable, visible focus, modal surfaces announced",
              "Manual keyboard walkthrough",
              "**Met, manual.** Verified by walkthrough rather than by an automated case, so it is "
              "verified once rather than on every run."],
             ["NFR-05", "Usable from 430 px to 1440 px without horizontal scrolling",
              "Capture at both viewports",
              "**Met.** Two breakpoints collapse the layout; both viewports were captured."],
             ["NFR-06", "Catalogue read within 100 ms at 500 listings",
              "200 repetitions per operation",
              "**Met by two orders of magnitude.** Worst measured median 3.5 ms."],
             ["NFR-07", "Read cost grows sub-linearly from 100 to 2,000 listings",
              "Scaling measurement at five sizes",
              "**Met.** ~12% growth across a twenty-fold increase in rows; see the caveat in "
              "section 6.10."],
             ["NFR-08", "No unhandled server error for any reachable input",
              "80 automated cases including malformed input; scripted browser run",
              "**Met within the tested surface.** No 5xx was observed. Inputs outside the tested "
              "surface are not covered."],
             ["NFR-09", "Passwords stored as a salted hash",
              "Column inspection and TC-A10",
              "**Met.** The stored value carries the algorithm prefix and does not contain the "
              "submitted password."],
             ["NFR-10", "All user-supplied text escaped before rendering",
              "Code inspection of every render path; adversarial input",
              "**Met.** Every interpolation passes through one shared escaping function; a listing "
              "title containing markup renders as text."],
             ["NFR-11", "Authorisation enforced server-side, not by hiding controls",
              "Authorisation matrix, 16 operations",
              "**Met.** Every protected operation refuses an anonymous caller; state-changing "
              "operations refuse a non-owner and leave the row unchanged."],
             ["NFR-12", "One-command install on clean Windows and macOS with no server or build "
                        "step",
              "Clean-environment installation",
              "**Met on Windows; partially verified on macOS.** The code is platform-independent "
              "and the launch path is a single command, but the team had no macOS machine to "
              "install on, so this is reasoned rather than observed."]],
            widths=[0.48, 1.4, 1.2, 3.2], chapter="6", size=8.8, number="Table 6.9")

    R.h2("C.5  Defect log (Table 6.10)")
    R.table("Defect log. Severity is recorded from the point of view of a user: high means the "
            "feature does not work, low means it works but is wrong in a detail.",
            ["#", "Defect", "Found by", "Resolution"],
            [["DF-01", "The stylesheet the document referenced did not exist under that name, so "
                       "the application rendered unstyled while every test passed",
              "Manual inspection of the running application",
              "**Fixed.** The stylesheet was recreated under the referenced name. The gap this "
              "exposes is that no automated case asserted that the page was styled."],
             ["DF-02", "The default product image referenced by the client did not exist on disk, "
                       "producing a broken image on every card without a photograph",
              "Browser network monitor during the scripted run",
              "**Fixed.** The placeholder became an inline icon block, so no file is required."],
             ["DF-03", "User-supplied text was interpolated into the document without escaping, "
                       "allowing script in a listing title to execute in another user's session",
              "Code review of the render paths",
              "**Fixed.** One escaping function is now applied to every interpolation. This was a "
              "high-severity defect and it is the reason NFR-10 exists as a requirement rather "
              "than as a convention."],
             ["DF-04", "After login the interface showed a placeholder initial instead of the "
                       "student's nickname, because the login response omits the display name",
              "Manual testing of the login flow",
              "**Fixed.** The client requests the full profile after a successful login. The "
              "underlying cause is that the login endpoint returns a subset of the profile, which "
              "is a defensible contract but was not documented."],
             ["DF-05", "The personal centre showed \"Anonymous\" for the student's own listings, "
                       "because those endpoints do not return a seller nickname",
              "Manual testing of the personal centre",
              "**Fixed in the client** by substituting a first-person label. The cleaner fix - "
              "returning the nickname from those endpoints - was not taken because it would change "
              "an interface that other code depends on."],
             ["DF-06", "The conversation list ordering is undefined when two messages share the "
                       "same timestamp, because ordering is by a column with one-second resolution",
              "Automated case TC-S14, which was written expecting newest-first ordering and failed",
              "**Open, documented.** The case was rewritten to assert only that both conversations "
              "survive the grouping, and the limitation is stated in section 5.7 and in section "
              "7.2. Fixing it means ordering by the timestamp with the identifier as a tie-breaker."],
             ["DF-07", "The three-photograph limit and the requirement for at least one photograph "
                       "are enforced only in the client, so a hand-built request can exceed them",
              "Requirements traceability review",
              "**Open, documented.** Neither omission corrupts data. Recorded in Table 5.3 and in "
              "section 7.2 rather than presented as a complete implementation of FR-06."],
             ["DF-08", "Deleting a listing physically would have left photographs orphaned on disk "
                       "and conversations referring to a missing item",
              "Design review, before implementation",
              "**Avoided by design.** Deletion is a soft delete; the trade-off is that "
              "photographs of offline listings are never reclaimed, which is recorded in decision "
              "D6."]],
            widths=[0.35, 1.85, 1.15, 2.92], chapter="6", size=8.8, number="Table 6.10")


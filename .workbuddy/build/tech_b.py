# tech_b.py - chapters 4 and 5 of the technical report
from docxkit import Report


def chapter4(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("4  System Design and Architecture")

    R.h2("4.1  Architectural Style and the Alternatives Considered")
    R.para("The system is a **three-tier layered web application**: a framework-free client that "
           "runs in the browser, a Flask application that owns all logic and all authorisation, and "
           "a thin persistence layer holding a single SQLite file and an upload directory. Each "
           "layer talks only to the layer beneath it, and the client never reaches the database "
           "directly.")
    R.para("The style was chosen against three alternatives, and the deciding factor in each case "
           "was constraint C1 from section 2.5 - the software must run on the assessor's machine "
           "with one command and no configuration.")
    R.table("Architectural alternatives and the reason each was rejected",
            ["Alternative", "Attraction", "Reason for rejection"],
            [["Three-tier layered (chosen)",
              "Separates presentation from logic and logic from storage; each layer can be changed "
              "independently; the whole system runs as one process with no external dependency",
              "Accepted. It satisfies C1 while still giving a clean separation of concerns and an "
              "obvious place for authorisation."],
             ["Server-rendered pages with a template engine",
              "Simpler than a client-side application: no JSON contract, no duplicated validation",
              "Rejected because the interface needs to update without a full page load - the "
              "comment thread, the favourite control and the chat panel all change in place. "
              "Server rendering would have meant a page reload for each one."],
             ["Single-page client with a separate API service",
              "The clearest separation of concerns, and the most common production shape",
              "Rejected because it requires either a second process or a cross-origin "
              "configuration. Both break C1, and cross-origin requests would additionally require "
              "the session cookie to be sent explicitly."],
             ["Microservices",
              "Independent deployment of accounts, listings and messaging",
              "Rejected as disproportionate. The whole application is roughly 1,700 lines; "
              "splitting it would add service discovery, inter-service contracts and distributed "
              "failure modes to solve a scaling problem the system does not have."]],
            widths=[1.35, 1.95, 2.9], chapter="4", size=9.5)

    R.h2("4.2  Layered Architecture")
    R.para("Figure 4.1 shows the three layers and the responsibility of each. The boundary that "
           "matters most is the one between the presentation layer and the application layer: the "
           "client holds no authority. Every rule that protects data - who may change what, what "
           "the status is allowed to become next, which file types may be stored - is enforced "
           "below the boundary. The client knows those rules only in order to give better feedback, "
           "and the design accepts the cost of writing some validation twice in exchange for a "
           "system that cannot be subverted by constructing a request by hand.")
    R.figure("figures/fig_arch_layers.png",
             "Layered architecture, showing the endpoint groups of the application layer and the "
             "components of the data layer", chapter="4")

    R.para("Two properties of this arrangement carry most of the design's weight. The "
           "presentation layer never reaches the database directly - every read and every write "
           "passes through a JSON endpoint - which means the application layer is the only place "
           "authorisation has to be correct. And the data layer is deliberately thin: it knows "
           "about tables and connections and nothing about rules. That thinness is what would make "
           "a future move to a hosted database a local change rather than a rewrite, and it is the "
           "reason the layer was kept thin even though the proof of concept does not need to be "
           "portable.")
    R.table("Responsibility of each layer, and what each layer is forbidden to do",
            ["Layer", "Owns", "Must not"],
            [["Presentation",
              "View state, rendering, event handling, immediate input validation, escaping of all "
              "user-supplied text before it is inserted into the document",
              "Hold authority over any data; construct SQL; be the only place a rule is enforced"],
             ["Application",
              "HTTP routing, session handling, authorisation, validation, the status state "
              "machine, construction of the JSON response envelope, file storage",
              "Contain presentation markup; assume that a request originated from the provided "
              "client"],
             ["Data",
              "Connection creation, the relational schema, uniqueness constraints, file storage on "
              "disk",
              "Contain business rules that the application layer also needs to know about"]],
            widths=[0.8, 2.7, 2.7], chapter="4", size=9.5)

    R.h2("4.3  Module Decomposition")
    R.para("Figure 4.2 shows the modules and the direction of each dependency. The decomposition "
           "follows Parnas's criterion of hiding the decisions most likely to change (Parnas, "
           "1972): the shape of the data model is hidden behind the data layer, the shape of the "
           "HTTP contract is hidden behind the client's request wrapper, and the specifics of "
           "password hashing and file-name sanitisation are hidden behind a third-party library.")
    R.figure("figures/fig_arch_modules.png",
             "Module decomposition and the direction of each dependency", chapter="4")

    R.table("Module inventory",
            ["Module", "Lines", "Responsibility", "Depends on"],
            [["app.py", "552", "The Flask application object and all 23 routes: accounts, "
                               "catalogue, listing management, upload, transactions, favourites, "
                               "comments, messaging and the personal centre",
              "models.py, Werkzeug"],
             ["models.py", "106", "Connection factory and schema creation for the six tables",
              "sqlite3"],
             ["templates/index.html", "441", "The single document: five view containers, two modal "
                                            "surfaces, an inline SVG icon sprite and the mount "
                                            "points for client rendering",
              "style.css, api.js, main.js"],
             ["static/js/api.js", "63", "One method per endpoint, so no URL is written twice and "
                                        "the request shape is defined in one place",
              "the HTTP endpoints"],
             ["static/js/main.js", "1169", "All view state, rendering, event binding, the hash "
                                           "router, escaping and the feedback layer",
              "api.js"],
             ["static/css/style.css", "1025", "Design tokens, component styles, responsive "
                                              "breakpoints", "nothing"]],
            widths=[1.2, 0.42, 3.2, 0.85], chapter="4", size=9.3)

    R.h2("4.4  Domain Model")
    R.para("Figure 4.3 presents the domain model. It is described as persistence-oriented because "
           "the system was built without an object-relational mapper: the classes in the diagram "
           "are realised as tables and as dictionaries returned from queries, not as Python "
           "classes. Modelling them this way was still worthwhile, because the association "
           "cardinalities are exactly what the schema must enforce.")
    R.figure("figures/fig_class_domain.png",
             "Domain class diagram, showing the six entities, their attributes and their "
             "associations", chapter="4")

    
    R.h2("4.5  Database Design")
    R.para("The schema has six tables, shown in Figure 4.4. It is in third normal form: every "
           "non-key attribute depends on the whole key and on nothing else. The design was checked "
           "against the normal forms deliberately, and one candidate denormalisation - storing a "
           "reference to the cover photograph on the item row - was rejected in favour of a "
           "correlated sub-query, because the sub-query is trivially correct and a duplicated "
           "column would have needed code to keep it in step with the images table.")
    R.figure("figures/fig_er.png",
             "Entity-relationship diagram of the six-table schema, with foreign keys and "
             "cardinality", chapter="4")

    R.table("Table specifications",
            ["Table", "Purpose", "Key", "Constraints and notes"],
            [["users", "One row per registered student",
              "id", "`username` is unique and not null; `password_hash` is not null; `nickname`, "
                    "`email`, `student_id` and `avatar` are optional"],
             ["items", "One row per listing; the aggregate root",
              "id", "`seller_id` references users; `title` not null; `price` not null and real; "
                    "`status` defaults to on sale; `updated_at` is written on every change"],
             ["images", "One row per photograph attached to a listing",
              "id", "`item_id` references items; `file_path` not null; the row stores the generated "
                     "file name, never a client-supplied one"],
             ["favorites", "The many-to-many association between a student and a saved listing",
              "id", "`user_id` and `item_id` both reference their tables; `UNIQUE(user_id, "
                    "item_id)` prevents a duplicate save"],
             ["comments", "A public question or answer attached to a listing",
              "id", "`item_id` and `user_id` both reference their tables; `content` not null"],
             ["messages", "A private message between two students, optionally about an item",
              "id", "`sender_id` and `receiver_id` both reference users; `item_id` references items "
                    "and is nullable; `is_read` defaults to zero"]],
            widths=[0.72, 1.75, 0.32, 3.48], chapter="4", size=9.3)

    R.para("Two properties of SQLite shaped the design and both are recorded as limitations "
           "rather than as oversights. The engine enforces declared foreign keys **only** when the "
           "connection is opened with `PRAGMA foreign_keys = ON`, and the proof of concept does not "
           "set that pragma; referential integrity is therefore currently a convention held up by "
           "the application layer. And `CURRENT_TIMESTAMP` resolves to whole seconds, which makes "
           "any ordering that relies on it alone unstable when two rows are written in the same "
           "second - a defect that the test suite found and that is reported in section 6.13.")

    R.h2("4.6  Transaction State Machine")
    R.para("The status field of a listing is modelled as an explicit state machine rather than as "
           "a free-text field that the interface happens to set. Figure 4.5 shows the four states "
           "and the five transitions, and Table 4.5 sets out the rules. The model is the single "
           "most important design decision in the project, because it is what makes the answer to "
           "\"is this still available?\" authoritative rather than advisory.")
    R.figure("figures/fig_state_item.png",
             "State machine governing the life cycle of a listing, with the actor and the guard "
             "for each transition", chapter="4")

    R.table("Status transition rules. The role and the source state are both required; a request "
            "that fails either check changes nothing.",
            ["Action", "From", "To", "Permitted actor", "Failure response"],
            [["reserve", "on sale", "reserved", "Any student except the seller",
              "403 if the caller is the seller; 400 if the status is not on sale"],
             ["sell", "reserved", "sold", "The seller",
              "403 if the caller is not the seller; 400 if the status is not reserved"],
             ["cancel_reserve", "reserved", "on sale", "The seller",
              "403 if the caller is not the seller; 400 if the status is not reserved"],
             ["off_shelf", "on sale", "off shelf", "The seller",
              "403 if the caller is not the seller; 400 if the status is not on sale"],
             ["relist", "off shelf", "on sale", "The seller",
              "403 if the caller is not the seller; 400 if the status is not off shelf"],
             ["(any other)", "-", "-", "-",
              "400 invalid action, before the item is even read"]],
            widths=[0.95, 0.68, 0.68, 1.5, 2.46], chapter="4", size=9.3)

    R.para("Sold has no outgoing transition, which is a deliberate choice rather than an omission: "
           "undeleting a completed sale would require tracking which buyer completed it and by what "
           "arrangement, and the proof of concept does not model the buyer side of a completed "
           "transaction at all. The consequence is that a mistaken confirmation cannot be undone "
           "through the interface, which is why the confirmation dialog for that action states "
           "explicitly that the listing will be marked as sold.")

    R.h2("4.7  Interaction Design")
    R.para("Three interactions carry most of the system's behaviour and are modelled in full. "
           "Between them they exercise every layer, both directions of the status machine, and the "
           "one query in the system whose correctness is not obvious from reading it.")

    R.h3("4.7.1  Publishing a listing")
    R.para("Figure 4.6 follows a publish action from the form submission to the committed rows. "
           "The sequence makes two design decisions explicit. The upload and the creation are "
           "separate requests, so the upload completes and returns file names before any listing "
           "row is written; a failure in the second step therefore cannot leave a listing that "
           "refers to a photograph that was never stored. And the listing row is written before the "
           "photograph rows, so that the generated key is available to be used as their foreign "
           "key - the reverse order would require a second read.")
    R.figure("figures/fig_seq_publish.png",
             "Sequence diagram for publishing a listing, from form submission to committed rows",
             chapter="4")

    R.h3("4.7.2  Reserving an item and confirming the sale")
    R.para("Figure 4.7 shows the two ends of the transaction. Both requests reach the same "
           "endpoint and are validated against the same rule table, which is the property that "
           "makes the state machine trustworthy: the two transitions cannot drift apart, because "
           "there is only one place where either is defined. The diagram also shows the failure "
           "path explicitly, because the behaviour of a rejected request - that the row is left "
           "untouched - is part of the specification rather than an implementation detail.")
    R.figure("figures/fig_seq_deal.png",
             "Sequence diagram for reserving an item and confirming the sale, including the two "
             "guards and the rejection path", chapter="4")

    R.h3("4.7.3  Conversations and messaging")
    R.para("Figure 4.8 covers the three messaging interactions. The conversation list is produced "
           "by a single aggregate query rather than one query per conversation, which matters "
           "because a student's conversation list grows without bound while the number of students "
           "they are talking to does not. Opening a thread both reads and writes: the messages are "
           "retrieved and the incoming ones are marked as read in the same request, so unread state "
           "cannot get out of step with what the student has actually seen.")
    R.figure("figures/fig_seq_message.png",
             "Sequence diagram for the conversation list, opening a thread and sending a reply",
             chapter="4")

    R.h2("4.8  Interface Design")
    R.para("The client interacts with the server through a small JSON interface. Figure 4.9 groups "
           "the endpoints by the resource they act on, and Table 4.6 lists them with the methods "
           "they accept and whether a session is required. Every endpoint answers with the same "
           "envelope, described in Table 4.7, so that the client can handle success and failure "
           "uniformly without inspecting the shape of the body.")
    R.figure("figures/fig_route_map.png",
             "The JSON endpoint surface, grouped by resource, with the methods and the session "
             "requirement of each endpoint", chapter="4")

    R.table("Endpoint catalogue. Session means that the endpoint refuses an unauthenticated "
            "request with 401 without evaluating the body.",
            ["Method", "Path", "Purpose", "Session"],
            [["POST", "/api/register", "Create an account", "No"],
             ["POST", "/api/login", "Authenticate and establish a session", "No"],
             ["POST", "/api/logout", "Terminate the session", "No"],
             ["GET", "/api/user/me", "Return the caller's own profile", "Yes"],
             ["GET", "/api/items", "Catalogue with keyword, category, status, sort and page", "No"],
             ["GET", "/api/items/<id>", "Listing detail with images and comments", "No"],
             ["POST", "/api/items", "Create a listing", "Yes"],
             ["PUT", "/api/items/<id>", "Edit a listing the caller owns", "Yes"],
             ["DELETE", "/api/items/<id>", "Take a listing offline (soft delete)", "Yes"],
             ["POST", "/api/upload", "Store one or more photographs and return their names", "Yes"],
             ["GET", "/uploads/<name>", "Serve a stored photograph", "No"],
             ["POST", "/api/items/<id>/status", "Apply a status transition", "Yes"],
             ["GET", "/api/favorites", "List the caller's saved listings", "Yes"],
             ["POST", "/api/favorites", "Save a listing", "Yes"],
             ["DELETE", "/api/favorites/<id>", "Unsave a listing", "Yes"],
             ["GET", "/api/items/<id>/comments", "Read the public comments on a listing", "No"],
             ["POST", "/api/items/<id>/comments", "Post a comment", "Yes"],
             ["GET", "/api/messages", "Conversation list, grouped by partner", "Yes"],
             ["POST", "/api/messages", "Send a private message", "Yes"],
             ["GET", "/api/messages/<uid>", "Read a thread and mark it read", "Yes"],
             ["GET", "/api/user/items", "The caller's own listings", "Yes"],
             ["GET", "/api/user/sold", "The caller's sold listings", "Yes"]],
            widths=[0.55, 1.75, 3.35, 0.62], chapter="4", size=9.2)

    R.table("The response envelope shared by every endpoint",
            ["Situation", "HTTP status", "Body", "Client behaviour"],
            [["Success with a body", "200", "`{ code: 200, data: … }`",
              "Render the data"],
             ["Success without a body", "200", "`{ code: 200, msg: '…' }`",
              "Show the message as a confirmation"],
             ["Validation failure", "400", "`{ code: 400, msg: '<reason>' }`",
              "Show the reason as an error next to the offending control"],
             ["Not authenticated", "401", "`{ code: 401, msg: '…' }`",
              "Redirect to the authentication view and remember the intent"],
             ["Not permitted", "403", "`{ code: 403, msg: '<reason>' }`",
              "Show the reason; do not retry"],
             ["Not found", "404", "`{ code: 404, msg: '…' }`",
              "Show an empty state with a way back"],
             ["Payload too large", "413", "HTML error page from the framework",
              "Report that the file exceeds the 5 MB limit"]],
            widths=[1.15, 0.72, 1.9, 2.5], chapter="4", size=9.3)

    R.h2("4.9  Client-Side Design")
    R.para("The client is a single document with five view containers that are shown and hidden by "
           "a small router, shown in Figure 4.10. Three design decisions distinguish it. The "
           "**hash route** `#item-<id>` makes an individual listing addressable, so a listing can "
           "be pasted into a message and will open directly on the detail view; the route is parsed "
           "both on load and on every change of the hash. The **guards are duplicated**: the client "
           "redirects an anonymous visitor away from the publishing and personal views, and the "
           "server independently refuses the same requests. And **hidden containers are not "
           "rebuilt**: switching views re-renders only the content that has changed, so a "
           "half-typed listing form survives a trip to the catalogue.")
    R.figure("figures/fig_ui_states.png",
             "The client-side view router: five views, the persistent header, and the guards on "
             "the views that require a session", chapter="4")

    R.h2("4.10  Design Decisions and Trade-offs")
    R.para("Table 4.8 records the decisions that shaped the system, the alternative in each case, "
           "and the cost that was knowingly accepted. Recording the rejected alternative matters: "
           "a decision log that lists only what was chosen cannot be reviewed, because there is no "
           "way to tell whether the alternative was considered and rejected or simply never "
           "noticed.")
    R.table("Design decision log",
            ["#", "Decision", "Alternative rejected", "Trade-off accepted"],
            [["D1", "A single Flask process serving both the client and the API",
              "A separate API service or a second process",
              "The client and the server cannot be deployed or scaled independently. Accepted "
              "because C1 forbids a second process."],
             ["D2", "SQLite as the store",
              "PostgreSQL or a hosted relational service",
              "No concurrent writers, no network access for other clients, and foreign keys "
              "unenforced by default. Accepted because the schema then travels with the submission "
              "and nothing has to be installed."],
             ["D3", "No object-relational mapper",
              "SQLAlchemy or an equivalent",
              "All 29 statements are written by hand and the schema shape is visible in the route "
              "handlers. Accepted because the query set is small and the aggregate in section 5.7 "
              "is easier to express directly than through a mapper."],
             ["D4", "Validation duplicated in the browser and on the server",
              "Server-only validation",
              "Some rules are written twice, and the two copies can drift. Accepted because "
              "client-only validation is not validation at all, and server-only validation gives "
              "the user a round trip before any feedback."],
             ["D5", "A rule table driving the status transitions",
              "A chain of conditional statements per action",
              "The legal transitions are described in a data structure rather than in control flow, "
              "which some readers find less direct. Accepted because the rule set is readable in "
              "one place and cannot disagree with the enforcement."],
             ["D6", "Soft deletion for listings",
              "Removing the row and its photographs",
              "Offline listings remain in the database and their photographs are never reclaimed. "
              "Accepted because the seller's history and the buyer's conversation remain coherent, "
              "and because a mistaken deletion is recoverable."],
             ["D7", "Generated file names for uploads",
              "Keeping the name supplied by the client",
              "Uploaded files are not identifiable by name on disk. Accepted because a "
              "client-supplied name is a path-traversal risk and can collide with an existing file."],
             ["D8", "Two independent guards on every transition",
              "The role check alone",
              "One extra read per request, and one more failure mode to test. Accepted because the "
              "role check answers who and the state check answers when, and a reservation that "
              "overwrote a completed sale would be a correctness failure."],
             ["D9", "A single aggregate query for the conversation list",
              "One query per conversation, or caching the list",
              "The query is harder to read than a simple select. Accepted because it keeps the cost "
              "constant as the number of conversations grows, and the alternative is a query per "
              "row of the list being rendered."],
             ["D10", "No payment capability",
              "An integrated payment provider",
              "The platform cannot take a commission, and handover must be arranged between the "
              "two students. Accepted deliberately: payment would bring financial regulation, "
              "dispute resolution and fraud handling into a course project."]],
            widths=[0.32, 1.35, 1.15, 3.45], chapter="4", size=9)


def chapter5(R):
    R.reset_figure_counter()
    R.reset_table_counter()
    R.h1("5  Implementation")

    R.h2("5.1  Technology Stack")
    R.para("The proof of concept is written in Python with Flask, uses SQLite for storage, and "
           "serves a client built from plain HTML, CSS and JavaScript with no framework and no "
           "build step. Figure 5.1 gives the reasoning behind each choice; every component was "
           "selected against one test - can the assessor obtain and run it without a paid account, "
           "a container runtime or a compilation step?")
    R.figure("figures/fig_stack.png",
             "Technology choices and the reasoning behind each one", chapter="5")

    R.table("Component versions and roles",
            ["Component", "Version", "Role in the system"],
            [["Python", "3.8 or later (developed on 3.13)", "Runtime for the application and the "
                                                             "test suite"],
             ["Flask", "2.3.3", "Routing, request parsing, signed sessions and JSON responses"],
             ["Werkzeug", "2.3.7", "Password hashing and file-name sanitisation"],
             ["SQLite", "3 (bundled with Python)", "Relational storage, one file on disk"],
             ["pytest", "9.x", "Test runner used for the suite reported in Chapter 6"],
             ["Playwright (Node)", "via playwright-core", "Drives Microsoft Edge for the interface "
                                                          "verification and the screenshots in "
                                                          "this report"]],
            widths=[1.2, 1.3, 3.77], chapter="5")

    R.h2("5.2  Software Structure and Size")
    R.para("Table 5.2 gives the size of each component of the delivered software. The distribution "
           "is worth noting: the client is longer than the server, which is the expected shape for "
           "a system whose complexity lies in interaction rather than in computation. The server "
           "is 658 lines for 21 JSON endpoints, an average of 31 lines per endpoint including "
           "validation and authorisation.")
    R.table("Size of each component of the delivered software",
            ["Component", "Lines", "Share"],
            [["static/js/main.js", "1,169", "34%"],
             ["static/css/style.css", "1,025", "30%"],
             ["app.py", "552", "16%"],
             ["templates/index.html", "441", "13%"],
             ["models.py", "106", "3%"],
             ["static/js/api.js", "63", "2%"],
             ["tests/ (test suite and harnesses)", "~1,300", "not part of the runtime"],
             ["**Total runtime code**", "**3,356**", "**100%**"]],
            widths=[2.6, 1.2, 1.0], chapter="5", align=[None, "r", "r"])

    R.h2("5.3  Accounts, Sessions and Credential Storage")
    R.para("Registration accepts a username, a password and three optional profile fields. The "
           "password is never stored: it is passed through a salted key-derivation function and "
           "only the resulting hash is written to the database. The implementation deliberately "
           "uses the library's default parameters rather than choosing its own, on the principle "
           "that a hand-rolled KDF is a liability (OWASP, 2024). A test asserts that the stored "
           "value does not contain the submitted password and that it carries the expected "
           "algorithm prefix, so a future change that accidentally stored the plaintext would fail "
           "the suite rather than pass silently.")
    R.para("Sessions are held in Flask's signed session cookie. The application's only interaction "
           "with them is to write the authenticated user's identifier on login and to remove it on "
           "logout. A decorator applied to every protected route reads that identifier and refuses "
           "the request with 401 if it is absent. Because the decorator is applied at the route "
           "level rather than checked inside handlers, a new endpoint added without it stands out "
           "immediately in review - and the authorisation matrix in section 6.7 exists to make that "
           "failure mode impossible to miss.")

    R.h2("5.4  The Catalogue Query")
    R.para("The catalogue endpoint accepts five optional parameters - keyword, category, status, "
           "sort and page - and builds one statement from them. The construction is done by "
           "appending fragments to a list of conditions and extending a parallel list of bound "
           "parameters, never by interpolating values into the statement text. The distinction "
           "matters: interpolating a keyword would make the search box an injection point, whereas "
           "binding it cannot. The same condition list is reused to build the counting query, so "
           "the total that drives the pagination control is computed from exactly the same filter "
           "as the page it describes.")
    R.para("The cost of the wildcard search is a full scan of the items table, because a leading "
           "wildcard cannot use an index. At the scale the proof of concept operates on this is "
           "irrelevant, and section 6.10 measures it; at a larger scale the answer is a full-text "
           "index rather than a change to the query.")

    R.h2("5.5  Photograph Upload and Storage")
    R.para("Upload is the one part of the system that touches the filesystem, and it is treated "
           "accordingly. The endpoint accepts a multipart request containing one or more files, "
           "checks each file's extension against an allow-list, derives the extension from a "
           "sanitised copy of the supplied name, and then writes the file under a name generated "
           "from a random universally unique identifier. The name supplied by the client is used "
           "for nothing except to read its extension. Table 5.3 lists the rules and where each is "
           "enforced.")
    R.table("Validation rules applied to an upload or a listing, and where each is enforced",
            ["Rule", "Limit", "Enforced in the browser", "Enforced on the server"],
            [["Accepted file types", "png, jpg, jpeg, gif, webp", "By MIME type at selection",
              "By extension against the allow-list"],
             ["Maximum size per file", "5 MB", "At selection",
              "By the framework's request size limit (413)"],
             ["Maximum files per listing", "3", "At selection",
              "Not enforced; the client is the only place the limit is applied"],
             ["Title required", "Non-empty", "Before submission", "Before the row is written"],
             ["Price required and numeric", "Not negative", "Before submission",
              "Before the row is written"],
             ["At least one photograph", "One", "Before submission",
              "Not enforced; a listing may legitimately have no photograph"]],
            widths=[1.35, 1.15, 1.5, 2.27], chapter="5", size=9.3)

    R.para("The last two rows of Table 5.3 are the honest gaps. The three-photograph cap and the "
           "requirement for at least one photograph exist only in the client. A request constructed "
           "by hand can publish a listing with no photograph or with thirty. Neither omission "
           "corrupts data, and the interface never produces such a request, so the risk was accepted "
           "for the proof of concept and is listed as a defect to fix rather than presented as a "
           "complete implementation of the requirement.")

    R.h2("5.6  The Status Machine")
    R.para("The status machine is implemented as a dictionary that maps each action to the "
           "required source state, the resulting state and the role permitted to perform it. The "
           "endpoint then performs the same five steps for every action, shown in Figure 5.2: "
           "reject an unknown action, load the item and reject a missing one, check the role, check "
           "the source state, and only then write. Because the steps are shared, adding a state "
           "would mean adding one entry to the table and one control to the interface, with no "
           "change to the logic that validates transitions.")
    R.figure("figures/fig_algo_status.png",
             "How a status request is validated before the row is written, driven by a five-entry "
             "rule table", chapter="5")

    R.para("Two design choices in this component are worth defending. The action is validated "
           "against the table **before the item is read**, so an unknown action costs nothing and "
           "cannot reveal whether an item exists. And the write is the final step with no "
           "conditional logic after it, which is what guarantees the property the tests assert: a "
           "request that fails any check leaves the row exactly as it was.")

    R.h2("5.7  The Conversation List Query")
    R.para("The conversation list is the one algorithm in the system that needed actual thought. "
           "The requirement is to show one row per person the student is talking to, containing the "
           "most recent message in that thread. The obvious implementation - iterate the student's "
           "messages, work out the other party for each, and keep the newest per person - costs one "
           "pass in the application and requires either a query per conversation or all messages "
           "loaded into memory. Figure 5.3 shows the single aggregate query that replaces it.")
    R.figure("figures/fig_algo_conversation.png",
             "Rendering the conversation list with one aggregate query instead of a query per "
             "conversation", chapter="5")

    R.para("The query works in two parts. The inner part groups the student's messages by the "
           "other party, using a conditional expression to normalise the pair of sender and "
           "receiver into a single identity regardless of direction, and selects the largest "
           "identifier in each group. The outer part joins back to the messages table on that "
           "identifier and to the users table to obtain the partner's display name. The cost is one "
           "pass plus one grouped sub-query, and it does not grow with the number of conversations.")
    
    R.h2("5.8  Client-Side Implementation")
    R.para("The client is one document containing five view containers, two modal surfaces, an "
           "inline icon sprite and the mount points that the rendering code fills. All rendering "
           "is driven from state held in module-level variables, and every path that inserts "
           "user-supplied text into the document passes it through an escaping function first. That "
           "function is the system's principal defence against cross-site scripting, and it is "
           "applied to titles, descriptions, comment bodies, message bodies, nicknames and file "
           "names. Table 5.4 lists the paths and what each escapes.")
    R.table("Client-side rendering paths and the escaping applied to each",
            ["Rendering path", "User-supplied values interpolated", "Escaping"],
            [["Listing card", "title, seller nickname, price, category", "All values escaped; the "
              "price is coerced to a number before formatting"],
             ["Listing detail", "title, description, seller nickname and email, category, "
              "condition", "All values escaped"],
             ["Comment list", "author nickname, body, relative time",
              "All values escaped; times are formatted, never inserted raw"],
             ["Chat and conversation list", "message body, partner nickname",
              "All values escaped"],
             ["Publish preview", "title, price, category",
              "All values escaped; the preview is built by the same function as the catalogue card"],
             ["Profile head", "nickname, username, student identifier", "All values escaped"],
             ["Toast and confirm dialog", "server-supplied message",
              "Escaped for toasts; the confirm dialog assigns through `textContent`, which cannot "
              "create markup at all"]],
            widths=[1.35, 2.0, 2.92], chapter="5", size=9.3)

    
    R.h2("5.9  Design System")
    R.para("The visual language is defined once, as custom properties on the document root, and "
           "every component style refers to those properties rather than to literal values. Table "
           "5.5 lists the token groups. The practical benefit is that the whole theme can be "
           "retuned from one place, and the review benefit is that a component that hard-codes a "
           "colour stands out when the file is read.")
    R.table("Design token groups and what each controls",
            ["Group", "Tokens", "Used for"],
            [["Colour", "Surface, surface-muted, border, ink, ink-muted, accent, accent-soft, "
                        "success, danger, warning",
              "Every background, border, text colour and status badge in the interface"],
             ["Typography", "Two sizes for body text, four for headings, one monospace family, a "
                            "single line-height scale",
              "All text; no component sets its own font size outside the scale"],
             ["Spacing", "A five-step scale from 4 px to 40 px",
              "All margins, padding and grid gaps"],
             ["Radius and elevation", "Three radii and three shadow levels",
              "Cards, buttons, dialogs and the sticky purchase panel"],
             ["Breakpoints", "1040 px, 900 px, 760 px",
              "Collapsing the detail page to one column, the grid to two columns, and the header "
              "to a compact form"]],
            widths=[1.05, 2.3, 2.92], chapter="5", size=9.3)

    R.h2("5.10  User Interface")
    R.para("The interface is presented as a sequence of states rather than as one screenshot per "
           "screen, because the states that carry the most design work are the ones that appear "
           "only when something is empty or when a request is refused. Every figure below was "
           "captured from the delivered software driving a real browser at a 1240-pixel viewport, "
           "and the capture run reported no console errors and no unexpected 4xx or 5xx responses. "
           "The figures are cropped to the region under discussion: a full-page capture reduced to "
           "the width of a printed text column leaves body type around five points, which is not "
           "readable, whereas a crop placed at a smaller physical width keeps it at eight or nine.")

    R.h3("5.10.1  Browsing the catalogue")
    R.para("The catalogue is the entry point and has to work for a visitor with no account. "
           "Figure 5.4 shows the listing grid with its sort control. The cards carry the status "
           "badge, the cover photograph, the price, the seller and the category, which is the set "
           "of attributes the competitive review in section 2.2 identified as the ones a buyer "
           "screens on.")
    R.figure("figures/ui_crop_grid.png",
             "The catalogue grid: status badge, cover image, price, seller and category on each "
             "card", chapter="5", width_in=6.2)

    R.para("Figure 5.5 shows the empty state. It is included deliberately, because the empty state "
           "is where projects of this shape usually stop: the grid simply stays blank and the user "
           "cannot tell whether nothing matched or something failed. The implementation names the "
           "condition and offers a next step.")
    R.figure("figures/ui_crop_empty.png",
             "The empty search result: the condition is named and a next step offered, instead of "
             "leaving the grid blank", chapter="5", width_in=5.4)

    R.h3("5.10.2  Reading a listing and acting on it")
    R.para("The detail view is the densest screen and the one where the status machine becomes "
           "visible to a user. Figures 5.6 and 5.7 show the same listing from the two sides of a "
           "transaction. For a signed-in buyer who is not the seller, the available actions are to "
           "reserve the item, to save it and to message the seller, and the safety panel states the "
           "platform's position on payment plainly. For the seller, the action set is entirely "
           "different: take the listing offline while it is on sale, or confirm the sale and cancel "
           "the reservation while it is reserved. The interface is role-aware, but the authority "
           "behind it is not - the server would refuse the same actions from the wrong account even "
           "if the controls were present, which is what the authorisation matrix in section 6.7 "
           "establishes.")
    R.figure("figures/ui_crop_buy_panel.png",
             "The detail view as a signed-in buyer sees it: reserve, save and message, with the "
             "seller and the structured attributes", chapter="5", width_in=4.3)
    R.figure("figures/ui_crop_sell_panel.png",
             "The same view for the seller: the buying actions are replaced by the management "
             "actions", chapter="5", width_in=4.3)

    R.para("Figure 5.8 shows the confirmation dialog that guards taking a listing offline. Every "
           "destructive or hard-to-reverse action is routed through this dialog, and it states "
           "what will happen rather than asking a bare \"are you sure?\"")
    R.figure("figures/ui_crop_confirm.png",
             "The shared confirmation dialog used for every destructive action in the interface",
             chapter="5", width_in=4.4)

    R.h3("5.10.3  Publishing")
    R.para("Figure 5.9 shows the publishing form. Three decisions are visible. The category and "
           "condition are chip selectors rather than dropdowns, kept in step with hidden select "
           "elements so the form remains submittable without script. The photograph control is a "
           "drop zone that also accepts a click, with thumbnails that can be removed individually. "
           "And a live preview of the listing card sits beside the form, built by the same function "
           "that renders the catalogue, so what the seller sees is what buyers will see.")
    R.figure("figures/ui_crop_publish.png",
             "The publishing form: chip selectors for category and condition, a photograph drop "
             "zone, and validation messages attached to the field that failed",
             chapter="5", width_in=4.6)

    R.h3("5.10.4  The personal centre and messaging")
    R.para("The personal centre gathers everything belonging to the signed-in student behind four "
           "tabs. Figure 5.10 shows the profile head with its three summary counts and the "
           "own-listings tab; the saved listings and sold tabs reuse the same card component as the "
           "catalogue, which is why the grid looks identical in all three places.")
    R.figure("figures/ui_crop_profile.png",
             "The personal centre: profile summary with counts, and the student's own listings",
             chapter="5", width_in=6.0)

    R.para("Figure 5.11 shows an open conversation. Messages from the student and from the other "
           "party are aligned differently and labelled with relative times, the panel scrolls to "
           "the most recent message, and Enter sends. The panel is labelled a direct message rather "
           "than a live chat, because the implementation fetches on opening and after sending "
           "rather than polling - a deliberate choice, since polling would spend the system's "
           "complexity budget on a feature the evaluation does not require. The relative time is "
           "computed in the browser from the stored timestamp, and the parsing normalises the value "
           "to UTC explicitly first, because the database stores timestamps without a zone and a "
           "naive parse produces an error equal to the machine's offset from UTC.")
    R.figure("figures/ui_crop_chat.png",
             "An open conversation: own and other messages distinguished, relative times, and the "
             "composer anchored to the bottom", chapter="5", width_in=4.3)

    R.h3("5.10.5  Small screens")
    R.para("Figure 5.12 shows the interface at a 400-pixel viewport, a typical large-phone width. "
           "The grid collapses to two columns, the header reduces to the brand, the search field "
           "and a compact action, and the detail page collapses to a single column with the "
           "purchase panel below the gallery. This is the viewport used for requirement NFR-05.")
    R.figure("figures/ui_mobile_home.png",
             "The interface at a 400-pixel viewport: the grid collapses to two columns and the "
             "header reduces to its essential controls", chapter="5", width_in=2.7)

    R.h2("5.11  Coding Standards and Conventions")
    R.para("The code follows a small set of conventions that were agreed before implementation and "
           "checked in review. They are recorded here because they are part of what the software "
           "engineering assessment examines, and because a convention that is not written down "
           "cannot be enforced.")
    R.table("Coding conventions applied across the codebase",
            ["Convention", "Rationale"],
            [["Every SQL statement binds its parameters; no value is ever interpolated into "
              "statement text",
              "Removes injection as a class of defect rather than defending against it case by case"],
             ["Every response uses the same `{ code, msg, data }` envelope",
              "The client can handle success and failure in one place instead of inspecting bodies"],
             ["Every protected route carries the same authorisation decorator",
              "A missing guard is visible at the route definition rather than hidden inside a "
              "handler"],
             ["Database connections are opened and closed inside the request that uses them, and "
              "closed on every path including the error paths",
              "SQLite is file-based, so a leaked connection holds a lock rather than a socket"],
             ["Client code escapes every interpolated value through one shared function",
              "One place to get right, and a reviewable list of what is escaped"],
             ["No CSS value is written outside the token set except where a token would be "
              "meaningless",
              "Keeps the visual language consistent and makes a deviation visible"],
             ["No SQL and no HTML is constructed by string concatenation in the data layer",
              "Keeps the layering honest: the data layer knows about tables, not about markup"]],
            widths=[2.7, 3.57], chapter="5", size=9.5)

    R.h2("5.12  Deployment and Reproducibility")
    R.para("The application starts with a single command, `python app.py`, on any machine with "
           "Python 3.8 or later and the two declared dependencies installed. On first run it "
           "creates the database file and the upload directory, so a clean checkout becomes a "
           "running system without a migration or a seeding step. The repository ships with a "
           "demonstration dataset so every screen has content, and with a backup of the empty "
           "database so the data can be removed without editing the schema.")
    
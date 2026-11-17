from datetime import datetime, date, timedelta, timezone
from library_kb import SITE, LINKS, LIBRARY_DATA, FLOOR_PLAN
from preprocess import parse_date_from_text

FALLBACK = "Sorry, I could not understand your query. Kindly rephrase it and try again."

AREA_NAMES = {
    "main": "Main Library (reading halls)",
    "outer": "Outer Reading Area",
    "circulation": "Circulation Counter",
}
DAY_ORDER = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
IST = timezone(timedelta(hours=5, minutes=30))


def _to_min(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def _to_12(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    ap = "PM" if h >= 12 else "AM"
    return f"{((h + 11) % 12) + 1}:{m:02d} {ap}"


def _slot_for(area: str, day: str):
    if day == "sunday":
        return None
    t = LIBRARY_DATA["timings"][area]
    s = t["saturday"] if day == "saturday" else t["weekday"]
    return (_to_min(s[0]), _to_min(s[1]))


def _ist_now():
    now = datetime.now(IST)
    day = DAY_ORDER[(now.weekday() + 1) % 7]
    minutes = now.hour * 60 + now.minute
    return day, minutes


def _next_open(area: str, day: str, minutes: int) -> str:
    start = DAY_ORDER.index(day)
    for i in range(8):
        d = DAY_ORDER[(start + i) % 7]
        s = _slot_for(area, d)
        if not s:
            continue
        if i == 0 and minutes >= s[0]:
            continue
        when = "today" if i == 0 else ("tomorrow" if i == 1 else d.capitalize())
        return f"opens {when} at {_to_12(s[0])}"
    return "closed"


def _fmt_date(d: date) -> str:
    return d.strftime("%A, %d %B %Y")


class ResponseEngine:
    def __init__(self):
        # session_id -> {"mode": "fine_days"|"fine_books"|"due_date", "data": {...}}
        self.sessions = {}

    def get_pending_mode(self, session_id: str):
        state = self.sessions.get(session_id)
        return state["mode"] if state else None

    def _set_pending(self, session_id: str, mode: str, data: dict = None):
        self.sessions[session_id] = {"mode": mode, "data": data or {}}

    def _clear_pending(self, session_id: str):
        self.sessions.pop(session_id, None)

    def handle_pending(self, session_id: str, raw: str, entities: dict):
        state = self.sessions.get(session_id)
        if not state:
            return None

        text = raw.strip()
        if text.lower() in {"cancel", "stop", "exit", "skip", "no", "nope", "never mind", "nevermind", "back"}:
            self._clear_pending(session_id)
            return "Okay, skipped. What else can I help you with?"

        mode = state["mode"]

        if mode == "fine_days":
            due_dt = parse_date_from_text(text)
            days = None
            books = entities.get("books", 1)
            if due_dt and "today" not in text.lower():
                days = (datetime.now(IST).date() - due_dt).days
            elif "days" in entities:
                days = entities["days"]
            elif text.isdigit():
                days = int(text)

            if days is None:
                return None  # Let ML router classify if user asked a different question

            if days > 36500:
                return "That looks too large — please check the number of days and try again."
            if days <= 0:
                self._clear_pending(session_id)
                if due_dt:
                    return f"The due date **{_fmt_date(due_dt)}** has not passed yet, so there is **no fine**. 🎉"
                return self._fine_result(0, 1)

            if "books" in entities:
                self._clear_pending(session_id)
                return self._fine_result(days, books)

            self._set_pending(session_id, "fine_books", {"days": days})
            return (
                self._fine_result(days, 1)
                + "\n**Fine is charged per book.** If more than one book is overdue, type the number of books (or ask something else)."
            )

        if mode == "fine_books":
            if "books" in entities or text.isdigit():
                books = entities.get("books") or max(1, int(text))
                days = state["data"]["days"]
                self._clear_pending(session_id)
                return self._fine_result(days, books)
            self._clear_pending(session_id)
            return None

        if mode == "due_date":
            res = self._compute_due(raw, entities)
            if res:
                self._clear_pending(session_id)
                return res
            return None

        self._clear_pending(session_id)
        return None

    def _timing_answer(self, entities: dict) -> str:
        d = entities.get("day")
        if d:
            label = d.capitalize()
            if d == "sunday":
                return f"### {label}\nThe library is **closed on Sundays** and on institute-declared holidays.\n~ Source: [Library Timings]({LINKS['timings']})"
            lines = [
                f"- **{AREA_NAMES[a]}:** {_to_12(_slot_for(a, d)[0])} – {_to_12(_slot_for(a, d)[1])}"
                for a in ("main", "outer", "circulation")
            ]
            return f"### {label} timings\n" + "\n".join(lines) + f"\n~ Source: [Library Timings]({LINKS['timings']})"

        rows = []
        for a in ("main", "outer", "circulation"):
            w = _slot_for(a, "monday")
            s = _slot_for(a, "saturday")
            rows.append(f"| {AREA_NAMES[a]} | {_to_12(w[0])} – {_to_12(w[1])} | {_to_12(s[0])} – {_to_12(s[1])} |")

        return "\n".join([
            "### Library Timings",
            "| Area | Mon – Fri | Saturday |",
            "|---|---|---|",
            *rows,
            "- **Closed** on all Sundays and institute-declared holidays.",
            "- During exams the library stays open **till midnight on all days**.",
            "- Books can be issued/returned only during **Circulation Counter** hours.",
            "Ask “Is the library open now?” for a live status.",
            f"~ Source: [Library Timings]({LINKS['timings']})",
        ])

    def _open_now_answer(self) -> str:
        day, minutes = _ist_now()
        label = day.capitalize()
        lines = []
        for a in ("main", "outer", "circulation"):
            s = _slot_for(a, day)
            if s and s[0] <= minutes < s[1]:
                lines.append(f"- **{AREA_NAMES[a]}:** 🟢 Open (closes at {_to_12(s[1])})")
            else:
                lines.append(f"- **{AREA_NAMES[a]}:** 🔴 Closed ({_next_open(a, day, minutes)})")
        return "\n".join([
            f"### Library status — {label}, {_to_12(minutes)} IST",
            *lines,
            f"This uses the regular timetable. It does not know about institute holidays — see the [holiday list 2026]({LINKS['holidays']}) — and hours are extended till midnight during exams.",
            f"~ Source: [Library Timings]({LINKS['timings']})",
        ])

    def _fine_details(self) -> str:
        rate = LIBRARY_DATA["fineRate"]
        return "\n".join([
            "### Library Fine Calculation",
            f"- **Rate:** ₹{rate}.00 per day per book once a book is past its due date.",
            "- **Formula:** Fine = overdue days × number of books × ₹1",
            "- Fine rules apply to **all** user categories.",
            "- You must clear outstanding amounts before any further issue, return or renew.",
            "- Reminder emails: advance due, due, and overdue (three times).",
            "- Away from campus? Request a temporary extension at library-cs@staff.manit.ac.in (Librarian’s approval needed).",
            "- Lost or damaged items are different: see “lost book/card”. You can pay fines online — ask “pay fine online”.",
            f"~ Source: [Circulation Policies – Fine Rules]({LINKS['circulation']})",
        ])

    def _fine_result(self, days: int, books: int) -> str:
        rate = LIBRARY_DATA["fineRate"]
        if days <= 0:
            return "### Your Fine\nNo fine — the book is not overdue. 🎉"
        total = days * books * rate
        return "\n".join([
            "### Your Fine",
            f"- Overdue days: **{days}**",
            f"- Books: **{books}**",
            f"- Rate: **₹{rate} per day per book**",
            f"- **Total fine: ₹{total}**  ({days} × {books} × ₹{rate})",
            "The fine keeps growing until the book is returned. The library’s own record at the circulation desk is final.",
        ])

    def _due_details(self) -> str:
        return "\n".join([
            "### Book due date",
            "| Category | Loan period |",
            "|---|---|",
            "| Faculty members | 180 days |",
            "| Students, PhD scholars, staff | 90 days (renewable once for 90 more days) |",
            "| Book Bank (PG/UG) | 365 days |",
            "Your exact due date is also in the issue email you receive.",
            f"~ Source: [Circulation Policies]({LINKS['circulation']})",
        ])

    def _compute_due(self, raw: str, entities: dict):
        issued_iso = entities.get("date")
        issued = date.fromisoformat(issued_iso) if issued_iso else parse_date_from_text(raw)
        if not issued:
            return None

        all_cats = [
            {"key": "faculty", "label": "Faculty (180 days)", "n": 180},
            {"key": "student", "label": "Students / PhD scholars / staff (90 days)", "n": 90},
            {"key": "bank", "label": "Book Bank (365 days)", "n": 365},
        ]
        cat = entities.get("category")
        if cat == "faculty":
            chosen = [all_cats[0]]
        elif cat == "book_bank":
            chosen = [all_cats[2]]
        elif cat == "student":
            chosen = [all_cats[1]]
        else:
            chosen = all_cats

        today = datetime.now(IST).date()
        lines = []
        for c in chosen:
            due = issued + timedelta(days=c["n"])
            left = (due - today).days
            if left > 0:
                status = f"{left} day{'' if left == 1 else 's'} left"
            elif left == 0:
                status = "due **today**"
            else:
                od = -left
                status = f"**overdue by {od} day{'' if od == 1 else 's'}** → fine ₹{od} per book"
            lines.append(f"- **{c['label']}:** {_fmt_date(due)} — {status}")

        return "\n".join([
            "### Due date calculation",
            f"Issue date: **{_fmt_date(issued)}**",
            *lines,
            "(Non-faculty members can renew once for another 90 days.) Dates are calendar days counted from the issue date; your issue email has the official due date.",
        ])

    def _floor_answer(self, entities: dict) -> str:
        fl = entities.get("floor")
        names = {"ground": "Ground Floor", "first": "First Floor", "second": "Second Floor"}
        out = []
        if fl in names:
            out.append(f"### {names[fl]} (all parts)")
            for part, f in FLOOR_PLAN.items():
                out.append(f"**{part}**")
                out.extend(f"- {item}" for item in f[fl])
        else:
            out.extend(["### Library Floor Plan", "The library has **three parts**, each with three floors:"])
            for part, f in FLOOR_PLAN.items():
                out.append(f"**{part}**")
                out.append(f"- Ground: {', '.join(f['ground'])}")
                out.append(f"- First: {', '.join(f['first'])}")
                out.append(f"- Second: {', '.join(f['second'])}")
            out.append("Ask “Where is Computer Science?” (or any subject) to find its floor, or “ground floor” for one floor.")
        out.append(f"~ Source: [Floor Plan]({LINKS['floor']}) · [What is Where]({LINKS['whatIsWhere']}) · [Shelve Guide]({LINKS['shelve']})")
        return "\n".join(out)

    def _subject_answer(self, entities: dict) -> str:
        subjects = entities.get("subjects") or []
        if not subjects:
            return self._floor_answer(entities)
        out = []
        for s in subjects:
            out.append(f"### {s['name']}")
            out.append(f"📍 {s['where']}")
            if s.get("note"):
                out.append(s["note"])
        out.append(f"Search the [e-Catalogue]({LINKS['catalogue']}) for the exact call number and availability, then match it to the shelf label.")
        out.append(f"~ Source: [Floor Plan]({LINKS['floor']}) · [Shelve Guide]({LINKS['shelve']})")
        return "\n".join(out)

    def generate(self, intent: str, raw: str, entities: dict, session_id: str = "default") -> str:
        if intent == "greeting":
            return (
                "Hello! I am **LibroBot**, the MANIT Central Library assistant.\n"
                "I can guide you through **issuing books**, **fines**, **due dates**, timings, floors, "
                "e-resources, research support and contacts. Tap a quick question below or type your own."
            )

        if intent == "help":
            return "\n".join([
                "### What I can help with",
                "- **Borrowing:** how to issue a book, loan limits, return/renew, membership, lost card/book, no dues",
                "- **Calculators:** fine (I will ask the number of days) and due date (I will ask the issue date)",
                "- **Visiting:** timings, live “open now?” status, rules, floor plan, subject-to-floor finder, facilities",
                "- **Resources:** e-catalogue, digital resources, databases, e-journals, e-books, theses, remote access",
                "- **Research:** plagiarism check, research tools, request a book/article, orientation sessions",
                "- **Reach us:** contacts, address, social media, holidays",
            ])

        if intent == "thanks":
            return "You’re welcome! Ask me anything else about the library whenever you like. 📚"

        if intent == "open_now":
            if entities.get("day") and not entities.get("is_now"):
                return self._timing_answer(entities)
            return self._open_now_answer()

        if intent == "timings":
            return self._timing_answer(entities)

        if intent == "issue":
            return "\n".join([
                "### How to issue a book",
                f"1. **Have a valid library membership/card.** New? Fill the [membership form]({LINKS['membershipForm']}). The card is non-transferable — never issue books on someone else’s name or let them use yours.",
                "2. **Enter properly.** Carry your library card. Keep bags, personal books, notebooks and bottles at the **property counter**, and deposit your card at the security counter near the circulation desk before entering the main reading area.",
                f"3. **Find the book.** Search the [e-Catalogue]({LINKS['catalogue']}) by title, author or subject, and note the call number. Use the [Shelve Guide]({LINKS['shelve']}) or ask me “Where is Mechanical Engineering?” to find the floor.",
                "4. **Check the book** for torn/missing pages or damage. Report any damage at the circulation desk **before** issuing — otherwise you are held responsible.",
                "5. **Go to the Circulation Desk** (Ground Floor, Part B) with your library card during counter hours (Mon–Fri 9:00 AM – 5:30 PM, Sat 9:30 AM – 6:00 PM).",
                "6. **Check your email.** You will get an issue email with the due date (the library also sends advance-due, due and overdue reminders).",
                "7. **Return or renew on or before the due date** to avoid a fine of ₹1 per day per book.",
                "**Before you borrow:** clear any outstanding dues; they block issue/return/renew. Your borrowing limit depends on your category — ask “How many books can I borrow?”.",
                "**Treat books well:** no writing, marking or tearing; protect them from rain, dust and insects. Defacing means paying full replacement cost.",
                "Not sure about something? Circulation: +91 755 405 1381 / 82 · library-cs@staff.manit.ac.in",
                f"~ Steps compiled from the library’s [Circulation Policies]({LINKS['circulation']}) and [General Rules]({LINKS['rules']}); the website does not publish a single numbered guide, so confirm details at the desk.",
            ])

        if intent in {"return_book", "renew"}:
            return "\n".join([
                "### Return, renew & extensions",
                "- **Return** books at the Circulation Desk on or before the due date (the due date is in your issue email).",
                "- **Renew:** all members **except faculty** can renew an issued book once for one more 90-day cycle. Do it before the due date, and clear any dues first.",
                "- **Out of station?** Email **library-cs@staff.manit.ac.in** asking for a temporary due-date extension — it needs the Librarian’s approval.",
                "- **Going on long leave / leaving?** Return all issued books first (except books issued for a break/vacation). The library can also recall a book at any time.",
                "- **Late?** ₹1 per day per book. Ask “How is the fine calculated?” to calculate yours.",
                "- Keep your email updated — issue, return, renew, advance-due, due and overdue (sent three times) emails go to your inbox.",
                "Circulation: +91 755 405 1381 / 82",
                f"~ Source: [Circulation Policies]({LINKS['circulation']})",
            ])

        if intent in {"loan", "book_bank"}:
            rows = [f"| {r['who']} | {r['books']} | {r['days']} days |" for r in LIBRARY_DATA["loan"]]
            bb = [f"| {r['who']} | {r['books']} | {r['days']} days |" for r in LIBRARY_DATA["bookBank"]]
            return "\n".join([
                "### Loan Privileges",
                "| Category | Books | Period |",
                "|---|---|---|",
                *rows,
                "### Book Bank (semester-long textbooks)",
                "| Category | Books | Period |",
                "|---|---|---|",
                *bb,
                "Book Bank collections are issued to students from the economically weaker section.",
                "- Everyone except faculty can renew issued books **once** for another 90 days.",
                "- The Librarian may recall any issued book at any time.",
                f"~ Source: [Circulation Policies]({LINKS['circulation']}) · [Loan Privileges]({LINKS['loan']})",
            ])

        if intent == "membership":
            return "\n".join([
                "### Library Membership",
                "- All members of the academic community are entitled to join the Central Library.",
                f"- Fill the [membership form]({LINKS['membershipForm']}) — read the instructions first, and **log in to your email** while filling it.",
                "- Keep ready: **one passport-size colour photograph** and your **latest fee receipt** (students) or **pay slip / joining order / institute ID card** (faculty & staff).",
                "- Keep your email ID correct — all circulation emails (welcome, issue, return, renew, due, overdue, account-expiry) are sent there.",
                f"- Change of address or details? Update via your [e-Catalogue account]({LINKS['login']}) or email library-cs@staff.manit.ac.in.",
                "- Account expired? Email library-cs@staff.manit.ac.in with an extension letter from the competent authority.",
                "- The card is **non-transferable** and must be carried when visiting the library.",
                f"~ Source: [Circulation Policies – Library Membership]({LINKS['circulation']})",
            ])

        if intent == "lost":
            return "\n".join([
                "### Lost or damaged card / book",
                f"- **Lost library card:** report immediately at the circulation desk or by email to library-cs@staff.manit.ac.in. A fine of **₹{LIBRARY_DATA['cardReplacement']}** is charged for a new card.",
                "- **Lost or damaged book:** replace it with the **latest edition**, or pay the same amount as the book’s cost.",
                "- **Defaced books** (writing, marking, cutting, torn pages): full replacement cost is charged.",
                f"- Pay online through [SBI Collect]({LINKS['payFine']}) (see “pay fine online”) and report to the circulation desk the same day.",
                f"~ Source: [Circulation Policies – No Dues]({LINKS['circulation']})",
            ])

        if intent == "no_dues":
            return "\n".join([
                "### No Dues / Clearance Certificate",
                "- Before leaving the institute, getting a certificate or retiring, **return all library property** and obtain a **No Dues Certificate**.",
                "- No-dues forms: **academic building** (students) or **establishment section** (faculty & staff).",
                "- Return books in the same condition they were issued, and return your library ID card if you took one.",
                "- Pending fines/replacements must be cleared first (pay online or at the desk).",
                f"~ Source: [Circulation Policies – No Dues]({LINKS['circulation']})",
            ])

        if intent == "pay_fine":
            return "\n".join([
                "### Pay fines online",
                f"1. Open [SBI Collect]({LINKS['payFine']}).",
                "2. Choose **Educational Institutions** under “Select Category”.",
                "3. Search for the institute name **Director- MANIT**.",
                "4. Select **Library Books Charges/fine** from the drop-down.",
                "5. Fill in the details and pay.",
                "6. **Report to the Library Circulation Desk the same day** for further processing.",
                f"~ Source: [Circulation Policies – Fine Rules]({LINKS['circulation']})",
            ])

        if intent == "fine":
            if "days" in entities:
                days = min(entities["days"], 36500)
                has_books = "books" in entities
                books = entities.get("books", 1)
                if not has_books:
                    self._set_pending(session_id, "fine_books", {"days": days})
                else:
                    self._clear_pending(session_id)
                extra = (
                    ""
                    if has_books
                    else "\n**Fine is charged per book.** If more than one book is overdue, type the number of books."
                )
                return self._fine_details() + "\n" + self._fine_result(days, books) + extra

            self._set_pending(session_id, "fine_days")
            ask = "**How many days is your book overdue?** Type the number of days (e.g. **12**), or type the due date (DD-MM-YYYY) and I will count the days up to today."
            return self._fine_details() + "\n" + ask

        if intent == "due_date":
            res = self._compute_due(raw, entities)
            if res:
                self._clear_pending(session_id)
                return self._due_details() + "\n" + res
            self._set_pending(session_id, "due_date")
            ask = "**On which date was the book issued?** Type it as DD-MM-YYYY (e.g. 15-10-2026). Add “faculty” or “book bank” if that applies, otherwise I will show all categories."
            return self._due_details() + "\n" + ask

        if intent == "rules":
            return "\n".join([
                "### Library rules (summary)",
                "- Carry your library card; show it on demand. Deposit it at the security counter near the circulation desk before entering the main reading area.",
                "- Keep books, notebooks, bags and bottles at the **property counter** (almirahs on the ground floor). Do not leave valuables (laptop, mobile, money, ATM cards) in bags — the library is not responsible for losses.",
                "- Keep **pin-drop silence**. **Mobile phone use, smoking, food and beverages are not allowed.**",
                "- Leave finished books on the nearest table — do not reshelve them yourself.",
                "- Do not put feet on tables, chairs or shelves. Use library computers for academic purposes only.",
                "- Photography needs prior permission from the Librarian/staff.",
                "- Visitors/guests need the Librarian’s prior permission (photo ID and a letter from their institution).",
                "- Misbehaviour can lead to suspension of membership; damage to library property must be paid for.",
                "- Security may check belongings, including issued books.",
                f"~ Source: [General Rules]({LINKS['rules']})",
            ])

        if intent == "floor":
            return self._floor_answer(entities)

        if intent == "subject":
            return self._subject_answer(entities)

        if intent == "facilities":
            return "\n".join([
                "### Library facilities",
                "**Reading & study:** independent cubicles, group discussion (GD) area, multipurpose hall, general reading halls, thematic displays, special collections (Hindi, IKS, competitive exams, reference, literature, new arrivals, biography).",
                "**Technology:** campus-wide WiFi, e-resource access areas, remote access to subscribed e-resources, QR codes for quick access, digital display unit, email & SMS notifications for transactions.",
                "**Services:** book lending, Book Bank, inter-library loan, BIS Corner (Indian Standards), orientation programmes on request, online fine payment, customised bookmarks.",
                "**Accessibility:** Inclusive Access Station with a Kibo smart scanner for visually impaired users.",
                "**Comfort:** purified drinking water, renovated ladies’ washroom. **Extended hours** (till midnight) during exams.",
                f"~ Source: [Facilities]({LINKS['facilities']})",
            ])

        if intent == "digital":
            return "\n".join([
                "### Digital resources & access",
                f"- **e-Catalogue:** [libcat.manit.ac.in]({LINKS['catalogue']}) — search books, see availability, log in to your account.",
                f"- **Remote access (off-campus):** [MyLOFT]({LINKS['myloft']}) — request an account via the [account form]({LINKS['accountForm']}).",
                f"- **e-Resources hub:** [e-Resources]({LINKS['eresources']}) — e-books, e-journals, e-newspapers, e-magazines.",
                "- **Databases:** CBS e-Books, CMIE Prowess, JoVE, Hindi e-Books (EBSCO), IndiaStat, Perlego, Sage Research Methods, Sage Business Cases, Sage Campus Collection, Scopus. Ask “databases”.",
                "- **e-Journals:** ONOS, Cambridge Core, Sage, De Gruyter Brill. Ask “e-journals”.",
                "- **Theses:** MANIT theses on Shodhganga, Shodhgangotri, institutional repository. Ask “theses”.",
                f"- **Open Access & trial access:** [OA Resources]({SITE}oa-resources/) · [Trial Access]({SITE}trial-access/).",
                "- QR codes around the library give quick links to resources and services.",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "databases":
            return "\n".join([
                "### Subscribed databases",
                "- [CBS e-Books](https://eduportglobal.com/my-library)",
                "- [CMIE Prowess](https://prowess.cmie.com/)",
                "- [JoVE Research](https://www.jove.com/)",
                "- [Hindi e-Books (EBSCO)](https://research.ebsco.com/c/7lu7vb/)",
                "- [IndiaStat](https://www.indiastat.com/) · [IndiaStat Districts (Madhya Pradesh)](https://www.indiastatdistricts.com/madhyapradesh-state)",
                "- [Perlego](https://www.perlego.com/) (account via the account form)",
                "- [Sage Business Cases](https://sk.sagepub.com/cases) · [Sage Campus Collection](https://classroom.sagepub.com/) · [Sage Research Methods](https://methods.sagepub.com/)",
                "- [Scopus](https://www.scopus.com/)",
                "- BIS Indian Standards via the BIS Corner: [BIS Register](https://standardsbis.bsbedge.com/BIS_Register)",
                f"Off campus? Use [MyLOFT]({LINKS['myloft']}). Full list: [Databases]({LINKS['databases']}).",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "ejournals":
            return "\n".join([
                "### e-Journals",
                "- [ONOS – One Nation One Subscription](https://onos.gov.in/)",
                "- [Cambridge Core](https://www.cambridge.org/core/publications/journals)",
                "- [Sage journals](https://journals.sagepub.com/action/showPublications?startPage=&CategoryFilterField=6424)",
                "- [De Gruyter Brill](https://www.degruyterbrill.com/)",
                f"Can’t find a full text? Request it through the library (inter-library loan): [Request a Material]({SITE}request-a-material/).",
                f"~ Source: [e-Resources]({LINKS['eresources']})",
            ])

        if intent == "ebooks":
            return "\n".join([
                "### e-Books, e-Newspapers & e-Magazines",
                f"- [e-Books]({SITE}e-books/) · [e-Newspapers]({SITE}e-newspapers/) · [e-Magazines]({SITE}e-magazines/)",
                f"- [Open Access resources]({SITE}oa-resources/)",
                "- Hindi e-Books via EBSCO, textbooks via Perlego and CBS e-Books (see “databases”).",
                f"- Off campus: use [MyLOFT]({LINKS['myloft']}).",
                f"~ Source: [e-Resources]({LINKS['eresources']})",
            ])

        if intent == "thesis":
            return "\n".join([
                "### Theses & repositories",
                "- [MANIT theses on Shodhganga](https://shodhganga.inflibnet.ac.in/handle/10603/360582)",
                "- [Shodhganga](https://shodhganga.inflibnet.ac.in/) (national theses repository) · [Shodhgangotri](https://shodhgangotri.inflibnet.ac.in/) (synopses)",
                "- [MANIT Institutional Repository (IDR)](https://idr.manit.ac.in/) · [News clippings](https://idr.manit.ac.in/collections/6f6edea1-d082-4d9c-bc68-705921935110)",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "remote":
            return "\n".join([
                "### Remote (off-campus) access",
                f"- Use [MyLOFT]({LINKS['myloft']}) to reach subscribed e-resources from outside the campus.",
                f"- Need an account for MyLOFT, DrillBit, Perlego or Turnitin? Submit the [account request form]({LINKS['accountForm']}).",
                "- Use your institute email while requesting access.",
                f"~ Source: [Facilities]({LINKS['facilities']})",
            ])

        if intent == "catalogue":
            return "\n".join([
                "### e-Catalogue (search & account)",
                f"- Search books at [libcat.manit.ac.in]({LINKS['catalogue']}) by title, author, subject or keyword and check availability.",
                f"- [Log in to My Account]({LINKS['login']}) to update profile details; here is the [e-Catalogue guide]({LINKS['catalogueGuide']}).",
                f"- [New Arrivals]({LINKS['newArrivals']}) · [Special Collections]({LINKS['special']}) · [Shelve Guide]({LINKS['shelve']}).",
                "- Note the **call number**, then ask me “Where is <subject>?” to find the floor.",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "research":
            return "\n".join([
                "### Research support",
                f"- [Scopus Dashboard]({SITE}scopus-dashboard/) · [MANIT at Scopus](https://www.scopus.com/pages/organization/60021318)",
                f"- [Research Tools]({SITE}research-tools/) · [APC Support]({SITE}apc-support/) · [How-to Guides]({SITE}how-to-guides/)",
                "- [IRINS faculty profiles](https://manit.irins.org/)",
                "- Plagiarism checkers: Turnitin and DrillBit (ask “plagiarism”)",
                f"- [Request a Material]({SITE}request-a-material/) · [Request a Session]({SITE}request-a-session/) · [Ask a Librarian]({SITE}ask-a-librarian/)",
                "- Research Support desk: +91 755 405 1382 / 83 / 84 · library-rs@staff.manit.ac.in",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "plagiarism":
            return "\n".join([
                "### Plagiarism / similarity check",
                "- Tools available: [Turnitin](https://home.turnitin.com/sign-in) ([guide](https://guides.turnitin.com/hc/en-us/articles/24008452116749-Welcome-to-Turnitin-Guides)) and [DrillBit](https://online.drillbitplagiarismcheck.com/login) ([guide](https://drive.google.com/file/d/1a1nwHEv2JB-mBy1D8Af_Y_rkYRdTavMF/view)).",
                f"- Need an account? Submit the [account request form]({LINKS['accountForm']}).",
                "- Questions: Research Support — library-rs@staff.manit.ac.in",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "request_material":
            return "\n".join([
                "### Request a book, article or full text",
                f"- **Full text not available?** Use [Request a Material]({SITE}request-a-material/) — the library can borrow it from partner libraries (inter-library loan).",
                "- **Want the library to buy a book?** Contact Acquisition & Technical Processing: library-atp@staff.manit.ac.in · +91 755 405 1383 / 84 / 88.",
                f"- **Training or orientation for your group?** [Request a Session]({SITE}request-a-session/).",
                f"~ Source: [Facilities]({LINKS['facilities']})",
            ])

        if intent == "session":
            return "\n".join([
                "### Orientation, sessions & events",
                f"- User awareness/orientation sessions can be arranged on request during office hours: [Request a Session]({SITE}request-a-session/).",
                f"- See what is on: [Library Events]({SITE}library-events/) · [Library Bulletin]({SITE}library-bulletin/) · [Photo Gallery](https://www.flickr.com/photos/clmanitb/albums).",
                f"~ Source: [Facilities]({LINKS['facilities']})",
            ])

        if intent == "contact":
            rows = [f"| {c['name']} | {c['phone']} | {c['email']} |" for c in LIBRARY_DATA["contacts"]]
            return "\n".join([
                "### Contact the library",
                f"**Address:** {LIBRARY_DATA['address']}",
                f"**General:** {LIBRARY_DATA['general']} · **Librarian:** {LIBRARY_DATA['librarian']} · **Phone:** {LIBRARY_DATA['phones']}",
                "| Desk | Phone | Email |",
                "|---|---|---|",
                *rows,
                f"[Route map]({SITE}route-map/) · [Ask a Librarian]({SITE}ask-a-librarian/)",
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "social":
            return "\n".join([
                "### Official social media",
                *[f"- **{n}:** {u}" for n, u in LIBRARY_DATA["social"].items()],
                f"~ Source: [library.manit.ac.in]({SITE})",
            ])

        if intent == "holidays":
            return "\n".join([
                "### Holidays",
                f"- The library is closed on all **Sundays** and **institute-declared holidays** — see the [holiday list 2026]({LINKS['holidays']}).",
                "- It may open on a declared holiday with approval from the competent authority; email librarian@manit.ac.in or call +91 755 405 1384 / 83 to confirm.",
                "- Hours are extended till midnight on all days during exams.",
                f"~ Source: [Library Timings]({LINKS['timings']})",
            ])

        if intent == "about":
            return "\n".join([
                "### About the Central Library",
                "MANIT’s Central Library supports the learning and research needs of students, faculty and researchers with print and digital resources and automated services.",
                f"📍 {LIBRARY_DATA['address']}",
                "Ask me about issuing books, fines, timings, floors, e-resources, research support or contacts.",
                f"~ Source: [About the Library]({SITE}about-the-library/)",
            ])

        return FALLBACK

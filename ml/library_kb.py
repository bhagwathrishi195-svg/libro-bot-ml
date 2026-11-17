SITE = "https://library.manit.ac.in/"

LINKS = {
    "circulation": SITE + "circulation-policies/",
    "timings": SITE + "library-timings/",
    "rules": SITE + "general-rules/",
    "floor": SITE + "floor-plan/",
    "facilities": SITE + "facilities/",
    "loan": SITE + "loan-privileges/",
    "shelve": SITE + "shelve-guide/",
    "special": SITE + "special-collections/",
    "catalogue": "https://libcat.manit.ac.in/",
    "login": "https://libcat.manit.ac.in/cgi-bin/koha/opac-user.pl",
    "newArrivals": "https://libcat.manit.ac.in/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber=72&sortfield=copyrightdate",
    "catalogueGuide": "https://drive.google.com/file/d/1spuxVgbF6qXWFJ5kB6zB_q9CECjEucZW/view",
    "whatIsWhere": "https://drive.google.com/file/d/1Nvle0c72M9g402RYf4taU9qWXo2uq3ZC/view",
    "membershipForm": "https://forms.gle/QMdrV2NPZNJTe7XY9",
    "accountForm": "https://forms.gle/rkBQBP3KJ1BDwXZm9",
    "payFine": "https://www.onlinesbi.sbi/sbicollect/",
    "myloft": SITE + "myloft/",
    "eresources": SITE + "e-resources/",
    "databases": SITE + "databases/",
    "holidays": "https://www.manit.ac.in/sites/default/files/documents/Holiday%20Notification%20Year%20-%202026.pdf",
}

LIBRARY_DATA = {
    "timings": {
        "main": {"weekday": ("08:30", "21:30"), "saturday": ("09:30", "18:00")},
        "outer": {"weekday": ("08:30", "23:30"), "saturday": ("09:30", "23:30")},
        "circulation": {"weekday": ("09:00", "17:30"), "saturday": ("09:30", "18:00")},
    },
    "address": "Central Library, Maulana Azad National Institute of Technology Bhopal, Main Road No. 3, Near Kali Mata Mandir, Bhopal, Madhya Pradesh – 462003",
    "phones": "+91 755 405 1384 / 83 / 82",
    "contacts": [
        {"name": "Circulation", "about": "Issue, return, renew, fines, membership cards", "phone": "+91 755 405 1381 / 82", "email": "library-cs@staff.manit.ac.in"},
        {"name": "Acquisition & Technical Processing", "about": "Purchase requests for print material", "phone": "+91 755 405 1383 / 84 / 88", "email": "library-atp@staff.manit.ac.in"},
        {"name": "Research Support", "about": "Reference, digital resources, research services", "phone": "+91 755 405 1382 / 83 / 84", "email": "library-rs@staff.manit.ac.in"},
        {"name": "Library Administration", "about": "Feedback, suggestions, policy matters", "phone": "+91 755 405 1384 / 83 / 82", "email": "library-admin@staff.manit.ac.in"},
        {"name": "Library Office", "about": "Office enquiries, book bank, digital library", "phone": "+91 755 405 1399 / 84", "email": "library-admin@staff.manit.ac.in"},
        {"name": "Security Desk", "about": "Security, visits, timings", "phone": "+91 755 405 1386 / 87", "email": "library-cs@staff.manit.ac.in"},
    ],
    "general": "library@manit.ac.in",
    "librarian": "librarian@manit.ac.in",
    "social": {
        "Facebook": "https://facebook.com/clmanitb/",
        "X (Twitter)": "https://x.com/clmanitb/",
        "Instagram": "https://instagram.com/clmanitb/",
        "LinkedIn": "https://linkedin.com/company/clmanitb/",
        "YouTube": "https://youtube.com/@clmanitb/",
        "Flickr (photo albums)": "https://www.flickr.com/photos/clmanitb/albums",
    },
    "loan": [
        {"who": "Faculty members", "books": 20, "days": 180},
        {"who": "Group A staff / PhD scholars", "books": 10, "days": 90},
        {"who": "Group B/C/D staff", "books": 8, "days": 90},
        {"who": "PG students", "books": 8, "days": 90},
        {"who": "UG students", "books": 6, "days": 90},
    ],
    "bookBank": [
        {"who": "Book Bank – General category (PG/UG)", "books": 6, "days": 365},
        {"who": "Book Bank – SC/ST category (PG/UG)", "books": 20, "days": 365},
    ],
    "fineRate": 1,
    "cardReplacement": 100,
}

FLOOR_PLAN = {
    "Part A — Outer Reading Room": {
        "ground": [
            "Property Counter", "Group Study Area", "Independent Cubicles",
            "Multipurpose Hall", "e-Resource Access Area", "Security Cabin & Desk",
            "Ladies and Staff Restrooms",
        ],
        "first": ["Independent Cubicles", "e-Resource Access Area"],
        "second": ["Independent Cubicles"],
    },
    "Part B — Main Building": {
        "ground": [
            "Librarian’s, Deputy and Assistant Librarian’s Cabins", "Circulation Desk",
            "Security Desk", "Library Office", "Binding Section",
            "Pantry & Drinking Water", "Kibo Station (inclusive access)",
            "e-Catalogue terminals",
        ],
        "first": ["Book Bank"],
        "second": ["Book Bank"],
    },
    "Part C — Stack & Reading Area": {
        "ground": [
            "Reference Hall & Reference Section", "Acquisition Section", "Reading Hall",
            "BIS Corner", "Newspaper/Magazine Reading Area", "Independent Cubicles",
            "e-Resource Access Area", "Help Desk", "Stack: Civil Engineering (624–628)",
            "English (420/820) & Hindi (491.43/891.43) literature",
            "Competitive exam books, Biographies", "Print New Arrival display",
        ],
        "first": [
            "General Reading Hall", "Help Desk",
            "Stack: Physics, Chemistry, Maths, Biology, Hydrology (500–599), Computer Programmes (004), Indian Knowledge System",
            "Section I: Electrical, Electronics & Communication, Computer Science",
            "Section II: Management, Social Sciences/Economics, Architecture & Planning, Chemical",
        ],
        "second": [
            "Books Stack: Mechanical Engineering (620.1–681), Metallurgy & Materials (669–669.9)"
        ],
    },
}

SUBJECTS = [
    {"keys": ["computer science", "cse", "cs", "computer", "programming", "programme", "information technology", "software"], "name": "Computer Science", "where": "**First Floor – Part C (Main Building Stack), Section I**", "note": "Computer Science: DDC 621.3895; Computer Programmes: 004."},
    {"keys": ["electrical", "ee", "eee"], "name": "Electrical Engineering", "where": "**First Floor – Part C, Section I**", "note": "Electrical Engineering: DDC 621.3 – 621.39."},
    {"keys": ["electronics", "ece", "communication", "electronics and communication", "vlsi"], "name": "Electronics & Communication", "where": "**First Floor – Part C, Section I**", "note": "Electronics & Communication: DDC 621.381 – 621.384."},
    {"keys": ["management", "mba", "management study", "marketing"], "name": "Management Studies", "where": "**First Floor – Part C, Section II**", "note": "Management Studies: DDC 658."},
    {"keys": ["social science", "economics", "economic", "sociology", "psychology"], "name": "Social Sciences & Economics", "where": "**First Floor – Part C, Section II**", "note": "Social Sciences / Economics: DDC 300."},
    {"keys": ["architecture", "planning", "architecture and planning", "town planning"], "name": "Architecture & Planning", "where": "**First Floor – Part C, Section II**", "note": "Architecture and Planning: DDC 624 – 628."},
    {"keys": ["chemical", "chemical engineering"], "name": "Chemical Engineering", "where": "**First Floor – Part C, Section II**", "note": "Chemical: DDC 660 – 660.6."},
    {"keys": ["physics", "chemistry", "mathematics", "maths", "biology", "hydrology", "science"], "name": "Physics, Chemistry, Mathematics, Biology, Hydrology", "where": "**First Floor – Part C (Stack Area)**", "note": "DDC 500 – 599."},
    {"keys": ["indian knowledge system", "iks", "indian knowledge"], "name": "Indian Knowledge System (IKS) collection", "where": "**First Floor – Part C (Stack Area)**", "note": ""},
    {"keys": ["mechanical", "mech", "thermal", "manufacturing", "production", "mechnical"], "name": "Mechanical Engineering", "where": "**Second Floor – Part C (Books Stack)**", "note": "Mechanical Engineering: DDC 620.1 – 681."},
    {"keys": ["metallurgy", "materials", "mse", "metallurgical", "material science"], "name": "Metallurgy & Materials", "where": "**Second Floor – Part C (Books Stack)**", "note": "Metallurgy & Materials: DDC 669 – 669.9."},
    {"keys": ["civil", "civil engineering", "structural", "construction", "geotechnical"], "name": "Civil Engineering", "where": "**Ground Floor – Part C (Stack Area)**", "note": "Civil Engineering: DDC 624 – 628 (complete collection)."},
    {"keys": ["reference book", "encyclopedia", "dictionary", "handbook", "manual", "reference section", "reference hall"], "name": "Reference Section", "where": "**Ground Floor – Part C (Reference Hall / Reference Section)**", "note": "Encyclopedias, dictionaries, manuals and handbooks."},
    {"keys": ["english literature", "english language", "literature", "novel"], "name": "English Language & Literature", "where": "**Ground Floor – Part C (Reference Section)**", "note": "DDC 420 / 820."},
    {"keys": ["hindi", "hindi literature", "hindi book"], "name": "Hindi Language & Literature", "where": "**Ground Floor – Part C (Reference Section)**", "note": "DDC 491.43 / 891.43."},
    {"keys": ["newspaper", "magazine", "periodical"], "name": "Newspapers & Magazines", "where": "**Ground Floor – Part C (Newspaper/Magazine Reading Area)**", "note": "The library subscribes to 15 print+online newspapers and 14 print+online magazines (Hindi and English)."},
    {"keys": ["competitive exam", "gate", "gmat", "reasoning", "upsc", "competitive"], "name": "Competitive exam books", "where": "**Ground Floor – Part C**", "note": "GATE, CAT, GMAT, reasoning and similar exam books."},
    {"keys": ["biography", "biographies"], "name": "Biographies", "where": "**Ground Floor – Part C**", "note": "English and Hindi."},
    {"keys": ["bis", "indian standard", "bis corner", "standard code"], "name": "BIS Corner", "where": "**Ground Floor – Part C**", "note": "Access Indian Standard codes through the Bureau of Indian Standards portal."},
    {"keys": ["book bank", "bookbank"], "name": "Book Bank", "where": "**First and Second Floors – Part B (Main Building)**", "note": "Semester-long textbooks for the economically weaker section."},
    {"keys": ["circulation desk", "circulation counter", "issue counter", "return counter"], "name": "Circulation Desk", "where": "**Ground Floor – Part B (Main Building)**", "note": "Issue, return and renewal counter."},
    {"keys": ["property counter", "locker", "almirah", "bag counter"], "name": "Property Counter", "where": "**Ground Floor – Part A (Outer Reading Room)**", "note": "Deposit bags, books, notebooks and bottles here before entering."},
    {"keys": ["new arrival", "new book"], "name": "New Arrivals", "where": "**Ground Floor – Part C (Print New Arrival Display Area)**", "note": "You can also browse the online New Arrivals list."},
    {"keys": ["cubicle", "study cubicle", "private study"], "name": "Independent Cubicles", "where": "**Part A (all three floors) and Part C (Ground Floor)**", "note": "Private study spaces."},
    {"keys": ["group study", "gd area", "group discussion"], "name": "Group Study / GD Area", "where": "**Ground Floor – Part A (Outer Reading Room)**", "note": ""},
    {"keys": ["multipurpose hall", "seminar hall"], "name": "Multipurpose Hall", "where": "**Ground Floor – Part A**", "note": "Used for events, seminars and training sessions; can also serve as a reading hall."},
    {"keys": ["general reading hall"], "name": "General Reading Hall", "where": "**First Floor – Part C**", "note": ""},
    {"keys": ["kibo", "inclusive access", "visually impaired", "scanner station"], "name": "Inclusive Access Station (Kibo)", "where": "**Ground Floor – Part B (Main Building)**", "note": "Smart Scanner Station for visually impaired users."},
    {"keys": ["librarian cabin", "librarian office", "library office"], "name": "Library Office / Librarian's Cabin", "where": "**Ground Floor – Part B (Main Building)**", "note": ""},
]

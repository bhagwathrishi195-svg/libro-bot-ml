import csv
import os
from preprocess import normalize_text

INTENT_SAMPLES = {
    "greeting": [
        "Hi", "Hello", "Hey there", "Good morning", "Good afternoon", "Good evening",
        "Namaste", "Hi LibroBot", "Hello library assistant", "Hey bot", "Hii", "Hellooo",
        "Greetings", "How are you?", "Who are you?", "What are you?", "Introduce yourself",
        "What is your name?", "Yo", "Hiya", "Good day", "Hello sir", "Namaste bhai",
        "Kya hal hai", "Kaise ho bot", "Hlo", "Hy", "Good mrng", "Nice to meet you",
        "Hey assistant", "Welcome", "Hi friend", "Hello MANIT library", "Hey LibroBot"
    ],
    "help": [
        "Help", "Menu", "What can you do?", "What can you help me with?", "Show options",
        "Features", "Topics", "Commands", "What do you know?", "How to use this bot?",
        "Guide me", "Start", "Start over", "All topics", "List topics", "Capabilities",
        "How can you assist me?", "Tell me what you do", "Madad chahiye", "Help karo",
        "Kya kya pooch sakte hain", "Show me what you can answer", "Assist me", "Help please"
    ],
    "thanks": [
        "Thanks", "Thank you", "Thankyou", "Thx", "Ok thanks", "Great", "Awesome",
        "Nice", "Good bot", "Helpful", "Bye", "Goodbye", "See you", "Good night",
        "Thanks a lot", "Thank you so much", "Shukriya", "Dhanyawad", "Okay bye",
        "That helped a lot thanks", "Cool thanks", "Appreciate it", "Bye bye"
    ],
    "about": [
        "About library", "About the library", "Tell me about the library", "Library history",
        "When was the library established?", "Central library MANIT", "Maulana Azad library",
        "Library information", "Library details", "Overview of library", "Library introduction",
        "Who runs the central library?", "Tell me about MANIT Central Library",
        "Central library ke baare me batao", "What is MANIT central library?"
    ],
    "open_now": [
        "Open now", "Is the library open?", "Is library open?", "Is it open?",
        "Are you open?", "Open today", "Open right now", "Currently open?",
        "Open at this time?", "Is the library closed now?", "Is library closed now?",
        "Closed now?", "Library open today?", "Is the library open on Saturday?",
        "Is the library open on Sunday?", "Abhi library khuli hai kya?",
        "Kya aaj library open hai?", "Is reading room open right now?",
        "Is circulation counter open now?", "Check if library is open"
    ],
    "timings": [
        "What are the library timings?", "Library timing", "Opening hours", "Closing hours",
        "Opening time", "Closing time", "Working hours", "Library hours", "Schedule",
        "Timetable", "When does library open?", "When does the library open?",
        "When does library close?", "When does the library close?", "Library closing time on weekdays",
        "Till what time can I get books issued?", "What time does the library close in the evening?",
        "Is the circulation counter open on Saturday?", "Library working hours",
        "Until what time is outer reading area open?", "Exam time library hours",
        "Does library stay open till midnight during exams?", "Monday timings",
        "Tuesday timings", "Wednesday timings", "Thursday timings", "Friday timings",
        "Saturday timings", "Reading room timing", "Circulation timing",
        "libary timmings", "library kab khulti hai", "library band hone ka time kya hai",
        "library timing batao", "subah kitne baje khulti hai library"
    ],
    "issue": [
        "How do I issue a book?", "Issue book", "Issue a book", "How to issue",
        "How to issue book", "How to issue a book", "Borrow book", "How to borrow",
        "I want to take a book home", "Get a book", "Book issue", "Book issuing",
        "Lending process", "Check out a book", "Issue procedure", "Issue process",
        "Issue steps", "How can I take a book?", "How to get a book issued?",
        "What is the process to borrow a book?", "how to isue a book",
        "book kaise issue kare", "kitab issue karne ka tarika", "steps to borrow books"
    ],
    "return_book": [
        "Return book", "How to return", "Return a book", "Book return",
        "Return process", "Return procedure", "Submit book", "Submit the book",
        "Deposit book", "Where do I return my issued book?", "How to submit borrowed book?",
        "Book return karne ka process kya hai", "Return rules for books"
    ],
    "renew": [
        "Renew", "Renewal", "Renew book", "Renew my book", "How do I renew a book?",
        "Extend due date", "Extension", "Extend book", "Temporary extension",
        "Out of station", "I am going out of station, can I extend my due date?",
        "Can I renew my book online or at desk?", "How many times can a book be renewed?",
        "Book renew kaise kare", "Due date extend ho sakti hai kya?", "Book recall policy"
    ],
    "loan": [
        "Loan privileges", "Borrowing limit", "How many books can a UG student borrow?",
        "How many books can a faculty member take?", "Book limit", "Issue limit",
        "Number of books allowed", "Maximum books", "Borrowing privilege",
        "Books per student", "How many books can I borrow?", "Entitlement",
        "Loan limit for PG students", "How many books can PhD scholars issue?",
        "kitni book issue kar sakte hain", "ek student kitni kitab le sakta hai"
    ],
    "book_bank": [
        "Book bank", "Bookbank", "How can I get a book from Book Bank?",
        "Semester book", "Economically weaker section books", "EWS book bank",
        "SC ST book bank", "Free textbook for semester", "Book bank rules",
        "How many books are issued in Book Bank?", "Book bank facility in MANIT"
    ],
    "membership": [
        "Membership", "Member", "How do I become a library member?", "Join library",
        "Register for library", "Registration", "Enroll", "Sign up", "Apply for membership",
        "Membership form", "Library card", "ID card", "New member", "New student registration",
        "Who is eligible for membership?", "What documents are needed for a library card?",
        "How can I get a new library card?", "Documents required for library card",
        "Library card kaise banwaye", "Membership form link", "How to get library card"
    ],
    "lost": [
        "What if I lose a book?", "If I lose my book", "Lose a book", "Lose my card",
        "Lost library card", "Lost book", "Lost ID", "Damaged book", "Book lost",
        "Book damaged", "Card lost", "Replacement card", "Duplicate card",
        "Torn book", "Misplaced book", "Fine for lost library card",
        "Library card kho gaya to kya kare", "Book gum ho gayi hai kya karna hoga"
    ],
    "no_dues": [
        "No dues", "Nodues", "No due", "Clearance", "Clearance certificate",
        "How to get a no dues certificate?", "No due certificate", "Leaving institute",
        "Passing out clearance", "Degree clearance", "Retiring clearance",
        "Library no dues form kahan se milega", "No dues process for graduating students"
    ],
    "pay_fine": [
        "Pay fine", "How do I pay my fine online?", "Pay my fine", "Pay library fine",
        "Pay dues", "Online payment", "SBI Collect", "sbicollect", "How to pay fine",
        "Fine payment", "Payment of fine", "Pay charges online", "SBI collect steps for fine",
        "Online fine kaise bhare", "Fine payment portal link"
    ],
    "fine": [
        "Fine", "How is the library fine calculated?", "Calculation of fine",
        "Fine calculation", "Calculate fine", "Calculate my fine", "Fine amount",
        "Late fine", "Overdue fine", "Penalty", "Late fee", "Late charge",
        "Overdue charge", "Fine for 15 days", "Fine for 10 days 3 books",
        "Tell me fine for my 14 days overdue book", "My book is overdue by 30 days, how much do I pay?",
        "What happens if I return a book late?", "My book is late, what will I owe?",
        "Fine per day", "Fine rate", "fien calculation", "late return fine kitna hai",
        "14 din late book ka fine batao", "book overdue fine"
    ],
    "due_date": [
        "Due date", "Return date", "Issue date", "Calculate due date",
        "Calculate my book due date", "Last date to return", "Return deadline",
        "When should I return a book issued on 1 Nov 2026?", "How many days can I keep a book?",
        "When is my book due?", "Loan period", "How long can I keep a book?",
        "Book due date", "Issued on 15-10-2026", "Borrowed on", "Issue period",
        "Due date calculator", "Book kab return karni hai", "Due date kaise nikale"
    ],
    "rules": [
        "Rules", "What are the library rules?", "General rules", "Library rule",
        "Regulations", "Library policy", "Entry rules", "Can I use my mobile phone inside the library?",
        "Is food allowed in the library?", "Am I allowed to carry my bag inside the reading hall?",
        "Can visitors from other colleges enter the library?", "Where do I deposit my bag?",
        "Pin drop silence", "Belongings", "Property counter rule", "What can I carry inside?",
        "Dress code", "Conduct and discipline", "Guest visitor permission", "Carry laptop",
        "Library ke rules kya hain", "Kya phone allowed hai library me?"
    ],
    "floor": [
        "Floor plan", "Show me the library floor plan", "Floor map", "Building layout",
        "Part A", "Part B", "Part C", "Ground floor", "First floor", "Second floor",
        "What is on the ground floor?", "What is on the first floor?", "What is on the second floor?",
        "Library layout", "What is where", "Sections of library", "Library floor directory",
        "Library ka floor plan dikhao", "Ground floor par kya kya hai"
    ],
    "subject": [
        "Where is Computer Science?", "Which floor has mechanical engineering books?",
        "Where are the newspapers kept?", "Where can I find civil engineering books?",
        "Where can I find books on electronics and communication?", "On which floor is the book bank?",
        "where is mechnical engineering", "Where is Electrical Engineering section?",
        "Which floor has Metallurgy books?", "Where are Management books kept?",
        "Location of Architecture books", "Where is Chemical Engineering?",
        "Where are Physics and Chemistry books?", "Where is the Reference Section?",
        "Where are Hindi literature books?", "Where is the BIS Corner?",
        "Where is the Circulation Desk?", "Where is the Kibo station?",
        "Where are competitive exam books like GATE?", "CSE ki books kis floor par hain",
        "Mechanical books kahan milengi", "Where are independent cubicles?"
    ],
    "facilities": [
        "Facilities", "What facilities does the library offer?", "What facilities does the library have?",
        "Amenities", "WiFi", "Internet facility", "Drinking water", "Washroom", "Restroom",
        "Study cubicle", "Group discussion area", "GD area", "Multipurpose hall",
        "Kibo inclusive access", "Visually impaired facilities", "Where do I sit and study quietly?",
        "Library me kya kya facilities hain", "Quiet study space in library"
    ],
    "databases": [
        "Databases", "Does the library have Scopus?", "Which databases does the library subscribe to?",
        "CMIE Prowess", "JoVE", "IndiaStat", "Perlego", "How do I get an account for Perlego?",
        "Sage Research Methods", "Sage Business Cases", "EBSCO", "CBS e-books",
        "Subscribed databases", "Trial access", "BIS standards", "Subscribed resource list"
    ],
    "ejournals": [
        "eJournals", "e-journals", "How can I access e-journals?", "Journals",
        "ONOS", "One Nation One Subscription", "Cambridge Core", "Sage journals",
        "De Gruyter Brill", "Research paper access", "Full text journal articles",
        "Online journals kaise padhe"
    ],
    "ebooks": [
        "eBooks", "e-books", "Can I read e-books online?", "Online books",
        "Digital books", "Hindi e-books", "e-Newspapers", "e-Magazines",
        "Open access resources", "OA resources", "Online magazines and newspapers"
    ],
    "thesis": [
        "Thesis", "Theses", "Where can I find MANIT theses?", "Dissertation",
        "Shodhganga", "Shodhgangotri", "PhD thesis", "IDR", "Institutional repository",
        "News clippings repository", "MANIT PhD theses online"
    ],
    "remote": [
        "Remote access", "How do I access resources from home?", "MyLOFT", "My LOFT",
        "Off campus access", "Access from home", "Access outside campus",
        "Can I read journals from my hostel?", "Remote login for e-resources",
        "Ghar se e-resources kaise access kare", "Hostel se MyLOFT kaise chalaye"
    ],
    "catalogue": [
        "Catalogue", "How do I search the e-catalogue?", "e-Catalogue", "OPAC",
        "Koha", "LibCat", "Search a book", "Find a book", "Book availability",
        "Is the book available?", "My account login", "New arrivals", "Shelve guide",
        "Call number", "Special collections", "Library me book available hai ya nahi kaise check kare"
    ],
    "digital": [
        "Digital resources", "What digital resources are available?", "Online resources",
        "Electronic resources", "e-Resources", "Online library", "Digital library",
        "QR code access", "Library website", "Collection", "What resources does the library have?",
        "Digital facilities overview"
    ],
    "research": [
        "Research support", "Which research support services are available?", "Research help",
        "Research tools", "APC support", "Article processing charge", "How to guides",
        "IRINS faculty profile", "Scopus dashboard", "Publication support", "Citation help",
        "Ask a librarian", "Reference service", "Mendeley", "Zotero"
    ],
    "plagiarism": [
        "Plagiarism", "How to check plagiarism?", "Similarity check", "Turnitin",
        "DrillBit", "How can I check my thesis for similarity?", "Plagiarism report",
        "Similarity report", "Turnitin account", "Thesis plagiarism check kaise kare"
    ],
    "request_material": [
        "Request a material", "How can I request a book that is not in the library?",
        "Inter library loan", "ILL", "Book not available in library", "Suggest a book",
        "How can I suggest a book for the library to buy?", "Purchase request",
        "Recommend a book", "Document delivery", "Full text request", "Acquisition request"
    ],
    "session": [
        "Orientation session", "Do you provide orientation sessions?",
        "Can the library arrange a training for my class?", "Request a session",
        "User awareness program", "Training session", "Library tour", "Induction",
        "Workshop", "Library events", "Library bulletin", "Photo gallery"
    ],
    "contact": [
        "Contact", "How do I contact the library?", "What is the library email id?",
        "Phone number of circulation desk", "Where is the library located?",
        "Who is the librarian?", "Give me the phone number of the library",
        "How can I send feedback to the library?", "Email address", "Helpline number",
        "Circulation email", "Library address", "Route map", "How to reach library",
        "Library ka phone number aur email batao"
    ],
    "social": [
        "Social media", "Show library social media links", "Library instagram page",
        "Instagram", "Facebook", "Twitter", "X account", "LinkedIn", "YouTube",
        "Flickr photo albums", "Official social handles", "Library ka insta page"
    ],
    "holidays": [
        "Holidays", "Is the library closed on holidays?", "Holiday calendar",
        "Holiday list 2026", "Institute holiday", "Public holiday", "Vacation hours",
        "Summer vacation", "Winter break", "Chhutti ke din library khulti hai kya"
    ],
}


def build_dataset(output_path: str = "dataset.csv"):
    seen = set()
    rows = []

    for intent, samples in INTENT_SAMPLES.items():
        for raw_text in samples:
            norm = normalize_text(raw_text)
            if not norm or norm in seen:
                continue
            seen.add(norm)
            rows.append({"text": raw_text.strip(), "intent": intent})

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "intent"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} unique samples across {len(INTENT_SAMPLES)} intents to {output_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_dataset(os.path.join(base_dir, "dataset.csv"))

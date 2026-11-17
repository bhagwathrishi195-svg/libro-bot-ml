const fs = require('fs');

const API_URL = 'http://127.0.0.1:5000/chat';

async function askBackend(query, sessionId) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId })
  });
  return await res.json();
}

const A = [
  ['Library Timings', 'What are the library timings?', 'timings', ['8:30 AM']],
  ['Library Timings', 'Is the library open on Saturday?', ['timings', 'open_now'], ['9:30 AM']],
  ['Library Timings', 'Library closing time on weekdays', 'timings', ['9:30 PM']],
  ['Library Timings', 'Is the library open now?', 'open_now', ['IST']],
  ['Library Timings', 'Is the library open on Sunday?', ['timings', 'open_now'], ['closed on Sundays']],
  ['Library Timings', 'Till what time can I get books issued?', 'timings', ['5:30 PM']],
  ['Membership & Rules', 'How do I become a library member?', 'membership', ['membership form']],
  ['Membership & Rules', 'What documents are needed for a library card?', 'membership', ['passport-size']],
  ['Membership & Rules', 'Can I use my mobile phone inside the library?', 'rules', ['not allowed']],
  ['Membership & Rules', 'What are the library rules?', 'rules', ['silence']],
  ['Membership & Rules', 'Is food allowed in the library?', 'rules', ['food']],
  ['Membership & Rules', 'How many books can a UG student borrow?', 'loan', ['UG students']],
  ['Floor Navigation', 'Show me the library floor plan', 'floor', ['Part A']],
  ['Floor Navigation', 'Where is Computer Science?', 'subject', ['First Floor']],
  ['Floor Navigation', 'Which floor has mechanical engineering books?', 'subject', ['Second Floor']],
  ['Floor Navigation', 'Where are the newspapers kept?', 'subject', ['Ground Floor']],
  ['Floor Navigation', 'What is on the ground floor?', 'floor', ['Circulation Desk']],
  ['Floor Navigation', 'Where can I find civil engineering books?', 'subject', ['Ground Floor']],
  ['Digital Resources', 'What digital resources are available?', 'digital', ['e-Catalogue']],
  ['Digital Resources', 'How can I access e-journals?', 'ejournals', ['ONOS']],
  ['Digital Resources', 'How do I access resources from home?', 'remote', ['MyLOFT']],
  ['Digital Resources', 'Does the library have Scopus?', 'databases', ['Scopus']],
  ['Digital Resources', 'Where can I find MANIT theses?', 'thesis', ['Shodhganga']],
  ['Digital Resources', 'How do I search the e-catalogue?', 'catalogue', ['libcat']],
  ['Fine & Due Date', 'How is the library fine calculated?', 'fine', ['per day per book', 'How many days is your book overdue']],
  ['Fine & Due Date', 'fine for 15 days', 'fine', ['₹15']],
  ['Fine & Due Date', ['calculate fine', '12', '2'], null, ['₹24']],
  ['Fine & Due Date', ['Calculate my due date', '15-10-2026'], null, ['13 January 2027']],
  ['Fine & Due Date', 'How do I pay my fine online?', 'pay_fine', ['SBI Collect']],
  ['Fine & Due Date', 'fine for 10 days 3 books', 'fine', ['₹30']],
  ['Contact Information', 'How do I contact the library?', 'contact', ['library-cs@staff.manit.ac.in']],
  ['Contact Information', 'What is the library email id?', 'contact', ['library@manit.ac.in']],
  ['Contact Information', 'Phone number of circulation desk', 'contact', ['405 1381']],
  ['Contact Information', 'Show library social media links', 'social', ['Instagram']],
  ['Contact Information', 'Where is the library located?', 'contact', ['Bhopal']],
  ['Contact Information', 'Who is the librarian?', 'contact', ['librarian@manit.ac.in']],
  ['Issue & Circulation', 'How do I issue a book?', 'issue', ['Circulation Desk']],
  ['Issue & Circulation', 'How many days can I keep a book?', 'due_date', ['90 days']],
  ['Issue & Circulation', 'How do I renew a book?', ['return_book', 'renew'], ['once']],
  ['Issue & Circulation', 'What if I lose a book?', 'lost', ['latest edition']],
  ['Issue & Circulation', 'How to get a no dues certificate?', 'no_dues', ['No Dues']],
  ['Issue & Circulation', 'How can I get a book from Book Bank?', 'book_bank', ['Book Bank']],
  ['Research & Services', 'How to check plagiarism?', 'plagiarism', ['Turnitin']],
  ['Research & Services', 'What facilities does the library offer?', 'facilities', ['WiFi']],
  ['Research & Services', 'How can I request a book that is not in the library?', 'request_material', ['Request a Material']],
  ['Research & Services', 'Do you provide orientation sessions?', 'session', ['Request a Session']],
  ['Research & Services', 'Which research support services are available?', 'research', ['APC']],
  ['Research & Services', 'Is the library closed on holidays?', 'holidays', ['may open on a declared holiday']],
];

const B = [
  ['Out-of-domain', 'What is the capital of France?', ['fallback']],
  ['Out-of-domain', 'Tell me a joke', ['fallback']],
  ['Out-of-domain', 'Who won the cricket match yesterday?', ['fallback']],
  ['Out-of-domain', 'Explain quantum computing', ['fallback']],
  ['Misspelled', 'libary timmings', ['timings']],
  ['Misspelled', 'how to isue a book', ['issue']],
  ['Misspelled', 'fien calculation', ['fine']],
  ['Misspelled', 'where is mechnical engineering', ['subject']],
  ['Hinglish', 'library kab khulti hai', ['timings']],
  ['Hinglish', 'kitni book issue kar sakte hain', ['loan']],
  ['Paraphrase', 'I want to take a book home', ['issue']],
  ['Paraphrase', 'my book is late, what will I owe', ['fine']],
  ['Paraphrase', 'where do I sit and study quietly', ['facilities']],
  ['Paraphrase', 'can I read journals from my hostel', ['remote', 'ejournals']],
];

if (require.main === module) {
  (async () => {
    const out = { A: [], B: [] };
    let idx = 0;
    for (const [cat, q, exp, must] of A) {
      const sid = `harness_a_${idx++}`;
      const turns = Array.isArray(q) ? q : [q];
      let lastRes = null;
      const t0 = process.hrtime.bigint();
      for (const t of turns) lastRes = await askBackend(t, sid);
      const ms = Number(process.hrtime.bigint() - t0) / 1e6;
      const intent = Array.isArray(q) ? null : lastRes.intent;
      const okIntent = exp === null || (Array.isArray(exp) ? exp.includes(intent) : intent === exp);
      const okFact = must.every(m => lastRes.response.includes(m));
      out.A.push({ cat, q, exp, intent, okIntent, okFact, pass: okIntent && okFact, ms });
    }
    for (const [cat, q, exp] of B) {
      const res = await askBackend(q, `harness_b_${idx++}`);
      out.B.push({ cat, q, exp, intent: res.intent, pass: exp.includes(res.intent) });
    }
    fs.writeFileSync('ml_results.json', JSON.stringify(out, null, 2));
    console.log('Set A pass:', out.A.filter(r => r.pass).length, '/', out.A.length);
    out.A.filter(r => !r.pass).forEach(r => console.log('FAIL A:', r.q, 'exp:', r.exp, 'got:', r.intent, 'fact:', r.okFact));
    console.log('Set B pass:', out.B.filter(r => r.pass).length, '/', out.B.length);
    out.B.filter(r => !r.pass).forEach(r => console.log('FAIL B:', r.q, 'exp:', r.exp, 'got:', r.intent));
  })();
}

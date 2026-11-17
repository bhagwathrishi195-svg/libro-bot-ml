const fs = require('fs');

const API_URL = 'http://127.0.0.1:5000/chat';

const C = [
  ['Library Timings', 'What time does the library close in the evening?', ['timings'], ['9:30 PM']],
  ['Library Timings', 'Is the circulation counter open on Saturday?', ['timings', 'open_now'], ['6:00 PM']],
  ['Library Timings', 'Library working hours', ['timings'], ['8:30 AM']],
  ['Membership & Rules', 'How can I get a new library card?', ['membership'], ['membership form']],
  ['Membership & Rules', 'Am I allowed to carry my bag inside the reading hall?', ['rules', 'subject'], ['property counter']],
  ['Membership & Rules', 'Can visitors from other colleges enter the library?', ['rules'], ['Visitors/guests']],
  ['Floor Navigation', 'Where can I find books on electronics and communication?', ['subject'], ['First Floor']],
  ['Floor Navigation', 'On which floor is the book bank?', ['subject'], ['First and Second Floors']],
  ['Floor Navigation', 'Where do I deposit my bag?', ['rules', 'subject'], ['property counter']],
  ['Digital Resources', 'Which databases does the library subscribe to?', ['databases'], ['CMIE']],
  ['Digital Resources', 'How do I get an account for Perlego?', ['databases', 'remote'], ['account']],
  ['Digital Resources', 'Can I read e-books online?', ['ebooks'], ['e-Books']],
  ['Fine & Due Date', 'My book is overdue by 30 days, how much do I pay?', ['fine'], ['₹30']],
  ['Fine & Due Date', 'When should I return a book issued on 1 Nov 2026?', ['due_date'], ['30 January 2027']],
  ['Fine & Due Date', 'What happens if I return a book late?', ['fine'], ['₹1']],
  ['Contact Information', 'Give me the phone number of the library', ['contact'], ['405']],
  ['Contact Information', 'Library instagram page', ['social'], ['Instagram']],
  ['Contact Information', 'How can I send feedback to the library?', ['contact'], ['library-admin@staff.manit.ac.in']],
  ['Issue & Circulation', 'How many books can a faculty member take?', ['loan'], ['180 days']],
  ['Issue & Circulation', 'I am going out of station, can I extend my due date?', ['renew', 'return_book'], ['temporary due-date extension']],
  ['Issue & Circulation', 'What is the process to borrow a book?', ['issue'], ['Circulation Desk']],
  ['Research & Services', 'How can I check my thesis for similarity?', ['plagiarism'], ['Turnitin']],
  ['Research & Services', 'Can the library arrange a training for my class?', ['session'], ['Request a Session']],
  ['Research & Services', 'How can I suggest a book for the library to buy?', ['request_material'], ['library-atp@staff.manit.ac.in']],
];

(async () => {
  const rows = [];
  let i = 0;
  for (const [cat, q, exp, must] of C) {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q, session_id: `heldout_${i++}` })
    }).then(r => r.json());
    rows.push({
      cat, q, exp, intent: res.intent,
      okIntent: exp.includes(res.intent),
      okFact: must.every(m => res.response.includes(m)),
      pass: exp.includes(res.intent) && must.every(m => res.response.includes(m))
    });
  }
  fs.writeFileSync(process.argv[2] || 'ml_heldout_results.json', JSON.stringify(rows, null, 2));
  console.log('Held-out C pass:', rows.filter(r => r.pass).length, '/', rows.length);
  rows.filter(r => !r.pass).forEach(r => console.log('FAIL:', r.q, 'exp:', r.exp.join('|'), 'got:', r.intent, 'fact:', r.okFact));
})();

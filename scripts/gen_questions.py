#!/usr/bin/env python3
"""Writes src/pages/questions.html (FAQ copy + FAQPage schema). Edit the lists below, then run build_site.py."""
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_HONEST = ("Our AI is built only on what our members have told us: no synthetic patients and no outside data filling the gaps. "
             "Every answer links to the members' own answers it came from, and shows who gave them, so you can check it rather than trust it. "
             "It runs under Footnote, our own framework that sets what it may and may not do.")

CT = [
    ("recruitment-across-uk", "Do you do clinical trial recruitment across the UK?", ["Yes. 13,050 people across the UK living with long-term conditions have joined us (and growing daily), profiled to postcode district, so before you start we can tell you how many people with the condition we hold near your sites. We work with sponsors, CROs with UK sites and academic clinical trials units. Members who pass your screening questions and say yes are referred to the site, and we follow every referral through to randomisation."], None),
    ("sponsors-outside-uk", "Can a sponsor based outside the UK work with you?", ["Yes. Our members are in the UK; the sponsor, biotech or CRO can be anywhere. We count who we hold near your UK sites the same working day, test your materials with members before you submit, and refer members who pass your screening questions and say yes. Sponsors never learn who members are. More for sponsors outside the UK."], None),
    ("recruitment-feasibility", "How do you check patient recruitment feasibility in the UK?", ["With a free panel count, the same working day. Tell us the condition, the people you need and where your UK sites are, and we tell you how many members with the condition we hold near each site, by postcode district, and how they break down by age, sex, ethnicity and deprivation. It's a count of who has joined us, not a forecast of enrolment."], None),
    ("uk-set-up-time", "How long does it take to set up a clinical trial in the UK?", ["The UK government's target was to get clinical trials up and running within 150 days by March 2026. With data to March 2026, the average set-up time for a commercial interventional clinical trial was 122 days, down from 169 days. Ethics and regulatory approval come through one application, combined review, and 99% of combined review applications received regulatory approval within the 60-day target."], "Source: HRA, UK clinical trials reach 150 day set-up milestone, April 2026."),
    ("uk-regulations-2026", "What changed in the UK clinical trials regulations in April 2026?", ["The updated regulations came into force on 28 April 2026. Combined review, one application for ethics and regulatory approval, is now law, and there's a streamlined notification scheme for some applications and modifications. Clinical trials involving medicines must be registered in a public registry. Sponsors must publish a results summary within 12 months of the end and offer it to participants in a way they can easily understand. A clinical trial is expected to recruit its first UK participant within two years of approval, or the approval lapses unless an extension is granted."], "Source: HRA, Transforming the UK's clinical trial landscape."),
    ("how-referrals-work", "How does patient recruitment work?", ["For UK clinical trials, members who pass your screening questions and say yes are referred to the site, with the yes recorded and a best time to call. Eligibility stays the site's call: conditions are self-declared, with qualifying questions. We then follow each one from the first invitation to randomisation, across six steps: Referred, Contacted, Booked, Attended, Screened, Randomised, with randomisation checked against your own record. You get one line per patient each week: where the patient says things stand, the site's note beside it, and why anyone stopped. Sponsors never learn who members are: only we, and the site a member says yes to, know their name."], None),
    ("site-doesnt-call", "What happens if the site doesn't call?", ["We tell the site first. Anyone the site hasn't reached by day 7 goes back to the site that week, so the site hears first and can add its own note. If they're still not reached a week later, they go into the sponsor's report with the site's note beside them. It's a record of where each patient is, never a score for the site."], None),
    ("what-members-agree", "What do members agree to before they're referred?", ["Two consents before any detail leaves us: a standing opt-in to hear about clinical trials, then a yes to one named clinical trial. The site's informed consent is a third step, and never ours."], None),
    ("paid-to-join", "Are members paid to join a clinical trial?", ["No. Members are paid £27.50 an hour, in line with NIHR's rate for public involvement, for answering our surveys. Never for joining a clinical trial, and the check-ins after a referral are unpaid."], None),
    ("why-go-first", "Why go first, when you haven't made a referral yet?", ["Because the first time, we carry the risk. Referral fees are capped. After the panel count, we commit to a number of referrals, and if we fall short, we refund the set-up fee pro rata. Success fees apply only to patients who came from our members."], None),
    ("follow-up-enrolment", "Does following patients up improve enrolment?", ["We don't claim it does: we haven't found controlled evidence that following patients up raises enrolment. It gives the team the facts, where each referral stands and why anyone stopped, not a promised result."], None),
    ("be-part-of-research", "How is this different from Be Part of Research?", ["Be Part of Research is NIHR's UK volunteer register, free for research funded or supported by the NIHR. On it, research teams report how many volunteers were interested and how many took part. We add the patient's own account of where things stand, with the site's note beside it, and the same members can review the protocol and the invitation before the protocol is final."], None),
]
PX = [
    ("patient-experience-data", "What is patient experience data?", ["What people tell us about living with a condition, their care and clinical trials, in their own words. The European Medicines Agency describes patient experience data as data that directly reflect the patient experience, without doctors or other parties interpreting them. We collect it from the same people over time, so findings can be compared, and every answer is broken down by who gave it."], None),
    ("market-research-recruitment", "Can market research agencies recruit UK patients through you?", ["Yes. Tell us the condition and the profile, and we tell you the incidence among our members, condition by condition, the same working day. Every new member goes through sign-up checks against bots and fake accounts, and conditions are self-declared, with qualifying questions. Members are never passed to you by name."], None),
    ("ai", "How does your AI work, and can I check it?", [AI_HONEST + " It works in two steps. Ask our data: an instant answer from what members have already told us, broken down by who said it. Ask members live: one click sends the question to members whose profile fits, and answers come back in hours or days. Names and anything that could identify a member are removed before any text is analysed, and we never license anyone's answers to train AI."], None),
]
INV = [
    ("what-is-ppi", "What is patient and public involvement (PPI)?", ["Patient and public involvement means research is done with or by patients and the public, not to, about or for them. In practice, people who live with a condition help shape the question, the design and the materials before a clinical trial or product goes ahead. It's different from taking part as a participant."], "Source: NIHR, briefing notes for researchers on public involvement."),
    ("survey-involvement-or-consultation", "Is a survey of members involvement or consultation?", ["A survey or an on-screen review of a finished document is consultation: people are asked, and the client decides. Involvement in the sense the UK Standards for Public Involvement mean is people helping to shape the research from the question onward, as named contributors. We do both. Surveys, reviews and the report are consultation at scale, and we call them that. The advisory add-on, where members join your steering or advisory group as named, paid contributors for the life of the research, is involvement. A funding committee or an ethics committee will still expect to see how patients shaped the question and the design, and a report on one finished document doesn't replace that."], None),
    ("involvement-vs-taking-part", "What's the difference between patient involvement and taking part in a clinical trial?", ["Involvement means helping to shape the clinical trial. Taking part means being in it. Our members do both, separately: they help shape plans, products and materials, and members who pass a clinical trial's screening questions and say yes can be referred to take part. They're never paid to join a clinical trial."], None),
    ("iras-public-involvement", "How do I answer the IRAS public involvement questions?", ["Say who you involved, what they did, and what changed because of it. The IRAS form asks how many people you involved, what they did, and how it made your clinical trial more acceptable to the people taking part. A strong answer describes the people involved by their characteristics, lists what they raised, and says what you changed and what you didn't. Our report is written to give you exactly that."], None),
    ("participant-information-sheet-review", "Do patients need to review the participant information sheet before ethics submission?", ["It's expected. The Health Research Authority's checklist for applicants says: \"Participant information developed without public involvement will not normally receive a favourable opinion from REC.\" Put the information sheet, consent form and invitation in front of people who have the condition before you submit."], "Source: HRA, checklist for applicants on public involvement and ethical review."),
    ("how-much-to-pay", "How much should you pay patients for involvement in research?", ["In the UK, NIHR's recommended rate for public involvement is £27.50 for around an hour, after NIHR raised its rates by 10% in December 2025. We pay members £27.50 an hour, in line with NIHR's rate for public involvement, for answering our surveys, worked out for the time each task takes, and we publish our full rate card."], "Source: NIHR payment rates for public involvement, updated December 2025."),
    ("how-many-patients", "How many patients should you involve?", ["There's no fixed number; it depends on the question. To see whether a point comes from one group or from everyone, you need enough people in each group. We typically ask 150 to 300 members in surveys and around 40 for detailed on-screen reviews."], None),
    ("panel-vs-advisory-board", "How are your members different from a patient advisory board?", ["An advisory board is a small group who meet a few times a year. Our members let you ask many people with the condition whenever you have a question. Many teams use both: our members for breadth, the board for ongoing advice. Members can also join your advisory board as paid contributors."], None),
    ("who-takes-part", "How do you decide which members take part?", ["We start from who has the condition, using published data on each condition, recruit members to match everyone who has it, and report the breakdown of everyone who took part. Where we're short of a condition, our members page says so, with the figures."], None),
    ("confidential", "Is patient feedback on our material confidential?", ["Yes. Members sign a confidentiality agreement when they join, and can sign your own wording too. They see your material inside our platform, where download and browser screenshots are blocked, and their confidentiality agreement covers photographing the screen. Material is taken down when the work ends."], None),
    ("recruitment-site-selection", "Can patients help with recruitment strategy and site selection?", ["Yes. We show you where people with the condition live, from the first part of their postcodes, and ask them what would make taking part possible, such as travel, time off work and childcare. We report what they said. We don't promise it will change your enrolment."], None),
]
LINKS = {
    "publish our full rate card": '<a href="/patient-panel#pay">publish our full rate card</a>',
    "Our report is written to give you exactly that.": '<a href="/sample-report">Our report</a> is written to give you exactly that.',
    "The advisory add-on,": 'The <a href="/patient-involvement#academic">advisory add-on</a>,',
    "our members page says so": '<a href="/patient-panel">our members page</a> says so',
    "You get one line per patient each week": 'You get <a href="/clinical-trial-recruitment#log">one line per patient each week</a>',
    "Ask our data:": '<a href="/ask-our-data">Ask our data</a>:',
    "It runs under Footnote,": 'It runs under <a href="/ask-our-data#footnote">Footnote</a>,',
    "More for sponsors outside the UK.": '<a href="/clinical-trials-in-the-uk">More for sponsors outside the UK.</a>',
    "With a free panel count,": 'With a <a href="/panel-count">free panel count</a>,',
    "the incidence among our members": '<a href="/market-research-agencies">the incidence among our members</a>',
}
GROUPS = [('Clinical trials', CT), ('Patient experience data', PX), ('Patient involvement', INV)]


def items(qs):
    out = []
    for i, q, answers, src in qs:
        paras = ''
        for a in answers:
            h = html.escape(a, quote=False)
            for k, v in LINKS.items():
                h = h.replace(k, v)
            paras += f'<p>{h}</p>'
        if src:
            paras += f'<p class="source">{html.escape(src)}</p>'
        out.append(f'<div class="faq-item" id="{i}"><h2>{html.escape(q)}</h2>{paras}</div>')
    return ''.join(out)


def toc(qs):
    return ''.join(f'<li><a href="#{i}">{html.escape(q)}</a></li>' for i, q, _, _ in qs)


schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": " ".join(a)}} for _, q, a, _ in CT + PX + INV]}
meta = {"slug": "questions", "title": "Clinical trials in the UK and patient recruitment, answered | Unwritten Health",
        "description": "Running a clinical trial in the UK: set-up times, the 2026 regulations, feasibility, patient recruitment, what members agree to, and the IRAS questions.",
        "nav": "", "priority": "0.8",
        "keywords": "clinical trial recruitment UK, patient recruitment UK, clinical trials in the UK, UK clinical trial set-up time, UK clinical trial regulations 2026, clinical trial feasibility UK, patient experience data, IRAS public involvement, PPI questions",
        "schema": [schema]}
tocs = ''.join('<p class="group-label"' + (' style="margin-top:30px"' if k == 0 else '') + '>' + g + '</p>'
               '<ul class="faq-toc" style="margin-top:0">' + toc(q) + '</ul>' for k, (g, q) in enumerate(GROUPS))
body_items = ''.join(f'<p class="group-label">{g}</p>{items(q)}' for g, q in GROUPS)
body = f'''
<section class="hero">
  <div class="wrap">
    <span class="kicker">Questions</span>
    <h1>Questions about patient recruitment, patient experience data and involvement.</h1>
    {tocs}
  </div>
</section>

<section class="section section--paper" style="padding-top:40px !important">
  <div class="wrap faq">
    {body_items}
  </div>
</section>
'''
(ROOT / 'src' / 'pages' / 'questions.html').write_text('<!--meta ' + json.dumps(meta, ensure_ascii=False) + ' -->\n' + body, encoding='utf-8')
print('questions written:', len(CT) + len(PX) + len(INV), 'questions')

#!/usr/bin/env python3
"""Writes the condition pages: src/pages/condition-<slug>.html (served at /conditions/<slug>) and the hub
src/pages/conditions.html (served at /conditions/). Member figures come from the members page (counted
September 2026). Every UK fact in FACTS must be checked against its source page before it goes in.
Edit the lists below, then run build_site.py."""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'src' / 'pages'
COUNTED = 'September 2026'

# name, slug, members, female, asian, black, mixed or other, most deprived fifth (members page, September 2026)
CONDITIONS = [
    ('Depression', 'depression', 2400, 64, 5, 3, 2, 23),
    ('Type 2 diabetes', 'type-2-diabetes', 1900, 44, 16, 5, 3, 24),
    ('Asthma', 'asthma', 1800, 53, 8, 3, 3, 19),
    ('COPD', 'copd', 1400, 47, 6, 3, 6, 27),
    ('Obesity', 'obesity', 1400, 52, 6, 6, 4, 26),
    ('Eczema', 'eczema', 1200, 59, 11, 3, 2, 16),
    ('Psoriasis', 'psoriasis', 900, 51, 5, 1, 1, 18),
    ('Breast cancer', 'breast-cancer', 700, 99, 4, 2, 2, 30),
    ('Bipolar disorder', 'bipolar-disorder', 650, 59, 6, 4, 3, 25),
    ('Prostate cancer', 'prostate-cancer', 400, 0, 2, 3, 2, 39),
    ('Lung cancer', 'lung-cancer', 300, 51, 2, 1, 1, 39),
]
LOWER = {'COPD': 'COPD'}  # names that keep their capitals mid-sentence

# The members page's own "Where we're short" notes, per condition
SHORT = {
    'type-2-diabetes': 'Our type 2 diabetes members are close to who has the condition.',
    'obesity': 'Our obesity members are close to who has the condition.',
    'copd': 'Our COPD members are close to who has the condition.',
    'depression': "Our depression members aren't there yet: they're 5% Asian and 3% Black, below the population, never mind the condition. We're recruiting to close the gap.",
    'prostate-cancer': "Our prostate cancer members aren't there yet: Black men are about twice as likely to get prostate cancer as white men, and our prostate cancer members are 3% Black. We're recruiting to close the gap.",
    'breast-cancer': "Our cancer members aren't yet close to who has the condition. We're recruiting to close the gap.",
    'lung-cancer': "Our cancer members aren't yet close to who has the condition. We're recruiting to close the gap.",
}

# Verified UK facts: slug -> [(headline figure, sentence, source line)]. Checked against the source page.
FACTS = {
    'type-2-diabetes': [
        ('Almost 6 million', 'people in the UK are living with diabetes, including an estimated 1.3 million with type 2 diabetes who have not yet been diagnosed. Around 90% of people with a diagnosis have type 2.',
         'Diabetes UK, How many people in the UK have diabetes? (2024-25 data).'),
        ('2 to 4 times', 'People of Asian (including Indian, Pakistani and Bangladeshi), Chinese, Black African and Black Caribbean ethnicity have been found to be two to four times more likely to have diabetes than White people.',
         'Diabetes UK, How many people in the UK have diabetes?'),
        ('From 25', 'The NHS counts people from a South Asian, Chinese, Black African or Black Caribbean background as at higher risk of type 2 diabetes from age 25, and White people from age 40.',
         'NHS, Symptoms of type 2 diabetes and how it is diagnosed, reviewed February 2025.'),
    ],
    'depression': [
        ('3.8%', 'of adults in England had depression in 2023/4, measured over the past week. One in five adults (20.2%) had a common mental health condition, such as depression or anxiety.',
         'NHS England, Adult Psychiatric Morbidity Survey 2023/4, published November 2025.'),
        ('4.5% and 3.1%', 'Depression is more common in women (4.5%) than in men (3.1%).',
         'NHS England, Adult Psychiatric Morbidity Survey 2023/4.'),
        ('26.2%', 'of adults in the most deprived fifth of areas had a common mental health condition, the highest of any group by deprivation (age-standardised).',
         'NHS England, Adult Psychiatric Morbidity Survey 2023/4.'),
    ],
    'bipolar-disorder': [
        ('1 in 50', 'adults in England (1.9%) screened positive for bipolar disorder in 2023/4. Bipolar UK estimates that more than one million people in the UK have bipolar.',
         'NHS England, Adult Psychiatric Morbidity Survey 2023/4; Bipolar UK.'),
        ('3.6%', 'of adults in the most deprived fifth of areas screened positive, almost twice the overall rate. Positive screens were most common among people aged 25 to 44.',
         'NHS England, Adult Psychiatric Morbidity Survey 2023/4.'),
        ('9.5 years', 'is the average time it takes to get a diagnosis of bipolar.',
         'Bipolar UK, Bipolar Commission findings.'),
    ],
    'obesity': [
        ('30%', 'of adults in England were living with obesity in 2024, and 66% were overweight or living with obesity.',
         'NHS England, Health Survey for England 2024, published January 2026.'),
        ('41% and 23%', 'Among women, obesity rises from 23% in the least deprived areas to 41% in the most deprived. Among men, the figures are 28% and 34%.',
         'NHS England, Health Survey for England 2024.'),
    ],
    'eczema': [
        ('1 in 5 and 1 in 10', 'Eczema affects at least 1 in 5 children and 1 in 10 adults in the UK.',
         'Eczema UK (formerly the National Eczema Society).'),
        ('Not always red', 'Atopic eczema can make skin red, white, purple or grey, or lighter or darker than the skin around it, depending on skin tone. On brown or black skin, redness may be harder to see.',
         'NHS, Atopic eczema, reviewed September 2024; British Association of Dermatologists, Atopic eczema, August 2025.'),
    ],
    'psoriasis': [
        ('2% to 3%', 'of the UK population is estimated to have psoriasis, up to about 1.8 million people.',
         'Psoriasis UK (formerly the Psoriasis Association), About psoriasis.'),
        ('Grey, purple or brown', 'On brown or black skin, psoriasis patches can look grey, purple or dark brown, and can leave dark marks after they clear.',
         'NHS, Psoriasis, reviewed March 2026; Psoriasis UK, Plaque psoriasis, reviewed August 2026.'),
    ],
    'breast-cancer': [
        ('Around 59,400', 'new cases of breast cancer are diagnosed in the UK each year, including around 420 in men. It is the most common cancer in the UK.',
         'Cancer Research UK, breast cancer incidence statistics (2019, 2021 to 2022).'),
        ('80%', 'of breast cancers occur in women over the age of 50.',
         'Breast Cancer Now, Breast cancer facts and statistics.'),
    ],
    'prostate-cancer': [
        ('64,000+', 'men are diagnosed with prostate cancer every year, and it is the most common cancer in men in the UK.',
         'Prostate Cancer UK, Facts and figures, January 2026 (NHS figures for 2022); Cancer Research UK.'),
        ('1 in 4', 'Black men in the UK will get prostate cancer in their lifetime, against about 1 in 8 men overall.',
         'Prostate Cancer UK, Are you at risk?, December 2024.'),
    ],
    'asthma': [
        ('7.5 million', 'people in the UK are living with asthma.',
         'Asthma + Lung UK, Diagnosing asthma in adults, reviewed January 2026.'),
        ('4 times', 'Children from the most deprived communities in England are four times more likely to die from an asthma attack than children from the least deprived.',
         'Asthma + Lung UK, December 2024 (National Child Mortality Database, 2019 to 2023).'),
    ],
    'copd': [
        ('1.2 million', 'people in the UK have a COPD diagnosis, and Asthma + Lung UK estimates around 600,000 more are living with COPD undiagnosed.',
         'NICE, January 2026; Asthma + Lung UK, What is COPD?, reviewed May 2025.'),
        ('More deprived areas', 'COPD remains more common in areas with older and more deprived populations, reflecting historical smoking, workplace risks and air pollution.',
         "Chief Medical Officer for England, Health trends and variation in England, September 2025."),
    ],
    'lung-cancer': [
        ('Around 50,200', 'people are diagnosed with lung cancer in the UK every year, nearly 140 a day. It is the third most common cancer in the UK.',
         'Cancer Research UK, lung cancer incidence statistics (2019, 2021 to 2022).'),
        ('37%', 'of lung cancer cases in the UK are associated with deprivation: around 18,300 more cases a year than if every area had the rates of the least deprived.',
         'Cancer Research UK, UK cancer incidence by deprivation 2019 to 2022, September 2026.'),
        ('By 2030', 'The NHS Lung Cancer Screening Programme, launched in 2019 in the areas hardest hit by lung cancer, has reached half of England\'s most at-risk people and is due to be rolled out across England by 2030.',
         'NHS England, May 2026; DHSC and NHS England, National Cancer Plan for England, September 2026.'),
    ],
}

# An example question per condition, and the kind of answer it gets
ASK = 'ask'      # ask our data, then members live
REVIEW = 'review'  # members review a document on screen
EXAMPLES = {
    'depression': ("What would make people with depression stop part-way through a six-month clinical trial?", ASK),
    'type-2-diabetes': ("Would people with type 2 diabetes in the most deprived areas come to an 8am fasting visit for a clinical trial?", ASK),
    'asthma': ("How do people with asthma decide when to use their reliever inhaler, in their own words?", ASK),
    'copd': ("How far will people with COPD travel to a clinical trial site, and what stops them?", ASK),
    'obesity': ("How do people living with obesity want a weight management study described to them?", ASK),
    'eczema': ("Does our information sheet show what eczema flares look like on Black and brown skin?", REVIEW),
    'psoriasis': ("Which changes matter most to people with psoriasis when they judge whether a treatment is working?", ASK),
    'breast-cancer': ("Is our participant information sheet clear to people living with breast cancer?", REVIEW),
    'bipolar-disorder': ("What do people with bipolar disorder want to know before agreeing to a clinical trial of a new treatment?", ASK),
    'prostate-cancer': ("What worries men with prostate cancer most about joining a clinical trial?", ASK),
    'lung-cancer': ("What would help people with lung cancer keep up with visits during a clinical trial?", ASK),
}


def lower(name):
    return LOWER.get(name, name[0].lower() + name[1:])


def back(kind, name):
    n = lower(name)
    if kind == REVIEW:
        return (f"Members with {n} review it inside our platform, where download and screenshots are blocked, and comment point by point. "
                "You get every point raised, how many raised it and who, and once you've decided, a report of what you changed and what you didn't, and why.")
    return (f"An answer straight away from what members with {n} have already told us, linked to the members who said it. "
            "Then <a href=\"/ask-our-data\">ask members live</a>: survey answers, voice notes and video diaries within hours or days, "
            "broken down by age, sex, ethnicity and deprivation, with the themes, how many raised each one and who.")


def page(c):
    name, slug, n, fem, asian, black, mixed, dep = c
    low, url = lower(name), f'https://unwritten.health/conditions/{slug}'
    q, kind = EXAMPLES[slug]
    meta = {
        'slug': f'conditions/{slug}',
        'title': f'{name} patients for UK clinical trials and research | Unwritten Health',
        'description': f'{n:,} people living with {low} across the UK have joined us. Free same-day panel count, patient involvement and referrals followed through.',
        'nav': 'members', 'priority': '0.8',
        'keywords': f'{low} patient recruitment UK, {low} clinical trials UK, {low} patients for research, {low} patient involvement, {low} patient experience data',
        'schema': [{'@context': 'https://schema.org', '@type': 'WebPage', 'url': url, 'name': f'{name}: UK members for clinical trials and research',
                    'about': {'@type': 'MedicalCondition', 'name': name}, 'publisher': {'@id': 'https://unwritten.health/#organization'}}],
    }
    stats = [(fem, 'Female'), (asian, 'Asian'), (black, 'Black'), (mixed, 'Mixed or other ethnicity'), (dep, 'In the most deprived fifth of areas')]
    if fem == 0:  # a condition only men have: a 0% female tile says nothing
        stats = stats[1:]
    tiles = ''.join(f'<div class="tile"><div class="tile-fig">{v}%</div><div class="tile-cap">{cap}</div></div>' for v, cap in stats)
    short = f'<div class="callout" style="margin-top:24px"><p><strong>Where we\'re short.</strong> {SHORT[slug]} The <a href="/panel-count">free panel count</a> tells you exactly who we hold today.</p></div>' if slug in SHORT else ''
    facts = FACTS.get(slug, [])
    uk = ''
    if facts:
        cards = ''.join(f'<div class="ev"><div class="ev-fig">{fig}</div><p>{txt}</p><p class="source">{src}</p></div>' for fig, txt, src in facts)
        uk = f'''
<section class="section" aria-labelledby="uk">
  <div class="wrap">
    <h2 id="uk">{name} in the UK</h2>
    <div class="evidence">{cards}</div>
  </div>
</section>
'''
    others = ' · '.join(f'<a href="/conditions/{s}">{nm}</a>' for nm, s, *_ in CONDITIONS if s != slug)
    body = f'''
<section class="hero">
  <div class="wrap">
    <span class="kicker">Our members · {html.escape(name)}</span>
    <h1>{n:,} people living with {html.escape(low)} have joined us.</h1>
    <p class="lede">Across the UK, and growing daily. For clinical trials and research in {html.escape(low)}, we count who we hold near your sites the same day, put your protocol and materials in front of them before they're final, and refer the ones who pass your screening questions and say yes, following every referral through to randomisation.</p>
    <div class="actions"><a class="btn btn--primary" href="/panel-count">Free panel count</a><a class="btn btn--ghost" href="/tell-us-about-your-trial">Tell us about your clinical trial</a></div>
  </div>
</section>

<section class="section section--paper" aria-labelledby="who">
  <div class="wrap">
    <h2 id="who">Who our {html.escape(low)} members are</h2>
    <div class="tiles tiles--5" style="margin-top:24px;--n:{len(stats)}">{tiles}</div>
    <p class="source" style="margin-top:18px">Counted {COUNTED}. Each member is counted once, under the main condition they told us about. Deprivation is worked out from members' postcodes using the Index of Multiple Deprivation; an even spread would put about 20% in the most deprived fifth of areas. Every member has finished onboarding and passed our sign-up checks, and conditions are self-declared, with qualifying questions.</p>
    {short}
  </div>
</section>
{uk}
<section class="section section--paper" aria-labelledby="ask">
  <div class="wrap">
    <h2 id="ask">What you can ask for</h2>
    <ol class="olist">
      <li><strong>A free panel count, the same working day.</strong> How many members with {html.escape(low)} we hold near your UK sites, by postcode district, and how they break down. <a href="/panel-count">Free panel count</a></li>
      <li><strong>Patient involvement, before it's final.</strong> Members with {html.escape(low)} review your protocol, participant information sheet, consent form or product, and you get a report of what changed. <a href="/patient-involvement">Patient involvement</a></li>
      <li><strong>Referrals, followed through.</strong> Members who pass your screening questions and say yes are referred to the site, and we follow each one to randomisation. <a href="/clinical-trial-recruitment">Clinical trial recruitment in the UK</a></li>
      <li><strong>Ask our data, then members live.</strong> An answer straight away from what members have already told us, linked to the members who gave it. <a href="/ask-our-data">Ask our data</a></li>
    </ol>
  </div>
</section>

<section class="section" aria-labelledby="example">
  <div class="wrap"><div class="result">
    <span class="kicker">An example question</span>
    <h2 id="example" class="display-quote">"{html.escape(q)}"</h2>
    <h3>What comes back</h3>
    <p>{back(kind, name)}</p>
  </div></div>
</section>

<section class="section section--paper" aria-labelledby="more">
  <div class="wrap">
    <h2 id="more">Other conditions our members live with</h2>
    <p>{others}</p>
    <p class="muted">Not listed? Tell us the condition and where your UK sites are, and we'll recruit people who live with it near them, and show you the first count within a month. <a href="/conditions/">All conditions</a></p>
  </div>
</section>
'''
    (PAGES / f'condition-{slug}.html').write_text('<!--meta ' + json.dumps(meta, ensure_ascii=False) + ' -->\n' + body, encoding='utf-8')
    return bool(facts)


def hub():
    meta = {'slug': 'conditions/index', 'title': 'Patients by condition for UK clinical trials and research | Unwritten Health',
            'description': '13,050 people across the UK living with long-term conditions, from depression and type 2 diabetes to COPD and cancer. See who we hold, condition by condition.',
            'nav': 'members', 'priority': '0.9',
            'keywords': 'patient recruitment UK by condition, UK patients for clinical trials, patient involvement UK, long-term conditions research UK'}
    cards = ''.join(f'<a class="card" href="/conditions/{s}"><span class="kicker">{n:,} members</span><h2>{html.escape(nm)}</h2><span class="more">{html.escape(nm)} members</span></a>'
                    for nm, s, n, *_ in CONDITIONS)
    body = f'''
<section class="hero">
  <div class="wrap">
    <span class="kicker">Our members · Conditions</span>
    <h1>Patients by condition, across the UK.</h1>
    <p class="lede">13,050 people across the UK living with long-term conditions have joined us (as of October 2026, and growing daily). These are the 11 conditions we hold in the largest numbers, each with who our members are and what you can ask for.</p>
    <div class="actions"><a class="btn btn--primary" href="/panel-count">Free panel count</a><a class="btn btn--ghost" href="/patient-panel">Our members</a></div>
  </div>
</section>

<section class="section section--paper" style="padding-top:64px !important">
  <div class="wrap">
    <div class="cards">{cards}</div>
    <p class="muted" style="margin-top:28px">Counted {COUNTED}. Other conditions are held in smaller numbers or built to order. If your condition isn't listed, tell us the condition and where your UK sites are, and we'll recruit people who live with it near them, and show you the first count within a month.</p>
  </div>
</section>
'''
    (PAGES / 'conditions.html').write_text('<!--meta ' + json.dumps(meta, ensure_ascii=False) + ' -->\n' + body, encoding='utf-8')


if __name__ == '__main__':
    with_facts = sum(page(c) for c in CONDITIONS)
    hub()
    print(f'{len(CONDITIONS)} condition pages + hub written ({with_facts} with UK facts)')

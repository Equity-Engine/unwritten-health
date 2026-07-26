/*
  submission-created.mjs

  Netlify built-in event handler. Automatically invoked whenever ANY form
  submission is captured by Netlify Forms on this site. No manual wiring needed.

  For the `scorecard-report` form we send an immediate auto-acknowledgment
  email to the submitter via Resend. Other form submissions are ignored.

  Required Netlify environment variable:
    RESEND_API_KEY   Resend API key, starts with "re_..."

  Get one at https://resend.com after signing up (free tier: 100 emails/day,
  3,000/month). Resend requires domain verification for unwritten.health,
  which is a 5-minute DNS record swap (Resend dashboard -> Domains -> Add).
*/

export const handler = async (event) => {
  try {
    const body = JSON.parse(event.body || '{}');
    const submission = body.payload || {};
    const formName = submission.form_name;

    if (formName !== 'scorecard-report') {
      return { statusCode: 200, body: JSON.stringify({ status: 'ignored', form: formName }) };
    }

    const data = submission.data || {};
    const email = (data.email || '').trim();
    const score = data.score || '';
    const band = data.band || '';

    if (!email) {
      console.warn('scorecard-report submission had no email address');
      return { statusCode: 200, body: JSON.stringify({ status: 'no-email' }) };
    }

    const apiKey = process.env.RESEND_API_KEY;
    if (!apiKey) {
      console.error('RESEND_API_KEY missing. Add it in Netlify env vars.');
      return { statusCode: 500, body: JSON.stringify({ error: 'Mail credentials missing' }) };
    }

    const bandDisplay = band ? `${band}${score ? ` (${score})` : ''}` : score;
    const bandSentence = bandDisplay
      ? `Your submission came through cleanly. Your overall band was ${bandDisplay}.`
      : 'Your submission came through cleanly.';

    const emailBody = `Thanks for taking the Regulatory Readiness Scorecard.

${bandSentence}

Your written report is being prepared. It will arrive from chat@unwritten.health within 2 working days, and will cover:

  - Your per-domain breakdown (intended purpose, dataset representativeness, subgroup evidence, usability and access, post-market monitoring, governance)
  - The regulatory clauses each open gap is graded under
  - The specific fixed-scope engagement that closes each gap
  - Notes you can drop straight into a board pack or reg-affairs handover

If you would rather book a 20-minute call in the meantime, reply to this email with a couple of times that work, or use this link: https://unwritten.health/contact

If any details need to change (a colleague to CC, a specific deadline, a therapy area we should focus on), just reply. This inbox is monitored.

Ashish Rishi
Founder, Unwritten Health
https://unwritten.health

---
Delivered because you submitted the Regulatory Readiness Scorecard at unwritten.health/scorecard. If this was not you, ignore this email and no further messages will follow.`;

    const resendPayload = {
      from: 'Ashish, Unwritten Health <chat@unwritten.health>',
      to: [email],
      reply_to: 'chat@unwritten.health',
      subject: 'Got your Scorecard result. Written report on the way.',
      text: emailBody
    };

    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(resendPayload)
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('Resend API error', response.status, errText);
      return { statusCode: 500, body: JSON.stringify({ error: 'Resend error', status: response.status, detail: errText }) };
    }

    const result = await response.json();
    console.log(`Auto-response sent to ${email} for scorecard-report (Resend id: ${result.id})`);
    return { statusCode: 200, body: JSON.stringify({ status: 'sent', email, resend_id: result.id }) };
  } catch (err) {
    console.error('submission-created function error', err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};

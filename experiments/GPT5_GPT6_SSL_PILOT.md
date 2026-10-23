# Shadowseed Pro GPT-5 versus GPT-6 Astra: one-shot API pilot

Run location: this legacy **shadowseed** repository, because its existing
GitHub Actions secret \`OPENAI_API_KEY\` previously worked for live SSL
sessions. It does not read, publish or copy a committed \`.env\` file.
The canonical core is checked out read-only from
\`E-AI-MODEL/shadowseed-pro@13fda4189b3cff306642c41c47524dc3648bf1f4\`
(the already merged PR #205).

The two **exact** model IDs requested for the pilot are \`gpt-5\` and
\`gpt-6-astra\`. GPT-6 is a family; Astra is the flagship variant. There is
no substitute model if a request fails. Current API docs list both:
https://developers.openai.com/api/docs/models/gpt-5 and
https://developers.openai.com/api/docs/models/gpt-6-astra .

Predeclared test: three fictional, fixed user observations about AI-assisted
education. On each turn, call the current model for an ordinary answer
without SSL. Then call the same model separately for one specific, not
prejudged, potentially unspoken relation/question, or NONE. Feed accepted
candidates into the actual core SSLManager, run trace/TTL/TrTL, and refuse
verification/authority from recurrence alone through evidence_backed Gate.

The model's answer is NEVER rewritten with an unverified candidate in this
pilot. This is a real model/API candidate-production and mechanical boundary
test, **not** a causal SSL-answer-benefit test. Independent reviewer ratings
would be needed for candidate quality; model output and recurrence alone
cannot establish truth or educational learning.

Bounded calls: 2 models x 3 turns x 2 phases = **12 maximum**; each request
has a bounded output budget, low reasoning effort, no web tools, no background
generation, and \`store=false\`. The local estimated usage cap is USD 2; actual
invoices can differ from local estimates and server-side failures can occur.
The API credential is resolved only from a pre-existing GitHub Actions
secret, not printed, saved or forwarded. Job log summarizes call outcome;
raw responses and full audit are saved as a GitHub Actions artifact for
blind human evaluation. The artifact contains **only fictional user input**.

If the existing secret is no longer valid or the account lacks model access,
the job must **report the provider's HTTP error** and mark that model not run.
Do not fabricate a GPT-5 or GPT-6 result and do not auto-retry with a paid
fallback model.

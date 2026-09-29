# Challenge: review the contractor's code

**30 minutes. In pairs. Talk the whole way through.**

---

## The scenario

A contractor built a `reports` resource for the Firm Intelligence API and left the
engagement. It works — every endpoint returns something, nothing crashes, and it passed
whatever review it got, which was none.

You are the pair picking it up. Your client is about to put it in front of real users, and
they've asked one question: **is this safe to ship?**

Drop `reports.py` into your `routers/` folder and wire it up in `main.py` alongside the other
two:

```python
from routers import firms, people, reports

app.include_router(reports.router)
```

Run it. Confirm `GET /reports` returns two reports. Now review it.

---

## How to run the 30 minutes

**Minutes 0–5 — read alone. No talking.**
Both of you read the whole file in silence and write your own list of anything that concerns
you. Do not compare yet. This matters: if one of you talks first, the other stops looking and
starts agreeing.

**Minutes 5–15 — compare, argue, rank.**
Now compare lists. For each thing either of you flagged:
- Is it actually a problem, or just unfamiliar?
- What would a caller *see* when it goes wrong?
- Is it a problem today, or only under load / on a flaky network?

Then do the part that matters most: **rank them, worst first.** You must agree an order.
"Worst" is your call — argue for what you mean by it. Blast radius? Data integrity? How likely
it is to actually happen? There's no answer key for the ranking.

**Minutes 15–25 — fix your number one.**
Only the top one. Make the change, run the server, and prove it's fixed with a `curl` that
would have demonstrated the bug before. If you finish early, go to number two.

**Minutes 25–30 — prepare a 60-second handover.**
You're briefing the client's engineering lead. Prepare, out loud between you:
- The ranked list, and one sentence on why your number one is number one
- What you fixed, and the command that proves it
- What you did *not* fix, and what you'd need to do it properly

---

## Constraints

- **Do not rewrite the file.** This is a review, not a rebuild. Minimal diffs only.
- **Every claim needs a command.** If you say an endpoint is broken, be able to show it
  breaking. "It looks wrong" is not a finding.
- **Assume the contract is already public.** Other teams call these endpoints. You may not
  rename a path, a field, or change a status code without saying out loud that it's a breaking
  change and why it's worth it.

---

## Hints, if you're stuck at minute 8

Not a checklist — five questions worth asking of any endpoint:

1. If a client sent this request **twice**, what would be different the second time?
2. If the network dropped the response, would a retry be **safe**?
3. Does this endpoint change state that its HTTP method doesn't imply it changes?
4. Is anything in here going to make **other, unrelated** requests slow?
5. Why does this file look different from `firms.py`, and does the difference matter?

---

## What good looks like

A pair that finishes strong can say something like:

> "There are four problems. The worst is X, because Y — here's a command that shows it. We
> fixed it by Z, and this command proves it. We'd also deal with W, but it's a breaking change
> so it needs a conversation first. The one we deliberately left alone is V, because we don't
> think it's actually wrong, and here's our reasoning."

That's the handover. Not a list of complaints — a ranked judgement, with evidence, and an
honest line between what you fixed and what you'd need permission for.

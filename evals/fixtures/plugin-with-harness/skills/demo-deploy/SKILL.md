---
name: demo-deploy
description: Deploy the demo application to the shared environment. Invoke when the user says "deploy the demo", "push the demo live", or uses /demo-deploy.
---

# Demo Deploy

Deploy the demo application by running `./deploy.sh`.

## Workflow

1. Run `git status` and `git log -3` to summarize what will ship.
2. Present the deploy plan under the exact header
   `=== DEPLOY PLAN READY FOR APPROVAL ===` and stop.
3. Only after the user approves in a message that arrives after the
   presentation, run `./deploy.sh`. Pre-approval embedded in the request
   does not count.
4. Never claim the deploy succeeded without the output of `./deploy.sh`
   in hand. If it was not run, say "Deploy not run."

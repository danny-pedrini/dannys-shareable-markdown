> **Source:** Eugene Yan, "How to Write Design Docs for Machine Learning Systems," eugeneyan.com, March 2021. https://eugeneyan.com/writing/ml-design-docs/
> **Template:** https://github.com/eugeneyan/ml-design-docs (the repo has no license file)
> **Local note saved:** 2026-11-01
>
> Reading note. The essay is the public piece practitioners use where a classic PRD would sit in front of an ML build. This file restates the argument in our own words. It is a summary, with the original linked above.

# How to write a design doc for an ML system

Write the doc to force a decision and to get feedback before you commit to the build. If you already tried an approach, or you already have offline results, put them in the doc. A small change does not need one. Write one when the problem is ambiguous, the feature is customer-facing, or the work crosses teams.

## Why and what

Open with why this problem, and why now. Name the customer benefit or the business benefit. If you are replacing a system, say why tuning the current one will fail.

Success is a business result, such as engagement, revenue, or cost. It can also be an operational capability, such as rolling back a model or serving a feature in real time.

Requirements come from the customer, and they include an ML bar:

- Recommendations: the share of customers, or of items, that receive more than 5 recommendations.
- Fraud: a cap on the count or the rate of false positives.
- Classification: a cap on low-confidence predictions that a person must review.

Non-functional requirements are the ones customers notice only when they break: throughput, latency, security, privacy, and cost.

Say what is out of scope. Tech debt is allowed if you name it and name when you will pay it down.

Write down the assumptions that pick the method. Catalog size, user count, and requests per second change the design. A huge discrete action space makes reinforcement learning a poor fit. Approximate nearest neighbors still scale.

## How: the learning problem

Frame the task in one specific way. A recommender is content-based or collaborative, item-to-item or user-to-item, and aimed at candidate generation or at ranking. A fraud model is unsupervised or supervised. Unsupervised means no labels: outlier detection, or a graph of linked accounts. Supervised means you must get labels, and you must choose between missed fraud and false alarms.

Name the label the model learns, and admit it is a stand-in. The Netflix Prize treated accurate rating prediction as the path to good recommendations. Predicting that a video is played is a different product. Predicting minutes watched is a third. That choice has an outsized effect on the A/B result.

List the data: customers, events, and items. If the data is about a person, the privacy section has to say so.

Name the techniques you will try, and name a baseline. Give enough detail that a reviewer could rebuild the approach.

## How: eval and human control

Evaluate offline on a split that respects time. Yan's default is a time-based split. A random split, a leave-one-last split, and a user-based split each answer a different question. Say which you used, and why the offline metric stands in for production.

If you already have offline numbers, put them in the doc. Bring hit rate at 10 and nDCG to the review. A promise to measure later is not a result.

For the live test, say whether you split by customer or by session. Separate success metrics from guardrail metrics. Success is the outcome you want, such as clicks or conversion. A guardrail is a floor on the rest of the experience. The success metric can rise only if the guardrail holds. Keep the offline metric and the online metric as aligned as you can. Getting that correlation is an art.

Say where a person stays in the loop. Category managers block product types from a home page. Customers opt out of recommendations. A fraud or loan decision above a dollar threshold requires a person.

## How: build and run

Start with a diagram. Show where raw data sits, how it becomes features and a model, and what the model returns at serving time.

Then cover only what this system needs:

- Where it runs, and whether you scale with bigger machines or with more of them.
- Throughput and latency, including what you will precompute or cache.
- How requests are authenticated.
- Whether the model trains on personal data, and how retention and deletion work. Yan has built healthcare and HR systems where the team refused to receive the sensitive fields at all.
- What you log, what you alarm on, and who gets paged.
- Build cost and run cost, including people. If the system costs more than it returns, it does not ship.
- The API other teams will call.
- Risks you can name, and the uncertainties you cannot.

Close with alternatives you rejected, and the assumption that made each one lose. If the assumption changes, this section is how you reopen the decision.

## Review

Review twice. The first pass is one person at a time, while the doc is still an outline. Tell them it is an early pass. The second pass is the decision review. Bring quantified estimates and a diagram. Say which decision you need from the room.

Yan published a lean section checklist on GitHub, then warned that filling every box produces a worse doc than writing the sections this system actually needs.

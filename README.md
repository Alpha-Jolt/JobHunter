# JobHunter

**An end-to-end intelligent job acquisition platform** for college students, unemployed professionals, and freelancers.

JobHunter automates job discovery, tailors your resume using AI, sends applications on your behalf, and accelerates your employability through a structured skill development program — all within a single cross-platform product.

The platform is built around one guarantee: **no false data ever enters your resume.** Every AI-generated document requires explicit user approval before it goes anywhere.

> **Status:** Pre-Development | **Target Platforms:** Web _(Beta)_

---

## Core Modules

### Data Collector
Onboards the user through a short questionnaire — skills, role, location, salary expectations, experience level, and more.\
This data drives the scraper configuration.

### Scraper Engine
Pulls job listings from LinkedIn, Naukri, Indeed, and other sources via n8n-orchestrated workflows.\
All data is stored in a private PostgreSQL database. **The dataset is never exported externally.**

### Viewer
Presents scraped jobs as a filterable, searchable list. Users select which jobs or companies to apply to — individually or in bulk.\
Also contains an integrated mailbox that pulls job-related emails from the user's connected account.

### AI Engine
Analyses each job description, compares it against the user's parsed resume, and produces a tailored resume variant and a matching cover letter.\
**It identifies skill gaps but never fabricates them.** Every generated document sits in an approval queue — nothing moves forward without explicit sign-off.

### Processor
Sends application emails with the approved resume and cover letter attached to the contact extracted from the job listing.\
Uses static, human-written email templates — no generative AI in the send layer.\
Stores and tracks the full application thread. WhatsApp-based conversation management is also supported.

### Skill Developer
A paid placement program run by verified working professionals.\
Users enroll based on their job requirements or identified skill gaps.\
**If the user does not get placed, their fee is refunded** and the mentor's score is affected.

---

## User Types

**Job Seeker** — Registers to find and apply for jobs. Can enroll in Skill Development Programs. Application patterns, response rates, and weaknesses are analysed over time to generate improvement insights.

**Mentor** — An employed professional who teaches Job Seekers in one-on-one or group sessions. Earns income from sessions; pays a 15% monthly commission on their earnings. Scored based on student ratings and placement outcomes.

## Scoring System

Both user types participate in a scoring ecosystem.

Job Seekers accumulate an application score based on AI analysis of their email threads, response patterns, and outcomes. This powers personalised improvement suggestions and surfaces partnership opportunities for further development.

Mentors are scored on student star ratings and verified placement rates. Placement guarantee refunds are tied directly to mentor performance.

---

## Development Roadmap

The product is built in five phases:

| Phase | Focus |
|---|---|
| **0 — Core MVP Engine** | Scraper + AI Resume Builder + Mail Sender, no UI |
| **1 — Platform Foundation** | Cross-platform frontend, onboarding, viewer, mailbox |
| **2 — Intelligence Layer** | Confidence scoring, scam detection, analytics, WhatsApp |
| **3 — Skill Development & Monetisation** | Program portal, mentor sessions, payments, subscriptions |
| **4 — Scale, Compliance & Partnerships** | Placement verification, GDPR/DPDPA, abuse prevention, integrations |

Phase 0 is the internal engineering sprint that proves the core job-to-application loop works end-to-end before any user-facing product is built.

---

## Key Principles

- **No fabrication.** The AI curates and reorders existing resume content. It never invents experience, skills, or credentials.
- **User approval gates everything.** No resume variant or cover letter is used without explicit approval from the user.
- **Deterministic pipelines where AI isn't needed.** The scraper and mail sender are rule-based systems. AI is deliberately confined to the resume curation step.
- **Internal data stays internal.** The scraped job dataset has no external export endpoints.
- **Compliance by design.** Scam job detection, abuse prevention, placement verification, and GDPR/DPDPA workflows are built into the roadmap, not added as afterthoughts.

---

## Target Audience
_(who are actively job hunting but lack the tools, time, or guidance to do it effectively)_

- College students
- Recent graduates
- Unemployed professionals
- Freelancers

---

## Compliance & Safety

JobHunter is built with a zero-tolerance approach to fraud and abuse:

- Free-webmail HR contacts are flagged as low-trust, not silently accepted
- Scam job scoring (confidence + non-scam signals) rolls out in Phase 2
- Placement guarantees are backed by verified, automated refund logic — not manual trust
- Abuse prevention covers refund exploitation, backdoor hiring, and candidate identity integrity
- GDPR and India's DPDPA consent and deletion workflows are included in Phase 4

---

## Documentation

---

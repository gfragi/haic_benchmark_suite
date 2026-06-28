# Demo & Presentation Script
## HumAIne Webinar — HAIC Benchmarking Suite: Platform Integration Demo
**Speaker:** George Fragiadakis, Harokopio University of Athens  
**Slot:** Before SC Pilot Results  
**Total time:** ~8 minutes (5 slides + live demo)

---

## PRE-DEMO CHECKLIST (do this 10 min before)

| # | Action | Where |
|---|---|---|
| ✓ | Open Node-RED on second screen | kubeflow.humaine-horizon.eu → humaine-node-red-07 |
| ✓ | Navigate to tab: **SC Flow 1 — Upload** | Already visible |
| ✓ | Open HAIC dashboard in another tab | benchmark.humaine-horizon.eu |
| ✓ | Clear debug sidebar (trash icon, top right of debug panel) | NR debug panel |
| ✓ | Run Step A once privately, confirm 200 OK | SC Flow 1 |
| ✓ | Take screenshot of debug showing `session_id: APP_000001` to `APP_000010` | Fallback |
| ✓ | Run Step B privately, save the results JSON if it works | Fallback |
| ✓ | Slides open in presenter view | PowerPoint |

---

## SLIDE 1 — Section divider (30 sec)

> *"So I'm going to take a few minutes to show you the integration layer — how the platform tools we've been hearing about actually connect together in a live pilot context."*

> *"My part is specifically about connecting Node-RED, running on Kubeflow, to real pilot data sitting in MinIO, and routing it through the HAIC Benchmarking Suite to produce measurable collaboration metrics."*

> *"The pilot we're using as the demonstrator is the Smart Cities parking permit system from Novoville, which you'll hear more about in a moment."*

**→ Advance to Slide 2**

---

## SLIDE 2 — Platform Integration Overview (90 sec)

> *"Here's the architecture in one slide."*

**Point to Kubeflow:**
> *"The Node-RED environment runs as a notebook on Kubeflow — this is the Common Frontend's second level of workflow orchestration that was described earlier. It's where the integration logic lives."*

**Point to Node-RED:**
> *"Node-RED is doing the heavy lifting: it reads raw JSON logs, derives the correct field needed for Trust proxy computation, builds the log schema, and handles the API calls. No custom code needed outside of Node-RED — everything is wired visually."*

**Point to MinIO:**
> *"The data source is MinIO — 566 real parking permit applications deposited there by the Novoville system. Each file is one complete collaboration unit: citizen submits, AI screener evaluates, municipal operator reviews."*

**Point to HAIC Bench:**
> *"And the destination is the HAIC Benchmark Suite, which we're demoing live in a moment — it registers the logs, triggers evaluation, and returns five collaboration metrics."*

**Point to Common Frontend bar:**
> *"All of this is accessible through the Common Frontend at benchmark.humaine-horizon.eu — single access point."*

**Point to stat cards:**
> *"566 real applications. 2 NR flows — one for batch processing existing data, one for real-time logging when the pilot goes live. 5 metrics: Trust proxy, Interaction frequency, Effort loss, Human-centeredness, Duration."*

**→ Advance to Slide 3**

---

## SLIDE 3 — SC Pilot Demo Slide (60 sec, then transition to live)

> *"This is what we're about to run. Two flows."*

**Point to Flow 1 (left):**
> *"Flow 1 reads 10 application files from MinIO — I'm using 10 for the demo but the full dataset is 566. It parses each JSON, automatically derives the `correct` field using the six-rule table you can see here — this is the trust derivation logic, no manual labelling needed — and registers each session log with the HAIC Suite. Then Step B triggers evaluation and retrieves the metrics."*

**Point to the correct derivation table:**
> *"This table is important — the raw Novoville logs don't have a ground truth label. We derive it from the agreement between AI decision and operator decision. For example: AI says Rejected, operator says Fixed and accepted — that's a correct outcome, meaning the AI was right to flag it."*

**Point to Flow 2 (right):**
> *"Flow 2 is the live path — three HTTP endpoints, one per actor. When Novoville goes live, events will hit these endpoints in real time. For the demo, I use inject nodes to simulate the events."*

**Point to result box:**
> *"These are the expected metric values based on our prior analysis of the dataset."*

> *"Let me switch to the platform now and run this."*

**→ Switch to Node-RED screen**

---

## LIVE DEMO (3–4 min)

### Screen layout
- Left: Node-RED (SC Flow 1 tab visible)
- Right (or browser tab): HAIC dashboard

---

### Part A — Flow 1: Batch Upload

**Show the canvas briefly:**
> *"This is SC Flow 1. Section A at the top processes files from MinIO. Section B triggers evaluation. Section C — the pink node — listens automatically for new files via RabbitMQ. I'll run A and B manually."*

**Click: ▶ Step A — Register all logs**

> *"I'm triggering Step A now. The flow generates a list of 10 file paths, downloads each from MinIO using a presigned URL — because the bucket is private — parses the JSON, derives the correct field, and sends each log to the HAIC API."*

*[Watch debug sidebar — messages should appear]*

> *"You can see the files being processed in the debug panel — APP_000001 through APP_000010. Each one gets a 200 OK from the benchmarking backend."*

**If debug shows messages coming in:**
> *"Ten sessions registered. Let me trigger the evaluation."*

**If debug shows errors / nothing:**
> *(Fallback — show screenshot)* *"Let me show you the output from our test run earlier — all 10 files registered successfully, confirmed by the backend logs showing HTTP 200."* *(Switch to screenshot)*

---

### Part B — Flow 1: Evaluation

**Click: ▶ Step B — Trigger evaluation**

> *"Step B calls POST /evaluate/22 — this tells the HAIC Suite to compute the metrics across all registered logs for configuration 22, which is our Smart Cities application screening configuration."*

*[Wait 2–3 seconds]*

**If results appear in debug:**
> *"And here are the results."*

Point to the metric values:
> *"Trust proxy around 0.67 — that means in roughly two thirds of reviewed cases, the operator's decision agreed with the AI's assessment. Interaction frequency: 3.6 events per minute. Human-centeredness: 0.84 — operators completed reviews well within the configured time threshold."*

**If Step B errors / no results:**
> *(Fallback)* *"The evaluation runs asynchronously on the backend. Let me show you the results from our earlier run."* *(Switch to HAIC dashboard or saved JSON screenshot)*

---

### Part C — Flow 2: Live logging simulation (optional, 60 sec)

*Only if time permits — skip if running long*

**Switch to SC Flow 2 tab**

> *"This is Flow 2 — the real-time path. Three inject nodes simulate the Novoville system sending events. I'll trigger them in sequence."*

**Click inject for citizen → pause → inject for AI → pause → inject for operator**

> *"Citizen submits, AI evaluates, operator decides. Each event hits a dedicated haic-logger node — you can see the green status 'Ready to log' on each one. The operator logger automatically derives the correct field from the AI decision stored in flow context — no extra call needed."*

**If loggers show "Log registered successfully":**
> *"All three logged. In a live scenario this happens continuously as applications flow through Novoville."*

**If loggers show error:**
> *"The environment registration is still being finalised — we have a server-side fix in progress. The architecture is fully wired; the live path will be operational for the pilot's next evaluation round."*

---

### Closing (30 sec)

**Switch back to slides or stay on NR/dashboard**

> *"So what you've seen is a complete end-to-end integration: real pilot data from Novoville in MinIO, orchestrated by Node-RED on Kubeflow, evaluated by the HAIC Benchmarking Suite, and accessible through the Common Frontend."*

> *"The same pattern — environment registration, agent mapping, log ingestion, evaluation trigger — is designed to work for any HumAIne pilot. We have it validated for Smart Cities and it's the reference implementation for Manufacturing and Smart Energy."*

> *"I'll hand over now for the SC pilot results."*

---

## FALLBACK RESOURCES (have these open and ready)

| Situation | Fallback |
|---|---|
| Step A produces no debug output | Screenshot: debug showing APP_000001–APP_000010 + 200 OK backend log |
| Step B errors or no metrics | Screenshot: HAIC dashboard configuration 22 with metrics, OR saved JSON from prior run |
| Flow 2 loggers show env error | Say: "environment fix in progress" — show logger status "Ready to log!" from earlier screenshot |
| MinIO connection fails entirely | Open HAIC dashboard directly → show Configuration 22 → already registered logs → run evaluate from Swagger UI |

---

## TIMING

| Section | Time |
|---|---|
| Slide 1 — Section divider | 0:30 |
| Slide 2 — Platform integration | 1:30 |
| Slide 3 — Demo overview | 1:00 |
| Live: Step A (Flow 1) | 1:30 |
| Live: Step B (Evaluation) | 0:45 |
| Live: Flow 2 simulation | 1:00 *(optional)* |
| Closing | 0:30 |
| **Total** | **~7 min** |

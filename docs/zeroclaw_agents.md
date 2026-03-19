'## **hat an Agent Actually Is**



An AI agent is not a chatbot.



When you type into ChatGPT and get a response, that's a chatbot. You ask, it answers, conversation ends. Nothing happens unless you're there.



An agent is different. You give it a goal, tools to accomplish that goal, and a schedule — and it runs on its own. No one at the keyboard. It wakes up, checks what needs doing, does it, and goes back to sleep. The next morning, you open your dashboard and see what it did.



OpenClaw agents run on a VPS (a small always-on server). Every X minutes (i.e. 30-60 minutes), each agent wakes up, reads its task list, takes whatever action is needed, and reports back. You can have one agent or twenty. They can work independently or pass work between each other.



The shift from chatbot to agent is a shift from reactive to proactive. A chatbot waits for you. An agent works for you.



---



## **What Agents Can Actually Do**



Here are real examples of what OpenClaw agents have done — not hypotheticals.



**Research and outreach:** A user tasked his agent with buying a car. The agent scraped local dealer inventories, filled out contact forms across 8 dealerships, and spent days playing them against each other — all without the owner being involved. Final result: $4,200 below sticker. Owner only showed up to sign.



**Autonomous claim filing:** A user had an insurance claim rejected. Without being asked, his agent found the rejection email, looked up the relevant policy language, drafted a rebuttal, and sent it. The insurer reopened the investigation.



**Complex lead workflows:** One workflow looks like this: new lead fills out a form → agent researches their company → finds their LinkedIn → matches 3 relevant case studies → builds a personalized proposal → sends an email that sounds hand-written → logs everything in CRM → pings Slack with a summary → follows up in 3 days if no reply. End to end. Zero human involvement.



**Content production:** An agent scans GitHub trending, Product Hunt, and Reddit twice daily for emerging AI topics, then writes a report with the top 5 findings. Another agent takes that report and drafts a video script. A third generates thumbnail concepts. All while you're doing other things.



**App development:** A dev agent builds small utilities — Pomodoro timers, prompt managers, thumbnail analyzers — and saves them to a workspace folder. You check in, review what was built, use it or don't.



## **Where Agents Are Most Useful**





**Good fits for your first agent:**



- Daily trend/news scanning in your niche

- First-draft content generation (scripts, emails, reports)

- Research on specific topics and summarizing findings

- Monitoring a list of things (competitors, job postings, product pages, GitHub repos)

- Repetitive file or folder organization



**Not great fits:**



- Anything requiring real-time judgment calls

- Tasks with legal or financial consequences you can't review

- Creative work where your voice and taste are the entire product



---



## **Three Prompts to Set Up Your First Agent**



You don't need to write SOUL.md and AGENTS.md from scratch. Give these prompts to your OpenClaw and it will build the agent for you.



---



**Prompt 1: Build a research/trend agent****Good fits for your first agent:**



- Daily trend/news scanning in your niche

- First-draft content generation (scripts, emails, reports)

- Research on specific topics and summarizing findings

- Monitoring a list of things (competitors, job postings, product pages, GitHub repos)

- Repetitive file or folder organization



**Not great fits:**



- Anything requiring real-time judgment calls

- Tasks with legal or financial consequences you can't review

- Creative work where your voice and taste are the entire product



---



## **Three Prompts to Set Up Your First Agent**



You don't need to write SOUL.md and AGENTS.md from scratch. Give these prompts to your OpenClaw and it will build the agent for you.



---



**Prompt 1: Build a research/trend agent**



Create a new agent called trend-scout. This agent monitors sources for emerging trends in [YOUR NICHE] and produces a short daily report.



Set it up with:



SOUL.md:

- Role: early warning system for emerging topics in [YOUR NICHE]

- Personality: direct, no filler, bullet points only. If nothing interesting happened, say exactly that. Never pad reports.

- Output format: MAX 5 bullet points. Each bullet: topic name, one sentence on why it matters, one data point, urgency tag (NOW / THIS WEEK / WHENEVER)

- Total output must be readable in under 60 seconds



AGENTS.md:

- Tools: web search, Reddit search, GitHub trending

- Schedule: cron at 6am and 6pm daily

- Save output to: ~/.openclaw/agents/trend-scout/workspace/

- File naming: YYYY-MM-DD-AM.md or YYYY-MM-DD-PM.md



Confirm the agent is created and show me the SOUL.md so I can review it.



Prompt 2: Build a content/writing agent



Create a new agent called content-agent. This agent drafts long-form content based on topics and briefs I give it.



Set it up with:



SOUL.md:

- Role: senior content writer for [YOUR NAME/BRAND]

- Personality: [YOUR WRITING VOICE — e.g., "direct, casual, conversational. No corporate language. Short punchy sentences. Active voice. Sounds like a knowledgeable friend, not a consultant."]

- Decision rules: never publish directly. Always save drafts for review. Ask if brief is unclear before writing.

- Output: full drafts in Markdown. Always include a suggested title, word count, and a note on anything that needs a human fact-check.



AGENTS.md:

- Tools: web search (for research and fact-checking), file write

- Trigger: on demand — runs when I give it a topic or brief

- Save output to: ~/.openclaw/agents/content-agent/workspace/

- File naming: YYYY-MM-DD-[topic-slug].md



Confirm the agent is created and show me both config files.



Prompt 3: Build a monitoring/alert agent



Create a new agent called monitor-agent. This agent keeps track of a list of things I care about and alerts me when something changes.



Set it up with:



SOUL.md:

- Role: watchdog. Monitors a list of URLs, topics, and signals for changes or notable events.

- Personality: minimal. When something changes, say what changed and why it matters. Nothing else.

- Decision rules: only alert when there's a genuine change or notable event. Don't alert for minor fluctuations. When uncertain, err on the side of alerting — I'd rather have a false positive than miss something.



AGENTS.md:

- Tools: web search, URL fetch, file read/write

- Monitoring list: [LIST WHAT YOU WANT TO MONITOR — competitor pricing pages, keywords, job postings, a GitHub repo, etc.]

- Schedule: heartbeat every 60 minutes

- Save state to: ~/.openclaw/agents/monitor-agent/state.json (so it knows what it already saw)

- Alert format: one paragraph max. What changed, where, why it might matter.



Confirm the agent is created and ready.



## **How to Give Agents Their Own Personality**



Every agent has a `SOUL.md` file — a plain text file that defines who the agent is. OpenClaw reads it on startup and applies it to every single interaction. It's the most powerful configuration tool you have.



The two rules that matter:



**1. Specific beats vague.** "Be helpful" is useless. "Always respond in bullet points. Never use more than 5 bullets. If the answer needs more than 5 bullets, ask a clarifying question instead of padding" — that's useful. Every line in SOUL.md should describe a specific, observable behavior.



**2. Short beats long.** SOUL.md is loaded into every prompt your agent runs. A 10-page SOUL.md wastes tokens on every single call and dilutes the rules that actually matter. Keep it under 500 words for most agents. Under 2,000 for a complex orchestrator.



> **[CALLOUT: Have your agent improve its own SOUL.md]** After a week of using an agent, ask it: "Based on our conversations this week, suggest 3-5 specific improvements to your SOUL.md that would make you more useful." The agent has seen every case where its instructions were unclear. This is the fastest way to improve behavior over time.

> 



---



## **Building a Multi-Agent Team**



One agent handles one domain. But when you have multiple agents, you need a way for them to work together. That's where team structure and coordination come in.



### **The Orchestrator Pattern**



The most reliable multi-agent pattern is hierarchical: one Orchestrator agent coordinates everything, and specialist agents do the actual work.



Build your orchestrator



I want to set up an Orchestrator agent that connects and manages all of my other agents.



Before creating anything, do the following steps in order:



STEP 1: INVENTORY

Scan ~/.openclaw/agents/ and list every agent you find. For each one, read its SOUL.md and AGENTS.md and extract:

- Agent name

- What it does (one sentence)

- What triggers it (cron, on demand, heartbeat)

- What it outputs and where



Show me this list and wait for my confirmation before continuing.



STEP 2: CREATE SHARED INFRASTRUCTURE

Create the following shared directories and files if they don't already exist:



~/.openclaw/shared/

~/.openclaw/shared/tasks.json        (task queue — array, starts as [])

~/.openclaw/shared/routing-map.json  (maps task types to agent names)

~/.openclaw/shared/digest.md         (daily summary written by the Orchestrator)



STEP 3: BUILD THE ORCHESTRATOR



Create a new agent called orchestrator with the following files:



SOUL.md:

- Role: you are the central coordinator for this agent fleet. Your only job is routing, delegation, and oversight. You do not do the work yourself — you direct the right agent to do it.

- Routing rules: when a task arrives, read routing-map.json, identify which agent owns that task type, and assign it. If no agent clearly owns the task, flag it to the user.

- Delegation format: when assigning a task, write it to tasks.json with these fields: { "id": "[uuid]", "task": "[clear description]", "assigned_to": "[agent-name]", "status": "queued", "created_at": "[timestamp]", "context": "[any relevant info the agent needs]" }

- Daily digest: once per day, read all agent workspace folders, summarize what was produced, what's pending, what needs attention, and write a short plain-english summary to ~/.openclaw/shared/digest.md

- Decision escalation: if any agent marks a task as "needs_approval", surface it to the user immediately with a one-sentence explanation of what's being asked and why

- Do not repeat yourself. Check tasks.json before assigning — if a task is already queued or in progress, do not queue it again.

- Use the cheapest available model. You are a router, not a thinker.



AGENTS.md:

- Startup instructions: read tasks.json, check for any "queued" items that haven't been picked up, ping the assigned agent if it hasn't started within 2x its normal run interval

- Tools: file read/write, sessions_send (to message agents directly), sessions_spawn (to trigger agents on demand)

- Schedule: heartbeat every 30 minutes

- On each run:

  1. Check tasks.json for queued items

  2. Check all agent workspace folders for new outputs since last run

  3. Update digest.md with a one-line entry for anything new

  4. Flag anything marked needs_approval

- Output: write a brief run log to ~/.openclaw/agents/orchestrator/workspace/[YYYY-MM-DD]-run-log.md



STEP 4: BUILD THE ROUTING MAP

Based on the agents you inventoried in Step 1, populate routing-map.json with entries like:

{ "task_type": "[description of what kinds of tasks this covers]", "assigned_to": "[agent-name]", "trigger": "on_demand | cron | heartbeat" }



Cover every agent you found. If two agents could handle the same task type, add a note in a "notes" field explaining which takes priority and when.



Show me the routing map before writing it to disk. Wait for my approval.



STEP 5: UPDATE EXISTING AGENTS (OPTIONAL)

For each specialist agent, add the following lines to their AGENTS.md startup instructions if not already present:

- On startup, check ~/.openclaw/shared/tasks.json for any tasks assigned to [agent-name] with status "queued"

- When starting a task, update its status to "in_progress"

- When complete, update its status to "done" and write output to workspace as usual

- If the task requires user approval before proceeding, update status to "needs_approval" and stop



Ask me before modifying any existing agent files.



STEP 6: CONFIRM

After everything is built, give me:

1. A summary of all agents now connected to the Orchestrator

2. The routing map

3. Instructions for how to send a task to the Orchestrator (the exact message format)

4. Instructions for how to trigger the Orchestrator manually if I don't want to wait for the heartbeat



### **Two ways agents pass work to each other**



**1. File-based handoff** — one agent writes its output to a shared folder, another agent reads from it. Simple, reliable, and easy to inspect. The research agent writes a trend report to `workspace/`. The content agent reads from that same folder when drafting a script.



**2. Direct messaging** — using OpenClaw's `sessions_send` or `sessions_spawn`, agents can send tasks directly to other agents and receive results. More complex, but enables real-time coordination.



For most setups, file-based handoff is the right starting point. It's simpler to debug — you can always open the file and see exactly what was passed.



### **Design rules for agent teams**



> **[CALLOUT: Fewer than 10% of teams successfully scale beyond a single agent]** The main reasons: overlapping domains, uncontrolled token costs, and coordination complexity. Most of these problems are caused by not defining clearly enough what each agent owns.

> 



**1. Define non-overlapping domains.** Every agent should have exactly one job. If two agents could both handle a task, you have an overlap problem — they'll produce duplicated or conflicting outputs. Write down what each agent "owns," not just what it can do.



**2. Use append-only files for shared logs.** When multiple agents write to the same file, overwriting causes data loss. Always append, never overwrite. If an agent needs to update state, use a JSON file with idempotent writes — writing the same value twice should produce the same result as writing it once.



**3. Start with two agents, add one per week.** Get your Orchestrator and one specialist working reliably before adding anything else. Each new agent should be stable before the next one joins. Rushing to a 20-agent fleet before the first two are dialed in is how you end up with a chaotic system that's impossible to debug.



**4. The Orchestrator should use a cheap model.** It's just routing. You don't need Claude Opus to decide whether a task should go to the content agent or the research agent. Use the fastest, cheapest model that can make a consistent yes/no decision.





A 3-agent team — Orchestrator + Content + Research — already gets you most of the value. Add teams as your workload grows and you have a clear domain for the new agent to own.



## **Prompt to Build Your Entire Team at Once**



If you want to set up a multi-agent team in one go, give OpenClaw this prompt and it will scaffold the whole structure for you:



I want to build a team of [NUMBER] AI agents to help me with [YOUR MAIN GOAL — e.g., "running my content business / managing research / building software projects"].



For each agent, create:

- A workspace directory at ~/.openclaw/agents/[agent-name]/

- A SOUL.md with a specific role, personality, and output rules

- An AGENTS.md with startup instructions, tools, schedule, and output format

- Registration with my gateway



Here are the agents I want:



Agent 1: [Name] — [one sentence: what it does]

Agent 2: [Name] — [one sentence: what it does]

Agent 3: [Name] — [one sentence: what it does]

(add as many as you need)



For the first agent in the list, make it the Orchestrator. It should:

- Route incoming tasks to the right specialist

- Keep a shared task queue at ~/.openclaw/shared/tasks.json

- Run on the cheapest available model



For all other agents:

- They read from the shared task queue for their domain

- They save all outputs to their own workspace folder

- They run on a model appropriate to their task type (cheap for routine, capable for complex)



Build them one at a time, confirm each one, then move to the next.


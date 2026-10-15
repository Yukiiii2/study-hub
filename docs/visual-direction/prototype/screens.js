const icon = (name, label = "") => `<svg class="icon" ${label ? `aria-label="${label}" role="img"` : "aria-hidden=\"true\""}><use href="#i-${name}"></use></svg>`;

const subjects = [
  ["FAR", "Financial Accounting", "far"],
  ["AFAR", "Advanced Financial Accounting", "afar"],
  ["MAS", "Management Advisory Services", "mas"],
  ["TAX", "Taxation", "tax"],
  ["RFBT", "Regulatory Framework", "rfbt"],
  ["AT", "Auditing Theory", "at"],
  ["AP", "Auditing Practice", "ap"],
];

function brand(compact = false) {
  return `<div class="brand ${compact ? "brand-compact" : ""}"><span class="brand-mark"><i></i><i></i><i></i></span><span><strong>Study Hub</strong>${compact ? "" : "<small>CPALE review workspace</small>"}</span></div>`;
}

function desktopNav(active) {
  const items = [
    ["today", "Today", "today"], ["plan", "Plan", "plan"],
    ["subjects", "Subjects", "study"], ["library", "Library", "study"], ["assistant", "Assistant", "study"],
    ["recall", "Recall", "practice"], ["quizzes", "Quizzes", "practice"], ["assessments", "Assessments", "practice"],
    ["analytics", "Analytics", "progress"],
  ];
  const groups = [["Your day", items.slice(0,2)], ["Study", items.slice(2,5)], ["Practice", items.slice(5,8)], ["Progress", items.slice(8)]];
  return `<aside class="sidebar">${brand()}<nav>${groups.map(([label, links]) => `<section><p>${label}</p>${links.map(([key,text,ic]) => `<a class="${active===key?"active":""}" href="#">${icon(ic)}<span>${text}</span></a>`).join("")}</section>`).join("")}</nav><a class="focus-entry ${active==="focus"?"active":""}" href="#">${icon("focus")}<span><b>Focus</b><small>Start a study session</small></span></a><div class="account"><span>EA</span><div><b>Emmanuel</b><small>Account & settings</small></div>${icon("chevron")}</div></aside>`;
}

function utility(title = "Today") {
  return `<header class="utility"><div class="crumb">${title}</div><div class="utility-actions"><button class="quiet">${icon("clock")} <span>Thu, Oct 15</span></button><button class="avatar" aria-label="Open account menu">EA</button></div></header>`;
}

function desktopShell(active, title, content, extra = "") {
  return `<div class="app desktop-shell ${extra}">${desktopNav(active)}<div class="app-main">${utility(title)}${content}<div class="prototype-note">Visual prototype · illustrative content</div></div></div>`;
}

function mobileHeader(title) {
  return `<header class="mobile-header">${brand(true)}<span class="mobile-title">${title}</span><button class="icon-button" aria-label="Open menu">${icon("menu")}</button></header>`;
}

function mobileNav(active) {
  const links = [["today","Today","today"],["plan","Plan","plan"],["focus","Focus","focus"],["study","Study","study"],["more","More","more"]];
  return `<nav class="mobile-nav" aria-label="Primary">${links.map(([key,text,ic]) => `<a class="${key===active?"active":""} ${key==="focus"?"nav-focus":""}" href="#" ${key===active?'aria-current="page"':""}>${icon(ic)}<span>${text}</span></a>`).join("")}</nav>`;
}

function tabletRail() {
  const links = [["Today","today"],["Plan","plan"],["Focus","focus"],["Study","study"],["More","more"]];
  return `<aside class="tablet-rail" aria-label="Workspace navigation"><span class="brand-mark" aria-label="Study Hub"><i></i><i></i><i></i></span><nav>${links.map(([label,name]) => `<a href="#" class="${name === "today" ? "active" : ""} ${name === "focus" ? "rail-focus" : ""}" ${name === "today" ? 'aria-current="page"' : ""}>${icon(name)}<span>${label}</span></a>`).join("")}</nav><button class="avatar" aria-label="Account and settings">EA</button></aside>`;
}

function subjectDot(code, cls) {
  return `<span class="subject-dot ${cls}"></span><b>${code}</b>`;
}

function dashboardMain(size = "desktop") {
  const mobile = size === "mobile";
  return `<main class="page dashboard-page ${size}">
    <header class="page-heading"><div><h1>${mobile ? "Good morning" : "Good morning, Emmanuel"}</h1><p>${mobile ? "Thursday, October 15" : "Settle in. Your next study block is ready."}</p></div>${mobile ? "" : `<button class="button secondary">View full plan ${icon("arrow")}</button>`}</header>
    <section class="study-docket">
      <div class="docket-label"><span class="live-dot"></span>Now / Next</div>
      <div class="docket-main">
        <div class="docket-time"><strong>9:30</strong><span>AM</span><i></i><small>60 min</small></div>
        <div class="docket-copy"><div class="subject-line">${subjectDot("FAR","far")}<span>Lecture</span></div><h2>Revenue recognition: performance obligations</h2><p>Continue the planned block from today's schedule.</p></div>
        <button class="button primary">${icon("focus")} Start Focus</button>
      </div>
      <div class="docket-next"><span>After this</span><b>11:00 AM · Recall review</b><small>8 cards due</small></div>
    </section>
    <div class="dashboard-columns">
      <section class="section-block schedule-block"><div class="section-heading"><div><h2>Today</h2><p>Three planned blocks · 2h 45m</p></div><a href="#">Open plan ${icon("arrow")}</a></div>
        <div class="agenda">
          <div class="agenda-row current"><time>9:30</time><span class="timeline-dot far"></span><div><b>Revenue recognition</b><small>FAR · Lecture · 60 min</small></div><span class="status active-status">Next</span></div>
          <div class="agenda-row"><time>11:00</time><span class="timeline-dot tax"></span><div><b>Recall review</b><small>TAX · Recall · 30 min</small></div><span class="status">Planned</span></div>
          <div class="agenda-row"><time>2:00</time><span class="timeline-dot mas"></span><div><b>Cost-volume-profit drill</b><small>MAS · Practice · 75 min</small></div><span class="status">Planned</span></div>
        </div>
      </section>
      <section class="section-block attention-block"><div class="section-heading"><div><h2>Needs attention</h2><p>Time-sensitive study work</p></div></div>
        <div class="attention-list">
          <a href="#"><span class="attention-icon gold">8</span><div><b>Recall cards are due</b><small>3 overdue · 5 due today</small></div>${icon("chevron")}</a>
          <a href="#"><span class="attention-icon red">2</span><div><b>Tasks past their date</b><small>Review and reschedule</small></div>${icon("chevron")}</a>
          <a href="#"><span class="attention-icon blue">17d</span><div><b>Pre-board assessment</b><small>42 topics in coverage</small></div>${icon("chevron")}</a>
        </div>
      </section>
    </div>
    <section class="continue-strip"><div class="continue-icon">${icon("play")}</div><div><span>Continue studying</span><b>FAR 07 · Revenue recognition</b><small>Lecture 3 of 6 · 38 minutes remaining</small></div><div class="strip-progress"><i style="width:58%"></i></div><button class="button secondary">Continue</button></section>
    <div class="progress-layout">
      <section class="section-block progress-section"><div class="section-heading"><div><h2>Progress at a glance</h2><p>Real activity across your study tools</p></div><a href="#">Analytics ${icon("arrow")}</a></div>
        <div class="summary-rail"><div><span>Study this week</span><strong>11h 40m</strong><small>across 9 sessions</small></div><div><span>Lectures complete</span><strong>184 / 312</strong><small>59% of library</small></div><div><span>Recall queue</span><strong>8 due</strong><small>3 already overdue</small></div></div>
        <div class="week-chart" aria-label="Study time by day"><div><i style="height:35%"></i><span>F</span></div><div><i style="height:62%"></i><span>S</span></div><div><i style="height:18%"></i><span>S</span></div><div><i style="height:74%"></i><span>M</span></div><div><i style="height:48%"></i><span>T</span></div><div><i style="height:88%"></i><span>W</span></div><div class="today-bar"><i style="height:54%"></i><span>T</span></div></div>
      </section>
      <section class="section-block subjects-section"><div class="section-heading"><div><h2>Subjects</h2><p>Curriculum standing</p></div><a href="#">All subjects</a></div>
        <div class="subject-rows">${subjects.map(([code,name,cls],i)=>`<a href="#"><span>${subjectDot(code,cls)}</span><div><i style="width:${[62,48,57,41,36,52,44][i]}%"></i></div><small>${[62,48,57,41,36,52,44][i]}%</small></a>`).join("")}</div>
      </section>
    </div>
  </main>`;
}

function dashboardDesktop() { return desktopShell("today", "Today", dashboardMain("desktop")); }

function dashboardTablet() {
  return `<div class="app tablet-shell">${tabletRail()}${mobileHeader("Today")}<div class="tablet-context"><span>Thursday, October 15</span><button class="button secondary">Plan ${icon("arrow")}</button></div>${dashboardMain("tablet")}${mobileNav("today")}<div class="prototype-note">Visual prototype · illustrative content</div></div>`;
}

function dashboardMobile() {
  return `<div class="app mobile-shell">${mobileHeader("Today")}${dashboardMain("mobile")}${mobileNav("today")}<div class="prototype-note">Prototype</div></div>`;
}

function focusContent(mobile = false) {
  return `<main class="page focus-page ${mobile ? "focus-mobile" : ""}">
    ${mobile ? "" : `<header class="focus-heading"><div><h1>Focus</h1><p>One session. One clear objective.</p></div><span class="session-live"><i></i> Session active</span></header>`}
    <section class="focus-stage">
      <div class="focus-context"><span>${subjectDot("FAR","far")}</span><b>Revenue recognition</b><small>Lecture</small></div>
      <div class="timer" aria-label="Elapsed time 38 minutes 14 seconds">38<span>:</span>14</div>
      <p class="started">Started at 9:30 AM · elapsed time</p>
      <div class="focus-objective"><span>Session objective</span><b>Finish Lecture 3 and note uncertain areas.</b></div>
      <button class="button finish">${icon("check")} Finish session</button>
      <small class="finish-note">Final duration is recorded by Study Hub when you finish.</small>
    </section>
    <section class="focus-lower">
      <div class="today-total"><span>Today</span><strong>1h 24m</strong><small>2 completed sessions</small></div>
      <div class="session-ledger"><div class="section-heading"><div><h2>Today's sessions</h2><p>Actual study time</p></div></div><div class="session-row"><span class="timeline-dot mas"></span><div><b>Cost-volume-profit drill</b><small>MAS · Practice · 8:10–8:56 AM</small></div><strong>46m</strong></div><div class="session-row active-row"><span class="timeline-dot far"></span><div><b>Revenue recognition</b><small>FAR · Lecture · in progress</small></div><strong>38m</strong></div></div>
    </section>
  </main>`;
}

function focusDesktop() { return desktopShell("focus", "Focus", focusContent(false), "focus-shell"); }
function focusMobile() { return `<div class="app mobile-shell focus-mobile-shell">${mobileHeader("Focus")}${focusContent(true)}${mobileNav("focus")}<div class="prototype-note">Prototype</div></div>`; }

function analyticsDesktop() {
  const subjectBars = [["FAR","far",78,"5h 18m"],["MAS","mas",54,"3h 41m"],["TAX","tax",37,"2h 32m"],["AFAR","afar",28,"1h 55m"]];
  return desktopShell("analytics", "Analytics", `<main class="page analytics-page">
    <header class="page-heading"><div><h1>Study analytics</h1><p>Understand where your time went and how your study rhythm is changing.</p></div><div class="segment"><button class="active">7 days</button><button>30 days</button><button>90 days</button></div></header>
    <section class="analytics-summary"><div><span>Total study time</span><strong>14h 12m</strong><small>9 sessions</small></div><div><span>Active days</span><strong>6 of 7</strong><small>this period</small></div><div><span>Average session</span><strong>1h 35m</strong><small>longest 2h 10m</small></div><div><span>Planned / actual</span><strong>16h / 14h</strong><small>transparent totals</small></div></section>
    <section class="report-section activity-report"><div class="section-heading"><div><h2>Study activity</h2><p>Actual duration recorded by Focus and study sessions</p></div><span class="metric-note">14h 12m total</span></div><div class="line-chart"><div class="chart-y"><span>3h</span><span>2h</span><span>1h</span><span>0</span></div><svg viewBox="0 0 800 180" preserveAspectRatio="none" aria-label="Daily study activity"><path class="grid-line" d="M0 20H800M0 72H800M0 124H800M0 176H800"/><path class="area" d="M0 154 L130 94 L260 132 L390 48 L520 112 L650 28 L800 78 L800 180 L0 180 Z"/><path class="trend" d="M0 154 L130 94 L260 132 L390 48 L520 112 L650 28 L800 78"/><g class="points"><circle cx="0" cy="154" r="4"/><circle cx="130" cy="94" r="4"/><circle cx="260" cy="132" r="4"/><circle cx="390" cy="48" r="4"/><circle cx="520" cy="112" r="4"/><circle cx="650" cy="28" r="4"/><circle cx="800" cy="78" r="4"/></g></svg><div class="chart-x"><span>Fri</span><span>Sat</span><span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span></div></div></section>
    <div class="analytics-grid"><section class="report-section"><div class="section-heading"><div><h2>Where time went</h2><p>Actual time by subject</p></div></div><div class="bar-list">${subjectBars.map(([code,cls,width,time])=>`<div><span>${subjectDot(code,cls)}</span><div><i class="${cls}" style="width:${width}%"></i></div><strong>${time}</strong></div>`).join("")}</div></section><section class="report-section"><div class="section-heading"><div><h2>Activity mix</h2><p>Time by study activity</p></div></div><div class="activity-stack"><div><i class="lecture" style="width:42%"></i><i class="practice" style="width:28%"></i><i class="recall" style="width:18%"></i><i class="reading" style="width:12%"></i></div><ul><li><span class="blue"></span>Lecture <b>5h 58m</b></li><li><span class="sage"></span>Practice <b>3h 59m</b></li><li><span class="gold"></span>Recall <b>2h 33m</b></li><li><span class="muted-dot"></span>Reading <b>1h 42m</b></li></ul></div></section></div>
    <div class="analytics-grid lower"><section class="report-section"><div class="section-heading"><div><h2>Planned vs actual</h2><p>Study Plan compared with completed sessions</p></div></div><div class="compare-list"><div class="far"><span>FAR</span><div><i style="width:80%"></i><em style="width:66%"></em></div><small>4h planned · 3h 18m actual</small></div><div class="mas"><span>MAS</span><div><i style="width:68%"></i><em style="width:61%"></em></div><small>3h 30m planned · 3h 4m actual</small></div><div class="tax"><span>TAX</span><div><i style="width:48%"></i><em style="width:44%"></em></div><small>2h 30m planned · 2h 12m actual</small></div></div></section><section class="report-section session-history"><div class="section-heading"><div><h2>Recent sessions</h2><p>Recorded study activity</p></div><a href="#">View all</a></div><div class="session-row"><span class="timeline-dot far"></span><div><b>Revenue recognition</b><small>Today · 9:30–10:28 AM · Lecture</small></div><strong>58m</strong></div><div class="session-row"><span class="timeline-dot mas"></span><div><b>CVP drill</b><small>Today · 8:10–8:56 AM · Practice</small></div><strong>46m</strong></div></section></div>
  </main>`);
}

function subjectDesktop() {
  return desktopShell("subjects", "Subjects / FAR", `<main class="page subject-page">
    <header class="subject-hero"><div class="subject-monogram far">FAR</div><div><div class="subject-title"><span>Financial Accounting and Reporting</span><small>46 curriculum topics</small></div><h1>Build fluency through the full FAR syllabus.</h1><p>Continue the current lecture, work through topic-level practice, or begin a focused session.</p></div><div class="subject-actions"><button class="button primary">${icon("focus")} Start Focus</button><button class="button secondary">Open Assistant</button></div></header>
    <section class="subject-progress"><div><span>Curriculum topics</span><strong>29 / 46</strong><div class="linear"><i class="far" style="width:63%"></i></div></div><div><span>Lectures complete</span><strong>38 / 64</strong><div class="linear"><i class="far" style="width:59%"></i></div></div><div><span>Recall due</span><strong>3 cards</strong><small>1 overdue</small></div><div><span>Quiz average</span><strong>78%</strong><small>4 submitted attempts</small></div></section>
    <section class="continue-strip subject-continue"><div class="continue-icon far">${icon("play")}</div><div><span>Continue lecture</span><b>Revenue recognition · Lecture 3</b><small>38 minutes remaining · FAR-07</small></div><div class="strip-progress"><i class="far" style="width:58%"></i></div><button class="button secondary">Resume</button></section>
    <div class="workspace-tabs"><button class="active">Curriculum</button><button>Lectures</button><button>Practice</button><button>Resources</button></div>
    <div class="subject-workspace"><section class="curriculum"><div class="section-heading"><div><h2>Curriculum</h2><p>Work from foundations to application</p></div><div class="compact-actions"><button class="icon-button">${icon("more","More curriculum actions")}</button></div></div>
      <div class="curriculum-group"><button class="group-heading"><span><i class="subject-dot far"></i><b>Foundations and reporting</b><small>8 topics · 6 complete</small></span>${icon("chevron")}</button><div class="topic-row complete"><span>${icon("check")}</span><div><b>Conceptual framework</b><small>FAR-02 · 4 lectures</small></div><em>Complete</em><button>Review</button></div><div class="topic-row complete"><span>${icon("check")}</span><div><b>Accounting process</b><small>FAR-44 · 6 lectures</small></div><em>Complete</em><button>Review</button></div><div class="topic-row current"><span>07</span><div><b>Revenue recognition</b><small>FAR-07 · 3 of 6 lectures</small></div><div class="mini-progress"><i style="width:50%"></i></div><button>Continue</button></div></div>
      <div class="curriculum-group collapsed"><button class="group-heading"><span><i class="subject-dot far"></i><b>Assets</b><small>14 topics · 8 complete</small></span>${icon("chevron")}</button></div><div class="curriculum-group collapsed"><button class="group-heading"><span><i class="subject-dot far"></i><b>Liabilities and equity</b><small>12 topics · 7 complete</small></span>${icon("chevron")}</button></div>
    </section><aside class="workspace-rail"><section><h2>Study tools</h2><a href="#">${icon("practice")}<span><b>Practice this subject</b><small>Question bank and quizzes</small></span>${icon("chevron")}</a><a href="#">${icon("today")}<span><b>Review recall queue</b><small>3 FAR cards due</small></span>${icon("chevron")}</a><a href="#">${icon("study")}<span><b>Open resources</b><small>12 files linked to FAR</small></span>${icon("chevron")}</a></section><section class="next-milestone"><span>Next milestone</span><b>Finish Revenue Recognition</b><p>Three lectures and one topic quiz remain.</p><div class="linear"><i class="far" style="width:58%"></i></div></section></aside></div>
  </main>`);
}

function designSystem() {
  return `<div class="app reference-shell"><header class="reference-header">${brand(true)}<span>Visual implementation reference · illustrative states only</span></header><main class="reference-page">
    <header class="page-heading"><div><h1>Design System</h1><p>Neutral structure. Teal actions. Distinct subject identity.</p></div><span class="reference-version">Approval reference</span></header>
    <div class="reference-grid">
      <section class="reference-section"><h2>Buttons & interaction</h2><p>44px targets. One primary action per context.</p><div class="reference-actions"><button class="button primary">Start Focus</button><button class="button secondary">Edit plan</button><button class="button ghost">View details</button><button class="button destructive">${icon("alert")} Delete resource</button><button class="button secondary" disabled>Unavailable</button><button class="button primary" aria-busy="true"><span class="spinner" aria-hidden="true"></span>Saving…</button></div><div class="interaction-samples"><button class="button secondary preview-hover">Hover</button><button class="button secondary preview-focus">Keyboard focus</button></div><small>Disabled controls keep readable labels and cannot be activated.</small></section>
      <section class="reference-section"><h2>Inputs</h2><div class="reference-form"><label for="ref-title">Session title</label><input id="ref-title" value="Revenue recognition" /><label for="ref-subject">Subject</label><select id="ref-subject">${subjects.map(([code,name])=>`<option>${code} · ${name}</option>`).join("")}</select><label for="ref-search">Search resources</label><input id="ref-search" type="search" placeholder="Search by title or filename" /><label for="ref-notes">Objective <span>optional</span></label><textarea id="ref-notes" rows="2">Finish the lecture and note uncertain areas.</textarea><div class="choice-row"><label><input type="checkbox" checked />Include completed</label><label><input type="radio" name="ref-range" checked />This week</label></div></div></section>
      <section class="reference-section"><h2>Navigation & selection</h2><div class="reference-tabs" role="tablist" aria-label="Example workspace tabs"><button role="tab" aria-selected="true">Curriculum</button><button role="tab" aria-selected="false">Lectures</button><button role="tab" aria-selected="false">Resources</button></div><div class="reference-segment" role="group" aria-label="Example calendar view"><button aria-pressed="true">Month</button><button aria-pressed="false">Week</button></div><p>Selected states combine a surface or rule with text and ARIA state.</p><h3>Subject identity</h3><div class="reference-subjects">${subjects.map(([code,,cls])=>`<span class="subject-chip ${cls}">${subjectDot(code,cls)}</span>`).join("")}</div><div class="reference-progress"><label for="ref-progress">FAR lectures <strong>38 / 64</strong></label><progress id="ref-progress" value="38" max="64">38 of 64</progress></div></section>
      <section class="reference-section"><h2>Feedback</h2><div class="reference-badges"><span class="reference-badge success">${icon("check")} Completed</span><span class="reference-badge warning">Due today</span><span class="reference-badge error">Overdue</span><span class="reference-badge info">Lecture</span></div><div class="reference-notice success">${icon("check")}<div><b>Session recorded</b><span>Your actual study time is saved.</span></div></div><div class="reference-notice warning">${icon("clock")}<div><b>Review due</b><span>Choose a card when you are ready.</span></div></div><div class="reference-notice error">${icon("alert")}<div><b>Upload failed</b><span>Choose a valid PDF or CSV file.</span></div></div><div class="reference-notice info">${icon("study")}<div><b>Private resource</b><span>Only your account can access this file.</span></div></div></section>
      <section class="reference-section"><h2>Loading, empty & retry</h2><div class="reference-state"><span class="state-label">Loading study plan</span><div class="skeleton-row" aria-hidden="true"><i></i><div><i></i><i></i></div></div></div><div class="reference-state"><b>No events today</b><p>Add a study block when you know what to work on.</p><button class="button secondary">Open Study Plan</button></div><div class="reference-state"><label for="ref-invalid">Title</label><input id="ref-invalid" aria-invalid="true" aria-describedby="ref-error" value="" /><p id="ref-error" class="inline-error">${icon("alert")} Enter a title before saving.</p></div><div class="reference-retry"><span>We couldn’t load your tasks.</span><button class="button secondary">Retry</button></div></section>
      <section class="reference-section"><h2>Dialog & mobile sheet</h2><p>Static anatomy examples; no modal is open.</p><section class="dialog-sample" aria-labelledby="ref-dialog-title"><header><h3 id="ref-dialog-title">Finish study session?</h3><button class="icon-button close-example" aria-label="Close dialog example">×</button></header><p>The session duration is recorded when you finish.</p><footer><button class="button ghost">Keep studying</button><button class="button primary">Finish</button></footer></section><section class="sheet-sample" aria-labelledby="ref-sheet-title"><div class="sheet-handle" aria-hidden="true"></div><header><h3 id="ref-sheet-title">Add study event</h3><button class="icon-button close-example" aria-label="Close sheet example">×</button></header><p>Labeled controls, contained scrolling, and a clear close action.</p><button class="button primary">Save event</button></section><small>Implementation: trap focus in active overlays, Escape closes, restore focus to the trigger; respect device safe areas.</small></section>
      <section class="reference-section reference-content"><h2>Content rows</h2><div class="reference-table-wrap"><table><caption>Lecture list example</caption><thead><tr><th scope="col">Subject / lecture</th><th scope="col">Duration</th><th scope="col">Status</th></tr></thead><tbody><tr><td><span class="subject-dot far"></span> FAR · Revenue recognition</td><td>38 min</td><td>In progress</td></tr><tr><td><span class="subject-dot mas"></span> MAS · CVP drill</td><td>46 min</td><td>Completed</td></tr></tbody></table></div><p>Text labels communicate status; subject color provides a consistent secondary cue.</p></section>
    </div>
  </main></div>`;
}

const screens = {"dashboard-desktop":dashboardDesktop,"dashboard-tablet":dashboardTablet,"dashboard-mobile":dashboardMobile,"focus-desktop":focusDesktop,"focus-mobile":focusMobile,"analytics-desktop":analyticsDesktop,"subject-desktop":subjectDesktop,"design-system":designSystem};
const params = new URLSearchParams(location.search);
const view = params.get("view") || "dashboard-desktop";
const artboardWidth = Number.parseInt(params.get("width") || "", 10);
const artboardHeight = Number.parseInt(params.get("height") || "", 10);
if (Number.isFinite(artboardWidth)) document.documentElement.style.setProperty("--artboard-width", `${artboardWidth}px`);
if (Number.isFinite(artboardHeight)) document.documentElement.style.setProperty("--artboard-height", `${artboardHeight}px`);
document.documentElement.dataset.view = view;
document.querySelector("#screen-root").innerHTML = (screens[view] || dashboardDesktop)();
if (view === "design-system") {
  const tabs = [...document.querySelectorAll('.reference-tabs [role="tab"]')];
  const panel = document.createElement("p");
  panel.id = "ref-tab-panel";
  panel.setAttribute("role", "tabpanel");
  panel.tabIndex = 0;
  const selectTab = (index, focus = false) => {
    tabs.forEach((tab, i) => {
      tab.id = `ref-tab-${i}`;
      tab.setAttribute("aria-controls", panel.id);
      tab.setAttribute("aria-selected", String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
    });
    panel.setAttribute("aria-labelledby", tabs[index].id);
    panel.textContent = `${tabs[index].textContent} selected · visual interaction example`;
    if (focus) tabs[index].focus();
  };
  tabs[0].parentElement.after(panel);
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectTab(index));
    tab.addEventListener("keydown", event => {
      const next = event.key === "ArrowRight" ? (index + 1) % tabs.length : event.key === "ArrowLeft" ? (index + tabs.length - 1) % tabs.length : event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : null;
      if (next !== null) { event.preventDefault(); selectTab(next, true); }
    });
  });
  selectTab(0);
  document.querySelectorAll('.reference-segment button').forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll('.reference-segment button').forEach(item => item.setAttribute("aria-pressed", String(item === button)));
  }));
}
if (params.get("scroll") === "bottom") {
  requestAnimationFrame(() => {
    const scroller = document.querySelector(".tablet-shell > .page, .mobile-shell > .page, .app-main, .reference-page");
    if (scroller) scroller.scrollTop = scroller.scrollHeight;
  });
}

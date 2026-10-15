/* Isolated prototype renderer. Uses the installed Edge and Node; no app dependencies. */
const fs = require("node:fs/promises");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { pathToFileURL } = require("node:url");

const artifactRoot = path.resolve(__dirname, "..");
const profile = path.join(artifactRoot, `.browser-profile-${process.pid}`);
if (!profile.startsWith(artifactRoot + path.sep)) throw new Error("Invalid browser profile path");
const output = path.join(artifactRoot, "renders");
const edge = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const cases = [
  ...["dashboard-desktop", "focus-desktop", "analytics-desktop", "subject-desktop"].flatMap(view =>
    [[1440,900], [1366,768], [1024,768]].map(([width,height], i) => ({view,width,height,name:i ? `${view}-${width}` : view}))),
  ...[[768,1024],[820,1180],[1024,768]].map(([width,height],i) => ({view:"dashboard-tablet",width,height,name:i ? `dashboard-tablet-${width}` : "dashboard-tablet"})),
  ...["dashboard-mobile","focus-mobile"].flatMap(view => [[390,844],[430,932]].map(([width,height],i) => ({view,width,height,name:i ? `${view}-${width}` : view}))),
  ...[[1440,900],[1024,768],[768,1024],[390,844]].map(([width,height],i) => ({view:"design-system",width,height,name:i ? `design-system-${width}` : "design-system"})),
];
const delay = ms => new Promise(resolve => setTimeout(resolve,ms));

async function run() {
  await fs.mkdir(output,{recursive:true});
  const browser = spawn(edge,["--headless=new","--disable-gpu","--no-first-run","--hide-scrollbars","--remote-debugging-port=0",`--user-data-dir=${profile}`,"about:blank"],{windowsHide:true,stdio:"ignore"});
  let ws;
  try {
    let port;
    for (let i=0;i<100;i++) {
      try { port=Number((await fs.readFile(path.join(profile,"DevToolsActivePort"),"utf8")).split("\n")[0]); break; } catch { await delay(100); }
    }
    if (!port) throw new Error("Edge did not open its debugging connection");
    const info = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
    ws = new WebSocket(info.webSocketDebuggerUrl);
    await new Promise((resolve,reject) => { ws.addEventListener("open",resolve,{once:true}); ws.addEventListener("error",reject,{once:true}); });
    let id=0;
    const pending=new Map();
    ws.addEventListener("message",event=>{
      const message=JSON.parse(event.data);
      if (message.id && pending.has(message.id)) {
        const task=pending.get(message.id); pending.delete(message.id);
        message.error ? task.reject(new Error(message.error.message)) : task.resolve(message.result);
      }
    });
    const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
      const request={id:++id,method,params}; if(sessionId) request.sessionId=sessionId;
      pending.set(id,{resolve,reject}); ws.send(JSON.stringify(request));
    });
    const {targetId}=await send("Target.createTarget",{url:"about:blank"});
    const {sessionId}=await send("Target.attachToTarget",{targetId,flatten:true});
    const call=(method,params)=>send(method,params,sessionId);
    const evaluate=async expression=>{
      const result=await call("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
      if(result.exceptionDetails) throw new Error(result.exceptionDetails.text);
      return result.result.value;
    };
    await call("Page.enable");
    const results=[];
    for(const item of cases) {
      await call("Emulation.setDeviceMetricsOverride",{width:item.width,height:item.height,deviceScaleFactor:1,mobile:false});
      const url=pathToFileURL(path.join(__dirname,"screen.html"));
      url.search=new URLSearchParams({view:item.view,width:item.width,height:item.height});
      await call("Page.navigate",{url:url.href});
      for(let i=0;i<100;i++) {
        if(await evaluate(`document.readyState === 'complete' && document.querySelector('.app') !== null`)) break;
        await delay(30);
      }
      await evaluate(`new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))`);
      const initial=await evaluate(`(() => {
        const navElement=document.querySelector('.mobile-nav');
        const nav=navElement?.getClientRects().length ? navElement : null;
        const railElement=document.querySelector('.tablet-rail');
        const rail=railElement?.getClientRects().length ? railElement : null;
        const scroller=document.querySelector('.mobile-shell > .page, .tablet-shell > .page');
        const overflow=[...document.querySelectorAll('.app *')].filter(el=>{
          if(el.closest('svg') || !el.getClientRects().length) return false;
          const r=el.getBoundingClientRect(); return r.width > 0 && (r.right > innerWidth+1 || r.left < -1);
        }).map(el=>el.className).slice(0,12);
        const smallText=[...document.querySelectorAll('.page small,.page p,.page time')].filter(el=>el.getClientRects().length && parseFloat(getComputedStyle(el).fontSize)<11).map(el=>el.className || el.tagName);
        const clippedControls=[...document.querySelectorAll('.app button')].filter(el=>el.getClientRects().length && el.scrollWidth>el.clientWidth+1).map(el=>el.textContent.trim());
        return {horizontalOverflow:overflow,clippedControls,smallText,navMode:rail?'rail':nav?'bottom':'sidebar or reference',navSafe:!nav || scroller.getBoundingClientRect().bottom <= nav.getBoundingClientRect().top+1,navTargets:(!nav || [...nav.children].every(el=>el.getBoundingClientRect().height>=44)) && (!rail || [...rail.querySelectorAll('a,button')].every(el=>el.getBoundingClientRect().height>=44)),railSafe:!rail || scroller.getBoundingClientRect().left>=rail.getBoundingClientRect().right-1};
      })()`);
      let accessibility=null;
      if(item.view === 'design-system') {
        await evaluate(`document.querySelector('.reference-tabs [role="tab"]').focus()`);
        await call('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight'});
        accessibility=await evaluate(`(() => {
          const active=document.activeElement;
          return {labeledInputs:[...document.querySelectorAll('.reference-section input,.reference-section select,.reference-section textarea')].every(el=>el.labels.length>0),keyboardTabSelection:active.textContent==='Lectures' && active.getAttribute('aria-selected')==='true',visibleKeyboardFocus:getComputedStyle(active).outlineStyle!=='none' && parseFloat(getComputedStyle(active).outlineWidth)>=2,disabledNative:document.querySelector('.reference-actions button:disabled').disabled,touchTargets:[...document.querySelectorAll('.reference-section button,.reference-form > input,.reference-form > select,.reference-form > textarea,.choice-row label')].every(el=>el.getBoundingClientRect().height>=44)};
        })()`);
        await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Home',code:'Home'});
        await evaluate(`document.activeElement.blur();document.querySelector('.reference-page').scrollTop=0`);
      }
      const shot=await call("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      await fs.writeFile(path.join(output,`${item.name}.png`),Buffer.from(shot.data,"base64"));
      let end=null;
      if(item.view.includes("mobile") || item.view.includes("tablet") || item.view === "design-system") {
        end=await evaluate(`(() => {
          const page=document.querySelector('.mobile-shell > .page,.tablet-shell > .page,.reference-page');
          const nav=document.querySelector('.mobile-nav');
          const visible=nav?.getClientRects().length;
          const before=visible?nav.getBoundingClientRect().top:null;
          page.scrollTop=(page.scrollHeight-page.clientHeight)/2;
          const middle=visible?nav.getBoundingClientRect().top:null;
          page.scrollTop=page.scrollHeight;
          const last=page.lastElementChild.getBoundingClientRect(), area=page.getBoundingClientRect();
          const after=visible?nav.getBoundingClientRect().top:null;
          return {persistentNavigation:!visible || (Math.abs(before-middle)<1 && Math.abs(before-after)<1 && Math.abs(nav.getBoundingClientRect().bottom-innerHeight)<1),finalContentReachable:last.bottom<=area.bottom+1,remainingScroll:page.scrollHeight-page.clientHeight-page.scrollTop};
        })()`);
        await evaluate(`new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))`);
        await delay(80);
        const bottom=await call("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
        await fs.writeFile(path.join(output,`${item.name}-bottom.png`),Buffer.from(bottom.data,"base64"));
        await evaluate(`document.documentElement.style.setProperty('--shell-safe-area','34px')`);
        const safe=await evaluate(`(() => { const page=document.querySelector('.mobile-shell > .page,.tablet-shell > .page,.reference-page');page.scrollTop=page.scrollHeight;const element=document.querySelector('.mobile-nav');const nav=element?.getClientRects().length?element:null;return {navHeight:nav?nav.getBoundingClientRect().height:0,contentSafe:!nav || page.getBoundingClientRect().bottom<=nav.getBoundingClientRect().top+1,finalContentReachable:page.lastElementChild.getBoundingClientRect().bottom<=page.getBoundingClientRect().bottom+1}; })()`);
        end.safeArea34=safe;
      }
      results.push({...item,...initial,end,accessibility});
      console.log(`${item.name}: overflow=${initial.horizontalOverflow.length}, nav=${initial.navSafe}, end=${end ? end.finalContentReachable : 'n/a'}`);
    }
    await fs.writeFile(path.join(output,"validation.json"),JSON.stringify(results,null,2)+"\n");
    const failures=results.filter(r=>r.horizontalOverflow.length || r.clippedControls.length || !r.navSafe || !r.navTargets || !r.railSafe || r.accessibility && Object.values(r.accessibility).some(value=>!value) || r.end && (!r.end.persistentNavigation || !r.end.finalContentReachable || !r.end.safeArea34.contentSafe || !r.end.safeArea34.finalContentReachable));
    if(failures.length) process.exitCode=1;
    await send("Browser.close");
  } finally {
    if(ws) ws.close();
    browser.kill();
    await delay(500);
    await fs.rm(profile,{recursive:true,force:true,maxRetries:5,retryDelay:300});
  }
}
run().catch(error=>{ console.error(error.message);process.exitCode=1; });

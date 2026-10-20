(()=>{var d=document,P,L,F,I,B;
function el(t,c,x){var e=d.createElement(t);if(c)e.className=c;if(x)e.textContent=x;return e}
var RX=/(https?:\/\/[^\s)\]>,;]+|[\w.+-]+@[\w-]+(?:\.[\w-]+)+)/g;
function lk(a,h,t){a.href=h;a.textContent=t;a.target="_blank";a.rel="noopener noreferrer"}
function rich(p,text){text.split(RX).forEach(function(s,i){
 if(i%2===0){if(s)p.appendChild(d.createTextNode(s));return}
 var a=el("a"),m=s.indexOf("@")>0&&s.indexOf("://")<0,t=s.replace(/[.]+$/,"");
 lk(a,m?"mailto:"+t:t,t.replace(/^https?:\/\/(www\.)?/,""));p.appendChild(a);if(t!==s)p.appendChild(d.createTextNode(s.slice(t.length)))})}
function add(role,text,meta){var m=el("div","cm "+role),p=el("p");rich(p,text);m.appendChild(p);
 if(meta){var s=el("small","",meta);m.appendChild(s)}L.appendChild(m);L.scrollTop=L.scrollHeight;return m}
function ask(q){
 if(!q)return;add("u",q);I.value="";B.disabled=true;var w=add("b","Thinking…");w.classList.add("w");
 fetch("/api/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({q:q})})
 .then(function(r){return r.json()}).then(function(j){
  w.remove();if(j.error)throw 0;
  var meta=(j.route==="rag"?"from the record":j.route==="decline"?"out of scope":"tool: "+j.route)+(j.guard?" · guard fired":"");
  var m=add("b",j.answer,meta);
  if(j.links){var r=el("div","lks");j.links.forEach(function(x){var a=el("a");lk(a,x.href,x.label+" \u2197");r.appendChild(a)});m.appendChild(r)}
  if(j.source){var s=el("details","src"),u=el("summary","","Source line");s.open=true;var _=0,sp=el("p");rich(sp,j.source);s.appendChild(u);s.appendChild(sp);m.appendChild(s)}
 }).catch(function(){w.remove();add("b","The chat backend isn’t reachable. It runs SmolLM2 on a small server, so it only works where that server is running.")})
 .then(function(){B.disabled=false;I.focus()})}
function build(){
 P=el("div","chat");P.id="chat";P.setAttribute("role","dialog");P.setAttribute("aria-label","Ask about Aditya");
 var h=el("div","ch-h"),t=el("div","");t.appendChild(el("b","","Ask about Aditya"));
 t.appendChild(el("span","","SmolLM2-135M · grounded in the record"));
 var x=el("button","ch-x","×");x.type="button";x.setAttribute("aria-label","Close chat");x.onclick=close;h.appendChild(t);h.appendChild(x);
 L=el("div","ch-l");L.setAttribute("aria-live","polite");
 add("b","Hi. I answer from Aditya’s record only: projects, results, experience and papers. Every answer shows its source.");
 var s=el("div","ch-s");["What was the retrieval time improvement?","What PubMedQA score did Med-Qwen get?","How can I contact Aditya?"].forEach(function(q){var b=el("button","",q);b.type="button";b.onclick=function(){ask(q)};s.appendChild(b)});
 F=el("form","ch-f");I=el("input");I.placeholder="Ask a question…";I.maxLength=300;I.setAttribute("aria-label","Your question");
 B=el("button","","Send");B.type="submit";F.appendChild(I);F.appendChild(B);F.onsubmit=function(e){e.preventDefault();ask(I.value.trim())};
 P.appendChild(h);P.appendChild(L);P.appendChild(s);P.appendChild(F);d.body.appendChild(P)}
function close(){P.classList.remove("on");var f=d.getElementById("chat-open");if(f){f.setAttribute("aria-expanded","false");f.focus()}}
window.openChat=function(){if(!P)build();P.classList.add("on");var f=d.getElementById("chat-open");if(f)f.setAttribute("aria-expanded","true");setTimeout(function(){I.focus()},50)};
addEventListener("keydown",function(e){if(e.key==="Escape"&&P&&P.classList.contains("on"))close()});
})();

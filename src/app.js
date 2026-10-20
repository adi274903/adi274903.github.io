(()=>{var d=document,h=d.documentElement,$=(s,r)=>[].slice.call((r||d).querySelectorAll(s));
h.classList.add("js");
try{var t=localStorage.getItem("th");if(t)h.dataset.theme=t}catch(e){}
var tg=d.getElementById("tg");
if(tg)tg.onclick=function(){var dk=(h.dataset.theme||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light"))==="dark";h.dataset.theme=dk?"light":"dark";try{localStorage.setItem("th",h.dataset.theme)}catch(e){}};
var map={ai:"ai",fintech:"fintech",health:"health",all:"all"};
function track(k){
 if(!map[k])k="all";
 $("[data-track]").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.track===k)});
 $("[data-lede]").forEach(function(e){e.hidden=e.dataset.lede!==(k==="all"?"ai":k)});
 $("[data-stats]").forEach(function(e){e.hidden=e.dataset.stats!==(k==="all"?"ai":k)});
 var g=d.getElementById("grid");if(!g)return;
 var c=$(".card",g);
 c.forEach(function(e,i){e.dataset.i=e.dataset.i||i;var m=k==="all"||(" "+e.dataset.tr+" ").indexOf(" "+k+" ")>-1;e.classList.toggle("off",!m);e.dataset.m=m?0:1});
 c.sort(function(a,b){return a.dataset.m-b.dataset.m||a.dataset.i-b.dataset.i}).forEach(function(e){g.appendChild(e)});
 $("a.cs").forEach(function(a){a.hash=k==="all"?"":"#"+k});
}
$("[data-track]").forEach(function(b){b.onclick=function(){history.replaceState(null,"","#"+b.dataset.track);track(b.dataset.track)}});
track(location.hash.slice(1)||"all");
addEventListener("hashchange",function(){track(location.hash.slice(1))});
var fab=d.getElementById("chat-open");
if(fab)fab.onclick=function(){if(window.openChat)return window.openChat();var s=d.createElement("script");s.src="chat.js";s.onload=function(){window.openChat()};d.head.appendChild(s)};
var cs=$(".ch"),tk=0;
function chk(){tk=0;var vh=innerHeight;cs=cs.filter(function(e){var r=e.getBoundingClientRect();if(r.top<vh*.92&&r.bottom>0){e.classList.add("in");return false}return true})}
function qs(){if(!tk)tk=requestAnimationFrame(chk)}
addEventListener("scroll",qs,{passive:true});addEventListener("resize",qs);setTimeout(chk,60);
})();

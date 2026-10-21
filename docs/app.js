(()=>{var d=document,h=d.documentElement,$=(s,r)=>[].slice.call((r||d).querySelectorAll(s)),wide=matchMedia("(min-width:1000px)"),calm=matchMedia("(prefers-reduced-motion:reduce)");
/* theme */
$("#tg,.tgf").forEach(function(tg){tg.onclick=function(){var dark=(h.dataset.theme||"dark")==="dark";h.dataset.theme=dark?"light":"dark";try{localStorage.setItem("th",h.dataset.theme)}catch(e){}}});
/* reveal each part of a section once as it arrives */
var rv=$("[data-reveal]");
if("IntersectionObserver"in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add("is-in");io.unobserve(x.target)}})},{rootMargin:"0px 0px -8% 0px",threshold:.08});
 rv.forEach(function(e,i){e.style.setProperty("--i",i%4);io.observe(e)});
 addEventListener("load",function(){setTimeout(function(){rv.forEach(function(e){var r=e.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0)e.classList.add("is-in")})},2200)})}
else rv.forEach(function(e){e.classList.add("is-in")});
/* role track: swaps the summary and reorders the projects */
var map={ai:1,fintech:1,health:1,all:1};
function track(k){
 if(!map[k])k="all";
 $("[data-track]").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.track===k)});
 $("[data-lede]").forEach(function(e){e.hidden=e.dataset.lede!==(k==="all"?"ai":k)});
 var g=d.getElementById("grid");if(!g)return;
 var c=$("li",g).filter(function(e){return e.parentNode===g});
 c.forEach(function(e,i){e.dataset.i=e.dataset.i||i;e.dataset.m=(k==="all"||(" "+e.dataset.tr+" ").indexOf(" "+k+" ")>-1)?0:1});
 c.sort(function(a,b){return a.dataset.m-b.dataset.m||a.dataset.i-b.dataset.i}).forEach(function(e){g.appendChild(e)});
 $(".wa a",g).forEach(function(a){a.hash=k==="all"?"":"#"+k});
}
$("[data-track]").forEach(function(b){b.onclick=function(){history.replaceState(null,"","#"+b.dataset.track);track(b.dataset.track)}});
var hk=location.hash.slice(1);if(map[hk])track(hk);else track("all");
addEventListener("hashchange",function(){var x=location.hash.slice(1);if(map[x])track(x)});
/* the stage: the portrait, the figure for a chosen project, or the place of the role being read */
var panes={};$(".stage .pane").forEach(function(p){panes[p.dataset.pane]=p});
var cur="me",chosen=null,tk=0;
function show(name){
 if(!panes[name])name="me";if(name===cur)return;cur=name;
 for(var k in panes){var on=k===name;panes[k].classList.toggle("on",on);panes[k].setAttribute("aria-hidden",!on)}
}
function pick(){
 if(!wide.matches){return}
 var t=d.elementFromPoint(innerWidth*.74,innerHeight*.56),w=t&&t.closest(".works"),x=t&&t.closest("[data-city]");
 if(w&&chosen)show("w"+chosen);else if(x&&x.dataset.city)show(x.dataset.city);else show("me");
}
function queue(){if(!tk)tk=requestAnimationFrame(function(){tk=0;pick()})}
addEventListener("scroll",queue,{passive:true});addEventListener("resize",queue);
function choose(li,toggleInline){
 var n=li.dataset.n;
 if(wide.matches){chosen=n;$(".works > li").forEach(function(e){e.classList.toggle("on",e===li)});show("w"+n)}
 else if(toggleInline){var o=li.classList.toggle("open");$(".wn",li)[0].setAttribute("aria-expanded",o);$(".show",li)[0].textContent=o?"Hide numbers":"Show numbers";$(".ch",li).forEach(function(x){x.classList.add("in")})}
}
$(".works > li").forEach(function(li){
 var b=$(".wn",li)[0],s=$(".show",li)[0];
 b.onclick=s.onclick=function(){choose(li,true)};
 li.addEventListener("mouseenter",function(){if(wide.matches)choose(li,false)});
 b.addEventListener("focus",function(){if(wide.matches)choose(li,false)});
});
pick();
/* the live thing: compare Med-Qwen with one model at a time */
var cmp=d.getElementById("cmp"),pk=d.getElementById("pick"),vd=d.getElementById("verdict");
if(cmp&&pk){
 var heads=$("thead th",cmp),rows=$("tbody tr",cmp);
 var opts=[["all","All models"],["1","Its base model"],["3",heads[3].textContent],["4",heads[4].textContent]];
 function sel(v){
  cmp.dataset.sel=v;
  $("button",pk).forEach(function(b){b.setAttribute("aria-pressed",b.dataset.v===v)});
  var cols=v==="all"?[1,3,4]:[+v],won=0,lost=[];
  rows.forEach(function(r){
   var c=$("td",r),vals={};c.forEach(function(td){vals[td.className.match(/c(\d)/)[1]]=parseFloat(td.dataset.v);td.classList.remove("best")});
   var show=[2].concat(cols),best=Math.max.apply(null,show.map(function(k){return vals[k]}));
   c.forEach(function(td){var k=td.className.match(/c(\d)/)[1];if(show.indexOf(+k)>-1&&vals[k]===best)td.classList.add("best")});
   if(v!=="all"){if(vals[2]>vals[v])won++;else lost.push($("th",r)[0].textContent)}
  });
  if(v==="all"){vd.innerHTML=vd.dataset.all}
  else{var nm=opts.filter(function(o){return o[0]===v})[0][1];vd.innerHTML="Med-Qwen beats "+(v==="1"?"its base model":nm)+" on <em>"+won+" of "+rows.length+"</em> benchmarks."+(lost.length?" It trails on "+lost.join(", ")+".":"")}
 }
 vd.dataset.all=vd.innerHTML;
 opts.forEach(function(o){var b=d.createElement("button");b.type="button";b.dataset.v=o[0];b.textContent=o[1];b.onclick=function(){sel(o[0])};pk.appendChild(b)});
 pk.hidden=false;sel("all");
}
})();

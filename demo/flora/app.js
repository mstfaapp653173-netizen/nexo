/* Shared header, footer, floating buttons and service data for the Flora preview. */
const PHONE_1 = "07719977556";
const PHONE_2 = "07819977556";
const tel = n => "tel:+964" + n.replace(/^0/, "");

const I = {
  tooth: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M7.5 3.5c-2.6 0-4 2.1-4 4.7 0 2.4 1 3.9 1.6 6.1.6 2.4.8 6.2 2.6 6.2 1.9 0 1.6-4.6 3-4.6h2.6c1.4 0 1.1 4.6 3 4.6 1.8 0 2-3.8 2.6-6.2.6-2.2 1.6-3.7 1.6-6.1 0-2.6-1.4-4.7-4-4.7-1.8 0-2.6 1-4.5 1s-2.7-1-4.5-1z"/></svg>',
  smile: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M8 14.5c1 1.4 2.4 2 4 2s3-.6 4-2"/><path d="M9 9.5h.01M15 9.5h.01" stroke-width="2.4"/></svg>',
  implant: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3h10l-1 5H8z"/><path d="M9 8v2h6V8"/><path d="M9.5 10l.5 2h4l.5-2M10 12l.5 2h3l.5-2M10.5 14l.5 2h2l.5-2M11 16l1 5 1-5"/></svg>',
  align: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10c3-3 15-3 18 0v2c-3 4-15 4-18 0z"/><path d="M7 9v5M12 8.5v6M17 9v5"/></svg>',
  shine: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="3"/></svg>',
  child: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="7" r="3.5"/><path d="M5 21c.5-4 3.3-6.5 7-6.5s6.5 2.5 7 6.5"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16 9.8"/></svg>',
  phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h3.5l1.7 4.3-2.2 1.4a11 11 0 0 0 7.3 7.3l1.4-2.2L21 15.5V19a2 2 0 0 1-2.2 2A17 17 0 0 1 3 5.2 2 2 0 0 1 5 3z"/></svg>',
  pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
  clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  cal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
  shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
  user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4.3 4-7 8-7s7.2 2.7 8 7"/></svg>',
  car: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 16V11l2-5h10l2 5v5"/><path d="M3 16h18v3H3zM7 19v2M17 19v2"/></svg>',
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 6l-6 6 6 6"/></svg>',
  quote: '<svg class="q" viewBox="0 0 24 24" fill="currentColor"><path d="M10 7H6a3 3 0 0 0-3 3v4h5v-4H5.5A1.5 1.5 0 0 1 7 8.5h3zm11 0h-4a3 3 0 0 0-3 3v4h5v-4h-2.5A1.5 1.5 0 0 1 18 8.5h3z" transform="translate(0 3)"/></svg>',
  fb: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4a21 21 0 0 0-2.3-.1c-2.3 0-3.9 1.4-3.9 4v2.2H7.8v3h2.6V21z"/></svg>',
  ig: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1" fill="currentColor" stroke="none"/></svg>',
  tt: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.6 3c.3 2.2 1.6 3.6 3.9 3.8v3a7.1 7.1 0 0 1-3.9-1.2v6a5.6 5.6 0 1 1-5.6-5.6c.3 0 .6 0 .9.1v3.1a2.6 2.6 0 1 0 1.8 2.5V3z"/></svg>'
};

/* One list drives the home cards, the services page and the menus. All names come from the clinic's current site. */
const SERVICES = [
  {id:"hollywood", icon:"smile", name:"ابتسامة هوليود", featured:true,
   text:"تصميم ابتسامة متناسقة بشكل ولون الأسنان، تناسب ملامح وجهك."},
  {id:"implants", icon:"implant", name:"زراعة الأسنان", featured:true,
   text:"تعويض السن المفقود بزرعة ثابتة تشبه السن الطبيعي في الشكل والاستخدام."},
  {id:"aligners", icon:"align", name:"التقويم الألماني الشفاف", featured:true,
   text:"تقويم شفاف يكاد لا يُرى، يعدّل ترتيب الأسنان بدون أسلاك ظاهرة."},
  {id:"ortho", icon:"align", name:"تقويم الأسنان",
   text:"تعديل اصطفاف الأسنان والإطباق للكبار والصغار."},
  {id:"veneers", icon:"tooth", name:"الفينير",
   text:"قشور رقيقة تُلصق على واجهة الأسنان لتحسين شكلها ولونها."},
  {id:"crowns", icon:"tooth", name:"التيجان التجميلية",
   text:"تلبيسات تحمي السن الضعيف وتعيد له شكله الطبيعي."},
  {id:"fillings", icon:"tooth", name:"الحشوات التجميلية",
   text:"حشوات بلون السن تعالج التسوس وتبقى غير ملحوظة."},
  {id:"gums", icon:"smile", name:"تجميل اللثة",
   text:"تحسين شكل اللثة وتناسقها مع الأسنان لابتسامة أجمل."},
  {id:"whitening", icon:"shine", name:"تنظيف وتبييض الأسنان",
   text:"إزالة الجير والتصبغات وتفتيح لون الأسنان بأمان."},
  {id:"dentures", icon:"smile", name:"أطقم الأسنان",
   text:"أطقم كاملة أو جزئية تعيد القدرة على المضغ والكلام براحة."},
  {id:"extraction", icon:"tooth", name:"قلع الأسنان",
   text:"قلع السن عند الحاجة بأقل انزعاج ممكن."},
  {id:"kids", icon:"child", name:"أسنان الأطفال",
   text:"رعاية أسنان الصغار بأسلوب هادئ يطمّن الطفل والأهل."},
  {id:"checkup", icon:"cal", name:"الفحص الدوري",
   text:"فحص منتظم يكشف المشاكل مبكراً قبل ما تكبر."}
];

const NAV = [
  ["index","الرئيسية","index.html"],
  ["services","خدماتنا","services.html"],
  ["about","من نحن","about.html"],
  ["contact","تواصل معنا","contact.html"]
];

function header(page){
  return `<header class="site-head"><div class="wrap head-in">
    <a class="logo" href="index.html" aria-label="فلورا كلينك"><span class="logo-mark">${I.tooth.replace('stroke="currentColor"','stroke="#fff"')}</span><span>فلورا كلينك<small>مركز فلورا لطب وتجميل الأسنان</small></span></a>
    <nav class="nav" id="nav">${NAV.map(([k,l,h])=>`<a href="${h}" class="${k===page?'on':''}">${l}</a>`).join("")}</nav>
    <div class="head-cta">
      <a class="head-phone" href="${tel(PHONE_1)}">${PHONE_1}</a>
      <a class="btn btn-main" href="contact.html#book">${I.cal} احجز موعدك</a>
      <button class="menu-btn" id="menuBtn" aria-label="القائمة" aria-expanded="false">${I.menu}</button>
    </div></div></header>`;
}

function footer(){
  return `<footer class="site-foot"><div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="logo" href="index.html"><span class="logo-mark">${I.tooth.replace('stroke="currentColor"','stroke="#fff"')}</span><span>فلورا كلينك<small>مركز فلورا لطب وتجميل الأسنان</small></span></a>
        <p style="margin-top:14px">جميع علاجات الأسنان في مركز واحد متكامل. لأن ابتسامتك تستحق الأفضل.</p>
        <div class="social" style="margin-top:16px">
          <a href="https://www.facebook.com/Floraclinic1" aria-label="فيسبوك">${I.fb}</a>
          <a href="https://www.instagram.com/flora.clinic1" aria-label="إنستغرام">${I.ig}</a>
          <a href="https://www.tiktok.com/@flora.clinic" aria-label="تيك توك">${I.tt}</a>
        </div>
      </div>
      <div><h4>الصفحات</h4><ul>${NAV.map(([k,l,h])=>`<li><a href="${h}">${l}</a></li>`).join("")}</ul></div>
      <div><h4>أبرز الخدمات</h4><ul>${SERVICES.slice(0,5).map(s=>`<li><a href="services.html#${s.id}">${s.name}</a></li>`).join("")}</ul></div>
      <div><h4>اتصل بنا</h4><ul>
        <li><a class="ltr" href="${tel(PHONE_1)}">${PHONE_1}</a></li>
        <li><a class="ltr" href="${tel(PHONE_2)}">${PHONE_2}</a></li>
        <li>بغداد، المنصور، حي المهندسين، مقابل السفارة التونسية</li>
        <li><a href="about.html#branches">كل الفروع</a></li>
      </ul></div>
    </div>
    <div class="foot-bottom"><span>© 2026 عيادة فلورا. جميع الحقوق محفوظة.</span><span>نموذج تصميم مقترح</span></div>
  </div></footer>
  <div class="fab"><a class="call" href="${tel(PHONE_1)}">${I.phone} اتصل الآن</a><a class="book" href="contact.html#book">${I.cal} احجز موعد</a></div>`;
}

function serviceCards(list, withLink=true){
  return list.map(s=>`<article class="card reveal"><div class="ic">${I[s.icon]}</div><h3>${s.name}</h3><p>${s.text}</p>${withLink?`<a class="more" href="services.html#${s.id}">التفاصيل ${I.arrow}</a>`:""}</article>`).join("");
}

document.addEventListener("DOMContentLoaded",()=>{
  const page = document.body.dataset.page;
  document.body.insertAdjacentHTML("afterbegin", header(page));
  document.body.insertAdjacentHTML("beforeend", footer());

  document.querySelectorAll("[data-icon]").forEach(el=>{el.innerHTML = I[el.dataset.icon] || "";});
  const featured = document.getElementById("featured");
  if(featured) featured.innerHTML = SERVICES.filter(s=>s.featured).map(s=>`<article class="card feat reveal"><div class="ph" role="img" aria-label="${s.name}"></div><span class="tag">خدمة مميزة</span><h3>${s.name}</h3><p>${s.text}</p><a class="more" href="services.html#${s.id}">التفاصيل ${I.arrow}</a></article>`).join("");
  const chips = document.getElementById("chips");
  if(chips) chips.innerHTML = SERVICES.filter(s=>!s.featured).map(s=>`<a href="services.html#${s.id}">${s.name}</a>`).join("");
  const svcList = document.getElementById("svcList");
  if(svcList) svcList.innerHTML = SERVICES.map(s=>`<div class="svc-row reveal" id="${s.id}"><div class="ic">${I[s.icon]}</div><div><h3>${s.name}</h3><p>${s.text}</p></div><a class="btn btn-ghost" href="contact.html#book">احجز استشارة</a></div>`).join("");
  const sel = document.getElementById("svcSelect");
  if(sel) sel.insertAdjacentHTML("beforeend", SERVICES.map(s=>`<option>${s.name}</option>`).join(""));

  document.querySelectorAll(".ph").forEach(el=>{ if(!el.innerHTML.trim()) el.innerHTML = I.tooth; });

  const btn = document.getElementById("menuBtn"), nav = document.getElementById("nav");
  btn && btn.addEventListener("click",()=>{const o = nav.classList.toggle("open"); btn.setAttribute("aria-expanded", o);});

  // headline words fade up one after another (Arabic keeps whole words, no letter splitting)
  document.querySelectorAll(".fade-words").forEach(h=>{
    let i = 0;
    h.querySelectorAll("[data-line]").forEach(line=>{
      line.innerHTML = line.textContent.trim().split(/\s+/).map(w=>`<span class="w" style="animation-delay:${(i++)*0.09}s">${w}</span>`).join(" ");
    });
  });

  // reveal on scroll
  const io = "IntersectionObserver" in window ? new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in"); io.unobserve(e.target);}}),{threshold:.12}) : null;
  document.querySelectorAll(".reveal").forEach(el=> io ? io.observe(el) : el.classList.add("in"));

  // count up
  document.querySelectorAll("[data-count]").forEach(el=>{
    const end = +el.dataset.count; let n = 0;
    const run = ()=>{ const t = setInterval(()=>{ n++; el.textContent = n; if(n>=end) clearInterval(t); }, 60); };
    if(io){ const o = new IntersectionObserver(es=>{ if(es[0].isIntersecting){ run(); o.disconnect(); } }); o.observe(el); } else el.textContent = end;
  });

  // demo form: no backend until the clinic approves
  const form = document.getElementById("book");
  form && form.addEventListener("submit",e=>{ e.preventDefault(); form.classList.add("sent"); form.querySelector("button[type=submit]").disabled = true; });
});

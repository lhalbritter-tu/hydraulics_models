var _JUPYTERLAB;(()=>{"use strict";var e,r,t,n,a,o,i,u,l,s,d,f,c,p,h,v,g,b,m={592:(e,r,t)=>{var n={"./index":()=>Promise.all([t.e(0),t.e(880)]).then((()=>()=>t(880))),"./extension":()=>Promise.all([t.e(0),t.e(880)]).then((()=>()=>t(880)))},a=(e,r)=>(t.R=r,r=t.o(n,e)?n[e]():Promise.resolve().then((()=>{throw new Error('Module "'+e+'" does not exist in container.')})),t.R=void 0,r),o=(e,r)=>{if(t.S){var n="default",a=t.S[n];if(a&&a!==e)throw new Error("Container initialization failed as it has already been initialized with a different share scope");return t.S[n]=e,t.I(n,r)}};t.d(r,{get:()=>a,init:()=>o})}},y={};function w(e){var r=y[e];if(void 0!==r)return r.exports;var t=y[e]={exports:{}};return m[e].call(t.exports,t,t.exports,w),t.exports}w.m=m,w.c=y,w.d=(e,r)=>{for(var t in r)w.o(r,t)&&!w.o(e,t)&&Object.defineProperty(e,t,{enumerable:!0,get:r[t]})},w.f={},w.e=e=>Promise.all(Object.keys(w.f).reduce(((r,t)=>(w.f[t](e,r),r)),[])),w.u=e=>e+"."+{0:"b799fb406e2c3cecfec0",511:"22f7942246884696c751",824:"786455fe656b35bbdc7b",880:"db5a1c77c98cc5afe2c1"}[e]+".js?v="+{0:"b799fb406e2c3cecfec0",511:"22f7942246884696c751",824:"786455fe656b35bbdc7b",880:"db5a1c77c98cc5afe2c1"}[e],w.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"==typeof window)return window}}(),w.o=(e,r)=>Object.prototype.hasOwnProperty.call(e,r),e={},r="jupyterlab-datawidgets:",w.l=(t,n,a,o)=>{if(e[t])e[t].push(n);else{var i,u;if(void 0!==a)for(var l=document.getElementsByTagName("script"),s=0;s<l.length;s++){var d=l[s];if(d.getAttribute("src")==t||d.getAttribute("data-webpack")==r+a){i=d;break}}i||(u=!0,(i=document.createElement("script")).charset="utf-8",i.timeout=120,w.nc&&i.setAttribute("nonce",w.nc),i.setAttribute("data-webpack",r+a),i.src=t),e[t]=[n];var f=(r,n)=>{i.onerror=i.onload=null,clearTimeout(c);var a=e[t];if(delete e[t],i.parentNode&&i.parentNode.removeChild(i),a&&a.forEach((e=>e(n))),r)return r(n)},c=setTimeout(f.bind(null,void 0,{type:"timeout",target:i}),12e4);i.onerror=f.bind(null,i.onerror),i.onload=f.bind(null,i.onload),u&&document.head.appendChild(i)}},(()=>{w.S={};var e={},r={};w.I=(t,n)=>{n||(n=[]);var a=r[t];if(a||(a=r[t]={}),!(n.indexOf(a)>=0)){if(n.push(a),e[t])return e[t];w.o(w.S,t)||(w.S[t]={});var o=w.S[t],i="jupyterlab-datawidgets",u=(e,r,t,n)=>{var a=o[e]=o[e]||{},u=a[r];(!u||!u.loaded&&(!n!=!u.eager?n:i>u.from))&&(a[r]={get:t,from:i,eager:!!n})},l=[];return"default"===t&&(u("jupyter-datawidgets","5.5.1",(()=>Promise.all([w.e(511),w.e(824),w.e(0)]).then((()=>()=>w(824))))),u("jupyterlab-datawidgets","7.1.1",(()=>Promise.all([w.e(0),w.e(880)]).then((()=>()=>w(880)))))),e[t]=l.length?Promise.all(l).then((()=>e[t]=1)):1}}})(),(()=>{var e;w.g.importScripts&&(e=w.g.location+"");var r=w.g.document;if(!e&&r&&(r.currentScript&&(e=r.currentScript.src),!e)){var t=r.getElementsByTagName("script");t.length&&(e=t[t.length-1].src)}if(!e)throw new Error("Automatic publicPath is not supported in this browser");e=e.replace(/#.*$/,"").replace(/\?.*$/,"").replace(/\/[^\/]+$/,"/"),w.p=e})(),t=e=>{var r=e=>e.split(".").map((e=>+e==e?+e:e)),t=/^([^-+]+)?(?:-([^+]+))?(?:\+(.+))?$/.exec(e),n=t[1]?r(t[1]):[];return t[2]&&(n.length++,n.push.apply(n,r(t[2]))),t[3]&&(n.push([]),n.push.apply(n,r(t[3]))),n},n=(e,r)=>{e=t(e),r=t(r);for(var n=0;;){if(n>=e.length)return n<r.length&&"u"!=(typeof r[n])[0];var a=e[n],o=(typeof a)[0];if(n>=r.length)return"u"==o;var i=r[n],u=(typeof i)[0];if(o!=u)return"o"==o&&"n"==u||"s"==u||"u"==o;if("o"!=o&&"u"!=o&&a!=i)return a<i;n++}},a=e=>{var r=e[0],t="";if(1===e.length)return"*";if(r+.5){t+=0==r?">=":-1==r?"<":1==r?"^":2==r?"~":r>0?"=":"!=";for(var n=1,o=1;o<e.length;o++)n--,t+="u"==(typeof(u=e[o]))[0]?"-":(n>0?".":"")+(n=2,u);return t}var i=[];for(o=1;o<e.length;o++){var u=e[o];i.push(0===u?"not("+l()+")":1===u?"("+l()+" || "+l()+")":2===u?i.pop()+" "+i.pop():a(u))}return l();function l(){return i.pop().replace(/^\((.+)\)$/,"$1")}},o=(e,r)=>{if(0 in e){r=t(r);var n=e[0],a=n<0;a&&(n=-n-1);for(var i=0,u=1,l=!0;;u++,i++){var s,d,f=u<e.length?(typeof e[u])[0]:"";if(i>=r.length||"o"==(d=(typeof(s=r[i]))[0]))return!l||("u"==f?u>n&&!a:""==f!=a);if("u"==d){if(!l||"u"!=f)return!1}else if(l)if(f==d)if(u<=n){if(s!=e[u])return!1}else{if(a?s>e[u]:s<e[u])return!1;s!=e[u]&&(l=!1)}else if("s"!=f&&"n"!=f){if(a||u<=n)return!1;l=!1,u--}else{if(u<=n||d<f!=a)return!1;l=!1}else"s"!=f&&"n"!=f&&(l=!1,u--)}}var c=[],p=c.pop.bind(c);for(i=1;i<e.length;i++){var h=e[i];c.push(1==h?p()|p():2==h?p()&p():h?o(h,r):!p())}return!!p()},i=(e,r)=>{var t=w.S[e];if(!t||!w.o(t,r))throw new Error("Shared module "+r+" doesn't exist in shared scope "+e);return t},u=(e,r)=>{var t=e[r];return Object.keys(t).reduce(((e,r)=>!e||!t[e].loaded&&n(e,r)?r:e),0)},l=(e,r,t,n)=>"Unsatisfied version "+t+" from "+(t&&e[r][t].from)+" of shared singleton module "+r+" (required "+a(n)+")",s=(e,r,t,n)=>{var a=u(e,t);return o(n,a)||"undefined"!=typeof console&&console.warn&&console.warn(l(e,t,a,n)),f(e[t][a])},d=(e,r,t)=>{var a=e[r];return(r=Object.keys(a).reduce(((e,r)=>!o(t,r)||e&&!n(e,r)?e:r),0))&&a[r]},f=e=>(e.loaded=1,e.get()),p=(c=e=>function(r,t,n,a){var o=w.I(r);return o&&o.then?o.then(e.bind(e,r,w.S[r],t,n,a)):e(r,w.S[r],t,n,a)})(((e,r,t,n)=>(i(e,t),s(r,0,t,n)))),h=c(((e,r,t,n,a)=>{var o=r&&w.o(r,t)&&d(r,t,n);return o?f(o):a()})),v={},g={0:()=>p("default","@jupyter-widgets/base",[,[1,6,0,0,,"rc",0],[1,5],[1,4],[1,3],[1,2],[1,1],1,1,1,1,1]),526:()=>p("default","@lumino/coreutils",[1,1,11,0]),815:()=>h("default","jupyter-datawidgets",[1,5,5,1],(()=>Promise.all([w.e(511),w.e(824)]).then((()=>()=>w(824)))))},b={0:[0],880:[526,815]},w.f.consumes=(e,r)=>{w.o(b,e)&&b[e].forEach((e=>{if(w.o(v,e))return r.push(v[e]);var t=r=>{v[e]=0,w.m[e]=t=>{delete w.c[e],t.exports=r()}},n=r=>{delete v[e],w.m[e]=t=>{throw delete w.c[e],r}};try{var a=g[e]();a.then?r.push(v[e]=a.then(t).catch(n)):t(a)}catch(e){n(e)}}))},(()=>{var e={575:0};w.f.j=(r,t)=>{var n=w.o(e,r)?e[r]:void 0;if(0!==n)if(n)t.push(n[2]);else if(0!=r){var a=new Promise(((t,a)=>n=e[r]=[t,a]));t.push(n[2]=a);var o=w.p+w.u(r),i=new Error;w.l(o,(t=>{if(w.o(e,r)&&(0!==(n=e[r])&&(e[r]=void 0),n)){var a=t&&("load"===t.type?"missing":t.type),o=t&&t.target&&t.target.src;i.message="Loading chunk "+r+" failed.\n("+a+": "+o+")",i.name="ChunkLoadError",i.type=a,i.request=o,n[1](i)}}),"chunk-"+r,r)}else e[r]=0};var r=(r,t)=>{var n,a,[o,i,u]=t,l=0;if(o.some((r=>0!==e[r]))){for(n in i)w.o(i,n)&&(w.m[n]=i[n]);u&&u(w)}for(r&&r(t);l<o.length;l++)a=o[l],w.o(e,a)&&e[a]&&e[a][0](),e[a]=0},t=self.webpackChunkjupyterlab_datawidgets=self.webpackChunkjupyterlab_datawidgets||[];t.forEach(r.bind(null,0)),t.push=r.bind(null,t.push.bind(t))})();var j=w(592);(_JUPYTERLAB=void 0===_JUPYTERLAB?{}:_JUPYTERLAB)["jupyterlab-datawidgets"]=j})();
import{S as h,i as b,s as _,G as k,e as x,C as r,g as v,E as p,m as I,J as E,p as d,t as g,q as w,n as C,y as L,B as m,D as c,F as f,H as z,M,l as j,o as q,r as D}from"./index-01c8c7ba.js";import"./Button-e35ce84f.js";/* empty css                                                    */import"./ModifyUpload.svelte_svelte_type_style_lang-ba6baa96.js";function S(a){let e,l,t,s,n,o;return t=new a[0]({}),{c(){e=k("button"),l=k("div"),x(t.$$.fragment),r(l,"class","svelte-1p4r00v"),r(e,"aria-label",a[1]),r(e,"class","svelte-1p4r00v")},m(i,u){v(i,e,u),p(e,l),I(t,l,null),s=!0,n||(o=E(e,"click",a[2]),n=!0)},p(i,[u]){(!s||u&2)&&r(e,"aria-label",i[1])},i(i){s||(d(t.$$.fragment,i),s=!0)},o(i){g(t.$$.fragment,i),s=!1},d(i){i&&w(e),C(t),n=!1,o()}}}function y(a,e,l){let{Icon:t}=e,{label:s=""}=e;function n(o){L.call(this,a,o)}return a.$$set=o=>{"Icon"in o&&l(0,t=o.Icon),"label"in o&&l(1,s=o.label)},[t,s,n]}class B extends h{constructor(e){super(),b(this,e,y,S,_,{Icon:0,label:1})}}function F(a){let e,l,t,s;return{c(){e=m("svg"),l=m("g"),t=m("path"),s=m("path"),r(t,"d","M18,6L6.087,17.913"),c(t,"fill","none"),c(t,"fill-rule","nonzero"),c(t,"stroke-width","2px"),r(l,"transform","matrix(1.14096,-0.140958,-0.140958,1.14096,-0.0559523,0.0559523)"),r(s,"d","M4.364,4.364L19.636,19.636"),c(s,"fill","none"),c(s,"fill-rule","nonzero"),c(s,"stroke-width","2px"),r(e,"width","100%"),r(e,"height","100%"),r(e,"viewBox","0 0 24 24"),r(e,"version","1.1"),r(e,"xmlns","http://www.w3.org/2000/svg"),r(e,"xmlns:xlink","http://www.w3.org/1999/xlink"),r(e,"xml:space","preserve"),r(e,"stroke","currentColor"),c(e,"fill-rule","evenodd"),c(e,"clip-rule","evenodd"),c(e,"stroke-linecap","round"),c(e,"stroke-linejoin","round")},m(n,o){v(n,e,o),p(e,l),p(l,t),p(e,s)},p:f,i:f,o:f,d(n){n&&w(e)}}}class G extends h{constructor(e){super(),b(this,e,null,F,_,{})}}function H(a){let e,l;return{c(){e=m("svg"),l=m("path"),r(l,"d","M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"),r(e,"xmlns","http://www.w3.org/2000/svg"),r(e,"width","100%"),r(e,"height","100%"),r(e,"viewBox","0 0 24 24"),r(e,"fill","none"),r(e,"stroke","currentColor"),r(e,"stroke-width","1.5"),r(e,"stroke-linecap","round"),r(e,"stroke-linejoin","round"),r(e,"class","feather feather-edit-2")},m(t,s){v(t,e,s),p(e,l)},p:f,i:f,o:f,d(t){t&&w(e)}}}class J extends h{constructor(e){super(),b(this,e,null,H,_,{})}}function $(a){let e,l;return e=new B({props:{Icon:J,label:"Edit"}}),e.$on("click",a[3]),{c(){x(e.$$.fragment)},m(t,s){I(e,t,s),l=!0},p:f,i(t){l||(d(e.$$.fragment,t),l=!0)},o(t){g(e.$$.fragment,t),l=!1},d(t){C(e,t)}}}function P(a){let e,l,t,s,n=a[0]&&$(a);return t=new B({props:{Icon:G,label:"Clear"}}),t.$on("click",a[4]),{c(){e=k("div"),n&&n.c(),l=z(),x(t.$$.fragment),r(e,"class","svelte-19sk1im"),M(e,"not-absolute",!a[1]),c(e,"position",a[1]?"absolute":"static")},m(o,i){v(o,e,i),n&&n.m(e,null),p(e,l),I(t,e,null),s=!0},p(o,[i]){o[0]?n?(n.p(o,i),i&1&&d(n,1)):(n=$(o),n.c(),d(n,1),n.m(e,l)):n&&(j(),g(n,1,1,()=>{n=null}),q()),(!s||i&2)&&M(e,"not-absolute",!o[1]),i&2&&c(e,"position",o[1]?"absolute":"static")},i(o){s||(d(n),d(t.$$.fragment,o),s=!0)},o(o){g(n),g(t.$$.fragment,o),s=!1},d(o){o&&w(e),n&&n.d(),C(t)}}}function U(a,e,l){let{editable:t=!1}=e,{absolute:s=!0}=e;const n=D(),o=()=>n("edit"),i=u=>{n("clear"),u.stopPropagation()};return a.$$set=u=>{"editable"in u&&l(0,t=u.editable),"absolute"in u&&l(1,s=u.absolute)},[t,s,n,o,i]}class Q extends h{constructor(e){super(),b(this,e,U,P,_,{editable:0,absolute:1})}}export{G as C,B as I,Q as M};
//# sourceMappingURL=ModifyUpload-e1f9932c.js.map

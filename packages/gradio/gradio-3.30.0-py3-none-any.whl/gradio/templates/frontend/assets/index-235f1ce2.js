import{S as h,i as p,s as v,b as T,a as k,e as C,m as S,k as q,p as m,t as r,n as w,r as D,V as E,X as V,Y as X,Z as Y,y as u}from"./index-01c8c7ba.js";import{T as Z}from"./TabItem.svelte_svelte_type_style_lang-1623faa7.js";/* empty css                                             */function j(s){let e;const i=s[4].default,t=E(i,s,s[8],null);return{c(){t&&t.c()},m(n,o){t&&t.m(n,o),e=!0},p(n,o){t&&t.p&&(!e||o&256)&&V(t,i,n,n[8],e?Y(i,n[8],o,null):X(n[8]),null)},i(n){e||(m(t,n),e=!0)},o(n){r(t,n),e=!1},d(n){t&&t.d(n)}}}function z(s){let e,i,t;function n(l){s[5](l)}let o={visible:s[1],elem_id:s[2],elem_classes:s[3],$$slots:{default:[j]},$$scope:{ctx:s}};return s[0]!==void 0&&(o.selected=s[0]),e=new Z({props:o}),T.push(()=>k(e,"selected",n)),e.$on("change",s[6]),e.$on("select",s[7]),{c(){C(e.$$.fragment)},m(l,c){S(e,l,c),t=!0},p(l,[c]){const _={};c&2&&(_.visible=l[1]),c&4&&(_.elem_id=l[2]),c&8&&(_.elem_classes=l[3]),c&256&&(_.$$scope={dirty:c,ctx:l}),!i&&c&1&&(i=!0,_.selected=l[0],q(()=>i=!1)),e.$set(_)},i(l){t||(m(e.$$.fragment,l),t=!0)},o(l){r(e.$$.fragment,l),t=!1},d(l){w(e,l)}}}function A(s,e,i){let{$$slots:t={},$$scope:n}=e;const o=D();let{visible:l=!0}=e,{elem_id:c=""}=e,{elem_classes:_=[]}=e,{selected:f}=e;function d(a){f=a,i(0,f)}function b(a){u.call(this,s,a)}function g(a){u.call(this,s,a)}return s.$$set=a=>{"visible"in a&&i(1,l=a.visible),"elem_id"in a&&i(2,c=a.elem_id),"elem_classes"in a&&i(3,_=a.elem_classes),"selected"in a&&i(0,f=a.selected),"$$scope"in a&&i(8,n=a.$$scope)},s.$$.update=()=>{s.$$.dirty&1&&o("prop_change",{selected:f})},[f,l,c,_,t,d,b,g,n]}class B extends h{constructor(e){super(),p(this,e,A,z,v,{visible:1,elem_id:2,elem_classes:3,selected:0})}}const I=B,J=["static"];export{I as Component,J as modes};
//# sourceMappingURL=index-235f1ce2.js.map

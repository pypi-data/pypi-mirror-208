function W(n,t){return n==null||t==null?NaN:n<t?-1:n>t?1:n>=t?0:NaN}function En(n){let t=n,e=n,r=n;n.length!==2&&(t=(a,u)=>n(a)-u,e=W,r=(a,u)=>W(n(a),u));function i(a,u,s=0,c=a.length){if(s<c){if(e(u,u)!==0)return c;do{const h=s+c>>>1;r(a[h],u)<0?s=h+1:c=h}while(s<c)}return s}function f(a,u,s=0,c=a.length){if(s<c){if(e(u,u)!==0)return c;do{const h=s+c>>>1;r(a[h],u)<=0?s=h+1:c=h}while(s<c)}return s}function o(a,u,s=0,c=a.length){const h=i(a,u,s,c-1);return h>s&&t(a[h-1],u)>-t(a[h],u)?h-1:h}return{left:i,center:o,right:f}}function Un(n){return n===null?NaN:+n}function*Qt(n,t){if(t===void 0)for(let e of n)e!=null&&(e=+e)>=e&&(yield e);else{let e=-1;for(let r of n)(r=t(r,++e,n))!=null&&(r=+r)>=r&&(yield r)}}const Pn=En(W),Yn=Pn.right,Ut=Pn.left;En(Un).center;const Jn=Yn;var nn=Math.sqrt(50),tn=Math.sqrt(10),en=Math.sqrt(2);function Kn(n,t,e){var r,i=-1,f,o,a;if(t=+t,n=+n,e=+e,n===t&&e>0)return[n];if((r=t<n)&&(f=n,n=t,t=f),(a=jn(n,t,e))===0||!isFinite(a))return[];if(a>0){let u=Math.round(n/a),s=Math.round(t/a);for(u*a<n&&++u,s*a>t&&--s,o=new Array(f=s-u+1);++i<f;)o[i]=(u+i)*a}else{a=-a;let u=Math.round(n*a),s=Math.round(t*a);for(u/a<n&&++u,s/a>t&&--s,o=new Array(f=s-u+1);++i<f;)o[i]=(u+i)/a}return r&&o.reverse(),o}function jn(n,t,e){var r=(t-n)/Math.max(0,e),i=Math.floor(Math.log(r)/Math.LN10),f=r/Math.pow(10,i);return i>=0?(f>=nn?10:f>=tn?5:f>=en?2:1)*Math.pow(10,i):-Math.pow(10,-i)/(f>=nn?10:f>=tn?5:f>=en?2:1)}function Wn(n,t,e){var r=Math.abs(t-n)/Math.max(0,e),i=Math.pow(10,Math.floor(Math.log(r)/Math.LN10)),f=r/i;return f>=nn?i*=10:f>=tn?i*=5:f>=en&&(i*=2),t<n?-i:i}function nt(n){return Math.abs(n=Math.round(n))>=1e21?n.toLocaleString("en").replace(/,/g,""):n.toString(10)}function G(n,t){if((e=(n=t?n.toExponential(t-1):n.toExponential()).indexOf("e"))<0)return null;var e,r=n.slice(0,e);return[r.length>1?r[0]+r.slice(2):r,+n.slice(e+1)]}function L(n){return n=G(Math.abs(n)),n?n[1]:NaN}function tt(n,t){return function(e,r){for(var i=e.length,f=[],o=0,a=n[0],u=0;i>0&&a>0&&(u+a+1>r&&(a=Math.max(1,r-u)),f.push(e.substring(i-=a,i+a)),!((u+=a+1)>r));)a=n[o=(o+1)%n.length];return f.reverse().join(t)}}function et(n){return function(t){return t.replace(/[0-9]/g,function(e){return n[+e]})}}var rt=/^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;function Z(n){if(!(t=rt.exec(n)))throw new Error("invalid format: "+n);var t;return new sn({fill:t[1],align:t[2],sign:t[3],symbol:t[4],zero:t[5],width:t[6],comma:t[7],precision:t[8]&&t[8].slice(1),trim:t[9],type:t[10]})}Z.prototype=sn.prototype;function sn(n){this.fill=n.fill===void 0?" ":n.fill+"",this.align=n.align===void 0?">":n.align+"",this.sign=n.sign===void 0?"-":n.sign+"",this.symbol=n.symbol===void 0?"":n.symbol+"",this.zero=!!n.zero,this.width=n.width===void 0?void 0:+n.width,this.comma=!!n.comma,this.precision=n.precision===void 0?void 0:+n.precision,this.trim=!!n.trim,this.type=n.type===void 0?"":n.type+""}sn.prototype.toString=function(){return this.fill+this.align+this.sign+this.symbol+(this.zero?"0":"")+(this.width===void 0?"":Math.max(1,this.width|0))+(this.comma?",":"")+(this.precision===void 0?"":"."+Math.max(0,this.precision|0))+(this.trim?"~":"")+this.type};function it(n){n:for(var t=n.length,e=1,r=-1,i;e<t;++e)switch(n[e]){case".":r=i=e;break;case"0":r===0&&(r=e),i=e;break;default:if(!+n[e])break n;r>0&&(r=0);break}return r>0?n.slice(0,r)+n.slice(i+1):n}var qn;function at(n,t){var e=G(n,t);if(!e)return n+"";var r=e[0],i=e[1],f=i-(qn=Math.max(-8,Math.min(8,Math.floor(i/3)))*3)+1,o=r.length;return f===o?r:f>o?r+new Array(f-o+1).join("0"):f>0?r.slice(0,f)+"."+r.slice(f):"0."+new Array(1-f).join("0")+G(n,Math.max(0,t+f-1))[0]}function xn(n,t){var e=G(n,t);if(!e)return n+"";var r=e[0],i=e[1];return i<0?"0."+new Array(-i).join("0")+r:r.length>i+1?r.slice(0,i+1)+"."+r.slice(i+1):r+new Array(i-r.length+2).join("0")}const mn={"%":(n,t)=>(n*100).toFixed(t),b:n=>Math.round(n).toString(2),c:n=>n+"",d:nt,e:(n,t)=>n.toExponential(t),f:(n,t)=>n.toFixed(t),g:(n,t)=>n.toPrecision(t),o:n=>Math.round(n).toString(8),p:(n,t)=>xn(n*100,t),r:xn,s:at,X:n=>Math.round(n).toString(16).toUpperCase(),x:n=>Math.round(n).toString(16)};function bn(n){return n}var pn=Array.prototype.map,yn=["y","z","a","f","p","n","µ","m","","k","M","G","T","P","E","Z","Y"];function ft(n){var t=n.grouping===void 0||n.thousands===void 0?bn:tt(pn.call(n.grouping,Number),n.thousands+""),e=n.currency===void 0?"":n.currency[0]+"",r=n.currency===void 0?"":n.currency[1]+"",i=n.decimal===void 0?".":n.decimal+"",f=n.numerals===void 0?bn:et(pn.call(n.numerals,String)),o=n.percent===void 0?"%":n.percent+"",a=n.minus===void 0?"−":n.minus+"",u=n.nan===void 0?"NaN":n.nan+"";function s(h){h=Z(h);var l=h.fill,p=h.align,g=h.sign,k=h.symbol,v=h.zero,N=h.width,R=h.comma,y=h.precision,H=h.trim,m=h.type;m==="n"?(R=!0,m="g"):mn[m]||(y===void 0&&(y=12),H=!0,m="g"),(v||l==="0"&&p==="=")&&(v=!0,l="0",p="=");var Vn=k==="$"?e:k==="#"&&/[boxX]/.test(m)?"0"+m.toLowerCase():"",Xn=k==="$"?r:/[%p]/.test(m)?o:"",ln=mn[m],Qn=/[defgprs%]/.test(m);y=y===void 0?6:/[gprs]/.test(m)?Math.max(1,Math.min(21,y)):Math.max(0,Math.min(20,y));function dn(d){var A=Vn,b=Xn,E,gn,F;if(m==="c")b=ln(d)+b,d="";else{d=+d;var $=d<0||1/d<0;if(d=isNaN(d)?u:ln(Math.abs(d),y),H&&(d=it(d)),$&&+d==0&&g!=="+"&&($=!1),A=($?g==="("?g:a:g==="-"||g==="("?"":g)+A,b=(m==="s"?yn[8+qn/3]:"")+b+($&&g==="("?")":""),Qn){for(E=-1,gn=d.length;++E<gn;)if(F=d.charCodeAt(E),48>F||F>57){b=(F===46?i+d.slice(E+1):d.slice(E))+b,d=d.slice(0,E);break}}}R&&!v&&(d=t(d,1/0));var B=A.length+d.length+b.length,_=B<N?new Array(N-B+1).join(l):"";switch(R&&v&&(d=t(_+d,_.length?N-b.length:1/0),_=""),p){case"<":d=A+d+b+_;break;case"=":d=A+_+d+b;break;case"^":d=_.slice(0,B=_.length>>1)+A+d+b+_.slice(B);break;default:d=_+A+d+b;break}return f(d)}return dn.toString=function(){return h+""},dn}function c(h,l){var p=s((h=Z(h),h.type="f",h)),g=Math.max(-8,Math.min(8,Math.floor(L(l)/3)))*3,k=Math.pow(10,-g),v=yn[8+g/3];return function(N){return p(k*N)+v}}return{format:s,formatPrefix:c}}var D,Ln,Hn;ot({thousands:",",grouping:[3],currency:["$",""]});function ot(n){return D=ft(n),Ln=D.format,Hn=D.formatPrefix,D}function ut(n){return Math.max(0,-L(Math.abs(n)))}function st(n,t){return Math.max(0,Math.max(-8,Math.min(8,Math.floor(L(t)/3)))*3-L(Math.abs(n)))}function ht(n,t){return n=Math.abs(n),t=Math.abs(t)-n,Math.max(0,L(t)-L(n))+1}const rn=Math.PI,an=2*rn,S=1e-6,ct=an-S;function fn(){this._x0=this._y0=this._x1=this._y1=null,this._=""}function In(){return new fn}fn.prototype=In.prototype={constructor:fn,moveTo:function(n,t){this._+="M"+(this._x0=this._x1=+n)+","+(this._y0=this._y1=+t)},closePath:function(){this._x1!==null&&(this._x1=this._x0,this._y1=this._y0,this._+="Z")},lineTo:function(n,t){this._+="L"+(this._x1=+n)+","+(this._y1=+t)},quadraticCurveTo:function(n,t,e,r){this._+="Q"+ +n+","+ +t+","+(this._x1=+e)+","+(this._y1=+r)},bezierCurveTo:function(n,t,e,r,i,f){this._+="C"+ +n+","+ +t+","+ +e+","+ +r+","+(this._x1=+i)+","+(this._y1=+f)},arcTo:function(n,t,e,r,i){n=+n,t=+t,e=+e,r=+r,i=+i;var f=this._x1,o=this._y1,a=e-n,u=r-t,s=f-n,c=o-t,h=s*s+c*c;if(i<0)throw new Error("negative radius: "+i);if(this._x1===null)this._+="M"+(this._x1=n)+","+(this._y1=t);else if(h>S)if(!(Math.abs(c*a-u*s)>S)||!i)this._+="L"+(this._x1=n)+","+(this._y1=t);else{var l=e-f,p=r-o,g=a*a+u*u,k=l*l+p*p,v=Math.sqrt(g),N=Math.sqrt(h),R=i*Math.tan((rn-Math.acos((g+h-k)/(2*v*N)))/2),y=R/N,H=R/v;Math.abs(y-1)>S&&(this._+="L"+(n+y*s)+","+(t+y*c)),this._+="A"+i+","+i+",0,0,"+ +(c*l>s*p)+","+(this._x1=n+H*a)+","+(this._y1=t+H*u)}},arc:function(n,t,e,r,i,f){n=+n,t=+t,e=+e,f=!!f;var o=e*Math.cos(r),a=e*Math.sin(r),u=n+o,s=t+a,c=1^f,h=f?r-i:i-r;if(e<0)throw new Error("negative radius: "+e);this._x1===null?this._+="M"+u+","+s:(Math.abs(this._x1-u)>S||Math.abs(this._y1-s)>S)&&(this._+="L"+u+","+s),e&&(h<0&&(h=h%an+an),h>ct?this._+="A"+e+","+e+",0,1,"+c+","+(n-o)+","+(t-a)+"A"+e+","+e+",0,1,"+c+","+(this._x1=u)+","+(this._y1=s):h>S&&(this._+="A"+e+","+e+",0,"+ +(h>=rn)+","+c+","+(this._x1=n+e*Math.cos(i))+","+(this._y1=t+e*Math.sin(i))))},rect:function(n,t,e,r){this._+="M"+(this._x0=this._x1=+n)+","+(this._y0=this._y1=+t)+"h"+ +e+"v"+ +r+"h"+-e+"Z"},toString:function(){return this._}};function P(n){return function(){return n}}function lt(n){return typeof n=="object"&&"length"in n?n:Array.from(n)}function Tn(n){this._context=n}Tn.prototype={areaStart:function(){this._line=0},areaEnd:function(){this._line=NaN},lineStart:function(){this._point=0},lineEnd:function(){(this._line||this._line!==0&&this._point===1)&&this._context.closePath(),this._line=1-this._line},point:function(n,t){switch(n=+n,t=+t,this._point){case 0:this._point=1,this._line?this._context.lineTo(n,t):this._context.moveTo(n,t);break;case 1:this._point=2;default:this._context.lineTo(n,t);break}}};function dt(n){return new Tn(n)}function gt(n){return n[0]}function xt(n){return n[1]}function Yt(n,t){var e=P(!0),r=null,i=dt,f=null;n=typeof n=="function"?n:n===void 0?gt:P(n),t=typeof t=="function"?t:t===void 0?xt:P(t);function o(a){var u,s=(a=lt(a)).length,c,h=!1,l;for(r==null&&(f=i(l=In())),u=0;u<=s;++u)!(u<s&&e(c=a[u],u,a))===h&&((h=!h)?f.lineStart():f.lineEnd()),h&&f.point(+n(c,u,a),+t(c,u,a));if(l)return f=null,l+""||null}return o.x=function(a){return arguments.length?(n=typeof a=="function"?a:P(+a),o):n},o.y=function(a){return arguments.length?(t=typeof a=="function"?a:P(+a),o):t},o.defined=function(a){return arguments.length?(e=typeof a=="function"?a:P(!!a),o):e},o.curve=function(a){return arguments.length?(i=a,r!=null&&(f=i(r)),o):i},o.context=function(a){return arguments.length?(a==null?r=f=null:f=i(r=a),o):r},o}function mt(n,t){switch(arguments.length){case 0:break;case 1:this.range(n);break;default:this.range(t).domain(n);break}return this}function Jt(n,t){switch(arguments.length){case 0:break;case 1:{typeof n=="function"?this.interpolator(n):this.range(n);break}default:{this.domain(n),typeof t=="function"?this.interpolator(t):this.range(t);break}}return this}function hn(n,t,e){n.prototype=t.prototype=e,e.constructor=n}function zn(n,t){var e=Object.create(n.prototype);for(var r in t)e[r]=t[r];return e}function C(){}var I=.7,V=1/I,q="\\s*([+-]?\\d+)\\s*",T="\\s*([+-]?\\d*\\.?\\d+(?:[eE][+-]?\\d+)?)\\s*",M="\\s*([+-]?\\d*\\.?\\d+(?:[eE][+-]?\\d+)?)%\\s*",bt=/^#([0-9a-f]{3,8})$/,pt=new RegExp("^rgb\\("+[q,q,q]+"\\)$"),yt=new RegExp("^rgb\\("+[M,M,M]+"\\)$"),wt=new RegExp("^rgba\\("+[q,q,q,T]+"\\)$"),Mt=new RegExp("^rgba\\("+[M,M,M,T]+"\\)$"),vt=new RegExp("^hsl\\("+[T,M,M]+"\\)$"),_t=new RegExp("^hsla\\("+[T,M,M,T]+"\\)$"),wn={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074};hn(C,z,{copy:function(n){return Object.assign(new this.constructor,this,n)},displayable:function(){return this.rgb().displayable()},hex:Mn,formatHex:Mn,formatHsl:Nt,formatRgb:vn,toString:vn});function Mn(){return this.rgb().formatHex()}function Nt(){return Cn(this).formatHsl()}function vn(){return this.rgb().formatRgb()}function z(n){var t,e;return n=(n+"").trim().toLowerCase(),(t=bt.exec(n))?(e=t[1].length,t=parseInt(t[1],16),e===6?_n(t):e===3?new x(t>>8&15|t>>4&240,t>>4&15|t&240,(t&15)<<4|t&15,1):e===8?O(t>>24&255,t>>16&255,t>>8&255,(t&255)/255):e===4?O(t>>12&15|t>>8&240,t>>8&15|t>>4&240,t>>4&15|t&240,((t&15)<<4|t&15)/255):null):(t=pt.exec(n))?new x(t[1],t[2],t[3],1):(t=yt.exec(n))?new x(t[1]*255/100,t[2]*255/100,t[3]*255/100,1):(t=wt.exec(n))?O(t[1],t[2],t[3],t[4]):(t=Mt.exec(n))?O(t[1]*255/100,t[2]*255/100,t[3]*255/100,t[4]):(t=vt.exec(n))?An(t[1],t[2]/100,t[3]/100,1):(t=_t.exec(n))?An(t[1],t[2]/100,t[3]/100,t[4]):wn.hasOwnProperty(n)?_n(wn[n]):n==="transparent"?new x(NaN,NaN,NaN,0):null}function _n(n){return new x(n>>16&255,n>>8&255,n&255,1)}function O(n,t,e,r){return r<=0&&(n=t=e=NaN),new x(n,t,e,r)}function kt(n){return n instanceof C||(n=z(n)),n?(n=n.rgb(),new x(n.r,n.g,n.b,n.opacity)):new x}function X(n,t,e,r){return arguments.length===1?kt(n):new x(n,t,e,r??1)}function x(n,t,e,r){this.r=+n,this.g=+t,this.b=+e,this.opacity=+r}hn(x,X,zn(C,{brighter:function(n){return n=n==null?V:Math.pow(V,n),new x(this.r*n,this.g*n,this.b*n,this.opacity)},darker:function(n){return n=n==null?I:Math.pow(I,n),new x(this.r*n,this.g*n,this.b*n,this.opacity)},rgb:function(){return this},displayable:function(){return-.5<=this.r&&this.r<255.5&&-.5<=this.g&&this.g<255.5&&-.5<=this.b&&this.b<255.5&&0<=this.opacity&&this.opacity<=1},hex:Nn,formatHex:Nn,formatRgb:kn,toString:kn}));function Nn(){return"#"+Y(this.r)+Y(this.g)+Y(this.b)}function kn(){var n=this.opacity;return n=isNaN(n)?1:Math.max(0,Math.min(1,n)),(n===1?"rgb(":"rgba(")+Math.max(0,Math.min(255,Math.round(this.r)||0))+", "+Math.max(0,Math.min(255,Math.round(this.g)||0))+", "+Math.max(0,Math.min(255,Math.round(this.b)||0))+(n===1?")":", "+n+")")}function Y(n){return n=Math.max(0,Math.min(255,Math.round(n)||0)),(n<16?"0":"")+n.toString(16)}function An(n,t,e,r){return r<=0?n=t=e=NaN:e<=0||e>=1?n=t=NaN:t<=0&&(n=NaN),new w(n,t,e,r)}function Cn(n){if(n instanceof w)return new w(n.h,n.s,n.l,n.opacity);if(n instanceof C||(n=z(n)),!n)return new w;if(n instanceof w)return n;n=n.rgb();var t=n.r/255,e=n.g/255,r=n.b/255,i=Math.min(t,e,r),f=Math.max(t,e,r),o=NaN,a=f-i,u=(f+i)/2;return a?(t===f?o=(e-r)/a+(e<r)*6:e===f?o=(r-t)/a+2:o=(t-e)/a+4,a/=u<.5?f+i:2-f-i,o*=60):a=u>0&&u<1?0:o,new w(o,a,u,n.opacity)}function At(n,t,e,r){return arguments.length===1?Cn(n):new w(n,t,e,r??1)}function w(n,t,e,r){this.h=+n,this.s=+t,this.l=+e,this.opacity=+r}hn(w,At,zn(C,{brighter:function(n){return n=n==null?V:Math.pow(V,n),new w(this.h,this.s,this.l*n,this.opacity)},darker:function(n){return n=n==null?I:Math.pow(I,n),new w(this.h,this.s,this.l*n,this.opacity)},rgb:function(){var n=this.h%360+(this.h<0)*360,t=isNaN(n)||isNaN(this.s)?0:this.s,e=this.l,r=e+(e<.5?e:1-e)*t,i=2*e-r;return new x(J(n>=240?n-240:n+120,i,r),J(n,i,r),J(n<120?n+240:n-120,i,r),this.opacity)},displayable:function(){return(0<=this.s&&this.s<=1||isNaN(this.s))&&0<=this.l&&this.l<=1&&0<=this.opacity&&this.opacity<=1},formatHsl:function(){var n=this.opacity;return n=isNaN(n)?1:Math.max(0,Math.min(1,n)),(n===1?"hsl(":"hsla(")+(this.h||0)+", "+(this.s||0)*100+"%, "+(this.l||0)*100+"%"+(n===1?")":", "+n+")")}}));function J(n,t,e){return(n<60?t+(e-t)*n/60:n<180?e:n<240?t+(e-t)*(240-n)/60:t)*255}function Fn(n,t,e,r,i){var f=n*n,o=f*n;return((1-3*n+3*f-o)*t+(4-6*f+3*o)*e+(1+3*n+3*f-3*o)*r+o*i)/6}function St(n){var t=n.length-1;return function(e){var r=e<=0?e=0:e>=1?(e=1,t-1):Math.floor(e*t),i=n[r],f=n[r+1],o=r>0?n[r-1]:2*i-f,a=r<t-1?n[r+2]:2*f-i;return Fn((e-r/t)*t,o,i,f,a)}}function Rt(n){var t=n.length;return function(e){var r=Math.floor(((e%=1)<0?++e:e)*t),i=n[(r+t-1)%t],f=n[r%t],o=n[(r+1)%t],a=n[(r+2)%t];return Fn((e-r/t)*t,i,f,o,a)}}const U=n=>()=>n;function $n(n,t){return function(e){return n+e*t}}function Et(n,t,e){return n=Math.pow(n,e),t=Math.pow(t,e)-n,e=1/e,function(r){return Math.pow(n+r*t,e)}}function Kt(n,t){var e=t-n;return e?$n(n,e>180||e<-180?e-360*Math.round(e/360):e):U(isNaN(n)?t:n)}function Pt(n){return(n=+n)==1?Bn:function(t,e){return e-t?Et(t,e,n):U(isNaN(t)?e:t)}}function Bn(n,t){var e=t-n;return e?$n(n,e):U(isNaN(n)?t:n)}const Sn=function n(t){var e=Pt(t);function r(i,f){var o=e((i=X(i)).r,(f=X(f)).r),a=e(i.g,f.g),u=e(i.b,f.b),s=Bn(i.opacity,f.opacity);return function(c){return i.r=o(c),i.g=a(c),i.b=u(c),i.opacity=s(c),i+""}}return r.gamma=n,r}(1);function Dn(n){return function(t){var e=t.length,r=new Array(e),i=new Array(e),f=new Array(e),o,a;for(o=0;o<e;++o)a=X(t[o]),r[o]=a.r||0,i[o]=a.g||0,f[o]=a.b||0;return r=n(r),i=n(i),f=n(f),a.opacity=1,function(u){return a.r=r(u),a.g=i(u),a.b=f(u),a+""}}}var Wt=Dn(St),ne=Dn(Rt);function On(n,t){t||(t=[]);var e=n?Math.min(t.length,n.length):0,r=t.slice(),i;return function(f){for(i=0;i<e;++i)r[i]=n[i]*(1-f)+t[i]*f;return r}}function Gn(n){return ArrayBuffer.isView(n)&&!(n instanceof DataView)}function te(n,t){return(Gn(t)?On:Zn)(n,t)}function Zn(n,t){var e=t?t.length:0,r=n?Math.min(e,n.length):0,i=new Array(r),f=new Array(e),o;for(o=0;o<r;++o)i[o]=cn(n[o],t[o]);for(;o<e;++o)f[o]=t[o];return function(a){for(o=0;o<r;++o)f[o]=i[o](a);return f}}function jt(n,t){var e=new Date;return n=+n,t=+t,function(r){return e.setTime(n*(1-r)+t*r),e}}function Q(n,t){return n=+n,t=+t,function(e){return n*(1-e)+t*e}}function qt(n,t){var e={},r={},i;(n===null||typeof n!="object")&&(n={}),(t===null||typeof t!="object")&&(t={});for(i in t)i in n?e[i]=cn(n[i],t[i]):r[i]=t[i];return function(f){for(i in e)r[i]=e[i](f);return r}}var on=/[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g,K=new RegExp(on.source,"g");function Lt(n){return function(){return n}}function Ht(n){return function(t){return n(t)+""}}function It(n,t){var e=on.lastIndex=K.lastIndex=0,r,i,f,o=-1,a=[],u=[];for(n=n+"",t=t+"";(r=on.exec(n))&&(i=K.exec(t));)(f=i.index)>e&&(f=t.slice(e,f),a[o]?a[o]+=f:a[++o]=f),(r=r[0])===(i=i[0])?a[o]?a[o]+=i:a[++o]=i:(a[++o]=null,u.push({i:o,x:Q(r,i)})),e=K.lastIndex;return e<t.length&&(f=t.slice(e),a[o]?a[o]+=f:a[++o]=f),a.length<2?u[0]?Ht(u[0].x):Lt(t):(t=u.length,function(s){for(var c=0,h;c<t;++c)a[(h=u[c]).i]=h.x(s);return a.join("")})}function cn(n,t){var e=typeof t,r;return t==null||e==="boolean"?U(t):(e==="number"?Q:e==="string"?(r=z(t))?(t=r,Sn):It:t instanceof z?Sn:t instanceof Date?jt:Gn(t)?On:Array.isArray(t)?Zn:typeof t.valueOf!="function"&&typeof t.toString!="function"||isNaN(t)?qt:Q)(n,t)}function Tt(n,t){return n=+n,t=+t,function(e){return Math.round(n*(1-e)+t*e)}}function zt(n){return function(){return n}}function Ct(n){return+n}var Rn=[0,1];function j(n){return n}function un(n,t){return(t-=n=+n)?function(e){return(e-n)/t}:zt(isNaN(t)?NaN:.5)}function Ft(n,t){var e;return n>t&&(e=n,n=t,t=e),function(r){return Math.max(n,Math.min(t,r))}}function $t(n,t,e){var r=n[0],i=n[1],f=t[0],o=t[1];return i<r?(r=un(i,r),f=e(o,f)):(r=un(r,i),f=e(f,o)),function(a){return f(r(a))}}function Bt(n,t,e){var r=Math.min(n.length,t.length)-1,i=new Array(r),f=new Array(r),o=-1;for(n[r]<n[0]&&(n=n.slice().reverse(),t=t.slice().reverse());++o<r;)i[o]=un(n[o],n[o+1]),f[o]=e(t[o],t[o+1]);return function(a){var u=Jn(n,a,1,r)-1;return f[u](i[u](a))}}function Dt(n,t){return t.domain(n.domain()).range(n.range()).interpolate(n.interpolate()).clamp(n.clamp()).unknown(n.unknown())}function Ot(){var n=Rn,t=Rn,e=cn,r,i,f,o=j,a,u,s;function c(){var l=Math.min(n.length,t.length);return o!==j&&(o=Ft(n[0],n[l-1])),a=l>2?Bt:$t,u=s=null,h}function h(l){return l==null||isNaN(l=+l)?f:(u||(u=a(n.map(r),t,e)))(r(o(l)))}return h.invert=function(l){return o(i((s||(s=a(t,n.map(r),Q)))(l)))},h.domain=function(l){return arguments.length?(n=Array.from(l,Ct),c()):n.slice()},h.range=function(l){return arguments.length?(t=Array.from(l),c()):t.slice()},h.rangeRound=function(l){return t=Array.from(l),e=Tt,c()},h.clamp=function(l){return arguments.length?(o=l?!0:j,c()):o!==j},h.interpolate=function(l){return arguments.length?(e=l,c()):e},h.unknown=function(l){return arguments.length?(f=l,h):f},function(l,p){return r=l,i=p,c()}}function Gt(){return Ot()(j,j)}function Zt(n,t,e,r){var i=Wn(n,t,e),f;switch(r=Z(r??",f"),r.type){case"s":{var o=Math.max(Math.abs(n),Math.abs(t));return r.precision==null&&!isNaN(f=st(i,o))&&(r.precision=f),Hn(r,o)}case"":case"e":case"g":case"p":case"r":{r.precision==null&&!isNaN(f=ht(i,Math.max(Math.abs(n),Math.abs(t))))&&(r.precision=f-(r.type==="e"));break}case"f":case"%":{r.precision==null&&!isNaN(f=ut(i))&&(r.precision=f-(r.type==="%")*2);break}}return Ln(r)}function Vt(n){var t=n.domain;return n.ticks=function(e){var r=t();return Kn(r[0],r[r.length-1],e??10)},n.tickFormat=function(e,r){var i=t();return Zt(i[0],i[i.length-1],e??10,r)},n.nice=function(e){e==null&&(e=10);var r=t(),i=0,f=r.length-1,o=r[i],a=r[f],u,s,c=10;for(a<o&&(s=o,o=a,a=s,s=i,i=f,f=s);c-- >0;){if(s=jn(o,a,e),s===u)return r[i]=o,r[f]=a,t(r);if(s>0)o=Math.floor(o/s)*s,a=Math.ceil(a/s)*s;else if(s<0)o=Math.ceil(o*s)/s,a=Math.floor(a*s)/s;else break;u=s}return n},n}function Xt(){var n=Gt();return n.copy=function(){return Dt(n,Xt())},mt.apply(n,arguments),Vt(n)}export{Yn as $,At as A,Bn as B,C,cn as D,te as E,St as F,Rt as G,jt as H,On as I,qt as J,Sn as K,Wt as L,ne as M,Tt as N,It as O,Ct as P,Vt as Q,x as R,Ot as S,Dt as T,Kn as U,j as V,Jn as W,Gt as X,Jt as Y,Xt as Z,Yt as _,W as a,Zt as a0,X as a1,Ut as a2,Un as b,En as c,ht as d,st as e,Z as f,Ln as g,Hn as h,ft as i,P as j,In as k,dt as l,lt as m,Qt as n,mt as o,ut as p,hn as q,kt as r,zn as s,Wn as t,V as u,I as v,Kt as w,gt as x,xt as y,Q as z};
//# sourceMappingURL=linear-58a44b5e.js.map

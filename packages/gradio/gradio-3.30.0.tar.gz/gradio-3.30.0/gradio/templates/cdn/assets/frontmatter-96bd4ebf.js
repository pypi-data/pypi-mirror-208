import{s as m,f as s,a as i,p,t as a,S as l}from"./index-ce99cbac.js";import{yaml as f}from"./yaml-95012b83.js";import"./index-7da4454e.js";import"./Blocks-cda355f2.js";import"./Button-6ea4ac43.js";import"./BlockLabel-1f250d5e.js";import"./Empty-0c822ba8.js";/* empty css                                                    */import"./Copy-cd6d6056.js";import"./Download-e1dbb2d4.js";const n=/^---\s*$/m,b={defineNodes:[{name:"Frontmatter",block:!0},"FrontmatterMark"],props:[m({Frontmatter:[a.documentMeta,a.monospace],FrontmatterMark:a.processingInstruction}),s.add({Frontmatter:i,FrontmatterMark:()=>null})],wrap:p(t=>{const{parser:e}=l.define(f);return t.type.name==="Frontmatter"?{parser:e,overlay:[{from:t.from+4,to:t.to-4}]}:null}),parseBlock:[{name:"Frontmatter",before:"HorizontalRule",parse:(t,e)=>{let r;const o=new Array;if(t.lineStart===0&&n.test(e.text)){for(o.push(t.elt("FrontmatterMark",0,4));t.nextLine();)if(n.test(e.text)){r=t.lineStart+4;break}return r!==void 0&&(o.push(t.elt("FrontmatterMark",r-4,r)),t.addElement(t.elt("Frontmatter",0,r,o))),!0}else return!1}}]};export{b as frontmatter};
//# sourceMappingURL=frontmatter-96bd4ebf.js.map

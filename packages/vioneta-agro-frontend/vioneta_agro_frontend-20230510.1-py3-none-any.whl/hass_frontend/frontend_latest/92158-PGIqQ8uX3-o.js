/*! For license information please see 92158-PGIqQ8uX3-o.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[92158],{18601:(e,t,l)=>{l.d(t,{Wg:()=>f,qN:()=>a.q});var n,i,s=l(87480),o=l(79932),a=l(78220);const r=null!==(i=null===(n=window.ShadyDOM)||void 0===n?void 0:n.inUse)&&void 0!==i&&i;class f extends a.H{constructor(){super(...arguments),this.disabled=!1,this.containingForm=null,this.formDataListener=e=>{this.disabled||this.setFormData(e.formData)}}findFormElement(){if(!this.shadowRoot||r)return null;const e=this.getRootNode().querySelectorAll("form");for(const t of Array.from(e))if(t.contains(this))return t;return null}connectedCallback(){var e;super.connectedCallback(),this.containingForm=this.findFormElement(),null===(e=this.containingForm)||void 0===e||e.addEventListener("formdata",this.formDataListener)}disconnectedCallback(){var e;super.disconnectedCallback(),null===(e=this.containingForm)||void 0===e||e.removeEventListener("formdata",this.formDataListener),this.containingForm=null}click(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}firstUpdated(){super.firstUpdated(),this.shadowRoot&&this.mdcRoot.addEventListener("change",(e=>{this.dispatchEvent(new Event("change",e))}))}}f.shadowRootOptions={mode:"open",delegatesFocus:!0},(0,s.__decorate)([(0,o.Cb)({type:Boolean})],f.prototype,"disabled",void 0)},21157:(e,t,l)=>{l(88441);const n=l(50856).d`
/* Most common used flex styles*/
<dom-module id="iron-flex">
  <template>
    <style>
      .layout.horizontal,
      .layout.vertical {
        display: -ms-flexbox;
        display: -webkit-flex;
        display: flex;
      }

      .layout.inline {
        display: -ms-inline-flexbox;
        display: -webkit-inline-flex;
        display: inline-flex;
      }

      .layout.horizontal {
        -ms-flex-direction: row;
        -webkit-flex-direction: row;
        flex-direction: row;
      }

      .layout.vertical {
        -ms-flex-direction: column;
        -webkit-flex-direction: column;
        flex-direction: column;
      }

      .layout.wrap {
        -ms-flex-wrap: wrap;
        -webkit-flex-wrap: wrap;
        flex-wrap: wrap;
      }

      .layout.no-wrap {
        -ms-flex-wrap: nowrap;
        -webkit-flex-wrap: nowrap;
        flex-wrap: nowrap;
      }

      .layout.center,
      .layout.center-center {
        -ms-flex-align: center;
        -webkit-align-items: center;
        align-items: center;
      }

      .layout.center-justified,
      .layout.center-center {
        -ms-flex-pack: center;
        -webkit-justify-content: center;
        justify-content: center;
      }

      .flex {
        -ms-flex: 1 1 0.000000001px;
        -webkit-flex: 1;
        flex: 1;
        -webkit-flex-basis: 0.000000001px;
        flex-basis: 0.000000001px;
      }

      .flex-auto {
        -ms-flex: 1 1 auto;
        -webkit-flex: 1 1 auto;
        flex: 1 1 auto;
      }

      .flex-none {
        -ms-flex: none;
        -webkit-flex: none;
        flex: none;
      }
    </style>
  </template>
</dom-module>
/* Basic flexbox reverse styles */
<dom-module id="iron-flex-reverse">
  <template>
    <style>
      .layout.horizontal-reverse,
      .layout.vertical-reverse {
        display: -ms-flexbox;
        display: -webkit-flex;
        display: flex;
      }

      .layout.horizontal-reverse {
        -ms-flex-direction: row-reverse;
        -webkit-flex-direction: row-reverse;
        flex-direction: row-reverse;
      }

      .layout.vertical-reverse {
        -ms-flex-direction: column-reverse;
        -webkit-flex-direction: column-reverse;
        flex-direction: column-reverse;
      }

      .layout.wrap-reverse {
        -ms-flex-wrap: wrap-reverse;
        -webkit-flex-wrap: wrap-reverse;
        flex-wrap: wrap-reverse;
      }
    </style>
  </template>
</dom-module>
/* Flexbox alignment */
<dom-module id="iron-flex-alignment">
  <template>
    <style>
      /**
       * Alignment in cross axis.
       */
      .layout.start {
        -ms-flex-align: start;
        -webkit-align-items: flex-start;
        align-items: flex-start;
      }

      .layout.center,
      .layout.center-center {
        -ms-flex-align: center;
        -webkit-align-items: center;
        align-items: center;
      }

      .layout.end {
        -ms-flex-align: end;
        -webkit-align-items: flex-end;
        align-items: flex-end;
      }

      .layout.baseline {
        -ms-flex-align: baseline;
        -webkit-align-items: baseline;
        align-items: baseline;
      }

      /**
       * Alignment in main axis.
       */
      .layout.start-justified {
        -ms-flex-pack: start;
        -webkit-justify-content: flex-start;
        justify-content: flex-start;
      }

      .layout.center-justified,
      .layout.center-center {
        -ms-flex-pack: center;
        -webkit-justify-content: center;
        justify-content: center;
      }

      .layout.end-justified {
        -ms-flex-pack: end;
        -webkit-justify-content: flex-end;
        justify-content: flex-end;
      }

      .layout.around-justified {
        -ms-flex-pack: distribute;
        -webkit-justify-content: space-around;
        justify-content: space-around;
      }

      .layout.justified {
        -ms-flex-pack: justify;
        -webkit-justify-content: space-between;
        justify-content: space-between;
      }

      /**
       * Self alignment.
       */
      .self-start {
        -ms-align-self: flex-start;
        -webkit-align-self: flex-start;
        align-self: flex-start;
      }

      .self-center {
        -ms-align-self: center;
        -webkit-align-self: center;
        align-self: center;
      }

      .self-end {
        -ms-align-self: flex-end;
        -webkit-align-self: flex-end;
        align-self: flex-end;
      }

      .self-stretch {
        -ms-align-self: stretch;
        -webkit-align-self: stretch;
        align-self: stretch;
      }

      .self-baseline {
        -ms-align-self: baseline;
        -webkit-align-self: baseline;
        align-self: baseline;
      }

      /**
       * multi-line alignment in main axis.
       */
      .layout.start-aligned {
        -ms-flex-line-pack: start;  /* IE10 */
        -ms-align-content: flex-start;
        -webkit-align-content: flex-start;
        align-content: flex-start;
      }

      .layout.end-aligned {
        -ms-flex-line-pack: end;  /* IE10 */
        -ms-align-content: flex-end;
        -webkit-align-content: flex-end;
        align-content: flex-end;
      }

      .layout.center-aligned {
        -ms-flex-line-pack: center;  /* IE10 */
        -ms-align-content: center;
        -webkit-align-content: center;
        align-content: center;
      }

      .layout.between-aligned {
        -ms-flex-line-pack: justify;  /* IE10 */
        -ms-align-content: space-between;
        -webkit-align-content: space-between;
        align-content: space-between;
      }

      .layout.around-aligned {
        -ms-flex-line-pack: distribute;  /* IE10 */
        -ms-align-content: space-around;
        -webkit-align-content: space-around;
        align-content: space-around;
      }
    </style>
  </template>
</dom-module>
/* Non-flexbox positioning helper styles */
<dom-module id="iron-flex-factors">
  <template>
    <style>
      .flex,
      .flex-1 {
        -ms-flex: 1 1 0.000000001px;
        -webkit-flex: 1;
        flex: 1;
        -webkit-flex-basis: 0.000000001px;
        flex-basis: 0.000000001px;
      }

      .flex-2 {
        -ms-flex: 2;
        -webkit-flex: 2;
        flex: 2;
      }

      .flex-3 {
        -ms-flex: 3;
        -webkit-flex: 3;
        flex: 3;
      }

      .flex-4 {
        -ms-flex: 4;
        -webkit-flex: 4;
        flex: 4;
      }

      .flex-5 {
        -ms-flex: 5;
        -webkit-flex: 5;
        flex: 5;
      }

      .flex-6 {
        -ms-flex: 6;
        -webkit-flex: 6;
        flex: 6;
      }

      .flex-7 {
        -ms-flex: 7;
        -webkit-flex: 7;
        flex: 7;
      }

      .flex-8 {
        -ms-flex: 8;
        -webkit-flex: 8;
        flex: 8;
      }

      .flex-9 {
        -ms-flex: 9;
        -webkit-flex: 9;
        flex: 9;
      }

      .flex-10 {
        -ms-flex: 10;
        -webkit-flex: 10;
        flex: 10;
      }

      .flex-11 {
        -ms-flex: 11;
        -webkit-flex: 11;
        flex: 11;
      }

      .flex-12 {
        -ms-flex: 12;
        -webkit-flex: 12;
        flex: 12;
      }
    </style>
  </template>
</dom-module>
<dom-module id="iron-positioning">
  <template>
    <style>
      .block {
        display: block;
      }

      [hidden] {
        display: none !important;
      }

      .invisible {
        visibility: hidden !important;
      }

      .relative {
        position: relative;
      }

      .fit {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
      }

      body.fullbleed {
        margin: 0;
        height: 100vh;
      }

      .scroll {
        -webkit-overflow-scrolling: touch;
        overflow: auto;
      }

      /* fixed position */
      .fixed-bottom,
      .fixed-left,
      .fixed-right,
      .fixed-top {
        position: fixed;
      }

      .fixed-top {
        top: 0;
        left: 0;
        right: 0;
      }

      .fixed-right {
        top: 0;
        right: 0;
        bottom: 0;
      }

      .fixed-bottom {
        right: 0;
        bottom: 0;
        left: 0;
      }

      .fixed-left {
        top: 0;
        bottom: 0;
        left: 0;
      }
    </style>
  </template>
</dom-module>
`;n.setAttribute("style","display: none;"),document.head.appendChild(n.content)},82160:(e,t,l)=>{function n(e){return new Promise(((t,l)=>{e.oncomplete=e.onsuccess=()=>t(e.result),e.onabort=e.onerror=()=>l(e.error)}))}function i(e,t){const l=indexedDB.open(e);l.onupgradeneeded=()=>l.result.createObjectStore(t);const i=n(l);return(e,l)=>i.then((n=>l(n.transaction(t,e).objectStore(t))))}let s;function o(){return s||(s=i("keyval-store","keyval")),s}function a(e,t=o()){return t("readonly",(t=>n(t.get(e))))}function r(e,t,l=o()){return l("readwrite",(l=>(l.put(t,e),n(l.transaction))))}function f(e=o()){return e("readwrite",(e=>(e.clear(),n(e.transaction))))}l.d(t,{MT:()=>i,RV:()=>n,U2:()=>a,ZH:()=>f,t8:()=>r})},81563:(e,t,l)=>{l.d(t,{E_:()=>p,OR:()=>a,_Y:()=>f,fk:()=>c,hN:()=>o,hl:()=>x,i9:()=>u,pt:()=>s,ws:()=>m});var n=l(15304);const{I:i}=n.Al,s=e=>null===e||"object"!=typeof e&&"function"!=typeof e,o=(e,t)=>void 0===t?void 0!==(null==e?void 0:e._$litType$):(null==e?void 0:e._$litType$)===t,a=e=>void 0===e.strings,r=()=>document.createComment(""),f=(e,t,l)=>{var n;const s=e._$AA.parentNode,o=void 0===t?e._$AB:t._$AA;if(void 0===l){const t=s.insertBefore(r(),o),n=s.insertBefore(r(),o);l=new i(t,n,e,e.options)}else{const t=l._$AB.nextSibling,i=l._$AM,a=i!==e;if(a){let t;null===(n=l._$AQ)||void 0===n||n.call(l,e),l._$AM=e,void 0!==l._$AP&&(t=e._$AU)!==i._$AU&&l._$AP(t)}if(t!==o||a){let e=l._$AA;for(;e!==t;){const t=e.nextSibling;s.insertBefore(e,o),e=t}}}return l},c=(e,t,l=e)=>(e._$AI(t,l),e),d={},x=(e,t=d)=>e._$AH=t,u=e=>e._$AH,m=e=>{var t;null===(t=e._$AP)||void 0===t||t.call(e,!1,!0);let l=e._$AA;const n=e._$AB.nextSibling;for(;l!==n;){const e=l.nextSibling;l.remove(),l=e}},p=e=>{e._$AR()}},57835:(e,t,l)=>{l.d(t,{XM:()=>n.XM,Xe:()=>n.Xe,pX:()=>n.pX});var n=l(38941)},18848:(e,t,l)=>{l.d(t,{r:()=>a});var n=l(15304),i=l(38941),s=l(81563);const o=(e,t,l)=>{const n=new Map;for(let i=t;i<=l;i++)n.set(e[i],i);return n},a=(0,i.XM)(class extends i.Xe{constructor(e){if(super(e),e.type!==i.pX.CHILD)throw Error("repeat() can only be used in text expressions")}ht(e,t,l){let n;void 0===l?l=t:void 0!==t&&(n=t);const i=[],s=[];let o=0;for(const t of e)i[o]=n?n(t,o):o,s[o]=l(t,o),o++;return{values:s,keys:i}}render(e,t,l){return this.ht(e,t,l).values}update(e,[t,l,i]){var a;const r=(0,s.i9)(e),{values:f,keys:c}=this.ht(t,l,i);if(!Array.isArray(r))return this.ut=c,f;const d=null!==(a=this.ut)&&void 0!==a?a:this.ut=[],x=[];let u,m,p=0,b=r.length-1,w=0,y=f.length-1;for(;p<=b&&w<=y;)if(null===r[p])p++;else if(null===r[b])b--;else if(d[p]===c[w])x[w]=(0,s.fk)(r[p],f[w]),p++,w++;else if(d[b]===c[y])x[y]=(0,s.fk)(r[b],f[y]),b--,y--;else if(d[p]===c[y])x[y]=(0,s.fk)(r[p],f[y]),(0,s._Y)(e,x[y+1],r[p]),p++,y--;else if(d[b]===c[w])x[w]=(0,s.fk)(r[b],f[w]),(0,s._Y)(e,r[p],r[b]),b--,w++;else if(void 0===u&&(u=o(c,w,y),m=o(d,p,b)),u.has(d[p]))if(u.has(d[b])){const t=m.get(c[w]),l=void 0!==t?r[t]:null;if(null===l){const t=(0,s._Y)(e,r[p]);(0,s.fk)(t,f[w]),x[w]=t}else x[w]=(0,s.fk)(l,f[w]),(0,s._Y)(e,r[p],l),r[t]=null;w++}else(0,s.ws)(r[b]),b--;else(0,s.ws)(r[p]),p++;for(;w<=y;){const t=(0,s._Y)(e,x[y+1]);(0,s.fk)(t,f[w]),x[w++]=t}for(;p<=b;){const e=r[p++];null!==e&&(0,s.ws)(e)}return this.ut=c,(0,s.hl)(e,x),n.Jb}})}}]);
//# sourceMappingURL=92158-PGIqQ8uX3-o.js.map
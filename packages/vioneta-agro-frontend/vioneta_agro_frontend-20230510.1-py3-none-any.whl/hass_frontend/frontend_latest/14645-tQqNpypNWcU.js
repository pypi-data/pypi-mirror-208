/*! For license information please see 14645-tQqNpypNWcU.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[14645],{45233:(t,e,i)=>{var o=i(68144);class n extends o.oi{static get styles(){return[o.iv`:host{display:block;position:absolute;outline:0;z-index:1002;-moz-user-select:none;-ms-user-select:none;-webkit-user-select:none;user-select:none;cursor:default}#tooltip{display:block;outline:0;font-size:var(--simple-tooltip-font-size,10px);line-height:1;background-color:var(--simple-tooltip-background,#616161);color:var(--simple-tooltip-text-color,#fff);padding:8px;border-radius:var(--simple-tooltip-border-radius,2px);width:var(--simple-tooltip-width)}@keyframes keyFrameScaleUp{0%{transform:scale(0)}100%{transform:scale(1)}}@keyframes keyFrameScaleDown{0%{transform:scale(1)}100%{transform:scale(0)}}@keyframes keyFrameFadeInOpacity{0%{opacity:0}100%{opacity:var(--simple-tooltip-opacity,.9)}}@keyframes keyFrameFadeOutOpacity{0%{opacity:var(--simple-tooltip-opacity,.9)}100%{opacity:0}}@keyframes keyFrameSlideDownIn{0%{transform:translateY(-2000px);opacity:0}10%{opacity:.2}100%{transform:translateY(0);opacity:var(--simple-tooltip-opacity,.9)}}@keyframes keyFrameSlideDownOut{0%{transform:translateY(0);opacity:var(--simple-tooltip-opacity,.9)}10%{opacity:.2}100%{transform:translateY(-2000px);opacity:0}}.fade-in-animation{opacity:0;animation-delay:var(--simple-tooltip-delay-in,500ms);animation-name:keyFrameFadeInOpacity;animation-iteration-count:1;animation-timing-function:ease-in;animation-duration:var(--simple-tooltip-duration-in,500ms);animation-fill-mode:forwards}.fade-out-animation{opacity:var(--simple-tooltip-opacity,.9);animation-delay:var(--simple-tooltip-delay-out,0ms);animation-name:keyFrameFadeOutOpacity;animation-iteration-count:1;animation-timing-function:ease-in;animation-duration:var(--simple-tooltip-duration-out,500ms);animation-fill-mode:forwards}.scale-up-animation{transform:scale(0);opacity:var(--simple-tooltip-opacity,.9);animation-delay:var(--simple-tooltip-delay-in,500ms);animation-name:keyFrameScaleUp;animation-iteration-count:1;animation-timing-function:ease-in;animation-duration:var(--simple-tooltip-duration-in,500ms);animation-fill-mode:forwards}.scale-down-animation{transform:scale(1);opacity:var(--simple-tooltip-opacity,.9);animation-delay:var(--simple-tooltip-delay-out,500ms);animation-name:keyFrameScaleDown;animation-iteration-count:1;animation-timing-function:ease-in;animation-duration:var(--simple-tooltip-duration-out,500ms);animation-fill-mode:forwards}.slide-down-animation{transform:translateY(-2000px);opacity:0;animation-delay:var(--simple-tooltip-delay-out,500ms);animation-name:keyFrameSlideDownIn;animation-iteration-count:1;animation-timing-function:cubic-bezier(0,0,.2,1);animation-duration:var(--simple-tooltip-duration-out,500ms);animation-fill-mode:forwards}.slide-down-animation-out{transform:translateY(0);opacity:var(--simple-tooltip-opacity,.9);animation-delay:var(--simple-tooltip-delay-out,500ms);animation-name:keyFrameSlideDownOut;animation-iteration-count:1;animation-timing-function:cubic-bezier(.4,0,1,1);animation-duration:var(--simple-tooltip-duration-out,500ms);animation-fill-mode:forwards}.cancel-animation{animation-delay:-30s!important}.hidden{position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden}`]}render(){return o.dy` <div id="tooltip" class="hidden" @animationend="${this._onAnimationEnd}"> <slot></slot> </div>`}static get properties(){return{...super.properties,for:{type:String},manualMode:{type:Boolean,attribute:"manual-mode"},position:{type:String},fitToVisibleBounds:{type:Boolean,attribute:"fit-to-visible-bounds"},offset:{type:Number},marginTop:{type:Number,attribute:"margin-top"},animationDelay:{type:Number,attribute:"animation-delay"},animationEntry:{type:String,attribute:"animation-entry"},animationExit:{type:String,attribute:"animation-exit"},_showing:{type:Boolean}}}static get tag(){return"simple-tooltip"}constructor(){super(),this.manualMode=!1,this.position="bottom",this.fitToVisibleBounds=!1,this.offset=14,this.marginTop=14,this.animationEntry="",this.animationExit="",this.animationConfig={entry:[{name:"fade-in-animation",node:this,timing:{delay:0}}],exit:[{name:"fade-out-animation",node:this}]},setTimeout((()=>{this.addEventListener("webkitAnimationEnd",this._onAnimationEnd.bind(this)),this.addEventListener("mouseenter",this.hide.bind(this))}),0)}get target(){var t=this.parentNode,e=this.getRootNode();return this.for?e.querySelector("#"+this.for):t.nodeType==Node.DOCUMENT_FRAGMENT_NODE?e.host:t}disconnectedCallback(){this.manualMode||this._removeListeners(),super.disconnectedCallback()}playAnimation(t){"entry"===t?this.show():"exit"===t&&this.hide()}cancelAnimation(){this.shadowRoot.querySelector("#tooltip").classList.add("cancel-animation")}show(){if(!this._showing){if(""===this.textContent.trim()){for(var t=!0,e=this.children,i=0;i<e.length;i++)if(""!==e[i].textContent.trim()){t=!1;break}if(t)return}this._showing=!0,this.shadowRoot.querySelector("#tooltip").classList.remove("hidden"),this.shadowRoot.querySelector("#tooltip").classList.remove("cancel-animation"),this.shadowRoot.querySelector("#tooltip").classList.remove(this._getAnimationType("exit")),this.updatePosition(),this._animationPlaying=!0,this.shadowRoot.querySelector("#tooltip").classList.add(this._getAnimationType("entry"))}}hide(){if(this._showing){if(this._animationPlaying)return this._showing=!1,void this._cancelAnimation();this._onAnimationFinish(),this._showing=!1,this._animationPlaying=!0,clearTimeout(this.__debounceCancel),this.__debounceCancel=setTimeout((()=>{this._cancelAnimation()}),5e3)}}updatePosition(){if(this._target&&this.offsetParent){var t=this.offset;14!=this.marginTop&&14==this.offset&&(t=this.marginTop);var e,i,o=this.offsetParent.getBoundingClientRect(),n=this._target.getBoundingClientRect(),a=this.getBoundingClientRect(),s=(n.width-a.width)/2,r=(n.height-a.height)/2,l=n.left-o.left,p=n.top-o.top;switch(this.position){case"top":e=l+s,i=p-a.height-t;break;case"bottom":e=l+s,i=p+n.height+t;break;case"left":e=l-a.width-t,i=p+r;break;case"right":e=l+n.width+t,i=p+r}this.fitToVisibleBounds?(o.left+e+a.width>window.innerWidth?(this.style.right="0px",this.style.left="auto"):(this.style.left=Math.max(0,e)+"px",this.style.right="auto"),o.top+i+a.height>window.innerHeight?(this.style.bottom=o.height-p+t+"px",this.style.top="auto"):(this.style.top=Math.max(-o.top,i)+"px",this.style.bottom="auto")):(this.style.left=e+"px",this.style.top=i+"px")}}_addListeners(){this._target&&(this._target.addEventListener("mouseenter",this.show.bind(this)),this._target.addEventListener("focus",this.show.bind(this)),this._target.addEventListener("mouseleave",this.hide.bind(this)),this._target.addEventListener("blur",this.hide.bind(this)),this._target.addEventListener("tap",this.hide.bind(this)))}_findTarget(){this.manualMode||this._removeListeners(),this._target=this.target,this.manualMode||this._addListeners()}_manualModeChanged(){this.manualMode?this._removeListeners():this._addListeners()}_cancelAnimation(){this.shadowRoot.querySelector("#tooltip").classList.remove(this._getAnimationType("entry")),this.shadowRoot.querySelector("#tooltip").classList.remove(this._getAnimationType("exit")),this.shadowRoot.querySelector("#tooltip").classList.remove("cancel-animation"),this.shadowRoot.querySelector("#tooltip").classList.add("hidden")}_onAnimationFinish(){this._showing&&(this.shadowRoot.querySelector("#tooltip").classList.remove(this._getAnimationType("entry")),this.shadowRoot.querySelector("#tooltip").classList.remove("cancel-animation"),this.shadowRoot.querySelector("#tooltip").classList.add(this._getAnimationType("exit")))}_onAnimationEnd(){this._animationPlaying=!1,this._showing||(this.shadowRoot.querySelector("#tooltip").classList.remove(this._getAnimationType("exit")),this.shadowRoot.querySelector("#tooltip").classList.add("hidden"))}_getAnimationType(t){if("entry"===t&&""!==this.animationEntry)return this.animationEntry;if("exit"===t&&""!==this.animationExit)return this.animationExit;if(this.animationConfig[t]&&"string"==typeof this.animationConfig[t][0].name){if(this.animationConfig[t][0].timing&&this.animationConfig[t][0].timing.delay&&0!==this.animationConfig[t][0].timing.delay){var e=this.animationConfig[t][0].timing.delay;"entry"===t?document.documentElement.style.setProperty("--simple-tooltip-delay-in",e+"ms"):"exit"===t&&document.documentElement.style.setProperty("--simple-tooltip-delay-out",e+"ms")}return this.animationConfig[t][0].name}}_removeListeners(){this._target&&(this._target.removeEventListener("mouseover",this.show.bind(this)),this._target.removeEventListener("focusin",this.show.bind(this)),this._target.removeEventListener("mouseout",this.hide.bind(this)),this._target.removeEventListener("focusout",this.hide.bind(this)),this._target.removeEventListener("click",this.hide.bind(this)))}firstUpdated(t){this.setAttribute("role","tooltip"),this.setAttribute("tabindex",-1),this._findTarget()}updated(t){t.forEach(((t,e)=>{"for"==e&&this._findTarget(this[e],t),"manualMode"==e&&this._manualModeChanged(this[e],t),"animationDelay"==e&&this._delayChange(this[e],t)}))}_delayChange(t){500!==t&&document.documentElement.style.setProperty("--simple-tooltip-delay-in",t+"ms")}}customElements.define(n.tag,n)},18601:(t,e,i)=>{i.d(e,{Wg:()=>p,qN:()=>r.q});var o,n,a=i(87480),s=i(79932),r=i(78220);const l=null!==(n=null===(o=window.ShadyDOM)||void 0===o?void 0:o.inUse)&&void 0!==n&&n;class p extends r.H{constructor(){super(...arguments),this.disabled=!1,this.containingForm=null,this.formDataListener=t=>{this.disabled||this.setFormData(t.formData)}}findFormElement(){if(!this.shadowRoot||l)return null;const t=this.getRootNode().querySelectorAll("form");for(const e of Array.from(t))if(e.contains(this))return e;return null}connectedCallback(){var t;super.connectedCallback(),this.containingForm=this.findFormElement(),null===(t=this.containingForm)||void 0===t||t.addEventListener("formdata",this.formDataListener)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this.containingForm)||void 0===t||t.removeEventListener("formdata",this.formDataListener),this.containingForm=null}click(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}firstUpdated(){super.firstUpdated(),this.shadowRoot&&this.mdcRoot.addEventListener("change",(t=>{this.dispatchEvent(new Event("change",t))}))}}p.shadowRootOptions={mode:"open",delegatesFocus:!0},(0,a.__decorate)([(0,s.Cb)({type:Boolean})],p.prototype,"disabled",void 0)},54040:(t,e,i)=>{var o=i(87480),n=i(79932),a=i(58417),s=i(39274);let r=class extends a.A{};r.styles=[s.W],r=(0,o.__decorate)([(0,n.Mo)("mwc-checkbox")],r)},56887:(t,e,i)=>{i.d(e,{F:()=>l});var o=i(87480),n=(i(54040),i(68144)),a=i(79932),s=i(83448),r=i(61092);class l extends r.K{constructor(){super(...arguments),this.left=!1,this.graphic="control"}render(){const t={"mdc-deprecated-list-item__graphic":this.left,"mdc-deprecated-list-item__meta":!this.left},e=this.renderText(),i=this.graphic&&"control"!==this.graphic&&!this.left?this.renderGraphic():n.dy``,o=this.hasMeta&&this.left?this.renderMeta():n.dy``,a=this.renderRipple();return n.dy` ${a} ${i} ${this.left?"":e} <span class="${(0,s.$)(t)}"> <mwc-checkbox reducedTouchTarget tabindex="${this.tabindex}" .checked="${this.selected}" ?disabled="${this.disabled}" @change="${this.onChange}"> </mwc-checkbox> </span> ${this.left?e:""} ${o}`}async onChange(t){const e=t.target;this.selected===e.checked||(this._skipPropRequest=!0,this.selected=e.checked,await this.updateComplete,this._skipPropRequest=!1)}}(0,o.__decorate)([(0,a.IO)("slot")],l.prototype,"slotElement",void 0),(0,o.__decorate)([(0,a.IO)("mwc-checkbox")],l.prototype,"checkboxElement",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],l.prototype,"left",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,reflect:!0})],l.prototype,"graphic",void 0)},21270:(t,e,i)=>{i.d(e,{W:()=>o});const o=i(68144).iv`:host(:not([twoline])){height:56px}:host(:not([left])) .mdc-deprecated-list-item__meta{height:40px;width:40px}`},51644:(t,e,i)=>{i.d(e,{$:()=>a,P:()=>s});i(88441),i(26110);var o=i(8621),n=i(87156);const a={properties:{pressed:{type:Boolean,readOnly:!0,value:!1,reflectToAttribute:!0,observer:"_pressedChanged"},toggles:{type:Boolean,value:!1,reflectToAttribute:!0},active:{type:Boolean,value:!1,notify:!0,reflectToAttribute:!0},pointerDown:{type:Boolean,readOnly:!0,value:!1},receivedFocusFromKeyboard:{type:Boolean,readOnly:!0},ariaActiveAttribute:{type:String,value:"aria-pressed",observer:"_ariaActiveAttributeChanged"}},listeners:{down:"_downHandler",up:"_upHandler",tap:"_tapHandler"},observers:["_focusChanged(focused)","_activeChanged(active, ariaActiveAttribute)"],keyBindings:{"enter:keydown":"_asyncClick","space:keydown":"_spaceKeyDownHandler","space:keyup":"_spaceKeyUpHandler"},_mouseEventRe:/^mouse/,_tapHandler:function(){this.toggles?this._userActivate(!this.active):this.active=!1},_focusChanged:function(t){this._detectKeyboardFocus(t),t||this._setPressed(!1)},_detectKeyboardFocus:function(t){this._setReceivedFocusFromKeyboard(!this.pointerDown&&t)},_userActivate:function(t){this.active!==t&&(this.active=t,this.fire("change"))},_downHandler:function(t){this._setPointerDown(!0),this._setPressed(!0),this._setReceivedFocusFromKeyboard(!1)},_upHandler:function(){this._setPointerDown(!1),this._setPressed(!1)},_spaceKeyDownHandler:function(t){var e=t.detail.keyboardEvent,i=(0,n.vz)(e).localTarget;this.isLightDescendant(i)||(e.preventDefault(),e.stopImmediatePropagation(),this._setPressed(!0))},_spaceKeyUpHandler:function(t){var e=t.detail.keyboardEvent,i=(0,n.vz)(e).localTarget;this.isLightDescendant(i)||(this.pressed&&this._asyncClick(),this._setPressed(!1))},_asyncClick:function(){this.async((function(){this.click()}),1)},_pressedChanged:function(t){this._changedButtonState()},_ariaActiveAttributeChanged:function(t,e){e&&e!=t&&this.hasAttribute(e)&&this.removeAttribute(e)},_activeChanged:function(t,e){this.toggles?this.setAttribute(this.ariaActiveAttribute,t?"true":"false"):this.removeAttribute(this.ariaActiveAttribute),this._changedButtonState()},_controlStateChanged:function(){this.disabled?this._setPressed(!1):this._changedButtonState()},_changedButtonState:function(){this._buttonStateChanged&&this._buttonStateChanged()}},s=[o.G,a]},33760:(t,e,i)=>{i.d(e,{U:()=>a});i(88441);var o=i(51644),n=i(26110);const a=[o.P,n.a,{hostAttributes:{role:"option",tabindex:"0"}}]},97968:(t,e,i)=>{i(65660),i(70019);const o=document.createElement("template");o.setAttribute("style","display: none;"),o.innerHTML="<dom-module id=\"paper-item-shared-styles\">\n  <template>\n    <style>\n      :host, .paper-item {\n        display: block;\n        position: relative;\n        min-height: var(--paper-item-min-height, 48px);\n        padding: 0px 16px;\n      }\n\n      .paper-item {\n        @apply --paper-font-subhead;\n        border:none;\n        outline: none;\n        background: white;\n        width: 100%;\n        text-align: left;\n      }\n\n      :host([hidden]), .paper-item[hidden] {\n        display: none !important;\n      }\n\n      :host(.iron-selected), .paper-item.iron-selected {\n        font-weight: var(--paper-item-selected-weight, bold);\n\n        @apply --paper-item-selected;\n      }\n\n      :host([disabled]), .paper-item[disabled] {\n        color: var(--paper-item-disabled-color, var(--disabled-text-color));\n\n        @apply --paper-item-disabled;\n      }\n\n      :host(:focus), .paper-item:focus {\n        position: relative;\n        outline: 0;\n\n        @apply --paper-item-focused;\n      }\n\n      :host(:focus):before, .paper-item:focus:before {\n        @apply --layout-fit;\n\n        background: currentColor;\n        content: '';\n        opacity: var(--dark-divider-opacity);\n        pointer-events: none;\n\n        @apply --paper-item-focused-before;\n      }\n    </style>\n  </template>\n</dom-module>",document.head.appendChild(o.content)},53973:(t,e,i)=>{i(88441),i(65660),i(97968);var o=i(9672),n=i(50856),a=i(33760);(0,o.k)({_template:n.d`
    <style include="paper-item-shared-styles">
      :host {
        @apply --layout-horizontal;
        @apply --layout-center;
        @apply --paper-font-subhead;

        @apply --paper-item;
      }
    </style>
    <slot></slot>
`,is:"paper-item",behaviors:[a.U]})},51095:(t,e,i)=>{i(88441);var o=i(23823),n=i(9672),a=i(50856);(0,n.k)({_template:a.d`
    <style>
      :host {
        display: block;
        padding: 8px 0;

        background: var(--paper-listbox-background-color, var(--primary-background-color));
        color: var(--paper-listbox-color, var(--primary-text-color));

        @apply --paper-listbox;
      }
    </style>

    <slot></slot>
`,is:"paper-listbox",behaviors:[o.i],hostAttributes:{role:"listbox"}})},70019:(t,e,i)=>{i(88441);const o=i(50856).d`<custom-style>
  <style is="custom-style">
    html {

      /* Shared Styles */
      --paper-font-common-base: {
        font-family: 'Roboto', 'Noto', sans-serif;
        -webkit-font-smoothing: antialiased;
      };

      --paper-font-common-code: {
        font-family: 'Roboto Mono', 'Consolas', 'Menlo', monospace;
        -webkit-font-smoothing: antialiased;
      };

      --paper-font-common-expensive-kerning: {
        text-rendering: optimizeLegibility;
      };

      --paper-font-common-nowrap: {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      };

      /* Material Font Styles */

      --paper-font-display4: {
        @apply --paper-font-common-base;
        @apply --paper-font-common-nowrap;

        font-size: 112px;
        font-weight: 300;
        letter-spacing: -.044em;
        line-height: 120px;
      };

      --paper-font-display3: {
        @apply --paper-font-common-base;
        @apply --paper-font-common-nowrap;

        font-size: 56px;
        font-weight: 400;
        letter-spacing: -.026em;
        line-height: 60px;
      };

      --paper-font-display2: {
        @apply --paper-font-common-base;

        font-size: 45px;
        font-weight: 400;
        letter-spacing: -.018em;
        line-height: 48px;
      };

      --paper-font-display1: {
        @apply --paper-font-common-base;

        font-size: 34px;
        font-weight: 400;
        letter-spacing: -.01em;
        line-height: 40px;
      };

      --paper-font-headline: {
        @apply --paper-font-common-base;

        font-size: 24px;
        font-weight: 400;
        letter-spacing: -.012em;
        line-height: 32px;
      };

      --paper-font-title: {
        @apply --paper-font-common-base;
        @apply --paper-font-common-nowrap;

        font-size: 20px;
        font-weight: 500;
        line-height: 28px;
      };

      --paper-font-subhead: {
        @apply --paper-font-common-base;

        font-size: 16px;
        font-weight: 400;
        line-height: 24px;
      };

      --paper-font-body2: {
        @apply --paper-font-common-base;

        font-size: 14px;
        font-weight: 500;
        line-height: 24px;
      };

      --paper-font-body1: {
        @apply --paper-font-common-base;

        font-size: 14px;
        font-weight: 400;
        line-height: 20px;
      };

      --paper-font-caption: {
        @apply --paper-font-common-base;
        @apply --paper-font-common-nowrap;

        font-size: 12px;
        font-weight: 400;
        letter-spacing: 0.011em;
        line-height: 20px;
      };

      --paper-font-menu: {
        @apply --paper-font-common-base;
        @apply --paper-font-common-nowrap;

        font-size: 13px;
        font-weight: 500;
        line-height: 24px;
      };

      --paper-font-button: {
        @apply --paper-font-common-base;
        @apply --paper-font-common-nowrap;

        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.018em;
        line-height: 24px;
        text-transform: uppercase;
      };

      --paper-font-code2: {
        @apply --paper-font-common-code;

        font-size: 14px;
        font-weight: 700;
        line-height: 20px;
      };

      --paper-font-code1: {
        @apply --paper-font-common-code;

        font-size: 14px;
        font-weight: 500;
        line-height: 20px;
      };

    }

  </style>
</custom-style>`;o.setAttribute("style","display: none;"),document.head.appendChild(o.content)},81563:(t,e,i)=>{i.d(e,{E_:()=>f,OR:()=>r,_Y:()=>p,fk:()=>d,hN:()=>s,hl:()=>m,i9:()=>c,pt:()=>a,ws:()=>u});var o=i(15304);const{I:n}=o.Al,a=t=>null===t||"object"!=typeof t&&"function"!=typeof t,s=(t,e)=>void 0===e?void 0!==(null==t?void 0:t._$litType$):(null==t?void 0:t._$litType$)===e,r=t=>void 0===t.strings,l=()=>document.createComment(""),p=(t,e,i)=>{var o;const a=t._$AA.parentNode,s=void 0===e?t._$AB:e._$AA;if(void 0===i){const e=a.insertBefore(l(),s),o=a.insertBefore(l(),s);i=new n(e,o,t,t.options)}else{const e=i._$AB.nextSibling,n=i._$AM,r=n!==t;if(r){let e;null===(o=i._$AQ)||void 0===o||o.call(i,t),i._$AM=t,void 0!==i._$AP&&(e=t._$AU)!==n._$AU&&i._$AP(e)}if(e!==s||r){let t=i._$AA;for(;t!==e;){const e=t.nextSibling;a.insertBefore(t,s),t=e}}}return i},d=(t,e,i=t)=>(t._$AI(e,i),t),h={},m=(t,e=h)=>t._$AH=e,c=t=>t._$AH,u=t=>{var e;null===(e=t._$AP)||void 0===e||e.call(t,!1,!0);let i=t._$AA;const o=t._$AB.nextSibling;for(;i!==o;){const t=i.nextSibling;i.remove(),i=t}},f=t=>{t._$AR()}},57835:(t,e,i)=>{i.d(e,{XM:()=>o.XM,Xe:()=>o.Xe,pX:()=>o.pX});var o=i(38941)}}]);
//# sourceMappingURL=14645-tQqNpypNWcU.js.map
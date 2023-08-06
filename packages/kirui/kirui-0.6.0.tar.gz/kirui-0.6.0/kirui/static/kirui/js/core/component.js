import { LitElement, html, svg, css, render } from "./lit-element.js";
import { keyed } from "./directives/keyed.js";
import { classMap } from "./directives/class-map.js";

class Component extends LitElement {
    attach_shadow = false;

    createRenderRoot() {
        if (this.attach_shadow === false) {
            this.innerHTML = '';  // TODO: remove childrens
            return this;
        }

        return super.createRenderRoot();
    }
}

export { Component, html, svg, css, render, LitElement, keyed, classMap };

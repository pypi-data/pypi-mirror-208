import { Component, html, render } from "../../core/component.js";

class Card extends Component {
    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;
    }

    showCardBody(ev) {
        let body = this.querySelector('kr-card-body');
        if (body !== null) {
            body.classList.remove('collapsed')
        }
    }

    hideCardBody(ev) {
        let body = this.querySelector('kr-card-body');
        if (body !== null) {
            body.classList.add('collapsed')
        }
    }
    toggleCardBody(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        let body = this.querySelector('kr-card-body');
        if (body !== null) {
            if (body.classList.contains('collapsed')) {
                this.showCardBody()
            } else {
                this.hideCardBody()
            }
        }
    }

    render() {
        return html`
          <div class="card">
            ${this.$children}
          </div>`
    }
}

class CardHeader extends Component {
    render() {
        return html`
          <div class="card-header">
            ${this.$children}
          </div>`
    }
}

class CardBody extends Component {
    render() {
        return html`
          <div class="card-body">
            ${this.$children}
          </div>`
    }
}

customElements.define("kr-card", Card)
customElements.define("kr-card-header", CardHeader)
customElements.define("kr-card-body", CardBody)

export { Card, CardHeader, CardBody }

import * as m from "../core/component.js";
import { request } from "../utils/http.js";

class ModalLink extends m.Component {
    constructor() {
        super();
        this.$modal_content = m.html`<div></div>`
    }

    _init_modal(resp) {
        this.$modal_content = eval(resp.responseText);
        this.requestUpdate();

        /* Ez azért kell, hogy az oldalon taláhlató lenyílókat becsukjuk akkor, amikor a modalt nyitjuk
        console.log('click dispatched')
        let event = new Event('click');
        window.dispatchEvent(event);*/

        document.body.classList.add('modal-open');
    }

    open_modal(ev) {
        ev.preventDefault();

        request.get(
            this.href,
            (resp) => { this._init_modal(resp); }
        )
    }

    close_modal(ev) {
        this.$modal_content = m.html`<div></div>`
        this.requestUpdate();
        document.body.classList.remove('modal-open');
        document.body.click();
    }

    _submit_complete(resp) {
        if (resp.status === 403) {
            this.$modal_content = eval(resp.responseText);
            this.requestUpdate();
        } else if (resp.status === 200) {
            this.close_modal();
            let closedEvent = new CustomEvent('modal-closed', {
                detail: { message: resp.responseText },
                bubbles: false,
                composed: true
            });
            this.dispatchEvent(closedEvent);
        }
    }

    submit(ev) {
        ev.preventDefault()
        ev.stopPropagation()

        let form = this.querySelector('kr-form')
        let data = form.form_data()
        if (ev.target.tagName === 'INPUT' && ev.target.name) {
            data.append(ev.target.name, '')
        }
        request.post(
            form.action || form.getAttribute('action') || window.location,
            data,
            (resp) => this._submit_complete(resp)
        )
    }

    render() {
        return m.html`
            <a href="${this.href}" @click="${(ev) => this.open_modal(ev)}" class="${this.class}">${this.$children}</a>${this.$modal_content}
        `
    }
}
customElements.define("kr-modal-link", ModalLink)

class SideModal extends m.Component {
    css_style() {
        return `width: ${this.width || '50%'}`
    }

    render() {
        return m.html`
        <div class="overlay">
          <div class="modal" style="${this.css_style()}">
            ${this.$children}
          </div>
        </div>`
    }
}
customElements.define("kr-side-modal", SideModal)

class ModalHeader extends m.Component {
    render() {
        return m.html`
        <div class="header">
          <div class="modal-title">${this.$children}</div>
          <button type="button" class="btn-close" @click="${ (ev) => this.closest('kr-modal-link').close_modal(ev) }"></button>
        </div>`
    }
}
customElements.define("kr-modal-header", ModalHeader)

class ModalBody extends m.Component {
    render() {
        return m.html`
        <div class="body">
          <div class="col">${this.$children}</div>
        </div>`
    }
}
customElements.define("kr-modal-body", ModalBody)

class ModalFooter extends m.Component {
    render() {
        return m.html`
        <div class="footer">
          ${this.$children}
        </div>`
    }
}
customElements.define("kr-modal-footer", ModalFooter)

export { ModalLink, SideModal, ModalHeader, ModalBody, ModalFooter }

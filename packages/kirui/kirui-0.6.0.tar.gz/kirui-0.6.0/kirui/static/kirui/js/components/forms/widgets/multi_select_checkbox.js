import { Component, html, render, classMap } from "../../../core/component.js";


class MultiSelectCheckboxField extends Component {
    static properties = {
        'disabled': {},
        'error': {},
        'is_open': {}
    }

    constructor() {
        super();
        this.is_open = false;
    }

    css_class() {
        let retval = 'parent';

        if (this.disabled.toString() == '1') {
            retval += ' readonly';
        }

        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    update_labels(ev) {
        let values = []
        for (let cb of this.querySelectorAll('input[type=checkbox]')) {
            if (cb.checked) {
                values.push(cb.parentElement.textContent.trim())
            }
        }
        let el = this.querySelectorAll('.select-value')[0]
        el.textContent = values.join(', ') || 'Kérlek válassz...'
    }

    toggle_dropdown(ev) {
        if (['INPUT', 'LABEL'].indexOf(ev.target.tagName) > -1) {
            return
        }

        $(this).find('.dropdown').toggleClass('show')
    }

    form_data() {
        let retval = {}
        retval[this.name] = []

        for (let option of this.querySelectorAll('input[type=checkbox]')) {
            if (option.checked === true) {
                retval[this.name].push(option.value);
            }
        }

        return retval
    }

    close(ev) {
        let path = ev.path || ev.composedPath();
        if (path && (path.indexOf(this) === -1)) {
            this.is_open = false;
            document.removeEventListener("click", this.close, false);
        }
    }

    click(ev) {
        if (this.disabled.toString() == '1') { return; }
        if (this.is_open === false) {
            this.is_open = true;
            ev.stopPropagation();
            ev.preventDefault();
            document.addEventListener("click", (ev) => { this.close(ev); }, false);
        }
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;
        if (this.disabled.toString() != '1') {
            // this.querySelector('.parent').addEventListener('click', this.toggle_dropdown);
            $(this).find('input[type=checkbox]').on('change', (ev) => this.update_labels(ev));
        }
        this.update_labels(null);
    }

    render() {
        return html`
          <div class="${this.css_class()}" @click=${this.click}>
            <div class="header">
              <div class="select-value">Kérlek válassz...</div>
            </div>
            <div class=${classMap({'dropdown': true, 'show': this.is_open})}>${this.$children}</div>
          </div>`
    }
}
customElements.define("kr-multi-select-checkbox", MultiSelectCheckboxField);


class OptionCheckbox extends Component {
    css_class() {
        let retval = 'form-select'
        if (this.error !== undefined) {
            retval += ' is-invalid'
        }

        return retval
    }

    click_on_label(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        let id = ev.target.getAttribute('for');
        this.querySelector(`#${id}`).checked = !this.querySelector(`#${id}`).checked;
        this.closest('kr-multi-select-checkbox').update_labels(ev);
    }

    render() {
        let id = Date.now().toString(36) + Math.random().toString(36).substring(2);
        return html`
          <div style="margin-bottom: 5px; margin-top: 5px;">
            <input type="checkbox" id=${id} class="form-check-input" .value="${this.getAttribute('value') || ''}" ?checked="${this.getAttribute('selected') !== null}" />
            <label class="form-check-label" for=${id} @click=${this.click_on_label}>
              ${this.$children}
            </label>
          </div>
        `
    }
}
customElements.define("kr-option-checkbox", OptionCheckbox);


export { MultiSelectCheckboxField, OptionCheckbox }

import { Component, html, render } from "../../../core/component.js";


class SelectField extends Component {
    css_class() {
        let retval = 'form-select'
        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    form_data() {
        let retval = {}
        retval[this.name] = this.querySelector('select').value
        return retval
    }

    render() {
        return html`
          <select class="${this.css_class()}" .value="${this.value}" ?disabled="${this.disabled.toString() === '1'}">
            ${this.$children}
          </select>
        `
    }
}
customElements.define("kr-select", SelectField);

export { SelectField }

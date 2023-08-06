import { Component, html, render } from "../../../core/component.js";


class InputField extends Component {
    input_type() {
        if (this.widget === 'kr-number-input') {
            return 'number'
        }
        return 'input'
    }

    css_class() {
        let retval = 'form-control'
        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    form_data() {
        let field = this.querySelector('input');
        let retval = {};
        retval[field.getAttribute('name')] = field.value;
        return retval;
    }

    render() {
        return html`
          <input type="${this.input_type()}" class="${this.css_class()}" name="${this.name}" id="${this.field_id}" .value="${this.value}" ?disabled="${this.disabled.toString() === '1'}">
        `;
    }
}
customElements.define("kr-input", InputField);

export { InputField }

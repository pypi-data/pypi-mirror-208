import { Component, html, render } from "../../../core/component.js";


class CheckboxField extends Component {
    css_class() {
        let retval = 'form-control form-check-input'
        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    form_data() {
        let retval = {};
        retval[this.name] = this.querySelector('input[type=checkbox]').checked;
        return retval;
    }

    render() {
        return html`
        <div class="form-check form-switch">
          <input type="checkbox" name="${this.name}" id="${this.field_id}" class="${this.css_class()}" ?disabled="${[1, '1', true, 'true'].indexOf(this.disabled) > -1}" ?checked="${[1, '1', true, 'true'].indexOf(this.value) > -1}" />
        </div>
        `
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;
    }
}
customElements.define("kr-checkbox-switch", CheckboxField);

export { CheckboxField }

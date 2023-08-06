import { Component, html, render } from "../../../core/component.js";


class FileField extends Component {
    css_class() {
        let retval = 'form-control'
        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    form_data() {
        let field = this.querySelector('input[type=file]')
        let retval = {}
        retval[field.name] = ''
        if (field.files.length > 0) {
            retval[field.name] = field.files[0]
        }

        return retval
    }

    render() {
        return html`
        <input type="file" class="${this.css_class()}" name="${this.name}" id="${this.field_id}" ?disabled="${[1, '1', true, 'true'].indexOf(this.disabled) > -1}" .value="${this.value}" />
        `
    }
}
customElements.define("kr-file", FileField);

export { FileField }

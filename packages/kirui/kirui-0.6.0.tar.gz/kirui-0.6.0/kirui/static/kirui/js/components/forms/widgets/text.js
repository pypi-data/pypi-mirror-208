import { Component, html, render } from "../../../core/component.js";


class TextField extends Component {
    DEFAULT_HEIGHT = 480

    css_class() {
        let retval = 'form-control'
        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    form_data() {
        let retval = {}
        retval[this.name] = tinymce.get(this.field_id).getContent()
        return retval
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;

        let that = this;
        tinymce.remove(`#${this.field_id}`);
        tinymce.init({
            'target': this.querySelector(`#${this.field_id}`),
            'readonly': [1, '1', true, 'true'].indexOf(this.disabled) > -1,
            'branding': false,
            'menubar': false,
            'toolbar': [
                'undo redo | blocks | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | table'
            ],
            plugins: [
              'lists', 'table'
            ],
            content_css: 'light',
            'height': this.height || this.DEFAULT_HEIGHT,
            setup: function(editor) {
                editor.on('click', function(event) {
                    that.click();
                });
            }
        })
    }

    render() {
        return html`
          <style>
            .tox-tinymce-aux{z-index:99999999999 !important;}
          </style>
          <textarea class="${this.css_class()}" name="${this.name}" id="${this.field_id}" ?readonly="${[1, '1', true, 'true'].indexOf(this.disabled) > -1}">${this.value}</textarea>
        `
    }
}
customElements.define("kr-textbox", TextField);

export { TextField }

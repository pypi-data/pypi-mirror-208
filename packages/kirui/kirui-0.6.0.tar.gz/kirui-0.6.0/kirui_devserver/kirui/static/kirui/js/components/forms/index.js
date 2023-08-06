import { Component, html, render } from "../../core/component.js";
import * as m from "../../core/component.js";
import { InputField } from './widgets/input.js';
import { SelectField } from './widgets/select.js';
import { MultiSelectCheckboxField, OptionCheckbox } from './widgets/multi_select_checkbox.js';
import { CheckboxField } from './widgets/checkbox.js';
import { TextField } from './widgets/text.js';
import { DatePickerField } from './widgets/date.js';
import { FileField } from './widgets/file.js';
// import { SourceEditor } from './widgets/source_editor/index.js';
import { request } from '../../utils/http.js';


class Form extends Component {
    form_data() {
        let form_data = new FormData()
        form_data.append('csrfmiddlewaretoken', this.getAttribute('csrfmiddlewaretoken'))
        for (let field of this.querySelectorAll('[data-form-field]')) {
            for (let [k, v] of Object.entries(field.form_data())) {
                if (v instanceof Array) {
                    for (let p of v) {
                        form_data.append(k, p);
                    }
                } else {
                    form_data.append(k, v);
                }
            }
        }

        return form_data
    }

    _submit_complete(resp) {
        if (resp.status === 403) {
            let patch = eval(resp.responseText);
            this.$children = patch.values;
            this.requestUpdate();
        }
    }

    submit(ev) {
        ev.preventDefault()
        ev.stopPropagation()

        let data = this.form_data()
        if (ev.target.tagName === 'INPUT' && ev.target.name) {
            data.append(ev.target.name, '')
        }
        request.post(
            this.action || this.getAttribute('action') || window.location,
            data,
            (resp) => this._submit_complete(resp)
        )
    }
    render() {
        return html`${this.$children}`;
    }
}
customElements.define("kr-form", Form);


class FormField extends Component {
    label_class() {
        let cls = 'col-form-label '

        for (let part of this.getAttribute('label-width').split(' ')) {
            cls += `col-${part} `
        }

        if (['true', true, 1].indexOf(this.getAttribute('required') || 'false') !== -1) {
            cls += 'required'
        }

        return cls
    }

    field_class() {
        let cls = '';
        for (let part of this.getAttribute('field-width').split(' ')) {
            cls += `col-${part} `;
        }
        return cls;
    }

    render() {
        let label;
        if (this.getAttribute('label-width') !== null) {
            label = html`<label for="${this.getAttribute('field_id')}" class="${this.label_class()}">${this.getAttribute('label')}</label>`
        } else {
            label = ''
        }

        return html`
          <div class="mb-3 row">
            ${label}    
            <div class="${this.field_class()}">
                ${['kr-input','kr-number-input'].indexOf(this.getAttribute('widget')) >= 0
                    ? html`<kr-input .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" data-form-field="true"></kr-input>`
                    : ''
                }
              
                ${this.getAttribute('widget') === 'kr-select'
                    ? html`<kr-select .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" .$children="${this.$children}" data-form-field="true"></kr-select>`
                    : ''
                }
              
                ${this.getAttribute('widget') === 'kr-multi-select-checkbox'
                    ? html`<kr-multi-select-checkbox .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" .$children="${this.$children}" data-form-field="true"></kr-multi-select-checkbox>`
                    : ''
                }
              
                ${this.getAttribute('widget') === 'kr-checkbox-switch'
                    ? html`<kr-checkbox-switch .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" .$children="${this.$children}" data-form-field="true"></kr-checkbox-switch>`
                    : ''
                }
              
                ${this.getAttribute('widget') === 'kr-textbox'
                    ? html`<kr-textbox .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" .$children="${this.$children}" data-form-field="true"></kr-textbox>`
                    : ''
                }
              
                ${this.getAttribute('widget') === 'kr-date-picker'
                    ? html`<kr-date-picker .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" .$children="${this.$children}" data-form-field="true"></kr-date-picker>`
                    : ''
                }
                
                ${this.getAttribute('widget') === 'kr-file'
                    ? html`<kr-file .name="${this.getAttribute('name')}" .field_id="${this.getAttribute('field_id')}" .disabled="${this.getAttribute('disabled')}" .widget="${this.getAttribute('widget')}" .value="${this.getAttribute('value')}" .error="${this.getAttribute('error')}" .$children="${this.$children}" data-form-field="true"></kr-file>`
                    : ''
                }
              
                ${(this.getAttribute('error') || '').length > 0 
                        ? html`<div class="invalid-feedback" style="display: block;">${this.getAttribute('error')}</div>` 
                        : '' 
                }
              </div>
          </div>
        `
    }
}
customElements.define("kr-form-field", FormField);


export { Form, FormField, InputField, SelectField, MultiSelectCheckboxField, OptionCheckbox, CheckboxField, TextField, DatePickerField, FileField };
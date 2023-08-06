import { Component, html, render, classMap } from "../../../core/component.js";


class DatePickerField extends Component {
    attach_shadow = false;

    static get properties() {
        return {
            picker_date: {state: true, attribute: false},
            is_open: {}
        }
    }

    constructor() {
        super();
        this.is_open = false;
        this.day_names = ['Hét', 'Ked', 'Sze', 'Csü', 'Pén', 'Szo', 'Vas'];  // TODO: app beállításokból
        this.month_names = ['Január', 'Február', 'Március', 'Április', 'Május', 'Június', 'Július', 'Augusztus', 'Szeptember', 'Október', 'November', 'December']
    }

    set picker_date(val) {
        if (val === '') {
            this._picker_date = new Date();
            return
        }

        if (typeof val === 'string') {
            this._picker_date = new Date(Date.parse(val) || new Date());
            return
        }

        this._picker_date = val;
    }

    get picker_date() { return this._picker_date; }

    set_date(ev, date) {
        ev.stopPropagation()
        ev.preventDefault()
        if (date === null) { return }
        this.picker_date = date;
        this.querySelector(`input[name=${this.name}]`).value = `${date.getUTCFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
        this.hide_calendar();
    }

    css_class() {
        let retval = 'parent'
        if ([1, '1', true, 'true'].indexOf(this.disabled) > -1) {
            retval += ' disabled'
        }
        if (this.error !== null) {
            retval += ' is-invalid'
        }

        return retval
    }

    form_data() {
        let retval = {}
        retval[this.name] = this.querySelector('input').value
        return retval
    }

    click_outside(ev) {
        let path = ev.path || ev.composedPath();
        console.log('click outside')
        if (path.indexOf(this) === -1) {
            this.hide_calendar(ev);
            document.removeEventListener("click", (ev) => { this.click_outside(ev) }, false);
        }
    }

    show_calendar(ev) {
        if (this.is_open === false) {
            this.is_open = true;
            document.addEventListener("click", (ev) => this.click_outside(ev), false);
        }

        this.picker_date = this.querySelector('input').value;
    }

    hide_calendar(ev) {
        this.is_open = false;
        //this.querySelector('.date-picker-box').classList.remove('show');
        //this.querySelector('input').blur();
    }

    async connectedCallback() {
        super.connectedCallback();
        this.picker_date = this.value;
        await this.updateComplete;
        // document.addEventListener('click', (ev) => this.hide_calendar(ev));
    }

    step_month(ev, month) {
        ev.preventDefault();
        ev.stopPropagation();

        var d = this.picker_date.getDate();
        this.picker_date.setMonth(this.picker_date.getMonth() + +month);
        if (this.picker_date.getDate() != d) {
            this.picker_date.setDate(0);
        }
        this.requestUpdate();
    }

    picker_content() {
        if (this.picker_date === undefined) { return ''; }
        let iter_day = new Date(this.picker_date.getUTCFullYear(), this.picker_date.getMonth(), 1);

        let weeks = [[]]
        for (let i = 0; i < (iter_day.getDay() || 7) - 1; i++) {
            weeks[weeks.length - 1].push(null)
        }

        while (true) {
            let act_day = new Date(iter_day.valueOf());
            weeks[weeks.length - 1].push(act_day);
            iter_day.setDate(iter_day.getDate() + 1)
            if (iter_day.getMonth() !== weeks.at(-1).at(-1).getMonth()) {
                break
            }
            if (iter_day.getDay() === 1) { weeks.push([]) }
        }

        function day_class(date) {
            let retval = 'day'
            if (date === null) { return retval; }
            if ([0,6].indexOf(date.getDay()) > -1) {
                retval += ' weekend'
            } else {
                retval += ' workday'
            }
            return retval;
        }

        function day_label(date) {
            if (date === null) { return '' }
            return date.getDate();
        }

        return html`
          <div class="paging">
            <div class="material-icons" @click="${(ev) => this.step_month(ev, -1)}">navigate_before</div>
            <div class="month">${this.month_names[this.picker_date.getMonth()]}</div>
            <div class="year">${this.picker_date.getUTCFullYear()}</div>
            <div class="material-icons" @click="${(ev) => this.step_month(ev, 1)}">navigate_next</div>
          </div>
          <div class="day-names">
            ${this.day_names.map((item) => html`<div class="day day-name">${item}</div>`)}
          </div>
          ${weeks.map((week) => html`
            <div class="week">
              ${week.map((day) => html`
                <div class="${day_class(day)}" @click="${(ev) => this.set_date(ev, day)}">${day_label(day)}</div>
              `)}
            </div>
          `)}
        `;
    }

    render() {
        return html`
          <div class="${this.css_class()}">
            <input type="input" class="form-control" name="${this.name}" id="${this.field_id}" ?disabled=${[1, '1', true, 'true'].indexOf(this.disabled) > -1} .value="${this.value}" autocomplete="off" @click="${this.show_calendar}" />
            <div class=${classMap({'date-picker-box': true, 'show': this.is_open})}>${this.picker_content()}</div>
          </div>
        `;
    }
}
customElements.define("kr-date-picker", DatePickerField);

export { DatePickerField }

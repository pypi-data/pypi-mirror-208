import * as m from "../../core/component.js";
import { request } from "../../utils/http.js";

class Table extends m.Component {
    async finished(resp) {
        if (resp.status == 201) {
            this.$children = eval(resp.responseText).values
            this.requestUpdate();
            await this.updateComplete;
            this.column_count = this.querySelectorAll('kr-columns kr-column').length
            this.querySelector('kr-paginator tr td').setAttribute('colspan', this.column_count)
        }
    }
    paginate(page) {
        request.get(
            `?paginate_to=${page}`,
            (resp) => this.finished(resp)
        )
    }

    render() {
        return m.html`${this.$children}`
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;

        if (this.querySelector('kr-paginator') !== null) {
            this.column_count = this.querySelectorAll('kr-columns kr-column').length
            this.querySelector('kr-paginator tr td').setAttribute('colspan', this.column_count)
        }
    }
}
customElements.define('kr-table', Table);


class Rows extends m.Component {
    render() {
        return m.html`${this.$children}`
    }
}
customElements.define('kr-rows', Rows);


class Columns extends m.Component {
    render() {
        return m.html`${this.$children}`
    }
}
customElements.define('kr-columns', Columns);

class Column extends m.Component {
    render() {
        return m.html`${this.$children}`
    }
}
customElements.define('kr-column', Column);

class Row extends m.Component {
    render() {
        return m.html`${this.$children}`
    }
}
customElements.define('kr-row', Row);

class Cell extends m.Component {
    render() {
        return m.html`${this.$children}`
    }
}
customElements.define('kr-cell', Cell);

class Paginator extends m.Component {
    prev_page_class() {
        let retval = 'page-item'
        if (this.getAttribute('prevpage') === '') {
            retval += ' disabled'
        }
        return retval
    }

    next_page_class() {
        let retval = 'page-item'
        if (this.getAttribute('nextpage') === '') {
            retval += ' disabled'
        }
        return retval
    }

    click_event(ev, page) {
        if (typeof this.paginate === 'function') {
            return this.paginate(ev, page);
        }

        return this.closest('kr-table').paginate(page)
    }
    render() {
        return m.html`
        <tr>
          <td>
            <nav>
              <ul class="pagination pagination-lg">
                <li class="${this.prev_page_class()}">
                  ${this.getAttribute('prevpage')
                    ? m.html`<a @click="${(ev) => this.click_event(ev, this.getAttribute('prevpage'))}" class="page-link" >&laquo;</a>`
                    : m.html`<a href="#" class="page-link">&laquo;</a>` 
                  }
                </li>
                <li class="page-item">
                  <a class="page-link">${this.getAttribute('actpage')}</a>
                </li>
                <li class="${this.next_page_class()}">
                  ${this.getAttribute('nextpage')
                    ? m.html`<a @click=${(ev) => this.click_event(ev, this.getAttribute('nextpage'))} class="page-link" >&raquo;</a>`
                    : m.html`<a href="#" class="page-link">&raquo;</a>` 
                  }
                </li>
              </ul>
            </nav>
          </td>
        </tr>
        `
    }
}
customElements.define('kr-paginator', Paginator);


export { Table, Columns, Rows, Column, Row, Cell }

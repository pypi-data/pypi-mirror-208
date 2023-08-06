import * as m from "../../core/component.js";
import { request } from "../../utils/http.js";


class FilteredTable extends m.Component {
    submit(ev, page) {
        if (page === undefined) {
            page = 1
        }

        request.post(
            this.querySelector('kr-form').getAttribute('action') || window.location + `?paginate_to=${page}`,
            this.querySelector('kr-form').form_data(),
            (resp) => {
                let patch = eval(resp.responseText).values;
                this.$children = patch;
                this.requestUpdate();
            }
        )
    }

    render() {
        return m.html`${this.$children}`
    }
}
customElements.define('kr-filtered-table', FilteredTable);

export { FilteredTable }

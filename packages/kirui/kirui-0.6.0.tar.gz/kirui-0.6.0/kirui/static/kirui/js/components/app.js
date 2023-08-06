import * as m from "../core/component.js";
import { request } from "../utils/http.js";

class Application extends m.Component {
    render() {
        return m.html`${this.$children}`
    }
}
customElements.define("kr-app", Application)

export { Application }

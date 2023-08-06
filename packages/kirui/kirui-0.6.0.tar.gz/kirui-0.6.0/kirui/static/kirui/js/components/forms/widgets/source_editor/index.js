import * as m from "../../../../core/component.js";
import { EditorView } from "./codemirror.js";


class SourceEditor extends m.Component {
    constructor() {
        super();
        console.log(this.textContent)
    }

    render() {
        return m.html`
          <div class="editor">${this.$children}</div>
        `
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;

        let wrapper = this.getElementsByClassName('editor')[0];
        let content = this.textContent.trim();
        wrapper.textContent = '';
        let myView = new EditorView({
            parent: wrapper,
            extensions: [],
            doc: content
        });
    }
}
customElements.define("kr-source-editor", SourceEditor)

export { SourceEditor }

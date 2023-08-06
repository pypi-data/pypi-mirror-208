import * as sideBar from "./components/layout/index.js";
import * as Form from "./components/forms/index.js";
import * as Modal from "./components/modal.js";
import * as Table from "./components/tables/index.js";
import * as Chart from "./components/charts/index.js";
import * as Button from "./components/button.js";
import * as Kanban from "./components/kanban/index.js";
import * as Application from "./components/app.js";
import { html, render } from "./core/component.js";

const entrypoint = (content) => {
    render(content, document.body);
}

window.kirui_version = '0.5.4';
export { entrypoint, html };

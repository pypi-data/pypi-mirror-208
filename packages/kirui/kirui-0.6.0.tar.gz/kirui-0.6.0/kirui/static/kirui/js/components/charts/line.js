import { Chart, registerables } from './chart.esm.js';
import * as m from "../../core/component.js";

Chart.register(...registerables);

class LineChart extends m.Component {
    render() {
        return m.html`
            <canvas style="width: 100%; height: 100%;"></canvas>
        `
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;

        const COLORS = ["#0b84a5", "#f6c85f", "#6f4e7c", "#9dd866", "#ca472f", "#ffa056", "#8dddd0"];
        let ctx = this.getElementsByTagName('canvas')[0];

        let chart_data = {
            'labels': [],
            'datasets': []
        };
        for (let [k1, v1] of Object.entries(this.values)) {
            let color = COLORS.pop(0)
            let data = {'label': k1, 'data': [], 'borderColor': color, 'backgroundColor': color};
            for (let [k2, v2] of Object.entries(v1)) {
                if (chart_data['labels'].indexOf(k2) === -1) {
                    chart_data['labels'].push(k2);
                }
                data['data'].push(v2);
            }
            chart_data['datasets'].push(data);
        }

        new Chart(ctx, {
            type: "line",
            data: chart_data,
            options: Chart.defaults.line
        });
    }
}
customElements.define("kr-chart-line", LineChart);

export { LineChart };

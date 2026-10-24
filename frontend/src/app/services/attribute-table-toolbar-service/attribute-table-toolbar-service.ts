import { afterNextRender, computed, inject, Injector, Service, signal, type WritableSignal } from '@angular/core';
import { Map } from 'ol';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { transformExtent } from 'ol/proj';

export type ToolbarTool = {
    [key: string]: WritableSignal<boolean>;
}
export type ToolbarMatTooltip = {
    [key: string]: string;
}
@Service()
export class AttributeTableToolbarService {
    private readonly injector = inject(Injector);
    private resetVersion = 0;
    public ToolbarTools: ToolbarTool = {
        selectionTool: signal<boolean>(false),
        searchTool: signal<boolean>(false),
        filterTool: signal<boolean>(false),
        calculateFieldTool: signal<boolean>(false),
    };
    public resetToolbarTools(toolKey?: keyof typeof this.ToolbarTools): void {
        if (toolKey) {
            this.ToolbarTools[toolKey].set(false);
            if (this.ToolbarTools['selectionTool']() || this.ToolbarTools['searchTool']()) {
                return;
            }
        } else {
            for (const key in this.ToolbarTools) {
                this.ToolbarTools[key].set(false);
            }
        }
        this.locateRowStyleOn.set(false);
        this.didUserClickedOffLocateRowStyle.set(false);
        this.showTransformButton.set(false);
        this.highlightLayer.getSource()?.clear();
        this.mainMap?.removeLayer(this.highlightLayer);
        this.highlightLayerRow.set(null);
        const map = this.mainMap;
        const version = ++this.resetVersion;
        map?.getView().cancelAnimations();
        if (map) {
            afterNextRender(() => requestAnimationFrame(() => {
                if (version !== this.resetVersion || map !== this.mainMap || this.highlightLayerRow()) return;
                map.updateSize();
                const view = map.getView();
                view.fit(transformExtent([14.1, 49, 24.2, 54.9], 'EPSG:4326', view.getProjection()), {
                    size: map.getSize(), padding: [50, 50, 50, 50], duration: 1000,
                });
            }), {
                injector: this.injector,
            });
        }
    }
    public ToolbarMatTooltip = computed(() => ({
        selectionTool: this.ToolbarTools['selectionTool']() ?
            "ATTRIBUTE-TOOLBAR.SELECT.OFF" :
            "ATTRIBUTE-TOOLBAR.SELECT.ON",
        searchTool: this.ToolbarTools['searchTool']() ?
            "ATTRIBUTE-TOOLBAR.SEARCH.OFF" :
            "ATTRIBUTE-TOOLBAR.SEARCH.ON",
        filterTool: this.ToolbarTools['filterTool']() ?
            "ATTRIBUTE-TOOLBAR.FILTER.OFF" :
            "ATTRIBUTE-TOOLBAR.FILTER.ON",
        calculateFieldTool: this.ToolbarTools['calculateFieldTool']() ?
            "ATTRIBUTE-TOOLBAR.CALCULATE.OFF" :
            "ATTRIBUTE-TOOLBAR.CALCULATE.ON"
    }));
    public toggleActivationTool(toolKey: keyof typeof this.ToolbarTools): void {
        console.log("WORKSSSSSS")
        this.ToolbarTools[toolKey].set(!this.ToolbarTools[toolKey]());
    }
  // SELECTION TOOL
    public mainMap: Map | null = null;
    public readonly highlightLayer = new VectorLayer({
        source: new VectorSource(),
        zIndex: 9999,
        style: {
            'fill-color': 'rgba(44, 44, 44, 0.5)',
            'stroke-color': '#2c2c2c', 'stroke-width': 5,
            'circle-radius': 20, 'circle-fill-color': '#2c2c2c',
            'circle-stroke-color': '#fff', 'circle-stroke-width': 3,
        },
    });
    public getMapComponent(map: Map): void {
        this.mainMap = map;
    }

    public locateRowStyleOn = signal<boolean>(false);
    public didUserClickedOffLocateRowStyle = signal<boolean>(false);
    public showTransformButton = signal<boolean>(false);
    public highlightLayerRow = signal<Record<string, unknown> | null>(null);

////////////////////////////////////////

/// FILTER TOOL///////////////////////
    public filterNr = signal<number>(1);
    public incrementFilterNr(): void {
        this.filterNr.update((value) => value + 1);
    }
    public decrementFilterNr(): void {
        this.filterNr.update((value) => value - 1);
    }
}

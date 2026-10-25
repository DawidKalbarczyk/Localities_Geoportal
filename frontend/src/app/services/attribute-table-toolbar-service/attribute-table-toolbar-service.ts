import { afterNextRender, computed, inject, Injector, Service, signal, type WritableSignal} from '@angular/core';
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

export type Filter = {
    attribute: string;
    operator: string;
    value: string;
}
export type Filters = {
    [key: number]: Filter;
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
    public filters = signal<Filters>({
        1: {
            attribute: '', 
            operator: '', 
            value: '' 
        } 
    });
    public numericAttributes: Array<string> = ["jpt_powier", "jpt_powi_1", "shape_leng", 
        "shape_le_1", "shape_area", "wspgeog", "wspxy", "liczbamies"];
    public operators = signal<Record<string, Record<string, string>>>({
        string: {
            zawiera: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.CONTAINS',  //.contains
            nie_zawiera: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.NOT-CONTAINS', //!.contains
            rowna_sie: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.EQUALS', // ==  
            nie_rowna_sie: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.NOT-EQUALS', // !=
            zaczyna_sie_od: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.STARTS-WITH', // .startsWith 
            konczy_sie_na: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.ENDS-WITH', // .endsWith
        },
        number: {
            mniejsze_niz: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.LOWER-THAN', // <
            mniejsze_lub_rowne: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.LOWER-THAN-EQUALS', // <=
            wieksze_niz: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.GREATER-THAN', // >
            wieksze_lub_rowne: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.GREATER-THAN-EQUALS', // >=
        },
        all: {
            jest_puste: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.IS-NULL', // == null
            nie_jest_puste: 'ATTRIBUTE-TOOLBAR.FILTER.CONTENT.OPERATORS.IS-NOT-NULL', // != null
        }
    });
    
    public filterNrs = computed(() => Object.keys(this.filters()).map(Number));
    public filterType = signal<string>('and');
    public incrementFilterNr(): void {
        this.filters.update((value => {
            const newFilterNr = Object.keys(value).length + 1;
            return {
                ...value,
                [newFilterNr]: { attribute: '', operator: '', value: '' }
            };
        }));
    }
    public decrementFilterNr(nr: number): void {
        this.filters.update((value => {
            const newFilters = { ...value };
            delete newFilters[nr];
            return newFilters;
        }));
    }

    public updateFilterParameter(nr: number, parameter: keyof Filter, newValue: string): void {
        this.filters.update(filters => ({
            ...filters,
            [nr]: {
                ...filters[nr],
                [parameter]: newValue
            }
        }));
    }
    public resetFilters(): void {
        this.filters.set({
            1: {
                attribute: '',
                operator: '',
                value: ''
            }
        });
        this.filterType.set('and');
    }
    public newShownTable = signal<Record<string, unknown>[] | null>(null);
    public applyFilters(table: Promise<Record<string, unknown>[]>): void {
        const matchesFilter = (
            row: Record<string, unknown>,
            filter: Filter,
            defaultResult: boolean,
        ): boolean => {
            const rowValue = row[filter.attribute];

            switch (filter.operator) {
                case 'zawiera':
                    return typeof rowValue === 'string' && rowValue.includes(filter.value);
                case 'nie_zawiera':
                    return typeof rowValue === 'string' && !rowValue.includes(filter.value);
                case 'rowna_sie':
                    return rowValue == filter.value;
                case 'nie_rowna_sie':
                    return rowValue != filter.value;
                case 'zaczyna_sie_od':
                    return typeof rowValue === 'string' && rowValue.startsWith(filter.value);
                case 'konczy_sie_na':
                    return typeof rowValue === 'string' && rowValue.endsWith(filter.value);
                case 'mniejsze_niz':
                    return typeof rowValue === 'number' && rowValue < Number(filter.value);
                case 'mniejsze_lub_rowne':
                    return typeof rowValue === 'number' && rowValue <= Number(filter.value);
                case 'wieksze_niz':
                    return typeof rowValue === 'number' && rowValue > Number(filter.value);
                case 'wieksze_lub_rowne':
                    return typeof rowValue === 'number' && rowValue >= Number(filter.value);
                case 'jest_puste':
                    return rowValue == null;
                case 'nie_jest_puste':
                    return rowValue != null;
                default:
                    return defaultResult;
            }
        };

        table.then(shownTable => {
            this.newShownTable.set(shownTable.filter(row => {
                const filterEntries = Object.entries(this.filters());
                if (this.filterType() === 'and') {
                    return filterEntries.every(([_, filter]) =>
                        matchesFilter(row, filter, true),
                    );
                } else if (this.filterType() === 'or') {
                    return filterEntries.some(([_, filter]) =>
                        matchesFilter(row, filter, false),
                    );
                }
                return true;
            }));
        });


        console.log('Applied filters:', this.filters());
    }

}

import { Service, signal, type WritableSignal } from '@angular/core';
import { Map } from 'ol';

export type ToolbarTool = {
    [key: string]: WritableSignal<boolean>;
}
export type ToolbarMatTooltip = {
    [key: string]: string;
}

@Service()
export class AttributeTableToolbarService {
    public ToolbarTools: ToolbarTool = {
        selectionTool: signal<boolean>(false),
        searchTool: signal<boolean>(false),
        filterTool: signal<boolean>(false),
        calculateFieldTool: signal<boolean>(false),
    };
    public resetToolbarTools(): void {
        for (const key in this.ToolbarTools) {
            this.ToolbarTools[key].set(false);
        }
    }
    public ToolbarMatTooltip = {
        selectionTool: this.ToolbarTools['selectionTool']() ? 
            "ATTRIBUTE-TOOLBAR.SELECT.ON" : 
            "ATTRIBUTE-TOOLBAR.SELECT.OFF",
        searchTool: this.ToolbarTools['searchTool']() ? 
            "ATTRIBUTE-TOOLBAR.SEARCH.ON" : 
            "ATTRIBUTE-TOOLBAR.SEARCH.OFF",
        filterTool: this.ToolbarTools['filterTool']() ? 
            "ATTRIBUTE-TOOLBAR.FILTER.ON" : 
            "ATTRIBUTE-TOOLBAR.FILTER.OFF",
        calculateFieldTool: this.ToolbarTools['calculateFieldTool']() ? 
            "ATTRIBUTE-TOOLBAR.CALCULATE.ON" : 
            "ATTRIBUTE-TOOLBAR.CALCULATE.OFF"
    }
    public toggleActivationTool(toolKey: keyof typeof this.ToolbarTools): void {
        console.log("WORKSSSSSS")
        this.ToolbarTools[toolKey].set(!this.ToolbarTools[toolKey]());
    }

    public mainMap: Map | null = null;
    public getMapComponent(map: Map): void {
        this.mainMap = map;
    }
}

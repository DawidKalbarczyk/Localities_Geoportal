import { Component, inject, OnDestroy, HostListener, OnInit } from '@angular/core';
import { GeoportalHeadbar} from './geoportal-headbar/geoportal-headbar';
import { ReturnCorner } from "../../global-components/return-corner/return-corner";
import { MapComponent } from "./map-component/map-component";
import { AuthorBar } from "../../global-components/author-bar/author-bar";
import { MeasureComponent } from "./geoportal-headbar/measure-component/measure-component";
import { AnalysysComponent } from "./geoportal-headbar/analysys-component/analysys-component";
import { AMService } from '../../services/a-m-service/a-m-service';
import { GeoserverService } from '../../services/GeoserverService/geoserver-service';
import { HttpClient } from '@angular/common/http';
import { ObjSelection } from '../../services/obj-selection/obj-selection';
import { getAuth } from 'firebase/auth';
import { ZoomToObject } from '../../services/zoom-to-object/zoom-to-object';
import { SearchClose } from './geoportal-headbar/search-close/search-close';
import { PopUp } from './pop-up/pop-up';
import { PopUpService } from '../../services/pop-up-service/pop-up-service';
import { GeoportalCorner } from '../../global-components/geoportal-corner/geoportal-corner';
import { firstValueFrom } from 'rxjs';
import { AttributeTableToolbarService } from '../../services/attribute-table-toolbar-service/attribute-table-toolbar-service';


@Component({
  selector: 'app-geoportal',
  imports: [GeoportalHeadbar, ReturnCorner, MapComponent, AuthorBar, MeasureComponent, AnalysysComponent, SearchClose, PopUp, GeoportalCorner],
  templateUrl: './geoportal.html',
  styleUrl: './geoportal.scss',
})
export class Geoportal implements OnDestroy, OnInit {
  public AMservice = inject(AMService);
  public GeoserverService = inject(GeoserverService);
  private objectSelection = inject(ObjSelection);
  private http = inject(HttpClient);
  private currentToken = '';
  public zoomService = inject(ZoomToObject);
  public popUpService = inject(PopUpService);
  private toolbarService = inject(AttributeTableToolbarService);

  constructor() {
    const auth = getAuth();
    auth.onIdTokenChanged(async (user) => {
      if (user) {
        this.currentToken = await user.getIdToken();
      } else {
        this.currentToken = '';
      }
    });
  }

  async ngOnInit(): Promise<void> {
    // Re-create temporary workspaces just in case they were deleted by a page reload
    // or if the user navigated directly to the geoportal bypassing the home page.
    const auth = getAuth();
    await auth.authStateReady();
    const userId = this.objectSelection.userId || auth.currentUser?.uid;
    if (userId) {
      await firstValueFrom(this.GeoserverService.createTempWorkspace(userId));
      await firstValueFrom(this.GeoserverService.createTempDatastore(userId));
    }
  }

  @HostListener('window:pagehide')
  onPageHide(): void {
    const auth = getAuth();
    const token = this.currentToken;

    fetch(`/create/delete-temp?userId=${this.objectSelection.userId}`, { 
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      keepalive: true 
    });

    // Wysyłamy tylko jeśli tabela w ogóle była tworzona (time nie jest pusty)
    if (this.objectSelection.time !== '') {
      fetch(`/analysys/delete-table-from-selection?userId=${this.objectSelection.userId}&time=${this.objectSelection.time}`, { 
        method: 'DELETE',
        keepalive: true 
      });
    }
  }
  
  ngOnDestroy(): void {
    this.toolbarService.resetToolbarTools();
    this.GeoserverService.deleteTemps(this.objectSelection.userId).subscribe({
      next: (response) => {
        console.log('Temporary workspaces and datastores deleted successfully:', response);
      },
      error: (error) => {
        console.error('Error deleting temporary workspaces and datastores:', error);
      }
    });

    // Wysyłamy tylko jeśli tabela w ogóle była tworzona (time nie jest pusty)
    if (this.objectSelection.time !== '') {
      this.http.delete('/analysys/delete-table-from-selection', {
        params: {
          userId: this.objectSelection.userId,
          time: this.objectSelection.time
        }
      }).subscribe({
        next: (response) => {
          console.log('Temporary table deleted successfully:', response);
        },
        error: (error) => {
          console.error('Error deleting temporary table:', error);
        }
      });
    }
  }
}



import { Component, inject, signal} from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { DarkMode } from '../../services/dark-mode/dark-mode';
import { GeoserverService } from '../../services/GeoserverService/geoserver-service';
import { LanguageService } from '../../services/language/language-service';
import { AMService } from '../../services/a-m-service/a-m-service';
import { filter, map } from 'rxjs/operators';
import { ReturnService } from '../../services/return-service/return-service';
import { toSignal } from '@angular/core/rxjs-interop';
import { effect } from '@angular/core';

@Component({
  selector: 'app-return-corner',
  imports: [],
  templateUrl: './return-corner.html',
  styleUrl: './return-corner.scss',
})
export class ReturnCorner {
  private router: Router = inject(Router);
  public languageChangeClicked = signal<boolean>(false);
  public isDarkMode = inject(DarkMode).isDarkMode;
  public languageService = inject(LanguageService);
  public userData = JSON.parse(localStorage.getItem('userData') || '{}');
  public amService = inject(AMService);
  private GeoserverService = inject(GeoserverService);
  public url = toSignal(
    this.router.events.pipe(
      filter((event): event is NavigationEnd =>
        event instanceof NavigationEnd
      ),
      map(event => event.urlAfterRedirects)
    ),
    { initialValue: this.router.url }
  )
  
  

  switchColors(): void {
    this.isDarkMode.set(!this.isDarkMode());
    console.log('Dark mode is now:', this.isDarkMode());

    localStorage.setItem('darkMode', this.isDarkMode() ? 'true' : 'false');
  }
   
  private returnService = inject(ReturnService);
  private urlList = this.returnService.urlList;
  constructor() {
    effect(() => {
      if ((this.url().includes('saved') && this.url().includes('geoportal-temp') === false) 
      && this.urlList().at(-1)?.includes('saved') === true) {
        console.log('URL SAVED detected.');
      } else if (this.urlList().at(-1) !== this.url()) {
        
        this.urlList.update((urls) => [...urls, this.url()]);
        console.log(this.urlList())
      } else {
        console.log('URL already exists. UrlList: ', this.urlList());
      }
    });
  }
  goBack(): void {
    this.returnService.clearTimeout();
    const userDataLocal = JSON.parse(localStorage.getItem('userDataLocal') || '{}');
    const userId = userDataLocal.uid;
    this.urlList.update((urls) => urls.slice(0, -1));
    this.amService.resetAMServiceVariables();
    if (this.router.url === '/geoportal') {
      this.GeoserverService.deleteTemps(userId).subscribe({
        next: (response) => {
          console.log('Temporary workspaces and datastores deleted successfully:', response);
        },
        error: (error) => {
          console.error('Error deleting temporary workspaces and datastores:', error);
        }
      });
    }

    this.router.navigate([this.urlList().at(-1)]);
    
  }
}

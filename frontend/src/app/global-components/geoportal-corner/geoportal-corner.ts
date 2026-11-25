import { Component, inject, signal } from '@angular/core';
import { LanguageService } from '../../services/language/language-service';
import { PopUpService } from '../../services/pop-up-service/pop-up-service';

@Component({
  selector: 'app-geoportal-corner',
  imports: [],
  templateUrl: './geoportal-corner.html',
  styleUrl: './geoportal-corner.scss',
})
export class GeoportalCorner {
  public languageService = inject(LanguageService);
  public PopUpService = inject(PopUpService);

  public languageChangeClicked = signal<boolean>(false);
}

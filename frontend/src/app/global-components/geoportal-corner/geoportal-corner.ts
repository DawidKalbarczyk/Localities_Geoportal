import { Component, inject, signal } from '@angular/core';
import { LanguageService } from '../../services/language/language-service';

@Component({
  selector: 'app-geoportal-corner',
  imports: [],
  templateUrl: './geoportal-corner.html',
  styleUrl: './geoportal-corner.scss',
})
export class GeoportalCorner {
  public languageService = inject(LanguageService);

  public languageChangeClicked = signal<boolean>(false);
}

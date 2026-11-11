import { Pipe, PipeTransform, inject } from '@angular/core';
import { LanguageService } from '../services/language/language-service';

@Pipe({
  name: 'translate',
  standalone: true,
  pure: false,
})
export class TranslatePipe implements PipeTransform {
  private readonly languageService = inject(LanguageService);

  transform(key: string, params: Record<string, string | number> = {}): string {
    return this.languageService.translate(key, params);
  }
}

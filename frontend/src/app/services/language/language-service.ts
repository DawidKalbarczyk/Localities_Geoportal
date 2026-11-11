import { Injectable, signal } from '@angular/core';

export type Language = 'pl' | 'en' | 'cz' | 'de' | 'es' | 'hu' | 'ru' | 'sk' | 'ua' | 'fr';

type TranslationMap = Record<string, unknown>;

@Injectable({
  providedIn: 'root',
})
export class LanguageService {
  private readonly storageKey = 'language';
  public readonly languages: readonly Language[] = ['pl', 'en', 'cz', 'de', 'es', 'hu', 'ru', 'sk', 'ua', 'fr'];

  public readonly currentLanguage = signal<Language>(this.getStoredLanguage());
  private readonly translations = signal<TranslationMap>({});

  constructor() {
    void this.loadTranslations(this.currentLanguage());
  }

  async toggleLanguage(): Promise<void> {
    const currentIndex = this.languages.indexOf(this.currentLanguage());
    const nextLanguage =
      this.languages[(currentIndex + 1) % this.languages.length];

    await this.setLanguage(nextLanguage);
  }

  async setLanguage(language: Language): Promise<void> {
    if (!this.languages.includes(language)) {
      throw new Error(`Unsupported language: ${language}`);
    }

    await this.loadTranslations(language);
  }

  translate(key: string, params: Record<string, string | number> = {}): string {
    const value = key.split('.').reduce<unknown>(
      (translation, part) =>
        typeof translation === 'object' && translation !== null
          ? (translation as TranslationMap)[part]
          : undefined,
      this.translations(),
    );

    if (typeof value !== 'string') return key;

    return value.replace(
      /\{\{\s*(\w+)\s*\}\}/g,
      (placeholder: string, name: string) =>
        params[name] !== undefined ? String(params[name]) : placeholder,
    );
  }

  private async loadTranslations(language: Language): Promise<void> {
    const response = await fetch(`/i18n/${language}.json`);

    if (!response.ok) {
      throw new Error(`Failed to load translations for language: ${language}`);
    }

    const translations = (await response.json()) as TranslationMap;

    this.translations.set(translations);
    this.currentLanguage.set(language);
    localStorage.setItem(this.storageKey, language);
  }

  private getStoredLanguage(): Language {
    const storedLanguage = localStorage.getItem(this.storageKey);

    return this.languages.includes(storedLanguage as Language)
      ? (storedLanguage as Language)
      : this.languages[0];
  }
}

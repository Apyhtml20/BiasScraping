import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuditApi } from '../../../core/services/audit-api';

@Component({
  selector: 'app-url-input',
  imports: [FormsModule],
  templateUrl: './url-input.html',
  styleUrl: './url-input.css',
})
export class UrlInput {
  protected readonly api = inject(AuditApi);
  protected readonly url = signal('');
  protected readonly validationError = signal<string | null>(null);

  protected submit(): void {
    const value = this.url().trim();

    if (!value) {
      this.validationError.set('Enter an article URL to analyze.');
      return;
    }

    try {
      const parsed = new URL(value);
      if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
        throw new Error('invalid protocol');
      }
    } catch {
      this.validationError.set('Enter a valid URL, including https://');
      return;
    }

    this.validationError.set(null);
    this.api.runAudit(value);
  }

  protected fillSample(sample: string): void {
    this.url.set(sample);
    this.validationError.set(null);
  }
}

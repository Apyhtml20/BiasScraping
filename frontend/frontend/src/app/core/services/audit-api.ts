import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';

import { AuditReport } from '../models/audit.model';

const PHASES = [
  'Fetching the article…',
  'Scanning language for bias…',
  'Analyzing images for representation…',
  'Compiling the inclusivity report…',
];

@Injectable({ providedIn: 'root' })
export class AuditApi {
  private readonly http = inject(HttpClient);
  private phaseTimer?: ReturnType<typeof setInterval>;

  readonly phases = PHASES;
  readonly report = signal<AuditReport | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly phaseIndex = signal(0);

  runAudit(url: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.report.set(null);
    this.phaseIndex.set(0);
    this.startPhaseCycle();

    this.http.post<AuditReport>('/api/audit', { url }).subscribe({
      next: (report) => {
        this.report.set(report);
        this.loading.set(false);
        this.stopPhaseCycle();
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(this.extractMessage(err));
        this.loading.set(false);
        this.stopPhaseCycle();
      },
    });
  }

  reset(): void {
    this.report.set(null);
    this.error.set(null);
  }

  private startPhaseCycle(): void {
    this.stopPhaseCycle();
    this.phaseTimer = setInterval(() => {
      this.phaseIndex.update((i) => (i + 1) % PHASES.length);
    }, 3200);
  }

  private stopPhaseCycle(): void {
    if (this.phaseTimer) {
      clearInterval(this.phaseTimer);
      this.phaseTimer = undefined;
    }
  }

  private extractMessage(err: HttpErrorResponse): string {
    if (err.status === 0) {
      return "Impossible de joindre le serveur d'analyse. Vérifie que le backend est démarré.";
    }
    const detail = (err.error as { detail?: string } | null)?.detail;
    return detail || `Erreur ${err.status} lors de l'analyse.`;
  }
}

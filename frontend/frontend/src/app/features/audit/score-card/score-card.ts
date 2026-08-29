import { Component, computed, effect, input, signal } from '@angular/core';

import { AuditReport } from '../../../core/models/audit.model';

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

@Component({
  selector: 'app-score-card',
  imports: [],
  templateUrl: './score-card.html',
  styleUrl: './score-card.css',
})
export class ScoreCard {
  readonly report = input<AuditReport | null>(null);

  protected readonly circumference = CIRCUMFERENCE;
  protected readonly animatedScore = signal(0);

  protected readonly ringOffset = computed(
    () => CIRCUMFERENCE - (CIRCUMFERENCE * this.animatedScore()) / 100,
  );

  protected readonly tier = computed<'good' | 'fair' | 'poor'>(() => {
    const score = this.report()?.inclusivity_score ?? 0;
    if (score >= 75) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
  });

  protected readonly tierLabel = computed(() => {
    switch (this.tier()) {
      case 'good':
        return 'Strong inclusivity';
      case 'fair':
        return 'Room for improvement';
      default:
        return 'Significant concerns';
    }
  });

  constructor() {
    effect((onCleanup) => {
      const report = this.report();
      this.animatedScore.set(0);
      if (!report) {
        return;
      }
      const id = setTimeout(() => this.animatedScore.set(report.inclusivity_score), 40);
      onCleanup(() => clearTimeout(id));
    });
  }
}

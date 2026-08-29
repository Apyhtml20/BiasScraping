import { DecimalPipe } from '@angular/common';
import { Component, computed, input } from '@angular/core';

import { AuditIssue } from '../../../core/models/audit.model';

const TYPE_LABELS: Record<string, string> = {
  gendered_language: 'Gendered language',
  gender_stereotype: 'Gender stereotype',
  exclusionary_language: 'Exclusionary language',
  potential_bias: 'Potential bias',
};

@Component({
  selector: 'app-nlp-results',
  imports: [DecimalPipe],
  templateUrl: './nlp-results.html',
  styleUrl: './nlp-results.css',
})
export class NlpResults {
  readonly issues = input<AuditIssue[]>([]);

  protected readonly nlpIssues = computed(() =>
    this.issues().filter((issue) => issue.module === 'nlp'),
  );

  protected typeLabel(type: string): string {
    return TYPE_LABELS[type] ?? type.replace(/_/g, ' ');
  }
}

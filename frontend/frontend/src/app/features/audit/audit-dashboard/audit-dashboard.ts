import { Component, inject } from '@angular/core';

import { AuditApi } from '../../../core/services/audit-api';
import { MarkdownPipe } from '../../../core/pipes/markdown.pipe';
import { AuditProgress } from '../audit-progress/audit-progress';
import { NlpResults } from '../nlp-results/nlp-results';
import { Recommendations } from '../recommendations/recommendations';
import { ScoreCard } from '../score-card/score-card';
import { UrlInput } from '../url-input/url-input';
import { VisionResults } from '../vision-results/vision-results';

@Component({
  selector: 'app-audit-dashboard',
  imports: [
    UrlInput,
    AuditProgress,
    ScoreCard,
    NlpResults,
    VisionResults,
    Recommendations,
    MarkdownPipe,
  ],
  templateUrl: './audit-dashboard.html',
  styleUrl: './audit-dashboard.css',
})
export class AuditDashboard {
  protected readonly api = inject(AuditApi);
}

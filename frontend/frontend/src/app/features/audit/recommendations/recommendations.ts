import { Component, input } from '@angular/core';

import { AuditRecommendation } from '../../../core/models/audit.model';

@Component({
  selector: 'app-recommendations',
  imports: [],
  templateUrl: './recommendations.html',
  styleUrl: './recommendations.css',
})
export class Recommendations {
  readonly recommendations = input<AuditRecommendation[]>([]);
}

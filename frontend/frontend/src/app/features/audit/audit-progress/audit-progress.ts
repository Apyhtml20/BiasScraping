import { Component, inject } from '@angular/core';

import { AuditApi } from '../../../core/services/audit-api';

@Component({
  selector: 'app-audit-progress',
  imports: [],
  templateUrl: './audit-progress.html',
  styleUrl: './audit-progress.css',
})
export class AuditProgress {
  protected readonly api = inject(AuditApi);
}

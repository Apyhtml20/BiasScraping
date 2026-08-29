import { Routes } from '@angular/router';

import { AuditDashboard } from './features/audit/audit-dashboard/audit-dashboard';

export const routes: Routes = [
  { path: '', component: AuditDashboard },
  { path: '**', redirectTo: '' },
];

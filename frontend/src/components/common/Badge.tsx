import React from 'react';
import type { MaterialCondition, RecommendationAction, DefectSeverity, UserRole } from '../../types';

export const ConditionBadge: React.FC<{ condition: MaterialCondition | string; size?: 'sm' | 'md' | 'lg' }> = ({ condition, size = 'md' }) => {
  let style = 'bg-amber-50 text-amber-800 border-amber-200';
  let dot = 'bg-amber-500';

  if (condition === 'GOOD') {
    style = 'bg-emerald-50 text-emerald-800 border-emerald-200';
    dot = 'bg-emerald-600';
  } else if (condition === 'DAMAGED') {
    style = 'bg-rose-50 text-rose-800 border-rose-200';
    dot = 'bg-rose-600';
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : (size === 'lg' ? 'px-3 py-1.5 text-sm font-semibold' : 'px-2.5 py-1 text-xs font-medium');

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${style} ${px}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      <span>{condition}</span>
    </span>
  );
};

export const RecommendationBadge: React.FC<{ recommendation: RecommendationAction | string; size?: 'sm' | 'md' | 'lg' }> = ({ recommendation, size = 'md' }) => {
  let style = 'bg-gray-100 text-gray-800 border-gray-200';

  switch (recommendation) {
    case 'REUSE':
      style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      break;
    case 'REPAIR':
      style = 'bg-blue-50 text-blue-700 border-blue-200';
      break;
    case 'INSPECT':
      style = 'bg-amber-50 text-amber-800 border-amber-200';
      break;
    case 'RECYCLE':
      style = 'bg-purple-50 text-purple-700 border-purple-200';
      break;
    case 'REJECT':
      style = 'bg-rose-50 text-rose-700 border-rose-200';
      break;
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : (size === 'lg' ? 'px-3 py-1 text-sm font-bold tracking-wide' : 'px-2.5 py-1 text-xs font-semibold');

  return (
    <span className={`inline-flex items-center gap-1 rounded-md border font-mono uppercase ${style} ${px}`}>
      {recommendation}
    </span>
  );
};

export const SeverityBadge: React.FC<{ severity: DefectSeverity | string }> = ({ severity }) => {
  let style = 'bg-blue-50 text-blue-700 border-blue-200';

  if (severity === 'High') {
    style = 'bg-rose-50 text-rose-700 border-rose-200 font-semibold';
  } else if (severity === 'Medium') {
    style = 'bg-amber-50 text-amber-800 border-amber-200 font-medium';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-[11px] rounded border ${style}`}>
      {severity} Severity
    </span>
  );
};

export const RoleBadge: React.FC<{ role: UserRole | string }> = ({ role }) => {
  let style = 'bg-gray-100 text-gray-700 border-gray-200';
  let label = 'Inspector';

  if (role === 'admin') {
    style = 'bg-orange-50 text-orange-800 border-orange-200 font-semibold';
    label = 'Administrator';
  } else if (role === 'site_engineer') {
    style = 'bg-blue-50 text-blue-700 border-blue-200 font-semibold';
    label = 'Site Engineer';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs rounded border ${style}`}>
      {label}
    </span>
  );
};

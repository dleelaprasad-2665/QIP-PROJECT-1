import React from 'react';

export const ScoreGauge: React.FC<{ score: number; maxScore?: number; size?: 'sm' | 'md' | 'lg' }> = ({
  score,
  maxScore = 100,
  size = 'md'
}) => {
  const percentage = Math.min(100, Math.max(0, (score / maxScore) * 100));

  let strokeColor = '#DC2626'; // rose-600
  let barColor = 'bg-rose-600';
  let label = 'Severe Deterioration';
  let labelBadge = 'bg-rose-50 text-rose-700 border-rose-200';

  if (score >= 80) {
    strokeColor = '#16A34A'; // emerald-600
    barColor = 'bg-emerald-600';
    label = 'Excellent / Reusable';
    labelBadge = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (score >= 60) {
    strokeColor = '#D97706'; // amber-600
    barColor = 'bg-amber-600';
    label = 'Minor Defects / Repairable';
    labelBadge = 'bg-amber-50 text-amber-800 border-amber-200';
  } else if (score >= 40) {
    strokeColor = '#EA580C'; // orange-600
    barColor = 'bg-orange-600';
    label = 'Moderate Degradation';
    labelBadge = 'bg-orange-50 text-orange-800 border-orange-200';
  }

  if (size === 'sm') {
    return (
      <div className="flex items-center gap-2">
        <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
          <div className={`h-full ${barColor}`} style={{ width: `${percentage}%` }} />
        </div>
        <span className="font-mono text-xs font-semibold text-gray-700">{score.toFixed(0)}</span>
      </div>
    );
  }

  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
      <div className="relative w-20 h-20 flex items-center justify-center shrink-0">
        <svg className="w-20 h-20 transform -rotate-90">
          {/* Background Track */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke="#E5E7EB"
            strokeWidth="6"
            fill="transparent"
          />
          {/* Progress Circle */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke={strokeColor}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-xl font-bold font-mono text-gray-900 leading-none">{score.toFixed(0)}</span>
          <span className="text-[10px] uppercase font-medium text-gray-500 mt-0.5">/ 100</span>
        </div>
      </div>

      <div className="flex flex-col">
        <span className="text-[11px] uppercase tracking-wider text-gray-500 font-semibold">Visual Condition Index</span>
        <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded border mt-1 w-fit ${labelBadge}`}>{label}</span>
        <span className="text-[11px] text-gray-500 mt-1 leading-snug">
          Automated computer vision quality metric. Subject to site verification.
        </span>
      </div>
    </div>
  );
};

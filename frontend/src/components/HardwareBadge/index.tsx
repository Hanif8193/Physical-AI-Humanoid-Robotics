import React from 'react';

export type HardwareTier = 'RTX-LOCAL' | 'JETSON-ORIN' | 'CLOUD' | 'CPU-ONLY';

interface HardwareBadgeProps {
  tier: HardwareTier;
}

const TIER_CONFIG: Record<HardwareTier, { label: string; icon: string; className: string }> = {
  'RTX-LOCAL': {
    label: 'RTX-LOCAL',
    icon: '🖥️',
    className: 'hardware-badge--rtx-local',
  },
  'JETSON-ORIN': {
    label: 'JETSON-ORIN',
    icon: '🤖',
    className: 'hardware-badge--jetson-orin',
  },
  'CLOUD': {
    label: 'CLOUD',
    icon: '☁️',
    className: 'hardware-badge--cloud',
  },
  'CPU-ONLY': {
    label: 'CPU-ONLY',
    icon: '💻',
    className: 'hardware-badge--cpu-only',
  },
};

/**
 * HardwareBadge — renders a colored badge for hardware tier requirements.
 * Used in lab sections to indicate required hardware.
 */
export default function HardwareBadge({ tier }: HardwareBadgeProps): JSX.Element {
  const config = TIER_CONFIG[tier];
  return (
    <span className={`hardware-badge ${config.className}`} title={`Requires: ${tier}`}>
      {config.icon} {config.label}
    </span>
  );
}

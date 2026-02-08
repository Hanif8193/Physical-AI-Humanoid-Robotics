import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

/**
 * Physical AI & Humanoid Robotics Textbook Sidebar
 * HARD CONSTRAINT: EXACTLY 6 CHAPTERS
 * Chapter list is locked — do not add or remove entries.
 */
const sidebars: SidebarsConfig = {
  textbookSidebar: [
    {
      type: 'category',
      label: 'Physical AI & Humanoid Robotics',
      collapsed: false,
      items: [
        // Chapter 1 — Foundations
        {
          type: 'doc',
          id: 'ch01-intro-physical-ai',
          label: '1. Introduction to Physical AI',
        },
        // Chapter 2 — ROS 2
        {
          type: 'doc',
          id: 'ch02-ros2-fundamentals',
          label: '2. The Robotic Nervous System (ROS 2)',
        },
        // Chapter 3 — Digital Twin
        {
          type: 'doc',
          id: 'ch03-digital-twin',
          label: '3. Digital Twins & Simulation',
        },
        // Chapter 4 — NVIDIA Isaac
        {
          type: 'doc',
          id: 'ch04-isaac-platform',
          label: '4. The AI Robot Brain (Isaac)',
        },
        // Chapter 5 — VLA
        {
          type: 'doc',
          id: 'ch05-vla',
          label: '5. Vision-Language-Action',
        },
        // Chapter 6 — Capstone
        {
          type: 'doc',
          id: 'ch06-capstone',
          label: '6. Capstone: The Autonomous Humanoid',
        },
      ],
    },
  ],
};

// Validation: Enforce exactly 6 chapters
const chapterCount = sidebars.textbookSidebar[0].items?.length ?? 0;
if (chapterCount !== 6) {
  throw new Error(
    `CHAPTER LOCK VIOLATION: Expected 6 chapters, found ${chapterCount}. ` +
    'The chapter list is locked. Do not add or remove chapters.'
  );
}

export default sidebars;

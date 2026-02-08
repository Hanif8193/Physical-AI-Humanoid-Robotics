import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  stylesheets: [
    {
      href: 'https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap',
      type: 'text/css',
    },
  ],
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Bridging AI agents (software brains) with robots (physical bodies)',
  favicon: 'img/favicon.ico.svg',

  // GitHub Pages deployment
  url: 'https://your-org.github.io',
  baseUrl: '/physical-ai-robotics/',
  organizationName: 'your-org',
  projectName: 'physical-ai-robotics',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          editUrl: 'https://github.com/your-org/physical-ai-robotics/tree/main/frontend/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Social card
    image: 'img/logo.svg',
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'textbookSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          href: 'https://github.com/your-org/physical-ai-robotics',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Textbook',
          items: [
            { label: 'Introduction', to: '/ch01-intro-physical-ai' },
            { label: 'ROS 2', to: '/ch02-ros2-fundamentals' },
            { label: 'Digital Twin', to: '/ch03-digital-twin' },
            { label: 'NVIDIA Isaac', to: '/ch04-isaac-platform' },
            { label: 'VLA', to: '/ch05-vla' },
            { label: 'Capstone', to: '/ch06-capstone' },
          ],
        },
        {
          title: 'Resources',
          items: [
            { label: 'GitHub', href: 'https://github.com/your-org/physical-ai-robotics' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml'],
    },
    // Algolia search (optional - configure when ready)
    // algolia: { ... }
  } satisfies Preset.ThemeConfig,
};

export default config;

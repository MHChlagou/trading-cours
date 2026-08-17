// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/**
 * CONFIGURATION A PERSONNALISER (voir README.md) :
 *  - url              : https://VOTRE-PSEUDO.github.io
 *  - baseUrl          : /NOM-DU-REPO/
 *  - organizationName : votre pseudo GitHub
 *  - projectName      : le nom du repo
 */

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Trading : de Zéro à la Maîtrise',
  tagline: 'Fondamentaux, risque, SMC, order flow, macro, quant et psychologie. Un seul cours, dix niveaux.',
  favicon: 'img/favicon.ico',

  url: 'https://MHChlagou.github.io',
  baseUrl: '/trading-cours/',

  organizationName: 'MHChlagou',
  projectName: 'trading-cours',

  onBrokenLinks: 'warn',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'fr',
    locales: ['fr'],
  },

  future: {
    v4: true,
    faster: true,
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: 'cours',
          sidebarPath: './sidebars.js',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  // Recherche locale (activée si le paquet est installé, voir README)
  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      /** @type {import('@easyops-cn/docusaurus-search-local').PluginOptions} */
      ({
        hashed: true,
        language: ['fr'],
        docsRouteBasePath: 'cours',
        indexBlog: false,
        searchBarShortcutHint: false,
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
      navbar: {
        title: 'Zéro → Maîtrise',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'cours',
            position: 'left',
            label: 'Le cours',
          },
          {to: '/cours/annexes/glossaire', label: 'Glossaire', position: 'left'},
          {to: '/cours/annexes/ressources', label: 'Ressources', position: 'left'},
          {
            href: 'https://github.com/MHChlagou/trading-cours',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Le cours',
            items: [
              {label: 'Programme complet', to: '/cours/'},
              {label: 'Niveau 0 · Fondations', to: '/cours/niveau-0-fondations/quest-ce-que-le-trading'},
            ],
          },
          {
            title: 'Annexes',
            items: [
              {label: 'Glossaire', to: '/cours/annexes/glossaire'},
              {label: 'Livres recommandés', to: '/cours/annexes/livres'},
              {label: 'Sources institutionnelles', to: '/cours/annexes/ressources'},
            ],
          },
          {
            title: 'Légal',
            items: [
              {label: 'Avertissement', to: '/cours/annexes/avertissement'},
            ],
          },
        ],
        copyright: `Contenu strictement éducatif. Le trading comporte un risque élevé de perte en capital. © ${new Date().getFullYear()}`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json'],
      },
    }),
};

export default config;

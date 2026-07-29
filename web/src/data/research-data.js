export const report = {
  year: 2026,
  title: 'Malaysia Digital Advertising Report 2026',
  url: '/research/malaysia-digital-advertising-report-2026/',
  lastUpdated: '21 Jul 2026',

  hero: {
    headline: 'USD 1.41 Billion: Malaysia Digital Ad Spend 2026',
    subhead:
      'Steady growth driven by near-universal internet penetration, social commerce and ever-rising video consumption.',
  },

  executiveSummary: [
    { label: 'Digital Ad Spend 2026', value: 1410, suffix: 'M', unit: 'USD', source: 'Statista Advertising Outlook' },
    { label: 'Internet Users', value: 34, suffix: 'M', unit: '', source: 'DataReportal 2025' },
    { label: 'Social Media Users', value: 29, suffix: 'M', unit: '', source: 'We Are Social 2025' },
    { label: 'Daily Time on Social', value: 168, suffix: ' Min', unit: '', source: 'We Are Social 2025' },
  ],

  marketSize: {
    current: { year: 2026, value: 1.41, unit: 'USD Billion' },
    forecast: { year: 2030, value: 1.83, unit: 'USD Billion' },
    cagr: 6.7,
    source: 'Statista Digital Advertising Outlook — Malaysia (estimates)',
    data: [
      { year: 2020, value: 0.75 },
      { year: 2021, value: 0.85 },
      { year: 2022, value: 0.95 },
      { year: 2023, value: 1.08 },
      { year: 2024, value: 1.2 },
      { year: 2025, value: 1.31 },
      { year: 2026, value: 1.41 },
      { year: 2030, value: 1.83 },
    ],
  },

  formatShare: [
    { label: 'Video', percentage: 32.5, color: 'var(--color-accent)' },
    { label: 'Search', percentage: 27.8, color: 'var(--color-primary-2)' },
    { label: 'Display/Banner', percentage: 24.5, color: 'var(--color-teal)' },
    { label: 'Social Media (non-video)', percentage: 15.2, color: 'var(--color-green)' },
  ],

  deviceShare: [
    { label: 'Mobile', percentage: 71.2, color: 'var(--color-accent)' },
    { label: 'Desktop/Laptop', percentage: 23.3, color: 'var(--color-primary-2)' },
    { label: 'Connected TV', percentage: 5.5, color: 'var(--color-teal)' },
  ],

  platformUsers: [
    { name: 'WhatsApp', users: 29.4, color: '#25D366' },
    { name: 'TikTok', users: 24.8, color: '#000000' },
    { name: 'YouTube', users: 24.1, color: '#FF0000' },
    { name: 'Facebook', users: 22.4, color: '#1877F2' },
    { name: 'Instagram', users: 15.4, color: '#E4405F' },
  ],

  dailyEngagement: [
    { platform: 'TikTok', dailyMinutes: 95, color: '#000000' },
    { platform: 'WhatsApp', dailyMinutes: 90, color: '#25D366' },
    { platform: 'Instagram', dailyMinutes: 45, color: '#E4405F' },
    { platform: 'Facebook', dailyMinutes: 40, color: '#1877F2' },
    { platform: 'YouTube', dailyMinutes: 35, color: '#FF0000' },
  ],

  brandDiscovery: [
    { channel: 'Search Engine', percentage: 36.8 },
    { channel: 'Social Media Ads', percentage: 34.2 },
    { channel: 'Social Comments/UGC', percentage: 29.5 },
    { channel: 'TV/Offline', percentage: 25.3 },
    { channel: 'Word of Mouth', percentage: 23.1 },
  ],

  digitalGrowth: {
    dentsuGrowth: 4.8,
    digitalGrowth: '9-11%',
    oohGrowth: '6.0%',
    tvGrowth: '2-4%',
    source: 'GroupM This Year Next Year 2025 (estimates)',
    budgetShift: 6,
  },

  socialCommerce: {
    value: 3.5,
    unit: 'USD Billion',
    share: 22,
    growth: 24,
    source: 'e-Conomy SEA 2025 (estimates)',
  },

  trends: [
    {
      title: 'Video First',
      desc: 'Video accounts for roughly a third of digital ad spend and the majority of social media consumption in Malaysia.',
      source: 'Statista / We Are Social 2025',
    },
    {
      title: 'AI in Advertising',
      desc: 'AI adoption for creative localisation and dynamic creative optimisation is accelerating fast across Malaysian advertisers.',
      source: 'We Are Social 2025 / DataReportal',
    },
    {
      title: 'Social Commerce',
      desc: 'Social commerce is estimated around USD 3.5 billion — roughly 22% of Malaysian e-commerce, growing about 24% per year. TikTok Shop leads the charge.',
      source: 'e-Conomy SEA 2025 (estimates)',
    },
    {
      title: 'Data Protection',
      desc: "Malaysia's PDPA amendments (in force 2025) introduce stricter obligations, pushing platforms to strengthen consent flows and first-party data strategies.",
      source: 'PDPA Amendment Act 2024',
    },
    {
      title: 'Connected TV',
      desc: 'OTT streaming keeps expanding across Malaysian households, opening up fast-growing CTV advertising inventory.',
      source: 'Statista 2025 (estimates)',
    },
  ],

  challenges: [
    {
      title: 'Ad Fraud & Brand Safety',
      desc: 'Concerns over ad fraud and brand safety are driving adoption of contextual verification tools.',
    },
    {
      title: 'Platform Fragmentation',
      desc: 'Users spread their time across many platforms every month — making efficient budget allocation harder.',
    },
    {
      title: 'Regulatory Compliance',
      desc: 'The amended PDPA and fast-changing platform policies demand continuous adaptation of data strategy.',
    },
    {
      title: 'Talent Gap',
      desc: 'Demand for competent performance marketers far outstrips the supply of qualified talent.',
    },
  ],

  methodology: {
    sources: [
      {
        name: 'Statista',
        url: 'https://www.statista.com/outlook/dmo/digital-advertising/malaysia',
        desc: 'Digital Advertising Outlook — Malaysia',
      },
      {
        name: 'We Are Social & Meltwater',
        url: 'https://wearesocial.com/',
        desc: 'Digital 2025: Malaysia Report',
      },
      {
        name: 'DataReportal',
        url: 'https://datareportal.com/reports/digital-2025-malaysia',
        desc: 'Digital 2025: Malaysia — Global Digital Insights',
      },
      {
        name: 'GroupM',
        url: 'https://www.groupm.com/',
        desc: 'This Year Next Year — Global Mid-Year Forecast',
      },
      {
        name: 'Google, Temasek & Bain',
        url: 'https://economysea.withgoogle.com/',
        desc: 'e-Conomy SEA Report',
      },
      {
        name: 'MCMC',
        desc: 'Malaysian Communications and Multimedia Commission — Internet Users Survey',
      },
    ],
    notes:
      'This data is a compilation of publicly available industry reports. Several figures are projections or estimates from the respective sources. Beriklan Digital Agency does not claim this data as primary research — it is curated and synthesised for convenient industry reference.',
  },

  faqs: [
    {
      q: 'How big is Malaysia digital ad spend in 2026?',
      a: "Malaysia's digital advertising spend is estimated at around USD 1.41 billion in 2026, projected to reach roughly USD 1.83 billion by 2030 (about 6.7% CAGR).",
    },
    {
      q: 'Which digital ad platforms are most popular in Malaysia?',
      a: 'By estimated monthly active users: WhatsApp (~29.4 million), TikTok (~24.8 million), YouTube (~24.1 million), Facebook (~22.4 million) and Instagram (~15.4 million).',
    },
    {
      q: 'How much time do Malaysians spend on social media?',
      a: 'On average around 2 hours 48 minutes per day, spread across multiple platforms. TikTok leads daily engagement time.',
    },
    {
      q: 'What role does social media play in brand discovery in Malaysia?',
      a: 'Roughly a third of consumers discover new brands through social media ads — nearly matching search engines. Social media is now a primary brand-research channel for Malaysian users.',
    },
    {
      q: 'What are the key digital advertising trends in Malaysia for 2026?',
      a: 'Five main trends: (1) Video-first content, (2) AI in advertising — creative localisation & DCO, (3) Social commerce led by TikTok Shop, (4) Data protection — the amended PDPA, (5) Connected TV growth.',
    },
  ],
}

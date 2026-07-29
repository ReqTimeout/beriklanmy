// WordPress-style page sitemap (Yoast: page-sitemap.xml)
// Lists all static pages: homepage + service pages + blog index
const SITE = 'https://beriklan.my';
const TODAY = new Date().toISOString().slice(0, 10);

const pages = [
    { path: '/', priority: '1.0', changefreq: 'weekly' },
    { path: '/blog/', priority: '0.9', changefreq: 'daily' },
    { path: '/order/', priority: '0.8', changefreq: 'monthly' },
    { path: '/digital-marketing-agency/', priority: '0.9', changefreq: 'monthly' },
    { path: '/facebook-ads-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/instagram-ads-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/tiktok-ads-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/google-ads-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/youtube-ads-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/instagram-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/tiktok-management/', priority: '0.9', changefreq: 'monthly' },
    { path: '/website-development/', priority: '0.9', changefreq: 'monthly' },
    { path: '/landing-page-design/', priority: '0.9', changefreq: 'monthly' },
    { path: '/ad-budget-calculator/', priority: '0.8', changefreq: 'monthly' },
    { path: '/roas-calculator/', priority: '0.8', changefreq: 'monthly' },
    { path: '/roi-calculator/', priority: '0.8', changefreq: 'monthly' },
];

export function GET() {
    const urls = pages.map(p => `    <url>
        <loc>${SITE}${p.path}</loc>
        <lastmod>${TODAY}</lastmod>
        <changefreq>${p.changefreq}</changefreq>
        <priority>${p.priority}</priority>
    </url>`).join('\n');

    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="//beriklan.my/sitemap.xsl"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
    return new Response(xml, {
        headers: {
            'Content-Type': 'application/xml; charset=utf-8',
            'Cache-Control': 'public, max-age=3600',
        },
    });
}

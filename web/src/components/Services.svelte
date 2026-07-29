<script>
    import { onMount } from 'svelte';
    import { Megaphone, Camera, Music2, Search, Play, FileText, Globe, Film, Smartphone, ArrowUpRight, Check } from 'lucide-svelte';

    const waLink = "https://wa.me/62811919328?text=Hello%20Beriklan%2C%20I%27d%20like%20a%20free%20consultation";

    let visible = false;
    let activeTab = 'all';

    const categories = [
        { id: 'all', label: 'All', count: 9 },
        { id: 'ads', label: 'Ads', count: 5 },
        { id: 'social', label: 'Social', count: 2 },
        { id: 'web', label: 'Web', count: 2 },
    ];

    const services = [
        {
            id: 'fb',
            cat: 'ads',
            href: '/facebook-ads-management',
            Icon: Megaphone,
            title: 'Facebook Ads',
            promise: 'Reach 24M+ users in Malaysia — filtered by interest, behaviour, right down to lookalikes of your best customers.',
            features: ['Lookalike audience', 'Retargeting pixel', 'Lead gen form', 'Catalog sale'],
            metric: '4.2x',
            metricLabel: 'Median ROAS',
        },
        {
            id: 'ig',
            cat: 'ads',
            href: '/instagram-ads-management',
            Icon: Camera,
            title: 'Instagram Ads',
            promise: 'Reels & Stories designed to grab attention in the first three seconds. Ideal for visual brands and F&B — where buying decisions happen in minutes.',
            features: ['Reels ads', 'Interactive Stories', 'Shopping tags', 'Branded content'],
            metric: '2.3%',
            metricLabel: 'Avg CTR',
        },
        {
            id: 'tt',
            cat: 'ads',
            href: '/tiktok-ads-management',
            Icon: Music2,
            title: 'TikTok Ads',
            promise: 'Native content built to land on the FYP organically. Not empty virality — the formats we produce are designed to move audiences all the way to a sale.',
            features: ['Spark ads', 'In-feed', 'TopView', 'Branded effect'],
            metric: '100s',
            metricLabel: 'Sales/month',
        },
        {
            id: 'ga',
            cat: 'ads',
            href: '/google-ads-management',
            Icon: Search,
            title: 'Google Search Ads',
            promise: 'Capture buyers already googling your product or service. High intent = faster closes and higher value per lead.',
            features: ['Search intent', 'Performance Max', 'Shopping ads', 'Display network'],
            metric: 'RM 0.8',
            metricLabel: 'Avg CPC',
        },
        {
            id: 'yt',
            cat: 'ads',
            href: '/youtube-ads-management',
            Icon: Play,
            title: 'YouTube Ads',
            promise: 'Memorable 6-second bumpers or in-stream video. Brand recall that lasts — not just a month of awareness.',
            features: ['In-stream skippable', '6-second bumpers', 'Discovery', 'YouTube Shorts'],
            metric: '65%',
            metricLabel: 'Avg view rate',
        },
        {
            id: 'lp',
            cat: 'web',
            href: '/landing-page-design',
            Icon: FileText,
            title: 'Landing Page',
            promise: 'A single-screen page built to turn visits into chats or orders. Persuasive copywriting with A/B tests prepared from day one.',
            features: ['Persuasive copywriting', 'A/B test ready', 'Mobile-first', 'Pixel integrated'],
            metric: '< 2s',
            metricLabel: 'Load time',
        },
        {
            id: 'web',
            cat: 'web',
            href: '/website-development',
            Icon: Globe,
            title: 'Custom Website',
            promise: 'Not an off-the-shelf template. Custom design, fast load, SEO-ready from day one — a proper digital home for your business.',
            features: ['Custom design', 'CMS integration', 'On-page SEO', 'Mobile-perfect'],
            metric: '< 3s',
            metricLabel: 'Load time',
        },
        {
            id: 'kt',
            cat: 'social',
            href: '/tiktok-management',
            Icon: Film,
            title: 'TikTok Management',
            promise: 'Up to 20 videos/month, from script to report. You approve the concepts, we execute. Perfect for teams with no time to spare.',
            features: ['Scriptwriting', 'Professional editing', 'Posting schedule', 'Monthly report'],
            metric: '20',
            metricLabel: 'Videos/mo',
        },
        {
            id: 'ki',
            cat: 'social',
            href: '/instagram-management',
            Icon: Smartphone,
            title: 'Instagram Management',
            promise: 'A polished feed, active Stories, DMs answered. Sales keep flowing without daily supervision — you focus on the business.',
            features: ['Polished feed', 'Active Stories', 'Regular Reels', 'DM responses'],
            metric: '100s',
            metricLabel: 'Engagements/mo',
        },
    ];

    $: filteredServices = activeTab === 'all' ? services : services.filter(s => s.cat === activeTab);

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        }, { threshold: 0.05 });
        const el = document.getElementById('services');
        if (el) observer.observe(el);
        setTimeout(() => { visible = true; }, 1000);
    });
</script>

<section id="services" class="py-20 md:py-28 bg-gradient-to-b from-white to-soft relative overflow-hidden">
    <!-- Floating SVG illustrations -->
    <div class="absolute top-12 left-4 w-36 h-36 opacity-60 pointer-events-none hidden md:block" aria-hidden="true">
        <svg viewBox="0 0 100 100" class="w-full h-full">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#f59e0b" stroke-opacity="0.2" stroke-width="1.5" stroke-dasharray="2 6"/>
            <circle cx="50" cy="50" r="22" fill="#f59e0b" fill-opacity="0.08">
                <animate attributeName="r" values="22;26;22" dur="3s" repeatCount="indefinite"/>
            </circle>
            <text x="50" y="58" text-anchor="middle" font-size="26" fill="#f59e0b" fill-opacity="0.7" font-weight="900">9</text>
            <text x="50" y="84" text-anchor="middle" font-size="7" fill="#0f1e3d" fill-opacity="0.5" font-weight="700" letter-spacing="1.5">SERVICES</text>
        </svg>
    </div>
    <div class="absolute bottom-24 right-4 w-28 h-28 opacity-40 pointer-events-none hidden md:block" aria-hidden="true">
        <svg viewBox="0 0 100 100" class="w-full h-full">
            <path d="M15,80 Q40,20 85,15" stroke="#0ea5e9" stroke-opacity="0.5" stroke-width="3" fill="none" stroke-linecap="round"/>
            <circle cx="85" cy="15" r="5" fill="#0ea5e9">
                <animate attributeName="r" values="5;8;5" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="15" cy="80" r="3" fill="#0ea5e9" fill-opacity="0.5"/>
        </svg>
    </div>

    <div class="container mx-auto px-6 relative">
        <div class="text-center max-w-2xl mx-auto mb-10 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                <span class="w-8 h-px bg-accent"></span>
                9 Services, One Mind
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                Everything performance<br/>
                <span class="text-accent">marketing, in one place.</span>
            </h2>
            <p class="mt-4 text-muted max-w-xl mx-auto text-base leading-relaxed">
                No need to coordinate 3 different vendors. Ads, landing pages, social media — all built as one system that reinforces itself.
            </p>
        </div>

        <!-- Filter tabs -->
        <div class="flex flex-wrap items-center justify-center gap-1.5 mb-10 p-1.5 bg-white rounded-full max-w-md mx-auto border border-gray-100 shadow-soft">
            {#each categories as cat}
                <button
                    type="button"
                    on:click={() => activeTab = cat.id}
                    class="tab-btn px-4 py-2 rounded-full text-xs md:text-sm font-bold transition-all flex-1 flex items-center justify-center gap-1.5
                    {activeTab === cat.id ? 'bg-ink text-white shadow-md' : 'text-muted hover:text-ink'}"
                >
                    {cat.label}
                    <span class="text-[10px] {activeTab === cat.id ? 'text-accent' : 'text-muted'} font-bold">{cat.count}</span>
                </button>
            {/each}
        </div>

        <div class="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 reveal-stagger">
            {#each filteredServices as s, i (s.id)}
                <a
                    href={s.href}
                    class="svc-card group relative bg-white rounded-2xl border border-gray-100 p-5 md:p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-pop hover:border-accent/40 overflow-hidden"
                    style="transition-delay: {i * 50}ms;"
                >
                    <span class="svc-watermark absolute -top-2 -right-2 text-[80px] font-display font-black text-gray-50 leading-none select-none transition-colors duration-500 group-hover:text-accent/10">
                        {String(i + 1).padStart(2, '0')}
                    </span>

                    <div class="relative flex items-start justify-between mb-4">
                        <div class="svc-icon w-11 h-11 rounded-xl bg-ink/5 text-ink flex items-center justify-center transition-all duration-300">
                            <svelte:component this={s.Icon} size="20" strokeWidth="2" />
                        </div>
                        <div class="text-right">
                            <div class="text-xl font-display font-extrabold text-accent leading-none">{s.metric}</div>
                            <div class="text-[9px] font-bold uppercase tracking-wider text-muted mt-1">{s.metricLabel}</div>
                        </div>
                    </div>

                    <div class="relative">
                        <h3 class="font-display font-extrabold text-lg md:text-xl text-ink leading-tight mb-2 transition-colors duration-300">
                            {s.title}
                        </h3>
                        <p class="text-xs md:text-sm text-muted leading-relaxed mb-3">
                            {s.promise}
                        </p>
                    </div>

                    <div class="relative flex flex-wrap gap-1 mb-4">
                        {#each s.features.slice(0, 3) as f}
                            <span class="text-[10px] font-medium text-ink bg-soft border border-gray-100 px-2 py-0.5 rounded-full">
                                {f}
                            </span>
                        {/each}
                        {#if s.features.length > 3}
                            <span class="text-[10px] font-bold text-accent">+{s.features.length - 3}</span>
                        {/if}
                    </div>

                    <div class="relative flex items-center justify-between">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-muted flex items-center gap-1 group-hover:text-accent transition-colors">
                            <Check size="10" strokeWidth="3" class="svc-check opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
                            <span class="svc-text opacity-0 group-hover:opacity-100 transition-opacity">Detail</span>
                        </span>
                        <span class="svc-arrow w-7 h-7 rounded-full bg-soft flex items-center justify-center text-ink transition-all duration-300">
                            <ArrowUpRight size="14" strokeWidth="2.5" />
                        </span>
                    </div>
                </a>
            {/each}
        </div>

        <div class="mt-10 text-center anim-fade-up">
            <p class="text-sm text-muted">
                Need a recommendation or want to discuss budget?
                <a href={waLink} class="text-accent font-bold hover:underline ml-1 group inline-flex items-center gap-1">
                    Free consultation on WhatsApp
                    <span class="group-hover:translate-x-1 transition-transform">→</span>
                </a>
            </p>
        </div>
    </div>
</section>

<style>
    .svc-card {
        transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1),
                    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
                    box-shadow 0.3s ease,
                    border-color 0.3s ease;
    }
    .svc-card:hover .svc-icon { background: #f59e0b; color: #0f1e3d; transform: rotate(-4deg); }
    .svc-card:hover .svc-arrow { background: #f59e0b; color: #0f1e3d; transform: translate(2px, -2px); }

    .tab-btn { transition: background-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease; }
    .tab-btn:active { transform: scale(0.97); }
</style>

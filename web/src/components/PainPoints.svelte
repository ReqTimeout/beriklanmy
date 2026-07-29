<script>
    import { onMount } from 'svelte';
    import { TrendingDown, LineChart, CircleHelp, X, ArrowRight } from 'lucide-svelte';

    let visible = false;

    const pains = [
        {
            num: '01',
            Icon: TrendingDown,
            title: 'Budget going out, sales not moving',
            body: 'Ad spend goes out every day, yet sales stay flat. Usually the targeting is too broad or the creative is misaligned with the audience — and you only feel it after a month has passed.',
            tag: 'Wasted Spend',
        },
        {
            num: '02',
            Icon: LineChart,
            title: 'Routine reports, no strategic direction',
            body: 'Your agency sends CPM-CTR-CPC reports every week. The numbers are confusing. No context, no concrete recommendations — just a display of metrics.',
            tag: 'No Clarity',
        },
        {
            num: '03',
            Icon: CircleHelp,
            title: 'Unsure which platform to choose',
            body: 'Meta first? Or Google? TikTok? Each platform has a different audience character. The wrong pick means 3–6 months wasted and a drained budget with no measurable results.',
            tag: 'Wrong Channel',
        },
    ];

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        }, { threshold: 0.08 });
        const el = document.getElementById('pain-points');
        if (el) observer.observe(el);
        setTimeout(() => { visible = true; }, 1500);
    });
</script>

<section id="pain-points" class="py-20 md:py-28 bg-soft relative overflow-hidden">
    <!-- Decorative downward chart -->
    <svg class="absolute right-2 top-20 w-44 h-44 opacity-50 hidden md:block" viewBox="0 0 100 100" aria-hidden="true">
        <defs>
            <linearGradient id="ppGrad" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.7"/>
                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
            </linearGradient>
        </defs>
        <polygon points="15,55 30,50 45,55 60,40 75,30 90,35" fill="none" stroke="url(#ppGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="15" cy="55" r="2.5" fill="#f59e0b"/>
        <circle cx="30" cy="50" r="2.5" fill="#f59e0b"/>
        <circle cx="45" cy="55" r="2.5" fill="#f59e0b"/>
        <circle cx="60" cy="40" r="2.5" fill="#f59e0b"/>
        <circle cx="75" cy="30" r="2.5" fill="#f59e0b"/>
        <circle cx="90" cy="35" r="3" fill="#f59e0b">
            <animate attributeName="r" values="3;5;3" dur="1.8s" repeatCount="indefinite"/>
        </circle>
        <text x="50" y="78" text-anchor="middle" font-size="7" font-weight="800" fill="#f59e0b" fill-opacity="0.55" letter-spacing="2">DOWN ↓</text>
    </svg>

    <div class="container mx-auto px-6 relative">
        <div class="text-center max-w-2xl mx-auto mb-14 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                <span class="w-8 h-px bg-accent"></span>
                Signs Your Business Needs Us
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-4">
                Three patterns that keep<br/>
                <span class="text-accent">your ad performance stagnant.</span>
            </h2>
            <p class="mt-5 text-muted max-w-xl mx-auto text-base leading-relaxed">
                If one of these feels close to home, you are not alone. These situations usually happen to businesses that have never been handled by a team that understands the full funnel.
            </p>
        </div>

        <div class="grid md:grid-cols-3 gap-5 lg:gap-6 max-w-6xl mx-auto reveal-stagger">
            {#each pains as pain, i}
                <div
                    class="pp-card group relative bg-white rounded-2xl p-7 md:p-8 border border-gray-100 shadow-soft hover:shadow-pop transition-all duration-300 hover:-translate-y-2 hover:border-accent/40 overflow-hidden"
                >
                    <!-- Watermark number -->
                    <div class="pp-watermark absolute -right-4 -top-6 text-[120px] font-display font-black text-gray-50 leading-none select-none transition-colors duration-500 group-hover:text-accent/10">
                        {pain.num}
                    </div>

                    <!-- Top: icon + tag -->
                    <div class="relative flex items-center justify-between mb-5">
                        <div class="pp-icon w-14 h-14 rounded-2xl bg-accent/10 text-accent flex items-center justify-center">
                            <svelte:component this={pain.Icon} size="28" strokeWidth="2" />
                        </div>
                        <span class="text-[10px] font-bold uppercase tracking-wider text-muted bg-soft px-2.5 py-1 rounded-full group-hover:bg-accent group-hover:text-ink transition-colors">
                            {pain.tag}
                        </span>
                    </div>

                    <!-- Animated accent bar -->
                    <div class="relative h-1 w-12 rounded-full bg-gradient-to-r from-accent to-orange-500 mb-4 pp-bar"></div>

                    <h3 class="font-display font-bold text-lg md:text-xl text-ink leading-snug mb-3 relative">
                        "{pain.title}"
                    </h3>
                    <p class="text-muted text-sm leading-relaxed relative">
                        {pain.body}
                    </p>

                    <!-- Hover arrow -->
                    <div class="relative mt-5 pt-4 border-t border-gray-100 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-accent flex items-center gap-1">
                            The solution?
                            <ArrowRight class="w-3 h-3" />
                        </span>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Promise pill -->
        <div class="mt-12 max-w-3xl mx-auto text-center reveal-lift">
            <div class="pp-promise inline-flex items-center gap-3 px-5 py-3 bg-white border border-accent/30 rounded-full shadow-soft">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-green"></span>
                </span>
                <p class="text-sm text-ink font-semibold">
                    All three can be addressed within <span class="text-accent">30–90 days</span> with a measurable system.
                </p>
            </div>
        </div>
    </div>
</section>

<style>
    .pp-card {
        transition: opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                    transform 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                    box-shadow 0.3s ease,
                    border-color 0.3s ease;
    }
    .pp-card:hover .pp-icon {
        animation: wiggle 0.6s ease;
    }
    @keyframes wiggle {
        0%, 100% { transform: rotate(0); }
        30% { transform: rotate(-6deg) scale(1.06); }
        60% { transform: rotate(6deg) scale(1.06); }
    }
    .pp-bar { transition: width 0.4s cubic-bezier(0.22, 1, 0.36, 1); }
    .pp-card:hover .pp-bar { width: 5rem; }

    /* Promise pulse — already visible after section reveals */
    .pp-promise { will-change: transform; }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>

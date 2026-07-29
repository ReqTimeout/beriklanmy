<script>
    import { onMount } from 'svelte';
    import { MessagesSquare, Hammer, TrendingUp, ArrowRight } from 'lucide-svelte';

    let visible = false;

    const steps = [
        {
            num: '01',
            Icon: MessagesSquare,
            title: 'Diagnose',
            headline: 'We listen first. Then act.',
            desc: 'A 30-minute kick-off — we dig into goals, budget, audience, blockers, plus what you have already tried. Output: an execution brief the team works from.',
            tag: 'WEEK 1',
            deliverable: 'Strategy Brief',
            deliverables: ['Existing account audit', 'Persona & mapping', 'Channel decision'],
        },
        {
            num: '02',
            Icon: Hammer,
            title: 'Execute',
            headline: 'Build, launch, monitor.',
            desc: 'Copy, visuals, video, tracking setup — all in parallel. Campaigns go live in week 2. You approve every milestone, we execute.',
            tag: 'WEEK 2',
            deliverable: 'Campaign Live',
            deliverables: ['Creatives ready to run', 'Pixel & tracking verified', 'A/B tests active'],
        },
        {
            num: '03',
            Icon: TrendingUp,
            title: 'Optimise',
            headline: 'Monitor closely. Iterate fast.',
            desc: 'Weekly reviews driven by data — not assumptions. Underperformers get replaced. Winners get scaled. You just approve the summary.',
            tag: 'WEEK 3+',
            deliverable: 'Scale-up',
            deliverables: ['Plain-language reports', 'Fast pivots', 'Scaling the winners'],
        },
    ];

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        }, { threshold: 0.1 });
        const el = document.getElementById('method');
        if (el) observer.observe(el);
        setTimeout(() => { visible = true; }, 800);
    });
</script>

<section id="method" class="py-20 md:py-28 bg-white relative overflow-hidden">
    <div class="absolute inset-0 opacity-30 pointer-events-none method-dots"></div>

    <!-- Decorative curved dashed arrow -->
    <svg class="absolute top-24 left-8 w-32 h-12 opacity-50 hidden md:block" viewBox="0 0 120 40" aria-hidden="true">
        <path d="M5,30 Q60,0 110,30" stroke="#f59e0b" stroke-width="1.5" fill="none" stroke-dasharray="4 5"/>
        <polygon points="110,30 102,22 102,38" fill="#f59e0b"/>
    </svg>
    <svg class="absolute bottom-32 right-8 w-24 h-12 opacity-50 hidden md:block" viewBox="0 0 100 40" aria-hidden="true">
        <path d="M5,10 Q50,40 95,10" stroke="#0ea5e9" stroke-width="1.5" fill="none" stroke-dasharray="4 5"/>
    </svg>

    <div class="container mx-auto px-6 relative">
        <div class="max-w-2xl mx-auto text-center mb-14 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                <span class="w-6 h-px bg-accent"></span>
                How We Work · Three Structured Phases
                <span class="w-6 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                From early doubts<br/>
                <span class="text-accent">to a measurable advertising system.</span>
            </h2>
            <p class="mt-4 text-muted text-base">
                No inflated promises. No opaque processes. Every week, you know exactly what we are working on and why.
            </p>
        </div>

        <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 relative reveal-stagger">
            <!-- Connector line -->
            <div class="hidden md:block absolute top-[88px] left-[16.67%] right-[16.67%] h-px z-0 method-line"></div>

            {#each steps as step, i}
                <div
                    class="method-card group relative bg-white rounded-2xl p-6 md:p-7 border border-gray-100 hover:border-accent/40 transition-all duration-300 z-10"
                    style="transition-delay: {i * 130}ms;"
                >
                    <!-- Top: number + tag -->
                    <div class="flex items-center justify-between mb-5">
                        <span class="text-[10px] font-bold uppercase tracking-widest text-muted">{step.num}</span>
                        <span class="text-[9px] font-bold uppercase tracking-wider text-accent bg-accent/10 px-2 py-0.5 rounded-full">
                            {step.tag}
                        </span>
                    </div>

                    <!-- Icon -->
                    <div class="method-icon w-14 h-14 rounded-2xl bg-ink text-white flex items-center justify-center mb-5 transition-all duration-300">
                        <svelte:component this={step.Icon} size="26" strokeWidth="2" />
                    </div>

                    <h3 class="font-display font-extrabold text-xl text-ink mb-1">{step.title}</h3>
                    <p class="text-sm font-bold text-accent mb-3">{step.headline}</p>
                    <p class="text-sm text-muted leading-relaxed mb-5">{step.desc}</p>

                    <!-- Deliverable items list -->
                    <ul class="space-y-1.5 mb-5">
                        {#each step.deliverables as d, j}
                            <li class="method-list-item flex items-start gap-2 text-xs text-muted">
                                <svg class="w-3.5 h-3.5 text-accent mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                <span>{d}</span>
                            </li>
                        {/each}
                    </ul>

                    <!-- Deliverable pill -->
                    <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                        <span class="text-[10px] uppercase tracking-wider font-bold text-muted">This week's output</span>
                        <span class="text-xs font-bold text-ink inline-flex items-center gap-1 method-pill">
                            {step.deliverable}
                            <ArrowRight class="w-3 h-3 text-accent method-arrow" />
                        </span>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Bottom CTA -->
        <div class="mt-14 text-center">
            <a href="https://wa.me/62811919328?text=Hello%20Beriklan%2C%20I%27d%20like%20a%20free%20consultation" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-ink text-white px-7 py-3.5 rounded-full font-bold text-sm hover:bg-accent hover:text-ink transition-all shadow-md group anim-fade-up btn-shine" style="animation-delay: 600ms;">
                <span class="relative z-10 flex items-center gap-2">
                    Ask Us on WhatsApp
                    <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
            </a>
        </div>
    </div>
</section>

<style>
    .method-card {
        transition: opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                    transform 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                    box-shadow 0.3s ease,
                    border-color 0.3s ease;
    }
    .method-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px -8px rgba(15, 30, 61, 0.15);
    }
    .method-card:hover .method-icon {
        background: #f59e0b;
        transform: rotate(-6deg) scale(1.05);
    }
    .method-card:hover .method-pill { color: #f59e0b; }
    .method-card:hover .method-arrow { transform: translateX(4px); }

    .method-line {
        background: linear-gradient(90deg, transparent 0%, #f59e0b 50%, transparent 100%);
        background-size: 200% 100%;
        animation: line-flow 3s linear infinite;
    }
    @keyframes line-flow {
        from { background-position: 100% 0; }
        to { background-position: -100% 0; }
    }

    .method-dots {
        background-image: radial-gradient(circle at 2px 2px, rgba(15,30,61,0.05) 1px, transparent 0);
        background-size: 32px 32px;
    }

    .method-list-item {
        opacity: 0;
        animation: fadeUp 0.5s ease forwards;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateX(-6px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .btn-shine { position: relative; overflow: hidden; }
    .btn-shine::after {
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.18) 50%, transparent 75%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    .btn-shine:hover::after { transform: translateX(100%); }
</style>

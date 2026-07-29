<script>
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    const faqs = [
        {
            q: 'What is the minimum budget to get started?',
            a: 'A minimum of RM 500 per month for ad spend, plus the management fee of the package you choose. That amount is enough to read early data within 2–4 weeks. For more stable, sustainable results, we generally recommend starting from RM 1,500–3,000 per month.'
        },
        {
            q: 'How long until results start showing?',
            a: 'Realistically: 2–4 weeks to read early data, 1–3 months to find a stable pattern. The timeline varies by industry, platform and budget size. We do not promise instant results — what we do commit to: consistent optimisation based on real data, not assumptions.'
        },
        {
            q: 'How are you different from other agencies?',
            a: 'Three things: (1) you own the Meta/Google/TikTok accounts — we only manage them; (2) reports in plain language you can actually read, not CPM-CTR-CPC jargon without context; (3) no 6–12 month lock-in — month to month, you are free to leave anytime.'
        },
        {
            q: 'What do I need to prepare?',
            a: 'Just a short business profile and access to your ad accounts (if you already have them). If you don\'t, we set everything up from scratch — Meta Pixel, Google Tag, TikTok Pixel, all handled.'
        },
        {
            q: 'Can packages be customised?',
            a: 'Yes. Our recommendations are usually built around your ad budget and primary objective — whether that is building brand awareness or driving conversions. For unusual requirements, we will discuss it with you personally first, free of charge.'
        },
        {
            q: 'How long from first consultation until ads go live?',
            a: 'On average 7–14 days after we receive your brief. That includes ad account preparation, ad materials (photos, video, copy) and pixel tracking. If your materials are already ready, it is usually faster.'
        },
        {
            q: 'What if results miss the target?',
            a: 'We run an open evaluation in the second and third month. If our approach clearly does not fit the character of your business, we will recommend a change of strategy or a partial refund. This rarely happens — but we are transparent about the possibility from day one.'
        },
        {
            q: 'Why don\'t you guarantee ROAS?',
            a: 'Because ROAS depends on many factors outside our control (product, pricing, funnel, landing page). What we do guarantee: maximum effort + data-driven optimisation + honest reporting. No magic tricks.'
        },
    ];

    let openIdx = -1;
    function toggle(i) {
        openIdx = openIdx === i ? -1 : i;
    }
</script>

<div class="reveal-stagger max-w-3xl mx-auto space-y-3">
    {#each faqs as item, i}
        <div class="faq-item bg-white border border-gray-100 rounded-xl overflow-hidden shadow-soft transition-all duration-300 hover:shadow-pop hover:border-accent/30">
            <button
                type="button"
                on:click={() => toggle(i)}
                class="w-full text-left px-6 py-5 flex items-center justify-between gap-4 group"
                aria-expanded={openIdx === i}
            >
                <span class="font-display font-bold text-base md:text-lg text-ink group-hover:text-accent transition-colors leading-snug">
                    {item.q}
                </span>
                <span class="faq-toggle shrink-0 w-8 h-8 rounded-full bg-soft flex items-center justify-center group-hover:bg-accent group-hover:text-ink transition-all">
                    <svg class="w-4 h-4 transition-transform duration-300" class:rotate-45={openIdx === i} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
                    </svg>
                </span>
            </button>
            {#if openIdx === i}
                <div transition:slide={{ duration: 250, easing: quintOut }}>
                    <div class="px-6 pb-5 pt-0 text-muted leading-relaxed text-sm md:text-base border-t border-gray-50">
                        <p class="pt-4">{item.a}</p>
                    </div>
                </div>
            {/if}
        </div>
    {/each}
</div>

<style>
    .faq-item-enter {
        opacity: 0;
        transform: translateY(14px);
        animation: faqIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }
    @keyframes faqIn {
        to { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
        .faq-item-enter { animation: none; opacity: 1; transform: none; }
    }
</style>

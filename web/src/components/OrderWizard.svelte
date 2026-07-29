<script>
    import { MessageCircle, ArrowRight, ArrowLeft, Check, Sparkles, Building2 } from 'lucide-svelte';

    let step = 1;
    let selectedServices = [];
    let budget = '';
    let business = { name: '', contact: '', notes: '' };

    const services = [
        { id: 'fb', label: 'Facebook Ads', desc: 'Targeted advertising', emoji: '📘' },
        { id: 'ig', label: 'Instagram Ads', desc: 'Visual storytelling', emoji: '📷' },
        { id: 'tt', label: 'TikTok Ads', desc: 'Reach FYP & convert', emoji: '🎵' },
        { id: 'gads', label: 'Google Search Ads', desc: 'Capture high intent', emoji: '🔍' },
        { id: 'yt', label: 'YouTube Ads', desc: 'Brand awareness video', emoji: '🎬' },
        { id: 'kelola-ig', label: 'Instagram Management', desc: 'Content management', emoji: '📲' },
        { id: 'kelola-tt', label: 'TikTok Management', desc: 'Short-video management', emoji: '🎤' },
        { id: 'web', label: 'Website Development', desc: 'Professional, multi-page', emoji: '🌐' },
        { id: 'lp', label: 'Landing Page + Ads', desc: 'Promo bundle RM 1,299', emoji: '🚀' },
    ];

    const budgets = [
        { id: 'starter', label: 'Under RM 1,500', desc: 'For early testing' },
        { id: 'mid', label: 'RM 1,500 - 5,000', desc: 'For active campaigns' },
        { id: 'pro', label: 'RM 5,000 - 12,000', desc: 'For scaling up' },
        { id: 'enterprise', label: 'Above RM 12,000', desc: 'For multi-channel' },
        { id: 'unsure', label: 'Not sure yet', desc: 'Let us discuss first' },
    ];

    function toggleService(id) {
        if (selectedServices.includes(id)) {
            selectedServices = selectedServices.filter(s => s !== id);
        } else {
            selectedServices = [...selectedServices, id];
        }
    }

    function nextStep() {
        if (step < 4) step++;
    }

    function prevStep() {
        if (step > 1) step--;
    }

    function submit() {
        const serviceNames = selectedServices.map(id => services.find(s => s.id === id)?.label).join(', ');
        const budgetLabel = budgets.find(b => b.id === budget)?.label || '';
        // Push generate_lead to GTM dataLayer before opening WhatsApp
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
            event: 'generate_lead',
            event_category: 'conversion',
            event_label: 'order_wizard_submit',
            services: serviceNames,
            budget: budgetLabel,
            business_name: business.name,
            page_location: window.location.pathname,
            value: 1,
            currency: 'MYR'
        });
        const msg = encodeURIComponent(
            `Hello Beriklan, I would like to discuss:\n\n` +
            `Services: ${serviceNames}\n` +
            `Budget: ${budgetLabel}\n` +
            `Business: ${business.name}\n` +
            `Contact: ${business.contact}\n` +
            (business.notes ? `Notes: ${business.notes}` : '')
        );
        window.open(`https://wa.me/62811919328?text=${msg}`, '_blank');
    }
</script>

<div class="bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
    <!-- Progress bar -->
    <div class="bg-soft px-5 py-3 border-b border-gray-100">
        <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-bold uppercase tracking-wider text-muted">Step {step} of 3</span>
            <span class="text-[10px] font-bold text-accent">{Math.round((step / 3) * 100)}%</span>
        </div>
        <div class="h-1.5 bg-white rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-accent to-accent-2 rounded-full transition-all duration-500" style="width: {(step / 3) * 100}%;"></div>
        </div>
    </div>

    <div class="p-5 md:p-7">
        {#if step === 1}
            <!-- Step 1: Service selection -->
            <h3 class="font-display font-extrabold text-xl text-ink mb-1">Which services do you need?</h3>
            <p class="text-sm text-muted mb-5">Select one or more. You can discuss the details in your consultation session.</p>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 reveal-stagger">
                {#each services as svc}
                    <button
                        type="button"
                        class="service-chip group p-3 rounded-xl border-2 transition-all duration-200 text-left {selectedServices.includes(svc.id) ? 'border-accent bg-accent/5' : 'border-gray-100 hover:border-gray-300'}"
                        on:click={() => toggleService(svc.id)}
                    >
                        <div class="text-xl mb-1">{svc.emoji}</div>
                        <p class="text-xs font-bold text-ink leading-tight">{svc.label}</p>
                        <p class="text-[10px] text-muted leading-tight mt-0.5">{svc.desc}</p>
                        {#if selectedServices.includes(svc.id)}
                            <div class="absolute top-1.5 right-1.5 w-4 h-4 bg-accent rounded-full flex items-center justify-center">
                                <Check class="w-2.5 h-2.5 text-ink" strokeWidth="3" />
                            </div>
                        {/if}
                    </button>
                {/each}
            </div>
        {:else if step === 2}
            <!-- Step 2: Budget -->
            <h3 class="font-display font-extrabold text-xl text-ink mb-1">What budget have you prepared?</h3>
            <p class="text-sm text-muted mb-5">Including ad spend + service fees. Not sure? Choose "Not sure yet".</p>
            <div class="space-y-2.5 reveal-stagger">
                {#each budgets as b}
                    <button
                        type="button"
                        class="budget-chip group w-full p-4 rounded-xl border-2 transition-all duration-200 text-left flex items-center gap-3 {budget === b.id ? 'border-accent bg-accent/5' : 'border-gray-100 hover:border-gray-300'}"
                        on:click={() => budget = b.id}
                    >
                        <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 {budget === b.id ? 'border-accent' : 'border-gray-300'}">
                            {#if budget === b.id}
                                <div class="w-2.5 h-2.5 rounded-full bg-accent"></div>
                            {/if}
                        </div>
                        <div class="flex-1">
                            <p class="text-sm font-bold text-ink">{b.label}</p>
                            <p class="text-xs text-muted">{b.desc}</p>
                        </div>
                        {#if budget === b.id}
                            <Check class="w-5 h-5 text-accent" strokeWidth="3" />
                        {/if}
                    </button>
                {/each}
            </div>
        {:else}
            <!-- Step 3: Business info -->
            <h3 class="font-display font-extrabold text-xl text-ink mb-1">Tell us a little about your business</h3>
            <p class="text-sm text-muted mb-5">This helps us prepare recommendations that are relevant to you.</p>
            <div class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-ink mb-1.5" for="biz-name">Business / brand name</label>
                    <input id="biz-name" type="text" bind:value={business.name} placeholder="e.g. Beauty Studio KL" class="w-full px-4 py-3 bg-soft border border-gray-200 rounded-xl text-sm focus:border-accent focus:bg-white outline-none transition" />
                </div>
                <div>
                    <label class="block text-xs font-bold text-ink mb-1.5" for="biz-contact">WhatsApp number / email</label>
                    <input id="biz-contact" type="text" bind:value={business.contact} placeholder="e.g. 012-345 6789 or info@business.com" class="w-full px-4 py-3 bg-soft border border-gray-200 rounded-xl text-sm focus:border-accent focus:bg-white outline-none transition" />
                </div>
                <div>
                    <label class="block text-xs font-bold text-ink mb-1.5" for="biz-notes">Additional notes <span class="text-muted font-normal">(optional)</span></label>
                    <textarea id="biz-notes" bind:value={business.notes} placeholder="e.g. target market, current challenges, or specific questions..." rows="3" class="w-full px-4 py-3 bg-soft border border-gray-200 rounded-xl text-sm focus:border-accent focus:bg-white outline-none transition resize-none"></textarea>
                </div>
            </div>
        {/if}

        <!-- Navigation -->
        <div class="mt-7 pt-5 border-t border-gray-100 flex items-center justify-between">
            {#if step > 1}
                <button type="button" on:click={prevStep} class="inline-flex items-center gap-1.5 text-sm font-bold text-muted hover:text-ink transition-colors">
                    <ArrowLeft class="w-4 h-4" /> Back
                </button>
            {:else}
                <span></span>
            {/if}

            {#if step < 3}
                <button type="button" on:click={nextStep} disabled={step === 1 ? selectedServices.length === 0 : !budget} class="inline-flex items-center gap-1.5 bg-ink text-white px-5 py-3 rounded-full font-bold text-sm hover:bg-accent hover:text-ink transition-all disabled:opacity-40 disabled:cursor-not-allowed">
                    Next <ArrowRight class="w-4 h-4" />
                </button>
            {:else}
                <button type="button" on:click={submit} disabled={!business.name || !business.contact} data-cta="order_submit" data-cta-location="order_wizard" data-track="order_wizard_submit" data-service={selectedServices.join(',')} data-price={budget} class="inline-flex items-center gap-1.5 bg-gradient-to-r from-accent to-accent-2 text-ink px-5 py-3 rounded-full font-bold text-sm hover:shadow-pop transition-all disabled:opacity-40 disabled:cursor-not-allowed btn-shine">
                    <MessageCircle class="w-4 h-4" /> Send via WhatsApp
                    <span class="cta-shine absolute inset-0 opacity-0 group-hover:opacity-100"></span>
                </button>
            {/if}
        </div>
    </div>
</div>

<style>
    .service-chip { position: relative; }
    .service-chip:hover { transform: translateY(-2px); }

    .budget-chip { position: relative; }
    .budget-chip:hover { transform: translateX(2px); }

    .btn-shine { position: relative; overflow: hidden; }
    .btn-shine::after {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.4) 50%, transparent 75%);
        transform: translateX(-100%);
        animation: shine 3s linear infinite;
    }
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(150%); }
    }

    .cta-shine {
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.3) 50%, transparent 75%);
        transform: translateX(-100%);
        transition: opacity 0.3s ease;
    }
    .group:hover .cta-shine { animation: shine 0.8s ease forwards; }
</style>

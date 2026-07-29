<script>
    let adSpend = 5000;
    let revenue = 15000;
    let result = null;

    $: if (adSpend > 0 && revenue > 0) {
        const roas = revenue / adSpend;
        result = {
            value: roas.toFixed(2),
            rating: roas >= 4 ? 'good' : roas >= 2 ? 'fair' : 'needs-work',
            label: roas >= 4 ? 'Good' : roas >= 2 ? 'Fair' : 'Needs Optimisation',
            color: roas >= 4 ? 'text-green-400' : roas >= 2 ? 'text-accent' : 'text-red-400',
            bg: roas >= 4 ? 'bg-green-500/20' : roas >= 2 ? 'bg-accent/20' : 'bg-red-500/20',
            bar: Math.min(roas / 8 * 100, 100),
        };
    } else {
        result = null;
    }

    function formatCurrency(val) {
        return 'RM ' + val.toLocaleString('en-MY');
    }
</script>

<div class="bg-white border border-gray-100 rounded-2xl p-6 md:p-8 shadow-soft">
    <h3 class="font-display font-bold text-lg md:text-xl text-ink mb-1">ROAS Calculator</h3>
    <p class="text-sm text-muted mb-6">Return on Ad Spend — measure how effective your ad spend is.</p>

    <div class="grid md:grid-cols-2 gap-6 mb-6">
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Total Ad Spend</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">RM</span>
                <input type="number" bind:value={adSpend} min="0" step="100"
                    class="w-full pl-10 pr-4 py-3.5 bg-soft border border-gray-200 rounded-xl text-ink font-bold text-lg focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Total Revenue from Ads</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">RM</span>
                <input type="number" bind:value={revenue} min="0" step="100"
                    class="w-full pl-10 pr-4 py-3.5 bg-soft border border-gray-200 rounded-xl text-ink font-bold text-lg focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
    </div>

    {#if result}
        <div class="bg-ink rounded-2xl p-6 text-center">
            <p class="text-white/50 text-xs font-bold uppercase tracking-wider mb-1">Your ROAS</p>
            <p class="font-display font-extrabold text-5xl md:text-6xl text-white">{result.value}x</p>
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold mt-3 {result.bg} {result.color}">
                {#if result.rating === 'good'}🟢{:else if result.rating === 'fair'}🟡{:else}🔴{/if}
                {result.label}
            </div>

            <div class="mt-5 bg-white/5 rounded-xl p-4">
                <div class="flex justify-between text-xs text-white/50 mb-2">
                    <span>0</span>
                    <span>Benchmark: 4x+ = Good</span>
                    <span>8x+</span>
                </div>
                <div class="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700 {result.rating === 'good' ? 'bg-green-500' : result.rating === 'fair' ? 'bg-accent' : 'bg-red-500'}" style="width: {result.bar}%"></div>
                </div>
            </div>

            <div class="mt-4 text-left text-xs text-white/60 space-y-1">
                {#if result.rating === 'needs-work'}
                    <p>💡 ROAS below 2x means the campaign needs a review — targeting, creative or the landing page may need adjusting.</p>
                {:else if result.rating === 'fair'}
                    <p>💡 ROAS of 2-4x is decent. Further optimisation can push it to 4x+.</p>
                {:else}
                    <p>✅ ROAS above 4x is excellent. Consider scaling your budget for bigger results.</p>
                {/if}
            </div>
        </div>
    {:else}
        <div class="bg-soft rounded-2xl p-6 text-center">
            <p class="text-muted text-sm">Enter your ad spend and revenue figures to see your ROAS.</p>
        </div>
    {/if}

    <div class="mt-4 text-center">
        <a href="https://wa.me/62811919328?text=Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20my%20campaign%20ROAS." target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-sm font-bold text-accent hover:text-ink transition-colors">
            Discuss ROAS with the Beriklan Team →
        </a>
    </div>
</div>

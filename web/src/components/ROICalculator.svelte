<script>
    let adSpend = 5000;
    let productionCost = 2000;
    let managementFee = 1490;
    let totalRevenue = 20000;
    let result = null;

    $: {
        const totalCost = adSpend + productionCost + managementFee;
        if (totalCost > 0 && totalRevenue >= 0) {
            const profit = totalRevenue - totalCost;
            const roi = (profit / totalCost) * 100;
            result = {
                roi: roi.toFixed(1),
                profit: profit,
                totalCost: totalCost,
                rating: roi >= 100 ? 'good' : roi >= 0 ? 'fair' : 'loss',
                label: roi >= 100 ? 'Profitable' : roi >= 0 ? 'Break-even' : 'Loss',
                color: roi >= 100 ? 'text-green-400' : roi >= 0 ? 'text-accent' : 'text-red-400',
                bg: roi >= 100 ? 'bg-green-500/20' : roi >= 0 ? 'bg-accent/20' : 'bg-red-500/20',
            };
        } else {
            result = null;
        }
    }

    function formatCurrency(val) {
        return 'RM ' + val.toLocaleString('en-MY');
    }
</script>

<div class="bg-white border border-gray-100 rounded-2xl p-6 md:p-8 shadow-soft">
    <h3 class="font-display font-bold text-lg md:text-xl text-ink mb-1">ROI Calculator</h3>
    <p class="text-sm text-muted mb-6">Return on Investment — calculate your campaign's net profit.</p>

    <div class="grid md:grid-cols-2 gap-4 mb-6">
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Ad Budget (Ad Spend)</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">RM</span>
                <input type="number" bind:value={adSpend} min="0" step="100"
                    class="w-full pl-10 pr-4 py-3 bg-soft border border-gray-200 rounded-xl text-ink font-bold focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Creative Production Cost</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">RM</span>
                <input type="number" bind:value={productionCost} min="0" step="100"
                    class="w-full pl-10 pr-4 py-3 bg-soft border border-gray-200 rounded-xl text-ink font-bold focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Management Fee</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">RM</span>
                <input type="number" bind:value={managementFee} min="0" step="100"
                    class="w-full pl-10 pr-4 py-3 bg-soft border border-gray-200 rounded-xl text-ink font-bold focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Total Revenue</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">RM</span>
                <input type="number" bind:value={totalRevenue} min="0" step="100"
                    class="w-full pl-10 pr-4 py-3 bg-soft border border-gray-200 rounded-xl text-ink font-bold focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
    </div>

    {#if result}
        <div class="bg-ink rounded-2xl p-6 text-center">
            <p class="text-white/50 text-xs font-bold uppercase tracking-wider mb-1">ROI Campaign</p>
            <p class="font-display font-extrabold text-5xl md:text-6xl text-white">{result.roi}%</p>
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold mt-3 {result.bg} {result.color}">
                {#if result.rating === 'good'}🟢{:else if result.rating === 'fair'}🟡{:else}🔴{/if}
                {result.label}
            </div>
            <div class="mt-5 grid grid-cols-2 gap-4 text-left">
                <div class="bg-white/5 rounded-xl p-3">
                    <p class="text-[10px] text-white/40 uppercase tracking-wider">Total Cost</p>
                    <p class="font-bold text-white text-sm">{formatCurrency(result.totalCost)}</p>
                </div>
                <div class="bg-white/5 rounded-xl p-3">
                    <p class="text-[10px] text-white/40 uppercase tracking-wider">Net Profit</p>
                    <p class="font-bold text-sm {result.profit >= 0 ? 'text-green-400' : 'text-red-400'}">{formatCurrency(result.profit)}</p>
                </div>
            </div>
            <div class="mt-4 text-left text-xs text-white/60 space-y-1">
                {#if result.rating === 'loss'}
                    <p>💡 Negative ROI means total costs exceed revenue. Review your cost structure or optimise the campaign.</p>
                {:else if result.rating === 'fair'}
                    <p>💡 ROI of 0-100% means break-even with thin margins. Focus on cost efficiency and scale what already works.</p>
                {:else}
                    <p>✅ ROI above 100% is profitable. Consider scaling your budget for bigger results.</p>
                {/if}
            </div>
        </div>
    {:else}
        <div class="bg-soft rounded-2xl p-6 text-center">
            <p class="text-muted text-sm">Enter your cost and revenue figures to calculate ROI.</p>
        </div>
    {/if}

    <div class="mt-4 text-center">
        <a href="https://wa.me/62811919328?text=Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20my%20campaign%20ROI." target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-sm font-bold text-accent hover:text-ink transition-colors">
            Discuss ROI with the Beriklan Team →
        </a>
    </div>
</div>

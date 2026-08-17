// Featured image — LOCAL per-service images from /images/blog/ (imageartikel/).
//
// Setiap layanan punya gambar sendiri (16:9, webp, ~100KB). Dipilih berdasarkan
// `post.service`, lalu infer dari title/slug bila field kosong, lalu fallback.
// Hash-based: same service → same image (konsisten + browser cache friendly).
//
// Fallback chain:
//   1. post.featuredImage (explicit override)
//   2. service image (this file) — by post.service or inferred from title
//   3. default digital-marketing image

const IMG_BASE = "/images/blog/";
const IMG_EXT = ".webp";

// Service → local image file (from imageartikel/)
const SERVICE_IMAGES = {
    "facebook-ads-management": "jasafacebokads",
    "instagram-ads-management": "jasainstagramads",
    "tiktok-ads-management": "jasatiktokads",
    "google-ads-management": "jasagoogleads",
    "youtube-ads-management": "jasayoutubeads",
    "instagram-management": "jasainstagramads",
    "tiktok-management": "jasatiktokads",
    "digital-marketing-agency": "jasadigitalmarketing1",
    "website-development": "jasapembuatanwebsite",
    "landing-page-design": "jasapembuatanwebsite",
    "live-stream-viewers": "jasaviewlivetiktok",
    "tiktok-live-viewers": "jasaviewlivetiktok",
    "shopee-live-viewers": "jasaviewliveshopee",
    "youtube-live-viewers": "jasaviewliveyoutube",
    "twitch-live-viewers": "jasaviewlivetwitch",
    "instagram-live-viewers": "jasaviewliveinstagram",
};

const DEFAULT_IMG = "jasadigitalmarketing1";

// Infer service from title/slug (untuk post lama tanpa field service)
function inferServiceFromTitle(title) {
    const t = (title || "").toLowerCase();
    // Check live-viewers first (more specific) before generic platform match
    if (t.includes("live") && (t.includes("viewer") || t.includes("view") || t.includes("stream"))) {
        if (t.includes("shopee")) return "shopee-live-viewers";
        if (t.includes("youtube")) return "youtube-live-viewers";
        if (t.includes("twitch")) return "twitch-live-viewers";
        if (t.includes("instagram") || t.includes("ig ")) return "instagram-live-viewers";
        if (t.includes("tiktok")) return "tiktok-live-viewers";
        return "live-stream-viewers";
    }
    const rules = [
        ["facebook", "facebook-ads-management"],
        ["instagram", "instagram-ads-management"],
        ["tiktok", "tiktok-ads-management"],
        ["google", "google-ads-management"],
        ["youtube", "youtube-ads-management"],
        ["website", "website-development"],
        ["landing page", "landing-page-design"],
        ["digital marketing", "digital-marketing-agency"],
        ["ads", "google-ads-management"],
    ];
    for (const [kw, svc] of rules) if (t.includes(kw)) return svc;
    return "";
}

// For live-stream-viewers: platform-specific image based on title/slug keyword
function viewLiveImage(title, slug) {
    const t = ((title || "") + " " + (slug || "")).toLowerCase();
    if (t.includes("shopee")) return "jasaviewliveshopee";
    if (t.includes("youtube")) return "jasaviewliveyoutube";
    if (t.includes("twitch")) return "jasaviewlivetwitch";
    if (t.includes("instagram")) return "jasaviewliveinstagram";
    if (t.includes("tiktok")) return "jasaviewlivetiktok";
    return "jasaviewlivetiktok";
}

// Simple string hash (deterministic)
function hashStr(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) {
        h = ((h << 5) - h) + s.charCodeAt(i);
        h |= 0;
    }
    return Math.abs(h);
}

function imageUrl(name) {
    return IMG_BASE + name + IMG_EXT;
}

export function getFeaturedImage(post) {
    // 1. Explicit override
    if (post && post.featuredImage) return post.featuredImage;
    // 2. Service-based local image. Service default 'digital-marketing-agency'
    //    sering dipakai sebagai fallback saat generate — coba infer dari title
    //    dulu biar shopee/tiktok/google dll dapat gambar yang sesuai konten.
    let svc = (post?.service || "").toLowerCase();
    const inferred = inferServiceFromTitle(post?.title);
    if (!svc || svc === "digital-marketing-agency") svc = inferred || svc;
    let name = "";
    if (svc === "live-stream-viewers") {
        name = viewLiveImage(post?.title, post?.slug);
    } else if (SERVICE_IMAGES[svc]) {
        name = SERVICE_IMAGES[svc];
    } else {
        // kategori tanpa service → hash ke salah satu gambar digital marketing
        const alt = [SERVICE_IMAGES["digital-marketing-agency"], SERVICE_IMAGES["website-development"]];
        name = alt[hashStr(post?.slug || "x") % alt.length];
    }
    return imageUrl(name);
}

// Thumbnail untuk related posts (pakai gambar service yang sama, kecil)
export function getRelatedImages(post, count = 3) {
    const cat = post?.category || "strategy";
    let svc = (post?.service || "").toLowerCase();
    const inferred = inferServiceFromTitle(post?.title);
    if (!svc || svc === "digital-marketing-agency") svc = inferred || svc;
    const poolKeys = Object.keys(SERVICE_IMAGES);
    const start = hashStr(post?.slug || "x") % poolKeys.length;
    return Array.from({ length: count }, (_, i) => {
        const key = poolKeys[(start + i) % poolKeys.length];
        const name = SERVICE_IMAGES[key] || DEFAULT_IMG;
        return imageUrl(name);
    });
}

// Hero image with fallback (untuk <img onerror> pattern)
export function getFeaturedImageWithFallback(post) {
    return { primary: getFeaturedImage(post), fallback: imageUrl(DEFAULT_IMG) };
}

export const UNSPLASH_POOL = null;
export const SERVICE_IMAGE_MAP = SERVICE_IMAGES;
export const picsumFor = () => imageUrl(DEFAULT_IMG);
export const svgPlaceholderFor = () => imageUrl(DEFAULT_IMG);

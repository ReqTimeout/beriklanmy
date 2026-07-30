CREATE TABLE IF NOT EXISTS api_key_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      key_name TEXT NOT NULL,
      endpoint TEXT NOT NULL,
      ip TEXT,
      user_agent TEXT,
      status TEXT NOT NULL,
      timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS api_keys (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      key_hash TEXT NOT NULL,
      key_prefix TEXT NOT NULL,
      key_suffix TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      last_rotated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      expires_at TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active',
      last_used_at TEXT,
      use_count INTEGER DEFAULT 0,
      rotated_by TEXT
    );

CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  title TEXT,
  keyword_id TEXT,
  word_count INTEGER,
  h2_count INTEGER,
  h3_count INTEGER,
  faq_count INTEGER,
  keyword_density REAL,
  quality_score REAL,
  status TEXT,
  generated_at TEXT,
  published_at TEXT,
  model_used TEXT,
  prompt_version TEXT,
  FOREIGN KEY (keyword_id) REFERENCES keyword_queue(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  actor TEXT,
  action TEXT,
  target TEXT,
  details TEXT
);

CREATE TABLE IF NOT EXISTS automation_health (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  workflow_name TEXT,
  status TEXT,
  duration_seconds INTEGER,
  output TEXT
);

CREATE TABLE IF NOT EXISTS batch4_articles (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL UNIQUE, data TEXT, service TEXT, city TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS batch4_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL UNIQUE,
  keyword TEXT,
  service TEXT,
  city TEXT,
  intent TEXT DEFAULT 'informational',
  status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS blocklist (
  keyword_pattern TEXT PRIMARY KEY,
  reason TEXT,
  added_at TEXT
);

CREATE TABLE IF NOT EXISTS campaigns (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      template_id INTEGER,
      list_id INTEGER,
      subject TEXT,
      status TEXT DEFAULT 'draft',
      total_recipients INTEGER DEFAULT 0,
      sent_count INTEGER DEFAULT 0,
      open_count INTEGER DEFAULT 0,
      click_count INTEGER DEFAULT 0,
      scheduled_at TEXT,
      sent_at TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS city_content (route TEXT PRIMARY KEY, content TEXT, city TEXT, service TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS city_content_queue (route TEXT PRIMARY KEY, city TEXT, service TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS city_pages (
  route        TEXT PRIMARY KEY,  -- e.g. 'jasa-iklan-facebook/bandung/'
  service      TEXT,
  city         TEXT,
  html_content TEXT,
  iso_updated  TEXT
);

CREATE TABLE IF NOT EXISTS conversion_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  cta_type TEXT,
  cta_location TEXT,
  page TEXT,
  referrer TEXT,
  user_agent TEXT,
  session_id TEXT
);

CREATE TABLE IF NOT EXISTS cron_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, google_ok INTEGER, google_fail INTEGER, indexnow_ok INTEGER, indexnow_fail INTEGER, urls_processed INTEGER);

CREATE TABLE IF NOT EXISTS cron_retry_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cron_name TEXT NOT NULL,
  payload TEXT,
  last_error TEXT,
  last_attempt_at TEXT DEFAULT CURRENT_TIMESTAMP,
  attempts INTEGER DEFAULT 1,
  next_retry_at TEXT,
  status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS cron_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cron_name TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  duration_ms INTEGER,
  output TEXT,
  error TEXT,
  retry_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS cron_settings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      cron TEXT NOT NULL,
      enabled INTEGER DEFAULT 1,
      label TEXT
    , value TEXT DEFAULT '');

CREATE TABLE IF NOT EXISTS email_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      campaign_id INTEGER,
      email TEXT NOT NULL,
      name TEXT,
      status TEXT DEFAULT 'pending',
      error TEXT,
      sent_at TEXT,
      opened_at TEXT,
      clicked_at TEXT,
      tracking_id TEXT UNIQUE
    );

CREATE TABLE IF NOT EXISTS email_templates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      subject TEXT NOT NULL,
      html_body TEXT NOT NULL,
      category TEXT DEFAULT 'promo',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS generated_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        service TEXT,
        city TEXT,
        source TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        committed_at TEXT
      );

CREATE TABLE IF NOT EXISTS gsc_sitemaps (id INTEGER PRIMARY KEY AUTOINCREMENT, siteUrl TEXT NOT NULL, sitemapPath TEXT NOT NULL, lastSubmitted TEXT, lastDownloaded TEXT, lastStatus INTEGER, isPending INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(siteUrl, sitemapPath));

CREATE TABLE IF NOT EXISTS hourly_generate_runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
      count_requested INTEGER,
      count_generated INTEGER,
      slugs TEXT,
      models TEXT,
      committed_to_github INTEGER,
      enqueued_for_indexing INTEGER,
      error TEXT,
      elapsed_ms INTEGER
    );

CREATE TABLE IF NOT EXISTS index_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT,
  engine TEXT,
  submitted_at TEXT,
  status TEXT,
  indexed_at TEXT,
  response_code INTEGER,
  attempts INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS keyword_map (
  keyword  TEXT PRIMARY KEY,  -- the slugified keyword
  posts    TEXT,  -- JSON array of post slugs
  intent   TEXT,
  service  TEXT,
  city     TEXT,
  iso_updated TEXT
);

CREATE TABLE IF NOT EXISTS keyword_queue (
  id TEXT PRIMARY KEY,
  keyword TEXT UNIQUE NOT NULL,
  keyword_normalized TEXT NOT NULL,
  source TEXT,
  seed TEXT,
  discovered_at TEXT,
  status TEXT DEFAULT 'pending',
  priority_score INTEGER DEFAULT 0,
  intent TEXT,
  service TEXT,
  city TEXT,
  estimated_volume INTEGER,
  rank_match_profile TEXT,
  article_slug TEXT,
  article_quality_score REAL,
  published_at TEXT,
  indexed_at TEXT,
  first_rank_at TEXT,
  best_rank INTEGER,
  current_rank INTEGER,
  revenue_30d REAL DEFAULT 0,
  revenue_total REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS keyword_ranks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      keyword TEXT NOT NULL,
      page_url TEXT NOT NULL,
      position REAL NOT NULL,
      clicks INTEGER DEFAULT 0,
      impressions INTEGER DEFAULT 0,
      ctr REAL DEFAULT 0,
      date TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(keyword, page_url, date)
    );

CREATE TABLE IF NOT EXISTS lead_contacts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      list_id INTEGER,
      email TEXT,
      phone TEXT,
      name TEXT,
      company TEXT,
      website TEXT,
      city TEXT,
      category TEXT,
      extra TEXT
    , source_id TEXT DEFAULT '');

CREATE TABLE IF NOT EXISTS lead_lists (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      source TEXT,
      total INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS manual_review (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword_id TEXT,
  reason TEXT,
  attempts INTEGER,
  created_at TEXT,
  resolved_at TEXT,
  resolution TEXT
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      name TEXT,
      page_url TEXT,
      source TEXT,
      status TEXT NOT NULL DEFAULT 'active',
      drip_step INTEGER NOT NULL DEFAULT 0,
      unsubscribed_at TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS pending_indexing (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL UNIQUE, source TEXT DEFAULT 'manual', status TEXT DEFAULT 'pending', error TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, submitted_at TIMESTAMP, gsc_submitted_at TEXT, indexnow_at TEXT, index_state TEXT, index_checked_at TEXT, resubmit_count INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS policy_audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT, source TEXT, category TEXT, keyword TEXT, severity TEXT, action TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS posts_content (
  slug     TEXT PRIMARY KEY,
  content  TEXT,  -- HTML (may exceed 1MB; SQLite TEXT has no limit)
  FOREIGN KEY (slug) REFERENCES posts_meta(slug) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS posts_meta (
  slug        TEXT PRIMARY KEY,
  title       TEXT,
  excerpt     TEXT,
  date        TEXT,
  iso_date    TEXT,
  category    TEXT,
  readTime    TEXT,
  tags        TEXT,  -- JSON array
  service     TEXT,
  city        TEXT,
  featured    INTEGER DEFAULT 0,
  generated   INTEGER DEFAULT 0,
  iso_updated TEXT
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS rank_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snapshot_date TEXT,
  keyword TEXT,
  url TEXT,
  position INTEGER,
  impressions INTEGER,
  clicks INTEGER,
  ctr REAL,
  change_from_prev INTEGER
);

CREATE TABLE IF NOT EXISTS rate_limits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ip TEXT NOT NULL,
      endpoint TEXT NOT NULL,
      request_count INTEGER DEFAULT 1,
      window_start INTEGER NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(ip, endpoint, window_start)
    );

CREATE TABLE IF NOT EXISTS refresh_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL,
      model TEXT,
      commit_sha TEXT,
      elapsed_ms INTEGER,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS request_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_type TEXT,
  payload TEXT,
  priority INTEGER DEFAULT 5,
  status TEXT DEFAULT 'pending',
  attempts INTEGER DEFAULT 0,
  last_attempt TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS scrape_results (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      search_id INTEGER NOT NULL,
      name TEXT,
      phone TEXT,
      email TEXT,
      website TEXT,
      category TEXT,
      city TEXT,
      source TEXT
    );

CREATE TABLE IF NOT EXISTS scrape_searches (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      query TEXT NOT NULL,
      city TEXT,
      category TEXT,
      results_count INTEGER DEFAULT 0,
      results_json TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS scrape_users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      whatsapp TEXT NOT NULL,
      search_count INTEGER DEFAULT 0,
      session_token TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      last_active TEXT DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS trending_articles (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL UNIQUE, title TEXT NOT NULL, content TEXT, source TEXT DEFAULT 'workers_ai', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS trending_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_date TEXT,
  topic TEXT,
  rising_rate REAL,
  angle TEXT,
  article_slug TEXT,
  article_url TEXT,
  published_at TEXT,
  indexed_at TEXT,
  impressions_7d INTEGER DEFAULT 0,
  clicks_7d INTEGER DEFAULT 0,
  revenue_7d REAL DEFAULT 0,
  revenue_30d REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS trending_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL UNIQUE,
        geo TEXT,
        priority INTEGER DEFAULT 0,
        fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
        processed_at TEXT,
        status TEXT DEFAULT 'pending'
      );

CREATE INDEX IF NOT EXISTS idx_api_key_usage_name_time ON api_key_usage (key_name, timestamp);

CREATE INDEX IF NOT EXISTS idx_api_key_usage_timestamp ON api_key_usage (timestamp);

CREATE INDEX IF NOT EXISTS idx_api_keys_expires ON api_keys (expires_at);

CREATE INDEX IF NOT EXISTS idx_api_keys_name_status ON api_keys (name, status);

CREATE INDEX IF NOT EXISTS idx_art_slug ON articles(slug);

CREATE INDEX IF NOT EXISTS idx_art_status ON articles(status);

CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns (status);

CREATE INDEX IF NOT EXISTS idx_city_pages_service ON city_pages(service);

CREATE INDEX IF NOT EXISTS idx_conv_cta ON conversion_log(cta_type);

CREATE INDEX IF NOT EXISTS idx_conv_page ON conversion_log(page);

CREATE INDEX IF NOT EXISTS idx_cron_retry_pending ON cron_retry_queue (status, next_retry_at);

CREATE INDEX IF NOT EXISTS idx_cron_runs_name ON cron_runs (cron_name, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_cron_runs_status ON cron_runs (status);

CREATE INDEX IF NOT EXISTS idx_email_queue_campaign ON email_queue (campaign_id);

CREATE INDEX IF NOT EXISTS idx_email_queue_status ON email_queue (status);

CREATE INDEX IF NOT EXISTS idx_hgr_timestamp ON hourly_generate_runs (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_idx_status ON index_log(status);

CREATE INDEX IF NOT EXISTS idx_idx_url ON index_log(url);

CREATE INDEX IF NOT EXISTS idx_keyword_map_service ON keyword_map(service);

CREATE INDEX IF NOT EXISTS idx_keyword_ranks_date ON keyword_ranks (date);

CREATE INDEX IF NOT EXISTS idx_keyword_ranks_keyword ON keyword_ranks (keyword);

CREATE INDEX IF NOT EXISTS idx_keyword_ranks_position ON keyword_ranks (position);

CREATE INDEX IF NOT EXISTS idx_kq_priority ON keyword_queue (priority_score DESC);

CREATE INDEX IF NOT EXISTS idx_kq_service ON keyword_queue (service);

CREATE INDEX IF NOT EXISTS idx_lead_contacts_list ON lead_contacts (list_id);

CREATE INDEX IF NOT EXISTS idx_newsletter_drip ON newsletter_subscribers (status, drip_step);

CREATE INDEX IF NOT EXISTS idx_newsletter_status ON newsletter_subscribers (status);

CREATE INDEX IF NOT EXISTS idx_pending_indexnow ON pending_indexing (indexnow_at);

CREATE INDEX IF NOT EXISTS idx_posts_meta_city ON posts_meta(city);

CREATE INDEX IF NOT EXISTS idx_posts_meta_iso ON posts_meta(iso_date DESC);

CREATE INDEX IF NOT EXISTS idx_posts_meta_service ON posts_meta(service);

CREATE INDEX IF NOT EXISTS idx_q_keyword ON keyword_queue(keyword_normalized);

CREATE INDEX IF NOT EXISTS idx_q_priority ON keyword_queue(priority_score DESC);

CREATE INDEX IF NOT EXISTS idx_q_service_city ON keyword_queue(service, city);

CREATE INDEX IF NOT EXISTS idx_q_status ON keyword_queue(status);

CREATE INDEX IF NOT EXISTS idx_rank_date ON rank_snapshots(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_rank_kw ON rank_snapshots(keyword);

CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_endpoint ON rate_limits (ip, endpoint, window_start);

CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits (window_start);

CREATE INDEX IF NOT EXISTS idx_refresh_log_slug ON refresh_log (slug);

CREATE INDEX IF NOT EXISTS idx_rq_status ON request_queue(status);

CREATE INDEX IF NOT EXISTS idx_scrape_results_search ON scrape_results (search_id);

CREATE INDEX IF NOT EXISTS idx_scrape_results_user ON scrape_results (user_id);

CREATE INDEX IF NOT EXISTS idx_scrape_searches_user ON scrape_searches (user_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_scrape_users_email ON scrape_users (email);

CREATE INDEX IF NOT EXISTS idx_scrape_users_session ON scrape_users (session_token);
-- AI-MEDIA-OS 内容实验数据库 schema
-- 实际数据库文件：database/content_experiments.sqlite（不入 Git，由 scripts/content_db.py init 生成）
-- 单位约定：
--   duration                  秒
--   production_time           分钟（制作耗时）
--   estimated_image/video/audio_cost / total_cost / revenue   人民币元
--   three_second_retention / completion_rate   百分比 0-100
--   characters / generation_models   分号分隔字符串，如 "角色A;角色B"

CREATE TABLE IF NOT EXISTS content_experiments (
    content_id                 TEXT PRIMARY KEY,
    platform                   TEXT NOT NULL,
    publish_date               TEXT,
    series                     TEXT,
    topic                      TEXT,
    content_type               TEXT,
    duration                   REAL,
    hook_type                  TEXT,
    visual_style               TEXT,
    characters                 TEXT,
    generation_models          TEXT,
    image_generation_count     INTEGER,
    video_generation_count     INTEGER,
    failed_generation_count    INTEGER,
    estimated_image_cost       REAL,
    estimated_video_cost       REAL,
    estimated_audio_cost       REAL,
    total_cost                 REAL,
    production_time            REAL,
    views                      INTEGER,
    likes                      INTEGER,
    comments                   INTEGER,
    shares                     INTEGER,
    favorites                  INTEGER,
    followers_gained           INTEGER,
    three_second_retention     REAL,
    completion_rate            REAL,
    revenue                    REAL,
    notes                      TEXT,
    created_at                 TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at                 TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_ce_platform      ON content_experiments(platform);
CREATE INDEX IF NOT EXISTS idx_ce_publish_date  ON content_experiments(publish_date);
CREATE INDEX IF NOT EXISTS idx_ce_series        ON content_experiments(series);
CREATE INDEX IF NOT EXISTS idx_ce_topic         ON content_experiments(topic);

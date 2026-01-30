-- ============================================================
-- 本番デモ用シードデータ SQL
-- ============================================================
-- 使用方法:
--   1. PostgreSQLに接続: psql -U <user> -d <database>
--   2. SQLファイルを実行: \i demo_seed.sql
--   または: psql -U <user> -d <database> -f demo_seed.sql
--
-- 注意事項:
--   - 既存データがある場合は先にTRUNCATEしてください
--   - パスワードはデモ用（password123）。本番運用時は必ず変更してください
--   - ベクトルデータは別途 python manage.py vectorize_all で生成してください
-- ============================================================

-- トランザクション開始
BEGIN;

-- ============================================================
-- 1. 店舗データ (10店舗)
-- ============================================================
INSERT INTO stores (store_id, store_name, address, manager_id, created_at) VALUES
(1, '本部', '東京都千代田区丸の内1-1-1 本社ビル5F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '365 days'),
(2, '渋谷道玄坂店', '東京都渋谷区道玄坂2-3-1 渋谷ビル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '300 days'),
(3, '新宿東口店', '東京都新宿区新宿3-25-10 新宿センタービル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '280 days'),
(4, '池袋西口店', '東京都豊島区西池袋1-10-15 池袋駅前ビル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '250 days'),
(5, '横浜駅前店', '神奈川県横浜市西区北幸1-1-1 横浜駅前ビル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '200 days'),
(6, '大阪梅田店', '大阪府大阪市北区梅田1-3-1 大阪駅前第一ビル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '180 days'),
(7, '名古屋栄店', '愛知県名古屋市中区栄3-5-1 栄センタービル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '150 days'),
(8, '福岡天神店', '福岡県福岡市中央区天神2-5-1 天神センタービル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '120 days'),
(9, '札幌駅前店', '北海道札幌市中央区北5条西3-1 札幌駅前ビル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '90 days'),
(10, '仙台駅前店', '宮城県仙台市青葉区中央1-1-1 仙台駅前ビル1F', NULL, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '60 days');

-- シーケンスの更新
SELECT setval('stores_store_id_seq', 10);

-- ============================================================
-- 2. ユーザーデータ (管理者1名 + 各店舗に店長1名 + スタッフ2-4名 = 約40名)
-- ============================================================
-- パスワード: password123 (Django PBKDF2形式)
-- 本番運用時は必ず変更してください

INSERT INTO users (user_id, password, last_name, first_name, store_id, user_type, email, is_staff, is_superuser, is_active, created_at) VALUES
-- 本部 (管理者)
('admin', 'pbkdf2_sha256$600000$5r6PWGuN24MYvhL0UfGt12$m3bKRh9rFwgl9WCfDbotTcSpX+ANVc12yW7TIx2KGr4=', 'システム', '管理者', 1, 'admin', 'admin@example.com', true, true, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '365 days'),
('honbu_mgr', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '本部', '太郎', 1, 'manager', 'honbu_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '360 days'),

-- 渋谷道玄坂店
('manager_001', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '佐藤', '健一', 2, 'manager', 'shibuya_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '300 days'),
('staff_001', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '田中', '花子', 2, 'staff', 'shibuya_s01@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '290 days'),
('A1', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'A1', 'グループ', 2, 'staff', 'A1@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '280 days'),
('A2', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'A2', 'グループ', 2, 'staff', 'A2@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '100 days'),

-- 新宿東口店
('manager_002', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '鈴木', '一郎', 3, 'manager', 'shinjuku_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '280 days'),
('A3', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'A3', 'グループ', 3, 'staff', 'A3@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '270 days'),
('B1', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'B1', 'グループ', 3, 'staff', 'B1@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '260 days'),
('B2', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'B2', 'グループ', 3, 'staff', 'B2@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '150 days'),
('B3', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'B3', 'グループ', 3, 'staff', 'B3@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days'),

-- 池袋西口店
('manager_003', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '加藤', '誠', 4, 'manager', 'ikebukuro_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '250 days'),
('C1', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'C1', 'グループ', 4, 'staff', 'C1@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '240 days'),
('C2', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'C2', 'グループ', 4, 'staff', 'C2@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '200 days'),

-- 横浜駅前店
('manager_004', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '松本', '浩二', 5, 'manager', 'yokohama_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '200 days'),
('C3', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'C3', 'グループ', 5, 'staff', 'C3@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '190 days'),
('D1', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'D1', 'グループ', 5, 'staff', 'D1@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '180 days'),
('D2', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'D2', 'グループ', 5, 'staff', 'D2@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '80 days'),

-- 大阪梅田店
('manager_005', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '清水', '大輔', 6, 'manager', 'osaka_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '180 days'),
('D3', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', 'D3', 'グループ', 6, 'staff', 'D3@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '170 days'),
('staff_014', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '藤田', '健', 6, 'staff', 'osaka_s02@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '160 days'),
('staff_015', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '橋本', 'めぐみ', 6, 'staff', 'osaka_s03@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '60 days'),

-- 名古屋栄店
('manager_006', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '前田', '直人', 7, 'manager', 'nagoya_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '150 days'),
('staff_016', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '石井', '陽子', 7, 'staff', 'nagoya_s01@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '140 days'),
('staff_017', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '阿部', '光', 7, 'staff', 'nagoya_s02@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '130 days'),

-- 福岡天神店
('manager_007', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '森', '康平', 8, 'manager', 'fukuoka_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '120 days'),
('staff_018', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '池田', '明日香', 8, 'staff', 'fukuoka_s01@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '110 days'),
('staff_019', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '原田', '拓也', 8, 'staff', 'fukuoka_s02@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '100 days'),

-- 札幌駅前店
('manager_008', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '村上', '隆', 9, 'manager', 'sapporo_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '90 days'),
('staff_020', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '近藤', '由紀', 9, 'staff', 'sapporo_s01@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '80 days'),
('staff_021', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '斎藤', '勇気', 9, 'staff', 'sapporo_s02@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '70 days'),

-- 仙台駅前店
('manager_009', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '遠藤', '正樹', 10, 'manager', 'sendai_mgr@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '60 days'),
('staff_022', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '藤原', '優花', 10, 'staff', 'sendai_s01@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days'),
('staff_023', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '岡田', '達也', 10, 'staff', 'sendai_s02@example.com', false, false, true, '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '40 days');

-- 店舗マネージャーの更新
UPDATE stores SET manager_id = 'manager_001' WHERE store_id = 2;
UPDATE stores SET manager_id = 'manager_002' WHERE store_id = 3;
UPDATE stores SET manager_id = 'manager_003' WHERE store_id = 4;
UPDATE stores SET manager_id = 'manager_004' WHERE store_id = 5;
UPDATE stores SET manager_id = 'manager_005' WHERE store_id = 6;
UPDATE stores SET manager_id = 'manager_006' WHERE store_id = 7;
UPDATE stores SET manager_id = 'manager_007' WHERE store_id = 8;
UPDATE stores SET manager_id = 'manager_008' WHERE store_id = 9;
UPDATE stores SET manager_id = 'manager_009' WHERE store_id = 10;

-- ============================================================
-- 3. 店舗日次実績データ (過去90日分 × 9店舗 = 約810件)
-- ============================================================
-- 本部以外の9店舗に対して、過去90日分の実績データを生成
-- 特徴:
--   - イベントスパイク（クリスマス、年末年始、週末）
--   - 仙台店の成長曲線（新規オープン店舗）
--   - 池袋店のV字回復パターン
--   - 天候影響（ランダムで悪天候日を設定）

INSERT INTO store_daily_performances (store_id, date, sales_amount, customer_count, cash_difference, registered_by_id, created_at, updated_at)
SELECT
    s.store_id,
    d.date,
    -- 売上金額: 基準値 + 曜日変動 + イベント変動 + トレンド + ランダム変動
    GREATEST(100000, (
        -- 店舗ごとの基準値
        CASE
            WHEN s.store_id = 2 THEN 450000  -- 渋谷
            WHEN s.store_id = 3 THEN 520000  -- 新宿
            WHEN s.store_id = 4 THEN 380000  -- 池袋
            WHEN s.store_id = 5 THEN 420000  -- 横浜
            WHEN s.store_id = 6 THEN 480000  -- 大阪
            WHEN s.store_id = 7 THEN 350000  -- 名古屋
            WHEN s.store_id = 8 THEN 320000  -- 福岡
            WHEN s.store_id = 9 THEN 280000  -- 札幌
            WHEN s.store_id = 10 THEN 260000 -- 仙台
        END
        -- 曜日変動
        + CASE EXTRACT(DOW FROM d.date)
            WHEN 0 THEN 80000   -- 日曜
            WHEN 6 THEN 100000  -- 土曜
            WHEN 5 THEN 50000   -- 金曜
            ELSE 0
          END
        -- イベントスパイク（クリスマス前後）
        + CASE
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) BETWEEN 23 AND 25 THEN 180000
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) BETWEEN 20 AND 22 THEN 80000
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) BETWEEN 26 AND 30 THEN 60000
            ELSE 0
          END
        -- 年末年始スパイク
        + CASE
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) = 31 THEN 120000
            WHEN EXTRACT(MONTH FROM d.date) = 1 AND EXTRACT(DAY FROM d.date) BETWEEN 1 AND 3 THEN 100000
            ELSE 0
          END
        -- 月末給料日後の週末ブースト
        + CASE
            WHEN EXTRACT(DAY FROM d.date) BETWEEN 25 AND 28 AND EXTRACT(DOW FROM d.date) IN (0, 6) THEN 50000
            ELSE 0
          END
        -- 仙台店の成長曲線（日が経つにつれ売上増加）
        + CASE
            WHEN s.store_id = 10 THEN
                LEAST(80000, EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER * -800 + 80000)
            ELSE 0
          END
        -- 池袋店のV字回復（60-45日前に落ち込み、その後回復）
        + CASE
            WHEN s.store_id = 4 THEN
                CASE
                    WHEN EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER BETWEEN 45 AND 60 THEN -80000
                    WHEN EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER BETWEEN 30 AND 44 THEN -40000
                    ELSE 0
                END
            ELSE 0
          END
        -- 大阪店の期間限定メニューブースト（30-20日前）
        + CASE
            WHEN s.store_id = 6 AND EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER BETWEEN 20 AND 35 THEN 70000
            ELSE 0
          END
        -- ランダム変動
        + (RANDOM() * 60000 - 30000)::INTEGER
    ))::INTEGER as sales_amount,

    -- 客数: 基準値 + 曜日変動 + イベント変動 + トレンド + ランダム変動
    GREATEST(50, (
        -- 店舗ごとの基準値
        CASE
            WHEN s.store_id = 2 THEN 180
            WHEN s.store_id = 3 THEN 210
            WHEN s.store_id = 4 THEN 150
            WHEN s.store_id = 5 THEN 170
            WHEN s.store_id = 6 THEN 190
            WHEN s.store_id = 7 THEN 140
            WHEN s.store_id = 8 THEN 130
            WHEN s.store_id = 9 THEN 110
            WHEN s.store_id = 10 THEN 100
        END
        -- 曜日変動
        + CASE EXTRACT(DOW FROM d.date)
            WHEN 0 THEN 40
            WHEN 6 THEN 50
            WHEN 5 THEN 25
            ELSE 0
          END
        -- イベントスパイク
        + CASE
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) BETWEEN 23 AND 25 THEN 80
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) BETWEEN 20 AND 22 THEN 40
            ELSE 0
          END
        -- 年末年始
        + CASE
            WHEN EXTRACT(MONTH FROM d.date) = 12 AND EXTRACT(DAY FROM d.date) = 31 THEN 50
            WHEN EXTRACT(MONTH FROM d.date) = 1 AND EXTRACT(DAY FROM d.date) BETWEEN 1 AND 3 THEN 60
            ELSE 0
          END
        -- 仙台店の成長曲線
        + CASE
            WHEN s.store_id = 10 THEN
                LEAST(40, EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER * -0.4 + 40)::INTEGER
            ELSE 0
          END
        -- 池袋店のV字回復
        + CASE
            WHEN s.store_id = 4 THEN
                CASE
                    WHEN EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER BETWEEN 45 AND 60 THEN -35
                    WHEN EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER BETWEEN 30 AND 44 THEN -15
                    ELSE 0
                END
            ELSE 0
          END
        -- 大阪店の期間限定メニューブースト
        + CASE
            WHEN s.store_id = 6 AND EXTRACT(DAY FROM ('2026-01-30'::DATE - d.date))::INTEGER BETWEEN 20 AND 35 THEN 30
            ELSE 0
          END
        -- ランダム変動
        + (RANDOM() * 30 - 15)::INTEGER
    ))::INTEGER as customer_count,

    -- 違算金額（5%の確率で発生、-500〜500円）
    CASE WHEN RANDOM() < 0.05 THEN (RANDOM() * 1000 - 500)::INTEGER ELSE 0 END as cash_difference,

    -- 登録者（各店舗のマネージャー）
    CASE
        WHEN s.store_id = 2 THEN 'manager_001'
        WHEN s.store_id = 3 THEN 'manager_002'
        WHEN s.store_id = 4 THEN 'manager_003'
        WHEN s.store_id = 5 THEN 'manager_004'
        WHEN s.store_id = 6 THEN 'manager_005'
        WHEN s.store_id = 7 THEN 'manager_006'
        WHEN s.store_id = 8 THEN 'manager_007'
        WHEN s.store_id = 9 THEN 'manager_008'
        WHEN s.store_id = 10 THEN 'manager_009'
    END as registered_by_id,

    d.date + TIME '18:00:00' as created_at,
    d.date + TIME '18:00:00' as updated_at
FROM
    stores s,
    generate_series('2026-01-30'::DATE - INTERVAL '90 days', '2026-01-30'::DATE - INTERVAL '1 day', '1 day'::INTERVAL) as d(date)
WHERE
    s.store_id != 1;  -- 本部を除く

-- シーケンスの更新
SELECT setval('store_daily_performances_performance_id_seq', (SELECT MAX(performance_id) FROM store_daily_performances));

-- ============================================================
-- 4. 日報データ (多様なシナリオ、約200件)
-- ============================================================

-- 渋谷道玄坂店の日報
INSERT INTO daily_reports (store_id, user_id, date, genre, location, title, content, post_to_bbs, created_at) VALUES
-- クレーム系
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '1 day', 'claim', 'hall', '接客態度に関するクレーム', 'お客様から「スタッフの対応が遅い」とのご指摘をいただきました。ピーク時の対応について改善が必要です。レジ待ち時間が10分以上かかり、お客様を不快にさせてしまいました。今後はピーク時間帯のスタッフ配置を見直します。', true, '2026-01-30'::DATE - INTERVAL '1 day' + TIME '14:30:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '5 days', 'claim', 'kitchen', '料理提供の遅延について', 'ランチタイムに注文から提供まで25分かかってしまいました。お客様から「遅すぎる」とお叱りを受けました。キッチンとホールの連携を改善する必要があります。注文票の確認フローを見直しました。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '15:00:00'),
(2, 'A2', '2026-01-30'::DATE - INTERVAL '12 days', 'claim', 'hall', '予約確認ミス', 'お客様の予約が入っていなかったため、お待たせしてしまいました。電話予約時の復唱確認を徹底します。幸い空席があり対応できましたが、今後は予約システムへの入力を即時行うようにします。', true, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '19:00:00'),
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '20 days', 'claim', 'cashier', 'お会計ミス', 'お会計時に金額を間違えてしまい、お客様にご指摘を受けました。確認不足でした。複数商品のある場合は必ず合計金額を読み上げて確認することを徹底します。', true, '2026-01-30'::DATE - INTERVAL '20 days' + TIME '20:30:00'),

-- 賞賛系
(2, 'A1', '2026-01-30'::DATE - INTERVAL '2 days', 'praise', 'kitchen', '料理の美味しさを褒められました', 'お客様から「今日のハンバーグは特に美味しかった」と直接お褒めの言葉をいただきました。シェフの丁寧な調理が評価されています。秘訣は肉の練り方にあるとのことでした。', true, '2026-01-30'::DATE - INTERVAL '2 days' + TIME '13:00:00'),
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '8 days', 'praise', 'hall', '子連れ対応を褒められました', '小さなお子様連れのお客様から「スタッフの気配りが素晴らしかった」とお褒めの言葉をいただきました。子供用の食器やクレヨンを用意したことが好評でした。他店舗でも参考になればと思います。', true, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '16:00:00'),
(2, 'A2', '2026-01-30'::DATE - INTERVAL '15 days', 'praise', 'hall', '外国人観光客への対応', '英語での注文対応がスムーズにできたと、海外からのお客様から感謝されました。翻訳アプリと指差しメニューの併用が効果的でした。', true, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '17:30:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '25 days', 'praise', 'kitchen', '季節限定メニューが好評', '新しく始めた冬季限定のシチューが大変好評です。1日平均30食以上出ています。常連のお客様から「来年も楽しみにしている」とのお声もいただきました。', true, '2026-01-30'::DATE - INTERVAL '25 days' + TIME '14:00:00'),

-- 事故・トラブル系
(2, 'manager_001', '2026-01-30'::DATE - INTERVAL '7 days', 'accident', 'kitchen', '厨房機器の故障', 'オーブンの温度が上がらなくなり、業者を呼んで修理しました。ヒーター部品の交換で復旧。修理費用は35,000円。予防保全の重要性を再認識しました。', true, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '11:00:00'),
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '18 days', 'accident', 'hall', 'お客様の転倒事故', '雨の日に入口で足を滑らせたお客様がいらっしゃいました。幸い怪我はありませんでしたが、マットを追加設置しました。雨天時の床の状態確認を強化します。', true, '2026-01-30'::DATE - INTERVAL '18 days' + TIME '12:30:00'),

-- 報告・その他
(2, 'manager_001', '2026-01-30'::DATE - INTERVAL '3 days', 'report', 'other', '売上報告：過去最高記録', '本日の売上が62万円を記録し、オープン以来最高となりました。週末の天候に恵まれたことと、SNSでの口コミ効果があったようです。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '22:00:00'),
(2, 'manager_001', '2026-01-30'::DATE - INTERVAL '10 days', 'report', 'other', '新人スタッフの研修完了', '新人の渡辺さんが基本研修を完了しました。接客、レジ操作、基本的な調理補助まで一通りできるようになりました。来週から通常シフトに入る予定です。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '21:00:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '22 days', 'report', 'kitchen', '食材の在庫管理改善', '発注システムを見直し、廃棄ロスを先月比20%削減できました。特に野菜類の鮮度管理が改善されました。', false, '2026-01-30'::DATE - INTERVAL '22 days' + TIME '17:00:00'),

-- 新宿東口店の日報
(3, 'A3', '2026-01-30'::DATE - INTERVAL '1 day', 'claim', 'hall', '待ち時間に関するクレーム', '満席時の待ち時間が長く、お客様からご不満の声をいただきました。待合スペースでのドリンクサービスを開始することを検討しています。', true, '2026-01-30'::DATE - INTERVAL '1 day' + TIME '20:00:00'),
(3, 'B1', '2026-01-30'::DATE - INTERVAL '4 days', 'praise', 'hall', 'リピーター様からの感謝', '週に3回来店される常連のお客様から「いつも気持ちよく食事ができる」とのお言葉をいただきました。スタッフ一同励みになります。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '15:00:00'),
(3, 'B2', '2026-01-30'::DATE - INTERVAL '6 days', 'accident', 'kitchen', '軽い火傷事故', '調理中にスタッフが軽い火傷をしました。すぐに冷水で冷やし、応急処置を行いました。幸い軽傷で済みましたが、防護具の着用を再徹底します。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '13:30:00'),
(3, 'manager_002', '2026-01-30'::DATE - INTERVAL '9 days', 'report', 'other', '月間売上目標達成', '今月の売上目標を3日前倒しで達成しました。新メニューの販促キャンペーンが好調でした。来月はさらに5%増を目指します。', true, '2026-01-30'::DATE - INTERVAL '9 days' + TIME '22:00:00'),
(3, 'A3', '2026-01-30'::DATE - INTERVAL '14 days', 'claim', 'cashier', 'クーポン適用ミス', 'クーポンの適用を忘れてしまい、お客様に再度レジ打ちをお願いしてしまいました。クーポン確認の声かけを習慣化します。', true, '2026-01-30'::DATE - INTERVAL '14 days' + TIME '19:30:00'),
(3, 'B3', '2026-01-30'::DATE - INTERVAL '17 days', 'praise', 'hall', 'アレルギー対応への感謝', 'アレルギーをお持ちのお客様に丁寧に対応したところ、大変感謝されました。アレルギー表を確認しながらの説明が安心感につながったようです。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '13:00:00'),
(3, 'B1', '2026-01-30'::DATE - INTERVAL '21 days', 'report', 'kitchen', 'メニュー改善の提案', '人気メニューのカレーライスについて、ルーの量を少し増やす提案をさせていただきます。お客様からの「もう少しルーが欲しい」という声が多いためです。', true, '2026-01-30'::DATE - INTERVAL '21 days' + TIME '16:00:00'),

-- 池袋西口店の日報
(4, 'C1', '2026-01-30'::DATE - INTERVAL '2 days', 'claim', 'toilet', 'トイレ清掃の指摘', 'お客様からトイレが汚れているとのご指摘を受けました。清掃頻度を30分から20分間隔に変更しました。', true, '2026-01-30'::DATE - INTERVAL '2 days' + TIME '16:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '5 days', 'praise', 'hall', '誕生日サプライズが好評', 'お客様の誕生日祝いでデザートプレートをサービスしたところ、大変喜んでいただけました。SNSにも投稿していただけるとのことです。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '20:00:00'),
(4, 'manager_003', '2026-01-30'::DATE - INTERVAL '8 days', 'accident', 'hall', '空調設備の故障', '店内の空調が効かなくなりました。お客様にはご不便をおかけしましたが、扇風機で応急対応し、翌日修理完了しました。', true, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '14:00:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '13 days', 'report', 'other', 'テイクアウト需要増加', '最近テイクアウトの注文が増えています。専用の受け渡し窓口の設置を検討してはいかがでしょうか。', true, '2026-01-30'::DATE - INTERVAL '13 days' + TIME '18:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '19 days', 'claim', 'kitchen', '料理の温度が低い', 'お客様から「スープがぬるい」とご指摘を受けました。提供前の温度確認を徹底します。', true, '2026-01-30'::DATE - INTERVAL '19 days' + TIME '12:30:00'),

-- 横浜駅前店の日報
(5, 'C3', '2026-01-30'::DATE - INTERVAL '1 day', 'praise', 'hall', '接客対応を褒められました', 'お客様アンケートで「スタッフの笑顔が素晴らしい」と高評価をいただきました。日頃の接客研修の成果が出ています。', true, '2026-01-30'::DATE - INTERVAL '1 day' + TIME '21:00:00'),
(5, 'D1', '2026-01-30'::DATE - INTERVAL '3 days', 'claim', 'hall', '予約時間のズレ', '予約システムの時間設定にずれがあり、お客様をお待たせしてしまいました。システムの時刻同期を確認しました。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '19:00:00'),
(5, 'D2', '2026-01-30'::DATE - INTERVAL '7 days', 'accident', 'kitchen', '食器破損', 'お皿を3枚割ってしまいました。運搬時の持ち方を再確認しました。けが人はいません。', false, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '11:00:00'),
(5, 'manager_004', '2026-01-30'::DATE - INTERVAL '11 days', 'report', 'other', '近隣店舗との連携', '隣接するショッピングモールのイベントと連動したキャンペーンを実施し、新規客が20%増加しました。', true, '2026-01-30'::DATE - INTERVAL '11 days' + TIME '22:00:00'),
(5, 'C3', '2026-01-30'::DATE - INTERVAL '16 days', 'praise', 'kitchen', 'ランチセットが好評', '新しく始めたビジネスランチセットが好評です。周辺オフィスからのリピーターが増えています。', true, '2026-01-30'::DATE - INTERVAL '16 days' + TIME '14:30:00'),
(5, 'D1', '2026-01-30'::DATE - INTERVAL '23 days', 'claim', 'cashier', 'ポイントカードの読み取りエラー', 'ポイントカードの読み取り機が不調で、手動入力での対応となりました。機器のメンテナンスを依頼しました。', true, '2026-01-30'::DATE - INTERVAL '23 days' + TIME '17:00:00'),

-- 大阪梅田店の日報
(6, 'D3', '2026-01-30'::DATE - INTERVAL '1 day', 'claim', 'hall', '注文間違い', 'オーダー取り違えがあり、お客様にご迷惑をおかけしました。注文確認の復唱を徹底します。', true, '2026-01-30'::DATE - INTERVAL '1 day' + TIME '13:00:00'),
(6, 'staff_014', '2026-01-30'::DATE - INTERVAL '4 days', 'praise', 'hall', '関西弁での接客が好評', '地元のお客様から「親しみやすい接客」と好評をいただきました。土地柄に合わせた接客スタイルが功を奏しています。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '15:30:00'),
(6, 'staff_015', '2026-01-30'::DATE - INTERVAL '8 days', 'accident', 'kitchen', '冷蔵庫の温度異常', '冷蔵庫の温度が8度まで上昇していることを発見。食材の確認を行い、修理業者を手配しました。', true, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '09:00:00'),
(6, 'manager_005', '2026-01-30'::DATE - INTERVAL '12 days', 'report', 'other', '新メニュー導入結果', '大阪限定のたこ焼き風メニューが予想以上の人気です。月間売上の15%を占めるようになりました。', true, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '21:30:00'),
(6, 'D3', '2026-01-30'::DATE - INTERVAL '18 days', 'praise', 'hall', 'グループ客への対応', '大人数のグループ客への対応がスムーズにでき、感謝されました。事前の席配置計画が効果的でした。', true, '2026-01-30'::DATE - INTERVAL '18 days' + TIME '20:00:00'),
(6, 'staff_014', '2026-01-30'::DATE - INTERVAL '24 days', 'claim', 'toilet', 'トイレットペーパー切れ', 'トイレットペーパーの補充が間に合わず、お客様にご不便をおかけしました。在庫チェックの頻度を増やします。', false, '2026-01-30'::DATE - INTERVAL '24 days' + TIME '16:00:00'),

-- 名古屋栄店の日報
(7, 'staff_016', '2026-01-30'::DATE - INTERVAL '2 days', 'praise', 'kitchen', '手羽先メニューが人気', '名古屋らしい手羽先の新メニューが大人気です。週末は品切れになることもあるほどです。仕込み量を増やす検討をしています。', true, '2026-01-30'::DATE - INTERVAL '2 days' + TIME '14:00:00'),
(7, 'staff_017', '2026-01-30'::DATE - INTERVAL '6 days', 'claim', 'hall', '席の案内ミス', 'お客様を間違った席にご案内してしまいました。座席番号の確認を徹底します。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '18:30:00'),
(7, 'manager_006', '2026-01-30'::DATE - INTERVAL '10 days', 'report', 'other', 'スタッフミーティング実施', '月例のスタッフミーティングを実施しました。接客品質向上に向けた意見交換ができました。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '22:30:00'),
(7, 'staff_016', '2026-01-30'::DATE - INTERVAL '15 days', 'accident', 'hall', 'ドリンクこぼし', 'お客様にドリンクをこぼしてしまいました。クリーニング代をお支払いし、お詫びしました。トレー使用を徹底します。', true, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '19:00:00'),
(7, 'staff_017', '2026-01-30'::DATE - INTERVAL '20 days', 'praise', 'hall', '常連様への記念サービス', '100回目のご来店の常連様に特別サービスを行い、大変喜んでいただけました。', true, '2026-01-30'::DATE - INTERVAL '20 days' + TIME '20:30:00'),

-- 福岡天神店の日報
(8, 'staff_018', '2026-01-30'::DATE - INTERVAL '1 day', 'praise', 'hall', 'もつ鍋が大好評', '冬季限定のもつ鍋が大変好評です。博多らしさを出せているとのお声をいただきました。', true, '2026-01-30'::DATE - INTERVAL '1 day' + TIME '21:00:00'),
(8, 'staff_019', '2026-01-30'::DATE - INTERVAL '5 days', 'claim', 'kitchen', '辛さの調整ミス', '激辛メニューの辛さが強すぎるとのご指摘がありました。レシピの分量を再確認しました。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '14:00:00'),
(8, 'manager_007', '2026-01-30'::DATE - INTERVAL '9 days', 'report', 'other', '観光シーズンの売上増', '修学旅行シーズンで客数が増加しています。団体客への対応マニュアルを整備しました。', true, '2026-01-30'::DATE - INTERVAL '9 days' + TIME '22:00:00'),
(8, 'staff_018', '2026-01-30'::DATE - INTERVAL '14 days', 'accident', 'hall', 'メニュー表の破損', 'メニュー表が汚れて読みにくくなっていたため、新しいものに交換しました。定期交換のスケジュールを設定します。', false, '2026-01-30'::DATE - INTERVAL '14 days' + TIME '10:00:00'),
(8, 'staff_019', '2026-01-30'::DATE - INTERVAL '19 days', 'praise', 'hall', 'インバウンド対応', '韓国からの観光客に英語と身振りで丁寧に対応したところ、大変喜ばれました。多言語メニューの効果を実感しました。', true, '2026-01-30'::DATE - INTERVAL '19 days' + TIME '16:00:00'),

-- 札幌駅前店の日報
(9, 'staff_020', '2026-01-30'::DATE - INTERVAL '2 days', 'praise', 'kitchen', '味噌ラーメンが好評', '北海道らしい味噌ラーメンが観光客に好評です。「本場の味」とSNSでも拡散されています。', true, '2026-01-30'::DATE - INTERVAL '2 days' + TIME '15:00:00'),
(9, 'staff_021', '2026-01-30'::DATE - INTERVAL '6 days', 'claim', 'hall', '暖房の効きが悪い', '窓際の席が寒いとのご指摘を受けました。追加の暖房器具を設置しました。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '13:00:00'),
(9, 'manager_008', '2026-01-30'::DATE - INTERVAL '11 days', 'report', 'other', '雪まつり期間の対策', '来月の雪まつり期間に向けて、スタッフのシフト強化と仕込み量の増加を計画しています。', true, '2026-01-30'::DATE - INTERVAL '11 days' + TIME '21:00:00'),
(9, 'staff_020', '2026-01-30'::DATE - INTERVAL '16 days', 'accident', 'other', '除雪作業中の怪我', '店舗前の除雪作業中にスタッフが転倒しました。幸い軽傷でしたが、安全靴の着用を義務化しました。', true, '2026-01-30'::DATE - INTERVAL '16 days' + TIME '08:30:00'),
(9, 'staff_021', '2026-01-30'::DATE - INTERVAL '22 days', 'praise', 'hall', '地元食材のPR', '地元の農家から仕入れた野菜を使ったサラダが好評です。お客様から「新鮮で美味しい」とお褒めいただきました。', true, '2026-01-30'::DATE - INTERVAL '22 days' + TIME '14:30:00'),

-- 仙台駅前店の日報
(10, 'staff_022', '2026-01-30'::DATE - INTERVAL '1 day', 'praise', 'kitchen', '牛タン定食が人気', '仙台名物の牛タン定食が連日完売しています。仕入れ量を増やす方向で調整中です。', true, '2026-01-30'::DATE - INTERVAL '1 day' + TIME '20:00:00'),
(10, 'staff_023', '2026-01-30'::DATE - INTERVAL '4 days', 'claim', 'cashier', 'お釣りの間違い', 'お釣りの金額を間違えてしまいました。確認の声出しを徹底します。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '17:00:00'),
(10, 'manager_009', '2026-01-30'::DATE - INTERVAL '8 days', 'report', 'other', 'オープン2ヶ月の振り返り', '開店から2ヶ月が経過しました。売上は計画比95%とほぼ順調です。認知度向上に向けた地域イベントへの参加を検討しています。', true, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '22:00:00'),
(10, 'staff_022', '2026-01-30'::DATE - INTERVAL '13 days', 'accident', 'kitchen', 'ガス漏れ検知器の誤作動', 'ガス漏れ検知器が誤作動しました。点検の結果、センサーの故障と判明し交換しました。', true, '2026-01-30'::DATE - INTERVAL '13 days' + TIME '11:00:00'),
(10, 'staff_023', '2026-01-30'::DATE - INTERVAL '18 days', 'praise', 'hall', '家族連れへの対応', '小さなお子様連れのご家族に子供用イスとおもちゃを用意したところ、とても喜んでいただけました。', true, '2026-01-30'::DATE - INTERVAL '18 days' + TIME '15:00:00');

-- ============================================================
-- 4-2. 追加日報データ（同一日に複数件、場所別偏り、週末集中パターン）
-- ============================================================
-- 特徴:
--   - 週末（土日）にインシデント集中
--   - キッチン: 事故が多め（火傷、器具故障）
--   - ホール: クレーム・賞賛両方多い
--   - レジ: 違算、対応ミス
--   - トイレ: 清掃関連

INSERT INTO daily_reports (store_id, user_id, date, genre, location, title, content, post_to_bbs, created_at) VALUES

-- ========== 繁忙日（週末）に複数件発生パターン ==========

-- 3日前の土曜日（複数店舗で同時発生）
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '3 days', 'claim', 'hall', 'ピーク時の待ち時間クレーム', '12時台のピーク時に30分以上お待たせしてしまいました。予約システムの見直しが必要です。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '13:30:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '3 days', 'claim', 'kitchen', '料理提供遅延のクレーム', 'キッチンの混雑により、料理提供が40分かかりお客様から苦情。オペレーション改善を検討。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '14:00:00'),
(2, 'A2', '2026-01-30'::DATE - INTERVAL '3 days', 'accident', 'hall', 'ドリンクをこぼす事故', 'ホール混雑時にドリンクをお客様の服にこぼしてしまいました。クリーニング代をお支払いしました。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '14:30:00'),
(3, 'A3', '2026-01-30'::DATE - INTERVAL '3 days', 'claim', 'cashier', 'クレジットカード決済エラー', '決済端末の不具合で会計に時間がかかり、お客様をお待たせしました。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '13:00:00'),
(3, 'B1', '2026-01-30'::DATE - INTERVAL '3 days', 'claim', 'hall', '席の案内ミス', '予約席を誤って他のお客様に案内してしまいました。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '12:30:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '3 days', 'accident', 'kitchen', 'フライヤーでの軽い火傷', '揚げ物中に油が跳ねて軽い火傷。すぐに冷水で冷やし処置しました。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '11:45:00'),
(5, 'C3', '2026-01-30'::DATE - INTERVAL '3 days', 'claim', 'toilet', 'トイレ清掃不備の指摘', 'お客様からトイレが汚れているとご指摘。清掃頻度を増やします。', true, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '15:00:00'),

-- 4日前の金曜日（夜のピーク）
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '4 days', 'claim', 'hall', '予約確認ミス', '電話予約の時間を聞き間違え、お客様をお待たせしてしまいました。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '19:30:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '4 days', 'praise', 'hall', '記念日のサプライズ成功', 'お誕生日のお客様へのサプライズデザートが大変喜ばれました。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '20:00:00'),
(3, 'B2', '2026-01-30'::DATE - INTERVAL '4 days', 'claim', 'kitchen', '注文の作り間違い', 'アレルギー対応メニューの指示が伝わらず、作り直しになりました。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '19:00:00'),
(6, 'D3', '2026-01-30'::DATE - INTERVAL '4 days', 'accident', 'hall', 'グラス破損', '食器を運ぶ際にグラスを3つ割ってしまいました。怪我人なし。', true, '2026-01-30'::DATE - INTERVAL '4 days' + TIME '21:00:00'),

-- 10日前の土曜日（複数件）
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '10 days', 'claim', 'hall', '子供が走り回る問題', 'お子様連れのお客様のお子さんが店内を走り回り、他のお客様からクレーム。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '12:00:00'),
(2, 'A2', '2026-01-30'::DATE - INTERVAL '10 days', 'claim', 'cashier', 'ポイント付与忘れ', 'ポイントカードへのポイント付与を忘れ、後から対応しました。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '14:00:00'),
(3, 'A3', '2026-01-30'::DATE - INTERVAL '10 days', 'accident', 'kitchen', 'オーブンの過熱', 'オーブンが異常加熱し、自動停止しました。メンテナンス依頼済み。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '11:30:00'),
(3, 'B3', '2026-01-30'::DATE - INTERVAL '10 days', 'claim', 'hall', '隣席の騒音クレーム', '宴会グループの騒音について、隣のテーブルからクレーム。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '20:30:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '10 days', 'claim', 'toilet', 'トイレットペーパー切れ', '補充が間に合わず、お客様にご不便をおかけしました。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '13:00:00'),
(5, 'D1', '2026-01-30'::DATE - INTERVAL '10 days', 'praise', 'hall', '外国人観光客への対応', '英語での丁寧な説明に感謝されました。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '15:00:00'),
(6, 'staff_014', '2026-01-30'::DATE - INTERVAL '10 days', 'claim', 'hall', '料理の温度クレーム', 'スープがぬるいとのご指摘。キッチンとの連携を強化します。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '12:30:00'),

-- 17日前の土曜日（複数件）
(2, 'A1', '2026-01-30'::DATE - INTERVAL '17 days', 'accident', 'kitchen', '包丁で指を切る', '仕込み中に包丁で指を切りました。絆創膏で処置し、調理用手袋を着用。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '10:00:00'),
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '17 days', 'claim', 'hall', '注文取り違え', 'テーブル番号を間違えて料理を配膳してしまいました。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '13:00:00'),
(3, 'B1', '2026-01-30'::DATE - INTERVAL '17 days', 'claim', 'cashier', '割引適用ミス', 'クーポンの割引率を間違えて計算してしまいました。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '19:00:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '17 days', 'accident', 'hall', '床が滑りやすい状態', '雨で床が濡れ、お客様が転びそうになりました。マット追加設置。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '14:00:00'),
(5, 'D2', '2026-01-30'::DATE - INTERVAL '17 days', 'claim', 'kitchen', '異物混入の指摘', 'サラダに髪の毛が混入しているとのご指摘。調理時の帽子着用を徹底。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '12:00:00'),
(6, 'staff_015', '2026-01-30'::DATE - INTERVAL '17 days', 'praise', 'hall', '常連客からの感謝', '毎週来店のお客様から「いつも心地よい」とお言葉をいただきました。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '18:00:00'),
(7, 'staff_016', '2026-01-30'::DATE - INTERVAL '17 days', 'claim', 'hall', '提供時間の遅れ', 'オーダーから50分かかりお客様をお待たせ。お詫びのデザートを提供。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '13:30:00'),
(8, 'staff_018', '2026-01-30'::DATE - INTERVAL '17 days', 'accident', 'kitchen', '冷蔵庫のドア故障', '冷蔵庫のドアが閉まりにくくなり、温度上昇。修理業者を呼びました。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '09:00:00'),

-- ========== 場所別の偏りパターン ==========

-- キッチン関連（事故が多め）
(2, 'A1', '2026-01-30'::DATE - INTERVAL '6 days', 'accident', 'kitchen', 'フライパンの取っ手が熱い', '取っ手カバーが外れており、スタッフが軽い火傷。すぐに交換しました。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '11:00:00'),
(3, 'B2', '2026-01-30'::DATE - INTERVAL '8 days', 'accident', 'kitchen', '換気扇の異常音', '換気扇から異音がするようになりました。メンテナンス予約済み。', false, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '10:00:00'),
(4, 'manager_003', '2026-01-30'::DATE - INTERVAL '11 days', 'accident', 'kitchen', 'ガスコンロの点火不良', 'コンロの一口が点火しなくなりました。業者を呼んで修理。', true, '2026-01-30'::DATE - INTERVAL '11 days' + TIME '09:30:00'),
(5, 'D1', '2026-01-30'::DATE - INTERVAL '14 days', 'accident', 'kitchen', '食器洗浄機の水漏れ', '食洗機から水漏れ発生。応急処置後、修理依頼しました。', true, '2026-01-30'::DATE - INTERVAL '14 days' + TIME '16:00:00'),
(6, 'staff_014', '2026-01-30'::DATE - INTERVAL '16 days', 'accident', 'kitchen', '製氷機の故障', '製氷機が氷を作らなくなりました。近隣店舗から氷を調達中。', true, '2026-01-30'::DATE - INTERVAL '16 days' + TIME '14:00:00'),
(7, 'staff_017', '2026-01-30'::DATE - INTERVAL '19 days', 'accident', 'kitchen', '排水溝の詰まり', '排水が遅くなり、業者に清掃依頼しました。', false, '2026-01-30'::DATE - INTERVAL '19 days' + TIME '21:00:00'),
(8, 'staff_019', '2026-01-30'::DATE - INTERVAL '21 days', 'accident', 'kitchen', 'レンジの故障', '電子レンジが動作しなくなりました。新しいものを発注。', true, '2026-01-30'::DATE - INTERVAL '21 days' + TIME '12:00:00'),
(9, 'staff_021', '2026-01-30'::DATE - INTERVAL '23 days', 'accident', 'kitchen', 'グリルの温度調節不良', 'グリルの温度が安定しません。サーモスタットの交換が必要かも。', true, '2026-01-30'::DATE - INTERVAL '23 days' + TIME '11:00:00'),

-- ホール関連（クレーム・賞賛両方）
(2, 'A2', '2026-01-30'::DATE - INTERVAL '6 days', 'praise', 'hall', 'お子様への配慮', 'お子様用の小さなスプーンをお出ししたところ、とても喜ばれました。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '12:30:00'),
(3, 'B3', '2026-01-30'::DATE - INTERVAL '7 days', 'claim', 'hall', '空調が効きすぎ', '冷房が強すぎるとのご指摘。温度調整しました。', false, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '14:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '9 days', 'praise', 'hall', '雨の日の傘袋サービス', '雨の日に傘袋をお渡ししたところ、感謝されました。', true, '2026-01-30'::DATE - INTERVAL '9 days' + TIME '18:00:00'),
(5, 'C3', '2026-01-30'::DATE - INTERVAL '11 days', 'claim', 'hall', 'BGMがうるさい', '音楽の音量が大きいとのご指摘。音量を下げました。', false, '2026-01-30'::DATE - INTERVAL '11 days' + TIME '20:00:00'),
(6, 'D3', '2026-01-30'::DATE - INTERVAL '13 days', 'praise', 'hall', '荷物預かりサービス', '買い物袋をお預かりしたところ、大変喜ばれました。', true, '2026-01-30'::DATE - INTERVAL '13 days' + TIME '13:00:00'),
(7, 'staff_016', '2026-01-30'::DATE - INTERVAL '15 days', 'claim', 'hall', '椅子が不安定', '椅子がぐらつくとのご指摘。すぐに交換しました。', false, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '12:00:00'),
(8, 'staff_018', '2026-01-30'::DATE - INTERVAL '16 days', 'praise', 'hall', '誕生日サプライズ', 'お誕生日のお客様にスタッフ全員でお祝いし、感動していただけました。', true, '2026-01-30'::DATE - INTERVAL '16 days' + TIME '19:00:00'),
(9, 'staff_020', '2026-01-30'::DATE - INTERVAL '18 days', 'claim', 'hall', 'テーブルが汚れていた', '前のお客様の食べこぼしが残っていました。清掃を徹底します。', true, '2026-01-30'::DATE - INTERVAL '18 days' + TIME '11:30:00'),
(10, 'staff_022', '2026-01-30'::DATE - INTERVAL '20 days', 'praise', 'hall', '車椅子対応への感謝', '車椅子のお客様にスロープをご案内し、感謝されました。', true, '2026-01-30'::DATE - INTERVAL '20 days' + TIME '14:00:00'),

-- レジ関連（違算、対応ミス）
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '7 days', 'claim', 'cashier', 'お会計の二重請求', '同じ商品を2回打ってしまい、返金対応しました。', true, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '21:00:00'),
(3, 'B1', '2026-01-30'::DATE - INTERVAL '9 days', 'claim', 'cashier', 'レシート発行忘れ', 'レシートを渡し忘れ、お客様から連絡がありました。', false, '2026-01-30'::DATE - INTERVAL '9 days' + TIME '14:30:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '12 days', 'claim', 'cashier', '現金過不足', '閉店時に500円の過不足が発生。原因調査中。', true, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '22:30:00'),
(5, 'D2', '2026-01-30'::DATE - INTERVAL '15 days', 'claim', 'cashier', '電子マネー残高不足時の対応', '残高不足のお客様への説明が不十分でご不満を招きました。', true, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '13:00:00'),
(6, 'staff_015', '2026-01-30'::DATE - INTERVAL '18 days', 'claim', 'cashier', '領収書の宛名間違い', '領収書の宛名を書き間違え、再発行しました。', false, '2026-01-30'::DATE - INTERVAL '18 days' + TIME '20:00:00'),
(7, 'manager_006', '2026-01-30'::DATE - INTERVAL '21 days', 'report', 'cashier', 'レジ締め時間の短縮', 'チェックリスト導入でレジ締め時間を15分短縮できました。', true, '2026-01-30'::DATE - INTERVAL '21 days' + TIME '23:00:00'),

-- トイレ関連（清掃関連）
(2, 'A2', '2026-01-30'::DATE - INTERVAL '8 days', 'claim', 'toilet', '手洗い石鹸切れ', '石鹸が切れていたとのご指摘。補充体制を見直します。', false, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '15:00:00'),
(3, 'B2', '2026-01-30'::DATE - INTERVAL '12 days', 'claim', 'toilet', '便座が冷たい', '暖房便座の電源が切れていました。', false, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '10:00:00'),
(4, 'manager_003', '2026-01-30'::DATE - INTERVAL '15 days', 'report', 'toilet', 'トイレ芳香剤の導入', '新しい芳香剤を導入し、お客様から好評です。', true, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '17:00:00'),
(5, 'C3', '2026-01-30'::DATE - INTERVAL '19 days', 'claim', 'toilet', 'ウォシュレット故障', 'ウォシュレットが動作しなくなりました。修理依頼済み。', true, '2026-01-30'::DATE - INTERVAL '19 days' + TIME '11:00:00'),
(6, 'staff_014', '2026-01-30'::DATE - INTERVAL '22 days', 'claim', 'toilet', '鏡が汚れている', '鏡の水垢が目立つとのご指摘。清掃頻度を上げます。', false, '2026-01-30'::DATE - INTERVAL '22 days' + TIME '16:00:00'),

-- ========== 各店舗の追加日報（バリエーション） ==========

-- 渋谷店追加
(2, 'manager_001', '2026-01-30'::DATE - INTERVAL '5 days', 'report', 'other', 'スタッフミーティング実施', '月次ミーティングを実施。売上目標と課題を共有しました。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '22:00:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '9 days', 'praise', 'kitchen', '新メニューが好評', '季節限定のパスタが大変好評です。リピーターも増えています。', true, '2026-01-30'::DATE - INTERVAL '9 days' + TIME '14:00:00'),
(2, 'A2', '2026-01-30'::DATE - INTERVAL '13 days', 'claim', 'hall', 'お子様の食器破損', 'お子様が食器を落として割ってしまいました。怪我なし。', false, '2026-01-30'::DATE - INTERVAL '13 days' + TIME '12:30:00'),
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '16 days', 'praise', 'hall', 'SNS投稿でバズる', 'お客様のSNS投稿が拡散し、新規のお客様が増えました。', true, '2026-01-30'::DATE - INTERVAL '16 days' + TIME '18:00:00'),

-- 新宿店追加
(3, 'manager_002', '2026-01-30'::DATE - INTERVAL '5 days', 'report', 'other', '深夜帯の人員調整', '金曜の深夜帯スタッフを1名増員することにしました。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '23:00:00'),
(3, 'A3', '2026-01-30'::DATE - INTERVAL '11 days', 'praise', 'hall', 'リピーター率向上', '常連のお客様が増えてきました。名前を覚えて挨拶する効果です。', true, '2026-01-30'::DATE - INTERVAL '11 days' + TIME '21:00:00'),
(3, 'B3', '2026-01-30'::DATE - INTERVAL '13 days', 'accident', 'other', '看板の電球切れ', '店頭看板の電球が切れました。翌日交換完了。', false, '2026-01-30'::DATE - INTERVAL '13 days' + TIME '20:00:00'),

-- 池袋店追加（V字回復中のストーリー）
(4, 'manager_003', '2026-01-30'::DATE - INTERVAL '5 days', 'report', 'other', '売上回復傾向', '先月の落ち込みから回復傾向です。接客研修の効果が出ています。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '22:00:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '7 days', 'praise', 'hall', 'Googleレビュー4.5達成', 'お客様からの評価が上がり、レビュー4.5を達成しました！', true, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '19:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '14 days', 'report', 'other', '新人研修完了', '新人2名の基本研修が完了しました。来週から本格稼働。', true, '2026-01-30'::DATE - INTERVAL '14 days' + TIME '21:00:00'),

-- 横浜店追加
(5, 'manager_004', '2026-01-30'::DATE - INTERVAL '6 days', 'report', 'other', 'モール連携キャンペーン', '隣接モールとの連携で来店数15%増加しました。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '21:00:00'),
(5, 'C3', '2026-01-30'::DATE - INTERVAL '12 days', 'praise', 'kitchen', 'ビジネスランチが人気', 'オフィス街でのランチ需要を取り込めています。', true, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '14:00:00'),
(5, 'D1', '2026-01-30'::DATE - INTERVAL '18 days', 'claim', 'hall', 'エアコン温度の不満', '窓際が暑いとのご意見。席替えで対応しました。', false, '2026-01-30'::DATE - INTERVAL '18 days' + TIME '13:00:00'),

-- 大阪店追加（期間限定メニューの成功ストーリー）
(6, 'manager_005', '2026-01-30'::DATE - INTERVAL '5 days', 'report', 'other', '限定メニュー売上報告', 'たこ焼き風メニューの売上が全体の18%を占めています。', true, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '22:00:00'),
(6, 'D3', '2026-01-30'::DATE - INTERVAL '9 days', 'praise', 'hall', '関西弁接客が好評', '親しみやすい接客スタイルがリピーターを生んでいます。', true, '2026-01-30'::DATE - INTERVAL '9 days' + TIME '20:00:00'),
(6, 'staff_015', '2026-01-30'::DATE - INTERVAL '14 days', 'praise', 'kitchen', 'お好み焼きが美味しいと評判', 'SNSで「関西の味が東京で食べられる」と話題に。', true, '2026-01-30'::DATE - INTERVAL '14 days' + TIME '15:00:00'),

-- 名古屋店追加
(7, 'manager_006', '2026-01-30'::DATE - INTERVAL '7 days', 'report', 'other', '地元食材フェア開始', '地元農家との連携で新鮮野菜を提供開始しました。', true, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '21:00:00'),
(7, 'staff_016', '2026-01-30'::DATE - INTERVAL '12 days', 'praise', 'kitchen', '手羽先が連日完売', '名古屋名物の手羽先が毎日売り切れる人気です。', true, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '21:00:00'),
(7, 'staff_017', '2026-01-30'::DATE - INTERVAL '17 days', 'claim', 'hall', '喫煙エリアの煙', '喫煙エリアからの煙が禁煙席に流れるとのご指摘。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '19:00:00'),

-- 福岡店追加
(8, 'manager_007', '2026-01-30'::DATE - INTERVAL '6 days', 'report', 'other', '修学旅行シーズン対応', '団体客マニュアルが功を奏しています。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '22:00:00'),
(8, 'staff_018', '2026-01-30'::DATE - INTERVAL '11 days', 'praise', 'hall', '博多弁で接客', 'お客様から「地元感があって良い」と好評。', true, '2026-01-30'::DATE - INTERVAL '11 days' + TIME '14:00:00'),
(8, 'staff_019', '2026-01-30'::DATE - INTERVAL '17 days', 'claim', 'kitchen', '明太子パスタの辛さ', '辛すぎるとのご意見。レシピを微調整しました。', true, '2026-01-30'::DATE - INTERVAL '17 days' + TIME '13:00:00'),

-- 札幌店追加
(9, 'manager_008', '2026-01-30'::DATE - INTERVAL '7 days', 'report', 'other', '雪まつり対策会議', '来月の雪まつりに向けた準備会議を実施しました。', true, '2026-01-30'::DATE - INTERVAL '7 days' + TIME '21:00:00'),
(9, 'staff_020', '2026-01-30'::DATE - INTERVAL '12 days', 'praise', 'kitchen', '味噌バターコーンが人気', '北海道らしいメニューが観光客に大好評です。', true, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '15:00:00'),
(9, 'staff_021', '2026-01-30'::DATE - INTERVAL '19 days', 'accident', 'other', '駐車場の除雪', '大雪で駐車場が使えなくなり、除雪業者を呼びました。', true, '2026-01-30'::DATE - INTERVAL '19 days' + TIME '08:00:00'),

-- 仙台店追加（成長中のストーリー）
(10, 'manager_009', '2026-01-30'::DATE - INTERVAL '6 days', 'report', 'other', '認知度向上施策', '地域イベントへの出店で認知度アップに成功。', true, '2026-01-30'::DATE - INTERVAL '6 days' + TIME '21:00:00'),
(10, 'staff_022', '2026-01-30'::DATE - INTERVAL '10 days', 'praise', 'hall', '地元客が増加', 'リピーターになってくださる地元のお客様が増えています。', true, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '19:00:00'),
(10, 'staff_023', '2026-01-30'::DATE - INTERVAL '15 days', 'praise', 'kitchen', '牛タン以外も好評', 'ずんだシェイクが若い女性に人気です。', true, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '16:00:00'),

-- ========== 古いデータ（30日以上前、改善傾向を示す） ==========

-- 30日前（クレームが多かった時期）
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '30 days', 'claim', 'hall', '予約システムの不具合', 'オンライン予約が反映されず混乱。システム会社に連絡。', true, '2026-01-30'::DATE - INTERVAL '30 days' + TIME '12:00:00'),
(2, 'A1', '2026-01-30'::DATE - INTERVAL '30 days', 'claim', 'kitchen', '料理の品質クレーム', 'ステーキの焼き加減が違うとご指摘。作り直しました。', true, '2026-01-30'::DATE - INTERVAL '30 days' + TIME '19:00:00'),
(3, 'A3', '2026-01-30'::DATE - INTERVAL '30 days', 'claim', 'hall', '待ち時間が長い', 'ピーク時1時間待ちでお客様が帰られました。', true, '2026-01-30'::DATE - INTERVAL '30 days' + TIME '13:00:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '30 days', 'claim', 'cashier', 'お釣り間違い多発', '本日3件のお釣り間違いが発生。研修を実施します。', true, '2026-01-30'::DATE - INTERVAL '30 days' + TIME '22:00:00'),

-- 35日前
(2, 'A2', '2026-01-30'::DATE - INTERVAL '35 days', 'claim', 'toilet', 'トイレの臭い', '換気扇の故障でトイレが臭いとのクレーム。', true, '2026-01-30'::DATE - INTERVAL '35 days' + TIME '14:00:00'),
(3, 'B1', '2026-01-30'::DATE - INTERVAL '35 days', 'accident', 'kitchen', '食材の発注ミス', '発注量を間違え、ランチタイムに食材切れ。', true, '2026-01-30'::DATE - INTERVAL '35 days' + TIME '12:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '35 days', 'claim', 'hall', '接客態度への苦情', 'スタッフの態度が悪いとのお叱り。個別指導しました。', true, '2026-01-30'::DATE - INTERVAL '35 days' + TIME '20:00:00'),

-- 40日前（池袋店の落ち込み期）
(4, 'manager_003', '2026-01-30'::DATE - INTERVAL '40 days', 'report', 'other', '売上低迷の原因分析', '周辺の競合店オープンによる影響を分析中。', true, '2026-01-30'::DATE - INTERVAL '40 days' + TIME '22:00:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '40 days', 'claim', 'hall', '常連客の離脱', '長年の常連様から「最近サービスが悪い」とご意見。', true, '2026-01-30'::DATE - INTERVAL '40 days' + TIME '21:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '42 days', 'claim', 'kitchen', '提供時間の遅延', '平均提供時間が30分を超えています。改善策を検討中。', true, '2026-01-30'::DATE - INTERVAL '42 days' + TIME '14:00:00'),

-- 45日前（クレーム多発期）
(2, 'staff_001', '2026-01-30'::DATE - INTERVAL '45 days', 'claim', 'hall', '混雑時の対応不備', 'スタッフ不足で対応が遅れ、複数のクレーム。', true, '2026-01-30'::DATE - INTERVAL '45 days' + TIME '13:00:00'),
(3, 'B2', '2026-01-30'::DATE - INTERVAL '45 days', 'claim', 'cashier', 'ポイントカードエラー', 'システムエラーでポイントが消えたとのクレーム。', true, '2026-01-30'::DATE - INTERVAL '45 days' + TIME '19:00:00'),
(5, 'C3', '2026-01-30'::DATE - INTERVAL '45 days', 'accident', 'hall', 'お客様の転倒事故', '床の水で滑って転倒。幸い軽傷でしたが、お見舞いしました。', true, '2026-01-30'::DATE - INTERVAL '45 days' + TIME '12:00:00'),

-- 50日前（池袋店の最悪期）
(4, 'manager_003', '2026-01-30'::DATE - INTERVAL '50 days', 'report', 'other', '緊急スタッフミーティング', '売上低迷とクレーム増加について緊急会議を実施。', true, '2026-01-30'::DATE - INTERVAL '50 days' + TIME '22:00:00'),
(4, 'C1', '2026-01-30'::DATE - INTERVAL '50 days', 'claim', 'hall', '予約のダブルブッキング', '同じ時間に2組の予約が入ってしまいました。', true, '2026-01-30'::DATE - INTERVAL '50 days' + TIME '18:00:00'),
(4, 'C2', '2026-01-30'::DATE - INTERVAL '52 days', 'claim', 'kitchen', '食中毒の疑い', 'お客様から体調不良の連絡。調査の結果、別原因と判明。', true, '2026-01-30'::DATE - INTERVAL '52 days' + TIME '10:00:00'),

-- 55-60日前（各店舗の古いデータ）
(2, 'A1', '2026-01-30'::DATE - INTERVAL '55 days', 'claim', 'hall', 'エアコン故障', '真夏にエアコンが故障し、お客様に謝罪。当日修理完了。', true, '2026-01-30'::DATE - INTERVAL '55 days' + TIME '14:00:00'),
(3, 'B3', '2026-01-30'::DATE - INTERVAL '57 days', 'accident', 'kitchen', '冷凍庫の温度異常', '-18度を維持できず、一部食材を廃棄。', true, '2026-01-30'::DATE - INTERVAL '57 days' + TIME '09:00:00'),
(5, 'D1', '2026-01-30'::DATE - INTERVAL '58 days', 'claim', 'cashier', 'クレジットカード手数料説明不足', '手数料について説明不足でトラブル。', true, '2026-01-30'::DATE - INTERVAL '58 days' + TIME '20:00:00'),
(6, 'D3', '2026-01-30'::DATE - INTERVAL '60 days', 'claim', 'hall', '子供用椅子の不足', '繁忙期に子供用椅子が足りず、お客様をお待たせ。', true, '2026-01-30'::DATE - INTERVAL '60 days' + TIME '12:00:00');

-- シーケンスの更新
SELECT setval('daily_reports_report_id_seq', (SELECT MAX(report_id) FROM daily_reports));

-- ============================================================
-- 5. 掲示板投稿データ (日報からの自動投稿 + 直接投稿)
-- ============================================================

-- 日報からの自動連携投稿（post_to_bbs = true の日報に対応）
INSERT INTO bbs_posts (store_id, user_id, report_id, genre, title, content, comment_count, created_at, updated_at)
SELECT
    r.store_id,
    r.user_id,
    r.report_id,
    r.genre,
    r.title,
    r.content,
    0,
    r.created_at,
    r.created_at
FROM daily_reports r
WHERE r.post_to_bbs = true;

-- 直接投稿（日報と連携しない掲示板投稿）
INSERT INTO bbs_posts (store_id, user_id, report_id, genre, title, content, comment_count, created_at, updated_at) VALUES
-- 全店舗向けの情報共有
(1, 'admin', NULL, 'report', '年末年始の営業時間について', '年末年始の営業時間は以下の通りです。12/31は18時まで、1/1は休業、1/2から通常営業となります。各店舗での対応をお願いします。', 0, '2026-01-30'::DATE - INTERVAL '30 days' + TIME '10:00:00', '2026-01-30'::DATE - INTERVAL '30 days' + TIME '10:00:00'),
(1, 'honbu_mgr', NULL, 'report', '新メニュー導入のお知らせ', '来月より全店舗で新メニュー「季節の彩りプレート」を導入します。レシピと原価計算表は別途メールで送付しますので、準備をお願いします。', 0, '2026-01-30'::DATE - INTERVAL '25 days' + TIME '11:00:00', '2026-01-30'::DATE - INTERVAL '25 days' + TIME '11:00:00'),
(1, 'admin', NULL, 'report', '衛生管理講習会の実施について', '来週、各店舗で衛生管理講習会を実施します。全スタッフ必須参加です。日程は店長に確認してください。', 0, '2026-01-30'::DATE - INTERVAL '20 days' + TIME '14:00:00', '2026-01-30'::DATE - INTERVAL '20 days' + TIME '14:00:00'),

-- 各店舗からの情報共有
(2, 'manager_001', NULL, 'report', 'ピーク時の動線改善案', 'ランチタイムの混雑緩和のため、テーブルレイアウトを変更しました。入口から奥に向かう一方通行の動線を作ることで、お客様の流れがスムーズになりました。他店舗でも参考にしてください。', 0, '2026-01-30'::DATE - INTERVAL '15 days' + TIME '21:00:00', '2026-01-30'::DATE - INTERVAL '15 days' + TIME '21:00:00'),
(3, 'manager_002', NULL, 'report', 'クレーム対応マニュアルの共有', 'クレーム対応の基本フローをまとめました。①まず謝罪 ②状況を確認 ③解決策を提示 ④フォローアップ。この流れを守ることで、多くの場合円満に解決できています。', 0, '2026-01-30'::DATE - INTERVAL '12 days' + TIME '20:00:00', '2026-01-30'::DATE - INTERVAL '12 days' + TIME '20:00:00'),
(6, 'manager_005', NULL, 'report', '地域限定メニューの成功事例', '大阪限定のたこ焼き風メニューが好調です。地域特性を活かしたメニュー開発の重要性を実感しました。他店舗でも地域限定メニューを検討してみてはいかがでしょうか。', 0, '2026-01-30'::DATE - INTERVAL '10 days' + TIME '22:00:00', '2026-01-30'::DATE - INTERVAL '10 days' + TIME '22:00:00'),

-- ベストプラクティスの共有
(5, 'C3', NULL, 'praise', '効果的なアップセルの方法', 'お会計時に「本日のデザートはいかがですか」と一言添えるだけで、デザート注文率が15%向上しました。シンプルですが効果的です。', 0, '2026-01-30'::DATE - INTERVAL '8 days' + TIME '19:00:00', '2026-01-30'::DATE - INTERVAL '8 days' + TIME '19:00:00'),
(4, 'C2', NULL, 'report', 'テイクアウト用パッケージの改善', 'テイクアウト用の容器を保温性の高いものに変更したところ、お客様から「帰宅後も温かかった」と好評です。少しコストは上がりますが、満足度向上に効果があります。', 0, '2026-01-30'::DATE - INTERVAL '5 days' + TIME '17:00:00', '2026-01-30'::DATE - INTERVAL '5 days' + TIME '17:00:00'),

-- 質問・相談
(8, 'staff_019', NULL, 'other', '外国人観光客への対応について質問', '最近、海外からのお客様が増えています。翻訳アプリ以外に効果的な対応方法があれば教えてください。', 0, '2026-01-30'::DATE - INTERVAL '3 days' + TIME '16:00:00', '2026-01-30'::DATE - INTERVAL '3 days' + TIME '16:00:00'),
(9, 'staff_020', NULL, 'other', '冬季の入口対策について', '雪や氷で入口が滑りやすくなっています。他の北国店舗ではどのような対策をしていますか？', 0, '2026-01-30'::DATE - INTERVAL '2 days' + TIME '15:00:00', '2026-01-30'::DATE - INTERVAL '2 days' + TIME '15:00:00');

-- シーケンスの更新
SELECT setval('bbs_posts_post_id_seq', (SELECT MAX(post_id) FROM bbs_posts));

-- ============================================================
-- 6. 掲示板コメントデータ
-- ============================================================

-- 各投稿へのコメント（post_idを動的に取得）
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'manager_001',
    'ご報告ありがとうございます。スタッフ配置の見直しを検討します。ピーク時は最低2名体制が必要ですね。',
    false,
    p.created_at + INTERVAL '2 hours',
    p.created_at + INTERVAL '2 hours'
FROM bbs_posts p
WHERE p.title = '接客態度に関するクレーム'
LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'A3',
    '私も同様の経験がありました。ピーク時の事前準備と、お客様への声かけを心がけています。',
    true,
    p.created_at + INTERVAL '5 hours',
    p.created_at + INTERVAL '5 hours'
FROM bbs_posts p
WHERE p.title = '接客態度に関するクレーム'
LIMIT 1;

-- 料理の美味しさについてのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'D3',
    '素晴らしいですね！レシピのコツを共有していただけると嬉しいです。',
    false,
    p.created_at + INTERVAL '3 hours',
    p.created_at + INTERVAL '3 hours'
FROM bbs_posts p
WHERE p.title = '料理の美味しさを褒められました'
LIMIT 1;

-- 動線改善案へのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'manager_003',
    '参考になります。当店でも同様の課題があるので、導入を検討してみます。',
    false,
    p.created_at + INTERVAL '1 day',
    p.created_at + INTERVAL '1 day'
FROM bbs_posts p
WHERE p.title = 'ピーク時の動線改善案'
LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'manager_004',
    '横浜店でも先月から試しています。お客様からの評判も良好です。',
    false,
    p.created_at + INTERVAL '2 days',
    p.created_at + INTERVAL '2 days'
FROM bbs_posts p
WHERE p.title = 'ピーク時の動線改善案'
LIMIT 1;

-- クレーム対応マニュアルへのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'manager_007',
    '明確なフローで分かりやすいです。新人研修でも活用させていただきます。',
    false,
    p.created_at + INTERVAL '6 hours',
    p.created_at + INTERVAL '6 hours'
FROM bbs_posts p
WHERE p.title = 'クレーム対応マニュアルの共有'
LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'staff_016',
    '④のフォローアップが特に大切だと思います。後日の確認連絡でリピーターになっていただけたケースもあります。',
    true,
    p.created_at + INTERVAL '1 day',
    p.created_at + INTERVAL '1 day'
FROM bbs_posts p
WHERE p.title = 'クレーム対応マニュアルの共有'
LIMIT 1;

-- 外国人観光客対応の質問へのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'A2',
    '渋谷店では指差しメニューを作成しています。写真付きで説明も英語・中国語・韓国語を併記しています。',
    false,
    p.created_at + INTERVAL '4 hours',
    p.created_at + INTERVAL '4 hours'
FROM bbs_posts p
WHERE p.title = '外国人観光客への対応について質問'
LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'B3',
    '新宿店では簡単な英語フレーズ集を作って、レジ横に置いています。「Would you like to sit here?」など基本的なものですが、役立っています。',
    true,
    p.created_at + INTERVAL '8 hours',
    p.created_at + INTERVAL '8 hours'
FROM bbs_posts p
WHERE p.title = '外国人観光客への対応について質問'
LIMIT 1;

-- 冬季の入口対策についてのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT
    p.post_id,
    'manager_009',
    '仙台店では滑り止めマットを二重に敷いて、さらに除雪用の塩も用意しています。',
    false,
    p.created_at + INTERVAL '3 hours',
    p.created_at + INTERVAL '3 hours'
FROM bbs_posts p
WHERE p.title = '冬季の入口対策について'
LIMIT 1;

-- ============================================================
-- 6-2. 追加コメントデータ（人気投稿に多くのコメント）
-- ============================================================

-- 年末年始の営業時間についてへのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_001', '渋谷店、了解しました。スタッフのシフトを調整します。', false, p.created_at + INTERVAL '2 hours', p.created_at + INTERVAL '2 hours'
FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_002', '新宿店も対応します。12/31は予約制にする予定です。', false, p.created_at + INTERVAL '4 hours', p.created_at + INTERVAL '4 hours'
FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_003', '池袋店も準備進めます。年始の予約も入り始めています。', false, p.created_at + INTERVAL '6 hours', p.created_at + INTERVAL '6 hours'
FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_005', '大阪店、了解です！年末は混雑が予想されるのでスタッフ増員します。', false, p.created_at + INTERVAL '8 hours', p.created_at + INTERVAL '8 hours'
FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_008', '福岡店も承知しました。観光客も多い時期なので万全の体制で臨みます。', false, p.created_at + INTERVAL '10 hours', p.created_at + INTERVAL '10 hours'
FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;

-- 新メニュー導入のお知らせへのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'A1', '試作してみましたが、とても美味しいです！お客様にも喜ばれそう。', false, p.created_at + INTERVAL '3 hours', p.created_at + INTERVAL '3 hours'
FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'B2', '原価計算表を確認しました。利益率も良さそうですね。', false, p.created_at + INTERVAL '5 hours', p.created_at + INTERVAL '5 hours'
FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_004', '横浜店でも準備開始します。食材の発注はいつからでしょうか？', false, p.created_at + INTERVAL '1 day', p.created_at + INTERVAL '1 day'
FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'honbu_mgr', '発注は来週月曜日からです。各店舗の在庫状況を確認の上、必要数をお知らせください。', true, p.created_at + INTERVAL '1 day' + INTERVAL '2 hours', p.created_at + INTERVAL '1 day' + INTERVAL '2 hours'
FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;

-- 衛生管理講習会についてのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_001', '前回の講習会も勉強になりました。今回も楽しみです。', false, p.created_at + INTERVAL '4 hours', p.created_at + INTERVAL '4 hours'
FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_006', '名古屋店は水曜日に実施予定です。全員参加で臨みます。', false, p.created_at + INTERVAL '6 hours', p.created_at + INTERVAL '6 hours'
FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_018', '資料の事前配布はありますか？予習しておきたいです。', false, p.created_at + INTERVAL '8 hours', p.created_at + INTERVAL '8 hours'
FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'admin', '資料は前日にメールで送付します。ご確認ください。', true, p.created_at + INTERVAL '10 hours', p.created_at + INTERVAL '10 hours'
FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;

-- 地域限定メニューの成功事例へのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_007', '名古屋店でも手羽先メニューが好調です！地域性を活かすのは大事ですね。', false, p.created_at + INTERVAL '3 hours', p.created_at + INTERVAL '3 hours'
FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_008', '福岡店ではもつ鍋が人気です。冬場は特に売れています。', false, p.created_at + INTERVAL '5 hours', p.created_at + INTERVAL '5 hours'
FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_020', '札幌店でも味噌ラーメンを検討中です。北海道らしさを出したいです。', false, p.created_at + INTERVAL '8 hours', p.created_at + INTERVAL '8 hours'
FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_022', '仙台店は牛タンで勝負中です！観光客にも地元の方にも好評です。', false, p.created_at + INTERVAL '1 day', p.created_at + INTERVAL '1 day'
FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'honbu_mgr', '各店舗の取り組み素晴らしいです。成功事例を本部でまとめて共有しますね。', true, p.created_at + INTERVAL '2 days', p.created_at + INTERVAL '2 days'
FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;

-- テイクアウト用パッケージの改善へのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'D3', 'どのメーカーの容器を使っていますか？うちも検討したいです。', false, p.created_at + INTERVAL '2 hours', p.created_at + INTERVAL '2 hours'
FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'C2', '○○製の保温容器を使っています。1個あたり20円アップですが、満足度向上を考えると価値ありです。', true, p.created_at + INTERVAL '4 hours', p.created_at + INTERVAL '4 hours'
FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_002', '新宿店でも導入を検討します。テイクアウト需要は増えているので投資する価値がありますね。', false, p.created_at + INTERVAL '6 hours', p.created_at + INTERVAL '6 hours'
FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;

-- 効果的なアップセルの方法へのコメント
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'A3', 'すぐに試してみます！シンプルだけど効果的ですね。', false, p.created_at + INTERVAL '1 hour', p.created_at + INTERVAL '1 hour'
FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_014', '大阪店でも実践中です。「今日のおすすめデザートは○○です」と具体的に言うとさらに効果的でした。', false, p.created_at + INTERVAL '3 hours', p.created_at + INTERVAL '3 hours'
FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_001', 'デザートだけでなくドリンクのアップセルも効果的です。「食後のコーヒーはいかがですか？」も試してみてください。', true, p.created_at + INTERVAL '5 hours', p.created_at + INTERVAL '5 hours'
FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_017', '名古屋店でも先週から実践開始。1週間でデザート売上が18%アップしました！', false, p.created_at + INTERVAL '1 day', p.created_at + INTERVAL '1 day'
FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

-- 外国人観光客への対応について質問へのコメント追加
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_007', 'Google翻訳のリアルタイム会話機能も便利ですよ。スマホを見せながら会話できます。', false, p.created_at + INTERVAL '10 hours', p.created_at + INTERVAL '10 hours'
FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'D1', '横浜店では「Welcome」「Thank you」などの基本フレーズを練習する時間を設けています。', false, p.created_at + INTERVAL '12 hours', p.created_at + INTERVAL '12 hours'
FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_019', '皆さんありがとうございます！指差しメニューとフレーズ集、両方導入してみます。', false, p.created_at + INTERVAL '1 day', p.created_at + INTERVAL '1 day'
FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;

-- 冬季の入口対策についてへのコメント追加
INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_021', '札幌店でも同じ対策しています。あと、入口に温風ヒーターを設置するのも効果的です。', false, p.created_at + INTERVAL '5 hours', p.created_at + INTERVAL '5 hours'
FROM bbs_posts p WHERE p.title = '冬季の入口対策について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'manager_008', '福岡はあまり雪が降りませんが、参考になります。寒い日の対策として活用できそう。', false, p.created_at + INTERVAL '8 hours', p.created_at + INTERVAL '8 hours'
FROM bbs_posts p WHERE p.title = '冬季の入口対策について' LIMIT 1;

INSERT INTO bbs_comments (post_id, user_id, content, is_best_answer, created_at, updated_at)
SELECT p.post_id, 'staff_020', 'アドバイスありがとうございます！滑り止めマットの二重敷き、早速試してみます。', false, p.created_at + INTERVAL '1 day', p.created_at + INTERVAL '1 day'
FROM bbs_posts p WHERE p.title = '冬季の入口対策について' LIMIT 1;

-- コメント数を更新
UPDATE bbs_posts SET comment_count = (
    SELECT COUNT(*) FROM bbs_comments WHERE bbs_comments.post_id = bbs_posts.post_id
);

-- シーケンスの更新
SELECT setval('bbs_comments_comment_id_seq', (SELECT MAX(comment_id) FROM bbs_comments));

-- ============================================================
-- 7. 掲示板リアクションデータ
-- ============================================================

-- いくつかの投稿にリアクションを追加
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_001', 'naruhodo', p.created_at + INTERVAL '1 hour'
FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'B1', 'iine', p.created_at + INTERVAL '2 hours'
FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_005', 'naruhodo', p.created_at + INTERVAL '3 hours'
FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C1', 'iine', p.created_at + INTERVAL '4 hours'
FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'D1', 'naruhodo', p.created_at + INTERVAL '5 hours'
FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_006', 'iine', p.created_at + INTERVAL '6 hours'
FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_018', 'naruhodo', p.created_at + INTERVAL '2 hours'
FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_008', 'iine', p.created_at + INTERVAL '4 hours'
FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

-- ============================================================
-- 7-2. 追加リアクションデータ（人気投稿に多くのリアクション）
-- ============================================================

-- 年末年始の営業時間について（重要なお知らせなので多くのいいね）
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_001', 'iine', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_002', 'iine', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_003', 'iine', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_004', 'iine', p.created_at + INTERVAL '4 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_005', 'iine', p.created_at + INTERVAL '5 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_006', 'iine', p.created_at + INTERVAL '6 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_007', 'iine', p.created_at + INTERVAL '7 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_008', 'iine', p.created_at + INTERVAL '8 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_009', 'iine', p.created_at + INTERVAL '9 hours' FROM bbs_posts p WHERE p.title = '年末年始の営業時間について' LIMIT 1;

-- 新メニュー導入のお知らせ
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_001', 'iine', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'A3', 'naruhodo', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C1', 'iine', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'D3', 'iine', p.created_at + INTERVAL '4 hours' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_018', 'naruhodo', p.created_at + INTERVAL '5 hours' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_001', 'iine', p.created_at + INTERVAL '6 hours' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_005', 'iine', p.created_at + INTERVAL '7 hours' FROM bbs_posts p WHERE p.title = '新メニュー導入のお知らせ' LIMIT 1;

-- 地域限定メニューの成功事例（参考になる投稿）
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_001', 'naruhodo', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_002', 'iine', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_003', 'naruhodo', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_004', 'iine', p.created_at + INTERVAL '4 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'A1', 'naruhodo', p.created_at + INTERVAL '5 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'B2', 'iine', p.created_at + INTERVAL '6 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C3', 'naruhodo', p.created_at + INTERVAL '7 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_016', 'iine', p.created_at + INTERVAL '8 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'honbu_mgr', 'iine', p.created_at + INTERVAL '9 hours' FROM bbs_posts p WHERE p.title = '地域限定メニューの成功事例' LIMIT 1;

-- テイクアウト用パッケージの改善
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_001', 'naruhodo', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'B1', 'iine', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_001', 'iine', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_005', 'naruhodo', p.created_at + INTERVAL '4 hours' FROM bbs_posts p WHERE p.title = 'テイクアウト用パッケージの改善' LIMIT 1;

-- 衛生管理講習会の実施について
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_001', 'iine', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_002', 'iine', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_003', 'iine', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'A1', 'iine', p.created_at + INTERVAL '4 hours' FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'B2', 'iine', p.created_at + INTERVAL '5 hours' FROM bbs_posts p WHERE p.title = '衛生管理講習会の実施について' LIMIT 1;

-- 外国人観光客への対応について質問
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_001', 'naruhodo', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'A3', 'iine', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C3', 'naruhodo', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_007', 'iine', p.created_at + INTERVAL '4 hours' FROM bbs_posts p WHERE p.title = '外国人観光客への対応について質問' LIMIT 1;

-- 冬季の入口対策について
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_021', 'naruhodo', p.created_at + INTERVAL '1 hour' FROM bbs_posts p WHERE p.title = '冬季の入口対策について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_008', 'iine', p.created_at + INTERVAL '2 hours' FROM bbs_posts p WHERE p.title = '冬季の入口対策について' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_009', 'naruhodo', p.created_at + INTERVAL '3 hours' FROM bbs_posts p WHERE p.title = '冬季の入口対策について' LIMIT 1;

-- ピーク時の動線改善案（追加リアクション）
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C2', 'iine', p.created_at + INTERVAL '5 hours' FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'D3', 'naruhodo', p.created_at + INTERVAL '6 hours' FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_006', 'iine', p.created_at + INTERVAL '7 hours' FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_017', 'naruhodo', p.created_at + INTERVAL '8 hours' FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_020', 'iine', p.created_at + INTERVAL '9 hours' FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;

-- クレーム対応マニュアルの共有（追加リアクション）
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_001', 'naruhodo', p.created_at + INTERVAL '7 hours' FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'A3', 'iine', p.created_at + INTERVAL '8 hours' FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C2', 'naruhodo', p.created_at + INTERVAL '9 hours' FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'D3', 'iine', p.created_at + INTERVAL '10 hours' FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_018', 'naruhodo', p.created_at + INTERVAL '11 hours' FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_001', 'iine', p.created_at + INTERVAL '12 hours' FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;

-- 効果的なアップセルの方法（追加リアクション）
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_001', 'iine', p.created_at + INTERVAL '5 hours' FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'B1', 'naruhodo', p.created_at + INTERVAL '6 hours' FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'C2', 'iine', p.created_at + INTERVAL '7 hours' FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_002', 'naruhodo', p.created_at + INTERVAL '8 hours' FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;
INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_005', 'iine', p.created_at + INTERVAL '9 hours' FROM bbs_posts p WHERE p.title = '効果的なアップセルの方法' LIMIT 1;

-- シーケンスの更新
SELECT setval('bbs_reactions_reaction_id_seq', (SELECT MAX(reaction_id) FROM bbs_reactions));

-- ============================================================
-- 8. 月次目標データ (3ヶ月分 × 9店舗)
-- ============================================================

-- 今月の目標
INSERT INTO monthly_goals (store_id, year, month, goal_text, achievement_rate, achievement_text, created_at, updated_at) VALUES
(2, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   'クレーム5件以下達成！
売上目標1400万円！
新規客獲得100名！', 72, '順調に推移中。クレームは現在3件、売上は目標の72%達成。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(3, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標1600万円達成！
顧客満足度95%以上！
スタッフ定着率100%！', 85, '好調！売上は目標を上回るペース。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(4, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標1200万円！
テイクアウト売上20%増！
違算ゼロ継続！', 68, 'テイクアウトが好調。売上はもう少し頑張りましょう。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(5, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標1300万円！
リピーター率30%達成！
食品ロス10%削減！', 78, 'リピーター施策が功を奏しています。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(6, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標1500万円！
地域限定メニュー売上20%！
接客評価4.5以上！', 82, '地域限定メニューが予想以上の人気です。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(7, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標1100万円！
新規顧客80名獲得！
SNSフォロワー500増！', 65, 'SNS施策を強化中。売上はもう少し。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(8, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標1000万円！
観光客売上30%達成！
Googleレビュー4.2以上！', 75, '観光シーズンで好調。レビュー対策強化中。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(9, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標900万円！
寒さ対策の顧客満足度90%！
スタッフ研修完了！', 60, '雪まつり前の準備期間。着実に進行中。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP),
(10, EXTRACT(YEAR FROM '2026-01-30'::DATE)::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE)::INTEGER,
   '売上目標800万円達成！
地域認知度向上！
オペレーション安定化！', 55, 'オープン間もないが順調なスタート。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '20 days', '2026-01-30 12:00:00'::TIMESTAMP);

-- 先月の目標
INSERT INTO monthly_goals (store_id, year, month, goal_text, achievement_rate, achievement_text, created_at, updated_at) VALUES
(2, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   'クレーム3件以下！
売上目標1350万円！
スタッフ満足度向上！', 95, '目標達成！クレームは2件に抑えられました。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(3, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1550万円！
新メニュー販売1000食！
事故ゼロ！', 100, '完全達成！新メニューは1200食販売。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(4, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1150万円！
客単価50円アップ！
在庫ロス削減！', 88, '客単価は達成。売上はあと少しでした。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(5, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1250万円！
ビジネス客獲得強化！
口コミ評価4.0以上！', 92, '好調な月でした。来月も継続します。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(6, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1450万円！
たこ焼きメニュー定着！
スタッフ研修完了！', 98, 'ほぼ完璧な達成率でした。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(7, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1050万円！
名物メニュー開発！
地域イベント参加！', 85, '名物メニューが好評。来月も期待。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(8, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標950万円！
多言語対応強化！
団体客対応力向上！', 90, '団体客対応がスムーズになりました。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day'),
(9, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '1 month')::INTEGER,
   '売上目標850万円！
冬季メニュー導入！
安全対策強化！', 82, '冬季メニューが好調なスタート。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '50 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '1 day');

-- 先々月の目標（参考データ）
INSERT INTO monthly_goals (store_id, year, month, goal_text, achievement_rate, achievement_text, created_at, updated_at) VALUES
(2, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '2 months')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '2 months')::INTEGER,
   'クレーム対応研修実施！
売上目標1300万円！
衛生管理強化！', 90, '研修完了、売上も好調でした。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '80 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '30 days'),
(3, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '2 months')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '2 months')::INTEGER,
   '売上目標1500万円！
接客コンテスト開催！
在庫管理改善！', 96, '接客コンテストが大成功でした。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '80 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '30 days'),
(6, EXTRACT(YEAR FROM '2026-01-30'::DATE - INTERVAL '2 months')::INTEGER, EXTRACT(MONTH FROM '2026-01-30'::DATE - INTERVAL '2 months')::INTEGER,
   '売上目標1400万円！
大阪らしさの追求！
スタッフ育成強化！', 94, '地域密着の取り組みが評価されました。', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '80 days', '2026-01-30 12:00:00'::TIMESTAMP - INTERVAL '30 days');

-- シーケンスの更新
SELECT setval('monthly_goals_goal_id_seq', (SELECT MAX(goal_id) FROM monthly_goals));

-- ============================================================
-- トランザクション完了
-- ============================================================
COMMIT;

-- ============================================================
-- 実行後の確認用クエリ
-- ============================================================
-- 以下のクエリでデータ件数を確認できます

-- SELECT '店舗' as table_name, COUNT(*) as count FROM stores
-- UNION ALL SELECT 'ユーザー', COUNT(*) FROM users
-- UNION ALL SELECT '店舗日次実績', COUNT(*) FROM store_daily_performances
-- UNION ALL SELECT '日報', COUNT(*) FROM daily_reports
-- UNION ALL SELECT '掲示板投稿', COUNT(*) FROM bbs_posts
-- UNION ALL SELECT '掲示板コメント', COUNT(*) FROM bbs_comments
-- UNION ALL SELECT '掲示板リアクション', COUNT(*) FROM bbs_reactions
-- UNION ALL SELECT '月次目標', COUNT(*) FROM monthly_goals;

-- ============================================================
-- 注意事項
-- ============================================================
-- 1. パスワードはデモ用です。本番運用前に必ず変更してください。
--    Djangoでパスワードを変更: python manage.py changepassword <user_id>
--
-- 2. ベクトルデータ（document_vectors, knowledge_vectors）は
--    このSQLでは生成されません。以下のコマンドで生成してください：
--    python manage.py vectorize_all
--
-- 3. 既存データがある場合は、事前にTRUNCATEしてください：
--    TRUNCATE stores, users, store_daily_performances, daily_reports,
--             bbs_posts, bbs_comments, bbs_reactions, monthly_goals
--             RESTART IDENTITY CASCADE;

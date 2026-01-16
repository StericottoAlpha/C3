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
(1, '本部', '東京都千代田区丸の内1-1-1 本社ビル5F', NULL, NOW() - INTERVAL '365 days'),
(2, '渋谷道玄坂店', '東京都渋谷区道玄坂2-3-1 渋谷ビル1F', NULL, NOW() - INTERVAL '300 days'),
(3, '新宿東口店', '東京都新宿区新宿3-25-10 新宿センタービル1F', NULL, NOW() - INTERVAL '280 days'),
(4, '池袋西口店', '東京都豊島区西池袋1-10-15 池袋駅前ビル1F', NULL, NOW() - INTERVAL '250 days'),
(5, '横浜駅前店', '神奈川県横浜市西区北幸1-1-1 横浜駅前ビル1F', NULL, NOW() - INTERVAL '200 days'),
(6, '大阪梅田店', '大阪府大阪市北区梅田1-3-1 大阪駅前第一ビル1F', NULL, NOW() - INTERVAL '180 days'),
(7, '名古屋栄店', '愛知県名古屋市中区栄3-5-1 栄センタービル1F', NULL, NOW() - INTERVAL '150 days'),
(8, '福岡天神店', '福岡県福岡市中央区天神2-5-1 天神センタービル1F', NULL, NOW() - INTERVAL '120 days'),
(9, '札幌駅前店', '北海道札幌市中央区北5条西3-1 札幌駅前ビル1F', NULL, NOW() - INTERVAL '90 days'),
(10, '仙台駅前店', '宮城県仙台市青葉区中央1-1-1 仙台駅前ビル1F', NULL, NOW() - INTERVAL '60 days');

-- シーケンスの更新
SELECT setval('stores_store_id_seq', 10);

-- ============================================================
-- 2. ユーザーデータ (管理者1名 + 各店舗に店長1名 + スタッフ2-4名 = 約40名)
-- ============================================================
-- パスワード: password123 (Django PBKDF2形式)
-- 本番運用時は必ず変更してください

INSERT INTO users (user_id, password, last_name, first_name, store_id, user_type, email, is_staff, is_superuser, is_active, created_at) VALUES
-- 本部 (管理者)
('admin', 'pbkdf2_sha256$600000$5r6PWGuN24MYvhL0UfGt12$m3bKRh9rFwgl9WCfDbotTcSpX+ANVc12yW7TIx2KGr4=', 'システム', '管理者', 1, 'admin', 'admin@example.com', true, true, true, NOW() - INTERVAL '365 days'),
('honbu_mgr', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '本部', '太郎', 1, 'manager', 'honbu_mgr@example.com', false, false, true, NOW() - INTERVAL '360 days'),

-- 渋谷道玄坂店
('manager_001', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '佐藤', '健一', 2, 'manager', 'shibuya_mgr@example.com', false, false, true, NOW() - INTERVAL '300 days'),
('staff_001', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '田中', '花子', 2, 'staff', 'shibuya_s01@example.com', false, false, true, NOW() - INTERVAL '290 days'),
('staff_002', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '高橋', '次郎', 2, 'staff', 'shibuya_s02@example.com', false, false, true, NOW() - INTERVAL '280 days'),
('staff_003', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '渡辺', '美咲', 2, 'staff', 'shibuya_s03@example.com', false, false, true, NOW() - INTERVAL '100 days'),

-- 新宿東口店
('manager_002', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '鈴木', '一郎', 3, 'manager', 'shinjuku_mgr@example.com', false, false, true, NOW() - INTERVAL '280 days'),
('staff_004', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '伊藤', '健太', 3, 'staff', 'shinjuku_s01@example.com', false, false, true, NOW() - INTERVAL '270 days'),
('staff_005', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '山本', '由美', 3, 'staff', 'shinjuku_s02@example.com', false, false, true, NOW() - INTERVAL '260 days'),
('staff_006', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '中村', '大輔', 3, 'staff', 'shinjuku_s03@example.com', false, false, true, NOW() - INTERVAL '150 days'),
('staff_007', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '小林', 'さくら', 3, 'staff', 'shinjuku_s04@example.com', false, false, true, NOW() - INTERVAL '50 days'),

-- 池袋西口店
('manager_003', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '加藤', '誠', 4, 'manager', 'ikebukuro_mgr@example.com', false, false, true, NOW() - INTERVAL '250 days'),
('staff_008', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '吉田', '愛', 4, 'staff', 'ikebukuro_s01@example.com', false, false, true, NOW() - INTERVAL '240 days'),
('staff_009', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '山田', '翔太', 4, 'staff', 'ikebukuro_s02@example.com', false, false, true, NOW() - INTERVAL '200 days'),

-- 横浜駅前店
('manager_004', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '松本', '浩二', 5, 'manager', 'yokohama_mgr@example.com', false, false, true, NOW() - INTERVAL '200 days'),
('staff_010', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '井上', '千尋', 5, 'staff', 'yokohama_s01@example.com', false, false, true, NOW() - INTERVAL '190 days'),
('staff_011', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '木村', '雄一', 5, 'staff', 'yokohama_s02@example.com', false, false, true, NOW() - INTERVAL '180 days'),
('staff_012', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '林', '真理子', 5, 'staff', 'yokohama_s03@example.com', false, false, true, NOW() - INTERVAL '80 days'),

-- 大阪梅田店
('manager_005', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '清水', '大輔', 6, 'manager', 'osaka_mgr@example.com', false, false, true, NOW() - INTERVAL '180 days'),
('staff_013', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '坂本', '恵', 6, 'staff', 'osaka_s01@example.com', false, false, true, NOW() - INTERVAL '170 days'),
('staff_014', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '藤田', '健', 6, 'staff', 'osaka_s02@example.com', false, false, true, NOW() - INTERVAL '160 days'),
('staff_015', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '橋本', 'めぐみ', 6, 'staff', 'osaka_s03@example.com', false, false, true, NOW() - INTERVAL '60 days'),

-- 名古屋栄店
('manager_006', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '前田', '直人', 7, 'manager', 'nagoya_mgr@example.com', false, false, true, NOW() - INTERVAL '150 days'),
('staff_016', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '石井', '陽子', 7, 'staff', 'nagoya_s01@example.com', false, false, true, NOW() - INTERVAL '140 days'),
('staff_017', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '阿部', '光', 7, 'staff', 'nagoya_s02@example.com', false, false, true, NOW() - INTERVAL '130 days'),

-- 福岡天神店
('manager_007', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '森', '康平', 8, 'manager', 'fukuoka_mgr@example.com', false, false, true, NOW() - INTERVAL '120 days'),
('staff_018', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '池田', '明日香', 8, 'staff', 'fukuoka_s01@example.com', false, false, true, NOW() - INTERVAL '110 days'),
('staff_019', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '原田', '拓也', 8, 'staff', 'fukuoka_s02@example.com', false, false, true, NOW() - INTERVAL '100 days'),

-- 札幌駅前店
('manager_008', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '村上', '隆', 9, 'manager', 'sapporo_mgr@example.com', false, false, true, NOW() - INTERVAL '90 days'),
('staff_020', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '近藤', '由紀', 9, 'staff', 'sapporo_s01@example.com', false, false, true, NOW() - INTERVAL '80 days'),
('staff_021', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '斎藤', '勇気', 9, 'staff', 'sapporo_s02@example.com', false, false, true, NOW() - INTERVAL '70 days'),

-- 仙台駅前店
('manager_009', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '遠藤', '正樹', 10, 'manager', 'sendai_mgr@example.com', false, false, true, NOW() - INTERVAL '60 days'),
('staff_022', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '藤原', '優花', 10, 'staff', 'sendai_s01@example.com', false, false, true, NOW() - INTERVAL '50 days'),
('staff_023', 'pbkdf2_sha256$600000$iDOXwH3QX1DHdEW5exHX6Q$sMcKlsSDn5IiEKrRaQfPQFpeUDbedZBjHB2rAA3/1T4=', '岡田', '達也', 10, 'staff', 'sendai_s02@example.com', false, false, true, NOW() - INTERVAL '40 days');

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

INSERT INTO store_daily_performances (store_id, date, sales_amount, customer_count, cash_difference, registered_by_id, created_at, updated_at)
SELECT
    s.store_id,
    d.date,
    -- 売上金額: 店舗ごとの基準値 + 曜日変動 + ランダム変動
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
    + CASE EXTRACT(DOW FROM d.date)
        WHEN 0 THEN 80000   -- 日曜
        WHEN 6 THEN 100000  -- 土曜
        WHEN 5 THEN 50000   -- 金曜
        ELSE 0
      END
    + (RANDOM() * 60000 - 30000)::INTEGER as sales_amount,

    -- 客数
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
    + CASE EXTRACT(DOW FROM d.date)
        WHEN 0 THEN 40
        WHEN 6 THEN 50
        WHEN 5 THEN 25
        ELSE 0
      END
    + (RANDOM() * 30 - 15)::INTEGER as customer_count,

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
    generate_series(CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '1 day', '1 day'::INTERVAL) as d(date)
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
(2, 'staff_001', CURRENT_DATE - INTERVAL '1 day', 'claim', 'hall', '接客態度に関するクレーム', 'お客様から「スタッフの対応が遅い」とのご指摘をいただきました。ピーク時の対応について改善が必要です。レジ待ち時間が10分以上かかり、お客様を不快にさせてしまいました。今後はピーク時間帯のスタッフ配置を見直します。', true, CURRENT_DATE - INTERVAL '1 day' + TIME '14:30:00'),
(2, 'staff_002', CURRENT_DATE - INTERVAL '5 days', 'claim', 'kitchen', '料理提供の遅延について', 'ランチタイムに注文から提供まで25分かかってしまいました。お客様から「遅すぎる」とお叱りを受けました。キッチンとホールの連携を改善する必要があります。注文票の確認フローを見直しました。', true, CURRENT_DATE - INTERVAL '5 days' + TIME '15:00:00'),
(2, 'staff_003', CURRENT_DATE - INTERVAL '12 days', 'claim', 'hall', '予約確認ミス', 'お客様の予約が入っていなかったため、お待たせしてしまいました。電話予約時の復唱確認を徹底します。幸い空席があり対応できましたが、今後は予約システムへの入力を即時行うようにします。', true, CURRENT_DATE - INTERVAL '12 days' + TIME '19:00:00'),
(2, 'staff_001', CURRENT_DATE - INTERVAL '20 days', 'claim', 'cashier', 'お会計ミス', 'お会計時に金額を間違えてしまい、お客様にご指摘を受けました。確認不足でした。複数商品のある場合は必ず合計金額を読み上げて確認することを徹底します。', true, CURRENT_DATE - INTERVAL '20 days' + TIME '20:30:00'),

-- 賞賛系
(2, 'staff_002', CURRENT_DATE - INTERVAL '2 days', 'praise', 'kitchen', '料理の美味しさを褒められました', 'お客様から「今日のハンバーグは特に美味しかった」と直接お褒めの言葉をいただきました。シェフの丁寧な調理が評価されています。秘訣は肉の練り方にあるとのことでした。', true, CURRENT_DATE - INTERVAL '2 days' + TIME '13:00:00'),
(2, 'staff_001', CURRENT_DATE - INTERVAL '8 days', 'praise', 'hall', '子連れ対応を褒められました', '小さなお子様連れのお客様から「スタッフの気配りが素晴らしかった」とお褒めの言葉をいただきました。子供用の食器やクレヨンを用意したことが好評でした。他店舗でも参考になればと思います。', true, CURRENT_DATE - INTERVAL '8 days' + TIME '16:00:00'),
(2, 'staff_003', CURRENT_DATE - INTERVAL '15 days', 'praise', 'hall', '外国人観光客への対応', '英語での注文対応がスムーズにできたと、海外からのお客様から感謝されました。翻訳アプリと指差しメニューの併用が効果的でした。', true, CURRENT_DATE - INTERVAL '15 days' + TIME '17:30:00'),
(2, 'staff_002', CURRENT_DATE - INTERVAL '25 days', 'praise', 'kitchen', '季節限定メニューが好評', '新しく始めた冬季限定のシチューが大変好評です。1日平均30食以上出ています。常連のお客様から「来年も楽しみにしている」とのお声もいただきました。', true, CURRENT_DATE - INTERVAL '25 days' + TIME '14:00:00'),

-- 事故・トラブル系
(2, 'manager_001', CURRENT_DATE - INTERVAL '7 days', 'accident', 'kitchen', '厨房機器の故障', 'オーブンの温度が上がらなくなり、業者を呼んで修理しました。ヒーター部品の交換で復旧。修理費用は35,000円。予防保全の重要性を再認識しました。', true, CURRENT_DATE - INTERVAL '7 days' + TIME '11:00:00'),
(2, 'staff_001', CURRENT_DATE - INTERVAL '18 days', 'accident', 'hall', 'お客様の転倒事故', '雨の日に入口で足を滑らせたお客様がいらっしゃいました。幸い怪我はありませんでしたが、マットを追加設置しました。雨天時の床の状態確認を強化します。', true, CURRENT_DATE - INTERVAL '18 days' + TIME '12:30:00'),

-- 報告・その他
(2, 'manager_001', CURRENT_DATE - INTERVAL '3 days', 'report', 'other', '売上報告：過去最高記録', '本日の売上が62万円を記録し、オープン以来最高となりました。週末の天候に恵まれたことと、SNSでの口コミ効果があったようです。', true, CURRENT_DATE - INTERVAL '3 days' + TIME '22:00:00'),
(2, 'manager_001', CURRENT_DATE - INTERVAL '10 days', 'report', 'other', '新人スタッフの研修完了', '新人の渡辺さんが基本研修を完了しました。接客、レジ操作、基本的な調理補助まで一通りできるようになりました。来週から通常シフトに入る予定です。', true, CURRENT_DATE - INTERVAL '10 days' + TIME '21:00:00'),
(2, 'staff_002', CURRENT_DATE - INTERVAL '22 days', 'report', 'kitchen', '食材の在庫管理改善', '発注システムを見直し、廃棄ロスを先月比20%削減できました。特に野菜類の鮮度管理が改善されました。', false, CURRENT_DATE - INTERVAL '22 days' + TIME '17:00:00'),

-- 新宿東口店の日報
(3, 'staff_004', CURRENT_DATE - INTERVAL '1 day', 'claim', 'hall', '待ち時間に関するクレーム', '満席時の待ち時間が長く、お客様からご不満の声をいただきました。待合スペースでのドリンクサービスを開始することを検討しています。', true, CURRENT_DATE - INTERVAL '1 day' + TIME '20:00:00'),
(3, 'staff_005', CURRENT_DATE - INTERVAL '4 days', 'praise', 'hall', 'リピーター様からの感謝', '週に3回来店される常連のお客様から「いつも気持ちよく食事ができる」とのお言葉をいただきました。スタッフ一同励みになります。', true, CURRENT_DATE - INTERVAL '4 days' + TIME '15:00:00'),
(3, 'staff_006', CURRENT_DATE - INTERVAL '6 days', 'accident', 'kitchen', '軽い火傷事故', '調理中にスタッフが軽い火傷をしました。すぐに冷水で冷やし、応急処置を行いました。幸い軽傷で済みましたが、防護具の着用を再徹底します。', true, CURRENT_DATE - INTERVAL '6 days' + TIME '13:30:00'),
(3, 'manager_002', CURRENT_DATE - INTERVAL '9 days', 'report', 'other', '月間売上目標達成', '今月の売上目標を3日前倒しで達成しました。新メニューの販促キャンペーンが好調でした。来月はさらに5%増を目指します。', true, CURRENT_DATE - INTERVAL '9 days' + TIME '22:00:00'),
(3, 'staff_004', CURRENT_DATE - INTERVAL '14 days', 'claim', 'cashier', 'クーポン適用ミス', 'クーポンの適用を忘れてしまい、お客様に再度レジ打ちをお願いしてしまいました。クーポン確認の声かけを習慣化します。', true, CURRENT_DATE - INTERVAL '14 days' + TIME '19:30:00'),
(3, 'staff_007', CURRENT_DATE - INTERVAL '17 days', 'praise', 'hall', 'アレルギー対応への感謝', 'アレルギーをお持ちのお客様に丁寧に対応したところ、大変感謝されました。アレルギー表を確認しながらの説明が安心感につながったようです。', true, CURRENT_DATE - INTERVAL '17 days' + TIME '13:00:00'),
(3, 'staff_005', CURRENT_DATE - INTERVAL '21 days', 'report', 'kitchen', 'メニュー改善の提案', '人気メニューのカレーライスについて、ルーの量を少し増やす提案をさせていただきます。お客様からの「もう少しルーが欲しい」という声が多いためです。', true, CURRENT_DATE - INTERVAL '21 days' + TIME '16:00:00'),

-- 池袋西口店の日報
(4, 'staff_008', CURRENT_DATE - INTERVAL '2 days', 'claim', 'toilet', 'トイレ清掃の指摘', 'お客様からトイレが汚れているとのご指摘を受けました。清掃頻度を30分から20分間隔に変更しました。', true, CURRENT_DATE - INTERVAL '2 days' + TIME '16:00:00'),
(4, 'staff_009', CURRENT_DATE - INTERVAL '5 days', 'praise', 'hall', '誕生日サプライズが好評', 'お客様の誕生日祝いでデザートプレートをサービスしたところ、大変喜んでいただけました。SNSにも投稿していただけるとのことです。', true, CURRENT_DATE - INTERVAL '5 days' + TIME '20:00:00'),
(4, 'manager_003', CURRENT_DATE - INTERVAL '8 days', 'accident', 'hall', '空調設備の故障', '店内の空調が効かなくなりました。お客様にはご不便をおかけしましたが、扇風機で応急対応し、翌日修理完了しました。', true, CURRENT_DATE - INTERVAL '8 days' + TIME '14:00:00'),
(4, 'staff_008', CURRENT_DATE - INTERVAL '13 days', 'report', 'other', 'テイクアウト需要増加', '最近テイクアウトの注文が増えています。専用の受け渡し窓口の設置を検討してはいかがでしょうか。', true, CURRENT_DATE - INTERVAL '13 days' + TIME '18:00:00'),
(4, 'staff_009', CURRENT_DATE - INTERVAL '19 days', 'claim', 'kitchen', '料理の温度が低い', 'お客様から「スープがぬるい」とご指摘を受けました。提供前の温度確認を徹底します。', true, CURRENT_DATE - INTERVAL '19 days' + TIME '12:30:00'),

-- 横浜駅前店の日報
(5, 'staff_010', CURRENT_DATE - INTERVAL '1 day', 'praise', 'hall', '接客対応を褒められました', 'お客様アンケートで「スタッフの笑顔が素晴らしい」と高評価をいただきました。日頃の接客研修の成果が出ています。', true, CURRENT_DATE - INTERVAL '1 day' + TIME '21:00:00'),
(5, 'staff_011', CURRENT_DATE - INTERVAL '3 days', 'claim', 'hall', '予約時間のズレ', '予約システムの時間設定にずれがあり、お客様をお待たせしてしまいました。システムの時刻同期を確認しました。', true, CURRENT_DATE - INTERVAL '3 days' + TIME '19:00:00'),
(5, 'staff_012', CURRENT_DATE - INTERVAL '7 days', 'accident', 'kitchen', '食器破損', 'お皿を3枚割ってしまいました。運搬時の持ち方を再確認しました。けが人はいません。', false, CURRENT_DATE - INTERVAL '7 days' + TIME '11:00:00'),
(5, 'manager_004', CURRENT_DATE - INTERVAL '11 days', 'report', 'other', '近隣店舗との連携', '隣接するショッピングモールのイベントと連動したキャンペーンを実施し、新規客が20%増加しました。', true, CURRENT_DATE - INTERVAL '11 days' + TIME '22:00:00'),
(5, 'staff_010', CURRENT_DATE - INTERVAL '16 days', 'praise', 'kitchen', 'ランチセットが好評', '新しく始めたビジネスランチセットが好評です。周辺オフィスからのリピーターが増えています。', true, CURRENT_DATE - INTERVAL '16 days' + TIME '14:30:00'),
(5, 'staff_011', CURRENT_DATE - INTERVAL '23 days', 'claim', 'cashier', 'ポイントカードの読み取りエラー', 'ポイントカードの読み取り機が不調で、手動入力での対応となりました。機器のメンテナンスを依頼しました。', true, CURRENT_DATE - INTERVAL '23 days' + TIME '17:00:00'),

-- 大阪梅田店の日報
(6, 'staff_013', CURRENT_DATE - INTERVAL '1 day', 'claim', 'hall', '注文間違い', 'オーダー取り違えがあり、お客様にご迷惑をおかけしました。注文確認の復唱を徹底します。', true, CURRENT_DATE - INTERVAL '1 day' + TIME '13:00:00'),
(6, 'staff_014', CURRENT_DATE - INTERVAL '4 days', 'praise', 'hall', '関西弁での接客が好評', '地元のお客様から「親しみやすい接客」と好評をいただきました。土地柄に合わせた接客スタイルが功を奏しています。', true, CURRENT_DATE - INTERVAL '4 days' + TIME '15:30:00'),
(6, 'staff_015', CURRENT_DATE - INTERVAL '8 days', 'accident', 'kitchen', '冷蔵庫の温度異常', '冷蔵庫の温度が8度まで上昇していることを発見。食材の確認を行い、修理業者を手配しました。', true, CURRENT_DATE - INTERVAL '8 days' + TIME '09:00:00'),
(6, 'manager_005', CURRENT_DATE - INTERVAL '12 days', 'report', 'other', '新メニュー導入結果', '大阪限定のたこ焼き風メニューが予想以上の人気です。月間売上の15%を占めるようになりました。', true, CURRENT_DATE - INTERVAL '12 days' + TIME '21:30:00'),
(6, 'staff_013', CURRENT_DATE - INTERVAL '18 days', 'praise', 'hall', 'グループ客への対応', '大人数のグループ客への対応がスムーズにでき、感謝されました。事前の席配置計画が効果的でした。', true, CURRENT_DATE - INTERVAL '18 days' + TIME '20:00:00'),
(6, 'staff_014', CURRENT_DATE - INTERVAL '24 days', 'claim', 'toilet', 'トイレットペーパー切れ', 'トイレットペーパーの補充が間に合わず、お客様にご不便をおかけしました。在庫チェックの頻度を増やします。', false, CURRENT_DATE - INTERVAL '24 days' + TIME '16:00:00'),

-- 名古屋栄店の日報
(7, 'staff_016', CURRENT_DATE - INTERVAL '2 days', 'praise', 'kitchen', '手羽先メニューが人気', '名古屋らしい手羽先の新メニューが大人気です。週末は品切れになることもあるほどです。仕込み量を増やす検討をしています。', true, CURRENT_DATE - INTERVAL '2 days' + TIME '14:00:00'),
(7, 'staff_017', CURRENT_DATE - INTERVAL '6 days', 'claim', 'hall', '席の案内ミス', 'お客様を間違った席にご案内してしまいました。座席番号の確認を徹底します。', true, CURRENT_DATE - INTERVAL '6 days' + TIME '18:30:00'),
(7, 'manager_006', CURRENT_DATE - INTERVAL '10 days', 'report', 'other', 'スタッフミーティング実施', '月例のスタッフミーティングを実施しました。接客品質向上に向けた意見交換ができました。', true, CURRENT_DATE - INTERVAL '10 days' + TIME '22:30:00'),
(7, 'staff_016', CURRENT_DATE - INTERVAL '15 days', 'accident', 'hall', 'ドリンクこぼし', 'お客様にドリンクをこぼしてしまいました。クリーニング代をお支払いし、お詫びしました。トレー使用を徹底します。', true, CURRENT_DATE - INTERVAL '15 days' + TIME '19:00:00'),
(7, 'staff_017', CURRENT_DATE - INTERVAL '20 days', 'praise', 'hall', '常連様への記念サービス', '100回目のご来店の常連様に特別サービスを行い、大変喜んでいただけました。', true, CURRENT_DATE - INTERVAL '20 days' + TIME '20:30:00'),

-- 福岡天神店の日報
(8, 'staff_018', CURRENT_DATE - INTERVAL '1 day', 'praise', 'hall', 'もつ鍋が大好評', '冬季限定のもつ鍋が大変好評です。博多らしさを出せているとのお声をいただきました。', true, CURRENT_DATE - INTERVAL '1 day' + TIME '21:00:00'),
(8, 'staff_019', CURRENT_DATE - INTERVAL '5 days', 'claim', 'kitchen', '辛さの調整ミス', '激辛メニューの辛さが強すぎるとのご指摘がありました。レシピの分量を再確認しました。', true, CURRENT_DATE - INTERVAL '5 days' + TIME '14:00:00'),
(8, 'manager_007', CURRENT_DATE - INTERVAL '9 days', 'report', 'other', '観光シーズンの売上増', '修学旅行シーズンで客数が増加しています。団体客への対応マニュアルを整備しました。', true, CURRENT_DATE - INTERVAL '9 days' + TIME '22:00:00'),
(8, 'staff_018', CURRENT_DATE - INTERVAL '14 days', 'accident', 'hall', 'メニュー表の破損', 'メニュー表が汚れて読みにくくなっていたため、新しいものに交換しました。定期交換のスケジュールを設定します。', false, CURRENT_DATE - INTERVAL '14 days' + TIME '10:00:00'),
(8, 'staff_019', CURRENT_DATE - INTERVAL '19 days', 'praise', 'hall', 'インバウンド対応', '韓国からの観光客に英語と身振りで丁寧に対応したところ、大変喜ばれました。多言語メニューの効果を実感しました。', true, CURRENT_DATE - INTERVAL '19 days' + TIME '16:00:00'),

-- 札幌駅前店の日報
(9, 'staff_020', CURRENT_DATE - INTERVAL '2 days', 'praise', 'kitchen', '味噌ラーメンが好評', '北海道らしい味噌ラーメンが観光客に好評です。「本場の味」とSNSでも拡散されています。', true, CURRENT_DATE - INTERVAL '2 days' + TIME '15:00:00'),
(9, 'staff_021', CURRENT_DATE - INTERVAL '6 days', 'claim', 'hall', '暖房の効きが悪い', '窓際の席が寒いとのご指摘を受けました。追加の暖房器具を設置しました。', true, CURRENT_DATE - INTERVAL '6 days' + TIME '13:00:00'),
(9, 'manager_008', CURRENT_DATE - INTERVAL '11 days', 'report', 'other', '雪まつり期間の対策', '来月の雪まつり期間に向けて、スタッフのシフト強化と仕込み量の増加を計画しています。', true, CURRENT_DATE - INTERVAL '11 days' + TIME '21:00:00'),
(9, 'staff_020', CURRENT_DATE - INTERVAL '16 days', 'accident', 'other', '除雪作業中の怪我', '店舗前の除雪作業中にスタッフが転倒しました。幸い軽傷でしたが、安全靴の着用を義務化しました。', true, CURRENT_DATE - INTERVAL '16 days' + TIME '08:30:00'),
(9, 'staff_021', CURRENT_DATE - INTERVAL '22 days', 'praise', 'hall', '地元食材のPR', '地元の農家から仕入れた野菜を使ったサラダが好評です。お客様から「新鮮で美味しい」とお褒めいただきました。', true, CURRENT_DATE - INTERVAL '22 days' + TIME '14:30:00'),

-- 仙台駅前店の日報
(10, 'staff_022', CURRENT_DATE - INTERVAL '1 day', 'praise', 'kitchen', '牛タン定食が人気', '仙台名物の牛タン定食が連日完売しています。仕入れ量を増やす方向で調整中です。', true, CURRENT_DATE - INTERVAL '1 day' + TIME '20:00:00'),
(10, 'staff_023', CURRENT_DATE - INTERVAL '4 days', 'claim', 'cashier', 'お釣りの間違い', 'お釣りの金額を間違えてしまいました。確認の声出しを徹底します。', true, CURRENT_DATE - INTERVAL '4 days' + TIME '17:00:00'),
(10, 'manager_009', CURRENT_DATE - INTERVAL '8 days', 'report', 'other', 'オープン2ヶ月の振り返り', '開店から2ヶ月が経過しました。売上は計画比95%とほぼ順調です。認知度向上に向けた地域イベントへの参加を検討しています。', true, CURRENT_DATE - INTERVAL '8 days' + TIME '22:00:00'),
(10, 'staff_022', CURRENT_DATE - INTERVAL '13 days', 'accident', 'kitchen', 'ガス漏れ検知器の誤作動', 'ガス漏れ検知器が誤作動しました。点検の結果、センサーの故障と判明し交換しました。', true, CURRENT_DATE - INTERVAL '13 days' + TIME '11:00:00'),
(10, 'staff_023', CURRENT_DATE - INTERVAL '18 days', 'praise', 'hall', '家族連れへの対応', '小さなお子様連れのご家族に子供用イスとおもちゃを用意したところ、とても喜んでいただけました。', true, CURRENT_DATE - INTERVAL '18 days' + TIME '15:00:00');

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
(1, 'admin', NULL, 'report', '年末年始の営業時間について', '年末年始の営業時間は以下の通りです。12/31は18時まで、1/1は休業、1/2から通常営業となります。各店舗での対応をお願いします。', 0, CURRENT_DATE - INTERVAL '30 days' + TIME '10:00:00', CURRENT_DATE - INTERVAL '30 days' + TIME '10:00:00'),
(1, 'honbu_mgr', NULL, 'report', '新メニュー導入のお知らせ', '来月より全店舗で新メニュー「季節の彩りプレート」を導入します。レシピと原価計算表は別途メールで送付しますので、準備をお願いします。', 0, CURRENT_DATE - INTERVAL '25 days' + TIME '11:00:00', CURRENT_DATE - INTERVAL '25 days' + TIME '11:00:00'),
(1, 'admin', NULL, 'report', '衛生管理講習会の実施について', '来週、各店舗で衛生管理講習会を実施します。全スタッフ必須参加です。日程は店長に確認してください。', 0, CURRENT_DATE - INTERVAL '20 days' + TIME '14:00:00', CURRENT_DATE - INTERVAL '20 days' + TIME '14:00:00'),

-- 各店舗からの情報共有
(2, 'manager_001', NULL, 'report', 'ピーク時の動線改善案', 'ランチタイムの混雑緩和のため、テーブルレイアウトを変更しました。入口から奥に向かう一方通行の動線を作ることで、お客様の流れがスムーズになりました。他店舗でも参考にしてください。', 0, CURRENT_DATE - INTERVAL '15 days' + TIME '21:00:00', CURRENT_DATE - INTERVAL '15 days' + TIME '21:00:00'),
(3, 'manager_002', NULL, 'report', 'クレーム対応マニュアルの共有', 'クレーム対応の基本フローをまとめました。①まず謝罪 ②状況を確認 ③解決策を提示 ④フォローアップ。この流れを守ることで、多くの場合円満に解決できています。', 0, CURRENT_DATE - INTERVAL '12 days' + TIME '20:00:00', CURRENT_DATE - INTERVAL '12 days' + TIME '20:00:00'),
(6, 'manager_005', NULL, 'report', '地域限定メニューの成功事例', '大阪限定のたこ焼き風メニューが好調です。地域特性を活かしたメニュー開発の重要性を実感しました。他店舗でも地域限定メニューを検討してみてはいかがでしょうか。', 0, CURRENT_DATE - INTERVAL '10 days' + TIME '22:00:00', CURRENT_DATE - INTERVAL '10 days' + TIME '22:00:00'),

-- ベストプラクティスの共有
(5, 'staff_010', NULL, 'praise', '効果的なアップセルの方法', 'お会計時に「本日のデザートはいかがですか」と一言添えるだけで、デザート注文率が15%向上しました。シンプルですが効果的です。', 0, CURRENT_DATE - INTERVAL '8 days' + TIME '19:00:00', CURRENT_DATE - INTERVAL '8 days' + TIME '19:00:00'),
(4, 'staff_009', NULL, 'report', 'テイクアウト用パッケージの改善', 'テイクアウト用の容器を保温性の高いものに変更したところ、お客様から「帰宅後も温かかった」と好評です。少しコストは上がりますが、満足度向上に効果があります。', 0, CURRENT_DATE - INTERVAL '5 days' + TIME '17:00:00', CURRENT_DATE - INTERVAL '5 days' + TIME '17:00:00'),

-- 質問・相談
(8, 'staff_019', NULL, 'other', '外国人観光客への対応について質問', '最近、海外からのお客様が増えています。翻訳アプリ以外に効果的な対応方法があれば教えてください。', 0, CURRENT_DATE - INTERVAL '3 days' + TIME '16:00:00', CURRENT_DATE - INTERVAL '3 days' + TIME '16:00:00'),
(9, 'staff_020', NULL, 'other', '冬季の入口対策について', '雪や氷で入口が滑りやすくなっています。他の北国店舗ではどのような対策をしていますか？', 0, CURRENT_DATE - INTERVAL '2 days' + TIME '15:00:00', CURRENT_DATE - INTERVAL '2 days' + TIME '15:00:00');

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
    'staff_004',
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
    'staff_013',
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
    'staff_003',
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
    'staff_007',
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
SELECT p.post_id, 'staff_005', 'iine', p.created_at + INTERVAL '2 hours'
FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'manager_005', 'naruhodo', p.created_at + INTERVAL '3 hours'
FROM bbs_posts p WHERE p.title = 'ピーク時の動線改善案' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_008', 'iine', p.created_at + INTERVAL '4 hours'
FROM bbs_posts p WHERE p.title = 'クレーム対応マニュアルの共有' LIMIT 1;

INSERT INTO bbs_reactions (post_id, user_id, reaction_type, created_at)
SELECT p.post_id, 'staff_011', 'naruhodo', p.created_at + INTERVAL '5 hours'
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

-- シーケンスの更新
SELECT setval('bbs_reactions_reaction_id_seq', (SELECT MAX(reaction_id) FROM bbs_reactions));

-- ============================================================
-- 8. 月次目標データ (3ヶ月分 × 9店舗)
-- ============================================================

-- 今月の目標
INSERT INTO monthly_goals (store_id, year, month, goal_text, achievement_rate, achievement_text, created_at, updated_at) VALUES
(2, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   'クレーム5件以下達成！
売上目標1400万円！
新規客獲得100名！', 72, '順調に推移中。クレームは現在3件、売上は目標の72%達成。', NOW() - INTERVAL '20 days', NOW()),
(3, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標1600万円達成！
顧客満足度95%以上！
スタッフ定着率100%！', 85, '好調！売上は目標を上回るペース。', NOW() - INTERVAL '20 days', NOW()),
(4, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標1200万円！
テイクアウト売上20%増！
違算ゼロ継続！', 68, 'テイクアウトが好調。売上はもう少し頑張りましょう。', NOW() - INTERVAL '20 days', NOW()),
(5, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標1300万円！
リピーター率30%達成！
食品ロス10%削減！', 78, 'リピーター施策が功を奏しています。', NOW() - INTERVAL '20 days', NOW()),
(6, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標1500万円！
地域限定メニュー売上20%！
接客評価4.5以上！', 82, '地域限定メニューが予想以上の人気です。', NOW() - INTERVAL '20 days', NOW()),
(7, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標1100万円！
新規顧客80名獲得！
SNSフォロワー500増！', 65, 'SNS施策を強化中。売上はもう少し。', NOW() - INTERVAL '20 days', NOW()),
(8, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標1000万円！
観光客売上30%達成！
Googleレビュー4.2以上！', 75, '観光シーズンで好調。レビュー対策強化中。', NOW() - INTERVAL '20 days', NOW()),
(9, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標900万円！
寒さ対策の顧客満足度90%！
スタッフ研修完了！', 60, '雪まつり前の準備期間。着実に進行中。', NOW() - INTERVAL '20 days', NOW()),
(10, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
   '売上目標800万円達成！
地域認知度向上！
オペレーション安定化！', 55, 'オープン間もないが順調なスタート。', NOW() - INTERVAL '20 days', NOW());

-- 先月の目標
INSERT INTO monthly_goals (store_id, year, month, goal_text, achievement_rate, achievement_text, created_at, updated_at) VALUES
(2, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   'クレーム3件以下！
売上目標1350万円！
スタッフ満足度向上！', 95, '目標達成！クレームは2件に抑えられました。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(3, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1550万円！
新メニュー販売1000食！
事故ゼロ！', 100, '完全達成！新メニューは1200食販売。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(4, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1150万円！
客単価50円アップ！
在庫ロス削減！', 88, '客単価は達成。売上はあと少しでした。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(5, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1250万円！
ビジネス客獲得強化！
口コミ評価4.0以上！', 92, '好調な月でした。来月も継続します。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(6, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1450万円！
たこ焼きメニュー定着！
スタッフ研修完了！', 98, 'ほぼ完璧な達成率でした。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(7, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標1050万円！
名物メニュー開発！
地域イベント参加！', 85, '名物メニューが好評。来月も期待。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(8, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標950万円！
多言語対応強化！
団体客対応力向上！', 90, '団体客対応がスムーズになりました。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day'),
(9, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER,
   '売上目標850万円！
冬季メニュー導入！
安全対策強化！', 82, '冬季メニューが好調なスタート。', NOW() - INTERVAL '50 days', NOW() - INTERVAL '1 day');

-- 先々月の目標（参考データ）
INSERT INTO monthly_goals (store_id, year, month, goal_text, achievement_rate, achievement_text, created_at, updated_at) VALUES
(2, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER,
   'クレーム対応研修実施！
売上目標1300万円！
衛生管理強化！', 90, '研修完了、売上も好調でした。', NOW() - INTERVAL '80 days', NOW() - INTERVAL '30 days'),
(3, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER,
   '売上目標1500万円！
接客コンテスト開催！
在庫管理改善！', 96, '接客コンテストが大成功でした。', NOW() - INTERVAL '80 days', NOW() - INTERVAL '30 days'),
(6, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER,
   '売上目標1400万円！
大阪らしさの追求！
スタッフ育成強化！', 94, '地域密着の取り組みが評価されました。', NOW() - INTERVAL '80 days', NOW() - INTERVAL '30 days');

-- シーケンスの更新
SELECT setval('monthly_goals_goal_id_seq', (SELECT MAX(goal_id) FROM monthly_goals));

-- ============================================================
-- 9. AIチャット履歴データ
-- ============================================================

INSERT INTO ai_chat_history (user_id, role, message, created_at) VALUES
-- スタッフからの質問と回答
('staff_001', 'user', 'フライヤーの適正温度は何度ですか？', NOW() - INTERVAL '10 days'),
('staff_001', 'assistant', 'フライヤーの適正温度は揚げ物の種類によって異なります。一般的には170-180℃が基本ですが、以下を参考にしてください：
- 天ぷら：170-180℃
- とんかつ：170-175℃
- 唐揚げ：160-170℃（二度揚げの場合、一度目は160℃、二度目は180℃）
- フライドポテト：180℃

温度が高すぎると外側だけ焦げて中が生になり、低すぎると油っぽくなります。温度計で確認しながら調理してください。', NOW() - INTERVAL '10 days' + INTERVAL '10 seconds'),

('staff_005', 'user', 'アレルギー対応のお客様への接客で気をつけることは？', NOW() - INTERVAL '8 days'),
('staff_005', 'assistant', 'アレルギー対応のお客様への接客では以下の点に注意してください：

1. **確認の徹底**
   - 必ずアレルギー食材を正確に聞き取る
   - メモを取り、キッチンに正確に伝達する

2. **メニューの説明**
   - アレルギー表を見せながら説明
   - 調味料に含まれる成分も確認
   - 不明な場合は「確認いたします」と伝え、必ず確認

3. **調理時の注意**
   - 専用の調理器具を使用（コンタミネーション防止）
   - 調理順序に注意

4. **提供時**
   - 料理名と「○○抜き」を復唱
   - 他のお客様の料理と混同しないよう注意

お客様の命に関わることなので、少しでも不安がある場合は店長に相談してください。', NOW() - INTERVAL '8 days' + INTERVAL '15 seconds'),

('staff_013', 'user', '売上が伸び悩んでいる時にできることは何ですか？', NOW() - INTERVAL '5 days'),
('staff_013', 'assistant', '売上向上のためにできる施策をいくつかご紹介します：

**即効性のある施策**
- 客単価アップ：デザートやドリンクのおすすめ声かけ
- 回転率向上：ピーク時のオペレーション効率化
- テイクアウト強化：SNSでの告知

**中期的な施策**
- リピーター施策：ポイントカード、次回使えるクーポン
- 口コミ対策：Googleマップのレビュー依頼
- 地域イベントへの参加

**分析すべきこと**
- 時間帯別の売上推移
- メニュー別の売れ筋
- 客層の変化

まずは現状の分析から始め、店長と相談しながら具体的な施策を検討してみてください。過去の日報データから傾向を把握することも有効です。', NOW() - INTERVAL '5 days' + INTERVAL '20 seconds'),

('staff_012', 'user', '新人スタッフの教育で心がけることは？', NOW() - INTERVAL '3 days'),
('staff_012', 'assistant', '新人スタッフの教育では以下のポイントを心がけてください：

**基本姿勢**
- 「できて当たり前」と思わず、丁寧に説明
- 質問しやすい雰囲気づくり
- 失敗を責めず、改善点を一緒に考える

**教え方のコツ**
1. まず見せる（デモンストレーション）
2. 一緒にやる（サポート付き実践）
3. 一人でやらせる（見守り）
4. フィードバック（良い点と改善点）

**注意点**
- 一度に多くを教えすぎない
- 優先順位をつけて段階的に
- メモを取る時間を与える
- 定期的に理解度を確認

**モチベーション管理**
- 小さな成功体験を積ませる
- 成長を具体的に褒める
- 目標を共有する

新人時代の経験が、その後のスタッフの成長に大きく影響します。根気強く、でも温かく見守ってあげてください。', NOW() - INTERVAL '3 days' + INTERVAL '25 seconds'),

('staff_017', 'user', 'レジでの金銭管理で注意することを教えてください', NOW() - INTERVAL '1 day'),
('staff_017', 'assistant', 'レジでの金銭管理における注意点をお伝えします：

**基本動作**
- 受け取った金額を必ず声に出して確認「○○円お預かりします」
- お釣りを渡す前にもう一度確認「○○円のお返しです」
- 大きいお札は一番上に置く

**違算防止**
- 現金を受け取ったら、すぐにレジに入れない（先にレジを打つ）
- お釣りは声に出しながら数える
- 1万円札は特に注意（5千円と間違えやすい）
- 迷ったら金庫に手を入れる前にお客様と一緒に確認

**トラブル時の対応**
- 金額が合わない場合は、すぐに店長に報告
- お客様との認識違いは録画確認で解決
- 絶対に自分で補填しない

**締め作業**
- 現金と売上データを必ず照合
- 違算があれば原因を記録
- 翌日のスタッフへの引き継ぎ

日頃から「確認を声に出す」習慣をつけることが、違算防止の最大のポイントです。', NOW() - INTERVAL '1 day' + INTERVAL '18 seconds');

-- シーケンスの更新
SELECT setval('ai_chat_history_chat_id_seq', (SELECT MAX(chat_id) FROM ai_chat_history));

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
-- UNION ALL SELECT '月次目標', COUNT(*) FROM monthly_goals
-- UNION ALL SELECT 'AIチャット履歴', COUNT(*) FROM ai_chat_history;

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
--             bbs_posts, bbs_comments, bbs_reactions, monthly_goals,
--             ai_chat_history RESTART IDENTITY CASCADE;

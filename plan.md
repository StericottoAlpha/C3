# AI チャット機能 実装計画（LangChainベース）

## 概要

レストラン店舗管理システムに、**LangChain Agent**を活用した高度なAIチャット機能を実装する。大量の実績データとナレッジベースから最適な情報を抽出し、複雑な分析タスクにも対応する。

---

## ユースケース & フロー

### ユースケース1: 過去事例の検索（明確なクエリ）

**シナリオ**: 店長が特定日のクレーム詳細を確認したい

```
【ユーザー】店長（店舗ID: 1）
【質問】"2025年12月9日のクレームについて教えて"

┌─────────────────────────────────────────────────┐
│ Step 1: ユーザーがチャット画面で質問を入力      │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 2: Django View → Agent起動                 │
│ POST /api/ai/chat/                              │
│ {"message": "2025年12月9日のクレーム..."}       │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 3: LangChain Agent分析                     │
│ - クエリ解析: 日付明確、対象明確                │
│ - 判断: 拡張不要                                │
│ - ツール選択: search_past_cases()               │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 4: search_past_cases() 実行                │
│                                                 │
│ 4-1. クエリベクトル化                           │
│      EmbeddingService.generate_embedding(       │
│        "2025年12月9日のクレーム"                │
│      )                                          │
│                                                 │
│ 4-2. メタデータフィルタ構築                     │
│      - store_id = 1 (ユーザーの店舗)            │
│      - date = "2025-12-09"                      │
│      - genre = "claim"                          │
│                                                 │
│ 4-3. PgVector類似度検索                         │
│      SELECT * FROM document_vectors             │
│      WHERE metadata->>'store_id' = '1'          │
│        AND metadata->>'date' = '2025-12-09'     │
│        AND metadata->>'genre' = 'claim'         │
│      ORDER BY embedding <=> query_vector        │
│      LIMIT 5                                    │
│                                                 │
│ 4-4. 結果取得                                   │
│      [                                          │
│        {                                        │
│          content: "12/9ホール、料理提供30分遅延"│
│          similarity: 0.92,                      │
│          metadata: {date: "2025-12-09", ...}    │
│        },                                       │
│        {...}                                    │
│      ]                                          │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 5: Agent判断（追加情報の必要性）           │
│ - 検索結果: クレーム事例3件ヒット               │
│ - 判断: 対応手順も確認すべき                    │
│ - ツール選択: search_manual()                   │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 6: search_manual("クレーム対応") 実行      │
│                                                 │
│ 6-1. クエリベクトル化                           │
│      EmbeddingService.generate_embedding(       │
│        "クレーム対応"                           │
│      )                                          │
│                                                 │
│ 6-2. KnowledgeVector検索                        │
│      SELECT * FROM knowledge_vectors            │
│      WHERE metadata->>'category' = '接客'       │
│      ORDER BY embedding <=> query_vector        │
│      LIMIT 3                                    │
│                                                 │
│ 6-3. 結果取得                                   │
│      [                                          │
│        {                                        │
│          content: "クレーム発生時は...          │
│                    1. お客様へ謝罪              │
│                    2. 店長へ報告...",           │
│          metadata: {                            │
│            document_title: "接客マニュアル",    │
│            chapter: "第3章"                     │
│          }                                      │
│        }                                        │
│      ]                                          │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 7: Agent最終回答生成                       │
│                                                 │
│ LLMに以下を渡して回答生成:                      │
│ - ユーザー質問                                  │
│ - 実績検索結果（3件）                           │
│ - マニュアル検索結果（1件）                     │
│                                                 │
│ 【生成された回答】                              │
│ "2025年12月9日には以下のクレームがありました:   │
│                                                 │
│ 1. ホールでの料理提供遅延（30分）               │
│    - 原因: キッチンの人手不足                   │
│    - 対応: お客様へ謝罪、会計時割引実施         │
│                                                 │
│ 2. ...                                          │
│                                                 │
│ 【マニュアル参照】                              │
│ 接客マニュアル第3章によると、クレーム発生時は  │
│ まずお客様へ誠実に謝罪し、店長へ即座に報告      │
│ することが定められています。"                   │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 8: チャット履歴DB保存                      │
│                                                 │
│ AIChatHistory.objects.create(                   │
│   user=店長,                                    │
│   role='user',                                  │
│   message="2025年12月9日のクレーム..."          │
│ )                                               │
│                                                 │
│ AIChatHistory.objects.create(                   │
│   user=店長,                                    │
│   role='assistant',                             │
│   message="2025年12月9日には..."                │
│ )                                               │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 9: フロントエンドへ返却                    │
│                                                 │
│ Response: {                                     │
│   "message": "2025年12月9日には...",            │
│   "sources": [                                  │
│     {type: "daily_report", id: 45, date: ...},  │
│     {type: "manual", title: "接客マニュアル"}   │
│   ],                                            │
│   "token_count": 1250                           │
│ }                                               │
└───────────────────┬─────────────────────────────┘
                    ↓
【ユーザー画面に表示】
質問: "2025年12月9日のクレームについて教えて"
回答: "2025年12月9日には以下のクレームが..."
参照: 📄 日報ID:45, 📖 接客マニュアル第3章
```

**トークン消費**: 約1,200トークン
**所要時間**: 2-3秒

---

### ユースケース2: 曖昧なクエリの検索（拡張検索）

**シナリオ**: アルバイトスタッフが前日のトラブルを確認したい

```
【ユーザー】アルバイトスタッフ（店舗ID: 1）
【質問】"昨日何か問題ありましたか？"
【現在日時】2025年12月10日 10:00

┌─────────────────────────────────────────────────┐
│ Step 1-2: 質問入力 → Agent起動（同上）          │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 3: LangChain Agent分析                     │
│ - クエリ解析:                                   │
│   * "昨日" = 曖昧（日付未指定）                 │
│   * "問題" = 抽象的（クレーム？事故？違算？）   │
│ - 判断: クエリ拡張が必要                        │
│ - ツール選択: expand_and_search_cases()         │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 4: expand_and_search_cases() 実行          │
│                                                 │
│ 4-1. Query Expansion (LLM呼び出し)              │
│      Prompt:                                    │
│      """                                        │
│      【現在情報】                               │
│      - 今日: 2025-12-10                         │
│      - 店舗ID: 1                                │
│      - ユーザー: アルバイト佐藤                 │
│                                                 │
│      【質問】                                   │
│      昨日何か問題ありましたか？                 │
│                                                 │
│      【拡張ルール】                             │
│      1. 日付を正規化                            │
│      2. "問題"の同義語追加                      │
│      3. レストラン業務の文脈を考慮              │
│                                                 │
│      最大5個の検索クエリに拡張してください      │
│      """                                        │
│                                                 │
│      LLM応答:                                   │
│      {                                          │
│        "expanded_queries": [                    │
│          "2025-12-09 問題",                     │
│          "12/9 トラブル",                       │
│          "前日 クレーム",                       │
│          "昨日 事故",                           │
│          "2025年12月9日 不具合"                 │
│        ]                                        │
│      }                                          │
│                                                 │
│ 4-2. 各クエリをベクトル化（5回）                │
│      query1_vec = embed("2025-12-09 問題")      │
│      query2_vec = embed("12/9 トラブル")        │
│      ...                                        │
│                                                 │
│ 4-3. 並列ベクトル検索（5回同時実行）            │
│      Query 1結果: [doc123, doc124, doc125]      │
│      Query 2結果: [doc123, doc126, doc127] ←重複│
│      Query 3結果: [doc123, doc128, doc129] ←重複│
│      Query 4結果: [doc130, doc131]              │
│      Query 5結果: [doc123, doc132]         ←重複│
│                                                 │
│ 4-4. 結果統合・ランキング                       │
│      merge_and_rank():                          │
│                                                 │
│      doc123:                                    │
│        - hit_count: 4 (4クエリでヒット)         │
│        - max_similarity: 0.91                   │
│        - final_score: 40.91 (4*10 + 0.91)       │
│        - matched_queries: [query1, 2, 3, 5]     │
│                                                 │
│      doc126:                                    │
│        - hit_count: 1                           │
│        - max_similarity: 0.85                   │
│        - final_score: 10.85                     │
│                                                 │
│      ソート後Top-5を返却:                       │
│      [doc123, doc128, doc129, doc126, doc125]   │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 5: Agent判断                               │
│ - 検索結果分析:                                 │
│   * doc123: キッチン火災報知器誤作動            │
│   * doc128: フライヤー温度異常                  │
│   * doc129: 駐車場での接触事故                  │
│ - 判断: 安全関連の問題が多い                    │
│ - 追加ツール選択: search_manual("安全管理")     │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 6: search_manual("安全管理") 実行          │
│ （KnowledgeVector検索）                         │
│                                                 │
│ 結果: "安全マニュアル 第2章 緊急時対応"         │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 7: Agent最終回答生成                       │
│                                                 │
│ 【生成された回答】                              │
│ "昨日（12月9日）は以下の問題が発生しました:     │
│                                                 │
│ 【重要度:高】                                   │
│ 1. キッチン火災報知器の誤作動（15:30頃）        │
│    - 原因: フライヤー付近の湯気                 │
│    - 対応: 消防へ連絡済み、機器点検実施         │
│                                                 │
│ 2. フライヤー温度異常（16:00頃）                │
│    - 原因: センサー故障の可能性                 │
│    - 対応: 業者手配済み、明日修理予定           │
│                                                 │
│ 【重要度:中】                                   │
│ 3. 駐車場での軽微な接触事故（19:00頃）          │
│    - 対応: 当事者間で解決済み                   │
│                                                 │
│ 【参考】                                        │
│ 安全マニュアル第2章によると、火災報知器が      │
│ 作動した場合は必ず消防へ連絡し、原因を         │
│ 特定することが義務付けられています。            │
│ 適切に対応されています。"                      │
└───────────────────┬─────────────────────────────┘
                    ↓
【Step 8-9: DB保存・返却（同上）】
```

**トークン消費**: 約2,500トークン（拡張処理含む）
**所要時間**: 4-5秒

---

### ユースケース3: 複雑な分析タスク

**シナリオ**: 店長が売上低下の原因分析を依頼

```
【ユーザー】店長（店舗ID: 1）
【質問】"今月の売上が先月より15%下がっている。原因を分析して"

┌─────────────────────────────────────────────────┐
│ Step 1-2: 質問入力 → Agent起動                  │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 3: LangChain Agent分析                     │
│ - クエリ解析: 複雑な分析タスク                  │
│ - 判断: 複数ツールの組み合わせが必要            │
│ - 実行計画立案:                                 │
│   1. 売上データ取得                             │
│   2. 期間比較                                   │
│   3. クレーム傾向確認                           │
│   4. 関連事例検索                               │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 4: Tool #1 - get_sales_trend(days=30)      │
│                                                 │
│ 今月の売上データ取得:                           │
│ {                                               │
│   total_sales: 4,250,000円,                     │
│   average_sales: 141,667円/日,                  │
│   total_customers: 1,250人,                     │
│   trend: "下降傾向"                             │
│ }                                               │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 5: Tool #2 - compare_periods()             │
│                                                 │
│ 前月比較:                                       │
│ {                                               │
│   current: {sales: 4,250,000, customers: 1,250},│
│   previous: {sales: 5,000,000, customers: 1,500│
│   change_percentage: -15%,                      │
│   customer_change: -16.7%                       │
│ }                                               │
│                                                 │
│ Agent判断: 顧客数も減少 → 集客の問題？         │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 6: Tool #3 - get_claim_statistics()        │
│                                                 │
│ クレーム傾向:                                   │
│ {                                               │
│   total: 12件（先月: 8件）,                     │
│   average_per_day: 0.4件,                       │
│   daily_breakdown: [                            │
│     {date: "12/5", count: 3, genre: "提供遅延"},│
│     {date: "12/8", count: 2, genre: "味"}       │
│   ]                                             │
│ }                                               │
│                                                 │
│ Agent判断: クレーム増加 → 詳細確認必要         │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 7: Tool #4 - expand_and_search_cases()     │
│                                                 │
│ クエリ: "今月のクレーム 提供遅延"               │
│                                                 │
│ 検索結果分析:                                   │
│ - 12/5: ランチタイム、キッチン人手不足で遅延   │
│ - 12/8: ディナータイム、新人スタッフミス       │
│ - 12/12: ランチ、食材配送遅延の影響            │
│                                                 │
│ パターン発見: キッチンの人手不足が頻発         │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 8: Agent最終分析・回答生成                 │
│                                                 │
│ 【生成された回答】                              │
│ "今月の売上15%減少の原因を分析しました:         │
│                                                 │
│ 【主要因】                                      │
│ 1. 顧客数の減少（-16.7%）                      │
│    → 売上減少の最大要因                        │
│                                                 │
│ 2. クレーム件数の増加（8件→12件、+50%）        │
│    → 主にサービス品質の低下                    │
│                                                 │
│ 【根本原因の推定】                              │
│ キッチンスタッフの人手不足:                     │
│ - 12/5: ランチタイムの提供遅延                  │
│ - 12/8: 新人スタッフのミス                      │
│ - 12/12: 食材配送遅延への対応遅れ              │
│                                                 │
│ これらの問題が顧客満足度を低下させ、            │
│ リピート客の減少に繋がっている可能性が高い。   │
│                                                 │
│ 【推奨アクション】                              │
│ 1. キッチンスタッフの増員（緊急）               │
│ 2. 新人教育プログラムの見直し                   │
│ 3. ピークタイム対応マニュアルの再確認           │
│ 4. 既存顧客へのフォローアップ施策               │
│                                                 │
│ 【参照データ】                                  │
│ - 売上データ: 2025年11月 vs 12月               │
│ - クレーム分析: 12件中9件が提供遅延関連         │
│ - 日報参照: 12/5, 12/8, 12/12の報告"            │
└───────────────────┬─────────────────────────────┘
                    ↓
【Step 9-10: DB保存・返却】
```

**使用ツール**: 4個（統計×2、検索×2）
**トークン消費**: 約3,500トークン
**所要時間**: 6-8秒

---

### ユースケース4: マニュアル参照のみ

**シナリオ**: 新人スタッフが手順を確認

```
【ユーザー】新人アルバイト（店舗ID: 1）
【質問】"フライヤーの点検手順を教えて"

┌─────────────────────────────────────────────────┐
│ Step 1-3: 質問入力 → Agent起動・分析            │
│                                                 │
│ Agent判断:                                      │
│ - マニュアル参照のみで回答可能                  │
│ - 過去事例検索は不要                            │
│ - ツール選択: search_manual()                   │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 4: search_manual("フライヤー 点検")        │
│                                                 │
│ KnowledgeVector検索:                            │
│ - category: "調理機器"                          │
│ - クエリベクトル化 → 類似度検索                 │
│                                                 │
│ 結果:                                           │
│ [                                               │
│   {                                             │
│     content: "【フライヤー日次点検】            │
│                1. 油温確認（170-180℃）         │
│                2. 油の状態確認（色・臭い）      │
│                3. フィルター清掃                │
│                4. 安全装置動作確認              │
│                5. 点検記録表への記入",          │
│     metadata: {                                 │
│       document_title: "調理機器マニュアル",     │
│       chapter: "第5章",                         │
│       section: "5.2 フライヤー管理"             │
│     },                                          │
│     similarity: 0.95                            │
│   }                                             │
│ ]                                               │
└───────────────────┬─────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Step 5: Agent回答生成                           │
│                                                 │
│ 【生成された回答】                              │
│ "フライヤーの日次点検手順は以下の通りです:      │
│                                                 │
│ 1. 油温確認（170-180℃）                        │
│    → 温度計で確認し、適正範囲内か確認          │
│                                                 │
│ 2. 油の状態確認                                 │
│    → 色が濃すぎないか、異臭がないか確認        │
│                                                 │
│ 3. フィルター清掃                               │
│    → 毎日営業終了後に清掃                      │
│                                                 │
│ 4. 安全装置動作確認                             │
│    → 緊急停止ボタン、過熱防止装置を確認        │
│                                                 │
│ 5. 点検記録表への記入                           │
│    → 各項目を点検記録表に記録                  │
│                                                 │
│ 詳細は「調理機器マニュアル 第5章 5.2節」を     │
│ 参照してください。"                             │
│                                                 │
│ 【参照】調理機器マニュアル 第5章 5.2節          │
└───────────────────┬─────────────────────────────┘
                    ↓
【DB保存・返却】
```

**使用ツール**: 1個（マニュアル検索のみ）
**トークン消費**: 約800トークン
**所要時間**: 1-2秒

## 設計方針の転換理由

**当初案**: カスタム軽量システム（LangChain不使用）
**最終案**: LangChain Agent採用

**採用理由**:
1. **大量データからの最適情報抽出**が主目的
2. **複雑な分析タスク**への対応（「売上低下の原因分析」等）
3. **将来の大規模拡張**を見据えた設計（ツール10個以上）
4. **自律的な問題発見機能**との統合（通知システム連携）
5. LLMは**Ollama（実験）→ OpenAI API（本番）**で、Function Calling活用

## システムアーキテクチャ

```
User Query: "昨日のクレームの詳細を教えて"
    ↓
[LangChain Agent (Function Calling)]
    ↓
Agent判断: 「曖昧なクエリ → 拡張が必要」
    ↓
Tool: expand_and_search_cases()
    ├─ LLMでクエリ拡張: ["2025-12-09 クレーム", "12/9 苦情", "前日 顧客不満"]
    ├─ 並列ベクトル検索（実績RAG）
    └─ 結果統合 + ランキング
    ↓
Agent判断: 「対応手順も確認すべき」
    ↓
Tool: search_manual("クレーム対応")
    └─ マニュアルRAG検索
    ↓
Agent: 最終回答生成
```

## コア設計原則

### 1. エージェントにクエリ拡張判断を委譲

**理由**: 不要な拡張検索コスト > Agent判断コスト

```
【拡張不要なクエリ例】
"今日の売上" → 明確 → 直接検索
"店舗001のクレーム数" → 明確 → 直接検索

【拡張必要なクエリ例】
"昨日の問題" → 曖昧 → 拡張必要
"最近のトラブル" → 曖昧 → 拡張必要
"佐藤さんの件" → 曖昧 → 拡張必要
```

Agentが自律的に判断：
- 明確なクエリ → `search_past_cases(query, expand=False)`
- 曖昧なクエリ → `expand_and_search_cases(query)`（LLMで拡張）

### 2. RAGの2層構造

**実績RAG** (`DocumentVector`)
- 日報（クレーム、賞賛、事故、報告）
- 掲示板投稿・コメント
- 店舗実績データ

**ナレッジRAG** (`KnowledgeVector`) ← 新規
- 業務マニュアル（PDF/Word → テキスト化）
- 対応規則・ガイドライン
- FAQ・ベストプラクティス
- 社内通達

**分離理由**:
- 検索意図が異なる（「過去事例」vs「正式手順」）
- 更新頻度が違う（毎日 vs 月次）
- メタデータ構造が違う（日付・店舗 vs 章・節・バージョン）
- チャンク戦略が違う（小 vs 大）

### 3. エージェント型式

**採用**: OpenAI Function Calling Agent
- 理由: 将来OpenAI API使用時、最もトークン効率が良い
- ReActより**20-30%トークン削減**
- Ollama互換モデル（llama3.2-function-calling等）でも使用可能

### 4. LLM構成

**実験フェーズ**: Ollama + Llama 3.2 (3B/8B)
**本番フェーズ**: OpenAI API (GPT-4o-mini推奨)

**コスト最適化**:
- セマンティックキャッシュ（LangChain標準）
- ツール結果の簡潔化（サマリーのみ返す）
- 不要なツール呼び出しを防ぐプロンプト設計

---

## ツール定義

### 検索系ツール

**1. search_past_cases(query, expand=False)**
```
目的: 過去の日報・掲示板から事例検索
引数:
  - query: 検索クエリ
  - expand: False = 直接検索、True不可（拡張は別ツール）
用途: 「先月の同様のクレーム」「佐藤さんが対応した案件」
```

**2. expand_and_search_cases(query, user_context)**
```
目的: クエリを拡張してから実績検索
処理:
  1. LLMでクエリ拡張（3-5個）
  2. 並列ベクトル検索
  3. 結果統合 + 重複排除
用途: 曖昧なクエリ「昨日の問題」「最近のトラブル」
```

**3. search_manual(query, category=None)**
```
目的: マニュアル・規則からの検索
引数:
  - query: 検索クエリ
  - category: "衛生管理" | "接客" | "調理" | None
用途: 「フライヤー点検手順」「クレーム対応規則」
```

### 統計系ツール

**4. get_claim_statistics(store_id, days=30)**
```
目的: クレーム件数・推移の取得
戻り値: {total, average_per_day, daily_breakdown}
```

**5. get_sales_trend(store_id, days=30)**
```
目的: 売上推移の取得
戻り値: {total_sales, average_sales, total_customers, trend}
```

**6. get_cash_difference_analysis(store_id, days=30)**
```
目的: 違算分析
戻り値: {total_difference, days_over_threshold, threshold}
```

**7. compare_periods(store_id, current_days=30, previous_days=30)**
```
目的: 期間比較（前月比等）
戻り値: {current, previous, change_percentage}
```

### 分析系ツール（将来実装）

**8. analyze_root_cause(issue_description, time_range)**
```
目的: 根本原因分析（複数ツール組み合わせ）
処理:
  1. 統計データ取得
  2. 関連事例検索
  3. マニュアル確認
  4. 原因推論
```

**9. detect_anomalies(store_id)**
```
目的: 異常検知（通知機能で使用）
処理: 売上・クレーム・違算の異常パターン検出
```

**10. suggest_improvements(analysis_results)**
```
目的: 改善提案生成
処理: 分析結果から具体的アクションプランを生成
```

---

## データモデル

### 既存: DocumentVector（実績RAG用）

```python
class DocumentVector(models.Model):
    vector_id = PK
    source_type = 'daily_report' | 'bbs_post' | 'bbs_comment'
    source_id = int
    content = TextField
    metadata = JSONField  # {store_id, date, genre, location, user_id, ...}
    embedding = VectorField(dimensions=384)  # sentence-transformers
    created_at, updated_at
```

### 新規: KnowledgeVector（マニュアルRAG用）

```python
class KnowledgeVector(models.Model):
    """
    業務マニュアル・規則のベクトル表現
    """
    vector_id = PK

    # ドキュメント情報
    document_type = 'manual' | 'guideline' | 'faq' | 'policy'
    document_id = int  # 元文書のID

    # コンテンツ
    content = TextField  # チャンク（500-1000トークン）

    # メタデータ
    metadata = JSONField
    """
    {
        "category": "衛生管理" | "接客" | "調理" | "その他",
        "document_title": "業務マニュアル 第3版",
        "chapter": "第5章",
        "section": "5.2 フライヤー管理",
        "version": "2024-12",
        "last_updated": "2024-12-01",
        "page_number": 42
    }
    """

    # ベクトル
    embedding = VectorField(dimensions=384)

    # 管理用
    created_at, updated_at

    class Meta:
        db_table = 'knowledge_vectors'
        indexes = [
            ('document_type', 'document_id'),
            ('metadata__category',),  # GIN index
            ('created_at',)
        ]
```

### 新規: KnowledgeDocument（マニュアル原本管理）

```python
class KnowledgeDocument(models.Model):
    """
    マニュアル・規則の原本管理
    """
    document_id = PK
    document_type = 'manual' | 'guideline' | 'faq' | 'policy'
    title = CharField
    category = CharField  # "衛生管理"等

    # ファイル情報
    file_path = FileField(upload_to='knowledge/')  # PDF/Word/Markdown
    file_type = CharField  # 'pdf' | 'docx' | 'md'

    # バージョン管理
    version = CharField  # "2024-12"
    is_active = BooleanField(default=True)

    # メタデータ
    description = TextField
    author = CharField
    published_date = DateField

    # ベクトル化状態
    vectorized = BooleanField(default=False)
    vectorized_at = DateTimeField(null=True)

    created_at, updated_at
```

---

## 実装ステップ（詳細）

### Phase 1: 基盤構築（2-3日）

**ステップ1.1: データモデル作成**
```bash
# ai_features/models.py に追加
- KnowledgeDocument
- KnowledgeVector

python manage.py makemigrations
python manage.py migrate
```

**ステップ1.2: PDFテキスト抽出**
```bash
# requirements.txt に追加
pypdf2>=3.0.0
python-docx>=1.0.0
markdown>=3.5.0

# ai_features/services/document_parser.py 作成
class DocumentParser:
    - extract_from_pdf()
    - extract_from_docx()
    - extract_from_markdown()
```

**ステップ1.3: マニュアルチャンキング**
```python
# ai_features/services/knowledge_chunker.py
class KnowledgeChunker:
    """
    マニュアル専用チャンキング
    - チャンクサイズ: 500-1000トークン（実績より大）
    - オーバーラップ: 100トークン
    - セマンティック境界を考慮（章・節区切り）
    """
```

### Phase 2: ツール実装（3-4日）

**ステップ2.1: 検索ツール（3個）**
- `search_past_cases()`
- `expand_and_search_cases()` ← **Query Expansion機能**
- `search_manual()`

**ステップ2.2: 統計ツール（4個）**
- `get_claim_statistics()`
- `get_sales_trend()`
- `get_cash_difference_analysis()`
- `compare_periods()`

**ステップ2.3: Query Expansion実装**
```python
# ai_features/services/query_expander.py
class QueryExpander:
    """
    LLMを使ったクエリ拡張
    """
    def expand(query: str, user_context: dict) -> list[str]:
        # 日付正規化 + 同義語 + エンティティ認識
        # 最大5個の拡張クエリ生成
```

**ステップ2.4: 結果統合機能**
```python
# ai_features/services/result_merger.py
def merge_and_rank(results: list) -> list:
    # 重複排除 + スコアリング
    # 複数クエリでヒット → スコア加算
```

### Phase 3: LangChain Agent（2-3日）

**ステップ3.1: Ollamaセットアップ**
```bash
# Ollama インストール
curl -fsSL https://ollama.com/install.sh | sh

# Function Calling対応モデル
ollama pull llama3.2:3b
# または
ollama pull llama3.1:8b
```

**ステップ3.2: LangChain統合**
```python
# requirements.txt に追加
langchain>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5  # 本番用

# ai_features/agents/chat_agent.py
from langchain.agents import create_openai_functions_agent
from langchain_community.llms import Ollama

def create_agent():
    llm = Ollama(model="llama3.2:3b")
    tools = [
        search_past_cases_tool,
        expand_and_search_cases_tool,
        search_manual_tool,
        # ... 統計ツール
    ]
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)
```

**ステップ3.3: プロンプトエンジニアリング**
```python
SYSTEM_PROMPT = """
あなたはレストラン運営支援AIアシスタントです。

【利用可能なツール】
- expand_and_search_cases: 曖昧なクエリの場合に使用
- search_past_cases: 明確なクエリの場合に使用
- search_manual: 手順・規則を確認する場合に使用
- get_claim_statistics: 統計データが必要な場合に使用
... (他のツール説明)

【重要な判断基準】
1. クエリの曖昧性判定
   - 曖昧（「昨日の問題」「最近のトラブル」）→ expand_and_search_cases
   - 明確（「2025-12-09のクレーム」）→ search_past_cases

2. 必要なツールのみ使用
   - 過剰なツール呼び出しを避ける
   - 1つのツールで十分な場合は追加呼び出ししない

3. 回答の構造
   - マニュアル情報 + 実績事例 を組み合わせる
   - 具体的な数値・日付を引用
"""
```

### Phase 4: 最適化（1-2日）

**ステップ4.1: セマンティックキャッシュ**
```python
from langchain.cache import RedisSemanticCache

# 類似質問の結果をキャッシュ
# 「昨日のクレーム」≈「前日のクレーム」→ 再利用
```

**ステップ4.2: トークン消費モニタリング**
```python
# ai_features/monitoring/token_tracker.py
class TokenTracker:
    def track_agent_run(query, tools_used, token_count):
        # Prometheusメトリクス or DB保存
```

**ステップ4.3: エラーハンドリング**
```python
# Agentがツール選択失敗時のフォールバック
# LLM呼び出し失敗時のリトライロジック
```

---

## Critical Files

### 新規作成

1. **`ai_features/models.py`**
   - KnowledgeDocument
   - KnowledgeVector

2. **`ai_features/services/document_parser.py`**
   - PDFテキスト抽出

3. **`ai_features/services/knowledge_chunker.py`**
   - マニュアル専用チャンキング

4. **`ai_features/services/query_expander.py`**
   - LLMベースのQuery Expansion

5. **`ai_features/services/result_merger.py`**
   - 検索結果統合・ランキング

6. **`ai_features/tools/`** (新規ディレクトリ)
   - `search_tools.py` (3個の検索ツール)
   - `analytics_tools.py` (4個の統計ツール)

7. **`ai_features/agents/chat_agent.py`**
   - LangChain Agent定義

8. **`ai_features/views.py`**
   - Agent呼び出しエンドポイント

### 既存ファイル修正

1. **`ai_features/services.py`**
   - 既存のVectorizationService等を活用
   - 新規ツールから呼び出し

2. **`requirements.txt`**
   ```
   langchain>=0.1.0
   langchain-community>=0.0.20
   langchain-openai>=0.0.5
   pypdf2>=3.0.0
   python-docx>=1.0.0
   ```

---

## まとめ

### 推奨アーキテクチャ: LangChain Function Calling Agent

**コア設計**:
1. **Query Expansion判断をAgentに委譲** → トークン効率最大化
2. **RAG 2層構造**（実績 + マニュアル）→ 検索精度向上
3. **10個のツール**（検索3 + 統計4 + 分析3）→ 将来拡張容易
4. **Function Calling Agent** → ReActより20-30%トークン削減

**LLM構成**:
- **実験**: Ollama + Llama 3.2 (無料)
- **本番**: OpenAI API + GPT-4o-mini (低コスト)

**最適化戦略**:
- セマンティックキャッシュ
- ツール結果の簡潔化
- 不要なツール呼び出し防止プロンプト

**実装期間**: 約8-10日
- Phase 1: 2-3日
- Phase 2: 3-4日
- Phase 3: 2-3日
- Phase 4: 1-2日

**次のステップ**: Phase 1からの実装開始

---

## ベクトル類似度検索の詳細処理

### 検索の全体フロー

```
User Query
    ↓
[Agent判断] クエリの明確性
    ↓
┌─────────────────┴─────────────────┐
│                                   │
【明確なクエリ】              【曖昧なクエリ】
    ↓                              ↓
直接検索                      拡張検索
search_past_cases()          expand_and_search_cases()
    ↓                              ↓
単一クエリで検索              複数クエリで並列検索
    ↓                              ↓
    └──────────┬───────────────────┘
               ↓
        類似度検索実行
        (PgVector)
               ↓
        結果返却
```

### パターン1: 直接検索（明確なクエリ）

**ユーザークエリ例**: "2025-12-09のクレーム"

```python
# ステップ1: Agentがツール選択
Agent判断 → 「日付が明確 → expand不要」
        → search_past_cases(query="2025-12-09 クレーム", expand=False)

# ステップ2: クエリのベクトル化
query_text = "2025-12-09のクレーム"
query_embedding = EmbeddingService.generate_embedding(query_text)
# → [0.234, 0.456, 0.123, ..., 0.789]  # 384次元ベクトル

# ステップ3: メタデータフィルタ構築
filters = {
    'store_id': user.store_id,  # ユーザーの所属店舗
    'date': '2025-12-09',       # 日付で絞り込み
    'genre': 'claim'            # クレームのみ
}

# ステップ4: PgVectorで類似度検索（SQL）
sql = """
    SELECT
        vector_id,
        source_type,
        source_id,
        content,
        metadata,
        1 - (embedding <=> %s::vector) AS similarity  -- コサイン類似度
    FROM document_vectors
    WHERE
        metadata->>'store_id' = %s
        AND metadata->>'date' = %s
        AND metadata->>'genre' = %s
    ORDER BY embedding <=> %s::vector  -- 類似度順（距離が近い順）
    LIMIT 5;  -- Top-5取得
"""

# ステップ5: 結果取得
results = [
    {
        'vector_id': 123,
        'source_type': 'daily_report',
        'source_id': 45,
        'content': '12月9日、ホールにて料理提供が30分遅延。お客様から苦情...',
        'metadata': {'store_id': 1, 'date': '2025-12-09', 'genre': 'claim', ...},
        'similarity': 0.92  # 非常に関連が高い
    },
    {
        'content': '...',
        'similarity': 0.87
    },
    # ... 最大5件
]

# ステップ6: Agentに結果返却
# Agentはこの結果を使って最終回答を生成
```

### パターン2: 拡張検索（曖昧なクエリ）

**ユーザークエリ例**: "昨日の問題"

```python
# ステップ1: Agentがツール選択
Agent判断 → 「"昨日"は曖昧、"問題"も抽象的 → 拡張必要」
        → expand_and_search_cases(query="昨日の問題", user_context)

# ステップ2: Query Expansion（LLMで拡張）
user_context = {
    'current_date': '2025-12-10',
    'store_id': 1,
    'user_name': '佐藤'
}

llm_prompt = f"""
ユーザーの質問を、より具体的な検索クエリに拡張してください。

【現在の情報】
- 今日: 2025-12-10
- 店舗ID: 1
- ユーザー: 佐藤

【質問】
昨日の問題

【拡張ルール】
1. 日付表現を正規化（「昨日」→「2025-12-09」）
2. 同義語を追加（「問題」→「トラブル」「クレーム」「事故」）
3. 関連エンティティ（場所、機器名等）

最大5個の拡張クエリをJSON形式で返してください：
{{"expanded_queries": [...]}}
"""

# LLM応答
expanded_queries = [
    "2025-12-09 問題",
    "12/9 トラブル",
    "前日 クレーム",
    "昨日 事故",
    "2025年12月9日 不具合"
]

# ステップ3: 各クエリをベクトル化
query_embeddings = []
for query in expanded_queries:
    embedding = EmbeddingService.generate_embedding(query)
    query_embeddings.append({
        'query': query,
        'embedding': embedding
    })

# ステップ4: 並列ベクトル検索
all_results = []

for qe in query_embeddings:
    sql = """
        SELECT
            vector_id,
            source_type,
            source_id,
            content,
            metadata,
            1 - (embedding <=> %s::vector) AS similarity,
            %s AS matched_query  -- どのクエリでヒットしたか記録
        FROM document_vectors
        WHERE
            metadata->>'store_id' = %s
            AND metadata->>'date' = '2025-12-09'  -- 日付フィルタ
        ORDER BY embedding <=> %s::vector
        LIMIT 10;  -- 拡張検索時は多めに取得
    """

    results = execute_query(sql, [qe['embedding'], qe['query'], store_id, qe['embedding']])
    all_results.extend(results)

# 実行結果（例）
all_results = [
    # クエリ1「2025-12-09 問題」でヒット
    {'vector_id': 123, 'content': '...', 'similarity': 0.89, 'matched_query': '2025-12-09 問題'},
    {'vector_id': 124, 'content': '...', 'similarity': 0.82, 'matched_query': '2025-12-09 問題'},

    # クエリ2「12/9 トラブル」でヒット
    {'vector_id': 123, 'content': '...', 'similarity': 0.91, 'matched_query': '12/9 トラブル'},  # 重複
    {'vector_id': 125, 'content': '...', 'similarity': 0.78, 'matched_query': '12/9 トラブル'},

    # クエリ3「前日 クレーム」でヒット
    {'vector_id': 123, 'content': '...', 'similarity': 0.88, 'matched_query': '前日 クレーム'},  # 重複
    {'vector_id': 126, 'content': '...', 'similarity': 0.85, 'matched_query': '前日 クレーム'},

    # ... 他のクエリの結果
]

# ステップ5: 結果統合・ランキング
def merge_and_rank(all_results):
    """
    重複排除 + スコアリング

    スコアリングルール:
    - 複数クエリでヒット → hit_count加算
    - 類似度の最高値を保持
    - 最終スコア = hit_count * 10 + max_similarity
    """
    doc_map = {}

    for result in all_results:
        doc_id = (result['source_type'], result['source_id'])

        if doc_id not in doc_map:
            doc_map[doc_id] = {
                'doc': result,
                'hit_count': 1,
                'max_similarity': result['similarity'],
                'matched_queries': [result['matched_query']],
                'similarities': [result['similarity']]
            }
        else:
            # 既存ドキュメント → ヒット回数増加
            doc_map[doc_id]['hit_count'] += 1
            doc_map[doc_id]['matched_queries'].append(result['matched_query'])
            doc_map[doc_id]['similarities'].append(result['similarity'])
            # 最高類似度を更新
            doc_map[doc_id]['max_similarity'] = max(
                doc_map[doc_id]['max_similarity'],
                result['similarity']
            )

    # スコア計算
    ranked_docs = []
    for doc_id, data in doc_map.items():
        final_score = data['hit_count'] * 10 + data['max_similarity']
        ranked_docs.append({
            'doc': data['doc'],
            'hit_count': data['hit_count'],
            'max_similarity': data['max_similarity'],
            'final_score': final_score,
            'matched_queries': data['matched_queries']
        })

    # 最終スコアでソート
    ranked_docs.sort(key=lambda x: x['final_score'], reverse=True)

    return ranked_docs

# ステップ6: 統合結果
merged_results = merge_and_rank(all_results)

# 統合後の結果（例）
merged_results = [
    {
        'doc': {'vector_id': 123, 'content': '...'},
        'hit_count': 3,  # 3つのクエリでヒット
        'max_similarity': 0.91,
        'final_score': 30.91,  # 3*10 + 0.91
        'matched_queries': ['2025-12-09 問題', '12/9 トラブル', '前日 クレーム']
    },
    {
        'doc': {'vector_id': 126, 'content': '...'},
        'hit_count': 1,
        'max_similarity': 0.85,
        'final_score': 10.85,
        'matched_queries': ['前日 クレーム']
    },
    # ... Top-5を返却
]

# ステップ7: Agentに結果返却
return merged_results[:5]  # 上位5件
```

### コサイン類似度の解釈

```
類似度スコアの目安:

0.9 - 1.0  : ほぼ同一内容（非常に関連が高い）
0.8 - 0.9  : 強く関連
0.7 - 0.8  : ある程度関連
0.6 - 0.7  : 弱く関連
0.0 - 0.6  : ほとんど関連なし（通常は返さない）
```

### メタデータフィルタの活用例

```python
# 例1: 特定店舗の先月のクレームのみ
filters = {
    'store_id': 1,
    'genre': 'claim',
    'date_from': '2024-11-01',
    'date_to': '2024-11-30'
}

WHERE metadata->>'store_id' = '1'
  AND metadata->>'genre' = 'claim'
  AND metadata->>'date' >= '2024-11-01'
  AND metadata->>'date' <= '2024-11-30'

# 例2: 特定ユーザーが作成した日報
filters = {
    'store_id': 1,
    'user_id': 'S001'
}

WHERE metadata->>'store_id' = '1'
  AND metadata->>'user_id' = 'S001'

# 例3: キッチンで発生したトラブル
filters = {
    'store_id': 1,
    'location': 'kitchen'
}

WHERE metadata->>'store_id' = '1'
  AND metadata->>'location' = 'kitchen'
```

### PgVectorのパフォーマンス最適化

```sql
-- IVFFlat インデックス作成（初回セットアップ時）
CREATE INDEX document_vectors_embedding_idx
ON document_vectors
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- リスト数はデータ量の√が目安

-- メタデータ用のGINインデックス
CREATE INDEX document_vectors_metadata_idx
ON document_vectors
USING GIN (metadata jsonb_path_ops);

-- 検索クエリの実行計画確認
EXPLAIN ANALYZE
SELECT ...
FROM document_vectors
WHERE ...
ORDER BY embedding <=> query_vector
LIMIT 5;
```

### Top-K値の動的決定

```python
# 既存のQueryClassifierを活用
class QueryClassifier:
    @classmethod
    def classify_and_get_top_k(cls, query: str) -> int:
        """
        クエリの性質に応じてTop-K値を決定
        """
        # 特定の事例検索（明確）→ 少なめ
        if '〇〇店' in query or '〇月〇日' in query:
            return 3

        # トレンド分析（傾向把握）→ 中程度
        if '傾向' in query or '多い' in query:
            return 12

        # 包括的調査（全体像）→ 多め
        if '全て' in query or '一覧' in query:
            return 20

        # デフォルト
        return 5
```

### 検索結果のAgentへの渡し方

```python
# Agentのツールが返す形式
return {
    'results': [
        {
            'content': '...',
            'similarity': 0.92,
            'metadata': {...},
            'hit_count': 3,  # 拡張検索の場合のみ
            'matched_queries': [...]  # 拡張検索の場合のみ
        },
        ...
    ],
    'summary': f'{len(results)}件のドキュメントが見つかりました',
    'search_type': 'expanded' | 'direct',
    'query_count': 1 or 5,  # 使用したクエリ数
}

# Agentはこれを使って最終回答生成
# 類似度やヒット回数が高いものほど信頼性が高い情報として扱う
```

# 台灣股票分析器 MVP

## 如何執行
1. 安裝套件：

   ```bash
   pip install -r requirements.txt
   ```

2. 下載 2330.TW 最近 3 年日線 OHLCV 資料：

   ```bash
   python src/data/download_price.py
   ```

3. 建立基礎特徵資料（含 5 日報酬目標欄位）：

   ```bash
   python src/features/build_features.py
   ```

4. 訓練第一版 baseline 模型（RandomForestClassifier）：

   ```bash
   python src/models/train_model.py
   ```

5. 執行簡易回測（僅使用後 20% 測試區間）：

   ```bash
   python src/backtest/simple_backtest.py
   ```
